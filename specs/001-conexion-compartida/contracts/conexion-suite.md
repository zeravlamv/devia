# Contract: Fichero de acceso de la suite

Devia es el único que escribe este fichero. Syquo y Datia solo lo leen.

## Ubicación

`%LOCALAPPDATA%\devia\conexion.json`

No se guarda en el repositorio de Devia, Syquo ni Datia.

## Documento

```json
{
  "version": 1,
  "host": "servidor",
  "port": 1433,
  "user": "usuario",
  "password_protected": "<opaco>",
  "driver": "{ODBC Driver 18 for SQL Server}",
  "trust_server_certificate": true,
  "active_database": "nombre-de-la-base",
  "updated_at": "2026-11-07T18:00:00+01:00",
  "last_test_at": "2026-11-07T18:00:05+01:00",
  "last_test_ok": true,
  "last_test_message": "Acceso aceptado. 2 bases visibles."
}
```

`password_protected` es el secreto envuelto con la protección de datos de Windows del usuario actual. No es la contraseña en claro. Un lector que no pueda desenvolverlo trata el acceso como rechazado.

## Lectura por Syquo y Datia

En cada uso nuevo, si el fichero existe:

1. Si no se puede leer o el secreto no se puede desenvolver, la aplicación explica que el acceso de la suite no está disponible. No usa el origen anterior.
2. Si falta servidor, usuario, secreto o base activa, explica qué falta. No usa el origen anterior.
3. Si `last_test_ok` no es verdadero, o `updated_at` es posterior a `last_test_at`, explica que el acceso no está comprobado o fue rechazado. No muestra cifras.
4. Si está aceptado, usa servidor, puerto, usuario, secreto y `active_database` como única puerta a los datos de empresa.

Si el fichero no existe, cada aplicación sigue con su resolución actual (administración y, si falta, entorno).

## Lo que no viaja en el fichero

- Compañía o empresa dentro de la base.
- Tabla de fórmulas de Syquo.
- Contraseña en claro.
- Lista completa de bases. Esa lista se pide al servidor al comprobar.

## Página de Devia

La página que ya abre el lanzador muestra el acceso además de las tarjetas de las aplicaciones.

- Al guardar, el cuerpo no devuelve el secreto.
- Al volver a abrir, el secreto aparece vacío. Dejarlo vacío conserva el ya guardado.
- Comprobar devuelve si fue aceptado, el mensaje y las bases visibles: `name` y `database_id`.
- Elegir base activa solo acepta un `name` de esa lista.
- Retirar borra el fichero.

Syquo y Datia no ofrecen un formulario para otro servidor, otro usuario, otro secreto ni otra base.
