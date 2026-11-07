# Data Model: Conexión compartida de la suite

Un solo fichero local. No hay una tabla nueva en Syquo ni en Datia.

## Acceso de la suite

Un registro como máximo.

| Campo | Obligatorio | Regla |
|-------|-------------|--------|
| Servidor | Sí | Texto no vacío. Nombre o dirección del servidor. |
| Puerto | Sí | Número entero. Si no se indica, 1433. |
| Usuario | Sí | Texto no vacío. |
| Secreto | Sí para guardar por primera vez | No se guarda en claro. Si al editar se deja vacío, se conserva el anterior. |
| Controlador | No | Si falta, `{ODBC Driver 18 for SQL Server}`. |
| Confiar en el certificado del servidor | No | Sí por defecto en este equipo de trabajo. |
| Actualizado | Sí al guardar | Momento del último guardado. |

No se puede guardar sin servidor o sin usuario. El primer guardado exige secreto.

## Comprobación

Se guarda junto al acceso. No es un segundo acceso.

| Campo | Regla |
|-------|--------|
| Momento | Cuándo se hizo la última comprobación. |
| Aceptada | Sí, no, o todavía no comprobada. |
| Mensaje | Texto claro. Si fue rechazada, el motivo. Vacío si aún no se ha comprobado. |

Una comprobación rechazada no borra el acceso, pero Syquo y Datia no deben presentar cifras del origen anterior como si siguieran vigentes.

## Base disponible

No se guarda la lista. Se pide al servidor en cada comprobación o al abrir el selector.

| Campo | Regla |
|-------|--------|
| Nombre | Único en el servidor. |
| Identificador | Número interno del servidor, para distinguirla si dos nombres se vieran igual. |

Quedan fuera `master`, `tempdb`, `model` y `msdb`.

## Base activa

Como máximo una. Pertenece al acceso, no a una aplicación.

| Campo | Regla |
|-------|--------|
| Nombre | Tiene que ser una de las bases que el acceso puede ver en la última comprobación aceptada. |

Sin base activa, Syquo y Datia explican que falta y no muestran cifras. Cambiarla sustituye a la anterior para las dos en el siguiente uso.

## Qué conserva cada aplicación

| Dato | Dónde sigue |
|------|-------------|
| Compañía o empresa dentro de la base | Syquo y Datia, cada una la suya |
| Tabla de fórmulas | Syquo |
| Especialidad documental o de negocio | Cada aplicación |
| Acceso anterior de administración o de entorno | Solo se usa si el fichero de la suite todavía no existe |

## Estados del acceso

1. **Ausente**: no hay fichero. Syquo y Datia siguen con su acceso anterior.
2. **Incompleto**: falta servidor, usuario, secreto o base activa. Las aplicaciones avisan y no usan un origen viejo de la suite.
3. **Guardado sin comprobar**: hay datos, pero la última comprobación no existe o es anterior al guardado.
4. **Aceptado**: la última comprobación fue aceptada y la base activa está entre las visibles.
5. **Rechazado**: la última comprobación falló. Las aplicaciones lo explican y no muestran cifras del origen previo.
6. **Retirado**: el responsable borra el fichero. Vuelve el estado ausente.

## Transiciones

- Guardar por primera vez: ausente → guardado sin comprobar.
- Comprobación correcta con base activa elegida: → aceptado.
- Comprobación fallida: → rechazado.
- Cambiar servidor, usuario, secreto o base: → guardado sin comprobar hasta una comprobación nueva.
- Retirar: → ausente.
