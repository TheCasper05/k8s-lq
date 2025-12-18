"""
Tasks for activities module - LingoBot integration.
These functions handle communication with the LingoBot API and database operations.
"""

import requests
from django.conf import settings
from activities.models import ContentItem, Conversation, Message, MessageSender
from celery import shared_task


@shared_task
def get_lingobot_headers():
    """Obtiene los headers para las requests al bot."""
    headers = {"Content-Type": "application/json"}
    if hasattr(settings, "LINGOBOT_API_KEY") and settings.LINGOBOT_API_KEY:
        headers["X-API-KEY"] = settings.LINGOBOT_API_KEY
    return headers


def create_scenario(user_request, temperature=0.7, max_tokens=2000, user=None):
    """
    Crea un escenario llamando al bot y guarda un ContentItem.

    Args:
        user_request (str): Solicitud del usuario para crear el escenario
        temperature (float): Temperatura para la generación (default: 0.7)
        max_tokens (int): Máximo de tokens a generar (default: 2000)
        user: Usuario que crea el escenario (opcional)

    Returns:
        ContentItem: El ContentItem creado con el escenario

    Raises:
        requests.exceptions.RequestException: Si hay error al comunicarse con el bot
        ValueError: Si user_request está vacío
    """
    if not user_request:
        raise ValueError("Campo 'user_request' es requerido")

    lingobot_address = settings.LINGOBOT_ADDRESS
    lingobot_url = f"{lingobot_address}/api/v1/scenario/create"

    request_data = {
        "user_request": user_request,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    # Hacer el request a LingoBot
    response = requests.post(
        lingobot_url,
        json=request_data,
        headers=get_lingobot_headers(),
        timeout=30,
    )

    response.raise_for_status()
    bot_response = response.json()

    # Extraer datos del scenario
    scenario = bot_response.get("scenario", {})
    title = scenario.get("title", "Scenario Created")
    description = scenario.get("complete_description", "")

    # Crear content_data sin title y complete_description
    content_data = scenario.copy()
    content_data.pop("title", None)
    content_data.pop("complete_description", None)

    # Agregar metadata si existe
    if "metadata" in bot_response:
        content_data["metadata"] = bot_response["metadata"]

    # Crear el ContentItem
    content_item = ContentItem.objects.create(
        content_type="conversation",
        title=title,
        description=description,
        content_data=content_data,
        owner_user=user,
    )

    return content_item


def get_text_answer(
    message,
    scenario_type,
    conversation_id=None,
    content_item_id=None,
    user=None,
    response_id=None,
    theme=None,
    assistant_role=None,
    user_role=None,
    potential_directions=None,
    setting=None,
    example=None,
    additional_data=None,
    practice_topic=None,
    language="English",
):
    """
    Obtiene una respuesta de texto del bot y crea/actualiza la conversación.

    Args:
        message (str): Mensaje del usuario
        scenario_type (str): Tipo de escenario ("roleplay", "teacher", "knowledge")
        conversation_id (str, optional): ID de conversación existente
        content_item_id (str, optional): ID del ContentItem relacionado
        user: Usuario de la conversación (opcional)
        response_id (str, optional): ID de respuesta anterior para mantener historial
        theme (str, optional): Tema de la conversación
        assistant_role (str, optional): Rol del asistente
        user_role (str, optional): Rol del usuario
        potential_directions (str, optional): Direcciones posibles de la conversación
        setting (str, optional): Escenario físico o situacional
        example (str, optional): Ejemplo de intercambio conversacional
        additional_data (str/list, optional): Datos adicionales
        practice_topic (str, optional): Tema específico a practicar
        language (str): Idioma de la conversación (default: "English")

    Returns:
        dict: Diccionario con conversation, response y messages creados

    Raises:
        requests.exceptions.RequestException: Si hay error al comunicarse con el bot
        Conversation.DoesNotExist: Si conversation_id no existe
        ValueError: Si message está vacío
    """
    if not message:
        raise ValueError("Campo 'message' es requerido")

    lingobot_address = settings.LINGOBOT_ADDRESS
    lingobot_url = f"{lingobot_address}/api/v1/conversation/text_answer"

    # Preparar datos del request
    request_data = {
        "message": message,
        "scenario_type": scenario_type,
        "response_id": response_id,
        "theme": theme,
        "assistant_role": assistant_role,
        "user_role": user_role,
        "potential_directions": potential_directions,
        "setting": setting,
        "example": example,
        "additional_data": additional_data,
        "practice_topic": practice_topic,
        "language": language,
    }

    # Obtener o crear conversación
    if conversation_id:
        conversation = Conversation.objects.get(id=conversation_id)
        previous_response_id = conversation.metadata.get("response_id", None)
        request_data["response_id"] = previous_response_id or response_id
    else:
        # Crear nueva conversación si no existe
        content_item = None
        if content_item_id:
            try:
                content_item = ContentItem.objects.get(id=content_item_id)
            except ContentItem.DoesNotExist:
                pass

        conversation = Conversation.objects.create(
            user=user,  # Puede ser None para testing
            content_item=content_item,
            status="active",
        )

    # Hacer el request a LingoBot
    response = requests.post(
        lingobot_url,
        json=request_data,
        headers=get_lingobot_headers(),
        timeout=30,
    )

    response.raise_for_status()
    bot_response = response.json()

    # Obtener el número de orden del último mensaje
    last_message = conversation.messages.order_by("-nro_order").first()
    next_order = (last_message.nro_order + 1) if last_message else 1

    # Crear mensaje del usuario
    user_message = Message.objects.create(
        conversation=conversation,
        sender=MessageSender.USER,
        content=message,
        nro_order=next_order,
    )

    # Crear mensaje del asistente
    assistant_message = Message.objects.create(
        conversation=conversation,
        sender=MessageSender.ASSISTANT,
        content=bot_response.get("answer"),
        nro_order=next_order + 1,
        input_tokens=bot_response.get("metadata", {}).get("prompt_tokens"),
        output_tokens=bot_response.get("metadata", {}).get("completion_tokens"),
        total_tokens=bot_response.get("tokens_used"),
        model_name=bot_response.get("model"),
        metadata={
            "provider": bot_response.get("provider"),
            "finish_reason": bot_response.get("finish_reason"),
            "response_id": bot_response.get("response_id"),
        },
    )

    # Guardar response_id en la conversación
    conversation.metadata["response_id"] = bot_response.get("response_id")
    conversation.save()

    return {
        "conversation": conversation,
        "response": {
            "content": bot_response.get("answer"),
            "response_id": bot_response.get("response_id"),
            "provider": bot_response.get("provider"),
            "model": bot_response.get("model"),
            "tokens_used": bot_response.get("tokens_used"),
        },
        "messages": {
            "user_message": user_message,
            "assistant_message": assistant_message,
        },
    }


def get_suggestions(assistant_message, scenario_context, language="English"):
    """
    Obtiene sugerencias de respuestas del bot.

    Args:
        assistant_message (str): Mensaje del asistente al que el estudiante debe responder
        scenario_context (str): Contexto del escenario educativo
        language (str): Idioma en el que se deben generar las sugerencias (default: "English")

    Returns:
        dict: Diccionario con suggestions, model y tokens_used

    Raises:
        requests.exceptions.RequestException: Si hay error al comunicarse con el bot
        ValueError: Si assistant_message o scenario_context están vacíos
    """
    if not assistant_message or not scenario_context:
        raise ValueError(
            "Campos 'assistant_message' y 'scenario_context' son requeridos"
        )

    lingobot_address = settings.LINGOBOT_ADDRESS
    lingobot_url = f"{lingobot_address}/api/v1/conversation/suggestions"

    request_data = {
        "assistant_message": assistant_message,
        "scenario_context": scenario_context,
        "language": language,
    }

    # Hacer el request a LingoBot
    response = requests.post(
        lingobot_url,
        json=request_data,
        headers=get_lingobot_headers(),
        timeout=30,
    )

    response.raise_for_status()
    bot_response = response.json()

    return {
        "suggestions": bot_response.get("suggestions", []),
        "model": bot_response.get("model"),
        "tokens_used": bot_response.get("tokens_used"),
    }


def start_conversation(
    scenario_type,
    language="English",
    theme=None,
    assistant_role=None,
    user_role=None,
    potential_directions=None,
    setting=None,
    example=None,
    additional_data=None,
    practice_topic=None,
):
    """
    Inicia una conversación generando un audio de bienvenida.

    Args:
        scenario_type (str): Tipo de escenario ("roleplay", "teacher", "knowledge")
        language (str): Idioma de la conversación (default: "English")
        theme (str, optional): Tema de la conversación
        assistant_role (str, optional): Rol del asistente
        user_role (str, optional): Rol del usuario
        potential_directions (str, optional): Direcciones posibles de la conversación
        setting (str, optional): Escenario físico o situacional
        example (str, optional): Ejemplo de intercambio conversacional
        additional_data (str/list, optional): Datos adicionales
        practice_topic (str, optional): Tema específico a practicar

    Returns:
        dict: Diccionario con conversation_id, response_id, audio_duration, voice_used, provider

    Raises:
        requests.exceptions.RequestException: Si hay error al comunicarse con el bot
        ValueError: Si scenario_type está vacío
    """
    if not scenario_type:
        raise ValueError("Campo 'scenario_type' es requerido")

    lingobot_address = settings.LINGOBOT_ADDRESS
    lingobot_url = f"{lingobot_address}/api/v1/conversation/start"

    request_data = {
        "scenario_type": scenario_type,
        "language": language,
        "theme": theme,
        "assistant_role": assistant_role,
        "user_role": user_role,
        "potential_directions": potential_directions,
        "setting": setting,
        "example": example,
        "additional_data": additional_data,
        "practice_topic": practice_topic,
    }

    # Hacer el request a LingoBot
    response = requests.post(
        lingobot_url,
        json=request_data,
        headers=get_lingobot_headers(),
        timeout=30,
    )

    response.raise_for_status()

    # El endpoint /start devuelve un archivo de audio
    # Extraer headers importantes
    conversation_id = response.headers.get("X-Conversation-ID")
    response_id = response.headers.get("X-Response-ID")
    audio_duration = response.headers.get("X-Audio-Duration")
    voice_used = response.headers.get("X-Voice-Used")
    provider = response.headers.get("X-Provider")

    return {
        "conversation_id": conversation_id,
        "response_id": response_id,
        "audio_duration": audio_duration,
        "voice_used": voice_used,
        "provider": provider,
        "audio_content": response.content,
    }
