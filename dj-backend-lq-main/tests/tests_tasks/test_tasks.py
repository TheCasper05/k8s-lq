from unittest.mock import patch

from apps.tasks.users.tasks import example_task as users_example_task
from apps.tasks.institutions.tasks import example_task as institutions_example_task
from apps.tasks.scenarios.tasks import example_task as scenarios_example_task


class TestUsersTasks:
    """Tests for users module tasks."""

    def test_users_example_task_can_be_imported(self):
        """Test that users.example_task can be imported without side effects."""
        assert users_example_task is not None
        assert hasattr(users_example_task, "delay")
        assert hasattr(users_example_task, "apply_async")

    @patch("apps.tasks.users.tasks.logger")
    def test_users_example_task_execution_success(self, mock_logger):
        """Test successful execution of users.example_task."""
        result = users_example_task("arg1", "arg2", key1="value1", key2="value2")

        assert result["status"] == "success"
        assert "message" in result
        mock_logger.info.assert_called_once()
        mock_logger.error.assert_not_called()

    @patch("apps.tasks.users.tasks.logger")
    def test_users_example_task_logs_info(self, mock_logger):
        """Test that users.example_task logs info messages."""
        users_example_task("test_arg", test_key="test_value")

        # Verify logger.info was called
        assert mock_logger.info.called
        call_args = mock_logger.info.call_args[0][0]
        assert "Executing users.example_task" in call_args

    def test_users_example_task_can_be_called_with_delay(self):
        """Test that users.example_task can be called with .delay() method."""
        # This tests that the task is properly decorated as a Celery task
        # In a real scenario, this would return an AsyncResult
        # We're just checking the method exists and is callable
        assert callable(users_example_task.delay)


class TestInstitutionsTasks:
    """Tests for institutions module tasks."""

    def test_institutions_example_task_can_be_imported(self):
        """Test that institutions.example_task can be imported without side effects."""
        assert institutions_example_task is not None
        assert hasattr(institutions_example_task, "delay")
        assert hasattr(institutions_example_task, "apply_async")

    @patch("apps.tasks.institutions.tasks.logger")
    def test_institutions_example_task_execution_success(self, mock_logger):
        """Test successful execution of institutions.example_task."""
        result = institutions_example_task()

        assert result["status"] == "success"
        assert "message" in result
        mock_logger.info.assert_called_once()
        mock_logger.error.assert_not_called()


class TestScenariosTasks:
    """Tests for scenarios module tasks."""

    def test_scenarios_example_task_can_be_imported(self):
        """Test that scenarios.example_task can be imported without side effects."""
        assert scenarios_example_task is not None
        assert hasattr(scenarios_example_task, "delay")
        assert hasattr(scenarios_example_task, "apply_async")

    @patch("apps.tasks.scenarios.tasks.logger")
    def test_scenarios_example_task_execution_success(self, mock_logger):
        """Test successful execution of scenarios.example_task."""
        result = scenarios_example_task()

        assert result["status"] == "success"
        assert "message" in result
        mock_logger.info.assert_called_once()
        mock_logger.error.assert_not_called()


class TestTasksModuleStructure:
    """Tests for tasks module structure and autodiscovery."""

    def test_all_task_modules_can_be_imported(self):
        """Test that all task modules can be imported without errors."""
        from apps.tasks import users, institutions, scenarios

        assert users is not None
        assert institutions is not None
        assert scenarios is not None

    def test_tasks_have_correct_names(self):
        """Test that tasks have correct names for Celery routing."""
        assert users_example_task.name == "users.example_task"
        assert institutions_example_task.name == "institutions.example_task"
        assert scenarios_example_task.name == "scenarios.example_task"
