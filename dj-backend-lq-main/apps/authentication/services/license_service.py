"""
License service interface and implementation.

This module provides an abstraction layer for license management,
allowing easy integration of license logic without breaking existing code.

The service follows the Strategy pattern, making it easy to:
- Swap implementations (stub, real, mock for testing)
- Extend functionality without modifying existing code
- Test components in isolation
"""

from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

    User = AbstractUser


class LicenseService(ABC):
    """
    Abstract base class for license management services.

    This interface defines the contract that all license service
    implementations must follow. This allows for plug-and-play
    integration of license logic.

    To implement a real license service:
    1. Create a class that inherits from LicenseService
    2. Implement all abstract methods
    3. Register it using set_license_service() or configure it in settings
    """

    @abstractmethod
    def check_availability(
        self, user: "User", workspace, role: str, count: int = 1
    ) -> bool:
        """
        Check if a user has available licenses to invite users.

        Args:
            user: The user who wants to invite
            workspace: The workspace where the invitation is being created
            role: The role of the user being invited
            count: Number of invitations being created (default: 1)

        Returns:
            bool: True if user has available licenses, False otherwise
        """
        pass

    @abstractmethod
    def reserve_seat(
        self, user: "User", workspace, role: str, invitation_id: Optional[str] = None
    ) -> bool:
        """
        Reserve a license seat when an invitation is created.

        This should be called when an invitation is successfully created
        to reserve the license.

        Args:
            user: The user who created the invitation
            workspace: The workspace where the invitation is being created
            role: The role of the user being invited
            invitation_id: Optional invitation ID for tracking

        Returns:
            bool: True if seat was successfully reserved, False otherwise
        """
        pass

    @abstractmethod
    def release_seat(
        self, user: "User", workspace, role: str, invitation_id: Optional[str] = None
    ) -> None:
        """
        Release a license seat when an invitation is declined, revoked, or expired.

        This should be called when an invitation is no longer active
        to free up the license.

        Args:
            user: The user who created the invitation
            workspace: The workspace where the invitation was created
            role: The role of the user who was invited
            invitation_id: Optional invitation ID for tracking
        """
        pass

    @abstractmethod
    def get_available_count(self, user: "User", workspace, role: str) -> int:
        """
        Get the number of available licenses for a user in a workspace.

        Args:
            user: The user to check
            workspace: The workspace to check
            role: The role to check availability for

        Returns:
            int: Number of available licenses (0 or more)
        """
        pass


class StubLicenseService(LicenseService):
    """
    Stub implementation of LicenseService that always allows invitations.

    This is the default implementation that allows the system to work
    without license logic implemented. When you're ready to implement
    real license logic, simply replace this with your implementation.

    Usage:
        # In your settings or initialization code:
        from authentication.services.license_service import set_license_service
        from your_app.services import YourLicenseService

        set_license_service(YourLicenseService())
    """

    def check_availability(
        self, user: "User", workspace, role: str, count: int = 1
    ) -> bool:
        """
        Stub implementation: always returns True.

        Replace this with real license checking logic.
        """
        return True

    def reserve_seat(
        self, user: "User", workspace, role: str, invitation_id: Optional[str] = None
    ) -> bool:
        """
        Stub implementation: always returns True.

        Replace this with real license reservation logic.
        """
        return True

    def release_seat(
        self, user: "User", workspace, role: str, invitation_id: Optional[str] = None
    ) -> None:
        """
        Stub implementation: does nothing.

        Replace this with real license release logic.
        """
        pass

    def get_available_count(self, user: "User", workspace, role: str) -> int:
        """
        Stub implementation: returns a high number.

        Replace this with real license counting logic.
        """
        return 999999


# Global service instance (singleton pattern)
_license_service: Optional[LicenseService] = None


def get_license_service() -> LicenseService:
    """
    Get the current license service instance.

    Returns the configured license service, or a StubLicenseService
    if none has been configured.

    Returns:
        LicenseService: The current license service instance
    """
    global _license_service

    if _license_service is None:
        _license_service = StubLicenseService()

    return _license_service


def set_license_service(service: LicenseService) -> None:
    """
    Set the global license service instance.

    This allows you to configure which license service implementation
    to use. Call this during application initialization (e.g., in AppConfig.ready()).

    Args:
        service: The license service instance to use
    """
    global _license_service
    _license_service = service


def reset_license_service() -> None:
    """
    Reset the license service to the default stub implementation.

    Useful for testing or resetting configuration.
    """
    global _license_service
    _license_service = None
