"""Tag inferrer - vocabulary-based tag suggestion.

Strategy: Seed + Expand
- Use existing tags from corpus as vocabulary
- Match content to existing tags via keyword matching
- Suggest new tags when appropriate (flagged for review)
"""

import re
from pathlib import Path
from typing import NamedTuple

import yaml

from ._common import strip_frontmatter

try:
    from rapidfuzz import fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False

from ..config import DEFAULT_TAG_VOCABULARY


class TagResult(NamedTuple):
    """Result of tag inference."""
    tags: list[str]
    suggested_new: list[str]
    needs_review: bool


class TagInferrer:
    """Infers tags from content using vocabulary matching."""

    def __init__(
        self,
        vocabulary: dict[str, list[str]] | None = None,
        vocabulary_file: Path | None = None,
        fuzzy_threshold: float = 0.7,
        max_tags: int = 10,
        min_confidence: float = 0.5,
    ):
        """Initialize the tag inferrer.

        Args:
            vocabulary: Dict mapping namespaces to tag lists
            vocabulary_file: Path to YAML file with vocabulary
            fuzzy_threshold: Threshold for fuzzy string matching (0-1)
            max_tags: Maximum number of tags to return
            min_confidence: Minimum confidence to include a tag
        """
        self.fuzzy_threshold = fuzzy_threshold
        self.max_tags = max_tags
        self.min_confidence = min_confidence

        # Load vocabulary
        if vocabulary_file:
            self._vocabulary_dict = self._load_vocabulary_file(vocabulary_file)
        elif vocabulary:
            self._vocabulary_dict = vocabulary
        else:
            self._vocabulary_dict = DEFAULT_TAG_VOCABULARY

        # Flatten vocabulary to set
        self.vocabulary: set[str] = set()
        for tags in self._vocabulary_dict.values():
            self.vocabulary.update(tags)

        # Build keyword index for faster matching
        self._keyword_index: dict[str, list[str]] = {}
        self._build_keyword_index()

    def _load_vocabulary_file(self, filepath: Path) -> dict[str, list[str]]:
        """Load vocabulary from YAML file."""
        filepath = Path(filepath)
        if not filepath.exists():
            return DEFAULT_TAG_VOCABULARY

        content = filepath.read_text(encoding='utf-8')
        data = yaml.safe_load(content)
        return data if isinstance(data, dict) else DEFAULT_TAG_VOCABULARY

    def _build_keyword_index(self) -> None:
        """Build index mapping keywords to tags for faster lookup."""
        for tag in self.vocabulary:
            # Extract keywords from tag path
            # e.g., "theory/class-analysis" -> ["theory", "class", "analysis"]
            parts = tag.replace("/", " ").replace("-", " ").lower().split()
            for part in parts:
                if part not in self._keyword_index:
                    self._keyword_index[part] = []
                self._keyword_index[part].append(tag)

    def infer(
        self,
        content: str,
        existing_tags: list[str] | None = None,
    ) -> TagResult:
        """Infer tags from content.

        Args:
            content: Markdown content to analyze
            existing_tags: Existing tags to preserve if valid

        Returns:
            TagResult with matched tags, suggested new tags, and review flag
        """
        matched_tags: set[str] = set()
        suggested_new: list[str] = []
        needs_review = False

        # Handle existing tags
        if existing_tags:
            for tag in existing_tags:
                normalized = tag.lower().strip()
                if normalized in self.vocabulary or self._normalize_tag(tag) in self.vocabulary:
                    matched_tags.add(self._normalize_tag(tag))
                else:
                    # Unknown tag - suggest for review
                    suggested_new.append(normalized)
                    needs_review = True

        # Extract content keywords
        content_keywords = self._extract_keywords(content)

        # Match keywords to vocabulary
        for keyword in content_keywords:
            keyword_lower = keyword.lower()

            # Direct keyword match
            if keyword_lower in self._keyword_index:
                for tag in self._keyword_index[keyword_lower]:
                    matched_tags.add(tag)

            # Fuzzy matching (if rapidfuzz available)
            elif HAS_RAPIDFUZZ:
                for vocab_keyword, tags in self._keyword_index.items():
                    ratio = fuzz.ratio(keyword_lower, vocab_keyword) / 100.0
                    if ratio >= self.fuzzy_threshold:
                        for tag in tags:
                            matched_tags.add(tag)

        # Limit number of tags
        tags_list = sorted(matched_tags)[:self.max_tags]

        # Flag for review if we suggested new tags
        if suggested_new:
            needs_review = True

        return TagResult(
            tags=tags_list,
            suggested_new=suggested_new,
            needs_review=needs_review,
        )

    def _normalize_tag(self, tag: str) -> str:
        """Normalize tag to lowercase with consistent format."""
        return tag.lower().strip()

    def _extract_keywords(self, content: str) -> set[str]:
        """Extract meaningful keywords from content.

        Filters out common words and short words.
        """
        # Strip frontmatter if present
        body = strip_frontmatter(content)

        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', body.lower())

        # Filter common words
        stopwords = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
            'can', 'had', 'her', 'was', 'one', 'our', 'out', 'has',
            'have', 'been', 'were', 'being', 'will', 'more', 'when',
            'who', 'with', 'they', 'this', 'that', 'from', 'which',
            'their', 'what', 'there', 'would', 'about', 'into', 'than',
            'then', 'them', 'these', 'some', 'other', 'such', 'only',
        }

        return {w for w in words if w not in stopwords and len(w) > 3}

    def parse_string_tags(
        self,
        tags: str | list[str]
    ) -> list[str]:
        """Parse tags from string or list format.

        Handles:
        - "tag1, tag2, tag3" -> ["tag1", "tag2", "tag3"]
        - ["tag1", "tag2"] -> ["tag1", "tag2"]

        Args:
            tags: Comma-separated string or list of tags

        Returns:
            List of normalized tag strings
        """
        if isinstance(tags, list):
            return [t.strip() for t in tags]

        if isinstance(tags, str):
            return [t.strip() for t in tags.split(',') if t.strip()]

        return []
