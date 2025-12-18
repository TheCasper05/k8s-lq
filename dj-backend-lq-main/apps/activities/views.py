import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from tasks.activities.tasks import (
    create_scenario,
    get_text_answer,
    get_suggestions,
    start_conversation,
)


class TestEndpointView(APIView):
    """
    View para recibir requests y llamar a diferentes endpoints del bot.
    Soporta: scenario, text_answer, suggestions, start

    NOTA: Este endpoint es solo para testing. La lógica real está en tasks.activities
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Recibe un request con campo 'type' que determina qué endpoint del bot llamar:
        - 'scenario': Crea un escenario y un ContentItem
        - 'text_answer': Obtiene respuesta de texto y crea Message
        - 'suggestions': Obtiene sugerencias de respuestas
        - 'start': Inicia una conversación con audio
        """
        request_type = request.data.get("type")

        if not request_type:
            return Response(
                {
                    "error": "Campo 'type' es requerido. Valores válidos: 'scenario', 'text_answer', 'suggestions', 'start'"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if request_type == "scenario":
                return self._handle_scenario(request)
            elif request_type == "text_answer":
                return self._handle_text_answer(request)
            elif request_type == "suggestions":
                return self._handle_suggestions(request)
            elif request_type == "start":
                return self._handle_start(request)
            else:
                return Response(
                    {
                        "error": f"Tipo '{request_type}' no válido. Valores válidos: 'scenario', 'text_answer', 'suggestions', 'start'"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except requests.exceptions.HTTPError as e:
            error_detail = str(e)
            try:
                if hasattr(e, "response") and hasattr(e.response, "text"):
                    error_detail = f"{str(e)} - Response: {e.response.text}"
            except:
                pass
            return Response(
                {
                    "error": f"Error al comunicarse con LingoBot: {error_detail}",
                    "status_code": e.response.status_code
                    if hasattr(e, "response")
                    else None,
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": f"Error al comunicarse con LingoBot: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Error inesperado: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _handle_scenario(self, request):
        """Maneja la creación de escenarios."""
        user = request.user if request.user.is_authenticated else None

        content_item = create_scenario(
            user_request=request.data.get("user_request"),
            temperature=request.data.get("temperature", 0.7),
            max_tokens=request.data.get("max_tokens", 2000),
            user=user,
        )

        return Response(
            {
                "id": str(content_item.id),
                "public_id": content_item.public_id,
                "title": content_item.title,
                "description": content_item.description,
                "content_data": content_item.content_data,
                "created_at": content_item.created_at.isoformat()
                if content_item.created_at
                else None,
            },
            status=status.HTTP_201_CREATED,
        )

    def _handle_text_answer(self, request):
        """Maneja las respuestas de texto en conversaciones."""
        user = request.user if request.user.is_authenticated else None

        result = get_text_answer(
            message=request.data.get("message"),
            scenario_type=request.data.get("scenario_type"),
            conversation_id=request.data.get("conversation_id"),
            content_item_id=request.data.get("content_item_id"),
            user=user,
            response_id=request.data.get("response_id"),
            theme=request.data.get("theme"),
            assistant_role=request.data.get("assistant_role"),
            user_role=request.data.get("user_role"),
            potential_directions=request.data.get("potential_directions"),
            setting=request.data.get("setting"),
            example=request.data.get("example"),
            additional_data=request.data.get("additional_data"),
            practice_topic=request.data.get("practice_topic"),
            language=request.data.get("language", "English"),
        )

        conversation = result["conversation"]
        response_data = result["response"]
        user_message = result["messages"]["user_message"]
        assistant_message = result["messages"]["assistant_message"]

        return Response(
            {
                "conversation_id": str(conversation.id),
                "response": response_data,
                "messages": {
                    "user_message_id": {
                        "id": str(user_message.id),
                        "content": user_message.content,
                    },
                    "assistant_message_id": {
                        "id": str(assistant_message.id),
                        "content": assistant_message.content,
                    },
                },
            },
            status=status.HTTP_200_OK,
        )

    def _handle_suggestions(self, request):
        """Maneja las sugerencias de respuestas."""
        result = get_suggestions(
            assistant_message=request.data.get("assistant_message"),
            scenario_context=request.data.get("scenario_context"),
            language=request.data.get("language", "English"),
        )

        return Response(
            result,
            status=status.HTTP_200_OK,
        )

    def _handle_start(self, request):
        """Maneja el inicio de conversaciones con audio."""
        result = start_conversation(
            scenario_type=request.data.get("scenario_type"),
            language=request.data.get("language", "English"),
            theme=request.data.get("theme"),
            assistant_role=request.data.get("assistant_role"),
            user_role=request.data.get("user_role"),
            potential_directions=request.data.get("potential_directions"),
            setting=request.data.get("setting"),
            example=request.data.get("example"),
            additional_data=request.data.get("additional_data"),
            practice_topic=request.data.get("practice_topic"),
        )

        return Response(
            {
                "conversation_id": result["conversation_id"],
                "response_id": result["response_id"],
                "audio_duration": result["audio_duration"],
                "voice_used": result["voice_used"],
                "provider": result["provider"],
                "audio_base64": None,  # Podríamos convertir a base64 si es necesario
                "message": "Audio recibido correctamente. Usa el audio_content para reproducir.",
            },
            status=status.HTTP_200_OK,
        )
