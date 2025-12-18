"""
Authorization utilities for authentication app.

This module contains reusable functions for checking user permissions
and workspace access rights.
"""

from typing import TYPE_CHECKING

from ..enums import WorkspaceRole, MembershipStatus
from ..models import UserWorkspaceMembership

if TYPE_CHECKING:
    from ..models import User, Workspace


def has_workspace_admin_permission(
    user: "User", workspace: "Workspace", include_teacher: bool = False
) -> bool:
    """
    Check if user has admin permissions for a workspace.

    Admin roles include:
    - ADMIN_INSTITUCIONAL (Institutional Admin)
    - COORDINATOR (Coordinator)
    - ADMIN_SEDE (Sede Admin)
    - TEACHER (optional, if include_teacher=True)

    Args:
        user: The user to check permissions for
        workspace: The workspace to check permissions for
        include_teacher: If True, also allows TEACHER role (default: False)

    Returns:
        True if user has admin permissions, False otherwise
    """
    allowed_roles = [
        WorkspaceRole.ADMIN_INSTITUCIONAL,
        WorkspaceRole.COORDINATOR,
        WorkspaceRole.ADMIN_SEDE,
    ]

    if include_teacher:
        allowed_roles.append(WorkspaceRole.TEACHER)

    return UserWorkspaceMembership.objects.filter(
        user=user,
        workspace=workspace,
        role__in=allowed_roles,
        status=MembershipStatus.ACTIVE,
        is_active=True,
    ).exists()


def get_user_admin_workspace_ids(user: "User", include_teacher: bool = False) -> list:
    """
    Get list of workspace IDs where user has admin permissions.

    Args:
        user: The user to get workspace IDs for
        include_teacher: If True, also includes workspaces where user is TEACHER

    Returns:
        List of workspace IDs where user has admin permissions
    """
    allowed_roles = [
        WorkspaceRole.ADMIN_INSTITUCIONAL,
        WorkspaceRole.COORDINATOR,
        WorkspaceRole.ADMIN_SEDE,
    ]

    if include_teacher:
        allowed_roles.append(WorkspaceRole.TEACHER)

    return list(
        UserWorkspaceMembership.objects.filter(
            user=user,
            role__in=allowed_roles,
            status=MembershipStatus.ACTIVE,
            is_active=True,
        ).values_list("workspace_id", flat=True)
    )
