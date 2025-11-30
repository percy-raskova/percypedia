"""Tests for BaseCollector and related utilities."""

from types import SimpleNamespace

import pytest

from _common.collector import BaseCollector, CollectorEntry, make_merge_handler


class TestCollectorEntry:
    """Tests for CollectorEntry dataclass."""

    def test_location_property(self):
        """location property formats as docname:lineno."""
        entry = CollectorEntry(docname='theory/marxism', lineno=42, anchor='term-value')
        assert entry.location == 'theory/marxism:42'

    def test_all_fields_accessible(self):
        """All fields are accessible."""
        entry = CollectorEntry(docname='doc', lineno=10, anchor='anchor-id')
        assert entry.docname == 'doc'
        assert entry.lineno == 10
        assert entry.anchor == 'anchor-id'


class SampleCollector(BaseCollector[str]):
    """Sample collector for testing."""

    env_attr = 'sample_collector'

    def __init__(self):
        self._entries: dict[str, str] = {}

    def add(self, key: str, value: str) -> None:
        self._entries[key] = value

    def merge(self, other: 'SampleCollector') -> None:
        self._entries.update(other._entries)


class TestBaseCollector:
    """Tests for BaseCollector abstract base class."""

    def test_get_or_create_creates_new(self):
        """get_or_create creates collector when not present."""
        env = SimpleNamespace()
        collector = SampleCollector.get_or_create(env)

        assert hasattr(env, 'sample_collector')
        assert isinstance(collector, SampleCollector)
        assert collector is env.sample_collector

    def test_get_or_create_returns_existing(self):
        """get_or_create returns existing collector."""
        env = SimpleNamespace()
        first = SampleCollector.get_or_create(env)
        first.add('key1', 'value1')

        second = SampleCollector.get_or_create(env)

        assert second is first
        assert 'key1' in second

    def test_get_or_create_replaces_none(self):
        """get_or_create replaces None attribute."""
        env = SimpleNamespace(sample_collector=None)
        collector = SampleCollector.get_or_create(env)

        assert collector is not None
        assert isinstance(collector, SampleCollector)

    def test_reset_sets_to_none(self):
        """reset() sets attribute to None."""
        env = SimpleNamespace()
        SampleCollector.get_or_create(env)
        SampleCollector.reset(env)

        assert env.sample_collector is None

    def test_len_with_entries_attr(self):
        """__len__ works with _entries attribute."""
        collector = SampleCollector()
        collector.add('a', '1')
        collector.add('b', '2')

        assert len(collector) == 2

    def test_contains_with_entries_attr(self):
        """__contains__ works with _entries attribute."""
        collector = SampleCollector()
        collector.add('found', 'value')

        assert 'found' in collector
        assert 'missing' not in collector

    def test_merge_combines_entries(self):
        """merge() combines entries from other collector."""
        collector1 = SampleCollector()
        collector1.add('a', '1')

        collector2 = SampleCollector()
        collector2.add('b', '2')
        collector2.add('c', '3')

        collector1.merge(collector2)

        assert len(collector1) == 3
        assert 'a' in collector1
        assert 'b' in collector1
        assert 'c' in collector1


class TestMakeMergeHandler:
    """Tests for make_merge_handler factory."""

    def test_creates_callable(self):
        """make_merge_handler returns a callable."""
        handler = make_merge_handler(SampleCollector)
        assert callable(handler)

    def test_handler_merges_collectors(self):
        """Handler merges collector from other_env."""
        env = SimpleNamespace()
        other_env = SimpleNamespace()

        # Set up collectors
        main = SampleCollector.get_or_create(env)
        main.add('existing', 'value')

        other = SampleCollector.get_or_create(other_env)
        other.add('new', 'data')

        # Call handler
        handler = make_merge_handler(SampleCollector)
        handler(None, env, [], other_env)

        assert 'existing' in main
        assert 'new' in main

    def test_handler_handles_missing_other_collector(self):
        """Handler does nothing if other_env has no collector."""
        env = SimpleNamespace()
        other_env = SimpleNamespace()  # No collector

        main = SampleCollector.get_or_create(env)
        main.add('existing', 'value')

        handler = make_merge_handler(SampleCollector)
        handler(None, env, [], other_env)

        # Should not raise, and main should be unchanged
        assert len(main) == 1

    def test_handler_creates_main_collector_if_needed(self):
        """Handler creates main collector if missing."""
        env = SimpleNamespace()
        other_env = SimpleNamespace()

        other = SampleCollector.get_or_create(other_env)
        other.add('new', 'data')

        handler = make_merge_handler(SampleCollector)
        handler(None, env, [], other_env)

        assert hasattr(env, 'sample_collector')
        assert 'new' in env.sample_collector
