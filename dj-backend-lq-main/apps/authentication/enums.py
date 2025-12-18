from django.db import models
from django.utils.translation import gettext_lazy as _


class PrimaryRole(models.TextChoices):
    """Primary role choices for UserProfile."""

    STUDENT = "student", _("Student")
    TEACHER = "teacher", _("Teacher")
    ADMIN_INSTITUCIONAL = "admin_institucional", _("Institutional Admin")


class WorkspaceType(models.TextChoices):
    """Workspace type choices."""

    PERSONAL = "personal", _("Personal")
    INSTITUTION_SEDE = "institution_sede", _("Institution Sede")
    SHARED = "shared", _("Shared")


class WorkspaceRole(models.TextChoices):
    """Workspace role choices for UserWorkspaceMembership."""

    ADMIN_INSTITUCIONAL = "admin_institucional", _("Institutional Admin")
    COORDINATOR = "coordinator", _("Coordinator")
    ADMIN_SEDE = "admin_sede", _("Sede Admin")
    TEACHER = "teacher", _("Teacher")
    STUDENT = "student", _("Student")
    VIEWER = "viewer", _("Viewer")


class MembershipStatus(models.TextChoices):
    """Membership status choices for UserWorkspaceMembership."""

    ACTIVE = "active", _("Active")
    INVITED = "invited", _("Invited")
    SUSPENDED = "suspended", _("Suspended")
    LEFT = "left", _("Left")


class DocumentType(models.TextChoices):
    """Document type choices for UserProfile."""

    CC = "CC", _("Cédula de Ciudadanía")
    CE = "CE", _("Cédula de Extranjería")
    DNI = "DNI", _("Documento Nacional de Identidad")
    PAS = "PAS", _("Pasaporte")
    TI = "TI", _("Tarjeta de Identidad")
    OTHER = "OTHER", _("Otro")


class InvitationStatus(models.TextChoices):
    """Invitation status choices."""

    PENDING = "pending", _("Pending")
    ACCEPTED = "accepted", _("Accepted")
    DECLINED = "declined", _("Declined")
    REVOKED = "revoked", _("Revoked")
    EXPIRED = "expired", _("Expired")


class ClassroomRole(models.TextChoices):
    """Classroom role choices for ClassroomMembership."""

    STUDENT = "student", _("Student")
    TEACHER = "teacher", _("Teacher")
    ASSISTANT = "assistant", _("Assistant")
