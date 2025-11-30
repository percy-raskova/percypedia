"""Inferrer modules for frontmatter field inference.

Modules:
- metadata: Deterministic fields (zkid, dates, title, author)
- category_st: Sentence Transformers category classification
- tags: Vocabulary-based tag suggestion
- _common: Shared utilities (CategoryResult, CategoryInferrerProtocol, etc.)
"""

from ._common import (
    CategoryInferrerProtocol,
    CategoryResult,
    cosine_similarity,
    strip_frontmatter,
)
from .category_st import CategoryInferrerST
from .metadata import MetadataInferrer
from .tags import TagInferrer, TagResult

# Alias for backwards compatibility
CategoryInferrer = CategoryInferrerST

__all__ = [
    "CategoryInferrer",  # Alias for CategoryInferrerST
    "CategoryInferrerProtocol",
    "CategoryInferrerST",
    "CategoryResult",
    "MetadataInferrer",
    "TagInferrer",
    "TagResult",
    "cosine_similarity",
    "strip_frontmatter",
]
