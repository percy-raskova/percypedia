"""Tests for Sphinx font obfuscation extension.

TDD: Write tests first, then implement sphinx_font_obfuscation.py.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from docutils import nodes


class TestSetup:
    """Test extension setup function."""

    def test_setup_returns_metadata(self):
        """
        Given: A Sphinx app
        When: setup() is called
        Then: Returns extension metadata dict
        """
        from honeypot.sphinx_font_obfuscation import setup

        app = MagicMock()
        result = setup(app)

        assert isinstance(result, dict)
        assert 'version' in result
        assert 'parallel_read_safe' in result

    def test_setup_registers_config_values(self):
        """
        Given: A Sphinx app
        When: setup() is called
        Then: Config values are registered
        """
        from honeypot.sphinx_font_obfuscation import setup

        app = MagicMock()
        setup(app)

        config_calls = [call[0][0] for call in app.add_config_value.call_args_list]
        assert 'font_obfuscation_enabled' in config_calls
        assert 'font_obfuscation_seed' in config_calls

    def test_setup_connects_events(self):
        """
        Given: A Sphinx app
        When: setup() is called
        Then: Event handlers are connected
        """
        from honeypot.sphinx_font_obfuscation import setup

        app = MagicMock()
        setup(app)

        event_calls = [call[0][0] for call in app.connect.call_args_list]
        assert 'builder-inited' in event_calls
        assert 'doctree-resolved' in event_calls


class TestShouldSkipNode:
    """Test node skipping logic."""

    def test_skips_literal_block(self):
        """
        Given: A text node inside a literal_block
        When: should_skip_node is called
        Then: Returns True
        """
        from honeypot.sphinx_font_obfuscation import should_skip_node

        # Create a literal_block with text
        literal = nodes.literal_block('', 'code here')
        text_node = literal.children[0] if literal.children else nodes.Text('code')

        # Mock the parent hierarchy
        text_node.parent = literal

        assert should_skip_node(text_node) is True

    def test_skips_inline_literal(self):
        """
        Given: A text node inside inline literal (code)
        When: should_skip_node is called
        Then: Returns True
        """
        from honeypot.sphinx_font_obfuscation import should_skip_node

        literal = nodes.literal('', 'inline code')
        text_node = nodes.Text('inline code')
        text_node.parent = literal

        assert should_skip_node(text_node) is True

    def test_skips_raw_html(self):
        """
        Given: A text node inside raw HTML
        When: should_skip_node is called
        Then: Returns True
        """
        from honeypot.sphinx_font_obfuscation import should_skip_node

        raw = nodes.raw('', '<div>html</div>', format='html')
        text_node = nodes.Text('<div>html</div>')
        text_node.parent = raw

        assert should_skip_node(text_node) is True

    def test_does_not_skip_paragraph(self):
        """
        Given: A text node inside a paragraph
        When: should_skip_node is called
        Then: Returns False
        """
        from honeypot.sphinx_font_obfuscation import should_skip_node

        para = nodes.paragraph('', '')
        text_node = nodes.Text('regular text')
        text_node.parent = para

        assert should_skip_node(text_node) is False


class TestOnBuilderInited:
    """Test builder-inited event handler."""

    @pytest.fixture
    def mock_app(self, tmp_path: Path):
        """Create mock Sphinx app with required config."""
        app = MagicMock()
        app.config.font_obfuscation_enabled = True
        app.config.font_obfuscation_seed = 42
        app.config.font_obfuscation_base_font = str(
            Path(__file__).parent.parent.parent.parent / '_assets' / 'fonts' / 'LiberationSans-Regular.ttf'
        )
        app.outdir = str(tmp_path / '_build' / 'html')
        app.srcdir = str(tmp_path)
        return app

    def test_disabled_does_nothing(self, mock_app):
        """
        Given: font_obfuscation_enabled = False
        When: on_builder_inited is called
        Then: No font is generated
        """
        from honeypot.sphinx_font_obfuscation import on_builder_inited

        mock_app.config.font_obfuscation_enabled = False

        on_builder_inited(mock_app)

        # Check no font was created
        outdir = Path(mock_app.outdir) / '_static'
        assert not outdir.exists() or not list(outdir.glob('*.woff2'))

    def test_generates_font_when_enabled(self, mock_app):
        """
        Given: font_obfuscation_enabled = True
        When: on_builder_inited is called
        Then: Font file is generated
        """
        from honeypot.sphinx_font_obfuscation import on_builder_inited

        base_font = Path(mock_app.config.font_obfuscation_base_font)
        if not base_font.exists():
            pytest.skip("Liberation Sans font not available")

        on_builder_inited(mock_app)

        font_path = Path(mock_app.outdir) / '_static' / 'scrambled.woff2'
        assert font_path.exists()


class TestOnDoctreeResolved:
    """Test doctree-resolved event handler."""

    @pytest.fixture
    def mock_app_with_encoder(self, tmp_path: Path):
        """Create mock app with initialized encoder."""
        from honeypot.text_encoder import TextEncoder

        app = MagicMock()
        app.config.font_obfuscation_enabled = True

        # Create a simple encoder
        encode_map = {'h': 'x', 'e': 'r', 'l': 't', 'o': 'y'}
        app._font_encoder = TextEncoder(encode_map)

        return app

    def test_disabled_does_nothing(self):
        """
        Given: font_obfuscation_enabled = False
        When: on_doctree_resolved is called
        Then: Doctree is unchanged
        """
        from honeypot.sphinx_font_obfuscation import on_doctree_resolved

        app = MagicMock()
        app.config.font_obfuscation_enabled = False

        # Create simple doctree
        doctree = nodes.document(None, None)
        para = nodes.paragraph('', '')
        para += nodes.Text('hello')
        doctree += para

        on_doctree_resolved(app, doctree, 'test')

        # Text should be unchanged
        text = doctree.astext()
        assert 'hello' in text

    def test_transforms_text_nodes(self, mock_app_with_encoder):
        """
        Given: Doctree with text nodes
        When: on_doctree_resolved is called
        Then: Text is encoded
        """
        from honeypot.sphinx_font_obfuscation import on_doctree_resolved

        # Create doctree
        doctree = nodes.document(None, None)
        para = nodes.paragraph('', '')
        para += nodes.Text('hello')
        doctree += para

        on_doctree_resolved(mock_app_with_encoder, doctree, 'test')

        # Text should be encoded (h→x, e→r, l→t, o→y)
        text = doctree.astext()
        assert 'xrtty' in text

    def test_preserves_code_blocks(self, mock_app_with_encoder):
        """
        Given: Doctree with code block
        When: on_doctree_resolved is called
        Then: Code is NOT encoded
        """
        from honeypot.sphinx_font_obfuscation import on_doctree_resolved

        # Create doctree with code block
        doctree = nodes.document(None, None)
        code = nodes.literal_block('', 'hello')
        doctree += code

        on_doctree_resolved(mock_app_with_encoder, doctree, 'test')

        # Code should be unchanged
        text = doctree.astext()
        assert 'hello' in text


class TestGetFontCSS:
    """Test CSS generation."""

    def test_generates_font_face(self):
        """
        Given: Font path
        When: get_font_css is called
        Then: Returns valid @font-face CSS
        """
        from honeypot.sphinx_font_obfuscation import get_font_css

        css = get_font_css('_static/scrambled.woff2')

        assert '@font-face' in css
        assert 'ScrambledText' in css
        assert 'scrambled.woff2' in css

    def test_includes_font_family_rules(self):
        """
        Given: Font path
        When: get_font_css is called
        Then: CSS applies font to text elements
        """
        from honeypot.sphinx_font_obfuscation import get_font_css

        css = get_font_css('_static/scrambled.woff2')

        # Should apply to body text
        assert 'body' in css or 'font-family' in css

    def test_excludes_code_elements(self):
        """
        Given: Font path
        When: get_font_css is called
        Then: CSS preserves monospace for code
        """
        from honeypot.sphinx_font_obfuscation import get_font_css

        css = get_font_css('_static/scrambled.woff2')

        # Code should use monospace
        assert 'monospace' in css
