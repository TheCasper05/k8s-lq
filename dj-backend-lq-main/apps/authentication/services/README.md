# Authentication Services

Este módulo contiene la lógica de negocio separada de los modelos para mantener una arquitectura limpia y escalable.

## Estructura

```
services/
├── __init__.py              # Exports públicos
├── invitation_validators.py # Validación de invitaciones
├── license_service.py       # Interfaz y servicio de licencias
└── README.md               # Esta documentación
```

## InvitationValidator

Servicio que encapsula toda la lógica de validación de invitaciones que anteriormente estaba en `Invitation.clean()`.

### Uso

El validador se usa automáticamente cuando se llama a `invitation.full_clean()` o `invitation.save()`.

```python
from authentication.models import Invitation

# La validación se ejecuta automáticamente
invitation = Invitation(
    email="user@example.com",
    workspace=workspace,
    role="teacher"
)
invitation.save()  # Valida automáticamente
```

### Validaciones incluidas

- Expiración por defecto (7 días si no se especifica)
- Validación de fecha de expiración (debe ser futura)
- Permisos del creador (estudiantes no pueden crear invitaciones)
- Permisos de actualización (solo el creador o el invitado pueden modificar)
- Validación de cambios de estado
- Actualización automática de timestamps según el estado
- Validación de disponibilidad de licencias (extensión)

## LicenseService

Interfaz abstracta para la gestión de licencias. Permite integrar la lógica de licencias de forma plug-and-play sin romper el código existente.

### Implementación actual (Stub)

Por defecto, el sistema usa `StubLicenseService` que siempre permite invitaciones. Esto permite que el sistema funcione mientras se implementa la lógica real de licencias.

### Cómo implementar un servicio de licencias real

#### 1. Crear tu implementación

```python
# apps/billing/services/license_service.py
from authentication.services.license_service import LicenseService
from django.contrib.auth import get_user_model

User = get_user_model()

class RealLicenseService(LicenseService):
    """Implementación real del servicio de licencias."""
    
    def check_availability(self, user, workspace, role, count=1):
        """
        Verifica si el usuario tiene licencias disponibles.
        
        Ejemplo de lógica:
        - Obtener el plan del usuario
        - Contar invitaciones activas
        - Verificar límites según el rol
        """
        # Tu lógica aquí
        user_plan = user.billing.plan
        active_invitations = Invitation.objects.filter(
            created_by=user,
            workspace=workspace,
            status='pending'
        ).count()
        
        max_invitations = user_plan.max_invitations
        return (active_invitations + count) <= max_invitations
    
    def reserve_seat(self, user, workspace, role, invitation_id=None):
        """
        Reserva una licencia cuando se crea una invitación.
        """
        # Tu lógica aquí
        LicenseSeat.objects.create(
            user=user,
            workspace=workspace,
            invitation_id=invitation_id,
            role=role,
            status='reserved'
        )
        return True
    
    def release_seat(self, user, workspace, role, invitation_id=None):
        """
        Libera una licencia cuando se cancela una invitación.
        """
        # Tu lógica aquí
        LicenseSeat.objects.filter(
            user=user,
            workspace=workspace,
            invitation_id=invitation_id
        ).update(status='released')
    
    def get_available_count(self, user, workspace, role):
        """
        Obtiene el número de licencias disponibles.
        """
        # Tu lógica aquí
        user_plan = user.billing.plan
        used = LicenseSeat.objects.filter(
            user=user,
            workspace=workspace,
            status='reserved'
        ).count()
        return max(0, user_plan.max_invitations - used)
```

#### 2. Registrar el servicio

**Opción A: En AppConfig.ready()**

```python
# apps/billing/apps.py
from django.apps import AppConfig
from authentication.services.license_service import set_license_service
from .services.license_service import RealLicenseService

class BillingConfig(AppConfig):
    name = 'billing'
    
    def ready(self):
        # Configurar el servicio de licencias
        set_license_service(RealLicenseService())
```

**Opción B: En settings**

```python
# config/settings/base.py
from authentication.services.license_service import set_license_service

# ... otras configuraciones ...

# Configurar servicio de licencias
if not settings.DEBUG:  # Solo en producción
    from billing.services.license_service import RealLicenseService
    set_license_service(RealLicenseService())
```

**Opción C: Lazy loading con función**

```python
# apps/billing/services/__init__.py
from authentication.services.license_service import LicenseService, set_license_service

def init_license_service():
    """Inicializa el servicio de licencias."""
    from .license_service_impl import RealLicenseService
    set_license_service(RealLicenseService())

# Llamar en AppConfig.ready()
```

### Integración automática

El servicio de licencias se integra automáticamente en:

1. **Validación de invitaciones**: `InvitationValidator` verifica disponibilidad antes de crear
2. **Reserva de licencias**: Se reserva automáticamente al crear una invitación
3. **Liberación de licencias**: Debe llamarse manualmente cuando se cancela/expira una invitación

### Ejemplo de liberación de licencias

```python
from authentication.services import get_license_service
from authentication.models import Invitation

# Cuando se cancela una invitación
invitation = Invitation.objects.get(pk=invitation_id)
invitation.status = InvitationStatus.REVOKED
invitation.save()

# Liberar la licencia
license_service = get_license_service()
license_service.release_seat(
    user=invitation.created_by,
    workspace=invitation.workspace,
    role=invitation.role,
    invitation_id=str(invitation.pk)
)
```

### Testing

El servicio puede ser fácilmente mockeado para tests:

```python
from unittest.mock import Mock
from authentication.services.license_service import set_license_service

class TestInvitation(TestCase):
    def setUp(self):
        # Mock del servicio de licencias
        mock_service = Mock()
        mock_service.check_availability.return_value = True
        mock_service.reserve_seat.return_value = True
        set_license_service(mock_service)
    
    def tearDown(self):
        from authentication.services.license_service import reset_license_service
        reset_license_service()
```

## Ventajas de esta arquitectura

1. **Separación de responsabilidades**: La lógica de negocio está separada de los modelos
2. **Testeable**: Cada servicio puede testearse independientemente
3. **Extensible**: Fácil agregar nuevas validaciones o servicios
4. **Plug-and-play**: El servicio de licencias puede cambiarse sin modificar código existente
5. **Mantenible**: Código más limpio y fácil de entender
6. **Escalable**: Fácil agregar nuevos servicios siguiendo el mismo patrón

## Próximos pasos

Cuando implementes la lógica de licencias:

1. Crea tu implementación de `LicenseService`
2. Regístrala usando `set_license_service()`
3. Implementa la lógica de reserva/liberación
4. Agrega tests para tu implementación
5. El sistema funcionará automáticamente sin cambios en el código de invitaciones

