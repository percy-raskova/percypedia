"""Tests for missing_refs extension.

TDD RED phase: Define expected behavior for capturing missing references.
Run with: mise run test
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock


class TestMissingRefsCollection:
    """Tests for collecting missing references during build."""

    def test_records_missing_doc_reference(self):
        from missing_refs import MissingRefsCollector

        collector = MissingRefsCollector()
        collector.record_missing('theory/future-topic', 'index')

        assert 'theory/future-topic' in collector.missing
        assert 'index' in collector.missing['theory/future-topic']['referenced_by']

    def test_tracks_multiple_references_to_same_target(self):
        from missing_refs import MissingRefsCollector

        collector = MissingRefsCollector()
        collector.record_missing('theory/future-topic', 'index')
        collector.record_missing('theory/future-topic', 'docs/taxonomy')

        refs = collector.missing['theory/future-topic']['referenced_by']
        assert 'index' in refs
        assert 'docs/taxonomy' in refs

    def test_tracks_multiple_missing_targets(self):
        from missing_refs import MissingRefsCollector

        collector = MissingRefsCollector()
        collector.record_missing('theory/topic-a', 'index')
        collector.record_missing('theory/topic-b', 'index')

        assert 'theory/topic-a' in collector.missing
        assert 'theory/topic-b' in collector.missing

    def test_no_duplicate_referrers(self):
        from missing_refs import MissingRefsCollector

        collector = MissingRefsCollector()
        collector.record_missing('theory/topic', 'index')
        collector.record_missing('theory/topic', 'index')  # Same reference twice

        refs = collector.missing['theory/topic']['referenced_by']
        assert refs.count('index') == 1

    def test_extracts_category_from_path(self):
        from missing_refs import MissingRefsCollector

        collector = MissingRefsCollector()
        collector.record_missing('theory/labor-aristocracy', 'index')
        collector.record_missing('concepts/dialectics', 'index')
        collector.record_missing('top-level-doc', 'index')

        assert collector.missing['theory/labor-aristocracy']['category'] == 'theory'
        assert collector.missing['concepts/dialectics']['category'] == 'concepts'
        assert collector.missing['top-level-doc']['category'] is None

    def test_handles_unicode_target_paths(self):
        """Should handle unicode characters in target paths."""
        from missing_refs import MissingRefsCollector

        collector = MissingRefsCollector()
        collector.record_missing('theory/teoría-del-valor', 'index')
        collector.record_missing('concepts/dialéctica', 'index')

        assert 'theory/teoría-del-valor' in collector.missing
        assert 'concepts/dialéctica' in collector.missing
        assert collector.missing['theory/teoría-del-valor']['category'] == 'theory'

    def test_handles_unicode_referrer_paths(self):
        """Should handle unicode characters in referrer document names."""
        from missing_refs import MissingRefsCollector

        collector = MissingRefsCollector()
        collector.record_missing('future/topic', 'teoría/introducción')

        refs = collector.missing['future/topic']['referenced_by']
        assert 'teoría/introducción' in refs

    def test_handles_special_characters_in_paths(self):
        """Should handle special characters like hyphens and underscores."""
        from missing_refs import MissingRefsCollector

        collector = MissingRefsCollector()
        collector.record_missing('theory/class_struggle-2024', 'index')
        collector.record_missing('concepts/labor-power_definition', 'docs/intro')

        assert 'theory/class_struggle-2024' in collector.missing
        assert 'concepts/labor-power_definition' in collector.missing


class TestJsonOutput:
    """Tests for JSON file output."""

    def test_to_json_returns_valid_structure(self):
        from missing_refs import MissingRefsCollector

        collector = MissingRefsCollector()
        collector.record_missing('theory/topic-a', 'index')
        collector.record_missing('theory/topic-b', 'docs/intro')

        data = collector.to_dict()

        assert 'missing_documents' in data
        assert 'generated_at' in data
        assert 'count' in data
        assert data['count'] == 2

    def test_writes_json_file(self, tmp_path):
        from missing_refs import MissingRefsCollector

        collector = MissingRefsCollector()
        collector.record_missing('theory/future', 'index')

        output_path = tmp_path / 'missing_refs.json'
        collector.write_json(output_path)

        assert output_path.exists()
        data = json.loads(output_path.read_text())
        assert data['count'] == 1
        assert 'theory/future' in [d['target'] for d in data['missing_documents']]

    def test_json_includes_category_grouping(self, tmp_path):
        from missing_refs import MissingRefsCollector

        collector = MissingRefsCollector()
        collector.record_missing('theory/topic-a', 'index')
        collector.record_missing('theory/topic-b', 'index')
        collector.record_missing('concepts/idea', 'index')

        data = collector.to_dict()

        # Check by_category grouping
        assert 'by_category' in data
        assert 'theory' in data['by_category']
        assert len(data['by_category']['theory']) == 2
        assert 'concepts' in data['by_category']


class TestMarkdownOutput:
    """Tests for generating a 'Coming Soon' markdown page."""

    def test_generates_markdown_content(self):
        from missing_refs import MissingRefsCollector

        collector = MissingRefsCollector()
        collector.record_missing('theory/future-topic', 'index')
        collector.record_missing('concepts/new-idea', 'docs/intro')

        md = collector.to_markdown()

        assert '# Planned Articles' in md or '# Coming Soon' in md
        # Paths are converted to human-readable titles
        assert 'Future Topic' in md
        assert 'New Idea' in md

    def test_markdown_groups_by_category(self):
        from missing_refs import MissingRefsCollector

        collector = MissingRefsCollector()
        collector.record_missing('theory/topic-a', 'index')
        collector.record_missing('theory/topic-b', 'index')
        collector.record_missing('concepts/idea', 'index')

        md = collector.to_markdown()

        # Should have category headers
        assert '## theory' in md.lower() or '## Theory' in md
        assert '## concepts' in md.lower() or '## Concepts' in md

    def test_writes_markdown_file(self, tmp_path):
        from missing_refs import MissingRefsCollector

        collector = MissingRefsCollector()
        collector.record_missing('theory/future', 'index')

        output_path = tmp_path / 'coming-soon.md'
        collector.write_markdown(output_path)

        assert output_path.exists()
        content = output_path.read_text()
        # Path converted to human-readable title
        assert 'Future' in content
        assert '## Theory' in content

    def test_empty_collector_produces_minimal_output(self):
        from missing_refs import MissingRefsCollector

        collector = MissingRefsCollector()
        md = collector.to_markdown()

        assert 'No planned articles' in md or md.strip() == '' or 'coming soon' in md.lower()


class TestSphinxIntegration:
    """Tests for Sphinx event hooks."""

    def test_setup_returns_extension_metadata(self):
        from missing_refs import setup

        app = Mock()
        app.connect = Mock()
        app.add_config_value = Mock()

        result = setup(app)

        assert 'version' in result
        assert result['parallel_read_safe'] is True

    def test_registers_event_handlers(self):
        from missing_refs import setup

        app = Mock()
        app.connect = Mock()
        app.add_config_value = Mock()

        setup(app)

        # Should connect to warn-missing-reference and build-finished
        event_names = [call[0][0] for call in app.connect.call_args_list]
        assert 'warn-missing-reference' in event_names or 'missing-reference' in event_names
        assert 'build-finished' in event_names


class TestCollectorGlobals:
    """Tests for global collector instance management."""

    def test_get_collector_creates_instance(self):
        """get_collector should create a new instance if none exists."""
        from missing_refs import get_collector, reset_collector

        env = Mock()
        reset_collector(env)  # Start clean
        collector = get_collector(env)

        assert collector is not None
        from missing_refs import MissingRefsCollector
        assert isinstance(collector, MissingRefsCollector)

    def test_get_collector_returns_same_instance(self):
        """get_collector should return the same instance on subsequent calls."""
        from missing_refs import get_collector, reset_collector

        env = Mock()
        reset_collector(env)
        collector1 = get_collector(env)
        collector2 = get_collector(env)

        assert collector1 is collector2

    def test_reset_collector_clears_instance(self):
        """reset_collector should clear the global instance."""
        from missing_refs import get_collector, reset_collector

        env = Mock()
        reset_collector(env)
        collector1 = get_collector(env)
        reset_collector(env)
        collector2 = get_collector(env)

        assert collector1 is not collector2


class TestOnMissingReference:
    """Tests for the missing-reference event handler."""

    def test_records_doc_reference(self):
        """Should record doc-type references."""
        from missing_refs import on_missing_reference, get_collector, reset_collector

        # Mock node with doc reference
        node = {'reftype': 'doc', 'reftarget': 'theory/future-topic'}
        env = Mock()
        env.docname = 'index'
        reset_collector(env)

        result = on_missing_reference(None, env, node, None)

        assert result is None  # Let Sphinx continue
        collector = get_collector(env)
        assert 'theory/future-topic' in collector.missing

    def test_ignores_non_doc_references(self):
        """Should ignore non-doc reference types."""
        from missing_refs import on_missing_reference, get_collector, reset_collector

        # Mock node with non-doc reference
        node = {'reftype': 'ref', 'reftarget': 'some-label'}
        env = Mock()
        env.docname = 'index'
        reset_collector(env)

        on_missing_reference(None, env, node, None)

        collector = get_collector(env)
        assert 'some-label' not in collector.missing

    def test_handles_missing_docname(self):
        """Should handle env without docname attribute."""
        from missing_refs import on_missing_reference, get_collector, reset_collector

        node = {'reftype': 'doc', 'reftarget': 'some/topic'}
        env = Mock(spec=[])  # No docname attribute
        reset_collector(env)

        on_missing_reference(None, env, node, None)

        collector = get_collector(env)
        assert 'some/topic' in collector.missing
        assert 'unknown' in collector.missing['some/topic']['referenced_by']


class TestOnBuildFinished:
    """Tests for the build-finished event handler."""

    def test_skips_on_exception(self, tmp_path):
        """Should not write files if build had an exception."""
        from missing_refs import on_build_finished, get_collector, reset_collector

        env = Mock()
        reset_collector(env)
        collector = get_collector(env)
        collector.record_missing('test/topic', 'index')

        app = Mock()
        app.outdir = str(tmp_path)
        app.env = env

        # Call with exception (simulating failed build)
        on_build_finished(app, Exception("Build failed"))

        # Should not create output file
        assert not (tmp_path / 'missing_refs.json').exists()

    def test_skips_when_no_missing_refs(self, tmp_path):
        """Should not write files when nothing is missing."""
        from missing_refs import on_build_finished, reset_collector

        env = Mock()
        reset_collector(env)  # Empty collector

        app = Mock()
        app.outdir = str(tmp_path)
        app.env = env

        on_build_finished(app, None)

        assert not (tmp_path / 'missing_refs.json').exists()

    def test_writes_json_file(self, tmp_path):
        """Should write JSON file on successful build."""
        from missing_refs import on_build_finished, get_collector, reset_collector

        env = Mock()
        reset_collector(env)
        collector = get_collector(env)
        collector.record_missing('theory/topic', 'index')

        app = Mock()
        app.outdir = str(tmp_path)
        app.env = env
        app.config.missing_refs_generate_page = False

        on_build_finished(app, None)

        json_path = tmp_path / 'missing_refs.json'
        assert json_path.exists()
        data = json.loads(json_path.read_text())
        assert data['count'] == 1

    def test_writes_markdown_when_configured(self, tmp_path):
        """Should write markdown page when configured."""
        from missing_refs import on_build_finished, get_collector, reset_collector

        env = Mock()
        reset_collector(env)
        collector = get_collector(env)
        collector.record_missing('theory/topic', 'index')

        srcdir = tmp_path / 'src'
        srcdir.mkdir()

        app = Mock()
        app.outdir = str(tmp_path / 'build')
        app.srcdir = str(srcdir)
        app.env = env
        app.config.missing_refs_generate_page = True
        app.config.missing_refs_page_path = 'coming-soon.md'
        app.config.missing_refs_page_title = 'Planned Articles'

        on_build_finished(app, None)

        md_path = srcdir / 'coming-soon.md'
        assert md_path.exists()
        assert 'Theory' in md_path.read_text()

    def test_resets_collector_after_write(self, tmp_path):
        """Should reset collector after writing output."""
        from missing_refs import on_build_finished, get_collector, reset_collector

        env = Mock()
        reset_collector(env)
        collector = get_collector(env)
        collector.record_missing('theory/topic', 'index')

        app = Mock()
        app.outdir = str(tmp_path)
        app.env = env
        app.config.missing_refs_generate_page = False

        on_build_finished(app, None)

        # Get collector again - should be fresh
        new_collector = get_collector(env)
        assert len(new_collector.missing) == 0
