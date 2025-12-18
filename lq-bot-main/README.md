# LingoBot

Servicio para LingoQuesto que recibe peticiones HTTP y devuelve audios y respuestas generados. Implementado con FastAPI siguiendo los principios de la **Arquitectura Hexagonal** (también conocida como Arquitectura de Puertos y Adaptadores).

## 🎯 Propósito

LingoBot es un servicio backend que procesa solicitudes de generación de audio. El servicio está diseñado para ser independiente de frameworks, bases de datos y servicios externos, permitiendo cambiar estas implementaciones sin afectar la lógica de negocio.

## 🏗️ Arquitectura Hexagonal

Este proyecto sigue la **Arquitectura Hexagonal**, que separa la lógica de negocio de los detalles técnicos y de infraestructura. La arquitectura se organiza en las siguientes capas:

### 📁 Estructura del Proyecto

```
src
├── docs
├── src                  # Código fuente principal del proyecto.
│   ├── application      # Capa de aplicación: coordina casos de uso.  
│   │   └── use_cases    # Casos de uso (application service layer).  
│   ├── domain           # Capa de dominio: reglas de negocio puras, sin dependencias externas.
│   │   ├── exceptions   # Excepciones del dominio (errores modelados según reglas de negocio).
│   │   ├── models       # Entidades, Value Objects y modelos del dominio.
│   │   ├── ports        # Puertos (interfaces) que definen las dependencias que el dominio necesita.
│   │   │   ├── ai       # Puertos relacionados con IA (LLM, TTS, STT, embeddings, etc.).
│   │   │   ├── logging  # Puertos para sistema de logging dentro del dominio.
│   │   │   └── storage  # Puertos de almacenamiento (storage, files, S3, etc.).
│   │   └── services     # Servicios de dominio: lógica de negocio pura.
│   ├── infrastructure   # Capa de infraestructura: implementa los puertos con proveedores reales.
│   │   ├── adapters     # Adaptadores concretos para IA, storage, logging, etc.
│   │   │   ├── ai       # Adaptadores para proveedores de IA (implementan domain.ports.ai).
│   │   │   └── storage  # Adaptadores de almacenamiento (implementan domain.ports.storage).
│   │   ├── logging      # Sistema de logging de infraestructura (loggers, formatters, handlers).
│   │   └── repositories # Implementaciones de repositorios (DB, caching, etc.).
│   └── interfaces       # Interfaces públicas de entrada: API HTTP, controladores y middleware.
│       └── api
│           ├── dtos     # DTOs (Request/Response schemas).
│           ├── middleware  # Middleware global para autenticación, logs, rate-limit, etc.
│           └── v1          # Endpoints versionados de la API (v1).
└── tests                   # Tests del proyecto: pruebas unitarias e integración.
    ├── integration         # Pruebas de integración: API real, adaptadores, flujos completos.
    └── unit                # Pruebas unitarias: tests del dominio y casos de uso.
```

### 🔄 Flujo de la Arquitectura

1. **Domain** (Dominio): Contiene las entidades de negocio y los puertos (interfaces). Esta capa **no depende de nada** y representa el núcleo del negocio.
2. **Application** (Aplicación): Contiene los casos de uso que orquestan la lógica de negocio usando los puertos definidos en el dominio.
3. **Infrastructure** (Infraestructura): Implementa los puertos definidos en el dominio (bases de datos, servicios externos, sistemas de archivos, etc.).
4. **Interfaces** (Interfaces): Adaptadores de entrada/salida que conectan el mundo exterior con la aplicación (API REST, CLI, etc.).

### 🎨 Ventajas de esta Arquitectura

- **Testabilidad**: La lógica de negocio puede probarse sin necesidad de bases de datos o servicios externos.
- **Independencia**: El dominio no depende de frameworks o librerías externas.
- **Flexibilidad**: Fácil cambiar implementaciones (ej: cambiar de SQLite a PostgreSQL) sin afectar el dominio.
- **Mantenibilidad**: Separación clara de responsabilidades facilita el mantenimiento.

## 📦 Estado Actual del Proyecto

### ✅ Implementado

- **Estructura base** de Arquitectura Hexagonal
- **FastAPI** configurado con punto de entrada en `main.py`
- **Sistema de configuración** con `pydantic-settings` (archivo `.env` compatible)
- **Endpoint de health check** (`GET /health`)
- **Tests básicos** para el endpoint de health
- **Configuración de herramientas**:
  - `uv` para gestión de dependencias
  - `Ruff` para linting y formateo
  - `pytest` para testing

### 🚧 Pendiente de Implementar

- **Domain**: Modelos y puertos para la generación de audio
- **Application**: Casos de uso para procesar solicitudes de audio
- **Infrastructure**: Repositorios para almacenamiento y servicios de TTS/generación de audio
- **Interfaces**: Endpoints para recibir peticiones y devolver audios

## 🛠️ Tecnologías

- **Python 3.11+**
- **FastAPI**: Framework web moderno y rápido
- **Pydantic**: Validación de datos y configuración
- **uv**: Gestor de paquetes rápido y moderno
- **Ruff**: Linter y formateador ultra-rápido
- **pytest**: Framework de testing

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.11 o superior
- `uv` instalado ([instrucciones](https://github.com/astral-sh/uv))

### Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/LingoQuesto/lq-bot
cd lq-bot
```

2. Inicializar el entorno virtual e instalar dependencias:
```bash
make init
```

O manualmente:
```bash
uv venv
uv sync --all-extras --group dev
```

### Ejecutar la Aplicación

```bash
make run
```

O manualmente:
```bash
uv run uvicorn lq_bot.main:app --reload --host 0.0.0.0 --port 8081
```

La aplicación estará disponible en `http://localhost:8081`

### Documentación de la API

Una vez ejecutando, puedes acceder a:
- **Swagger UI**: `http://localhost:8081/docs`
- **ReDoc**: `http://localhost:8081/redoc`

## 📋 Comandos Disponibles

El proyecto incluye un `Makefile` con comandos útiles:

| Comando | Descripción |
|---------|-------------|
| `make init` | Crea el entorno virtual e instala todas las dependencias |
| `make run` | Ejecuta la aplicación en modo desarrollo (con auto-reload) |
| `make test` | Ejecuta todos los tests |
| `make lint` | Ejecuta el linter (Ruff) |
| `make format` | Formatea el código con Ruff |
| `make check` | Ejecuta lint y tests (sin formatear) |
| `make qa` | Ejecuta format, lint y tests |
| `make dev` | Ejecuta qa y luego inicia el servidor |

## 🧪 Testing

Ejecutar tests:
```bash
make test
```

O manualmente:
```bash
uv run pytest
```

## 🔧 Configuración

La configuración se gestiona mediante variables de entorno. Crea un archivo `.env` en la raíz del proyecto:

```env
APP_NAME=lq-bot
ENVIRONMENT=local
LOG_LEVEL=INFO
```

Las configuraciones disponibles están definidas en `src/lq_bot/config.py`.

## 📝 Estructura de Archivos Clave

- **`src/lq_bot/main.py`**: Punto de entrada de la aplicación FastAPI
- **`src/lq_bot/config.py`**: Configuración de la aplicación usando Pydantic Settings
- **`src/lq_bot/domain/`**: Entidades y contratos (puertos) del dominio
- **`src/lq_bot/application/use_cases/`**: Casos de uso de la aplicación
- **`src/lq_bot/infrastructure/repositories/`**: Implementaciones de repositorios
- **`src/lq_bot/interfaces/api/routers/`**: Routers de FastAPI
- **`tests/`**: Tests de la aplicación
- **`pyproject.toml`**: Dependencias y configuración del proyecto
- **`ruff.toml`**: Configuración de Ruff (linter/formateador)

## 🔄 Próximos Pasos

Para continuar el desarrollo:

1. **Definir entidades de dominio** en `domain/models.py`
2. **Definir puertos** (interfaces) en `domain/ports.py` para servicios de audio
3. **Implementar casos de uso** en `application/use_cases/`
4. **Implementar repositorios** en `infrastructure/repositories/` (ej: servicio de TTS)
5. **Crear endpoints** en `interfaces/api/routers/` para recibir peticiones y devolver audios
6. **Conectar todo** en `main.py` mediante inyección de dependencias

## 📄 Licencia

[Especificar licencia si aplica]

## 👥 Contribuidores

- Martin Ubaque
docker build . -t registry.digitalocean.com/lq-registry/lq-bot:qa-latest

docker push registry.digitalocean.com/lq-registry/lq-bot:qa-latest