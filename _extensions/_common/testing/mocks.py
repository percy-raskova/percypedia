"""Mock factories for Sphinx extension testing.

Provides factory functions to create properly configured mock objects
for testing Sphinx directives, roles, and extensions.
"""

from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

__all__ = [
    'make_mock_app',
    'make_mock_directive',
    'make_mock_env',
    'make_mock_inliner',
]


def make_mock_app(
    srcdir: Path | str = '/tmp/src',
    outdir: Path | str | None = None,
    config_values: dict[str, Any] | None = None,
) -> MagicMock:
    """Create a mock Sphinx application for testing.

    Args:
        srcdir: Source directory path (default: '/tmp/src')
        outdir: Output directory path (default: srcdir/_build/html)
        config_values: Additional config values to set

    Returns:
        MagicMock configured as a Sphinx application

    Example:
        >>> app = make_mock_app('/docs/src', config_values={'my_option': True})
        >>> app.config.my_option
        True
    """
    srcdir = Path(srcdir)
    if outdir is None:
        outdir = srcdir / '_build' / 'html'

    app = MagicMock()
    app.srcdir = str(srcdir)
    app.outdir = str(outdir)
    app.config = MagicMock()
    app.config.exclude_patterns = []
    app.connect = MagicMock()
    app.add_config_value = MagicMock()
    app.add_directive = MagicMock()
    app.add_role = MagicMock()
    app.add_node = MagicMock()

    if config_values:
        for key, value in config_values.items():
            setattr(app.config, key, value)

    return app


def make_mock_env(
    docname: str = 'test-doc',
    attrs: dict[str, Any] | None = None,
) -> SimpleNamespace:
    """Create a mock Sphinx environment using SimpleNamespace.

    Uses SimpleNamespace instead of MagicMock because MagicMock auto-creates
    child mocks for any attribute access, which breaks getattr() with defaults.

    Args:
        docname: Current document name (default: 'test-doc')
        attrs: Additional attributes to set on env

    Returns:
        SimpleNamespace configured as a build environment

    Example:
        >>> env = make_mock_env('theory/marxism', {'my_data': []})
        >>> env.docname
        'theory/marxism'
    """
    env_attrs = {'docname': docname}
    if attrs:
        env_attrs.update(attrs)
    return SimpleNamespace(**env_attrs)


def make_mock_directive(
    directive_class: type,
    arguments: list[str] | None = None,
    content: list[str] | None = None,
    options: dict[str, Any] | None = None,
    docname: str = 'test-doc',
    lineno: int = 10,
    content_offset: int = 0,
    env_attrs: dict[str, Any] | None = None,
) -> MagicMock:
    """Create a mock directive instance for testing.

    Args:
        directive_class: The directive class to mock (used for spec)
        arguments: List of directive arguments
        content: List of content lines
        options: Dict of directive options
        docname: Document name for env.docname
        lineno: Line number in source
        content_offset: Content offset for nested parsing
        env_attrs: Additional attributes for the env

    Returns:
        MagicMock configured as a directive instance

    Example:
        >>> from my_extension import MyDirective
        >>> d = make_mock_directive(MyDirective, ['arg1'], options={'opt': 'val'})
        >>> d.arguments[0]
        'arg1'
    """
    directive = MagicMock(spec=directive_class)
    directive.arguments = arguments or []
    directive.content = content or []
    directive.content_offset = content_offset
    directive.lineno = lineno
    directive.options = options or {}

    # Build environment attributes
    all_env_attrs = {'docname': docname}
    if env_attrs:
        all_env_attrs.update(env_attrs)

    # Use SimpleNamespace for predictable getattr behavior
    directive.env = SimpleNamespace(**all_env_attrs)

    # Mock state for nested parsing
    directive.state = MagicMock()

    return directive


def make_mock_inliner(
    env_attrs: dict[str, Any] | None = None,
) -> MagicMock:
    """Create a mock inliner for role testing.

    Args:
        env_attrs: Attributes to set on the environment

    Returns:
        MagicMock configured as an inliner

    Example:
        >>> inliner = make_mock_inliner({'my_data': {'key': 'value'}})
        >>> inliner.document.settings.env.my_data
        {'key': 'value'}
    """
    inliner = MagicMock()
    inliner.document = MagicMock()
    inliner.document.settings = MagicMock()

    # Use SimpleNamespace for env
    all_attrs = env_attrs or {}
    inliner.document.settings.env = SimpleNamespace(**all_attrs)

    inliner.reporter = MagicMock()
    inliner.reporter.warning = MagicMock(return_value=MagicMock())

    return inliner
