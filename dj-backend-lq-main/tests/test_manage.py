import os
import sys
from unittest import mock
import pytest
from manage import main

# Import the main function from manage.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_django_settings_module_default():
    """Test that DJANGO_SETTINGS_MODULE is set correctly."""
    with mock.patch.dict(os.environ, clear=True):
        with mock.patch("django.core.management.execute_from_command_line"):
            main()
            assert os.environ.get("DJANGO_SETTINGS_MODULE") == "config.settings"


def test_execute_from_command_line_called_with_sys_argv():
    """Test that execute_from_command_line is called with sys.argv."""
    test_args = ["manage.py", "test"]
    with mock.patch.object(sys, "argv", test_args):
        with mock.patch(
            "django.core.management.execute_from_command_line"
        ) as mock_execute:
            main()
            mock_execute.assert_called_once_with(test_args)


def test_import_error_handling():
    """Test that ImportError is handled correctly."""
    with mock.patch.dict(os.environ, clear=True):
        with mock.patch(
            "django.core.management.execute_from_command_line",
            side_effect=ImportError("Test error"),
        ):
            with pytest.raises(ImportError) as excinfo:
                main()
            assert "Test error" in str(excinfo.value)


def test_main_function_execution():
    """Test the complete execution flow of the main function."""
    with mock.patch.dict(os.environ, clear=True):
        with mock.patch(
            "django.core.management.execute_from_command_line"
        ) as mock_execute:
            main()
            assert mock_execute.called
            assert os.environ.get("DJANGO_SETTINGS_MODULE") == "config.settings"
