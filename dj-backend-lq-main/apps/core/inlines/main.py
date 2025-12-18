from unfold.admin import StackedInline, TabularInline
from nested_admin.nested import (
    NestedStackedInline,
    NestedTabularInline,
    NestedInlineFormSet,
)
from django.db import models
from ..forms.widgets import AutoResizingTextarea


class BaseTabularInline(TabularInline, NestedTabularInline):
    # class BaseTabularInline(NestedTabularInline, TabularInline): # TODO- El orden esta alterando que el nested no pueda funcionar o el unfold no pueda, mirar como organizar
    formfield_overrides: dict = {  # type: ignore
        models.TextField: {"widget": AutoResizingTextarea},
    }
    formset = NestedInlineFormSet

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """
        Hook for specifying the form Field instance for a given database Field
        instance. If kwargs are given, they're passed to the form Field's constructor.
        """
        try:
            return super().formfield_for_dbfield(db_field, request, **kwargs)
        except Exception:
            return db_field.formfield(**kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        """
        Get the formset for this inline admin.
        """
        try:
            return super().get_formset(request, obj, **kwargs)
        except Exception:
            return super(TabularInline, self).get_formset(request, obj, **kwargs)


class BaseStackedInline(NestedStackedInline, StackedInline):
    formfield_overrides: dict = {  # type: ignore
        models.TextField: {"widget": AutoResizingTextarea},
    }
    formset = NestedInlineFormSet

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """
        Hook for specifying the form Field instance for a given database Field
        instance. If kwargs are given, they're passed to the form Field's constructor.
        """
        try:
            return super().formfield_for_dbfield(db_field, request, **kwargs)
        except Exception:
            return db_field.formfield(**kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        """
        Get the formset for this inline admin.
        """
        try:
            return super().get_formset(request, obj, **kwargs)
        except Exception:
            return super(StackedInline, self).get_formset(request, obj, **kwargs)
