import json
import uuid
from datetime import datetime

from src.application.use_cases.generate_conversation_suggestions_use_case import (
    GenerateConversationSuggestionsUseCase,
)
from src.application.use_cases.generate_text_response_use_case import GenerateTextResponseUseCase
from src.domain.models.message import Message
from src.domain.ports.ai.llm_port import LLMPort
from src.domain.ports.ai.stt_port import STTPort
from src.domain.ports.ai.tts_port import TTSPort
from src.prompt_manager.manager import PromptManager


def generate_text_response_use_case() -> GenerateTextResponseUseCase:
    from src.container import Container

    return GenerateTextResponseUseCase(llm=Container.llm_adapter())


def generate_conversation_suggestions_use_case() -> GenerateConversationSuggestionsUseCase:
    from src.container import Container

    return GenerateConversationSuggestionsUseCase(llm=Container.llm_adapter())


def get_prompt_manager() -> PromptManager:
    from src.container import Container

    return Container.prompt_manager()


class ConversationService:
    """Servicio de dominio para gestionar conversaciones."""

    def __init__(self, llm: LLMPort, tts: TTSPort, stt: STTPort):
        """
        Inyección de dependencias mediante ports.

        Args:
            llm: Port para LLM (puede ser OpenAI, Anthropic, etc.)
            tts: Port para TTS
            stt: Port para STT
        """
        self.llm = llm
        self.tts = tts
        self.stt = stt

    async def process_voice_message(
        self, audio_data: bytes, conversation_context: list[Message], language: str = "en"
    ) -> tuple[str, bytes]:
        """
        Procesa un mensaje de voz y retorna respuesta textual + audio.

        Lógica de negocio pura, sin depender de implementaciones específicas.
        """
        # 1. Transcribir audio a texto (STT)
        transcription = await self.stt.transcribe_audio(audio=audio_data, language=language)

        # 2. Crear mensaje del usuario
        user_message = Message(role="user", content=transcription.text, timestamp=datetime.now())

        # 3. Generar respuesta con LLM
        llm_response = await self.llm.generate_response(
            messages=conversation_context + [user_message], temperature=0.7
        )

        # 4. Sintetizar respuesta a voz (TTS)
        audio_response = await self.tts.synthesize_speech(
            text=llm_response.content, language=language
        )

        return llm_response.content, audio_response.audio_data

    async def process_text_answer(
        self,
        message: str,
        response_id: str,
        scenario_type: str,
        theme: str,
        assistant_role: str,
        user_role: str,
        potential_directions: str,
        setting: str,
        example: str,
        additional_data: str,
        practice_topic: str,
        language: str = "English",
    ) -> str:
        """
        Procesa un mensaje de texto y retorna respuesta textual.
        """
        from src.interfaces.api.v1.dtos.conversation_dtos import TextAnswerResponse

        prompt_name = scenario_type  # Sin sufijo _v1, la versión se pasa por separado
        system_prompt = get_prompt_manager().render(
            "conversations",
            prompt_name,
            version="v1",
            theme=theme,
            assistant_role=assistant_role,
            user_role=user_role,
            potential_directions=potential_directions,
            setting=setting,
            example=example,
            additional_data=additional_data,
            practice_topic=practice_topic,
            language=language,
        )
        use_case = generate_text_response_use_case()

        llm_response = await use_case.execute(
            message, response_id=response_id, system_prompt=system_prompt
        )

        # Extraer tokens del metadata si están disponibles
        metadata = llm_response.metadata or {}
        input_tokens = metadata.get("prompt_tokens", 0)
        output_tokens = metadata.get("completion_tokens", 0)
        total_tokens = llm_response.tokens_used or (input_tokens + output_tokens)

        # response_id es requerido en el DTO, usar el de la respuesta o generar uno
        response_id_value = llm_response.response_id or "unknown"

        text_answer_response = TextAnswerResponse(
            answer=llm_response.content,
            response_id=response_id_value,
            model=llm_response.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
        )

        return text_answer_response

    async def process_suggestions(
        self,
        assistant_message: str,
        scenario_context: str,
        language: str = "English",
    ) -> list[str]:
        """
        Procesa un mensaje de texto y retorna sugerencias de palabras.
        """
        from src.interfaces.api.v1.dtos.conversation_dtos import SuggestionsResponse

        user_prompt = get_prompt_manager().render(
            "conversations",
            "suggestions_user",
            version="v1",
            assistant_message=assistant_message,
            scenario_context=scenario_context,
            language=language,
        )
        system_prompt = get_prompt_manager().render(
            "conversations",
            "suggestions_system",
            version="v1",
            assistant_message=assistant_message,
            scenario_context=scenario_context,
            language=language,
        )

        response_schema = get_prompt_manager().render(
            "conversations",
            "suggestions_response_schema",
            version="v1",
        )

        use_case = generate_conversation_suggestions_use_case()

        llm_response = await use_case.execute(
            user_message=user_prompt, system_prompt=system_prompt, response_schema=response_schema
        )

        suggestions = json.loads(llm_response.content)["suggestions"]
        suggestions_response = SuggestionsResponse(
            suggestions=suggestions,
            model=llm_response.model,
            tokens_used=llm_response.tokens_used,
        )

        return suggestions_response

    async def start_conversation(
        self,
        scenario_type: str,
        language: str,
        theme: str | None = None,
        assistant_role: str | None = None,
        user_role: str | None = None,
        potential_directions: str | None = None,
        setting: str | None = None,
        example: str | None = None,
        additional_data: str | None = None,
        practice_topic: str | None = None,
    ):
        """
        Inicia una nueva conversación generando un mensaje de bienvenida y su audio.
        Funciona igual que process_text_answer pero con un mensaje fijo de inicio.

        Args:
            scenario_type: Tipo de escenario
            theme: Tema de la conversación
            assistant_role: Rol del asistente
            user_role: Rol del usuario
            potential_directions: Posibles direcciones de la conversación
            setting: Configuración de la conversación
            example: Ejemplo de la conversación
            additional_data: Datos adicionales de la conversación
            practice_topic: Tema de la práctica
            language: Idioma de la conversación

        Returns:
            ConversationStartResponse con conversation_id, response_id y audio_file
        """

        # 1. Generar conversation_id único
        conversation_id = str(uuid.uuid4())

        # 2. Mensaje fijo para iniciar la conversación (en el idioma objetivo)
        # Mapeo simple de idiomas comunes para el mensaje de inicio
        start_message = f"This is the first message to the conversation. Your answer must be in {language}. Follow the instructions and keep the conversation going."
        # Usar el mensaje en el idioma correspondiente o el genérico en inglés

        # 3. Usar process_text_answer con el mensaje de inicio y sin response_id
        text_answer_response = await self.process_text_answer(
            message=start_message,
            response_id=None,  # Sin response_id ya que es el inicio
            scenario_type=scenario_type,
            theme=theme,
            assistant_role=assistant_role,
            user_role=user_role,
            potential_directions=potential_directions,
            setting=setting,
            example=example,
            additional_data=additional_data,
            practice_topic=practice_topic,
            language=language,
        )

        welcome_message = text_answer_response.answer
        response_id = text_answer_response.response_id

        audio_response = await self.tts.synthesize_speech(
            text=welcome_message,
            audio_format="mp3",
            speed=1.0,
        )

        # 6. Retornar datos necesarios (audio como AudioOutput, no base64)
        return conversation_id, response_id, audio_response
