# Celery Tasks Module

Este módulo centraliza todas las tareas asíncronas de Celery organizadas por dominio de negocio. La estructura está diseñada para ser escalable, mantenible y fácil de extender.

> **📖 Para información sobre workers escalables, deployment y Docker:**
> Ver [Guía de Workers de Celery](../../docs/CELERY_WORKERS.md)

## 📁 Estructura

```
apps/tasks/
├── __init__.py              # Importa todos los módulos para autodiscovery
├── README.md                # Esta documentación
├── tests/                   # Pruebas unitarias
│   ├── __init__.py
│   └── test_tasks.py
├── users/                   # Tareas relacionadas con usuarios
│   ├── __init__.py
│   └── tasks.py
├── institutions/            # Tareas relacionadas con instituciones
│   ├── __init__.py
│   └── tasks.py
├── scenarios/               # Tareas relacionadas con escenarios
│   ├── __init__.py
│   └── tasks.py
└── billing/                 # Tareas relacionadas con facturación
    ├── __init__.py
    └── tasks.py
```

## 🚀 Autodiscovery

Celery automáticamente detecta todas las tareas definidas en `apps/tasks/` gracias a la configuración en `config/celery.py`:

```python
app.autodiscover_tasks(["apps.tasks"])
```

Esto significa que cualquier tarea decorada con `@shared_task` en los archivos `tasks.py` de cada módulo será automáticamente registrada y disponible para ejecución.

## 📝 Crear una Nueva Tarea

### 1. Elegir el Módulo Correcto

Si la tarea pertenece a un dominio existente (users, institutions, scenarios, billing), agrega la tarea en el archivo `tasks.py` correspondiente.

Si necesitas crear un nuevo módulo:

```bash
mkdir apps/tasks/nuevo_modulo
touch apps/tasks/nuevo_modulo/__init__.py
touch apps/tasks/nuevo_modulo/tasks.py
```

Luego actualiza `apps/tasks/__init__.py` para importar el nuevo módulo:

```python
from apps.tasks import nuevo_modulo  # noqa: F401
```

### 2. Plantilla de Tarea Estándar

Usa esta plantilla como base para todas las nuevas tareas:

```python
"""
Tasks for [módulo] operations.
"""
import logging

from celery import shared_task

logger = logging.getLogger("lq.tasks")


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
    name="[modulo].[nombre_tarea]",
)
def mi_nueva_tarea(param1: str, param2: int, **kwargs):
    """
    Descripción clara de lo que hace la tarea.

    Args:
        param1: Descripción del parámetro 1
        param2: Descripción del parámetro 2
        **kwargs: Argumentos adicionales

    Returns:
        dict: Resultado de la ejecución con status y datos relevantes

    Raises:
        Exception: Descripción de posibles excepciones
    """
    try:
        logger.info(f"Executing [modulo].mi_nueva_tarea with param1={param1}, param2={param2}")
        
        # Implementar lógica de la tarea aquí
        # ...
        
        result = {
            "status": "success",
            "message": "Tarea completada exitosamente",
            # Agregar datos relevantes del resultado
        }
        
        logger.info(f"Task [modulo].mi_nueva_tarea completed successfully")
        return result
        
    except Exception as e:
        logger.error(
            f"Error in [modulo].mi_nueva_tarea: {str(e)}",
            exc_info=True,
            extra={
                "param1": param1,
                "param2": param2,
            }
        )
        raise
```

### 3. Parámetros del Decorador `@shared_task`

- **`autoretry_for`**: Tupla de excepciones que deben activar reintentos automáticos
- **`retry_backoff`**: Habilita backoff exponencial entre reintentos
- **`retry_jitter`**: Añade aleatoriedad al backoff para evitar thundering herd
- **`max_retries`**: Número máximo de reintentos (recomendado: 3)
- **`name`**: Nombre único de la tarea en formato `modulo.nombre_tarea`

### 4. Logging

Todas las tareas deben usar el logger `lq.tasks` que está configurado para escribir en `logs/tasks_errors.log`:

```python
logger = logging.getLogger("lq.tasks")
```

**Buenas prácticas de logging:**
- Usa `logger.info()` para eventos normales y progreso
- Usa `logger.error()` con `exc_info=True` para errores
- Incluye contexto relevante en los mensajes (IDs, parámetros importantes)
- Usa `extra={}` para metadata estructurada cuando sea útil

## 🧪 Pruebas Unitarias

Cada nueva tarea debe tener pruebas unitarias en `apps/tasks/tests/test_tasks.py` o en un archivo específico del módulo.

**Ejemplo de prueba mínima:**

```python
from unittest.mock import patch
from apps.tasks.[modulo].tasks import mi_nueva_tarea

@patch("apps.tasks.[modulo].tasks.logger")
def test_mi_nueva_tarea_success(mock_logger):
    """Test ejecución exitosa de mi_nueva_tarea."""
    result = mi_nueva_tarea("param1", 123)
    
    assert result["status"] == "success"
    mock_logger.info.assert_called_once()
    mock_logger.error.assert_not_called()
```

## 🔧 Ejecutar Tareas

### Usando Make (Recomendado)

```bash
# Iniciar todos los workers
make celery-start

# Ver estado
make celery-status

# Ver logs
make celery-logs

# Abrir Flower (monitoreo web)
make celery-flower

# Escalar workers
make celery-scale-default N=5
```

### En Desarrollo Local

```bash
# Worker
celery -A config worker --loglevel=info

# Beat (para tareas programadas)
celery -A config beat --loglevel=info
```

### Con Docker

```bash
# Workers con escalado (recomendado)
docker-compose -f docker-compose.celery.yml up -d

# O usar script de gestión
./scripts/celery-workers.sh start
```

### Desde el Código

```python
from apps.tasks.users.tasks import mi_tarea

# Ejecución asíncrona (recomendado)
result = mi_tarea.delay("arg1", "arg2", key="value")

# Ejecución síncrona (solo para testing)
result = mi_tarea("arg1", "arg2", key="value")
```

## 📋 Tareas Programadas (Celery Beat)

Para agregar una tarea programada, edita `config/settings/celery.py`:

```python
CELERY_BEAT_SCHEDULE = {
    "mi_tarea_periodica": {
        "task": "users.mi_tarea",
        "schedule": timedelta(hours=1),  # o crontab(hour=0, minute=0)
    },
}
```

## ✅ Checklist para Nueva Tarea

- [ ] Tarea creada en el módulo correcto
- [ ] Decorador `@shared_task` con parámetros estándar
- [ ] Nombre único en formato `modulo.nombre_tarea`
- [ ] Logger `lq.tasks` configurado
- [ ] Manejo de excepciones con logging
- [ ] Docstring descriptivo
- [ ] Pruebas unitarias creadas
- [ ] Tarea se puede importar sin side effects
- [ ] Si es periódica, agregada a `CELERY_BEAT_SCHEDULE`

## 🔍 Verificar que las Tareas se Registran

Para verificar que Celery detecta tus tareas:

```bash
# Listar todas las tareas registradas
celery -A config inspect registered
```

O desde Python:

```python
from celery import app
print(list(app.tasks.keys()))
```

## 🐛 Troubleshooting

### Las tareas no se detectan

1. Verifica que el módulo esté importado en `apps/tasks/__init__.py`
2. Verifica que el archivo `tasks.py` exista y tenga el decorador `@shared_task`
3. Reinicia el worker de Celery
4. Verifica que `config/celery.py` tenga `app.autodiscover_tasks(["apps.tasks"])`

### Errores de importación

- Asegúrate de que todas las dependencias estén disponibles cuando Celery importa las tareas
- Evita imports pesados o side effects en el nivel de módulo
- Usa imports lazy dentro de las funciones si es necesario

### Logs no aparecen en `logs/tasks_errors.log`

- Verifica que el directorio `logs/` exista y tenga permisos de escritura
- Verifica la configuración en `config/settings/logging.py`
- Asegúrate de usar `logger = logging.getLogger("lq.tasks")`

## 📚 Referencias

- [Documentación oficial de Celery](https://docs.celeryproject.org/)
- [Celery Best Practices](https://docs.celeryproject.org/en/stable/userguide/tasks.html#best-practices)
- [Django + Celery Integration](https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html)

