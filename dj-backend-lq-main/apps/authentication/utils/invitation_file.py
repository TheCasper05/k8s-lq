"""
Utility for parsing bulk invitation files (CSV/Excel).
Handles Base64 encoded files and extracts invitation data.
This class only handles file parsing, not business logic validation.
"""

import base64
import csv
import io
import re
import openpyxl
from django.core.exceptions import ValidationError
from typing import List, Dict, Any, Tuple
from authentication.models import Workspace, Classroom, UserWorkspaceMembership
from authentication.enums import WorkspaceRole


class InvitationFileParser:
    """Parser for bulk invitation files in CSV or Excel format."""

    REQUIRED_COLUMNS = ["Email", "Workspace Slug", "Role"]
    OPTIONAL_COLUMNS = ["Classroom Names", "Welcome Message"]
    ALL_COLUMNS = REQUIRED_COLUMNS + OPTIONAL_COLUMNS

    # RFC 5322 simplified email regex
    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def __init__(self, base64_file: str):
        """
        Initialize parser with base64 encoded file.

        Args:
            base64_file: Base64 encoded string of the file
        """
        self.base64_file = base64_file
        self.file_data = None
        self.file_type = None
        self.header_mapping = None  # Maps normalized headers to expected column names

    def parse(self) -> List[Dict[str, Any]]:
        """
        Parse the file and return list of invitation data.
        Only validates file format and basic data structure, not business rules.

        Returns:
            List of dictionaries with invitation data

        Raises:
            ValidationError: If file format is invalid or data is malformed
        """
        # Decode base64
        try:
            self.file_data = base64.b64decode(self.base64_file)
        except Exception as e:
            raise ValidationError(f"Invalid base64 encoding: {str(e)}")

        # Detect file type and parse
        if self._is_excel():
            return self._parse_excel()
        else:
            return self._parse_csv()

    def _is_excel(self) -> bool:
        """Detect if file is Excel format."""
        # Excel files start with PK (ZIP signature)
        return self.file_data[:2] == b"PK"

    def _normalize_header(self, header: str) -> str:
        """
        Normalize header by trimming whitespace and converting to lowercase.

        Args:
            header: Original header string

        Returns:
            Normalized header string
        """
        if header is None:
            return ""
        return str(header).strip().lower()

    def _build_header_mapping(self, file_headers: List[str]) -> Dict[str, str]:
        """
        Build mapping from expected column names to original file headers.

        Args:
            file_headers: List of headers from the file

        Returns:
            Dictionary mapping expected column names to original file headers

        Raises:
            ValidationError: If required columns are missing
        """
        # Normalize expected columns
        normalized_expected = {
            self._normalize_header(col): col for col in self.ALL_COLUMNS
        }

        # Build mapping from expected columns to original file headers
        # Maps: expected_column -> original_file_header
        header_mapping = {}
        for file_header in file_headers:
            normalized = self._normalize_header(file_header)
            if normalized in normalized_expected:
                expected_col = normalized_expected[normalized]
                header_mapping[expected_col] = file_header

        # Check for required columns
        missing_required = []
        for col in self.REQUIRED_COLUMNS:
            if col not in header_mapping:
                missing_required.append(col)

        if missing_required:
            raise ValidationError(
                f"Missing required columns: {', '.join(missing_required)}"
            )

        return header_mapping

    def _parse_csv(self) -> List[Dict[str, Any]]:
        """Parse CSV file."""
        try:
            # Try UTF-8 first
            text_data = self.file_data.decode("utf-8")
        except UnicodeDecodeError:
            # Fallback to latin-1
            try:
                text_data = self.file_data.decode("latin-1")
            except Exception as e:
                raise ValidationError(f"Unable to decode CSV file: {str(e)}")

        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(text_data))
        file_headers = csv_reader.fieldnames or []

        # Build header mapping
        self.header_mapping = self._build_header_mapping(file_headers)

        return self._process_rows(csv_reader)

    def _parse_excel(self) -> List[Dict[str, Any]]:
        """Parse Excel file (XLS/XLSX)."""
        try:
            workbook = openpyxl.load_workbook(
                io.BytesIO(self.file_data), read_only=True
            )
            sheet = workbook.active

            # Get headers from first row
            headers = [cell.value for cell in sheet[1]]

            # Build header mapping
            self.header_mapping = self._build_header_mapping(headers)

            # Process rows
            rows = []
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if any(row):  # Skip empty rows
                    row_dict = dict(zip(headers, row))
                    rows.append(row_dict)

            return self._process_rows(rows)

        except Exception as e:
            raise ValidationError(f"Error parsing Excel file: {str(e)}")

    def _process_rows(self, rows) -> List[Dict[str, Any]]:
        """
        Process rows from CSV or Excel.
        Only validates format, not business logic.

        Args:
            rows: Iterator or list of row dictionaries

        Returns:
            List of parsed invitation data dictionaries
        """
        invitations = []

        for idx, row in enumerate(rows, start=2):  # Start at 2 (after header)
            try:
                invitation_data = self._process_row(row, idx)
                if invitation_data:
                    invitation_data["row_number"] = (
                        idx  # Add row number for validation errors
                    )
                    invitations.append(invitation_data)
            except ValidationError:
                # Re-raise with row number context
                raise

        if not invitations:
            raise ValidationError("No valid invitation data found in file")

        return invitations

    def _get_column_value(self, row: Dict[str, Any], expected_column: str) -> Any:
        """
        Get column value from row using normalized header mapping.

        Args:
            row: Dictionary with row data
            expected_column: Expected column name (e.g., "Email", "Workspace Slug")

        Returns:
            Column value or None if not found
        """
        if not self.header_mapping:
            # Fallback to direct access if mapping not available
            return row.get(expected_column)

        # Get the original file header that corresponds to this expected column
        original_header = self.header_mapping.get(expected_column)
        if not original_header:
            return None

        # Get value using the original header
        return row.get(original_header)

    def _process_row(self, row: Dict[str, Any], row_number: int) -> Dict[str, Any]:
        """
        Process a single row - only basic format validation.

        Args:
            row: Dictionary with row data
            row_number: Row number for error messages

        Returns:
            Processed invitation data dictionary
        """
        # Check required columns using normalized headers
        missing_columns = []
        for col in self.REQUIRED_COLUMNS:
            value = self._get_column_value(row, col)
            if not value or (isinstance(value, str) and not value.strip()):
                missing_columns.append(col)

        if missing_columns:
            raise ValidationError(
                f"Row {row_number}: Missing required columns: {', '.join(missing_columns)}"
            )

        # Extract and validate email format
        email_value = self._get_column_value(row, "Email")
        email = str(email_value).strip().lower() if email_value else ""
        if not email:
            raise ValidationError(f"Row {row_number}: Email is required")
        if len(email) > 254:
            raise ValidationError(
                f"Row {row_number}: Email exceeds maximum length of 254 characters"
            )
        if not self.EMAIL_REGEX.match(email):
            raise ValidationError(f"Row {row_number}: Invalid email format: {email}")

        # Extract workspace_slug
        workspace_slug_value = self._get_column_value(row, "Workspace Slug")
        workspace_slug = (
            str(workspace_slug_value).strip() if workspace_slug_value else ""
        )
        if not workspace_slug:
            raise ValidationError(f"Row {row_number}: Workspace slug is required")

        # Extract role
        role_value = self._get_column_value(row, "Role")
        role = str(role_value).strip().lower() if role_value else ""
        if not role:
            raise ValidationError(f"Row {row_number}: Role is required")

        # Process optional classroom_names
        classroom_names = []
        classroom_names_value = self._get_column_value(row, "Classroom Names")
        if classroom_names_value:
            classroom_names_str = str(classroom_names_value).strip()
            if classroom_names_str:
                # Split by pipe and clean
                classroom_names = [
                    name.strip()
                    for name in classroom_names_str.split("|")
                    if name.strip()
                ]

        # Process optional welcome_message
        welcome_message = None
        welcome_message_value = self._get_column_value(row, "Welcome Message")
        if welcome_message_value:
            welcome_message_str = str(welcome_message_value).strip()
            if welcome_message_str and welcome_message_str.lower() not in [
                "",
                "none",
                "null",
            ]:
                welcome_message = welcome_message_str

        return {
            "email": email,
            "workspace_slug": workspace_slug,
            "role": role,
            "classroom_names": classroom_names,
            "welcome_message": welcome_message,
        }


class InvitationDataValidator:
    """
    Validator for bulk invitation data.
    Validates business rules: workspace exists, user permissions, classrooms, etc.
    """

    # Roles that can send invitations
    ALLOWED_SENDER_ROLES = [
        WorkspaceRole.TEACHER,
        WorkspaceRole.ADMIN_INSTITUCIONAL,
        WorkspaceRole.COORDINATOR,
        WorkspaceRole.ADMIN_SEDE,
    ]

    def __init__(self, current_user):
        """
        Initialize validator with current user.

        Args:
            current_user: The user attempting to create invitations
        """
        self.current_user = current_user
        self.workspace_cache = {}
        self.classroom_cache = {}
        self.user_memberships_cache = {}

    def validate(
        self, invitations_data: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Validate all invitation data and return results with row-by-row status.

        Args:
            invitations_data: List of parsed invitation dictionaries

        Returns:
            Tuple of (valid_invitations, validation_results)
            - valid_invitations: List of validated invitation data ready for creation
            - validation_results: List of dicts with row_number and errors/status
        """
        # Pre-load all workspaces and check user memberships
        self._preload_workspaces(invitations_data)
        self._preload_user_memberships()
        self._preload_classrooms(invitations_data)

        valid_invitations = []
        validation_results = []

        for inv_data in invitations_data:
            row_number = inv_data.get("row_number", 0)
            errors = []

            # Validate workspace exists
            workspace_slug = inv_data["workspace_slug"]
            workspace = self.workspace_cache.get(workspace_slug)
            if not workspace:
                errors.append(
                    f"Workspace '{workspace_slug}' does not exist or is not active"
                )

            # Validate role
            role = inv_data["role"]
            valid_roles = [choice[0] for choice in WorkspaceRole.choices]
            if role not in valid_roles:
                errors.append(
                    f"Invalid role '{role}'. Must be one of: {', '.join(valid_roles)}"
                )

            # Validate user permissions (only if workspace exists)
            has_permission = False
            if workspace:
                has_permission = self._check_user_permission(workspace)
                if not has_permission:
                    errors.append(
                        f"You don't have permission to send invitations to workspace '{workspace_slug}'. "
                        f"Required roles: {', '.join([r.value for r in self.ALLOWED_SENDER_ROLES])}"
                    )

            # Validate classrooms (only if workspace exists AND user has permission)
            classroom_ids = []
            if workspace and has_permission and inv_data.get("classroom_names"):
                classroom_errors, classroom_ids = self._validate_classrooms(
                    inv_data["classroom_names"], workspace
                )
                errors.extend(classroom_errors)

            # Build validation result
            if errors:
                validation_results.append(
                    {
                        "row_number": row_number,
                        "status": "error",
                        "errors": errors,
                    }
                )
            else:
                validation_results.append(
                    {
                        "row_number": row_number,
                        "status": "correct",
                        "errors": [],
                    }
                )

                # Add to valid invitations
                valid_invitations.append(
                    {
                        "email": inv_data["email"],
                        "workspace_id": workspace.id,
                        "role": role,
                        "classroom_ids": classroom_ids,
                        "welcome_message": inv_data.get("welcome_message"),
                        "row_number": row_number,
                    }
                )

        return valid_invitations, validation_results

    def _preload_workspaces(self, invitations_data: List[Dict[str, Any]]):
        """Pre-load all workspaces mentioned in the file."""
        workspace_slugs = {inv["workspace_slug"] for inv in invitations_data}
        workspaces = Workspace.objects.filter(slug__in=workspace_slugs, is_active=True)
        self.workspace_cache = {ws.slug: ws for ws in workspaces}

    def _preload_user_memberships(self):
        """Pre-load user's workspace memberships."""
        memberships = UserWorkspaceMembership.objects.filter(
            user=self.current_user, is_active=True
        ).select_related("workspace")

        for membership in memberships:
            workspace_id = membership.workspace_id
            if workspace_id not in self.user_memberships_cache:
                self.user_memberships_cache[workspace_id] = []
            self.user_memberships_cache[workspace_id].append(membership.role)

    def _preload_classrooms(self, invitations_data: List[Dict[str, Any]]):
        """Pre-load all classrooms that might be referenced."""
        # Group classroom names by workspace
        workspace_classrooms = {}
        for inv_data in invitations_data:
            workspace_slug = inv_data["workspace_slug"]
            classroom_names = inv_data.get("classroom_names", [])
            if classroom_names:
                if workspace_slug not in workspace_classrooms:
                    workspace_classrooms[workspace_slug] = set()
                workspace_classrooms[workspace_slug].update(classroom_names)

        # Load classrooms for each workspace
        for workspace_slug, classroom_names in workspace_classrooms.items():
            workspace = self.workspace_cache.get(workspace_slug)
            if workspace:
                classrooms = Classroom.objects.filter(
                    workspace=workspace, name__in=classroom_names, is_active=True
                )

                if workspace.id not in self.classroom_cache:
                    self.classroom_cache[workspace.id] = {}

                for classroom in classrooms:
                    self.classroom_cache[workspace.id][classroom.name] = classroom

    def _check_user_permission(self, workspace: Workspace) -> bool:
        """
        Check if current user has permission to send invitations to this workspace.

        Args:
            workspace: The workspace to check permissions for

        Returns:
            True if user has permission, False otherwise
        """
        user_roles = self.user_memberships_cache.get(workspace.id, [])

        # Check if user has any of the allowed roles
        for role in user_roles:
            if role in [r.value for r in self.ALLOWED_SENDER_ROLES]:
                return True

        return False

    def _validate_classrooms(
        self, classroom_names: List[str], workspace: Workspace
    ) -> Tuple[List[str], List[int]]:
        """
        Validate that classrooms exist and belong to the workspace.

        Args:
            classroom_names: List of classroom names to validate
            workspace: The workspace to check classrooms against

        Returns:
            Tuple of (errors, classroom_ids)
        """
        errors = []
        classroom_ids = []

        workspace_classrooms = self.classroom_cache.get(workspace.id, {})

        for classroom_name in classroom_names:
            classroom = workspace_classrooms.get(classroom_name)
            if not classroom:
                errors.append(
                    f"Classroom '{classroom_name}' does not exist in workspace '{workspace.slug}' "
                    f"or is not active"
                )
            else:
                classroom_ids.append(classroom.id)

        return errors, classroom_ids
