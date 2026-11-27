// Añade locución a un vídeo colocando cada clip de audio en su segundo exacto.
// Uso: swift voz.swift <video.mp4> <salida.mp4> <audio1.aiff>@<segundos> [<audio2.aiff>@<segundos> ...]
import AVFoundation

let a = CommandLine.arguments
guard a.count >= 4 else { print("Uso: swift voz.swift video.mp4 salida.mp4 clip.aiff@0.3 ..."); exit(1) }
let out = URL(fileURLWithPath: a[2])
try? FileManager.default.removeItem(at: out)
let sem = DispatchSemaphore(value: 0)

Task {
  do {
    let video = AVURLAsset(url: URL(fileURLWithPath: a[1]))
    let comp = AVMutableComposition()
    let vSrc = try await video.loadTracks(withMediaType: .video).first!
    let dur = try await video.load(.duration)
    let vTrack = comp.addMutableTrack(withMediaType: .video, preferredTrackID: kCMPersistentTrackID_Invalid)!
    try vTrack.insertTimeRange(CMTimeRange(start: .zero, duration: dur), of: vSrc, at: .zero)
    let aTrack = comp.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid)!
    for spec in a[3...] {
      let parts = spec.split(separator: "@")
      let clip = AVURLAsset(url: URL(fileURLWithPath: String(parts[0])))
      let src = try await clip.loadTracks(withMediaType: .audio).first!
      var cd = try await clip.load(.duration)
      let at = CMTime(seconds: Double(parts[1])!, preferredTimescale: 600)
      if CMTimeAdd(at, cd) > dur { cd = CMTimeSubtract(dur, at) }          // no pasar del final
      try aTrack.insertTimeRange(CMTimeRange(start: .zero, duration: cd), of: src, at: at)
    }
    let ex = AVAssetExportSession(asset: comp, presetName: AVAssetExportPresetHighestQuality)!
    ex.outputURL = out; ex.outputFileType = .mp4
    await ex.export()
    print(ex.status == .completed ? "OK → \(out.path)" : "ERROR \(String(describing: ex.error))")
  } catch { print("ERROR \(error)") }
  sem.signal()
}
sem.wait()
