import logging
import graphene
from graphql import GraphQLError, Undefined
from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ValidationError, PermissionDenied
from .enums import InvitationStatus
from .models import Invitation
from .utils.invitation_file import InvitationFileParser, InvitationDataValidator
from .utils.authorization import get_user_admin_workspace_ids
from .services.email_service import resend_invitation_email

logger = logging.getLogger(__name__)


def _format_validation_errors(validation_results):
    """
    Format validation results into a readable error message for GraphQL.

    Args:
        validation_results: List of validation result dictionaries

    Returns:
        Formatted error message string
    """
    lines = ["Bulk invitation validation failed:"]
    lines.append("")

    for result in validation_results:
        row_num = result["row_number"]
        status = result["status"]
        errors = result.get("errors", [])

        if status == "error":
            lines.append(f"Row {row_num}: ERROR")
            for error in errors:
                lines.append(f"  - {error}")
        else:
            lines.append(f"Row {row_num}: CORRECT")

    return "\n".join(lines)


class LanguageCruddalsInterface:
    class ObjectType:
        @classmethod
        def get_objects(cls, objects, info, **kwargs):
            return objects


class UserProfileCruddalsInterface:
    class ObjectType:
        @classmethod
        def get_objects(cls, objects, info, **kwargs):
            return objects


class InstitutionCruddalsInterface:
    class ObjectType:
        @classmethod
        def get_objects(cls, objects, info, **kwargs):
            return objects


class WorkspaceCruddalsInterface:
    class ObjectType:
        @classmethod
        def get_objects(cls, objects, info, **kwargs):
            return objects


class UserWorkspaceMembershipCruddalsInterface:
    class ObjectType:
        @classmethod
        def get_objects(cls, objects, info, **kwargs):
            return objects


class ClassroomCruddalsInterface:
    class ObjectType:
        @classmethod
        def get_objects(cls, objects, info, **kwargs):
            return objects


class ClassroomMembershipCruddalsInterface:
    class ObjectType:
        @classmethod
        def get_objects(cls, objects, info, **kwargs):
            return objects


class InvitationCruddalsInterface:
    class ObjectType:
        @classmethod
        def get_objects(cls, objects, info, **kwargs):
            current_user = info.context.user
            if not current_user or not current_user.is_authenticated:
                return objects.none()

            admin_workspace_ids = get_user_admin_workspace_ids(current_user)
            return objects.filter(workspace_id__in=admin_workspace_ids)

    class ModelCreateField:
        class Meta:
            modify_input_argument = {
                "required": False,
                "default_value": Undefined,
            }
            extra_arguments = {
                "file": graphene.String(),
            }

        @staticmethod
        def pre_mutate(root, info, *args, **kwargs):
            """
            Pre-mutate hook: Si 'file' está presente, parsear, validar y convertir a input array.
            Si hay errores de validación, se devuelve un error estructurado con detalles por fila.
            """
            # Validar que no vengan ambos parámetros o ninguno
            if "file" in kwargs and "input" in kwargs:
                raise ValidationError(
                    "Cannot use both file and input arguments at the same time"
                )
            if "file" not in kwargs and "input" not in kwargs:
                raise ValidationError("Either file or input argument is required")
            if "input" in kwargs and len(kwargs["input"]) == 0:
                raise ValidationError("Input argument cannot be an empty array")

            file_b64 = kwargs.pop("file", None)

            if not file_b64:
                # No hay archivo, proceder normalmente con single invitation
                return (root, info, *args, kwargs)

            # 1. Parsear archivo (solo validación de formato)
            try:
                parser = InvitationFileParser(file_b64)
                invitations_data = parser.parse()
            except ValidationError as e:
                raise ValidationError(f"File parsing error: {str(e)}")
            except Exception as e:
                raise ValidationError(f"Unexpected error parsing file: {str(e)}")

            # 2. Validar datos (validación de negocio)
            current_user = info.context.user
            validator = InvitationDataValidator(current_user)

            try:
                valid_invitations, validation_results = validator.validate(
                    invitations_data
                )
            except Exception as e:
                raise ValidationError(f"Validation error: {str(e)}")

            # 3. Verificar si hay errores
            errors_found = [r for r in validation_results if r["status"] == "error"]

            if errors_found:
                # Formatear errores para GraphQL
                error_message = _format_validation_errors(validation_results)
                raise ValidationError(error_message)

            # 4. Convertir invitaciones válidas a formato de input
            input_list = []
            for inv_data in valid_invitations:
                input_obj = {
                    "email": inv_data["email"],
                    "workspace": inv_data["workspace_id"],
                    "role": inv_data["role"],
                    "status": InvitationStatus.PENDING,
                }

                # Agregar campos opcionales solo si tienen valor
                if inv_data.get("classroom_ids"):
                    input_obj["classrooms"] = inv_data["classroom_ids"]

                if inv_data.get("welcome_message"):
                    input_obj["welcome_message"] = inv_data["welcome_message"]

                input_list.append(input_obj)

            # Reemplazar o agregar el input como arreglo
            kwargs["input"] = input_list

            return (root, info, *args, kwargs)


class ResendInvitation(graphene.Mutation):
    """
    Mutation to resend an invitation email.

    This mutation validates:
    - User authentication
    - User has admin permissions for the invitation's workspace
    - Invitation exists and is in PENDING status
    - Invitation is not expired
    - Workspace is active

    The email sending result and resend history are stored in the invitation's metadata.
    """

    class Arguments:
        invitation_id = graphene.ID(
            required=True, description="ID of the invitation to resend"
        )

    # Return fields
    success = graphene.Boolean(description="Whether the email was sent successfully")
    invitation_id = graphene.ID(description="ID of the invitation that was resent")
    message = graphene.String(description="Success or error message")

    @staticmethod
    def mutate(root, info, invitation_id):
        """
        Execute the resend invitation mutation.

        Args:
            root: Root object (unused)
            info: GraphQL execution info containing context and user
            invitation_id: ID of the invitation to resend

        Returns:
            ResendInvitation instance with result

        Raises:
            GraphQLError: If validation fails or user is not authenticated
        """
        # Validate user is authenticated
        current_user = info.context.user
        if (
            not isinstance(current_user, AbstractBaseUser)
            or not current_user.is_authenticated
        ):
            raise GraphQLError("You must be logged in to perform this action.")

        try:
            result = resend_invitation_email(
                invitation_id=invitation_id,
                current_user=current_user,
            )

            if result["success"]:
                logger.info(
                    f"Invitation {invitation_id} resent successfully by user {current_user.id}"
                )
            else:
                logger.warning(
                    f"Failed to resend invitation {invitation_id} by user {current_user.id}: "
                    f"{result.get('email_result', {}).get('error', 'Unknown error')}"
                )

            return ResendInvitation(
                success=result["success"],
                invitation_id=invitation_id,
                message="Invitation email resent successfully"
                if result["success"]
                else "Failed to send invitation email",
            )

        except ValidationError as e:
            logger.warning(
                f"Validation error resending invitation {invitation_id} by user {current_user.id}: {str(e)}"
            )
            raise GraphQLError(str(e))
        except PermissionDenied as e:
            logger.warning(
                f"Permission denied for user {current_user.id} attempting to resend invitation {invitation_id}"
            )
            raise GraphQLError(str(e))
        except Invitation.DoesNotExist:
            logger.warning(
                f"Invitation {invitation_id} not found when user {current_user.id} attempted to resend"
            )
            raise GraphQLError("Invitation not found")
        except Exception as e:
            logger.error(
                f"Unexpected error resending invitation {invitation_id} by user {current_user.id}",
                exc_info=True,
            )
            raise GraphQLError(
                f"An error occurred while resending the invitation: {str(e)}"
            )
