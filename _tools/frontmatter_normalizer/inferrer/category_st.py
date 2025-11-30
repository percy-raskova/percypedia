"""Category inferrer using Sentence Transformers.

Uses all-mpnet-base-v2 model for semantic similarity classification.
Embeddings are computed for category descriptions and compared against
document embeddings using cosine similarity.
"""


from ..config import CATEGORY_DEFINITIONS, VALID_CATEGORIES
from ._common import CategoryResult, cosine_similarity, strip_frontmatter


class CategoryInferrerST:
    """Infers document category using Sentence Transformers.

    Uses semantic similarity between document content and category
    descriptions (example_phrases) to classify documents.
    """

    def __init__(
        self,
        model_name: str = "all-mpnet-base-v2",
        categories: dict[str, dict] | None = None,
        confidence_threshold: float = 0.6,
    ):
        """Initialize the category inferrer.

        Args:
            model_name: Sentence Transformers model to use
            categories: Custom category definitions (with example_phrases)
            confidence_threshold: Threshold below which needs_review is True
        """
        self._model_name = model_name
        self.confidence_threshold = confidence_threshold
        self._model = None

        # Load category definitions
        if categories:
            self._category_definitions = categories
        else:
            self._category_definitions = CATEGORY_DEFINITIONS

        # Cache for category embeddings
        self._category_embeddings = None

    def _load_model(self):
        """Lazy-load the Sentence Transformers model."""
        if self._model is not None:
            return

        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name)
        except ImportError:
            raise ImportError(
                "sentence-transformers is required. "
                "Install with: pip install sentence-transformers"
            )

    def _compute_category_embeddings(self):
        """Compute and cache embeddings for all category descriptions."""
        if self._category_embeddings is not None:
            return

        self._load_model()

        self._category_embeddings = {}
        for category, definition in self._category_definitions.items():
            # Use example_phrases for semantic similarity
            phrases = definition.get("example_phrases", [])
            if not phrases:
                # Fallback to description + keywords
                desc = definition.get("description", "")
                keywords = definition.get("keywords", [])
                phrases = [desc, *keywords[:5]]

            # Encode all phrases and average them
            embeddings = self._model.encode(phrases)
            # Mean of phrase embeddings represents the category
            self._category_embeddings[category] = embeddings.mean(axis=0)

    def infer(
        self,
        content: str,
        existing_category: str | None = None,
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

        # Load model and compute category embeddings
        self._load_model()
        self._compute_category_embeddings()

        # Extract body text (strip frontmatter)
        body = strip_frontmatter(content)

        # Handle very short content
        if len(body.strip()) < 20:
            return CategoryResult(
                category="Miscellaneous",
                confidence=0.3,
                needs_review=True,
                alternatives=[(cat, 0.2) for cat in list(VALID_CATEGORIES)[:3]],
            )

        # Truncate long content for performance
        body_truncated = body[:10000]

        # Compute document embedding
        doc_embedding = self._model.encode(body_truncated)

        # Compute similarity with each category
        scores: list[tuple[str, float]] = []

        for category, cat_embedding in self._category_embeddings.items():
            # Cosine similarity
            similarity = cosine_similarity(doc_embedding, cat_embedding)
            # Normalize to 0-1 range (cosine similarity is -1 to 1)
            score = (similarity + 1) / 2
            scores.append((category, float(score)))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)

        # Get best match
        best_category, best_score = scores[0] if scores else ("Miscellaneous", 0.0)

        # Alternatives are the rest (top 3)
        alternatives = scores[1:4]

        # Determine if review is needed
        needs_review = best_score < self.confidence_threshold

        return CategoryResult(
            category=best_category,
            confidence=best_score,
            needs_review=needs_review,
            alternatives=alternatives,
        )
