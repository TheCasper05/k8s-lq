import logging

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from src.infrastructure.adapters.logging.structured_logger import StructuredLogger

from src.domain.ports.logging.logger_port import LoggerPort


class SentryLogger(LoggerPort):
    """Logger que envía eventos a Sentry además de logging local."""

    def __init__(
        self,
        base_logger: StructuredLogger,
        sentry_dsn: str,
        environment: str,
        traces_sample_rate: float = 0.1,
    ):
        self.base_logger = base_logger

        # Inicializar Sentry
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=environment,
            traces_sample_rate=traces_sample_rate,
            integrations=[
                LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
            ],
            send_default_pii=False,
            max_breadcrumbs=50,
        )

    def error(self, message: str, exception: Exception | None = None, **context):
        # Log local
        self.base_logger.error(message, exception=exception, **context)

        # Enviar a Sentry con contexto
        with sentry_sdk.push_scope() as scope:
            # Agregar contexto a Sentry
            for key, value in context.items():
                scope.set_context(key, {"value": value})

            if exception:
                sentry_sdk.capture_exception(exception)
            else:
                sentry_sdk.capture_message(message, level="error")

    def critical(self, message: str, exception: Exception | None = None, **context):
        # Log local
        self.base_logger.critical(message, exception=exception, **context)

        # Enviar a Sentry
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_context(key, {"value": value})

            if exception:
                sentry_sdk.capture_exception(exception)
            else:
                sentry_sdk.capture_message(message, level="fatal")

    # Delegar otros métodos al base_logger
    def trace(self, message: str, **context):
        self.base_logger.trace(message, **context)

    def debug(self, message: str, **context):
        self.base_logger.debug(message, **context)

    def info(self, message: str, **context):
        self.base_logger.info(message, **context)

    def success(self, message: str, **context):
        self.base_logger.success(message, **context)

    def warning(self, message: str, **context):
        self.base_logger.warning(message, **context)
        # Opcionalmente enviar warnings a Sentry como breadcrumbs
        sentry_sdk.add_breadcrumb(
            category="warning", message=message, level="warning", data=context
        )

    def with_context(self, **context):
        return SentryLogger(
            base_logger=self.base_logger.with_context(**context),
            sentry_dsn="",  # Ya inicializado
            environment=self.base_logger.environment,
        )

    def start_span(self, operation: str, **context):
        # Crear span de Sentry también
        with sentry_sdk.start_span(op=operation, description=operation):
            return self.base_logger.start_span(operation, **context)
