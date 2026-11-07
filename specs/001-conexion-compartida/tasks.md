# Tasks: Conexión compartida de la suite

**Input**: Design documents from `/specs/001-conexion-compartida/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/conexion-suite.md, quickstart.md

**Tests**: Incluidas para el fichero de la suite y para la resolución en Syquo, porque el plan las pide.

**Organization**: Por historia de usuario, para poder comprobar cada una por separado.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

**Purpose**: Dejar el repositorio listo para el fichero local y las pruebas.

- [x] T001 Añadir en `.gitignore` los patrones Python `__pycache__/`, `*.pyc`, `.venv/` y `venv/`
- [x] T002 Crear `conexion.py` con la ruta `%LOCALAPPDATA%\devia\conexion.json`, sustituible por la variable `DEVIA_CONEXION_PATH`

---

## Phase 2: Foundational

**Purpose**: El fichero de acceso, el secreto protegido y la comprobación. Bloquea el resto de historias.

- [x] T003 Proteger y desproteger el secreto con DPAPI del usuario de Windows en `conexion.py`. El fichero no contiene la contraseña en claro
- [x] T004 Guardar en `conexion.py` un solo acceso con servidor obligatorio, puerto entero (si falta, 1433), usuario obligatorio y secreto obligatorio en el primer guardado. Si el secreto llega vacío al editar, se conserva el anterior
- [x] T005 Rechazar en `conexion.py` un guardado sin servidor o sin usuario, y señalar qué falta
- [x] T006 Comprobar en `conexion.py` el acceso con `pyodbc`, tiempo de espera de 5 segundos, y listar bases con `database_id` y `name`, excluyendo `master`, `tempdb`, `model` y `msdb`
- [x] T007 Elegir en `conexion.py` una sola base activa y solo si ese `name` está entre las bases que el acceso puede ver en ese momento
- [x] T008 Retirar el acceso borrando el fichero desde `conexion.py`
- [x] T009 Exponer en `lanzador.py` `GET /api/conexion`, `POST /api/conexion`, `POST /api/conexion/comprobar`, `POST /api/conexion/base` y `POST /api/conexion/retirar`, sin devolver el secreto
- [x] T010 [P] Cubrir guardado, secreto ausente en la respuesta, conservación del secreto, rechazo sin servidor y retirada en `tests/test_conexion.py`

**Checkpoint**: Devia puede guardar y comprobar el acceso sin abrir Syquo ni Datia.

---

## Phase 3: User Story 1 - Registrar el acceso una sola vez (Priority: P1)

**Goal**: El responsable deja el acceso y la base activa en la página de Devia.

**Independent Test**: Guardar, comprobar y marcar una base solo en `http://127.0.0.1:8090/`, sin abrir Syquo ni Datia.

- [x] T011 [US1] Añadir en `index.html` el formulario de servidor, puerto, usuario y secreto, el botón de comprobar, la lista de bases y el botón de retirar
- [x] T012 [US1] Mostrar en `index.html` el resultado de la comprobación y no volver a pintar el secreto

**Checkpoint**: La historia 1 se prueba solo en Devia.

---

## Phase 4: User Story 2 - Syquo y Datia usan el acceso (Priority: P2)

**Goal**: Si el fichero existe y está aceptado, las dos aplicaciones usan esa puerta y no piden otra.

**Independent Test**: Con fichero ausente siguen su acceso anterior. Con fichero aceptado y base activa, la resolución de cada una devuelve ese servidor y esa base.

- [x] T013 [P] [US2] Leer el fichero en cada uso desde `F:\priveria\tatai\ai_config\suite_conexion.py`
- [x] T014 [US2] Hacer que `F:\priveria\tatai\ai_config\mssql_resolver.py` use el fichero cuando existe y deje la tabla de fórmulas en Syquo. Si el fichero falta, conservar administración y entorno
- [x] T015 [US2] Desactivar en `F:\priveria\tatai\ai_config\admin.py` los campos de servidor, puerto, usuario, secreto y base cuando el fichero existe, y mostrar el aviso sin el secreto
- [x] T016 [P] [US2] Leer el fichero en cada uso desde `F:\datia\datia\services\suite_conexion.py`
- [x] T017 [US2] Hacer que `F:\datia\datia\services\runtime_config.py` use el fichero cuando existe. Si falta, conservar `GlobalConfig` y el entorno
- [x] T018 [US2] Desactivar en `F:\datia\datia\admin.py` los campos de servidor, puerto, usuario, secreto y base cuando el fichero existe, e indicar que el origen es Devia sin mostrar el secreto

**Checkpoint**: La historia 2 se prueba con el fichero ausente y con el fichero aceptado.

---

## Phase 5: User Story 3 - La misma base, dos especialidades (Priority: P3)

**Goal**: Ninguna de las dos puede consultar otra base del mismo servidor mientras la suite tiene una activa.

**Independent Test**: La lista de bases de Datia y la conexión de Syquo nombran solo la base activa. Si esa base no se puede leer, el aviso no ofrece cifras de otra.

- [x] T019 [US3] Limitar `F:\datia\datia\api\etl_endpoints.py` a la base activa cuando el fichero manda, y devolver el aviso si el acceso está rechazado o la base no se puede leer
- [x] T020 [US3] Impedir en `F:\datia\datia\services\etl_service.py` que un fallo de la base activa enumere otras bases como origen de recambio
- [x] T021 [P] [US3] Mostrar en `F:\datia\datia\static\js\dashboard\initial_setup.js` la base activa fija y el aviso de la suite
- [x] T022 [P] [US3] Mostrar en `F:\datia\datia\static\js\dashboard\ia.js` la base activa fija y el aviso de la suite
- [x] T023 [US3] Devolver en `F:\priveria\tatai\services\mssql_client.py` el aviso de la suite cuando la conexión no está disponible, con espera de 5 segundos si el origen es la suite

**Checkpoint**: Las dos especialidades salen de la misma base.

---

## Phase 6: User Story 4 - Un cambio llega a las dos (Priority: P4)

**Goal**: El siguiente uso lee el fichero de nuevo. Un acceso rechazado o a medias no muestra cifras del origen anterior.

**Independent Test**: Cambiar el fichero y resolver otra vez. Syquo y Datia ven el estado nuevo. Si se retira el fichero, vuelve el acceso anterior de cada una.

- [x] T024 [US4] Tratar en `conexion.py` un cambio de servidor, puerto, usuario o secreto como acceso sin comprobar y sin base activa hasta la siguiente comprobación
- [x] T025 [P] [US4] Añadir en `F:\priveria\tatai\services\tests\test_mssql_client.py` la prueba de que el fichero aceptado gana y el fichero rechazado no deja una base usable
- [x] T026 [P] [US4] Comprobar en `tests/test_conexion.py` que la lectura de Syquo y la de Datia interpretan el mismo fichero

**Checkpoint**: Un cambio en Devia vale para el siguiente uso de las dos.

---

## Phase 7: Polish

**Purpose**: Dejar el lanzador sirviendo el código nuevo.

- [x] T027 Reiniciar el lanzador de `lanzador.py` para que cargue el acceso en el puerto 8090
- [x] T028 Ejecutar `tests/test_conexion.py` y la prueba de resolución de Syquo

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup, luego el fichero de acceso, luego la página, luego Syquo y Datia, luego el cierre.
- La historia 2 depende del fichero. La historia 3 depende de la lectura de la historia 2. La historia 4 depende de esa lectura.

### User Story Dependencies

- **User Story 1 (P1)**: después del fichero. No depende de Syquo ni de Datia.
- **User Story 2 (P2)**: después del fichero. Syquo y Datia pueden hacerse en paralelo.
- **User Story 3 (P3)**: después de la lectura de cada aplicación.
- **User Story 4 (P4)**: después de la lectura. El fichero ausente devuelve el acceso anterior.

### Parallel Opportunities

- T013 y T016, los dos lectores.
- T021 y T022, los dos scripts de Datia.
- T025 y T026, las pruebas.

---

## Parallel Example: User Story 2

```text
T013 Leer el fichero en F:\priveria\tatai\ai_config\suite_conexion.py
T016 Leer el fichero en F:\datia\datia\services\suite_conexion.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Fichero y comprobación.
2. Formulario en Devia.
3. Parar y probar solo esa página.

### Incremental Delivery

1. Devia guarda y comprueba.
2. Syquo y Datia leen el fichero.
3. La base activa es la única.
4. Un cambio o una retirada se ve en el siguiente uso.

---

## Notes

- Okia y el CRM no entran.
- La compañía dentro de la base se sigue eligiendo en cada aplicación.
- No hay commit hasta CORRECTO.
