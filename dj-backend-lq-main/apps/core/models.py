import re
import uuid
from django.db import models
from django_stubs_ext.db.models import TypedModelMeta
from shortuuid.django_fields import ShortUUIDField
from django_currentuser.db.models import CurrentUserField
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class DynamicPrefixShortUUIDField(ShortUUIDField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _split_pascal_case(self, text: str) -> list[str]:
        """
        Split PascalCase text into individual words.
        Example: 'PracticeAssignment' -> ['Practice', 'Assignment']
        """
        # Insert space before uppercase letters (except the first one)
        spaced = re.sub(r"(?<!^)(?=[A-Z])", " ", text)
        # Split by spaces and filter empty strings
        words = [word for word in spaced.split() if word]
        return words

    def _truncate_word(self, word: str, max_length: int) -> str:
        """
        Intelligently truncate a word to max_length, preserving readability.
        """
        if len(word) <= max_length:
            return word.lower()
        return word[:max_length].lower()

    def _generate_readable_prefix(self, words: list[str]) -> str:
        """
        Generate readable prefix with underscores, keeping reasonable length.
        Target: max 12 characters total (before the final _)
        """
        if not words:
            return "unkn"

        num_words = len(words)

        if num_words == 1:
            # Single word: up to 8 characters for better readability
            return self._truncate_word(words[0], 8)

        elif num_words == 2:
            # Two words: 4+4 characters with separator
            word1 = self._truncate_word(words[0], 4)
            word2 = self._truncate_word(words[1], 4)
            return f"{word1}_{word2}"

        elif num_words == 3:
            # Three words: 3+3+3 characters with separators
            word1 = self._truncate_word(words[0], 3)
            word2 = self._truncate_word(words[1], 3)
            word3 = self._truncate_word(words[2], 3)
            return f"{word1}_{word2}_{word3}"

        else:
            # Four or more words: 3+3+3 for first 3 words
            word1 = self._truncate_word(words[0], 3)
            word2 = self._truncate_word(words[1], 3)
            word3 = self._truncate_word(words[2], 3)
            return f"{word1}_{word2}_{word3}"

    def _generate_automatic_prefix(self, model_name: str) -> str:
        """
        Automatically generate readable prefix from model name using PascalCase separation.
        """
        words = self._split_pascal_case(model_name)
        prefix = self._generate_readable_prefix(words)

        # Add final separator for the UUID part
        return prefix + "_"

    def get_default(self):
        model = self.model
        model_name = model.__name__

        # Generate prefix automatically with separators
        prefix = self._generate_automatic_prefix(model_name)

        current_default = super().get_default()
        return prefix + current_default


class AuditModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        blank=True,
    )
    public_id = DynamicPrefixShortUUIDField(
        length=16,
        max_length=40,
        editable=False,
        blank=True,
    )
    created_by = CurrentUserField(
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_created",
        help_text=_("User who created this record."),
        verbose_name=_("Created By"),
        editable=True,
        null=True,
        blank=True,
    )
    updated_by = CurrentUserField(
        on_update=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_updated",
        help_text=_("User who last modified this record."),
        verbose_name=_("Updated By"),
        editable=True,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Date when this record was created."),
        verbose_name=_("Creation Date"),
        editable=False,
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Date when this record was last modified."),
        verbose_name=_("Last Updated"),
        editable=False,
        null=True,
        blank=True,
    )
    # Soft delete fields
    is_active = models.BooleanField(
        default=True,
        help_text=_("Indicates whether this record is active in the platform."),
        verbose_name=_("Active"),
        blank=True,
    )
    deleted_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Deleted At")
    )
    deleted_by = CurrentUserField(
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_deleted",
        verbose_name=_("Deleted By"),
        editable=True,
        null=True,
        blank=True,
    )

    class Meta(TypedModelMeta):
        abstract = True
        ordering = ["-created_at"]

    def save(self, *args, **kwargs) -> None:
        if self.created_at is None:
            self.created_at = timezone.now()
        was_creating = self._state.adding
        if was_creating:
            self.is_active = True
        self.updated_at = timezone.now()
        if not was_creating and not self.is_active:
            self.deleted_at = timezone.now()
            self.deleted_by = self.updated_by
        return super().save(*args, **kwargs)


class AiAuditModel(models.Model):
    input_tokens = models.IntegerField(
        help_text=_("Number of input tokens."),
        verbose_name=_("Input Tokens"),
        default=0,
        blank=True,
        null=True,
    )
    output_tokens = models.IntegerField(
        help_text=_("Number of output tokens."),
        verbose_name=_("Output Tokens"),
        default=0,
        blank=True,
        null=True,
    )
    total_tokens = models.IntegerField(
        help_text=_("Total number of tokens."),
        verbose_name=_("Total Tokens"),
        default=0,
        blank=True,
        null=True,
    )
    time_taken = models.FloatField(
        help_text=_("Time taken to generate the response."),
        verbose_name=_("Time Taken"),
        default=0,
        blank=True,
        null=True,
    )
    cost = models.FloatField(
        help_text=_("Cost of the response."),
        verbose_name=_("Cost"),
        default=0,
        blank=True,
        null=True,
    )
    model_name = models.CharField(
        help_text=_("Name of the model used."),
        verbose_name=_("Model Name"),
        blank=True,
        null=True,
        max_length=100,
    )

    class Meta(TypedModelMeta):
        abstract = True


class Feedback(AuditModel):
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    rating = models.IntegerField(
        blank=True,
        null=True,
        default=1,
        help_text="Rating from 1 to 5",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    class Meta:
        db_table = "feedback"
        app_label = "core"
