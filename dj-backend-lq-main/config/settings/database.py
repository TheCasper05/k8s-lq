"""
Database configuration.
"""

from config.settings.base import env

database_url = env("DATABASE_URL", default="sqlite:///db.sqlite3")

if database_url.startswith("sqlite"):
    DATABASES = {
        "default": env.db(),
    }
else:
    # PostgreSQL configuration for production
    # Parse database configurations
    default_db_config = env.db()
    replica_db_config = (
        env.db("REPLICA_DB_URL") if env("REPLICA_DB_URL") != "" else env.db()
    )

    if "OPTIONS" not in default_db_config:
        default_db_config["OPTIONS"] = {}
    default_db_config["OPTIONS"]["options"] = "-c search_path=lq"

    DATABASES = {
        "replica": replica_db_config,
        "default": default_db_config,
    }

    # Esta linea se usa para que pgbouncer (El conection pooler) maneje las conexiones en vez de django
    DATABASES["default"]["CONN_MAX_AGE"] = 0
    DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = True

    DATABASES["replica"]["CONN_MAX_AGE"] = 0
    DATABASES["replica"]["DISABLE_SERVER_SIDE_CURSORS"] = True

    DATABASE_ROUTERS = ["config.db_router.ReadReplicaRouter"]

# ===================================================
# Session Configuration - Using Redis + PostgreSQL (hybrid)
# ===================================================
# cached_db: Usa Redis como cache rápido pero persiste en DB como backup
# Esto previene pérdida de sesiones si Redis se reinicia
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"

# Configuración del tiempo de vida de las sesiones
SESSION_COOKIE_AGE = 1209600  # 2 semanas en segundos (14 días)
SESSION_SAVE_EVERY_REQUEST = False  # Solo actualiza si hay cambios (ahorra writes)
SESSION_COOKIE_HTTPONLY = True  # Seguridad: JavaScript no puede acceder
SESSION_COOKIE_SECURE = env(
    "SESSION_COOKIE_SECURE", default=True
)  # Solo HTTPS en producción
SESSION_COOKIE_SAMESITE = "Lax"  # Protección CSRF
