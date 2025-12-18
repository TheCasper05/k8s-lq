from __future__ import annotations

from fastapi import FastAPI

from src.config import settings
from src.container import Container
from src.interfaces.api.v1 import (
    audio_routes,
    chat_routes,
    conversation_routes,
    curriculum_routes,
    rubric_routes,
    scenario_routes,
    translation_routes,
)


def create_app() -> FastAPI:
    """Crea y configura la aplicación FastAPI."""
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="LingoBot - Servicio de audio y conversación con IA",
    )

    # Configurar container de dependencias
    container = Container()
    container.wire(
        modules=[
            chat_routes,
            audio_routes,
            translation_routes,
            curriculum_routes,
            rubric_routes,
            scenario_routes,
        ]
    )

    # Agregar container a la app para acceder desde otros lugares si es necesario
    app.container = container  # type: ignore

    # Health check
    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    # Registrar routers
    app.include_router(chat_routes.router, prefix="/api/v1")
    app.include_router(conversation_routes.router, prefix="/api/v1")
    app.include_router(audio_routes.router, prefix="/api/v1")
    app.include_router(translation_routes.router, prefix="/api/v1")
    app.include_router(curriculum_routes.router, prefix="/api/v1")
    app.include_router(rubric_routes.router, prefix="/api/v1")
    app.include_router(scenario_routes.router, prefix="/api/v1")

    return app


app = create_app()
