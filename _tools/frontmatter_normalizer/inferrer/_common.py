"""Common utilities shared across inferrer modules.

This module provides shared functionality to avoid code duplication:
- strip_frontmatter(): Extract body text from markdown with frontmatter
- CategoryResult: NamedTuple for category inference results
- cosine_similarity(): Vector similarity calculation
- CategoryInferrerProtocol: Protocol for category inferrer implementations
"""

from typing import List, NamedTuple, Optional, Protocol, Tuple, runtime_checkable


class CategoryResult(NamedTuple):
    """Result of category inference."""
    category: str
    confidence: float
    needs_review: bool
    alternatives: List[Tuple[str, float]]


@runtime_checkable
class CategoryInferrerProtocol(Protocol):
    """Protocol defining the interface for category inferrers.

    Any class implementing this protocol can be used for category inference.
    This enables dependency injection and easier testing.

    Example:
        class MockCategoryInferrer:
            def infer(self, content: str, existing_category: str | None = None) -> CategoryResult:
                return CategoryResult("Theory", 1.0, False, [])

        # MockCategoryInferrer is a valid CategoryInferrerProtocol
        normalizer = Normalizer(category_inferrer=MockCategoryInferrer())
    """

    def infer(
        self,
        content: str,
        existing_category: Optional[str] = None,
    ) -> CategoryResult:
        """Infer category from content.

        Args:
            content: Markdown content to classify
            existing_category: Existing category to preserve if valid

        Returns:
            CategoryResult with category, confidence, needs_review, and alternatives
        """
        ...


def strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from markdown content.

    Args:
        content: Markdown content potentially starting with ---

    Returns:
        Body text without frontmatter
    """
    if not content.startswith('---'):
        return content

    lines = content.split('\n')
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == '---':
            return '\n'.join(lines[i + 1:])

    return content


def cosine_similarity(vec1, vec2) -> float:
    """Compute cosine similarity between two vectors.

    Args:
        vec1: First vector (numpy array)
        vec2: Second vector (numpy array)

    Returns:
        Cosine similarity value between -1 and 1
    """
    import numpy as np

    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 > 0 and norm2 > 0:
        return dot_product / (norm1 * norm2)
    return 0.0
