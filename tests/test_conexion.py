"""Pruebas del fichero de acceso de la suite."""

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

import conexion


def _cargar(ruta: Path, nombre: str):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class ConexionTests(unittest.TestCase):
    def setUp(self):
        self._old = os.environ.get("DEVIA_CONEXION_PATH")
        self._dir = tempfile.TemporaryDirectory()
        self.path = Path(self._dir.name) / "conexion.json"
        os.environ["DEVIA_CONEXION_PATH"] = str(self.path)
        self.syquo = _cargar(
            Path(r"F:\priveria\tatai\ai_config\suite_conexion.py"),
            "suite_syquo",
        )
        self.datia = _cargar(
            Path(r"F:\datia\datia\services\suite_conexion.py"),
            "suite_datia",
        )

    def tearDown(self):
        if self._old is None:
            os.environ.pop("DEVIA_CONEXION_PATH", None)
        else:
            os.environ["DEVIA_CONEXION_PATH"] = self._old
        self._dir.cleanup()

    def test_sin_fichero_las_aplicaciones_no_ven_acceso(self):
        self.assertFalse(conexion.publico()["present"])
        self.assertIsNone(self.syquo.leer())
        self.assertIsNone(self.datia.leer())

    def test_guardar_no_devuelve_el_secreto_y_lo_conserva(self):
        estado = conexion.guardar({
            "host": "srv",
            "port": "1433",
            "user": "lector",
            "password": "clave-uno",
        })
        self.assertNotIn("password", estado)
        self.assertNotIn("password_protected", estado)
        self.assertTrue(estado["has_secret"])
        texto = self.path.read_text(encoding="utf-8")
        self.assertNotIn("clave-uno", texto)

        editado = conexion.guardar({
            "host": "srv",
            "port": 1433,
            "user": "lector",
            "password": "",
        })
        self.assertTrue(editado["has_secret"])
        guardado = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(conexion.desproteger(guardado["password_protected"]), "clave-uno")
        self.assertNotIn("clave-uno", self.path.read_text(encoding="utf-8"))

    def test_rechaza_guardado_sin_servidor(self):
        with self.assertRaises(ValueError) as ctx:
            conexion.guardar({"host": "", "user": "lector", "password": "x"})
        self.assertIn("servidor", str(ctx.exception))

    def test_cambio_de_secreto_deja_el_acceso_sin_comprobar(self):
        momento = "2026-11-07T18:00:00+01:00"
        documento = {
            "version": 1,
            "host": "srv",
            "port": 1433,
            "user": "lector",
            "password_protected": conexion.proteger("clave-uno"),
            "driver": "{ODBC Driver 18 for SQL Server}",
            "trust_server_certificate": True,
            "active_database": "Contabilidad",
            "updated_at": momento,
            "last_test_at": momento,
            "last_test_ok": True,
            "last_test_message": "Acceso aceptado. Base activa: Contabilidad.",
        }
        self.path.write_text(json.dumps(documento), encoding="utf-8")
        syquo = self.syquo.leer()
        datia = self.datia.leer()
        self.assertTrue(syquo["usable"])
        self.assertEqual(syquo["active_database"], datia["active_database"])
        self.assertEqual(syquo["password"], datia["password"])

        estado = conexion.guardar({
            "host": "srv-nuevo",
            "port": 1433,
            "user": "lector",
            "password": "clave-dos",
        })
        self.assertEqual(estado["active_database"], "")
        self.assertIsNone(estado["last_test_ok"])
        self.assertFalse(self.syquo.leer()["usable"])
        self.assertFalse(self.datia.leer()["usable"])
        self.assertEqual(self.syquo.leer()["password"], "")

    def test_retirar_borra_el_fichero(self):
        conexion.guardar({"host": "srv", "user": "lector", "password": "clave"})
        self.assertTrue(self.path.is_file())
        conexion.retirar()
        self.assertFalse(self.path.is_file())
        self.assertIsNone(self.syquo.leer())
        self.assertIsNone(self.datia.leer())


if __name__ == "__main__":
    unittest.main()
