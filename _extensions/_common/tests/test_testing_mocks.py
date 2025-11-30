"""Tests for testing mock utilities."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from _common.testing import (
    make_mock_app,
    make_mock_directive,
    make_mock_env,
    make_mock_inliner,
)


class TestMakeMockApp:
    """Tests for make_mock_app factory."""

    def test_basic_app_structure(self):
        """Creates app with essential attributes."""
        app = make_mock_app()

        assert app.srcdir is not None
        assert app.outdir is not None
        assert app.config is not None

    def test_custom_srcdir(self):
        """Respects custom srcdir."""
        app = make_mock_app(srcdir='/custom/path')

        assert app.srcdir == '/custom/path'

    def test_default_outdir(self):
        """Creates default outdir based on srcdir."""
        app = make_mock_app(srcdir='/docs/src')

        assert '_build' in app.outdir
        assert 'html' in app.outdir

    def test_custom_outdir(self):
        """Respects custom outdir."""
        app = make_mock_app(outdir='/custom/output')

        assert app.outdir == '/custom/output'

    def test_config_values(self):
        """Sets config values correctly."""
        app = make_mock_app(config_values={'my_option': True, 'limit': 42})

        assert app.config.my_option is True
        assert app.config.limit == 42

    def test_has_mock_methods(self):
        """App has common Sphinx methods mocked."""
        app = make_mock_app()

        assert callable(app.connect)
        assert callable(app.add_config_value)
        assert callable(app.add_directive)
        assert callable(app.add_role)
        assert callable(app.add_node)


class TestMakeMockEnv:
    """Tests for make_mock_env factory."""

    def test_basic_env_structure(self):
        """Creates env with docname."""
        env = make_mock_env()

        assert env.docname == 'test-doc'

    def test_custom_docname(self):
        """Respects custom docname."""
        env = make_mock_env(docname='theory/marxism')

        assert env.docname == 'theory/marxism'

    def test_additional_attrs(self):
        """Sets additional attributes."""
        env = make_mock_env(attrs={'my_data': [], 'counter': 0})

        assert env.my_data == []
        assert env.counter == 0

    def test_is_simple_namespace(self):
        """Returns SimpleNamespace for predictable getattr behavior."""
        env = make_mock_env()

        assert isinstance(env, SimpleNamespace)

    def test_getattr_with_default_works(self):
        """getattr with default works (unlike MagicMock)."""
        env = make_mock_env()

        # This would fail with MagicMock - it would return a MagicMock
        result = getattr(env, 'nonexistent', None)

        assert result is None


class TestMakeMockDirective:
    """Tests for make_mock_directive factory."""

    class DummyDirective:
        """Dummy directive class for testing."""
        pass

    def test_basic_directive_structure(self):
        """Creates directive with essential attributes."""
        directive = make_mock_directive(self.DummyDirective)

        assert directive.arguments == []
        assert directive.content == []
        assert directive.options == {}
        assert directive.lineno == 10

    def test_custom_arguments(self):
        """Respects custom arguments."""
        directive = make_mock_directive(
            self.DummyDirective,
            arguments=['arg1', 'arg2'],
        )

        assert directive.arguments == ['arg1', 'arg2']

    def test_custom_content(self):
        """Respects custom content."""
        directive = make_mock_directive(
            self.DummyDirective,
            content=['line 1', 'line 2'],
        )

        assert directive.content == ['line 1', 'line 2']

    def test_custom_options(self):
        """Respects custom options."""
        directive = make_mock_directive(
            self.DummyDirective,
            options={'date': '2024-01-01', 'class': ['custom']},
        )

        assert directive.options['date'] == '2024-01-01'
        assert directive.options['class'] == ['custom']

    def test_env_has_docname(self):
        """Directive env has docname."""
        directive = make_mock_directive(self.DummyDirective, docname='my-doc')

        assert directive.env.docname == 'my-doc'

    def test_env_has_custom_attrs(self):
        """Directive env has custom attributes."""
        directive = make_mock_directive(
            self.DummyDirective,
            env_attrs={'my_data': {'key': 'value'}},
        )

        assert directive.env.my_data == {'key': 'value'}

    def test_env_is_simple_namespace(self):
        """Directive env is SimpleNamespace."""
        directive = make_mock_directive(self.DummyDirective)

        assert isinstance(directive.env, SimpleNamespace)

    def test_has_mock_state(self):
        """Directive has mock state for nested_parse."""
        directive = make_mock_directive(self.DummyDirective)

        assert directive.state is not None
        assert callable(directive.state.nested_parse)


class TestMakeMockInliner:
    """Tests for make_mock_inliner factory."""

    def test_basic_inliner_structure(self):
        """Creates inliner with essential structure."""
        inliner = make_mock_inliner()

        assert inliner.document is not None
        assert inliner.document.settings is not None
        assert inliner.document.settings.env is not None

    def test_env_attributes(self):
        """Sets env attributes correctly."""
        inliner = make_mock_inliner(env_attrs={'my_data': ['a', 'b']})

        assert inliner.document.settings.env.my_data == ['a', 'b']

    def test_has_reporter(self):
        """Inliner has reporter for warnings."""
        inliner = make_mock_inliner()

        assert inliner.reporter is not None
        assert callable(inliner.reporter.warning)

    def test_env_is_simple_namespace(self):
        """Inliner env is SimpleNamespace."""
        inliner = make_mock_inliner()

        assert isinstance(inliner.document.settings.env, SimpleNamespace)
