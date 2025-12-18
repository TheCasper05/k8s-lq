from dependency_injector import containers, providers

from src.application.use_cases.batch_translate_use_case import BatchTranslateUseCase
from src.application.use_cases.create_rubric_use_case import CreateRubricUseCase
from src.application.use_cases.create_scenario_use_case import CreateScenarioUseCase
from src.application.use_cases.generate_audio_response_use_case import (
    GenerateAudioResponseUseCase,
)
from src.application.use_cases.generate_curriculum_use_case import CurriculumGeneratorUseCase
from src.application.use_cases.generate_text_response_use_case import GenerateTextResponseUseCase
from src.application.use_cases.generate_transcription_use_case import (
    GenerateTranscriptionUseCase,
)
from src.application.use_cases.grade_rubric_use_case import GradeRubricUseCase
from src.application.use_cases.translate_message_use_case import TranslateMessageUseCase
from src.config import Settings
from src.domain.services.conversation_service import ConversationService
from src.infrastructure.adapters.ai.factory import AIProviderFactory
from src.infrastructure.adapters.storage.factory import StorageProviderFactory
from src.multi_agent_manager.manager import MultiAgentManager
from src.multi_agent_manager.repositories import FileProcessRepository
from src.prompt_manager.manager import PromptManager
from src.prompt_manager.prompts import PROMPTS
from src.prompt_manager.repositories import FilePromptRepository, InMemoryPromptRepository
from src.prompt_manager.templates import TemplateEngine


class Container(containers.DeclarativeContainer):
    """Contenedor de inyección de dependencias."""

    # Configuración
    config = providers.Singleton(Settings)

    # Factory de proveedores AI
    ai_factory = providers.Singleton(AIProviderFactory, settings=config)

    # Factory de proveedores Storage
    storage_factory = providers.Singleton(StorageProviderFactory, settings=config)

    # Adaptadores (Ports implementados)
    llm_adapter = providers.Factory(
        lambda factory: factory.create_llm_adapter(), factory=ai_factory
    )

    tts_adapter = providers.Factory(
        lambda factory: factory.create_tts_adapter(), factory=ai_factory
    )

    stt_adapter = providers.Factory(
        lambda factory: factory.create_stt_adapter(), factory=ai_factory
    )

    storage_adapter = providers.Factory(
        lambda factory: factory.create_storage_adapter(), factory=storage_factory
    )

    prompt_memory_repository = providers.Singleton(InMemoryPromptRepository, prompts=PROMPTS)
    prompt_file_repository = providers.Singleton(FilePromptRepository, root_dir="prompts")
    prompt_manager = providers.Singleton(
        PromptManager,
        memory_repo=prompt_memory_repository,
        file_repo=prompt_file_repository,
        template_engine=TemplateEngine(),
    )
    process_repository = providers.Singleton(FileProcessRepository, root_dir="processes")
    multi_agent_manager = providers.Factory(
        MultiAgentManager,
        prompt_manager=prompt_manager,
        llm=llm_adapter,
        process_repository=process_repository,
    )
    # Casos de uso
    generate_text_response_use_case = providers.Factory(
        GenerateTextResponseUseCase, llm=llm_adapter
    )

    generate_transcription_use_case = providers.Factory(
        GenerateTranscriptionUseCase, stt=stt_adapter
    )

    generate_audio_response_use_case = providers.Factory(
        GenerateAudioResponseUseCase, tts=tts_adapter
    )

    conversation_service = providers.Factory(
        ConversationService, llm=llm_adapter, tts=tts_adapter, stt=stt_adapter
    )

    batch_translate_use_case = providers.Factory(
        BatchTranslateUseCase, llm=llm_adapter, prompt_manager=prompt_manager
    )

    translate_message_use_case = providers.Factory(
        TranslateMessageUseCase, llm=llm_adapter, prompt_manager=prompt_manager
    )

    generate_curriculum_use_case = providers.Factory(
        CurriculumGeneratorUseCase, llm=llm_adapter, prompt_manager=prompt_manager
    )

    create_rubric_use_case = providers.Factory(
        CreateRubricUseCase,
        llm=llm_adapter,
        prompt_manager=prompt_manager,
        storage=storage_adapter,
    )

    grade_rubric_use_case = providers.Factory(
        GradeRubricUseCase,
        llm=llm_adapter,
        prompt_manager=prompt_manager,
    )

    create_scenario_use_case = providers.Factory(
        CreateScenarioUseCase,
        llm=llm_adapter,
        prompt_manager=prompt_manager,
        multi_agent_manager=multi_agent_manager,
        settings=config,
    )
