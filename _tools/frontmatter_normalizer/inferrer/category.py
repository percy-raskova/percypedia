"""Category inferrer - SpaCy NLP-based classification.

Uses SpaCy word vectors for semantic similarity matching
between content and category definitions.

Falls back to keyword matching if SpaCy model lacks vectors.
"""

import re
from typing import Dict, List, NamedTuple, Optional, Set, Tuple

from ..config import CATEGORY_DEFINITIONS, VALID_CATEGORIES


class CategoryResult(NamedTuple):
    """Result of category inference."""
    category: str
    confidence: float
    needs_review: bool
    alternatives: List[Tuple[str, float]]


class CategoryInferrer:
    """Infers document category using SpaCy NLP."""

    def __init__(
        self,
        model_name: str = "en_core_web_lg",
        categories: Optional[Dict[str, List[str]]] = None,
        confidence_threshold: float = 0.6,
    ):
        """Initialize the category inferrer.

        Args:
            model_name: SpaCy model to use (lg has 685k vectors, best for similarity)
            categories: Custom category definitions (keyword lists)
            confidence_threshold: Threshold below which needs_review is True
        """
        self.confidence_threshold = confidence_threshold
        self._nlp = None
        self._model_name = model_name
        self._has_vectors = False

        # Load category definitions
        if categories:
            self._categories = categories
        else:
            self._categories = {
                cat: defn["keywords"]
                for cat, defn in CATEGORY_DEFINITIONS.items()
            }

        # Pre-compute category vectors lazily
        self._category_vectors: Dict[str, any] = {}

    def _load_model(self):
        """Lazy-load the SpaCy model."""
        if self._nlp is not None:
            return

        try:
            import spacy
            self._nlp = spacy.load(self._model_name)
            # Check if model has word vectors
            self._has_vectors = self._nlp.vocab.vectors.shape[0] > 0
        except (ImportError, OSError):
            # SpaCy not installed or model not found
            self._nlp = None
            self._has_vectors = False

    def _get_category_vector(self, category: str):
        """Get or compute vector representation for a category."""
        if category in self._category_vectors:
            return self._category_vectors[category]

        if not self._has_vectors or self._nlp is None:
            return None

        # Create document from category keywords
        keywords = self._categories.get(category, [])
        text = " ".join(keywords)
        doc = self._nlp(text)
        self._category_vectors[category] = doc.vector
        return doc.vector

    def infer(
        self,
        content: str,
        existing_category: Optional[str] = None,
    ) -> CategoryResult:
        """Infer the category from content.

        Args:
            content: Markdown content to classify
            existing_category: Preserve if valid

        Returns:
            CategoryResult with category, confidence, and alternatives
        """
        # If existing category is valid, preserve it with high confidence
        if existing_category and existing_category in VALID_CATEGORIES:
            return CategoryResult(
                category=existing_category,
                confidence=1.0,
                needs_review=False,
                alternatives=[],
            )

        # Load SpaCy model
        self._load_model()

        # Extract body text (strip frontmatter)
        body = self._strip_frontmatter(content)

        # Score each category
        scores: List[Tuple[str, float]] = []

        if self._has_vectors:
            scores = self._score_by_vectors(body)
        else:
            scores = self._score_by_keywords(body)

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)

        # Get best match
        best_category, best_score = scores[0] if scores else ("Miscellaneous", 0.0)

        # Alternatives are the rest
        alternatives = scores[1:4]  # Top 3 alternatives

        # Determine if review is needed
        needs_review = best_score < self.confidence_threshold

        return CategoryResult(
            category=best_category,
            confidence=best_score,
            needs_review=needs_review,
            alternatives=alternatives,
        )

    def _strip_frontmatter(self, content: str) -> str:
        """Remove frontmatter from content."""
        if not content.startswith('---'):
            return content

        lines = content.split('\n')
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == '---':
                return '\n'.join(lines[i + 1:])

        return content

    def _score_by_vectors(self, body: str) -> List[Tuple[str, float]]:
        """Score categories using SpaCy vector similarity."""
        scores: List[Tuple[str, float]] = []

        # Get document vector
        doc = self._nlp(body[:10000])  # Limit for performance
        doc_vector = doc.vector

        # Check if document has meaningful vector
        if doc_vector is None or doc_vector.sum() == 0:
            return self._score_by_keywords(body)

        for category in self._categories:
            cat_vector = self._get_category_vector(category)
            if cat_vector is None:
                continue

            # Cosine similarity
            import numpy as np
            dot_product = np.dot(doc_vector, cat_vector)
            norm_doc = np.linalg.norm(doc_vector)
            norm_cat = np.linalg.norm(cat_vector)

            if norm_doc > 0 and norm_cat > 0:
                similarity = dot_product / (norm_doc * norm_cat)
                # Normalize to 0-1 range (cosine can be -1 to 1)
                score = (similarity + 1) / 2
            else:
                score = 0.0

            scores.append((category, float(score)))

        return scores if scores else [("Miscellaneous", 0.3)]

    def _score_by_keywords(self, body: str) -> List[Tuple[str, float]]:
        """Score categories by keyword frequency (fallback method)."""
        body_lower = body.lower()

        # Extract words from body
        words = set(re.findall(r'\b[a-zA-Z]{3,}\b', body_lower))

        scores: List[Tuple[str, float]] = []

        for category, keywords in self._categories.items():
            # Count keyword matches
            matches = sum(1 for kw in keywords if kw.lower() in words)

            # Normalize by number of keywords
            if keywords:
                score = min(matches / len(keywords), 1.0)
            else:
                score = 0.0

            # Boost score if multiple matches
            if matches >= 3:
                score = min(score * 1.2, 1.0)

            scores.append((category, score))

        return scores if scores else [("Miscellaneous", 0.3)]
