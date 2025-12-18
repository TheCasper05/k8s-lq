# src/interfaces/di_prompt.py
from src.prompt_manager import (
    FilePromptRepository,
    InMemoryPromptRepository,
    PromptManager,
    TemplateEngine,
)
from src.prompt_manager.prompts import PROMPTS


def build_prompt_manager() -> PromptManager:
    mem = InMemoryPromptRepository(PROMPTS)
    files = FilePromptRepository("prompts")
    eng = TemplateEngine()
    return PromptManager(memory_repo=mem, file_repo=files, template_engine=eng)


pm = build_prompt_manager()
