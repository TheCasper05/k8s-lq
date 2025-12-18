# 📋 Documentación de Migración de Prompts


## 📁 Estructura de Categorías

Los prompts están organizados en las siguientes categorías:

1. **`scenarios`** - Prompts para creación y gestión de escenarios de conversación
2. **`conversations`** - Prompts para interacciones conversacionales (roleplay, teacher, correcciones, sugerencias)
3. **`learning_units`** - Prompts para generación de unidades de aprendizaje (palabras y oraciones)
4. **`curriculums`** - Prompts para creación de currículos y cursos estructurados

---

## 📝 Documentación de Prompts Individuales

### Categoría: `scenarios`

#### Prompts en `prompts.py` (Memoria)

##### `create_system_v1`
- **Ubicación:** `src/prompt_manager/prompts.py`
- **Tipo:** String (prompt pequeño)
- **Utilidad:** Define el rol del sistema para el asistente de construcción de escenarios. Establece que el AI es un asistente de diseño instruccional especializado en crear características específicas de escenarios para actividades conversacionales de enseñanza.
- **Variables requeridas:** Ninguna
- **Uso:** Prompt del sistema para la generación de escenarios de conversación.

#### Prompts en `prompts/scenarios/` (Archivos)

##### `create_user_v1.txt`
- **Ubicación:** `prompts/scenarios/create_user_v1.txt`
- **Tipo:** Archivo `.txt` (prompt grande)
- **Utilidad:** Prompt detallado para crear objetos de escenario de práctica conversacional. Incluye instrucciones completas sobre cómo parsear inputs, inferir atributos, asignar roles, generar descripciones pedagógicas, y validar el resultado final. El prompt genera un JSON con toda la información del escenario.
- **Variables requeridas:**
  - `context` - Contexto del escenario solicitado por el usuario
  - `language` - Idioma del escenario
- **Uso:** Se utiliza cuando el usuario proporciona una descripción de texto libre para crear un escenario.

##### `create_user_file_v1.txt`
- **Ubicación:** `prompts/scenarios/create_user_file_v1.txt`
- **Tipo:** Archivo `.txt` (prompt grande)
- **Utilidad:** Similar a `create_user_v1.txt`, pero diseñado para crear escenarios basados en el contenido de un archivo. El prompt recibe un `file_id` en lugar de un contexto de texto libre.
- **Variables requeridas:**
  - `file_id` - ID del archivo que contiene la información para crear el escenario
  - `language` - Idioma del escenario
- **Uso:** Se utiliza cuando el escenario debe crearse a partir del contenido de un archivo subido.

##### `create_response_schema_v1.json`
- **Ubicación:** `prompts/scenarios/create_response_schema_v1.json`
- **Tipo:** Esquema JSON (dict)
- **Utilidad:** Define la estructura JSON que debe devolver el LLM al crear un escenario. Incluye campos como `title`, `assistant_gender`, `scenario_type`, `practice_topic`, `complete_description`, `theme`, `assistant_role`, `user_role`, `setting`, `potential_directions`, `example`, `additional_data`, y `appropriate`.
- **Variables requeridas:** Ninguna (es un esquema, no un template)
- **Uso:** Se pasa al LLM como esquema de respuesta estructurada para garantizar que el output tenga el formato correcto.

---

### Categoría: `conversations`

#### Prompts en `prompts.py` (Memoria)

##### `suggestions_user_v1`
- **Ubicación:** `src/prompt_manager/prompts.py`
- **Tipo:** String (prompt pequeño con template)
- **Utilidad:** Prompt del usuario para generar sugerencias de respuesta en una conversación. Proporciona el mensaje del asistente, el contexto del escenario y el idioma.
- **Variables requeridas:**
  - `assistant_message` - Mensaje del asistente al que el usuario debe responder
  - `scenario_context` - Contexto del escenario en el que se desarrolla la conversación
  - `language` - Idioma de la conversación
- **Uso:** Se combina con `suggestions_system_v1` para generar 3 sugerencias de respuesta para el estudiante.

##### `suggestions_system_v1`
- **Ubicación:** `src/prompt_manager/prompts.py`
- **Tipo:** String (prompt pequeño)
- **Utilidad:** Define el rol del sistema como generador de sugerencias. Instruye al AI para proporcionar 3 sugerencias de respuesta que ayuden al estudiante, considerando el contexto y el historial de la conversación. Enfatiza el uso de emojis y el respeto al idioma especificado.
- **Variables requeridas:** Ninguna
- **Uso:** Prompt del sistema para la generación de sugerencias de respuesta.

##### `message_correction_system_v1`
- **Ubicación:** `src/prompt_manager/prompts.py`
- **Tipo:** String (prompt pequeño)
- **Utilidad:** Define el rol del sistema como corrector de mensajes. Instruye al AI para corregir mensajes de estudiantes considerando el contexto y los atributos del esquema proporcionado. Enfatiza que la respuesta debe estar en el mismo idioma que el mensaje del usuario.
- **Variables requeridas:** Ninguna
- **Uso:** Prompt del sistema para la corrección de mensajes de estudiantes.

##### `message_correction_user_v1`
- **Ubicación:** `src/prompt_manager/prompts.py`
- **Tipo:** String (prompt pequeño con template)
- **Utilidad:** Prompt del usuario para la corrección de mensajes. Proporciona el mensaje del usuario y el idioma de la conversación.
- **Variables requeridas:**
  - `user_message` - Mensaje del usuario que necesita corrección
  - `language` - Idioma de la conversación
- **Uso:** Se combina con `message_correction_system_v1` y el esquema de respuesta para corregir errores en el mensaje del estudiante.

#### Prompts en `prompts/conversations/` (Archivos)

##### `roleplay_v1.txt`
- **Ubicación:** `prompts/conversations/roleplay_v1.txt`
- **Tipo:** Archivo `.txt` (prompt grande)
- **Utilidad:** Prompt completo para guiar al asistente AI en conversaciones de roleplay interactivas. Define cómo el AI debe adoptar un personaje, mantener el rol, hacer preguntas, usar emojis, manejar desviaciones del tema, mantener el idioma, y ajustar el nivel de lenguaje según el CEFR. Incluye instrucciones detalladas sobre límites de palabras, manejo de despedidas, y restricciones de contenido.
- **Variables requeridas:**
  - `theme` - Tema del escenario
  - `assistant_role` - Rol que juega el asistente
  - `user_role` - Rol que juega el usuario
  - `potential_directions` - Direcciones potenciales de la conversación
  - `setting` - Escenario físico o situacional
  - `example` - Ejemplo de intercambio (una línea)
  - `additional_data` - Datos adicionales importantes para la conversación
- **Uso:** Se utiliza como prompt del sistema para conversaciones de roleplay donde el estudiante practica en un escenario realista.

##### `teacher_v1.txt`
- **Ubicación:** `prompts/conversations/teacher_v1.txt`
- **Tipo:** Archivo `.txt` (prompt grande)
- **Utilidad:** Prompt completo para que el AI actúe como profesor y conduzca conversaciones enfocadas en corrección. Define cómo introducir temas, lanzar ejercicios, corregir errores significativos, mantener el flujo conversacional, y explorar temas desde múltiples ángulos. Incluye instrucciones sobre cuándo y cómo corregir, límites de palabras, y manejo de desviaciones.
- **Variables requeridas:**
  - `practice_topic` - Tema a practicar
  - `potential_directions` - Posibles contextos/sub-temas
  - `theme` - Tema del escenario
  - `additional_data` - Datos adicionales importantes (opcional pero recomendado)
- **Uso:** Se utiliza como prompt del sistema para conversaciones donde el AI actúa como profesor y corrige al estudiante en tiempo real.

##### `message_correction_response_schema.json`
- **Ubicación:** `prompts/conversations/message_correction_response_schema.json`
- **Tipo:** Esquema JSON (dict)
- **Utilidad:** Define la estructura JSON para la respuesta de corrección de mensajes. Incluye un array de `mistakes`, donde cada error tiene `explanation`, `mistake` (texto exacto del error), `correction`, `mistake_type` (enum con 25+ tipos de errores), y `mistake_level` (A1-C2 según CEFR).
- **Variables requeridas:** Ninguna (es un esquema, no un template)
- **Uso:** Se pasa al LLM como esquema de respuesta estructurada para garantizar que las correcciones tengan el formato correcto con todos los detalles necesarios.

##### `suggestions_response_schema.json`
- **Ubicación:** `prompts/conversations/suggestions_response_schema.json`
- **Tipo:** Esquema JSON (dict)
- **Utilidad:** Define la estructura JSON para la respuesta de sugerencias. Requiere un array `suggestions` con exactamente 3 strings, cada uno con menos de 40 palabras.
- **Variables requeridas:** Ninguna (es un esquema, no un template)
- **Uso:** Se pasa al LLM como esquema de respuesta estructurada para garantizar que se generen exactamente 3 sugerencias.

---

### Categoría: `learning_units`

#### Prompts en `prompts.py` (Memoria)

##### `create_user_v1`
- **Ubicación:** `src/prompt_manager/prompts.py`
- **Tipo:** String (prompt pequeño con template)
- **Utilidad:** Prompt del usuario para generar unidades de aprendizaje (palabras o oraciones). Proporciona el contexto del escenario, idioma, tipo de unidad, cantidad, nivel CEFR, y unidades previas.
- **Variables requeridas:**
  - `scenario_context` - Contexto del escenario
  - `language` - Idioma
  - `unit_type` - Tipo de unidad ("words" o "sentences")
  - `unit_quantity` - Cantidad de unidades a generar
  - `level` - Nivel CEFR (A1, A2, B1, B2, C1, C2)
  - `previous_units` - Unidades previamente generadas (para evitar duplicados)
- **Uso:** Se combina con `create_system_v1` para generar palabras u oraciones apropiadas para el contexto y nivel.

##### `create_system_v1`
- **Ubicación:** `src/prompt_manager/prompts.py`
- **Tipo:** String (prompt pequeño)
- **Utilidad:** Define el rol del sistema como generador de palabras y oraciones. Instruye al AI para crear unidades de aprendizaje considerando el contexto, idioma, tipo, cantidad, nivel y unidades previas. Enfatiza que las unidades deben ser diferentes de las previas y estar en el nivel CEFR correcto.
- **Variables requeridas:** Ninguna
- **Uso:** Prompt del sistema para la generación de unidades de aprendizaje.

##### `create_response_schema_v1`
- **Ubicación:** `src/prompt_manager/prompts.py`
- **Tipo:** Dict (esquema JSON)
- **Utilidad:** Define la estructura JSON para la respuesta de unidades de aprendizaje. Requiere un array `units` de strings.
- **Variables requeridas:** Ninguna (es un esquema, no un template)
- **Uso:** Se pasa al LLM como esquema de respuesta estructurada para garantizar que las unidades se devuelvan como un array.

---

### Categoría: `curriculums`

#### Prompts en `prompts.py` (Memoria)

##### `create_user_v1`
- **Ubicación:** `src/prompt_manager/prompts.py`
- **Tipo:** String (prompt pequeño con template)
- **Utilidad:** Prompt del usuario para crear un currículo. Proporciona la descripción del curso y el idioma.
- **Variables requeridas:**
  - `description` - Descripción de lo que debe enseñarse en el curso
  - `language` - Idioma del curso
- **Uso:** Se combina con `create_system_v1` o `create_system_file_v1` para generar un currículo estructurado.

#### Prompts en `prompts/curriculums/` (Archivos)

##### `create_system_v1.txt`
- **Ubicación:** `prompts/curriculums/create_system_v1.txt`
- **Tipo:** Archivo `.txt` (prompt grande)
- **Utilidad:** Prompt del sistema para crear cursos estructurados con múltiples submódulos y escenarios. Define cómo organizar el contenido en submódulos progresivos, crear escenarios conversacionales (sin material externo), y generar diferentes tipos de escenarios (roleplay, teacher, knowledge). Enfatiza que los escenarios deben ser estrictamente conversacionales y omite actividades que requieren material externo.
- **Variables requeridas:** Ninguna
- **Uso:** Se utiliza cuando se crea un currículo desde una descripción de texto.

##### `create_system_file_v1.txt`
- **Ubicación:** `prompts/curriculums/create_system_file_v1.txt`
- **Tipo:** Archivo `.txt` (prompt grande)
- **Utilidad:** Similar a `create_system_v1.txt`, pero diseñado para crear cursos basados en el contenido de un archivo. El prompt recibe un `file_id` en lugar de una descripción de texto.
- **Variables requeridas:**
  - `file_id` - ID del archivo que contiene la información para crear el curso
- **Uso:** Se utiliza cuando el currículo debe crearse a partir del contenido de un archivo subido.

##### `course_unit_create_response_schema_v1.json`
- **Ubicación:** `prompts/curriculums/course_unit_create_response_schema_v1.json`
- **Tipo:** Esquema JSON (dict)
- **Utilidad:** Define la estructura JSON para la respuesta de creación de cursos. Requiere `name`, `description`, y `submodules` (array de objetos con `name` y `scenarios` - array de strings con descripciones de escenarios).
- **Variables requeridas:** Ninguna (es un esquema, no un template)
- **Uso:** Se pasa al LLM como esquema de respuesta estructurada para garantizar que el curso tenga la estructura correcta con submódulos y escenarios.

---

## 🔄 Flujo de Uso del PromptManager

### Inicialización

```python
from prompt_manager import PromptManager, InMemoryPromptRepository, FilePromptRepository, TemplateEngine
from prompt_manager.prompts import PROMPTS

def build_prompt_manager() -> PromptManager:
    mem = InMemoryPromptRepository(PROMPTS)
    files = FilePromptRepository("prompts")
    eng = TemplateEngine()
    return PromptManager(memory_repo=mem, file_repo=files, template_engine=eng)
```

### Uso de Prompts

#### Prompts de String (Templates)
```python
pm = build_prompt_manager()

# Renderizar un prompt con variables
result = pm.render(
    "conversations", 
    "suggestions_user_v1",
    assistant_message="Hello!",
    scenario_context="Restaurant",
    language="English"
)
```

#### Prompts de Esquema (Dict)
```python
# Los esquemas se devuelven directamente sin renderizar
schema = pm.render("scenarios", "create_response_schema_v1")
# schema es un dict con la estructura JSON
```

#### Prompts de Archivo
```python
# Los prompts en archivos .txt se cargan automáticamente
roleplay_prompt = pm.render(
    "conversations",
    "roleplay_v1",
    theme="Restaurant",
    assistant_role="waiter",
    user_role="customer",
    potential_directions="ordering, paying",
    setting="Italian restaurant",
    example="Customer: I'd like pizza. Waiter: What size?",
    additional_data="Use polite language"
)
```

---

## 📊 Resumen de Prompts por Categoría

| Categoría | Prompts en Memoria | Prompts en Archivos | Total |
|-----------|-------------------|---------------------|-------|
| `scenarios` | 1 | 3 | 4 |
| `conversations` | 4 | 4 | 8 |
| `learning_units` | 3 | 0 | 3 |
| `curriculums` | 1 | 3 | 4 |
| **TOTAL** | **9** | **10** | **19** |

---

## 🎯 Convenciones de Nomenclatura

- **Versiones:** Los prompts incluyen sufijos `_v1`, `_v2`, etc. para versionado
- **Tipos:**
  - `_system_*` - Prompts del sistema (rol del AI)
  - `_user_*` - Prompts del usuario (input del usuario)
  - `_response_schema_*` - Esquemas JSON para respuestas estructuradas
- **Archivos:**
  - Prompts grandes → `.txt` o `.md`
  - Esquemas JSON → `.json`
  - Prompts pequeños → constantes en `prompts.py`

---

## ✅ Validación y Testing

Todos los prompts están cubiertos por tests en `tests/prompt_manager/` que verifican:

- ✅ Carga correcta de todos los prompts
- ✅ Validación de templates y variables
- ✅ Validación de esquemas JSON
- ✅ Renderizado correcto con datos de prueba
- ✅ Completitud y no vacíos

---

## 📚 Referencias

- **PromptManager:** `src/prompt_manager/manager.py`
- **Repositorios:** `src/prompt_manager/repositories/`
- **Templates:** `src/prompt_manager/templates/engine.py`
- **Prompts en memoria:** `src/prompt_manager/prompts.py`
- **Prompts en archivos:** `prompts/`

