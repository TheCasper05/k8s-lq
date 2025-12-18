import graphene
from graphene_django_cruddals import (
    DjangoProjectCruddals,
    build_files_for_client_schema_cruddals,
)
from django.contrib.auth.models import AbstractBaseUser
from graphql import GraphQLError
from core.schema import UserCruddalsInterface
from authentication.schema import (
    LanguageCruddalsInterface,
    UserProfileCruddalsInterface,
    InstitutionCruddalsInterface,
    WorkspaceCruddalsInterface,
    UserWorkspaceMembershipCruddalsInterface,
    ClassroomCruddalsInterface,
    ClassroomMembershipCruddalsInterface,
    InvitationCruddalsInterface,
    ResendInvitation,
)


def login_required(func):
    def wrapper(*args, **kwargs):
        info = args[1]
        user = info.context.user

        if not isinstance(user, AbstractBaseUser) or not user.is_authenticated:
            raise GraphQLError(
                "You must be logged in to perform this action.",
                nodes=[info.field_nodes[0]] if hasattr(info, "field_nodes") else None,
            )

        return func(*args, **kwargs)

    return wrapper


class AuthenticationInterface:
    class ModelCreateField:
        @login_required
        def pre_mutate(*args, **kwargs):
            return (*args, kwargs)

    class ModelReadField:
        @login_required
        def pre_resolver(*args, **kwargs):
            return (*args, kwargs)

    class ModelUpdateField:
        @login_required
        def pre_mutate(*args, **kwargs):
            return (*args, kwargs)

    class ModelDeleteField:
        @login_required
        def pre_mutate(*args, **kwargs):
            return (*args, kwargs)

    class ModelDeactivateField:
        @login_required
        def pre_mutate(*args, **kwargs):
            return (*args, kwargs)

    class ModelActivateField:
        @login_required
        def pre_mutate(*args, **kwargs):
            return (*args, kwargs)

    class ModelListField:
        @login_required
        def pre_resolver(*args, **kwargs):
            return (*args, kwargs)

    class ModelSearchField:
        @login_required
        def pre_resolver(*args, **kwargs):
            return (*args, kwargs)


class ExcludeAiAuditModelFieldsInterface:
    class ObjectType:
        class Meta:
            exclude_fields = (
                "input_tokens",
                "output_tokens",
                "total_tokens",
                "time_taken",
                "cost",
                "model_name",
            )

    class InputObjectType:
        class Meta:
            exclude_fields = (
                "input_tokens",
                "output_tokens",
                "total_tokens",
                "time_taken",
                "cost",
                "model_name",
            )

    class UpdateInputObjectType:
        class Meta:
            exclude_fields = (
                "input_tokens",
                "output_tokens",
                "total_tokens",
                "time_taken",
                "cost",
                "model_name",
            )

    class CreateInputObjectType:
        class Meta:
            exclude_fields = (
                "input_tokens",
                "output_tokens",
                "total_tokens",
                "time_taken",
                "cost",
                "model_name",
            )


class LingoQuestoProjectCruddals(DjangoProjectCruddals):
    class Meta:
        exclude_apps = (
            "contenttypes",
            "sessions",
            "admin",
            "unfold",
            "unfold_filters",
            "unfold_forms",
            "unfold_inlines",
            "unfold_importexport",
            "unfold_guardian",
            "unfold_simple_history",
            "allauth",
            "nested_admin",
            "headless",
            "google",
            "microsoft",
            "dummy",
            # "core",
            "storages",
        )
        cruddals_interfaces = (
            AuthenticationInterface,
            ExcludeAiAuditModelFieldsInterface,
        )
        exclude_functions = ("list",)
        settings_for_app = {
            "authentication": {
                "settings_for_model": {
                    "User": {
                        "cruddals_interfaces": (UserCruddalsInterface,),
                    },
                    "Language": {
                        "cruddals_interfaces": (LanguageCruddalsInterface,),
                    },
                    "UserProfile": {
                        "cruddals_interfaces": (UserProfileCruddalsInterface,),
                    },
                    "Institution": {
                        "cruddals_interfaces": (InstitutionCruddalsInterface,),
                    },
                    "Workspace": {
                        "exclude_functions": (
                            "create",
                            "update",
                            "delete",
                            "deactivate",
                            "activate",
                        ),
                        "cruddals_interfaces": (WorkspaceCruddalsInterface,),
                    },
                    "UserWorkspaceMembership": {
                        "exclude_functions": (
                            "create",
                            "update",
                            "delete",
                            "deactivate",
                            "activate",
                        ),
                        "cruddals_interfaces": (
                            UserWorkspaceMembershipCruddalsInterface,
                        ),
                    },
                    "Classroom": {
                        "cruddals_interfaces": (ClassroomCruddalsInterface,),
                    },
                    "ClassroomMembership": {
                        "cruddals_interfaces": (ClassroomMembershipCruddalsInterface,),
                    },
                    "Invitation": {
                        "cruddals_interfaces": (InvitationCruddalsInterface,),
                    },
                }
            }
        }


class Query(LingoQuestoProjectCruddals.Query):
    # debug = graphene.Field(DjangoDebug, name="_debug")
    pass


class Mutation(LingoQuestoProjectCruddals.Mutation):
    resend_invitation = ResendInvitation.Field(description="Resend an invitation email")


schema = graphene.Schema(query=Query, mutation=Mutation)

# This will generate the client files for the schema
if False:
    build_files_for_client_schema_cruddals(
        schema,
    )
