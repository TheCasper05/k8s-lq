class MultiAgentManagerError(Exception):
    """Base para errores del orquestador multi-agente."""


class InvalidProcessDefinitionError(MultiAgentManagerError):
    """Señala que la definición del proceso/step es inválida o está incompleta."""

    def __init__(self, message: str):
        super().__init__(message)
        self.detail = message


class PromptRenderingError(MultiAgentManagerError):
    """Error al renderizar un prompt mediante PromptManager."""

    def __init__(self, step_id: str, prompt_type: str, original: Exception):
        msg = f"Error rendering {prompt_type} prompt in step '{step_id}': {original}"
        super().__init__(msg)
        self.step_id = step_id
        self.prompt_type = prompt_type
        self.original = original


class StepExecutionError(MultiAgentManagerError):
    """Error ejecutando un step contra el LLM."""

    def __init__(self, process_name: str, step_id: str, original: Exception):
        msg = f"Error executing step '{step_id}' in process '{process_name}': {original}"
        super().__init__(msg)
        self.process_name = process_name
        self.step_id = step_id
        self.original = original
