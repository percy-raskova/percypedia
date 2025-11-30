"""Tests for directive utility functions."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from docutils import nodes

from _common.directive_utils import (
    build_content_section,
    build_header_node,
    ensure_env_storage,
)


class TestBuildHeaderNode:
    """Tests for build_header_node function."""

    def test_basic_header_structure(self):
        """Creates header with title, meta, and badge."""
        header = build_header_node(
            css_prefix='ai-chat',
            title='My Chat',
            options={'date': '2024-01-01'},
            badge_text='AI Chat',
        )

        assert isinstance(header, nodes.container)
        assert 'ai-chat-header' in header['classes']

    def test_includes_title(self):
        """Header includes title when provided."""
        header = build_header_node(
            css_prefix='test',
            title='Test Title',
            options={},
            badge_text='Badge',
        )

        # Find title paragraph
        title_para = None
        for child in header.children:
            if isinstance(child, nodes.paragraph) and 'test-title' in child.get('classes', []):
                title_para = child
                break

        assert title_para is not None

    def test_excludes_title_when_disabled(self):
        """Header excludes title when include_title=False."""
        header = build_header_node(
            css_prefix='test',
            title='Should Not Appear',
            options={},
            badge_text='Badge',
            include_title=False,
        )

        # Should not find title paragraph
        for child in header.children:
            if isinstance(child, nodes.paragraph):
                classes = child.get('classes', [])
                assert 'test-title' not in classes

    def test_metadata_line_from_options(self):
        """Header includes metadata from options."""
        header = build_header_node(
            css_prefix='ex',
            title='Title',
            options={'date': '2024-01-01', 'model': 'claude-sonnet'},
            badge_text='Badge',
            meta_keys=('date', 'model', 'source'),
        )

        # Find meta paragraph
        meta_para = None
        for child in header.children:
            if isinstance(child, nodes.paragraph) and 'ex-meta' in child.get('classes', []):
                meta_para = child
                break

        assert meta_para is not None

    def test_skips_empty_meta_values(self):
        """Empty meta values are not included."""
        header = build_header_node(
            css_prefix='ex',
            title='Title',
            options={'date': '2024-01-01', 'model': ''},  # model is empty
            badge_text='Badge',
            meta_keys=('date', 'model'),
        )

        # Meta should only have date
        meta_para = None
        for child in header.children:
            if isinstance(child, nodes.paragraph) and 'ex-meta' in child.get('classes', []):
                meta_para = child
                break

        # The meta line exists with just date
        assert meta_para is not None

    def test_no_meta_paragraph_when_all_empty(self):
        """No meta paragraph created when all values missing."""
        header = build_header_node(
            css_prefix='ex',
            title='Title',
            options={},  # No meta options
            badge_text='Badge',
            meta_keys=('date', 'model'),
        )

        # Should not find meta paragraph
        for child in header.children:
            if isinstance(child, nodes.paragraph):
                classes = child.get('classes', [])
                assert 'ex-meta' not in classes

    def test_includes_context_when_provided(self):
        """Header includes context line when context_key specified."""
        header = build_header_node(
            css_prefix='msg',
            title='Title',
            options={'context': 'Discussion about X'},
            badge_text='Badge',
            context_key='context',
        )

        # Find context paragraph
        context_para = None
        for child in header.children:
            if isinstance(child, nodes.paragraph) and 'msg-context' in child.get('classes', []):
                context_para = child
                break

        assert context_para is not None

    def test_always_includes_badge(self):
        """Header always includes badge."""
        header = build_header_node(
            css_prefix='test',
            title='Title',
            options={},
            badge_text='My Badge',
        )

        # Find badge inline
        badge = None
        for child in header.children:
            if isinstance(child, nodes.inline) and 'ai-badge' in child.get('classes', []):
                badge = child
                break

        assert badge is not None


class TestBuildContentSection:
    """Tests for build_content_section function."""

    def test_creates_container_with_class(self):
        """Creates container with specified CSS class."""
        mock_state = MagicMock()
        mock_state.nested_parse = MagicMock()

        section = build_content_section(
            content_text='Test content',
            css_class='ai-question',
            label='Question',
            state=mock_state,
            content_offset=0,
        )

        assert 'ai-question' in section['classes']

    def test_includes_label(self):
        """Section includes bold label."""
        mock_state = MagicMock()
        mock_state.nested_parse = MagicMock()

        section = build_content_section(
            content_text='Content',
            css_class='test',
            label='My Label',
            state=mock_state,
            content_offset=0,
        )

        # Find label paragraph
        label_para = None
        for child in section.children:
            if isinstance(child, nodes.paragraph) and 'test-label' in child.get('classes', []):
                label_para = child
                break

        assert label_para is not None

    def test_calls_nested_parse(self):
        """Calls state.nested_parse with content."""
        mock_state = MagicMock()
        mock_state.nested_parse = MagicMock()

        build_content_section(
            content_text='Line 1\nLine 2',
            css_class='test',
            label='Label',
            state=mock_state,
            content_offset=5,
        )

        mock_state.nested_parse.assert_called_once()
        call_args = mock_state.nested_parse.call_args
        assert call_args[0][0] == ['Line 1', 'Line 2']  # Content lines
        assert call_args[0][1] == 5  # Content offset

    def test_custom_node_class(self):
        """Uses custom node class when specified."""
        mock_state = MagicMock()
        mock_state.nested_parse = MagicMock()

        class CustomNode(nodes.container):
            pass

        section = build_content_section(
            content_text='Content',
            css_class='test',
            label='Label',
            state=mock_state,
            content_offset=0,
            node_class=CustomNode,
        )

        assert isinstance(section, CustomNode)


class TestEnsureEnvStorage:
    """Tests for ensure_env_storage function."""

    def test_creates_dict_when_missing(self):
        """Creates dict when attribute missing."""
        env = SimpleNamespace()

        storage = ensure_env_storage(env, 'my_storage')

        assert hasattr(env, 'my_storage')
        assert isinstance(storage, dict)
        assert storage is env.my_storage

    def test_returns_existing_storage(self):
        """Returns existing storage if present."""
        env = SimpleNamespace(my_storage={'existing': 'data'})

        storage = ensure_env_storage(env, 'my_storage')

        assert storage == {'existing': 'data'}
        assert storage is env.my_storage

    def test_custom_factory(self):
        """Uses custom factory function."""
        env = SimpleNamespace()

        storage = ensure_env_storage(env, 'my_list', factory=list)

        assert isinstance(storage, list)

    def test_factory_with_callable(self):
        """Works with any callable as factory."""
        env = SimpleNamespace()

        def my_factory():
            return {'default': 'value'}

        storage = ensure_env_storage(env, 'custom', factory=my_factory)

        assert storage == {'default': 'value'}

    def test_does_not_overwrite_existing(self):
        """Does not overwrite existing non-None value."""
        env = SimpleNamespace(my_storage=['a', 'b'])

        storage = ensure_env_storage(env, 'my_storage', factory=dict)

        # Should return existing list, not create new dict
        assert storage == ['a', 'b']
        assert isinstance(storage, list)
