import hashlib
import json
import mimetypes
import pathlib
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

ROOT = pathlib.Path.home() / "AiMetaverse"
CATALOG_PATH = ROOT / "data" / "endless-ai-toolset.json"
RUNNER_PATH = ROOT / "scripts" / "endless_ai_toolset.py"
APK_DIR = ROOT / "apk"
STORE_DIR = ROOT / "store"
LOG_PATH = pathlib.Path.home() / "tmp" / "endless_ai_api_probe.log"


def load_tools() -> list[dict]:
    if not CATALOG_PATH.exists():
        return []
    raw = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and isinstance(raw.get("tools"), list):
        return raw["tools"]
    return raw if isinstance(raw, list) else []


def latest_apk() -> pathlib.Path | None:
    if not APK_DIR.exists():
        return None
    apks = sorted(APK_DIR.glob("*.apk"), key=lambda p: p.stat().st_mtime, reverse=True)
    return apks[0] if apks else None


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class AiMetaverseHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args) -> None:
        # Quiet default access spam; errors still surface via stderr/logs.
        return

    def _send_bytes(self, status: int, content_type: str, data: bytes, extra_headers: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, status: int, payload: object) -> None:
        raw = json.dumps(payload, indent=2).encode("utf-8")
        self._send_bytes(status, "application/json; charset=utf-8", raw)

    def _serve_file(self, path: pathlib.Path, force_download: bool = False) -> None:
        if not path.exists() or not path.is_file():
            self._send_json(404, {"error": "Not found", "path": str(path)})
            return
        ctype, _ = mimetypes.guess_type(str(path))
        if not ctype:
            ctype = "application/vnd.android.package-archive" if path.suffix == ".apk" else "application/octet-stream"
        if ctype.startswith("text/") or path.suffix in {".html", ".js", ".css", ".json"}:
            ctype = f"{ctype}; charset=utf-8"
        headers = {}
        if force_download:
            headers["Content-Disposition"] = f'attachment; filename="{path.name}"'
        self._send_bytes(200, ctype, path.read_bytes(), headers)

    def do_OPTIONS(self) -> None:
        self._send_bytes(204, "text/plain; charset=utf-8", b"")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path == "/health":
            tools = load_tools()
            apk = latest_apk()
            self._send_json(
                200,
                {
                    "status": "ok",
                    "server": "stdlib-http.server",
                    "repo": str(ROOT),
                    "tools_total": len(tools),
                    "ai_focused_total": sum(1 for t in tools if isinstance(t, dict) and t.get("aiFocused")),
                    "latest_apk": apk.name if apk else None,
                },
            )
            return

        if path == "/api/tools":
            ai_only = qs.get("ai_only", ["false"])[0].lower() in {"1", "true", "yes"}
            module_filter = (qs.get("module", [""])[0] or "").strip().lower()
            try:
                limit = max(1, min(1000, int(qs.get("limit", ["200"])[0])))
            except ValueError:
                limit = 200

            matched = [t for t in load_tools() if isinstance(t, dict)]
            if ai_only:
                matched = [t for t in matched if bool(t.get("aiFocused"))]
            if module_filter:
                matched = [
                    t
                    for t in matched
                    if module_filter
                    in str(t.get("file") or t.get("module") or t.get("moduleId") or "").lower()
                ]

            self._send_json(
                200,
                {
                    "count": len(matched[:limit]),
                    "total_matched": len(matched),
                    "tools": matched[:limit],
                },
            )
            return

        if path == "/api/apk/latest":
            apk = latest_apk()
            if not apk:
                self._send_json(200, {"available": False, "apk_dir": str(APK_DIR)})
                return
            st = apk.stat()
            self._send_json(
                200,
                {
                    "available": True,
                    "filename": apk.name,
                    "size_bytes": st.st_size,
                    "sha256": sha256_file(apk),
                    "download_url": f"/apk/{apk.name}",
                },
            )
            return

        if path in {"/", "/index.html"}:
            self._serve_file(APK_DIR / "index.html")
            return

        if path.startswith("/apk/"):
            rel = path.removeprefix("/apk/")
            target = (APK_DIR / rel).resolve()
            if APK_DIR.resolve() not in target.parents:
                self._send_json(403, {"error": "Forbidden"})
                return
            self._serve_file(target, force_download=target.suffix == ".apk")
            return

        if path.startswith("/store/"):
            rel = path.removeprefix("/store/") or "index.html"
            target = (STORE_DIR / rel).resolve()
            if target.is_dir():
                target = target / "index.html"
            if STORE_DIR.resolve() not in target.parents and target != STORE_DIR.resolve():
                self._send_json(403, {"error": "Forbidden"})
                return
            self._serve_file(target)
            return

        self._send_json(404, {"error": "Unknown route", "path": path})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/probe/run":
            self._send_json(404, {"error": "Unknown POST route", "path": parsed.path})
            return

        content_len = int(self.headers.get("Content-Length", "0") or "0")
        body_data = {}
        if content_len > 0:
            raw_body = self.rfile.read(content_len).decode("utf-8", errors="replace").strip()
            if raw_body:
                try:
                    body_data = json.loads(raw_body)
                except json.JSONDecodeError:
                    body_data = {}

        qs = parse_qs(parsed.query)
        try:
            cycles = max(1, min(15, int(body_data.get("cycles", qs.get("cycles", [3])[0]))))
        except (ValueError, TypeError):
            cycles = 3
        try:
            interval = max(0, min(10, int(body_data.get("interval", qs.get("interval", [1])[0]))))
        except (ValueError, TypeError):
            interval = 1

        if not RUNNER_PATH.exists():
            self._send_json(404, {"error": "Runner script not found", "runner": str(RUNNER_PATH)})
            return

        cmd = [
            "python3",
            str(RUNNER_PATH),
            "--loop",
            "--interval",
            str(interval),
            "--max-cycles",
            str(cycles),
        ]
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=60)
        combined = (proc.stdout or "") + (proc.stderr or "")
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        LOG_PATH.write_text(combined, encoding="utf-8")
        lines = [ln.strip() for ln in combined.splitlines() if ln.strip()]

        self._send_json(
            200,
            {
                "returncode": proc.returncode,
                "cycles": cycles,
                "interval": interval,
                "lines": lines,
                "log_file": str(LOG_PATH),
            },
        )


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8000), AiMetaverseHandler)
    print("Serving AiMetaverse stdlib API & APK portal on http://127.0.0.1:8000", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
