from core.models import AuditModel
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ContentType(models.TextChoices):
    CONVERSATION = "conversation", "Conversation"
    VIDEO = "video", "Video"
    SLIDE_DECK = "slide_deck", "Slide Deck"
    INTERACTIVE_EXERCISE = "interactive_exercise", "Interactive Exercise"
    QUIZ = "quiz", "Quiz"
    READING_MATERIAL = "reading_material", "Reading Material"
    AUDIO = "audio", "Audio"
    READ = "read", "Read"
    WRITE = "write", "Write"
    COURSE = "course", "Course"


class ConversationStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    PAUSED = "paused", _("Paused")
    COMPLETED = "completed", _("Completed")
    ABANDONED = "abandoned", _("Abandoned")


class MessageSender(models.TextChoices):
    USER = "user", _("User")
    ASSISTANT = "assistant", _("Assistant")


class ContentItem(AuditModel):
    content_type = models.CharField(max_length=50, choices=ContentType.choices)

    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    owner_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="owned_content",
    )
    owner_institution = models.ForeignKey(
        "authentication.Institution",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="institution_content",
    )

    workspace = models.ForeignKey(
        "authentication.Workspace", null=True, blank=True, on_delete=models.SET_NULL
    )

    language = models.ForeignKey(
        "authentication.Language", null=True, blank=True, on_delete=models.SET_NULL
    )
    # level = models.ForeignKey("authentication.ProficiencyLevel", null=True, blank=True, on_delete=models.SET_NULL)

    content_data = models.JSONField(default=dict)
    metadata = models.JSONField(default=dict)

    version = models.IntegerField(default=1)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)

    nro_order = models.IntegerField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        db_table = "content_items"
        app_label = "activities"


class Conversation(AuditModel):
    """Conversation model for tracking user conversations with AI assistant."""

    submission = models.ForeignKey(
        "AssignmentSubmission",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    content_item = models.ForeignKey(
        ContentItem,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="conversations",
    )

    status = models.CharField(
        max_length=20,
        choices=ConversationStatus.choices,
        default=ConversationStatus.ACTIVE,
    )

    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "conversations"
        app_label = "activities"
        ordering = ["-started_at"]

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"Conversation {self.id} - {username}"


class Message(models.Model):
    """Message model for tracking individual messages in conversations."""

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.CharField(
        max_length=20,
        choices=MessageSender.choices,
    )

    content = models.TextField(null=True, blank=True)
    audio_url = models.TextField(null=True, blank=True)
    transcription = models.TextField(null=True, blank=True)

    # LLM tracking
    input_tokens = models.IntegerField(null=True, blank=True)
    output_tokens = models.IntegerField(null=True, blank=True)
    total_tokens = models.IntegerField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    time_taken = models.IntegerField(null=True, blank=True)  # in milliseconds
    model_name = models.CharField(max_length=100, null=True, blank=True)

    suggested_answers = models.JSONField(null=True, blank=True)
    helps_used = models.JSONField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    nro_order = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "messages"
        app_label = "activities"
        ordering = ["nro_order"]
        unique_together = [["conversation", "nro_order"]]

    def __str__(self):
        return f"Message {self.nro_order} - {self.get_sender_display()}"


class AssignmentSubmission(models.Model):
    """Assignment submission model for tracking student submissions."""

    assignment = models.ForeignKey(
        "Assignment",
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignment_submissions",
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("not_started", "Not Started"),
            ("in_progress", "In Progress"),
            ("submitted", "Submitted"),
            ("graded", "Graded"),
            ("late", "Late"),
        ],
        default="not_started",
    )

    started_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="graded_submissions",
    )

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "assignment_submissions"
        app_label = "activities"
        unique_together = [["assignment", "user"]]

    def __str__(self):
        return f"Submission {self.id} - {self.user.username}"


class Assignment(AuditModel):
    """Assignment model for classroom assignments."""

    classroom = models.ForeignKey(
        "authentication.Classroom",
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assigned_assignments",
    )
    content_item = models.ForeignKey(
        ContentItem,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assignments",
    )
    course = models.ForeignKey(
        "Course",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assignments",
    )

    due_date_start = models.DateTimeField(null=True, blank=True)
    due_date_end = models.DateTimeField(null=True, blank=True)
    allow_late_submission = models.BooleanField(default=False)

    settings = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "assignments"
        app_label = "activities"

    def __str__(self):
        return f"Assignment {self.id} - {self.classroom.name}"


class Course(AuditModel):
    """Course model (placeholder - may need to be moved to another app)."""

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    # Ownership contextual
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_courses",
    )
    owner_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="owned_courses",
    )
    owner_institution = models.ForeignKey(
        "authentication.Institution",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="owned_courses",
    )
    workspace = models.ForeignKey(
        "authentication.Workspace",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="courses",
    )

    language = models.ForeignKey(
        "authentication.Language",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    # level = models.ForeignKey(
    #     "authentication.ProficiencyLevel",
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL,
    # )

    metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        db_table = "courses"
        app_label = "activities"

    def __str__(self):
        return self.name
