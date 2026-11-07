"""Acceso único de la suite al servidor de datos. Devia es quien lo escribe."""

from __future__ import annotations

import base64
import ctypes
import json
import os
from ctypes import wintypes
from datetime import datetime
from pathlib import Path

SISTEMA = {"master", "tempdb", "model", "msdb"}
CONTROLADOR = "{ODBC Driver 18 for SQL Server}"
ESPERA_SEGUNDOS = 5
_UI_FORBIDDEN = 0x1


class DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_char)),
    ]


_crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
_crypt32.CryptProtectData.argtypes = [
    ctypes.POINTER(DATA_BLOB),
    wintypes.LPCWSTR,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_void_p,
    wintypes.DWORD,
    ctypes.POINTER(DATA_BLOB),
]
_crypt32.CryptProtectData.restype = wintypes.BOOL
_crypt32.CryptUnprotectData.argtypes = [
    ctypes.POINTER(DATA_BLOB),
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_void_p,
    wintypes.DWORD,
    ctypes.POINTER(DATA_BLOB),
]
_crypt32.CryptUnprotectData.restype = wintypes.BOOL
_kernel32.LocalFree.argtypes = [ctypes.c_void_p]
_kernel32.LocalFree.restype = ctypes.c_void_p


def ruta() -> Path:
    override = os.environ.get("DEVIA_CONEXION_PATH", "").strip()
    if override:
        return Path(override)
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    return Path(base) / "devia" / "conexion.json"


def ahora() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _blob(data: bytes) -> tuple[DATA_BLOB, ctypes.Array]:
    buffer = ctypes.create_string_buffer(data)
    blob = DATA_BLOB(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_char)))
    return blob, buffer


def proteger(secreto: str) -> str:
    blob, _buffer = _blob(secreto.encode("utf-8"))
    salida = DATA_BLOB()
    ok = _crypt32.CryptProtectData(
        ctypes.byref(blob),
        "devia-conexion",
        None,
        None,
        None,
        _UI_FORBIDDEN,
        ctypes.byref(salida),
    )
    if not ok:
        raise OSError("No se pudo proteger el secreto")
    try:
        crudo = ctypes.string_at(salida.pbData, salida.cbData)
    finally:
        _kernel32.LocalFree(ctypes.cast(salida.pbData, ctypes.c_void_p))
    return base64.b64encode(crudo).decode("ascii")


def desproteger(token: str) -> str:
    crudo = base64.b64decode(token)
    blob, _buffer = _blob(crudo)
    salida = DATA_BLOB()
    ok = _crypt32.CryptUnprotectData(
        ctypes.byref(blob),
        None,
        None,
        None,
        None,
        _UI_FORBIDDEN,
        ctypes.byref(salida),
    )
    if not ok:
        raise OSError("No se pudo leer el secreto")
    try:
        return ctypes.string_at(salida.pbData, salida.cbData).decode("utf-8")
    finally:
        _kernel32.LocalFree(ctypes.cast(salida.pbData, ctypes.c_void_p))


def _vacio() -> dict:
    return {
        "present": False,
        "host": "",
        "port": 1433,
        "user": "",
        "has_secret": False,
        "driver": CONTROLADOR,
        "trust_server_certificate": True,
        "active_database": "",
        "updated_at": "",
        "last_test_at": "",
        "last_test_ok": None,
        "last_test_message": "",
        "usable": False,
        "message": "",
    }


def _leer_documento() -> dict | None:
    path = ruta()
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _escribir(documento: dict) -> None:
    path = ruta()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(documento, ensure_ascii=False, indent=2), encoding="utf-8")


def evaluar(documento: dict | None) -> dict:
    """Estado para las aplicaciones. No incluye el secreto."""
    if documento is None:
        return _vacio()
    estado = _vacio()
    estado["present"] = True
    estado["host"] = str(documento.get("host") or "").strip()
    try:
        estado["port"] = int(documento.get("port") or 1433)
    except (TypeError, ValueError):
        estado["port"] = 1433
    estado["user"] = str(documento.get("user") or "").strip()
    estado["driver"] = str(documento.get("driver") or CONTROLADOR).strip() or CONTROLADOR
    estado["trust_server_certificate"] = bool(documento.get("trust_server_certificate", True))
    estado["active_database"] = str(documento.get("active_database") or "").strip()
    estado["updated_at"] = str(documento.get("updated_at") or "")
    estado["last_test_at"] = str(documento.get("last_test_at") or "")
    estado["last_test_ok"] = documento.get("last_test_ok")
    estado["last_test_message"] = str(documento.get("last_test_message") or "")
    token = str(documento.get("password_protected") or "")
    estado["has_secret"] = bool(token)
    secreto = ""
    if token:
        try:
            secreto = desproteger(token)
        except Exception:
            estado["message"] = "El acceso de la suite no se puede leer en esta sesión de Windows."
            return estado
    if not estado["host"] or not estado["user"] or not secreto:
        estado["message"] = "Falta el servidor, el usuario o el secreto de la suite. Complétalo en Devia."
        return estado
    if estado["last_test_ok"] is not True:
        estado["message"] = estado["last_test_message"] or "El acceso de la suite no está comprobado."
        return estado
    if not estado["last_test_at"] or estado["updated_at"] > estado["last_test_at"]:
        estado["message"] = "El acceso de la suite cambió y todavía no está comprobado."
        return estado
    if not estado["active_database"]:
        estado["message"] = "Falta la base activa de la suite. Elígela en Devia."
        return estado
    estado["usable"] = True
    estado["message"] = estado["last_test_message"]
    estado["password"] = secreto
    return estado


def leer() -> dict:
    try:
        documento = _leer_documento()
    except (OSError, json.JSONDecodeError):
        estado = _vacio()
        estado["present"] = True
        estado["message"] = "El acceso de la suite no se puede leer."
        return estado
    return evaluar(documento)


def publico() -> dict:
    estado = leer()
    estado.pop("password", None)
    return estado


def _puerto(valor) -> int:
    try:
        puerto = int(valor)
    except (TypeError, ValueError):
        raise ValueError("El puerto tiene que ser un número.")
    if puerto < 1 or puerto > 65535:
        raise ValueError("El puerto tiene que estar entre 1 y 65535.")
    return puerto


def guardar(datos: dict) -> dict:
    host = str(datos.get("host") or "").strip()
    user = str(datos.get("user") or "").strip()
    faltan = []
    if not host:
        faltan.append("servidor")
    if not user:
        faltan.append("usuario")
    if faltan:
        raise ValueError("Falta " + " y ".join(faltan) + ".")
    puerto = _puerto(datos.get("port") or 1433)
    anterior = None
    try:
        anterior = _leer_documento()
    except (OSError, json.JSONDecodeError):
        anterior = None
    secreto_nuevo = str(datos.get("password") or "")
    if secreto_nuevo:
        token = proteger(secreto_nuevo)
    elif anterior and anterior.get("password_protected"):
        token = anterior["password_protected"]
    else:
        raise ValueError("Falta el secreto.")
    cambio = True
    if anterior:
        try:
            secreto_anterior = desproteger(str(anterior.get("password_protected") or ""))
        except Exception:
            secreto_anterior = None
        cambio = not (
            str(anterior.get("host") or "").strip() == host
            and int(anterior.get("port") or 1433) == puerto
            and str(anterior.get("user") or "").strip() == user
            and secreto_anterior == (secreto_nuevo or secreto_anterior)
        )
    documento = {
        "version": 1,
        "host": host,
        "port": puerto,
        "user": user,
        "password_protected": token,
        "driver": CONTROLADOR,
        "trust_server_certificate": True,
        "active_database": "" if cambio else str((anterior or {}).get("active_database") or ""),
        "updated_at": ahora(),
        "last_test_at": "" if cambio else str((anterior or {}).get("last_test_at") or ""),
        "last_test_ok": None if cambio else (anterior or {}).get("last_test_ok"),
        "last_test_message": "" if cambio else str((anterior or {}).get("last_test_message") or ""),
    }
    if not cambio and anterior:
        documento["updated_at"] = str(anterior.get("updated_at") or documento["updated_at"])
    _escribir(documento)
    return publico()


def _mensaje_odbc(exc: Exception) -> str:
    texto = str(exc).lower()
    if "login failed" in texto or "18456" in texto:
        return "El servidor ha rechazado el usuario o el secreto."
    if "timeout" in texto or "08001" in texto or "server is not found" in texto or "no es accesible" in texto:
        return "El servidor no responde."
    if "im002" in texto or "data source name not found" in texto:
        return "No está el controlador ODBC de SQL Server en este equipo."
    return "El servidor ha rechazado el acceso."


def _conectar(documento: dict, secreto: str, base: str):
    import pyodbc

    partes = [
        f"DRIVER={documento.get('driver') or CONTROLADOR}",
        f"SERVER={documento['host']},{int(documento.get('port') or 1433)}",
        f"DATABASE={base}",
        f"UID={documento['user']}",
        f"PWD={secreto}",
        "Encrypt=yes",
        "TrustServerCertificate=yes",
        f"Connection Timeout={ESPERA_SEGUNDOS}",
    ]
    return pyodbc.connect(";".join(partes), timeout=ESPERA_SEGUNDOS)


def comprobar() -> dict:
    try:
        documento = _leer_documento()
    except (OSError, json.JSONDecodeError):
        raise ValueError("El acceso de la suite no se puede leer.")
    if not documento:
        raise ValueError("Todavía no hay un acceso guardado.")
    try:
        secreto = desproteger(str(documento.get("password_protected") or ""))
    except Exception as exc:
        raise ValueError("El acceso de la suite no se puede leer en esta sesión de Windows.") from exc
    bases: list[dict] = []
    try:
        conexion = _conectar(documento, secreto, "master")
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT database_id, name FROM sys.databases "
                "WHERE HAS_DBACCESS(name)=1 "
                "AND name NOT IN ('master','tempdb','model','msdb') "
                "ORDER BY name"
            )
            for fila in cursor.fetchall():
                nombre = str(fila[1])
                if nombre.lower() in SISTEMA:
                    continue
                bases.append({"database_id": int(fila[0]), "name": nombre})
        finally:
            conexion.close()
    except ImportError as exc:
        raise ValueError("Falta pyodbc en el Python del lanzador.") from exc
    except Exception as exc:
        documento["last_test_at"] = ahora()
        documento["last_test_ok"] = False
        documento["last_test_message"] = _mensaje_odbc(exc)
        documento["updated_at"] = documento["last_test_at"]
        _escribir(documento)
        estado = publico()
        estado["databases"] = []
        return estado
    if bases:
        mensaje = f"Acceso aceptado. {len(bases)} bases visibles."
    else:
        mensaje = "El acceso es válido, pero este usuario no puede ver ninguna base de trabajo."
    activa = str(documento.get("active_database") or "")
    if activa and not any(item["name"] == activa for item in bases):
        documento["active_database"] = ""
        mensaje = f"La base activa «{activa}» ya no está disponible."
    momento = ahora()
    documento["last_test_at"] = momento
    documento["updated_at"] = momento
    documento["last_test_ok"] = True
    documento["last_test_message"] = mensaje
    _escribir(documento)
    estado = publico()
    estado["databases"] = bases
    return estado


def elegir_base(nombre: str) -> dict:
    nombre = str(nombre or "").strip()
    if not nombre:
        raise ValueError("Falta el nombre de la base.")
    estado = comprobar()
    if estado.get("last_test_ok") is not True:
        raise ValueError(estado.get("last_test_message") or "El acceso no está aceptado.")
    visibles = estado.get("databases") or []
    if not any(item.get("name") == nombre for item in visibles):
        raise ValueError("Esa base no está entre las que este acceso puede ver.")
    documento = _leer_documento()
    if not documento:
        raise ValueError("Todavía no hay un acceso guardado.")
    momento = ahora()
    documento["active_database"] = nombre
    documento["updated_at"] = momento
    documento["last_test_at"] = momento
    documento["last_test_ok"] = True
    documento["last_test_message"] = f"Acceso aceptado. Base activa: {nombre}."
    _escribir(documento)
    return publico()


def retirar() -> dict:
    path = ruta()
    if path.is_file():
        path.unlink()
    return publico()
