# MultiAgentManager (v1)

Orquestador para flujos multi‑paso usando prompts ya gestionados por `PromptManager`.
Cada step define qué prompts se renderizan y se ejecutan secuencialmente con un `LLMPort`.

## Almacenamiento de Procesos

Los procesos se guardan como archivos JSON en la estructura de directorios:

```
processes/
  {category}/
    {version}/
      {name}.json
```

**Ejemplo:**
```
processes/
  scenarios/
    v1/
      create_multi_agent_process.json
  conversations/
    v1/
      generate_suggestions_process.json
```

El `FileProcessRepository` busca procesos en esta estructura, similar a cómo `FilePromptRepository` busca prompts en `prompts/`.

## Estructura de Definición de Proceso

Un proceso es un array JSON de steps (agentes) que se ejecutan en orden:

```json
[
  {
    "id": "prepare_context",
    "system_prompt": {
      "category": "scenarios",
      "name": "prepare_context_system",
      "version": "v1"
    },
    "user_prompt": {
      "category": "scenarios",
      "name": "prepare_context_user",
      "version": "v1"
    },
    "response_schema": {
      "category": "scenarios",
      "name": "prepare_context_schema",
      "version": "v1"
    },
    "context": {},
    "llm_params": {
      "temperature": 0.2,
      "max_tokens": 400
    },
    "output_key": "scenario_inputs",
    "stop_on_error": true
  },
  {
    "id": "build_scenario",
    "system_prompt": {
      "category": "scenarios",
      "name": "create_system",
      "version": "v1"
    },
    "user_prompt": {
      "category": "scenarios",
      "name": "create_user",
      "version": "v1"
    },
    "response_schema": {
      "category": "scenarios",
      "name": "create_response_schema",
      "version": "v1"
    },
    "context": {},
    "llm_params": {
      "temperature": 0.35,
      "max_tokens": 1800
    },
    "output_key": "scenario_json",
    "stop_on_error": true
  }
]
```

### Campos por Step

- **`id`** (obligatorio): Identificador único del paso dentro del proceso.
- **`user_prompt`** (obligatorio): Referencia al prompt de usuario (`category`, `name`, `version`).
- **`system_prompt`** (opcional): Referencia al prompt de sistema.
- **`response_schema`** (opcional): Referencia a un schema JSON para respuestas estructuradas.
- **`context`** (opcional): Diccionario de variables estáticas para renderizar prompts en este step.
- **`llm_params`** (opcional): Parámetros específicos del LLM para este step (e.g. `temperature`, `max_tokens`). Se combinan con `llm_defaults`.
- **`output_key`** (opcional): Clave donde se guarda el output en el contexto compartido. Por defecto usa el `id` del step.
- **`stop_on_error`** (opcional, default: `true`): Si es `false`, el proceso continúa aunque el step falle.

## Contexto de Renderizado

El contexto disponible para renderizar prompts en cada step incluye:

1. **`initial_context`**: Variables pasadas al método `execute()`.
2. **`previous_output`** / **`last_output`**: Contenido de texto del paso anterior.
3. **Outputs por `output_key`**: Cada output previo se guarda bajo su `output_key` y también en un diccionario `outputs`.
4. **JSON parseado**: Si un step devuelve JSON válido, sus claves se fusionan directamente al contexto compartido.

**Ejemplo de propagación:**

```python
# Step 1 devuelve: {"context": "Ordering tacos", "language": "Spanish"}
# Step 2 puede usar en su prompt: {context} y {language}
```

## Flujo de Ejecución

1. **Carga del proceso**: Se carga desde el repositorio o se pasa directamente.
2. **Por cada step**:
   - Se construye el contexto combinando `initial_context`, outputs previos y `step.context`.
   - Se renderizan los prompts (system, user, response_schema) usando `PromptManager`.
   - Se ejecuta el LLM con los prompts renderizados.
   - Si la respuesta es JSON válido, se parsea y fusiona al contexto compartido.
   - El output se guarda bajo `output_key` y como `previous_output`.
3. **Resultado**: Se retorna una lista de `AgentStepResult` con los resultados de cada step.

## Uso Básico

### Con repositorio (recomendado)

```python
from src.container import Container

# El Container ya tiene configurado el MultiAgentManager
manager = Container.multi_agent_manager()

# Ejecutar proceso desde el repositorio
results = await manager.execute_from_repo(
    category="scenarios",
    name="create_multi_agent_process",
    version="v1",
    initial_context={"user_request": "I want to practice ordering tacos in Spanish"},
    llm_defaults={"temperature": 0.35, "max_tokens": 2000},
)

# Acceder a resultados
for result in results:
    print(f"Step: {result.step_id}")
    print(f"Output: {result.llm_response.content}")
    if result.error:
        print(f"Error: {result.error}")
```

### Sin repositorio (proceso directo)

```python
from src.multi_agent_manager.manager import MultiAgentManager
from src.container import Container

manager = MultiAgentManager(
    prompt_manager=Container.prompt_manager(),
    llm=Container.llm_adapter(),
)

# Cargar proceso manualmente
import json
with open("processes/scenarios/v1/create_multi_agent_process.json") as f:
    process_def = json.load(f)

results = await manager.execute(
    process_definition=process_def,
    initial_context={"user_request": "..."},
    llm_defaults={"temperature": 0.35},
)
```

## Ejemplo Completo: Crear Escenario

El proceso `create_multi_agent_process` tiene dos steps:

1. **`prepare_context`**: Toma `user_request` y genera `context` y `language`.
2. **`build_scenario`**: Usa `context` y `language` para generar el JSON del escenario.

```python
results = await manager.execute_from_repo(
    category="scenarios",
    name="create_multi_agent_process",
    version="v1",
    initial_context={
        "user_request": "I want to practice ordering tacos in Spanish with a friendly waiter"
    },
)

# El primer step genera: {"context": "...", "language": "Spanish"}
# El segundo step usa esos valores para renderizar su prompt
scenario_json = results[1].llm_response.content  # JSON del escenario completo
```

## Manejo de Errores

- **`PromptRenderingError`**: Se lanza si falla el renderizado de un prompt.
- **`StepExecutionError`**: Se lanza si falla la ejecución del LLM y `stop_on_error=true`.
- **`InvalidProcessDefinitionError`**: Se lanza si la definición del proceso es inválida.

Si `stop_on_error=false` en un step, el proceso continúa y el error se registra en `AgentStepResult.error`.

## Integración con Container

El `Container` ya tiene configurado:

```python
process_repository = FileProcessRepository(root_dir="processes")
multi_agent_manager = MultiAgentManager(
    prompt_manager=prompt_manager,
    llm=llm_adapter,
    process_repository=process_repository,
)
```

Usa `Container.multi_agent_manager()` para obtener una instancia lista para usar.

## Modelos

- **`AgentProcessDefinition`**: Representa un proceso completo con nombre y lista de steps.
- **`AgentStepDefinition`**: Representa un step individual con sus prompts y configuración.
- **`AgentStepResult`**: Resultado de ejecutar un step (response, prompts renderizados, errores).
- **`PromptRef`**: Referencia a un prompt en el catálogo (`category`, `name`, `version`).

