"""Inferrer modules for frontmatter field inference.

Modules:
- metadata: Deterministic fields (zkid, dates, title, author)
- category: SpaCy NLP-based category classification
- tags: Vocabulary-based tag suggestion
"""

from .metadata import MetadataInferrer
from .category import CategoryInferrer, CategoryResult
from .tags import TagInferrer, TagResult

__all__ = [
    "MetadataInferrer",
    "CategoryInferrer",
    "CategoryResult",
    "TagInferrer",
    "TagResult",
]
