# 📦 Documentación del Storage con Boto3

Adapter de almacenamiento de objetos compatible con AWS S3 y DigitalOcean Spaces siguiendo **Arquitectura Hexagonal**.

---

## 📋 Descripción General

El módulo de storage implementa el patrón de **Arquitectura Hexagonal** (Ports and Adapters) para mantener la lógica de negocio independiente de la implementación de almacenamiento.

**Componentes:**
- **FileStoragePort**: Interface (Port) que define el contrato de almacenamiento
- **BotoSettings**: Configuración para boto3 usando pydantic
- **Boto3StorageAdapter**: Implementación del port usando boto3 (AWS S3 / DO Spaces)

**Ubicaciones:**
- Port: `src/domain/ports/storage/file_storage_port.py`
- Config: `src/config.py` (BotoSettings)
- Adapter: `src/infrastructure/adapters/storage/boto3_storage_adapter.py`

---

## ⚙️ Configuración

### Variables de Entorno

El adapter se configura mediante variables de entorno con el prefijo `LQBOT_`:

#### Variables Requeridas (para AWS S3)
```env
LQBOT_AWS_ACCESS_KEY_ID=tu_access_key
LQBOT_AWS_SECRET_ACCESS_KEY=tu_secret_key
LQBOT_AWS_S3_REGION_NAME=us-east-1  # o usa LQBOT_AWS_REGION como fallback
```

#### Variables Opcionales
```env
# Para DigitalOcean Spaces (o S3-compatible)
LQBOT_S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com

# Bucket por defecto
LQBOT_S3_BUCKET_DEFAULT=mi-bucket

# Configuración de timeouts y reintentos
LQBOT_S3_MAX_ATTEMPTS=3
LQBOT_S3_CONNECT_TIMEOUT=5
LQBOT_S3_READ_TIMEOUT=60
```

#### Prioridad de Variables de Región
1. `LQBOT_AWS_S3_REGION_NAME` (tiene prioridad)
2. `LQBOT_AWS_REGION` (fallback)
3. `us-east-1` (valor por defecto)

---

## 🏗️ Arquitectura Hexagonal

```
Domain Layer (Ports)
    │
    ├─ FileStoragePort (interface abstracta)
    │      ├─ save_file() / save_file_sync()
    │      ├─ get_file() / get_file_sync()
    │      ├─ delete_file() / delete_file_sync()
    │      ├─ file_exists() / file_exists_sync()
    │      ├─ download_to_path()
    │      └─ generate_presigned_url()
    │
    ↓ implements
    │
Infrastructure Layer (Adapters)
    │
    └─ Boto3StorageAdapter (implementación)
           ├─ Usa BotoSettings (config)
           └─ Usa boto3 directamente
```

---

## 📦 Componentes

### 1. BotoSettings (Configuración)

`pydantic.BaseModel` que encapsula la configuración de boto3.

**Ubicación:** `src/config.py`

```python
from src.config import BotoSettings, Settings

# Opción 1: Crear desde Settings (recomendado)
settings = Settings()
boto_settings = settings.get_boto_settings()

# Opción 2: Crear manualmente
boto_settings = BotoSettings(
    access_key="tu_key",
    secret_key="tu_secret",
    region="us-east-1",
    endpoint_url=None,  # None para AWS S3, URL para DO Spaces
    default_bucket="mi-bucket",
    max_attempts=3,
    connect_timeout=5,
    read_timeout=60,
)
```

**Campos:**
- `access_key` (str): Access key ID
- `secret_key` (str): Secret access key
- `region` (str): Región del servicio (default: "us-east-1")
- `endpoint_url` (str | None): URL del endpoint (None para AWS S3)
- `default_bucket` (str | None): Bucket por defecto
- `max_attempts` (int): Reintentos (default: 3)
- `connect_timeout` (int): Timeout conexión en segundos (default: 5)
- `read_timeout` (int): Timeout lectura en segundos (default: 60)

---

### 2. FileStoragePort (Interface)

Port que define el contrato de almacenamiento.

**Ubicación:** `src/domain/ports/storage/file_storage_port.py`

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

class FileStoragePort(ABC):
    """Port para gestión de archivos."""

    # Métodos asíncronos
    @abstractmethod
    async def save_file(self, file_data: bytes, file_name: str,
                       folder: str | None = None,
                       metadata: dict[str, Any] | None = None) -> str: ...

    @abstractmethod
    async def get_file(self, file_id: str) -> bytes: ...

    @abstractmethod
    async def delete_file(self, file_id: str) -> bool: ...

    @abstractmethod
    async def file_exists(self, file_id: str) -> bool: ...

    # Métodos síncronos
    @abstractmethod
    def save_file_sync(self, file_data: bytes, file_name: str, ...) -> str: ...

    @abstractmethod
    def get_file_sync(self, file_id: str) -> bytes: ...

    @abstractmethod
    def delete_file_sync(self, file_id: str) -> bool: ...

    @abstractmethod
    def file_exists_sync(self, file_id: str) -> bool: ...

    # Métodos adicionales
    @abstractmethod
    def download_to_path(self, file_id: str, destination: str | Path) -> Path: ...

    @abstractmethod
    def generate_presigned_url(self, file_id: str, expires_in: int = 3600) -> str: ...
```

---

### 3. Boto3StorageAdapter (Implementación)

Adapter que implementa `FileStoragePort` usando boto3.

**Ubicación:** `src/infrastructure/adapters/storage/boto3_storage_adapter.py`

```python
from src.config import BotoSettings
from src.infrastructure.adapters.storage.boto3_storage_adapter import Boto3StorageAdapter

# Crear adapter
boto_settings = BotoSettings(
    access_key="key",
    secret_key="secret",
    region="us-east-1",
    default_bucket="mi-bucket"
)
adapter = Boto3StorageAdapter(boto_settings)
```

**Características:**
- ✅ Implementa todos los métodos del port
- ✅ Métodos asíncronos usando `asyncio.to_thread()`
- ✅ Métodos síncronos para casos sin async
- ✅ Construye cliente boto3 internamente
- ✅ Streaming para archivos grandes
- ✅ URLs firmadas temporales
- ✅ Manejo de errores robusto

---

## 📚 API del Adapter

### Métodos Asíncronos (Core)

#### `async save_file(file_data: bytes, file_name: str, folder: str | None = None, metadata: dict | None = None) -> str`

Guarda un archivo en S3 y retorna su key.

```python
# Guardar archivo
key = await adapter.save_file(
    file_data=b"contenido del archivo",
    file_name="documento.pdf",
    folder="uploads/2024",
    metadata={"user_id": "123", "type": "pdf"}
)
# Retorna: "uploads/2024/documento.pdf"
```

#### `async get_file(file_id: str) -> bytes`

Obtiene los datos de un archivo.

```python
# Obtener contenido
content = await adapter.get_file("uploads/2024/documento.pdf")
```

#### `async delete_file(file_id: str) -> bool`

Elimina un archivo.

```python
# Eliminar archivo
deleted = await adapter.delete_file("uploads/2024/documento.pdf")
# Retorna: True si se eliminó, False en caso de error
```

#### `async file_exists(file_id: str) -> bool`

Verifica si un archivo existe.

```python
# Verificar existencia
exists = await adapter.file_exists("uploads/2024/documento.pdf")
```

---

### Métodos Síncronos

Los mismos métodos pero con sufijo `_sync` para casos sin async:

```python
# Guardar síncrono
key = adapter.save_file_sync(file_data, "file.pdf")

# Obtener síncrono
content = adapter.get_file_sync(key)

# Eliminar síncrono
deleted = adapter.delete_file_sync(key)

# Verificar síncrono
exists = adapter.file_exists_sync(key)
```

---

### Métodos Adicionales

#### `download_to_path(file_id: str, destination: str | Path, bucket: str | None = None) -> Path`

Descarga un archivo a una ruta local usando streaming.

```python
from pathlib import Path

# Descargar archivo
file_path = adapter.download_to_path(
    "uploads/file.pdf",
    Path("/tmp/downloaded.pdf")
)

# Con bucket personalizado
file_path = adapter.download_to_path(
    "file.pdf",
    "/tmp/file.pdf",
    bucket="custom-bucket"
)
```

**Características:**
- Streaming de datos (chunks de 1MB)
- Crea directorios automáticamente
- No carga todo en memoria

#### `generate_presigned_url(file_id: str, expires_in: int = 3600, bucket: str | None = None) -> str`

Genera URL firmada temporal.

```python
# URL válida por 1 hora (default)
url = adapter.generate_presigned_url("uploads/file.pdf")

# URL válida por 24 horas
url = adapter.generate_presigned_url("file.pdf", expires_in=86400)

# Con bucket personalizado
url = adapter.generate_presigned_url(
    "file.pdf",
    expires_in=3600,
    bucket="custom-bucket"
)
```

---

## 🔌 Integración con Container

El adapter está integrado en el sistema de inyección de dependencias:

```python
from src.container import Container

# Obtener adapter desde el container
storage = Container.storage_adapter()

# Usar el adapter
key = await storage.save_file(file_data, "file.pdf", folder="uploads")
content = await storage.get_file(key)
```

**Configuración en Container:**
```python
# src/container.py
from src.infrastructure.adapters.storage.factory import StorageProviderFactory

storage_factory = providers.Singleton(StorageProviderFactory, settings=config)

storage_adapter = providers.Factory(
    lambda factory: factory.create_storage_adapter(),
    factory=storage_factory
)
```

**Factory Pattern:**
```python
# src/infrastructure/adapters/storage/factory.py
class StorageProviderFactory:
    def create_storage_adapter(self, provider: str | None = None) -> FileStoragePort:
        provider = provider or self.settings.storage_provider

        if provider == "boto3":
            boto_settings = self.settings.get_boto_settings()
            return Boto3StorageAdapter(boto_settings=boto_settings)

        raise ValueError(f"Proveedor '{provider}' no soportado")
```

---

## 📝 Ejemplos de Uso

### Ejemplo 1: Guardar y obtener archivo (Async)

```python
from src.container import Container

storage = Container.storage_adapter()

# Guardar
file_data = b"contenido del archivo"
key = await storage.save_file(
    file_data=file_data,
    file_name="documento.pdf",
    folder="uploads/2024",
    metadata={"user_id": "123"}
)

# Obtener
content = await storage.get_file(key)
assert content == file_data
```

### Ejemplo 2: Verificar y eliminar (Async)

```python
from src.container import Container

storage = Container.storage_adapter()

key = "uploads/2024/documento.pdf"

# Verificar existencia
if await storage.file_exists(key):
    # Eliminar
    deleted = await storage.delete_file(key)
    print(f"Eliminado: {deleted}")
```

### Ejemplo 3: Descargar archivo local

```python
from src.container import Container
from pathlib import Path

storage = Container.storage_adapter()

# Descargar usando streaming
file_path = storage.download_to_path(
    "uploads/large_file.pdf",
    Path("/tmp/large_file.pdf")
)

print(f"Descargado en: {file_path}")
```

### Ejemplo 4: Generar URL para descarga directa

```python
from src.container import Container

storage = Container.storage_adapter()

# Generar URL firmada (válida por 1 hora)
url = storage.generate_presigned_url(
    "uploads/documento.pdf",
    expires_in=3600
)

# Enviar URL al cliente para descarga directa
return {"download_url": url}
```

### Ejemplo 5: Uso síncrono

```python
from src.container import Container

storage = Container.storage_adapter()

# Operaciones síncronas (sin async/await)
key = storage.save_file_sync(b"content", "file.txt", folder="docs")
content = storage.get_file_sync(key)
exists = storage.file_exists_sync(key)
deleted = storage.delete_file_sync(key)
```

---

## 🌍 Compatibilidad

### AWS S3

Para usar con AWS S3, no definas `S3_ENDPOINT_URL`:

```env
LQBOT_AWS_ACCESS_KEY_ID=tu_key
LQBOT_AWS_SECRET_ACCESS_KEY=tu_secret
LQBOT_AWS_S3_REGION_NAME=us-east-1
LQBOT_S3_BUCKET_DEFAULT=mi-bucket
```

### DigitalOcean Spaces

Para usar con DigitalOcean Spaces, define el `S3_ENDPOINT_URL`:

```env
LQBOT_AWS_ACCESS_KEY_ID=tu_spaces_key
LQBOT_AWS_SECRET_ACCESS_KEY=tu_spaces_secret
LQBOT_AWS_S3_REGION_NAME=nyc3
LQBOT_S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
LQBOT_S3_BUCKET_DEFAULT=mi-space
```

**Regiones comunes de DO Spaces:**
- `nyc3`: `https://nyc3.digitaloceanspaces.com`
- `ams3`: `https://ams3.digitaloceanspaces.com`
- `sgp1`: `https://sgp1.digitaloceanspaces.com`
- `sfo3`: `https://sfo3.digitaloceanspaces.com`

---

## 🔒 Seguridad

- ✅ Credenciales desde variables de entorno (nunca hardcodeadas)
- ✅ URLs firmadas con expiración configurable
- ✅ Timeouts para prevenir conexiones colgadas
- ✅ Reintentos automáticos para resiliencia

**Mejores Prácticas:**
- Nunca commitees credenciales en el código
- Usa variables de entorno o secret managers
- Configura timeouts apropiados según tu red
- Usa URLs firmadas con tiempos cortos cuando sea posible

---

## 🧪 Testing

Los tests cubren toda la funcionalidad del adapter.

**Ubicación:**
- `tests/unit/test_boto3_storage_adapter.py` (27 tests)
- `tests/unit/test_config_boto_settings.py` (7 tests)

**Ejecutar tests:**
```bash
# Tests del adapter
pytest tests/unit/test_boto3_storage_adapter.py -v

# Tests de configuración
pytest tests/unit/test_config_boto_settings.py -v

# Todos los tests
pytest -v
```

**Cobertura:**
- ✅ Métodos asíncronos (save, get, delete, exists)
- ✅ Métodos síncronos (save_sync, get_sync, etc.)
- ✅ Métodos adicionales (download_to_path, generate_presigned_url)
- ✅ Helpers internos (_get_bucket, _build_key)
- ✅ Manejo de errores y casos edge
- ✅ Configuración con BotoSettings
- ✅ Integración con Settings

---

## 🐛 Manejo de Errores

### Error: Bucket no especificado

```python
# Si no hay default_bucket
boto_settings = BotoSettings(access_key="key", secret_key="secret", region="us-east-1")
adapter = Boto3StorageAdapter(boto_settings)
await adapter.save_file(b"data", "file.txt")  # ValueError: Bucket no especificado
```

**Solución:**
```python
# Opción 1: Configurar default_bucket
boto_settings = BotoSettings(..., default_bucket="mi-bucket")

# Opción 2: Pasar bucket en métodos que lo soportan
adapter.download_to_path("file.txt", "/tmp/file.txt", bucket="mi-bucket")
```

### Error: Archivo no existe

```python
# file_exists() retorna False (no lanza excepción)
if not await adapter.file_exists("nonexistent.txt"):
    print("Archivo no encontrado")

# get_file() lanzará excepción de boto3
try:
    content = await adapter.get_file("nonexistent.txt")
except Exception as e:
    print(f"Error: {e}")
```

---

## 📚 Referencias

**Código fuente:**
- Port: [src/domain/ports/storage/file_storage_port.py](../src/domain/ports/storage/file_storage_port.py)
- Config: [src/config.py](../src/config.py) (BotoSettings)
- Adapter: [src/infrastructure/adapters/storage/boto3_storage_adapter.py](../src/infrastructure/adapters/storage/boto3_storage_adapter.py)
- Factory: [src/infrastructure/adapters/storage/factory.py](../src/infrastructure/adapters/storage/factory.py)

**Tests:**
- [tests/unit/test_boto3_storage_adapter.py](../tests/unit/test_boto3_storage_adapter.py)
- [tests/unit/test_config_boto_settings.py](../tests/unit/test_config_boto_settings.py)

**Documentación externa:**
- [boto3 S3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)
- [DigitalOcean Spaces](https://docs.digitalocean.com/products/spaces/)

---

## 🔄 Flujo Completo

```python
from src.container import Container
from pathlib import Path

# 1. Obtener adapter del container
storage = Container.storage_adapter()

# 2. Guardar archivo con metadata
key = await storage.save_file(
    file_data=b"contenido",
    file_name="documento.pdf",
    folder="uploads/2024",
    metadata={"user_id": "123", "type": "pdf"}
)

# 3. Verificar existencia
if await storage.file_exists(key):
    # 4a. Obtener contenido
    content = await storage.get_file(key)

    # 4b. Descargar a archivo local
    file_path = storage.download_to_path(key, Path("/tmp/documento.pdf"))

    # 4c. Generar URL para cliente
    url = storage.generate_presigned_url(key, expires_in=3600)

    # 5. Eliminar cuando ya no se necesite
    deleted = await storage.delete_file(key)
```

---

## 💡 Ventajas de esta Arquitectura

### ✅ Arquitectura Hexagonal Correcta
- **Port (FileStoragePort)**: Define el contrato
- **Adapter (Boto3StorageAdapter)**: Implementa el port
- Sin capas intermedias innecesarias

### ✅ Separation of Concerns
- **Domain**: Define qué se puede hacer (port)
- **Infrastructure**: Define cómo se hace (adapter)
- **Config**: Centraliza la configuración

### ✅ Testeable
- Fácil de mockear el port
- Tests unitarios del adapter con mocks de boto3
- 34 tests cubriendo todos los casos

### ✅ Flexible
- Cambiar de proveedor es trivial (nueva implementación del port)
- Sin cambios en la lógica de negocio
- Factory pattern para crear adapters

### ✅ API Completa
- Métodos asíncronos para FastAPI
- Métodos síncronos para scripts/CLI
- Métodos adicionales para casos específicos

---

## 🎯 Próximos Pasos

Para agregar un nuevo proveedor de storage (ej: Google Cloud Storage):

1. **Crear nuevo adapter:**
   ```python
   # src/infrastructure/adapters/storage/gcs_storage_adapter.py
   class GCSStorageAdapter(FileStoragePort):
       def __init__(self, gcs_settings: GCSSettings):
           # Implementar usando google-cloud-storage
           pass
   ```

2. **Actualizar factory:**
   ```python
   # src/infrastructure/adapters/storage/factory.py
   if provider == "gcs":
       return GCSStorageAdapter(...)
   ```

3. **Agregar configuración:**
   ```python
   # src/config.py
   class GCSSettings(BaseModel):
       project_id: str
       credentials_file: str
   ```

**Sin cambiar la lógica de negocio** que usa `FileStoragePort` ✨
