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
