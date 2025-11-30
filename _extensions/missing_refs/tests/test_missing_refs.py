"""
Tests for missing_refs Sphinx extension.

Tests the collection and output of forward-links to unwritten documents.
These tests establish a baseline for safe refactoring.
"""

import json
from datetime import datetime
from unittest.mock import MagicMock

from missing_refs import (
    DEFAULT_PAGE_PATH,
    DEFAULT_PAGE_TITLE,
    JSON_OUTPUT_FILENAME,
    REFTYPE_DOC,
    UNCATEGORIZED,
    UNKNOWN_SOURCE,
    MissingRefsCollector,
    # Constants
    __version__,
    get_collector,
    on_build_finished,
    on_missing_reference,
    reset_collector,
    setup,
)

# =============================================================================
# Test Group 0: Module constants
# =============================================================================

class TestConstants:
    """Test module constants are defined correctly."""

    def test_version_is_string(self):
        """
        Given: __version__ constant
        When: Checking type
        Then: It is a string
        """
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_reftype_doc_constant(self):
        """
        Given: REFTYPE_DOC constant
        When: Checking value
        Then: It equals 'doc'
        """
        assert REFTYPE_DOC == 'doc'

    def test_uncategorized_constant(self):
        """
        Given: UNCATEGORIZED constant
        When: Checking value
        Then: It equals 'uncategorized'
        """
        assert UNCATEGORIZED == 'uncategorized'

    def test_unknown_source_constant(self):
        """
        Given: UNKNOWN_SOURCE constant
        When: Checking value
        Then: It equals 'unknown'
        """
        assert UNKNOWN_SOURCE == 'unknown'

    def test_default_page_title_constant(self):
        """
        Given: DEFAULT_PAGE_TITLE constant
        When: Checking value
        Then: It equals 'Planned Articles'
        """
        assert DEFAULT_PAGE_TITLE == 'Planned Articles'

    def test_default_page_path_constant(self):
        """
        Given: DEFAULT_PAGE_PATH constant
        When: Checking value
        Then: It equals 'coming-soon.md'
        """
        assert DEFAULT_PAGE_PATH == 'coming-soon.md'

    def test_json_output_filename_constant(self):
        """
        Given: JSON_OUTPUT_FILENAME constant
        When: Checking value
        Then: It equals 'missing_refs.json'
        """
        assert JSON_OUTPUT_FILENAME == 'missing_refs.json'


# =============================================================================
# Test Group 1a: MissingRefsCollector - _group_by_category helper
# =============================================================================

class TestGroupByCategory:
    """Test the _group_by_category helper method."""

    def test_empty_collector_returns_empty_dict(self):
        """
        Given: Empty collector
        When: _group_by_category is called
        Then: Returns empty dict
        """
        collector = MissingRefsCollector()

        result = collector._group_by_category()

        assert result == {}

    def test_groups_targets_by_category(self):
        """
        Given: Collector with targets in different categories
        When: _group_by_category is called
        Then: Returns dict with targets grouped by category
        """
        collector = MissingRefsCollector()
        collector.record_missing('theory/topic1', 'source')
        collector.record_missing('theory/topic2', 'source')
        collector.record_missing('concepts/other', 'source')

        result = collector._group_by_category()

        assert 'theory' in result
        assert 'concepts' in result
        assert len(result['theory']) == 2
        assert len(result['concepts']) == 1

    def test_uncategorized_for_root_targets(self):
        """
        Given: Collector with root-level target (no category)
        When: _group_by_category is called
        Then: Target grouped under UNCATEGORIZED constant
        """
        collector = MissingRefsCollector()
        collector.record_missing('glossary', 'source')

        result = collector._group_by_category()

        assert UNCATEGORIZED in result
        assert 'glossary' in result[UNCATEGORIZED]

    def test_categories_are_sorted(self):
        """
        Given: Multiple categories
        When: _group_by_category is called
        Then: Keys are sorted alphabetically
        """
        collector = MissingRefsCollector()
        collector.record_missing('z-cat/topic', 'source')
        collector.record_missing('a-cat/topic', 'source')
        collector.record_missing('m-cat/topic', 'source')

        result = collector._group_by_category()
        keys = list(result.keys())

        assert keys == sorted(keys)

    def test_targets_within_category_are_sorted(self):
        """
        Given: Category with multiple targets
        When: _group_by_category is called
        Then: Targets within category are sorted
        """
        collector = MissingRefsCollector()
        collector.record_missing('theory/z-topic', 'source')
        collector.record_missing('theory/a-topic', 'source')

        result = collector._group_by_category()

        assert result['theory'] == ['theory/a-topic', 'theory/z-topic']


# =============================================================================
# Test Group 1b: MissingRefsCollector - record_missing
# =============================================================================

class TestRecordMissing:
    """Test recording missing document references."""

    def test_record_single_missing_reference(self):
        """
        Given: Empty collector
        When: record_missing is called with target and source
        Then: Target is recorded with source in referenced_by
        """
        collector = MissingRefsCollector()

        collector.record_missing('theory/future-topic', 'index')

        assert 'theory/future-topic' in collector.missing
        assert 'index' in collector.missing['theory/future-topic']['referenced_by']

    def test_record_extracts_category_from_nested_path(self):
        """
        Given: Empty collector
        When: record_missing is called with nested path
        Then: Category is extracted from first path segment
        """
        collector = MissingRefsCollector()

        collector.record_missing('theory/future-topic', 'index')

        assert collector.missing['theory/future-topic']['category'] == 'theory'

    def test_record_sets_none_category_for_root_path(self):
        """
        Given: Empty collector
        When: record_missing is called with non-nested path
        Then: Category is None
        """
        collector = MissingRefsCollector()

        collector.record_missing('glossary', 'index')

        assert collector.missing['glossary']['category'] is None

    def test_record_handles_leading_slash(self):
        """
        Given: Empty collector
        When: record_missing is called with leading slash
        Then: Leading slash is stripped for category extraction
        """
        collector = MissingRefsCollector()

        collector.record_missing('/concepts/topic', 'index')

        assert collector.missing['/concepts/topic']['category'] == 'concepts'

    def test_record_multiple_sources_same_target(self):
        """
        Given: Collector with existing missing reference
        When: Same target referenced from different source
        Then: Both sources in referenced_by list
        """
        collector = MissingRefsCollector()

        collector.record_missing('theory/topic', 'doc1')
        collector.record_missing('theory/topic', 'doc2')

        refs = collector.missing['theory/topic']['referenced_by']
        assert 'doc1' in refs
        assert 'doc2' in refs
        assert len(refs) == 2

    def test_record_avoids_duplicate_sources(self):
        """
        Given: Collector with existing reference
        When: Same source references same target again
        Then: Source is not duplicated
        """
        collector = MissingRefsCollector()

        collector.record_missing('theory/topic', 'doc1')
        collector.record_missing('theory/topic', 'doc1')

        refs = collector.missing['theory/topic']['referenced_by']
        assert refs.count('doc1') == 1

    def test_record_multiple_targets(self):
        """
        Given: Empty collector
        When: Multiple different targets recorded
        Then: All targets tracked independently
        """
        collector = MissingRefsCollector()

        collector.record_missing('theory/topic1', 'doc1')
        collector.record_missing('concepts/topic2', 'doc1')
        collector.record_missing('polemics/topic3', 'doc2')

        assert len(collector.missing) == 3
        assert 'theory/topic1' in collector.missing
        assert 'concepts/topic2' in collector.missing
        assert 'polemics/topic3' in collector.missing


# =============================================================================
# Test Group 2: MissingRefsCollector - to_dict
# =============================================================================

class TestToDict:
    """Test conversion to dictionary structure."""

    def test_empty_collector_returns_empty_structure(self):
        """
        Given: Empty collector
        When: to_dict is called
        Then: Returns structure with count=0 and empty lists
        """
        collector = MissingRefsCollector()

        result = collector.to_dict()

        assert result['count'] == 0
        assert result['missing_documents'] == []
        assert result['by_category'] == {}
        assert 'generated_at' in result

    def test_to_dict_includes_generated_timestamp(self):
        """
        Given: Collector with data
        When: to_dict is called
        Then: generated_at is ISO format UTC timestamp
        """
        collector = MissingRefsCollector()
        collector.record_missing('topic', 'source')

        result = collector.to_dict()

        # Should parse without error
        timestamp = datetime.fromisoformat(result['generated_at'])
        assert timestamp.tzinfo is not None

    def test_to_dict_documents_sorted_by_target(self):
        """
        Given: Collector with multiple targets
        When: to_dict is called
        Then: missing_documents sorted alphabetically by target
        """
        collector = MissingRefsCollector()
        collector.record_missing('z-topic', 'source')
        collector.record_missing('a-topic', 'source')
        collector.record_missing('m-topic', 'source')

        result = collector.to_dict()
        targets = [d['target'] for d in result['missing_documents']]

        assert targets == ['a-topic', 'm-topic', 'z-topic']

    def test_to_dict_referenced_by_sorted(self):
        """
        Given: Target with multiple sources
        When: to_dict is called
        Then: referenced_by list is sorted
        """
        collector = MissingRefsCollector()
        collector.record_missing('topic', 'z-doc')
        collector.record_missing('topic', 'a-doc')
        collector.record_missing('topic', 'm-doc')

        result = collector.to_dict()
        refs = result['missing_documents'][0]['referenced_by']

        assert refs == ['a-doc', 'm-doc', 'z-doc']

    def test_to_dict_groups_by_category(self):
        """
        Given: Collector with targets in different categories
        When: to_dict is called
        Then: by_category groups targets correctly
        """
        collector = MissingRefsCollector()
        collector.record_missing('theory/topic1', 'source')
        collector.record_missing('theory/topic2', 'source')
        collector.record_missing('concepts/topic3', 'source')

        result = collector.to_dict()

        assert 'theory' in result['by_category']
        assert 'concepts' in result['by_category']
        assert len(result['by_category']['theory']) == 2
        assert len(result['by_category']['concepts']) == 1

    def test_to_dict_uncategorized_for_root_targets(self):
        """
        Given: Collector with root-level target (no category)
        When: to_dict is called
        Then: Target grouped under 'uncategorized'
        """
        collector = MissingRefsCollector()
        collector.record_missing('glossary', 'source')

        result = collector.to_dict()

        assert 'uncategorized' in result['by_category']
        assert 'glossary' in result['by_category']['uncategorized']

    def test_to_dict_categories_sorted(self):
        """
        Given: Collector with multiple categories
        When: to_dict is called
        Then: by_category keys are sorted
        """
        collector = MissingRefsCollector()
        collector.record_missing('z-category/topic', 'source')
        collector.record_missing('a-category/topic', 'source')

        result = collector.to_dict()
        keys = list(result['by_category'].keys())

        assert keys == sorted(keys)

    def test_to_dict_targets_within_category_sorted(self):
        """
        Given: Category with multiple targets
        When: to_dict is called
        Then: Targets within each category are sorted
        """
        collector = MissingRefsCollector()
        collector.record_missing('theory/z-topic', 'source')
        collector.record_missing('theory/a-topic', 'source')

        result = collector.to_dict()

        assert result['by_category']['theory'] == ['theory/a-topic', 'theory/z-topic']


# =============================================================================
# Test Group 3: MissingRefsCollector - write_json
# =============================================================================

class TestWriteJson:
    """Test JSON file output."""

    def test_write_json_creates_file(self, tmp_path):
        """
        Given: Collector with data
        When: write_json is called
        Then: JSON file is created
        """
        collector = MissingRefsCollector()
        collector.record_missing('topic', 'source')
        output = tmp_path / 'missing.json'

        collector.write_json(output)

        assert output.exists()

    def test_write_json_creates_parent_dirs(self, tmp_path):
        """
        Given: Output path with non-existent parent
        When: write_json is called
        Then: Parent directories are created
        """
        collector = MissingRefsCollector()
        collector.record_missing('topic', 'source')
        output = tmp_path / 'nested' / 'dir' / 'missing.json'

        collector.write_json(output)

        assert output.exists()

    def test_write_json_content_is_valid_json(self, tmp_path):
        """
        Given: Collector with data
        When: write_json is called
        Then: File contains valid JSON
        """
        collector = MissingRefsCollector()
        collector.record_missing('topic', 'source')
        output = tmp_path / 'missing.json'

        collector.write_json(output)

        # Should not raise
        data = json.loads(output.read_text())
        assert 'missing_documents' in data

    def test_write_json_encoding_utf8(self, tmp_path):
        """
        Given: Collector with unicode characters
        When: write_json is called
        Then: File is UTF-8 encoded
        """
        collector = MissingRefsCollector()
        collector.record_missing('teoria/valor', 'fuente')
        output = tmp_path / 'missing.json'

        collector.write_json(output)

        content = output.read_text(encoding='utf-8')
        assert 'teoria/valor' in content


# =============================================================================
# Test Group 4: MissingRefsCollector - to_markdown
# =============================================================================

class TestToMarkdown:
    """Test markdown generation."""

    def test_empty_collector_generates_empty_message(self):
        """
        Given: Empty collector
        When: to_markdown is called
        Then: Returns message about no planned articles
        """
        collector = MissingRefsCollector()

        result = collector.to_markdown()

        assert 'No planned articles' in result

    def test_to_markdown_includes_title(self):
        """
        Given: Collector with data
        When: to_markdown is called with default title
        Then: Output starts with default title
        """
        collector = MissingRefsCollector()
        collector.record_missing('topic', 'source')

        result = collector.to_markdown()

        assert result.startswith('# Planned Articles')

    def test_to_markdown_custom_title(self):
        """
        Given: Collector with data
        When: to_markdown is called with custom title
        Then: Output uses custom title
        """
        collector = MissingRefsCollector()
        collector.record_missing('topic', 'source')

        result = collector.to_markdown(title="Coming Soon")

        assert '# Coming Soon' in result

    def test_to_markdown_category_headings(self):
        """
        Given: Collector with categorized targets
        When: to_markdown is called
        Then: Categories appear as H2 headings
        """
        collector = MissingRefsCollector()
        collector.record_missing('theory/topic', 'source')
        collector.record_missing('concepts/other', 'source')

        result = collector.to_markdown()

        assert '## Theory' in result
        assert '## Concepts' in result

    def test_to_markdown_uncategorized_heading(self):
        """
        Given: Collector with uncategorized target
        When: to_markdown is called
        Then: 'Uncategorized' appears as heading
        """
        collector = MissingRefsCollector()
        collector.record_missing('glossary', 'source')

        result = collector.to_markdown()

        assert '## Uncategorized' in result

    def test_to_markdown_formats_target_name(self):
        """
        Given: Target with dashes/underscores
        When: to_markdown is called
        Then: Name is formatted (dashes/underscores to spaces, title case)
        """
        collector = MissingRefsCollector()
        collector.record_missing('theory/my-cool_topic', 'source')

        result = collector.to_markdown()

        assert 'My Cool Topic' in result

    def test_to_markdown_includes_references(self):
        """
        Given: Target with references
        When: to_markdown is called
        Then: Referenced by info is included
        """
        collector = MissingRefsCollector()
        collector.record_missing('theory/topic', 'index')

        result = collector.to_markdown()

        assert 'index' in result
        assert 'referenced from' in result

    def test_to_markdown_categories_sorted(self):
        """
        Given: Multiple categories
        When: to_markdown is called
        Then: Categories appear in sorted order
        """
        collector = MissingRefsCollector()
        collector.record_missing('z-cat/topic', 'source')
        collector.record_missing('a-cat/topic', 'source')

        result = collector.to_markdown()

        a_pos = result.find('A-Cat')
        z_pos = result.find('Z-Cat')
        assert a_pos < z_pos


# =============================================================================
# Test Group 5: MissingRefsCollector - write_markdown
# =============================================================================

class TestWriteMarkdown:
    """Test markdown file output."""

    def test_write_markdown_creates_file(self, tmp_path):
        """
        Given: Collector with data
        When: write_markdown is called
        Then: Markdown file is created
        """
        collector = MissingRefsCollector()
        collector.record_missing('topic', 'source')
        output = tmp_path / 'coming-soon.md'

        collector.write_markdown(output)

        assert output.exists()

    def test_write_markdown_creates_parent_dirs(self, tmp_path):
        """
        Given: Output path with non-existent parent
        When: write_markdown is called
        Then: Parent directories are created
        """
        collector = MissingRefsCollector()
        collector.record_missing('topic', 'source')
        output = tmp_path / 'nested' / 'coming-soon.md'

        collector.write_markdown(output)

        assert output.exists()

    def test_write_markdown_uses_custom_title(self, tmp_path):
        """
        Given: Custom title parameter
        When: write_markdown is called
        Then: File uses custom title
        """
        collector = MissingRefsCollector()
        collector.record_missing('topic', 'source')
        output = tmp_path / 'coming-soon.md'

        collector.write_markdown(output, title="Future Topics")

        content = output.read_text()
        assert '# Future Topics' in content


# =============================================================================
# Test Group 6: Global collector management
# =============================================================================

class TestGlobalCollector:
    """Test env-based collector pattern."""

    def test_get_collector_returns_collector(self):
        """
        Given: Fresh env
        When: get_collector is called
        Then: Returns MissingRefsCollector instance
        """
        env = MagicMock()
        env.missing_refs_collector = None
        reset_collector(env)

        collector = get_collector(env)

        assert isinstance(collector, MissingRefsCollector)

    def test_get_collector_returns_same_instance(self):
        """
        Given: Collector already created on env
        When: get_collector called again with same env
        Then: Returns same instance
        """
        env = MagicMock()
        env.missing_refs_collector = None
        reset_collector(env)

        collector1 = get_collector(env)
        collector2 = get_collector(env)

        assert collector1 is collector2

    def test_reset_collector_clears_instance(self):
        """
        Given: Collector with data on env
        When: reset_collector called, then get_collector
        Then: Returns fresh empty collector
        """
        env = MagicMock()
        env.missing_refs_collector = None
        reset_collector(env)
        collector1 = get_collector(env)
        collector1.record_missing('topic', 'source')

        reset_collector(env)
        collector2 = get_collector(env)

        assert collector1 is not collector2
        assert len(collector2.missing) == 0


# =============================================================================
# Test Group 7: on_missing_reference handler
# =============================================================================

class TestOnMissingReference:
    """Test Sphinx missing-reference event handler."""

    def test_records_doc_reference(self):
        """
        Given: Missing reference event for doc type
        When: on_missing_reference is called
        Then: Reference is recorded
        """
        app = MagicMock()
        env = MagicMock()
        env.missing_refs_collector = None
        env.docname = 'index'
        node = {'reftype': 'doc', 'reftarget': 'theory/future'}
        contnode = MagicMock()

        on_missing_reference(app, env, node, contnode)

        collector = get_collector(env)
        assert 'theory/future' in collector.missing

    def test_ignores_non_doc_references(self):
        """
        Given: Missing reference event for non-doc type (e.g., ref, term)
        When: on_missing_reference is called
        Then: Reference is not recorded
        """
        app = MagicMock()
        env = MagicMock()
        env.missing_refs_collector = None
        env.docname = 'index'
        node = {'reftype': 'ref', 'reftarget': 'some-label'}
        contnode = MagicMock()

        on_missing_reference(app, env, node, contnode)

        collector = get_collector(env)
        assert len(collector.missing) == 0

    def test_ignores_empty_reftarget(self):
        """
        Given: Doc reference with empty target
        When: on_missing_reference is called
        Then: Reference is not recorded
        """
        app = MagicMock()
        env = MagicMock()
        env.missing_refs_collector = None
        env.docname = 'index'
        node = {'reftype': 'doc', 'reftarget': ''}
        contnode = MagicMock()

        on_missing_reference(app, env, node, contnode)

        collector = get_collector(env)
        assert len(collector.missing) == 0

    def test_returns_none(self):
        """
        Given: Any missing reference
        When: on_missing_reference is called
        Then: Returns None (lets Sphinx continue)
        """
        app = MagicMock()
        env = MagicMock()
        env.missing_refs_collector = None
        env.docname = 'index'
        node = {'reftype': 'doc', 'reftarget': 'topic'}
        contnode = MagicMock()

        result = on_missing_reference(app, env, node, contnode)

        assert result is None

    def test_handles_missing_docname(self):
        """
        Given: env without docname attribute
        When: on_missing_reference is called
        Then: Uses 'unknown' as source
        """
        app = MagicMock()
        env = MagicMock(spec=['missing_refs_collector'])
        env.missing_refs_collector = None
        node = {'reftype': 'doc', 'reftarget': 'topic'}
        contnode = MagicMock()

        on_missing_reference(app, env, node, contnode)

        collector = get_collector(env)
        assert 'unknown' in collector.missing['topic']['referenced_by']


# =============================================================================
# Test Group 8: on_build_finished handler
# =============================================================================

class TestOnBuildFinished:
    """Test Sphinx build-finished event handler."""

    def test_does_nothing_on_exception(self, tmp_path):
        """
        Given: Build finished with exception
        When: on_build_finished is called
        Then: No output files created
        """
        env = MagicMock()
        env.missing_refs_collector = None
        app = MagicMock()
        app.outdir = str(tmp_path)
        app.env = env

        collector = get_collector(env)
        collector.record_missing('topic', 'source')

        on_build_finished(app, Exception("Build failed"))

        assert not (tmp_path / 'missing_refs.json').exists()

    def test_does_nothing_when_no_missing(self, tmp_path):
        """
        Given: Build finished with no missing refs
        When: on_build_finished is called
        Then: No output files created
        """
        env = MagicMock()
        env.missing_refs_collector = None
        app = MagicMock()
        app.outdir = str(tmp_path)
        app.env = env

        on_build_finished(app, None)

        assert not (tmp_path / 'missing_refs.json').exists()

    def test_writes_json_to_outdir(self, tmp_path):
        """
        Given: Build finished with missing refs
        When: on_build_finished is called
        Then: JSON file written to outdir
        """
        env = MagicMock()
        env.missing_refs_collector = None
        app = MagicMock()
        app.outdir = str(tmp_path)
        app.env = env
        app.config.missing_refs_generate_page = False

        collector = get_collector(env)
        collector.record_missing('topic', 'source')

        on_build_finished(app, None)

        assert (tmp_path / 'missing_refs.json').exists()

    def test_writes_markdown_when_configured(self, tmp_path):
        """
        Given: missing_refs_generate_page = True
        When: on_build_finished is called
        Then: Markdown page written to srcdir
        """
        srcdir = tmp_path / 'src'
        srcdir.mkdir()
        outdir = tmp_path / 'out'
        outdir.mkdir()

        env = MagicMock()
        env.missing_refs_collector = None
        app = MagicMock()
        app.outdir = str(outdir)
        app.srcdir = str(srcdir)
        app.env = env
        app.config.missing_refs_generate_page = True
        app.config.missing_refs_page_path = 'coming-soon.md'
        app.config.missing_refs_page_title = 'Coming Soon'

        collector = get_collector(env)
        collector.record_missing('topic', 'source')

        on_build_finished(app, None)

        assert (srcdir / 'coming-soon.md').exists()

    def test_skips_markdown_when_not_configured(self, tmp_path):
        """
        Given: missing_refs_generate_page = False
        When: on_build_finished is called
        Then: No markdown page written
        """
        srcdir = tmp_path / 'src'
        srcdir.mkdir()
        outdir = tmp_path / 'out'
        outdir.mkdir()

        env = MagicMock()
        env.missing_refs_collector = None
        app = MagicMock()
        app.outdir = str(outdir)
        app.srcdir = str(srcdir)
        app.env = env
        app.config.missing_refs_generate_page = False

        collector = get_collector(env)
        collector.record_missing('topic', 'source')

        on_build_finished(app, None)

        assert not (srcdir / 'coming-soon.md').exists()

    def test_resets_collector_after_write(self, tmp_path):
        """
        Given: Build finished with missing refs
        When: on_build_finished is called
        Then: Collector is reset for next build
        """
        env = MagicMock()
        env.missing_refs_collector = None
        app = MagicMock()
        app.outdir = str(tmp_path)
        app.env = env
        app.config.missing_refs_generate_page = False

        collector = get_collector(env)
        collector.record_missing('topic', 'source')

        on_build_finished(app, None)

        # Get new collector from env (should be fresh after reset)
        new_collector = get_collector(env)
        assert len(new_collector.missing) == 0


# =============================================================================
# Test Group 9: setup function
# =============================================================================

class TestSetup:
    """Test Sphinx extension setup."""

    def test_returns_extension_metadata(self):
        """
        Given: Mock Sphinx app
        When: setup() is called
        Then: Returns dict with version and parallel safety info
        """
        app = MagicMock()

        result = setup(app)

        assert isinstance(result, dict)
        assert 'version' in result
        assert result['parallel_read_safe'] is True
        assert result['parallel_write_safe'] is True

    def test_adds_config_values(self):
        """
        Given: Mock Sphinx app
        When: setup() is called
        Then: Configuration values are registered
        """
        app = MagicMock()

        setup(app)

        config_names = [call[0][0] for call in app.add_config_value.call_args_list]
        assert 'missing_refs_generate_page' in config_names
        assert 'missing_refs_page_path' in config_names
        assert 'missing_refs_page_title' in config_names

    def test_connects_missing_reference_event(self):
        """
        Given: Mock Sphinx app
        When: setup() is called
        Then: missing-reference event is connected
        """
        app = MagicMock()

        setup(app)

        events = [call[0][0] for call in app.connect.call_args_list]
        assert 'missing-reference' in events

    def test_connects_build_finished_event(self):
        """
        Given: Mock Sphinx app
        When: setup() is called
        Then: build-finished event is connected
        """
        app = MagicMock()

        setup(app)

        events = [call[0][0] for call in app.connect.call_args_list]
        assert 'build-finished' in events


# =============================================================================
# Test Group 10: Integration tests
# =============================================================================

class TestIntegration:
    """Integration tests for full workflows."""

    def test_full_workflow_json_output(self, tmp_path):
        """
        Given: Multiple missing references recorded
        When: Build finishes successfully
        Then: JSON output contains all references grouped correctly
        """
        env = MagicMock()
        env.missing_refs_collector = None
        app = MagicMock()
        app.outdir = str(tmp_path)
        app.env = env
        app.config.missing_refs_generate_page = False

        # Simulate multiple missing references
        env.docname = 'index'

        targets = [
            ('theory/dialectics', 'index'),
            ('theory/materialism', 'index'),
            ('concepts/value', 'theory/economics'),
            ('glossary', 'index'),
        ]

        for target, source in targets:
            env.docname = source
            node = {'reftype': 'doc', 'reftarget': target}
            on_missing_reference(app, env, node, MagicMock())

        on_build_finished(app, None)

        # Verify output
        output = tmp_path / 'missing_refs.json'
        data = json.loads(output.read_text())

        assert data['count'] == 4
        assert 'theory' in data['by_category']
        assert 'concepts' in data['by_category']
        assert 'uncategorized' in data['by_category']

    def test_full_workflow_markdown_output(self, tmp_path):
        """
        Given: Missing references and markdown generation enabled
        When: Build finishes successfully
        Then: Markdown page contains formatted content
        """
        srcdir = tmp_path / 'src'
        srcdir.mkdir()
        outdir = tmp_path / 'out'
        outdir.mkdir()

        env = MagicMock()
        env.missing_refs_collector = None
        app = MagicMock()
        app.outdir = str(outdir)
        app.srcdir = str(srcdir)
        app.env = env
        app.config.missing_refs_generate_page = True
        app.config.missing_refs_page_path = 'planned.md'
        app.config.missing_refs_page_title = 'Planned Articles'

        collector = get_collector(env)
        collector.record_missing('theory/future-topic', 'index')

        on_build_finished(app, None)

        content = (srcdir / 'planned.md').read_text()
        assert '# Planned Articles' in content
        assert '## Theory' in content
        assert 'Future Topic' in content
