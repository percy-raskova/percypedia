"""Session-scoped ML model fixtures for normalizer tests.

These fixtures load expensive ML models once per test session instead of
once per test, reducing test time by ~70%. Keep these separate to ensure
proper session scope inheritance.
"""

import pytest


# =============================================================================
# Session-Scoped ML Model Fixtures (Performance Optimization)
# =============================================================================

@pytest.fixture(scope="session")
def st_category_inferrer():
    """Shared Sentence Transformers category inferrer - loads model once for entire session."""
    from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST
    inferrer = CategoryInferrerST()
    # Force model and embeddings loading
    inferrer.infer("# Test\n\nContent to force model load.")
    return inferrer


@pytest.fixture(scope="session")
def shared_metadata_inferrer():
    """Shared metadata inferrer (cheap, but consistent)."""
    from frontmatter_normalizer.inferrer.metadata import MetadataInferrer
    return MetadataInferrer()


@pytest.fixture(scope="session")
def shared_tag_inferrer():
    """Shared tag inferrer (cheap, but consistent)."""
    from frontmatter_normalizer.inferrer.tags import TagInferrer
    return TagInferrer()


@pytest.fixture(scope="session")
def shared_normalizer(st_category_inferrer, shared_metadata_inferrer, shared_tag_inferrer):
    """Shared normalizer with pre-loaded models for fast CLI/integration tests."""
    from frontmatter_normalizer.normalizer import Normalizer
    return Normalizer(
        metadata_inferrer=shared_metadata_inferrer,
        category_inferrer=st_category_inferrer,
        tag_inferrer=shared_tag_inferrer,
    )
