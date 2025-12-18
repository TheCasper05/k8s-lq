"""Adaptadores de storage."""

from src.infrastructure.adapters.storage.boto3_storage_adapter import Boto3StorageAdapter
from src.infrastructure.adapters.storage.factory import StorageProviderFactory

__all__ = ["Boto3StorageAdapter", "StorageProviderFactory"]
