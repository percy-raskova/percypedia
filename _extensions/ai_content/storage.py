"""Environment storage management for AI content.

Provides utilities for managing AI content data in the Sphinx environment.
"""

from typing import Any

__all__ = [
    'AIContentStorage',
]


class AIContentStorage:
    """Manages AI content storage in Sphinx environment.

    Provides a unified interface for storing and retrieving AI content
    (chats, exchanges, messages) from the Sphinx build environment.
    """

    STORAGE_ATTRS = {
        'chat': 'ai_content_chats',
        'exchange': 'ai_content_exchanges',
        'message': 'ai_content_messages',
    }

    @classmethod
    def ensure_storage(cls, env: Any, content_type: str) -> dict:
        """Ensure storage dict exists and return it.

        Args:
            env: Sphinx build environment
            content_type: Type of content ('chat', 'exchange', 'message')

        Returns:
            The storage dict for this content type
        """
        attr = cls.STORAGE_ATTRS[content_type]
        if not hasattr(env, attr):
            setattr(env, attr, {})
        return getattr(env, attr)

    @classmethod
    def store_content(
        cls,
        env: Any,
        content_type: str,
        name: str,
        data: dict[str, Any],
    ) -> None:
        """Store content data in environment.

        Args:
            env: Sphinx build environment
            content_type: Type of content ('chat', 'exchange', 'message')
            name: Unique name/key for this content
            data: Content data to store
        """
        storage = cls.ensure_storage(env, content_type)
        storage[name] = data

    @classmethod
    def get_all(cls, env: Any, content_type: str) -> dict:
        """Get all stored content of a type.

        Args:
            env: Sphinx build environment
            content_type: Type of content ('chat', 'exchange', 'message')

        Returns:
            Dict of all content of this type
        """
        return cls.ensure_storage(env, content_type)

    @classmethod
    def get(cls, env: Any, content_type: str, name: str) -> dict | None:
        """Get specific content by name.

        Args:
            env: Sphinx build environment
            content_type: Type of content
            name: Content name to retrieve

        Returns:
            Content data dict or None if not found
        """
        storage = cls.ensure_storage(env, content_type)
        return storage.get(name)
