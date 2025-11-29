"""Property-based tests using Hypothesis.

These tests verify invariants across randomly generated inputs.
Install hypothesis with: pip install hypothesis

Skip these tests if hypothesis not installed: pytest -m "not property"
"""

import pytest

try:
    from hypothesis import given, strategies as st, settings, assume
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    # Provide dummy decorators when hypothesis is not installed
    def given(*args, **kwargs):
        def decorator(f):
            return pytest.mark.skip(reason="hypothesis not installed")(f)
        return decorator

    class st:
        """Dummy strategies class for when hypothesis is not installed."""
        @staticmethod
        def text(*args, **kwargs):
            return None
        @staticmethod
        def integers(*args, **kwargs):
            return None
        @staticmethod
        def floats(*args, **kwargs):
            return None
        @staticmethod
        def booleans(*args, **kwargs):
            return None
        @staticmethod
        def dictionaries(*args, **kwargs):
            return None
        @staticmethod
        def lists(*args, **kwargs):
            return None
        @staticmethod
        def tuples(*args, **kwargs):
            return None
        @staticmethod
        def one_of(*args, **kwargs):
            return None

    def settings(*args, **kwargs):
        def decorator(f):
            return f
        return decorator

    def assume(x):
        pass


pytestmark = pytest.mark.skipif(
    not HYPOTHESIS_AVAILABLE,
    reason="hypothesis not installed"
)


@pytest.mark.property
class TestFrontmatterExtractionProperties:
    """Property-based tests for frontmatter extraction."""

    @given(st.text(min_size=0, max_size=1000))
    @settings(max_examples=50)
    def test_extract_never_crashes(self, content):
        """extract_frontmatter should never crash on any input."""
        from _common.frontmatter import extract_frontmatter

        # Should not raise any exception
        result = extract_frontmatter(content)

        # Result should always be a dict (possibly empty)
        assert isinstance(result, dict)

    @given(st.text(min_size=0, max_size=500))
    @settings(max_examples=50)
    def test_extract_returns_dict_or_empty(self, yaml_content):
        """Result should always be a dict."""
        from _common.frontmatter import extract_frontmatter

        # Create valid frontmatter structure
        content = f"---\n{yaml_content}\n---\n# Content"

        result = extract_frontmatter(content)
        assert isinstance(result, dict)

    @given(st.dictionaries(
        keys=st.text(alphabet="abcdefghijklmnopqrstuvwxyz_", min_size=1, max_size=20),
        values=st.one_of(st.text(max_size=100), st.booleans(), st.integers()),
        max_size=10
    ))
    @settings(max_examples=30)
    def test_valid_yaml_roundtrips(self, data):
        """Valid YAML frontmatter should be extractable."""
        import yaml
        from _common.frontmatter import extract_frontmatter

        # Skip if data would produce invalid YAML
        try:
            yaml_str = yaml.dump(data, default_flow_style=False)
        except Exception:
            assume(False)

        content = f"---\n{yaml_str}---\n# Content"
        result = extract_frontmatter(content)

        # Should extract the data (keys should match)
        for key in data:
            if key in result:
                # Value might be transformed by YAML parsing
                assert result[key] is not None or data[key] is None


@pytest.mark.property
class TestObsidianCommentProperties:
    """Property-based tests for Obsidian comment stripping."""

    @given(st.text(min_size=0, max_size=500))
    @settings(max_examples=50)
    def test_strip_never_crashes(self, content):
        """strip_obsidian_comments should never crash."""
        from publish_filter import strip_obsidian_comments

        source = [content]
        # Should not raise
        strip_obsidian_comments(None, 'test', source)

        # Result should be a string
        assert isinstance(source[0], str)

    @given(st.text(min_size=0, max_size=200))
    @settings(max_examples=30)
    def test_no_comments_unchanged(self, content):
        """Content without %% should be unchanged."""
        from publish_filter import strip_obsidian_comments

        # Skip if content contains %%
        assume("%%" not in content)

        source = [content]
        strip_obsidian_comments(None, 'test', source)

        assert source[0] == content

    @given(
        st.text(min_size=1, max_size=50),  # before
        st.text(min_size=1, max_size=50),  # comment
        st.text(min_size=1, max_size=50),  # after
    )
    @settings(max_examples=30)
    def test_comment_stripped(self, before, comment, after):
        """Comments should be removed from output."""
        from publish_filter import strip_obsidian_comments

        # Ensure none of the parts contain %%
        assume("%%" not in before)
        assume("%%" not in comment)
        assume("%%" not in after)

        content = f"{before}%%{comment}%%{after}"
        source = [content]
        strip_obsidian_comments(None, 'test', source)

        # Comment should be gone
        assert comment not in source[0] or comment in before or comment in after


@pytest.mark.property
class TestMissingRefsCollectorProperties:
    """Property-based tests for missing refs collector."""

    @given(
        st.text(alphabet="abcdefghijklmnopqrstuvwxyz/-_", min_size=1, max_size=50),
        st.text(alphabet="abcdefghijklmnopqrstuvwxyz/-_", min_size=1, max_size=50),
    )
    @settings(max_examples=50)
    def test_record_never_crashes(self, target, referrer):
        """record_missing should never crash on valid-ish paths."""
        from missing_refs import MissingRefsCollector

        collector = MissingRefsCollector()
        # Should not raise
        collector.record_missing(target, referrer)

        # Target should be recorded
        assert target in collector.missing

    @given(st.lists(
        st.tuples(
            st.text(alphabet="abcdefghijklmnopqrstuvwxyz/", min_size=1, max_size=30),
            st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=20),
        ),
        min_size=0,
        max_size=20
    ))
    @settings(max_examples=30)
    def test_count_matches_unique_targets(self, records):
        """Count should match number of unique targets."""
        from missing_refs import MissingRefsCollector

        collector = MissingRefsCollector()
        for target, referrer in records:
            collector.record_missing(target, referrer)

        unique_targets = len(set(target for target, _ in records))
        assert len(collector.missing) == unique_targets


@pytest.mark.property
class TestCategoryInferrerProperties:
    """Property-based tests for ML category inferrer."""

    @pytest.fixture
    def inferrer(self):
        """Get shared inferrer instance."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST
        return CategoryInferrerST()

    @given(st.text(min_size=0, max_size=500))
    @settings(max_examples=20)  # Fewer examples due to ML overhead
    def test_infer_never_crashes(self, inferrer, content):
        """infer() should never crash on any input."""
        result = inferrer.infer(content)

        # Should return a valid result
        assert result.category is not None
        assert isinstance(result.confidence, float)
        assert 0.0 <= result.confidence <= 1.0

    @given(st.text(min_size=10, max_size=200))
    @settings(max_examples=15)
    def test_category_is_valid(self, inferrer, content):
        """Inferred category should always be valid."""
        valid_categories = {"Theory", "Praxis", "Polemics", "Creative", "Meta"}

        result = inferrer.infer(content)

        assert result.category in valid_categories
