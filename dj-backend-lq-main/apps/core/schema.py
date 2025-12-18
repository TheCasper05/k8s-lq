import graphene


user_exclude_fields = (
    "last_login",
    "is_superuser",
    "is_staff",
    "groups",
    "user_permissions",
)


class UserCruddalsInterface:
    class ObjectType:
        user_type = graphene.String()

    class InputObjectType:
        class Meta:
            exclude_fields = user_exclude_fields

    class CreateInputObjectType:
        class Meta:
            exclude_fields = user_exclude_fields

    class UpdateInputObjectType:
        class Meta:
            exclude_fields = user_exclude_fields

    class ModelReadField:
        class Meta:
            extra_arguments = {"me": graphene.Boolean()}

        def pre_resolver(self, info, **kwargs):
            if "me" in kwargs:
                user = info.context.user
                kwargs = {"where": {"id": {"exact": user.pk}}}
            return self, info, kwargs
