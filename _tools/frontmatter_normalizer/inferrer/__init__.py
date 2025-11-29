"""Inferrer modules for frontmatter field inference.

Modules:
- metadata: Deterministic fields (zkid, dates, title, author)
- category_st: Sentence Transformers category classification
- tags: Vocabulary-based tag suggestion
- _common: Shared utilities (CategoryResult, CategoryInferrerProtocol, etc.)
"""

from .metadata import MetadataInferrer
from .category_st import CategoryInferrerST
from .tags import TagInferrer, TagResult
from ._common import (
    CategoryResult,
    CategoryInferrerProtocol,
    strip_frontmatter,
    cosine_similarity,
)

# Alias for backwards compatibility
CategoryInferrer = CategoryInferrerST

__all__ = [
    "MetadataInferrer",
    "CategoryInferrer",  # Alias for CategoryInferrerST
    "CategoryInferrerST",
    "CategoryInferrerProtocol",
    "CategoryResult",
    "TagInferrer",
    "TagResult",
    "strip_frontmatter",
    "cosine_similarity",
]
