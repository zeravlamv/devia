"""Lanzador local de Syquo y Datia. Escucha solo en 127.0.0.1:8090."""

from __future__ import annotations

import json
import socket
import subprocess
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = "127.0.0.1"
PORT = 8090
ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"

APPS = {
    "syquo": {
        "cwd": r"E:\priveria\tatai",
        "port": 8000,
        "args": ["py", "manage.py", "runserver", "8000"],
    },
    "datia": {
        "cwd": r"E:\datia",
        "port": 8001,
        "args": ["py", "manage.py", "runserver", "8001"],
    },
}

_locks = {name: threading.Lock() for name in APPS}
_procs: dict[str, subprocess.Popen] = {}


def port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.4)
        return sock.connect_ex((HOST, port)) == 0


def app_status(name: str) -> dict:
    app = APPS[name]
    running = port_open(app["port"])
    proc = _procs.get(name)
    exited = proc is not None and proc.poll() is not None
    return {
        "running": running,
        "port": app["port"],
        "url": f"http://{HOST}:{app['port']}/",
        "cwd": app["cwd"],
        "exited": exited and not running,
        "code": proc.returncode if exited else None,
    }


def start_app(name: str) -> dict:
    app = APPS[name]
    folder = Path(app["cwd"])
    if not folder.is_dir():
        return {"ok": False, "error": f"No existe la carpeta {folder}"}
    if not (folder / "manage.py").is_file():
        return {"ok": False, "error": f"No hay manage.py en {folder}"}
    if port_open(app["port"]):
        return {"ok": True, "state": "already_running", **app_status(name)}

    with _locks[name]:
        if port_open(app["port"]):
            return {"ok": True, "state": "already_running", **app_status(name)}
        proc = subprocess.Popen(
            app["args"],
            cwd=str(folder),
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        _procs[name] = proc
        return {"ok": True, "state": "started", "pid": proc.pid, **app_status(name)}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._send(200, INDEX.read_bytes(), "text/html; charset=utf-8")
            return
        if path == "/api/status":
            body = {name: app_status(name) for name in APPS}
            self._send(200, json.dumps(body).encode("utf-8"), "application/json; charset=utf-8")
            return
        self.send_error(404)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        name = path.removeprefix("/api/").removesuffix("/start")
        if path == f"/api/{name}/start" and name in APPS:
            payload = start_app(name)
            code = 200 if payload.get("ok") else 400
            self._send(code, json.dumps(payload).encode("utf-8"), "application/json; charset=utf-8")
            return
        self.send_error(404)

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[devia] {self.address_string()} {fmt % args}")


def main() -> None:
    if port_open(PORT):
        print(f"Devia ya está en marcha: http://{HOST}:{PORT}/")
        webbrowser.open(f"http://{HOST}:{PORT}/")
        return
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}/"
    print(f"Devia escuchando en {url}")
    print("Syquo  -> E:\\priveria\\tatai  puerto 8000")
    print("Datia  -> E:\\datia           puerto 8001")
    print("Cierra esta ventana para apagar solo el lanzador.")
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nLanzador detenido.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
