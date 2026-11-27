// Renderiza un reel: carga engine.html en WebKit, dibuja cada fotograma según el timeline,
// lo codifica en H.264 y mezcla la voz en su momento exacto.
// Uso: swift render.swift <engine.html> <timeline.json> <salida.mp4>
import Cocoa
import WebKit
import AVFoundation

let A = CommandLine.arguments
let engine = URL(fileURLWithPath: A[1]), tlURL = URL(fileURLWithPath: A[2]), out = URL(fileURLWithPath: A[3])
let tlData = try! Data(contentsOf: tlURL)
let tl = try! JSONSerialization.jsonObject(with: tlData) as! [String: Any]
let fps = 30, W = 1080, H = 1920
let duration = tl["duration"] as! Double
let frames = Int((duration * Double(fps)).rounded())

let app = NSApplication.shared
app.setActivationPolicy(.accessory)

final class Loader: NSObject, WKNavigationDelegate {
  var done: CheckedContinuation<Void, Never>?
  func webView(_ w: WKWebView, didFinish n: WKNavigation!) { done?.resume(); done = nil }
}

@MainActor func run() async {
  let conf = WKWebViewConfiguration()
  if #available(macOS 14.0, *) { conf.preferences.inactiveSchedulingPolicy = .none }   // sin frenado en segundo plano
  let web = WKWebView(frame: NSRect(x: 0, y: 0, width: W, height: H), configuration: conf)
  let win = NSWindow(contentRect: NSRect(x: -6000, y: -6000, width: W, height: H), styleMask: .borderless, backing: .buffered, defer: false)
  win.contentView = web
  win.orderFrontRegardless()
  let loader = Loader(); web.navigationDelegate = loader
  await withCheckedContinuation { c in loader.done = c; web.loadFileURL(engine, allowingReadAccessTo: engine.deletingLastPathComponent()) }
  _ = try? await web.callAsyncJavaScript("await document.fonts.ready; await new Promise(r => setTimeout(r, 400)); return 1", contentWorld: .page)
  let json = String(data: tlData, encoding: .utf8)!
  _ = try? await web.evaluateJavaScript("setTimeline(\(json)); 1")

  // --- vídeo sin audio
  let tmp = out.deletingPathExtension().appendingPathExtension("tmp.mp4")
  try? FileManager.default.removeItem(at: tmp)
  let writer = try! AVAssetWriter(outputURL: tmp, fileType: .mp4)
  let input = AVAssetWriterInput(mediaType: .video, outputSettings: [
    AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: W, AVVideoHeightKey: H,
    AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: 12_000_000, AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel]])
  let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: [
    kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32ARGB, kCVPixelBufferWidthKey as String: W, kCVPixelBufferHeightKey as String: H])
  writer.add(input); writer.startWriting(); writer.startSession(atSourceTime: .zero)
  let cfg = WKSnapshotConfiguration(); cfg.rect = NSRect(x: 0, y: 0, width: W, height: H); cfg.snapshotWidth = NSNumber(value: W)

  for f in 0..<frames {
    _ = try? await web.evaluateJavaScript("renderAt(\(Double(f) / Double(fps))); 1")
    guard let img = try? await web.takeSnapshot(configuration: cfg),
          let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { print("fallo en fotograma \(f)"); continue }
    var pb: CVPixelBuffer?
    CVPixelBufferPoolCreatePixelBuffer(nil, adaptor.pixelBufferPool!, &pb)
    let buf = pb!
    CVPixelBufferLockBaseAddress(buf, [])
    let ctx = CGContext(data: CVPixelBufferGetBaseAddress(buf), width: W, height: H, bitsPerComponent: 8, bytesPerRow: CVPixelBufferGetBytesPerRow(buf),
                        space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue)!
    ctx.interpolationQuality = .high
    ctx.draw(cg, in: CGRect(x: 0, y: 0, width: W, height: H))
    CVPixelBufferUnlockBaseAddress(buf, [])
    while !input.isReadyForMoreMediaData { try? await Task.sleep(nanoseconds: 2_000_000) }
    adaptor.append(buf, withPresentationTime: CMTime(value: CMTimeValue(f), timescale: CMTimeScale(fps)))
    if f % 90 == 0 { print("  fotograma \(f)/\(frames)"); fflush(stdout) }
  }
  input.markAsFinished()
  await writer.finishWriting()

  // --- mezcla de la voz
  do {
    let video = AVURLAsset(url: tmp)
    let comp = AVMutableComposition()
    let vDur = try await video.load(.duration)
    let vt = comp.addMutableTrack(withMediaType: .video, preferredTrackID: kCMPersistentTrackID_Invalid)!
    try vt.insertTimeRange(CMTimeRange(start: .zero, duration: vDur), of: try await video.loadTracks(withMediaType: .video).first!, at: .zero)
    let at = comp.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid)!
    for v in (tl["voice"] as? [[String: Any]]) ?? [] {
      let clip = AVURLAsset(url: URL(fileURLWithPath: v["file"] as! String))
      guard let src = try await clip.loadTracks(withMediaType: .audio).first else { continue }
      var cd = try await clip.load(.duration)
      let start = CMTime(seconds: v["at"] as! Double, preferredTimescale: 600)
      if CMTimeAdd(start, cd) > vDur { cd = CMTimeSubtract(vDur, start) }
      try at.insertTimeRange(CMTimeRange(start: .zero, duration: cd), of: src, at: start)
    }
    try? FileManager.default.removeItem(at: out)
    let ex = AVAssetExportSession(asset: comp, presetName: AVAssetExportPresetHighestQuality)!
    ex.outputURL = out; ex.outputFileType = .mp4
    await ex.export()
    try? FileManager.default.removeItem(at: tmp)
    print(ex.status == .completed ? "OK \(frames) fotogramas · \(String(format: "%.1f", duration)) s → \(out.lastPathComponent)" : "ERROR \(String(describing: ex.error))")
  } catch { print("ERROR audio \(error)") }
  exit(0)
}

Task { @MainActor in await run() }
app.run()
