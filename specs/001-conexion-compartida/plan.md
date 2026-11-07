# Implementation Plan: Conexión compartida de la suite

**Branch**: `feature/conexion-compartida` | **Date**: 2026-11-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-conexion-compartida/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Devia pasa a ser el único sitio donde se registra el acceso al servidor de datos y la base activa. Syquo y Datia leen ese acceso en el siguiente uso y dejan de pedir el suyo. Cada una sigue agrupando y mostrando los datos según su especialidad, y la compañía dentro de la base se sigue eligiendo en la aplicación.

El acceso vive en un fichero local escrito solo por Devia. El secreto va protegido con la protección de datos de Windows del usuario de la sesión. Si el fichero aún no existe, Syquo y Datia conservan su comportamiento actual.

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: Biblioteca estándar para la página de Devia; `pyodbc` y ODBC Driver 18 para hablar con el servidor; protección de datos de Windows (DPAPI) para el secreto. Syquo y Datia siguen en Django.

**Storage**: Un fichero JSON en `%LOCALAPPDATA%\devia\conexion.json`. No se añade una base propia de la suite. La base de la empresa sigue en SQL Server. Syquo conserva Postgres o SQLite en local y SQL Server en producción para lo suyo; Datia igual para lo suyo. Ese almacenamiento no guarda el acceso de la suite.

**Testing**: Pruebas de unidad del fichero y de la resolución en Syquo (`pytest` o el ejecutor que ya usa) y en Datia. La comprobación de punta a punta está en [quickstart.md](quickstart.md).

**Target Platform**: Windows 10 en este equipo. Devia en el puerto 8090. Syquo en el 8000. Datia en el 8001.

**Performance Goals**: Comprobar el acceso y ver el resultado en menos de 3 minutos. La llamada al servidor no espera más de 5 segundos.

**Constraints**: Un solo acceso y una sola base activa. El secreto no se muestra otra vez ni se escribe en claro. Okia y el CRM no cambian. La página de lanzamiento no gana ni pierde la función de arrancar aplicaciones. Lo ya pintado en una pantalla abierta no se reescribe solo.

**Scale/Scope**: Una persona, un equipo, dos aplicaciones consumidoras. La lista de bases es la que ese usuario puede ver, sin las de sistema.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

La constitución de Devia sigue siendo la plantilla sin principios ratificados. No hay una puerta de gobierno que esta entrega pueda incumplir.

| Puerta | Antes del diseño | Después del diseño |
|--------|------------------|--------------------|
| Principios ratificados | Pasa: no hay ninguno vigente | Pasa: el diseño no inventa un segundo servicio ni mueve la especialidad de cada aplicación |
| Alcance de la spec | Pasa: una puerta, una base, dos aplicaciones | Pasa: el fichero y los dos lectores cubren los requisitos sin añadir Okia ni el CRM |

No hay violaciones que justificar.

## Project Structure

### Documentation (this feature)

```text
specs/001-conexion-compartida/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── conexion-suite.md
└── tasks.md             # lo crea /speckit-tasks, no este comando
```

### Source Code (repository root)

```text
devia/
├── lanzador.py          # guarda, comprueba, elige la base y retira el fichero
└── index.html           # formulario del acceso junto a las tarjetas

Syquo (F:\priveria\tatai\)
└── ai_config/mssql_resolver.py
    # si el fichero existe, gana sobre administración y entorno

Datia (F:\datia\)
└── datia/services/runtime_config.py
    # si el fichero existe, mssql_params usa ese acceso y esa base
```

**Structure Decision**: El cambio de cara está en Devia, que hoy es una página y un lanzador. La lectura se engancha en el punto único que cada aplicación ya usa para resolver el servidor: `resolve_mssql_config` en Syquo y `mssql_params` en Datia. La compañía dentro de la base, la tabla de fórmulas y las pantallas de especialidad no se mueven.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No aplica. La constitución no impone una puerta incumplida.
