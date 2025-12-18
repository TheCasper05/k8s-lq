from __future__ import annotations

import string
from collections.abc import Iterable

from src.prompt_manager.exceptions import (
    InvalidPromptFormatError,
    MissingTemplateVariablesError,
)


class TemplateEngine:
    """
    Engine simple de plantillas basado en str.format() con validación estricta.
    - Placeholders soportados: {var}
    - No se permiten accesos complejos tipo {obj.attr} o {arr[0]} en v1.
    """

    def required_variables(self, template: str) -> set[str]:
        """
        Devuelve el conjunto de variables requeridas por el template.
        Lanza InvalidPromptFormatError si detecta placeholders no soportados.
        """
        try:
            required: set[str] = set()
            for _, field_name, _, _ in string.Formatter().parse(template):
                if not field_name:
                    continue
                # v1: sólo nombres planos (sin ".", "[" o "]")
                if any(ch in field_name for ch in (".", "[", "]")):
                    raise InvalidPromptFormatError(
                        f"Unsupported placeholder '{field_name}' in simple engine "
                        "(use flat names like {var})."
                    )
                required.add(field_name)
            return required
        except ValueError as e:  # errores de parseo del formato
            raise InvalidPromptFormatError(str(e)) from e

    def validate(self, template: str, provided_keys: Iterable[str]) -> None:
        """Valida que no falten variables requeridas."""
        needed = self.required_variables(template)
        provided = set(provided_keys)
        missing = needed - provided
        if missing:
            raise MissingTemplateVariablesError(missing)

    def render(self, template: str, **kwargs: object) -> str:
        """
        Renderiza el template con kwargs.
        - Valida variables faltantes antes de formatear.
        - Envuelve cualquier error de formateo como InvalidPromptFormatError.
        """
        self.validate(template, kwargs.keys())
        try:
            return template.format(**kwargs)
        except Exception as e:
            # Ej.: KeyError inesperado, ValueError de format spec, etc.
            raise InvalidPromptFormatError(str(e)) from e


# Punto de extensión para v2 (ej.: Jinja2). Mantiene la misma interfaz pública.
class Jinja2TemplateEngine(TemplateEngine):
    """
    Stub (no implementada en v1).
    En v2 podrías:
      - from jinja2 import Environment, StrictUndefined
      - env = Environment(undefined=StrictUndefined, autoescape=False, ...)
      - template = env.from_string(template_str)
      - template.render(**kwargs)
    """

    pass
