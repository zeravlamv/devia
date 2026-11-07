# Research: Conexión compartida de la suite

## 1. Dónde vive el acceso

**Decision**: Devia escribe un único fichero local. Syquo y Datia lo leen. No se copia el secreto a la configuración propia de cada aplicación.

**Rationale**: Son tres procesos distintos. Un fichero sigue disponible aunque la página de Devia esté cerrada, y un cambio se ve en el siguiente uso sin empujar nada a las pantallas ya abiertas. Guardarlo otra vez en Syquo y en Datia volvería a crear dos verdades.

**Alternatives considered**:
- Que Devia llame a cada aplicación y reescriba su configuración: el secreto queda duplicado y hay que tener las dos en marcha para guardar.
- Un servicio de red en el puerto 8090: si el lanzador está cerrado, Syquo y Datia se quedan sin acceso.

## 2. Protección del secreto

**Decision**: El secreto se guarda cifrado con la protección de datos de Windows del usuario de la sesión (DPAPI). El fichero en claro no contiene la contraseña. Ni la página de Devia ni Syquo ni Datia la vuelven a mostrar.

**Rationale**: El equipo es de una sola persona. DPAPI impide que copiar el fichero a otra cuenta de Windows sirva para leer el secreto, sin añadir un servicio ni una clave compartida en el repositorio.

**Alternatives considered**:
- Texto plano en el fichero: basta con abrir el archivo para ver el secreto.
- Reutilizar el cifrado interno de Syquo: Datia y Devia no lo comparten, y el secreto seguiría atado a una sola aplicación.

## 3. Qué gana el fichero de la suite

**Decision**: Si el fichero existe y tiene servidor, usuario y base activa, ese origen manda sobre la configuración de administración y sobre las variables de entorno. Si el fichero no existe, Syquo y Datia siguen como hoy.

**Rationale**: La spec permite el acceso anterior hasta el primer guardado. A partir de ahí la suite es la única puerta.

**Alternatives considered**:
- Borrar de inmediato la configuración vieja al instalar el cambio: cortaría el trabajo antes de que el responsable haya guardado nada en Devia.
- Dejar que la configuración de cada aplicación pueda tapar a la suite: el cambio en Devia no llegaría a las dos.

## 4. Cómo se listan las bases

**Decision**: Devia se conecta al servidor con el acceso guardado, pide las bases que ese usuario puede usar y excluye las de sistema (`master`, `tempdb`, `model`, `msdb`). El tiempo de espera de la comprobación es de 5 segundos. Cada base se distingue por su nombre y, si hiciera falta, por su identificador interno.

**Rationale**: Es el mismo criterio que Datia ya usa para no ofrecer bases de sistema. El límite de 5 segundos evita una pantalla que no termina.

**Alternatives considered**:
- Listar también `master`: no es una base de trabajo de la empresa.
- Sin límite de espera: choca con el caso de un servidor que no responde.

## 5. Qué no se mueve a Devia

**Decision**: La compañía o empresa dentro de la base sigue eligiéndose en Syquo y en Datia. La tabla de fórmulas de Syquo sigue en Syquo. Datia no gana permiso de escritura. Syquo conserva la preparación de la salida contable. Okia y el CRM no leen el fichero en esta entrega.

**Rationale**: La spec separa la puerta común de la especialidad de cada aplicación.

**Alternatives considered**:
- Elegir también la empresa en Devia: la spec lo deja fuera.
- Un usuario de solo lectura para Datia y otro de escritura para Syquo: el responsable pidió una sola conexión y una sola base.

## 6. Cuándo ven el cambio las aplicaciones

**Decision**: Cada uso nuevo de Syquo o Datia vuelve a leer el fichero. Lo que ya está pintado en una pantalla abierta no se reescribe solo.

**Rationale**: Coincide con el caso límite de la spec: el trabajo en curso no cambia a mitad de pantalla; el siguiente uso ya va al origen nuevo.

**Alternatives considered**:
- Avisar a los procesos en caliente: exige que las dos estén arrancadas y complica el lanzador sin cambiar el resultado pedido.
