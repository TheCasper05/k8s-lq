from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PromptKey:
    """
    Unique identifier of a prompt within the catalog.
    `category` groups prompts (e.g., 'corrections', 'scenarios').
    `version` is the version of the prompt (e.g., 'v1', 'v2'). Defaults to 'v1'.
    `name` is the prompt id inside the category (e.g., 'grammar', 'prompt_chat').
    """

    category: str
    name: str
    version: str = "v1"


@dataclass(frozen=True, slots=True)
class PromptDefinition:
    """
    Canonical prompt representation used by repositories and the manager.
    `content` holds the raw template text (with placeholders like {var}) or
    a dict for structured prompts (e.g., response schemas).
    """

    key: PromptKey
    content: str | dict
    # Future-friendly: locale, version, tags, metadata, etc.


@dataclass(slots=True)
class TenantContext:
    """
    Placeholder for future multi-tenant support (institution/workspace).
    v1 does not use it, but we keep the type for forward-compatibility.
    """

    tenant_id: str | None = None
