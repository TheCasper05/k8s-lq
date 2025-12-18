import pytest
from unittest.mock import patch
from django.core.exceptions import ValidationError
from ..validators import (
    validate_file_category,
    validate_file_size,
    validate_file_extension,
    validate_usage_path,
    validate_usage_consistency,
)


class TestFileCategoryValidator:
    """Tests para validación de categorías de archivo."""

    def test_valid_categories(self):
        """Test que categorías válidas pasan la validación."""
        valid_categories = ["audio", "image", "pdf", "video"]
        for category in valid_categories:
            # No debe lanzar excepción
            validate_file_category(category)

    def test_invalid_category(self):
        """Test que categoría inválida lanza ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            validate_file_category("invalid")
        assert "no permitida" in str(exc_info.value)


class TestFileSizeValidator:
    """Tests para validación de tamaños de archivo."""

    @patch(
        "apps.files.validators.FILE_UPLOAD_MAX_SIZES",
        {
            "audio": 10 * 1024 * 1024,  # 10MB
            "image": 10 * 1024 * 1024,  # 10MB
        },
    )
    @patch(
        "apps.files.validators.FILE_UPLOAD_MAX_SIZE_GLOBAL", 100 * 1024 * 1024
    )  # 100MB
    def test_valid_size_within_category_limit(self):
        """Test que tamaño válido dentro del límite de categoría pasa."""
        # 5MB está dentro del límite de 10MB para audio
        validate_file_size(5 * 1024 * 1024, "audio")

    @patch(
        "apps.files.validators.FILE_UPLOAD_MAX_SIZES",
        {
            "audio": 10 * 1024 * 1024,  # 10MB
        },
    )
    @patch(
        "apps.files.validators.FILE_UPLOAD_MAX_SIZE_GLOBAL", 100 * 1024 * 1024
    )  # 100MB
    def test_size_exceeds_category_limit(self):
        """Test que tamaño que excede límite de categoría lanza error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_file_size(15 * 1024 * 1024, "audio")  # 15MB > 10MB
        assert "excede el límite" in str(exc_info.value)
        assert "categoría" in str(exc_info.value)

    @patch(
        "apps.files.validators.FILE_UPLOAD_MAX_SIZES",
        {
            "audio": 10 * 1024 * 1024,  # 10MB
        },
    )
    @patch(
        "apps.files.validators.FILE_UPLOAD_MAX_SIZE_GLOBAL", 100 * 1024 * 1024
    )  # 100MB
    def test_size_exceeds_global_limit(self):
        """Test que tamaño que excede límite global lanza error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_file_size(150 * 1024 * 1024, "audio")  # 150MB > 100MB
        assert "excede el límite global" in str(exc_info.value)


class TestFileExtensionValidator:
    """Tests para validación de extensiones de archivo."""

    def test_valid_audio_extensions(self):
        """Test que extensiones válidas para audio pasan."""
        valid_extensions = ["file.mp3", "file.wav", "file.ogg", "file.m4a", "file.aac"]
        for file_name in valid_extensions:
            validate_file_extension(file_name, "audio")

    def test_valid_image_extensions(self):
        """Test que extensiones válidas para imagen pasan."""
        valid_extensions = [
            "file.jpg",
            "file.jpeg",
            "file.png",
            "file.gif",
            "file.webp",
        ]
        for file_name in valid_extensions:
            validate_file_extension(file_name, "image")

    def test_invalid_extension_for_category(self):
        """Test que extensión inválida para categoría lanza error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_file_extension("file.mp3", "image")  # .mp3 no es válido para image
        assert "no es válida para la categoría" in str(exc_info.value)

    def test_no_extension(self):
        """Test que archivo sin extensión lanza error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_file_extension("file", "audio")
        assert "debe tener una extensión" in str(exc_info.value)


class TestUsagePathValidator:
    """Tests para validación de formato de usage path."""

    def test_valid_usage_path(self):
        """Test que path válido pasa la validación."""
        valid_paths = [
            "conversation/uuid/audio/file.mp3",
            "conversation/123/image/photo.jpg",
            "conversation/abc-123/pdf/doc.pdf",
        ]
        for path in valid_paths:
            validate_usage_path(path)

    def test_empty_usage(self):
        """Test que usage vacío lanza error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_usage_path("")
        assert "no puede estar vacío" in str(exc_info.value)

    def test_usage_starts_with_slash(self):
        """Test que usage que empieza con / lanza error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_usage_path("/conversation/uuid/audio/file.mp3")
        assert "no debe empezar con '/'" in str(exc_info.value)

    def test_usage_contains_path_traversal(self):
        """Test que usage con .. lanza error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_usage_path("conversation/../audio/file.mp3")
        assert "no puede contener '..'" in str(exc_info.value)

    def test_usage_no_separator(self):
        """Test que usage sin separador lanza error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_usage_path("file.mp3")
        assert "debe contener al menos un separador" in str(exc_info.value)

    def test_usage_contains_spaces(self):
        """Test que usage con espacios lanza error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_usage_path("conversation/uuid/audio/file name.mp3")
        assert "no puede contener espacios" in str(exc_info.value)


class TestUsageConsistencyValidator:
    """Tests para validación de consistencia entre usage, file_name y category."""

    def test_consistent_usage(self):
        """Test que usage consistente pasa la validación."""
        validate_usage_consistency(
            "conversation/uuid/audio/file.mp3",
            "file.mp3",
            "audio",
        )

    def test_usage_filename_mismatch(self):
        """Test que usage con nombre de archivo diferente lanza error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_usage_consistency(
                "conversation/uuid/audio/file.mp3",
                "other.mp3",
                "audio",
            )
        assert "debe coincidir" in str(exc_info.value)

    def test_usage_missing_category(self):
        """Test que usage sin categoría en el path lanza error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_usage_consistency(
                "conversation/uuid/file.mp3",
                "file.mp3",
                "audio",
            )
        assert "debe contener la categoría" in str(exc_info.value)
