# Feature Specification: Conexión compartida de la suite

**Feature Branch**: `feature/conexion-compartida`

**Created**: 2026-11-07

**Status**: Draft

**Input**: User description: "Devia es una aplicación que gestiona a modo de suite todos los desarrollos que voy integrando. Hay una particularidad común de casi todas las app. Esta particularidad es que se conectan a MSSQL Server y mediante la selección de base recogen datos, los agrupan y después muestran cada una en base a su especialidad. Quiero que revises, de momento solo SYQUO y DATIA, para que compartir la conexión que se gestionará desde DEVIA."

## Clarifications

### Session 2026-11-07

- Q: ¿Syquo y Datia usan bases distintas o la misma? → A: Se conectan a la misma.
- Q: ¿Dónde se elige esa base y qué pasa si cambia? → A: Se selecciona una vez en Devia, la utilizan las dos, y un cambio vale para las dos.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registrar el acceso al servidor una sola vez (Priority: P1)

El responsable de la suite abre Devia y deja anotado, en un solo sitio, cómo se entra al servidor de datos de la empresa. Comprueba en ese mismo sitio si el servidor acepta el acceso. No tiene que repetir servidor, usuario ni secreto dentro de Syquo ni dentro de Datia.

**Why this priority**: Sin un acceso único no hay nada que compartir. Hoy Syquo y Datia piden cada una su propio acceso al mismo servidor, y un cambio hay que hacerlo dos veces.

**Independent Test**: Se puede probar solo en Devia: guardar el acceso, lanzar la comprobación y ver si el servidor responde o por qué no. No hace falta abrir Syquo ni Datia.

**Acceptance Scenarios**:

1. **Given** que Devia no tiene todavía un acceso al servidor, **When** el responsable indica servidor, puerto, usuario y secreto y guarda, **Then** ese acceso queda como el de la suite y se puede volver a abrir para revisarlo sin que el secreto se muestre entero.
2. **Given** un acceso guardado con datos correctos, **When** el responsable pide comprobarlo, **Then** Devia confirma que el servidor acepta el acceso y muestra las bases que ese acceso puede ver.
3. **Given** esas bases visibles, **When** el responsable marca una como activa, **Then** esa queda como la única base de la suite y Syquo y Datia no pueden elegir otra.
4. **Given** un acceso guardado con usuario o secreto incorrectos, **When** el responsable pide comprobarlo, **Then** Devia explica el rechazo en lenguaje claro y no presenta bases como si el acceso hubiera funcionado.

---

### User Story 2 - Syquo y Datia usan el acceso de la suite (Priority: P2)

Cuando el responsable entra en Syquo o en Datia para trabajar con los datos de la empresa, esas aplicaciones usan el acceso definido en Devia. Ninguna de las dos vuelve a pedir un servidor, un usuario o un secreto propios.

**Why this priority**: Es el resultado que se busca. El acceso deja de estar duplicado y las dos especialidades leen a través de la misma puerta.

**Independent Test**: Con un acceso ya comprobado y una base activa en la suite, se abre Syquo y se abre Datia. Ninguna pide otro servidor ni otra base, y las dos trabajan sobre la misma.

**Acceptance Scenarios**:

1. **Given** un acceso de suite comprobado y una base activa, **When** el responsable abre Syquo, **Then** Syquo usa esa base y no pide otro servidor, otro secreto ni otra base.
2. **Given** el mismo acceso y la misma base, **When** el responsable abre Datia, **Then** Datia usa esa misma base y tampoco pide otro acceso ni otra base.
3. **Given** que todavía no hay acceso guardado en Devia, **When** el responsable abre Syquo o Datia, **Then** la aplicación explica que falta el acceso de la suite y no le hace escribir un acceso paralelo.

---

### User Story 3 - La misma base, dos especialidades (Priority: P3)

Syquo y Datia leen la misma base activa de la suite. Cada una agrupa y muestra esos datos según su especialidad: Syquo en su ciclo documental y Datia en su cuadro de negocio. Ninguna puede quedar apuntando a una base distinta.

**Why this priority**: Compartir el acceso no basta si cada aplicación acaba en una base diferente. La especialidad está en cómo presentan los datos, no en cuál base usan.

**Independent Test**: Con dos bases visibles en el servidor y una sola marcada como activa, Syquo y Datia muestran datos de esa base. Un dato que solo existe en la otra base no aparece en ninguna de las dos.

**Acceptance Scenarios**:

1. **Given** el servidor muestra al menos dos bases y la suite tiene una activa, **When** el responsable consulta Syquo y Datia, **Then** las dos indican la misma base activa.
2. **Given** esa base activa, **When** el responsable consulta documentos en Syquo y cifras en Datia, **Then** ambos resultados salen de esa base y no de otra del mismo servidor.
3. **Given** la base activa desaparece del servidor, **When** el responsable vuelve a entrar en Syquo o en Datia, **Then** la aplicación avisa de que ya no está disponible y no presenta cifras de otra base como si fueran las de la activa.

---

### User Story 4 - Un cambio de acceso llega a las dos aplicaciones (Priority: P4)

El responsable corrige el acceso en Devia (otro servidor, otro usuario o un secreto nuevo) y lo comprueba. La próxima vez que usa Syquo y la próxima vez que usa Datia, las dos trabajan con el acceso nuevo. Los datos del servidor anterior dejan de aparecer.

**Why this priority**: Si el cambio se queda solo en Devia, la suite vuelve a tener dos verdades. El valor del acceso único es que un cambio basta.

**Independent Test**: Se cambia el servidor en Devia, se comprueba el acceso nuevo, se deja una base activa de ese servidor y se visita Syquo y Datia. Las dos usan esa base y no muestran datos del servidor anterior.

**Acceptance Scenarios**:

1. **Given** Syquo y Datia ya usaban un acceso y una base anteriores, **When** el responsable guarda y comprueba un acceso distinto y deja activa una base del servidor nuevo, **Then** el siguiente uso de cada aplicación usa esa base y no la anterior.
2. **Given** el acceso nuevo rechaza la entrada, **When** el responsable abre Syquo o Datia, **Then** cada una explica que el acceso de la suite no funciona y no muestra cifras del servidor anterior como si siguieran vigentes.
3. **Given** un acceso que funcionaba, **When** el responsable lo retira de Devia, **Then** Syquo y Datia dejan de usarlo y vuelven a explicar que falta el acceso de la suite.

---

### Edge Cases

- El servidor no responde o tarda demasiado: la comprobación en Devia y el intento en cada aplicación terminan con un aviso claro, sin dejar la pantalla cargando de forma indefinida.
- El usuario existe pero no puede ver ninguna base: la comprobación lo dice y las aplicaciones no muestran una lista vacía como si fuera un éxito silencioso.
- Dos bases se llaman igual a ojos de la persona: la lista las distingue para que la base activa no sea ambigua.
- El secreto se cambia en Devia mientras Syquo o Datia están abiertas: el trabajo ya en pantalla no se reescribe solo; el siguiente uso ya emplea el secreto nuevo.
- La base activa sigue existiendo, pero el usuario ya no tiene permiso para leerla: la aplicación lo explica y no sustituye esa base por otra.
- Se intenta guardar un acceso sin servidor o sin usuario: Devia no lo da por válido y señala qué falta.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Devia MUST permitir al responsable de la suite registrar un único acceso al servidor de datos de la empresa, con servidor, puerto, usuario y secreto.
- **FR-002**: Devia MUST permitir comprobar ese acceso y MUST mostrar si el servidor lo acepta o el motivo del rechazo, en lenguaje comprensible.
- **FR-003**: Cuando el acceso es aceptado, Devia MUST mostrar las bases de datos que ese acceso puede ver.
- **FR-004**: El secreto guardado MUST NOT volver a mostrarse entero. Syquo y Datia MUST NOT mostrar ese secreto ni ofrecer un segundo formulario para crear otro acceso al servidor.
- **FR-005**: Syquo MUST usar el acceso de la suite como única puerta a los datos de empresa que hoy obtiene del servidor.
- **FR-006**: Datia MUST usar el acceso de la suite como única puerta a los datos de empresa que hoy obtiene del servidor.
- **FR-007**: Devia MUST permitir elegir una sola base activa entre las que el acceso puede ver. Esa elección se hace una vez y MUST NOT repetirse dentro de Syquo ni de Datia.
- **FR-008**: Syquo y Datia MUST usar esa misma base activa. Un cambio de base activa en Devia MUST valer para las dos en el siguiente uso.
- **FR-009**: Syquo MUST seguir agrupando y presentando la información según su especialidad documental, y Datia MUST seguir haciéndolo según su especialidad de negocio, las dos a partir de la misma base.
- **FR-010**: Datia MUST seguir consultando los datos de empresa sin modificarlos.
- **FR-011**: Syquo MUST conservar su capacidad actual de preparar la salida contable hacia el ERP, usando el mismo acceso y la misma base activa de la suite.
- **FR-012**: Un cambio de acceso o de base activa MUST aplicarse al siguiente uso de Syquo y al siguiente uso de Datia.
- **FR-013**: Si no hay acceso de suite, no hay base activa, o el acceso guardado es rechazado, Syquo y Datia MUST explicarlo y MUST NOT presentar cifras del último origen que sí funcionó como si siguieran vigentes.
- **FR-014**: Si la base activa ya no está disponible o ya no se puede leer, Syquo y Datia MUST avisarlo y MUST NOT mostrar datos de otra base en su lugar.
- **FR-015**: La empresa o la compañía dentro de la base activa MUST seguir eligiéndose dentro de cada aplicación, no en Devia.

### Key Entities

- **Acceso de la suite**: la puerta única al servidor de datos. Incluye servidor, puerto, usuario, secreto y el resultado de la última comprobación. Solo hay uno activo para la suite.
- **Base disponible**: una base que el acceso de la suite puede ver. Tiene un nombre distinguible para la persona que elige.
- **Base activa**: la única base que Syquo y Datia usan como origen de sus datos de empresa. Se elige una vez en Devia. No hay una base activa por aplicación.
- **Aplicación de la suite**: en esta entrega, Syquo o Datia. Cada una agrupa y muestra los datos de la base activa según su especialidad.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El responsable deja registrado el acceso y sabe si el servidor lo acepta en menos de 3 minutos, sin abrir Syquo ni Datia.
- **SC-002**: Después de ese registro, el responsable no vuelve a escribir el usuario ni el secreto del servidor ni en Syquo ni en Datia.
- **SC-003**: Con dos bases visibles en el servidor y una sola activa, Syquo y Datia muestran datos de esa misma base, y un dato que solo existe en la otra no aparece en ninguna de las dos.
- **SC-004**: Tras cambiar el servidor o la base activa en la suite, la siguiente visita a Syquo y la siguiente visita a Datia usan el origen nuevo y ninguna cifra del origen anterior.
- **SC-005**: Cuando el servidor rechaza el acceso, tanto Devia como la aplicación abierta explican el fallo en el primer intento, sin pedir un segundo acceso distinto.

## Assumptions

- Hay un solo acceso activo y una sola base activa para toda la suite local. Syquo y Datia se conectan a esa misma base. No se pide, en esta entrega, un acceso o una base distintos por cliente o por empresa.
- La elección de empresa o compañía dentro de la base activa sigue viviendo en cada aplicación.
- Hasta que el responsable guarde el primer acceso en Devia, Syquo y Datia pueden seguir trabajando con el acceso que ya tuvieran. En cuanto existe un acceso de suite, ese pasa a ser el que se edita y el que ambas usan.
- Datia no modifica los datos de empresa. Syquo puede seguir preparando la salida contable hacia el ERP.
- Okia y el CRM quedan fuera de esta entrega, aunque más adelante podrán usar el mismo acceso.
- Arrancar o parar las aplicaciones desde la página de Devia no forma parte de este cambio.
- Quien configura el acceso en Devia es la misma persona que usa Syquo y Datia en este equipo.
