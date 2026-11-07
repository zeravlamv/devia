# Quickstart: Conexión compartida de la suite

Guía de comprobación. Los detalles del fichero están en [contracts/conexion-suite.md](contracts/conexion-suite.md) y los estados en [data-model.md](data-model.md).

## Antes de empezar

- Devia arrancado en este equipo (puerto 8090).
- Syquo y Datia pueden arrancarse desde Devia.
- El servidor de datos de la empresa acepta el usuario de prueba y muestra al menos dos bases de trabajo.
- Okia y el CRM no entran en esta comprobación.

## 1. Guardar y comprobar solo en Devia

1. Abrir la página de Devia.
2. Dejar servidor, puerto, usuario y secreto. Guardar.
3. Volver a abrir el formulario: el secreto no aparece.
4. Comprobar el acceso.

Resultado: en menos de 3 minutos se ve si el servidor acepta, y la lista de bases no incluye las de sistema. Con usuario o secreto incorrectos el mensaje explica el rechazo y no deja marcar una base.

## 2. Una base para las dos

1. Marcar una base como activa.
2. Abrir Syquo y Datia.
3. Confirmar que las dos nombran esa misma base y que ninguna pide servidor, usuario, secreto ni otra base.

Resultado: un dato que solo existe en otra base del mismo servidor no aparece en ninguna de las dos.

## 3. La especialidad no se mueve

1. En Syquo, elegir la compañía dentro de la base y revisar un documento o la salida contable que ya prepara hoy.
2. En Datia, elegir la empresa dentro de la base y revisar un cuadro de negocio.
3. Confirmar que Datia no modifica datos de empresa.

Resultado: cada una sigue mostrando su especialidad a partir de la misma base.

## 4. Un cambio vale para las dos

1. En Devia, cambiar la base activa a la otra base visible, o cambiar el servidor, y comprobar.
2. Recargar Syquo y Datia.

Resultado: las dos usan el origen nuevo. Lo que ya estaba pintado antes del cambio no se reescribe solo. Si la comprobación falla, las dos lo explican y no muestran cifras del origen anterior.

## 5. Todavía no hay fichero

1. Retirar el acceso en Devia.
2. Abrir Syquo y Datia.

Resultado: vuelven a su acceso anterior. No piden un segundo formulario de la suite.

## 6. Base que ya no está

1. Dejar activa una base y después hacer que ese usuario ya no pueda leerla, o retirarla del servidor.
2. Entrar en Syquo y en Datia.

Resultado: las dos avisan y no sustituyen esa base por otra.
