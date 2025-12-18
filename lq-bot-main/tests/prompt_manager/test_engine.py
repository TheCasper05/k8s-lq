import pytest

from src.prompt_manager.exceptions import (
    InvalidPromptFormatError,
    MissingTemplateVariablesError,
)
from src.prompt_manager.templates.engine import TemplateEngine


def test_render_ok():
    eng = TemplateEngine()
    out = eng.render("Hola {name}", name="Martín")
    assert out == "Hola Martín"


def test_missing_vars_raises():
    eng = TemplateEngine()
    with pytest.raises(MissingTemplateVariablesError) as e:
        eng.render("Hi {who} and {when}", who="you")
    assert "when" in ",".join(sorted(e.value.missing))


def test_invalid_placeholder_attr():
    eng = TemplateEngine()
    with pytest.raises(InvalidPromptFormatError):
        eng.render("Bad {obj.attr}", obj={"attr": "x"})
