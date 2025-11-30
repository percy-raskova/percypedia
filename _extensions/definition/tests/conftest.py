"""Shared fixtures for definition directive tests."""

import pytest
from pathlib import Path
from textwrap import dedent


@pytest.fixture
def tmp_srcdir(tmp_path: Path) -> Path:
    """Create a minimal Sphinx source directory."""
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    # Create minimal conf.py
    conf_py = srcdir / "conf.py"
    conf_py.write_text(dedent("""
        extensions = [
            'myst_parser',
            'sphinx_design',
            'definition',
        ]
        exclude_patterns = ['_build']
    """))

    # Create minimal index
    index_md = srcdir / "index.md"
    index_md.write_text(dedent("""
        # Test Site

        ```{toctree}
        :maxdepth: 2
        ```
    """))

    return srcdir


@pytest.fixture
def simple_definition_content() -> str:
    """A simple definition directive."""
    return dedent("""
        # Test Article

        ```{definition} Labor Aristocracy
        The privileged stratum of the proletariat that benefits from
        imperialist super-profits.
        ```
    """)


@pytest.fixture
def definition_with_markdown() -> str:
    """A definition with markdown formatting in the body."""
    return dedent("""
        # Test Article

        ```{definition} Dialectical Materialism
        A philosophical framework combining:

        - **Dialectics**: Analysis through contradiction
        - **Materialism**: Material conditions as primary

        See also: *historical materialism*
        ```
    """)


@pytest.fixture
def multiple_definitions_content() -> str:
    """Content with multiple definition directives."""
    return dedent("""
        # Theory Article

        ```{definition} Term One
        Definition of term one.
        ```

        Some intervening text.

        ```{definition} Term Two
        Definition of term two.
        ```

        ```{definition} Term Three
        Definition of term three.
        ```
    """)


@pytest.fixture
def duplicate_definition_content() -> str:
    """Content that would create a duplicate definition."""
    return dedent("""
        # Article One

        ```{definition} Labor Aristocracy
        First definition.
        ```
    """)


@pytest.fixture
def empty_definition_content() -> str:
    """A definition directive with no body content."""
    return dedent("""
        # Test Article

        ```{definition} Empty Term
        ```
    """)


@pytest.fixture
def definition_no_term_content() -> str:
    """A definition directive with no term name."""
    return dedent("""
        # Test Article

        ```{definition}
        Some content but no term name.
        ```
    """)
