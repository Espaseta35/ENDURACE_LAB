#!/usr/bin/env python3
"""Renderiza los fotogramas de un reel con un único Chrome sin ventana, controlado por el
protocolo DevTools (sin librerías externas: cliente WebSocket mínimo incluido).

    python3 cdp_render.py <engine.html> <timeline.json> <carpeta_fotogramas> [puerto]
"""
import base64, json, os, socket, struct, subprocess, sys, time, urllib.request

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FPS = 30


class WS:
    def __init__(self, url):
        rest = url.split("://", 1)[1]
        hostport, path = rest.split("/", 1)
        host, port = hostport.split(":")
        self.s = socket.create_connection((host, int(port)))
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((f"GET /{path} HTTP/1.1\r\nHost: {hostport}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                        f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += self.s.recv(4096)
        self.extra = buf.split(b"\r\n\r\n", 1)[1]

    def _read(self, n):
        out = self.extra[:n]; self.extra = self.extra[n:]
        while len(out) < n:
            chunk = self.s.recv(max(65536, n - len(out)))
            if not chunk:
                raise ConnectionError("conexión cerrada")
            out += chunk
        if len(out) > n:
            self.extra = out[n:] + self.extra; out = out[:n]
        return out

    def send(self, text):
        data = text.encode(); n = len(data); mask = os.urandom(4)
        hdr = bytes([0x81]) + (bytes([0x80 | n]) if n < 126 else bytes([0x80 | 126]) + struct.pack(">H", n) if n < 65536 else bytes([0x80 | 127]) + struct.pack(">Q", n))
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
        self.s.sendall(hdr + mask + masked)

    def recv(self):
        msg = b""
        while True:
            b1, b2 = self._read(2)
            n = b2 & 0x7F
            if n == 126: n = struct.unpack(">H", self._read(2))[0]
            elif n == 127: n = struct.unpack(">Q", self._read(8))[0]
            if b2 & 0x80: self._read(4)
            msg += self._read(n)
            if b1 & 0x80:
                return msg.decode("utf-8", "replace")


class CDP:
    def __init__(self, ws):
        self.ws, self.i = ws, 0

    def call(self, method, **params):
        self.i += 1
        self.ws.send(json.dumps({"id": self.i, "method": method, "params": params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == self.i:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m.get("result", {})


def render(engine, timeline, outdir, port=9333):
    os.makedirs(outdir, exist_ok=True)
    tl = json.load(open(timeline))
    profile = f"/tmp/endurace-cdp-{port}"
    proc = subprocess.Popen([CHROME, "--headless=new", "--use-angle=metal", "--enable-gpu-rasterization", "--hide-scrollbars", "--disable-background-timer-throttling",
                             "--disable-renderer-backgrounding", "--disable-backgrounding-occluded-windows", f"--remote-debugging-port={port}",
                             "--remote-allow-origins=*", f"--user-data-dir={profile}", "--window-size=1080,1920",
                             "--force-device-scale-factor=1", "--allow-file-access-from-files", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json"))
                page = next(t for t in tabs if t.get("type") == "page")
                break
            except Exception:
                time.sleep(.2)
        c = CDP(WS(page["webSocketDebuggerUrl"]))
        c.call("Emulation.setDeviceMetricsOverride", width=1080, height=1920, deviceScaleFactor=1, mobile=False)
        c.call("Page.enable")
        c.call("Page.navigate", url="file://" + os.path.abspath(engine))
        for _ in range(100):
            r = c.call("Runtime.evaluate", expression="typeof renderAt === 'function' && document.readyState === 'complete'", returnByValue=True)
            if r.get("result", {}).get("value"):
                break
            time.sleep(.1)
        c.call("Runtime.evaluate", expression="document.fonts.ready.then(() => new Promise(r => setTimeout(r, 300)))", awaitPromise=True)
        c.call("Runtime.evaluate", expression=f"setTimeline({json.dumps(tl, ensure_ascii=False)}); 1")
        frames = round(tl["duration"] * FPS)
        t0 = time.time()
        for f in range(frames):
            c.call("Runtime.evaluate", expression=f"renderAt({f / FPS}); 1")
            shot = c.call("Page.captureScreenshot", format="jpeg", quality=95, fromSurface=True,
                          clip={"x": 0, "y": 0, "width": 1080, "height": 1920, "scale": 1})
            open(os.path.join(outdir, f"{f:04d}.jpg"), "wb").write(base64.b64decode(shot["data"]))
        print(f"{frames} fotogramas en {time.time() - t0:.0f} s", flush=True)
    finally:
        proc.terminate()


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 9333)
