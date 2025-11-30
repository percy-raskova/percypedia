"""Base collector class for Sphinx extensions.

Provides a standard interface for collecting data during Sphinx builds,
with support for parallel builds via env-merge-info.

This is the single source of truth for collector patterns.
All extensions should extend BaseCollector.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar, Generic, TypeVar

__all__ = [
    'BaseCollector',
    'CollectorEntry',
]

T = TypeVar('T')


@dataclass
class CollectorEntry:
    """Base class for entries with source location tracking.

    Subclasses should extend this with additional fields.
    """
    docname: str
    lineno: int
    anchor: str

    @property
    def location(self) -> str:
        """Human-readable location string (docname:lineno)."""
        return f"{self.docname}:{self.lineno}"


class BaseCollector(ABC, Generic[T]):
    """Base class for environment-based data collectors.

    Features:
    - Automatic env attribute management via get_or_create()
    - env-merge-info support for parallel builds via merge()
    - Standard __len__ and __contains__ implementations

    Subclasses must:
    1. Define class attribute `env_attr` (str) - the attribute name on env
    2. Implement `merge()` for parallel build support

    Example:
        class MyCollector(BaseCollector[MyEntry]):
            env_attr = 'my_extension_collector'

            def __init__(self):
                self._entries: dict[str, MyEntry] = {}

            def merge(self, other: 'MyCollector') -> None:
                self._entries.update(other._entries)
    """

    env_attr: ClassVar[str]  # Subclass must define

    @classmethod
    def get_or_create(cls, env: Any, **init_kwargs: Any) -> 'BaseCollector[T]':
        """Get existing collector from env or create a new one.

        Args:
            env: Sphinx build environment
            **init_kwargs: Arguments to pass to __init__ if creating new

        Returns:
            The collector instance attached to env
        """
        if not hasattr(env, cls.env_attr) or getattr(env, cls.env_attr) is None:
            setattr(env, cls.env_attr, cls(**init_kwargs))
        return getattr(env, cls.env_attr)

    @classmethod
    def reset(cls, env: Any) -> None:
        """Reset the collector on environment (for testing or new builds).

        Args:
            env: Sphinx build environment
        """
        setattr(env, cls.env_attr, None)

    @abstractmethod
    def merge(self, other: 'BaseCollector[T]') -> None:
        """Merge entries from another collector (for parallel builds).

        This is called during env-merge-info to combine collectors from
        parallel build processes.

        Args:
            other: Another collector instance to merge from
        """

    def __len__(self) -> int:
        """Return number of entries. Subclasses should override if needed."""
        if hasattr(self, '_entries'):
            return len(self._entries)
        if hasattr(self, 'entries'):
            return len(self.entries)
        raise NotImplementedError("Subclass must implement __len__ or have _entries/entries attr")

    def __contains__(self, key: str) -> bool:
        """Check if key exists. Subclasses should override if needed."""
        if hasattr(self, '_entries'):
            return key in self._entries
        if hasattr(self, 'entries'):
            return key in self.entries
        raise NotImplementedError("Subclass must implement __contains__ or have _entries/entries attr")


def make_merge_handler(collector_class: type[BaseCollector]) -> callable:
    """Create an env-merge-info handler for a collector class.

    Usage in extension setup():
        app.connect('env-merge-info', make_merge_handler(MyCollector))

    Args:
        collector_class: The BaseCollector subclass

    Returns:
        A handler function for the env-merge-info event
    """
    def merge_handler(
        _app: Any,
        env: Any,
        _docnames: list[str],
        other_env: Any,
    ) -> None:
        """Merge collector from parallel build process."""
        other_collector = getattr(other_env, collector_class.env_attr, None)
        if other_collector is not None:
            collector = collector_class.get_or_create(env)
            collector.merge(other_collector)

    return merge_handler
