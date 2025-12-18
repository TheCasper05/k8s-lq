class PromptManagerError(Exception):
    """Base exception for all PromptManager errors."""


class PromptNotFoundError(PromptManagerError):
    """Raised when a prompt (category/version/name) does not exist."""

    def __init__(self, category: str, name: str, version: str = "v1"):
        msg = f"Prompt not found: category='{category}', version='{version}', name='{name}'"
        super().__init__(msg)
        self.category = category
        self.name = name
        self.version = version


class MissingTemplateVariablesError(PromptManagerError):
    """Raised when required template variables are missing at render time."""

    def __init__(self, missing: set[str]):
        msg = f"Missing template variables: {', '.join(sorted(missing))}"
        super().__init__(msg)
        self.missing = missing


class InvalidPromptFormatError(PromptManagerError):
    """Raised when a prompt template has an invalid/unsupported placeholder syntax."""

    pass
