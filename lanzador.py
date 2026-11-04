"""Lanzador local de Syquo, Datia y Okia. Escucha solo en 127.0.0.1:8090."""

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

DRIVES = ("E:", "F:")

APPS = {
    "syquo": {
        "relative": r"priveria\tatai",
        "port": 8000,
        "python": None,
    },
    "datia": {
        "relative": "datia",
        "port": 8001,
        "python": None,
    },
    "okia": {
        "relative": r"priveria\okia",
        "port": 8002,
        "python": r".venv\Scripts\python.exe",
    },
}

_locks = {name: threading.Lock() for name in APPS}
_procs: dict[str, subprocess.Popen] = {}


def port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.4)
        return sock.connect_ex((HOST, port)) == 0


def candidate_folders(name: str) -> list[Path]:
    relative = APPS[name]["relative"]
    return [Path(drive + "\\") / relative for drive in DRIVES]


def locate(name: str) -> Path | None:
    for folder in candidate_folders(name):
        if (folder / "manage.py").is_file():
            return folder
    return None


def launch_args(name: str, folder: Path) -> list[str]:
    app = APPS[name]
    port = str(app["port"])
    python = app["python"]
    if python:
        return [str(folder / python), "manage.py", "runserver", port]
    return ["py", "manage.py", "runserver", port]


def command_label(name: str) -> str:
    app = APPS[name]
    port = app["port"]
    if app["python"]:
        return f"{app['python']} manage.py runserver {port}"
    return f"py manage.py runserver {port}"


def app_status(name: str) -> dict:
    app = APPS[name]
    folder = locate(name)
    running = port_open(app["port"])
    proc = _procs.get(name)
    exited = proc is not None and proc.poll() is not None
    if folder is None:
        tried = " ni en ".join(str(path) for path in candidate_folders(name))
        cwd = f"No está en {tried}"
    else:
        cwd = str(folder)
    return {
        "running": running,
        "found": folder is not None,
        "port": app["port"],
        "url": f"http://{HOST}:{app['port']}/",
        "cwd": cwd,
        "command": command_label(name),
        "exited": exited and not running,
        "code": proc.returncode if exited else None,
    }


def start_app(name: str) -> dict:
    app = APPS[name]
    folder = locate(name)
    if folder is None:
        tried = " ni en ".join(str(path) for path in candidate_folders(name))
        return {"ok": False, "error": f"No está en {tried}", **app_status(name)}
    python = app["python"]
    if python and not (folder / python).is_file():
        return {
            "ok": False,
            "error": f"No está el Python del entorno en {folder / python}",
            **app_status(name),
        }
    if port_open(app["port"]):
        return {"ok": True, "state": "already_running", **app_status(name)}

    with _locks[name]:
        if port_open(app["port"]):
            return {"ok": True, "state": "already_running", **app_status(name)}
        proc = subprocess.Popen(
            launch_args(name, folder),
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
    print("Busca cada proyecto en E: y, si no está, en F:.")
    for name in APPS:
        print(f"{name:<6} -> {app_status(name)['cwd']}  puerto {APPS[name]['port']}")
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
