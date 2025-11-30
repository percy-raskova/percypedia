"""Normalizer - core merge logic for frontmatter normalization.

Orchestrates:
- Parsing existing frontmatter
- Migrating old field names
- Discarding non-schema fields
- Inferring missing fields
- Merging to produce normalized frontmatter
"""

from pathlib import Path
from typing import Any, NamedTuple

from .config import (
    DEFAULTS,
    FIELD_MIGRATIONS,
    SCHEMA_FIELDS,
)
from .inferrer._common import CategoryInferrerProtocol
from .inferrer.category_st import CategoryInferrerST
from .inferrer.metadata import MetadataInferrer
from .inferrer.tags import TagInferrer
from .parser import parse_frontmatter


class NormalizationResult(NamedTuple):
    """Result of normalizing a document."""
    changed: bool
    frontmatter: dict[str, Any]
    body: str
    inferred_fields: list[str]
    needs_review: bool


class Normalizer:
    """Normalizes frontmatter for markdown documents.

    Uses Sentence Transformers (all-mpnet-base-v2) for category classification
    by default. The model uses semantic similarity to match document content
    against intent-based category definitions.
    """

    def __init__(
        self,
        metadata_inferrer: MetadataInferrer | None = None,
        category_inferrer: CategoryInferrerProtocol | None = None,
        tag_inferrer: TagInferrer | None = None,
    ):
        """Initialize the normalizer with inferrers.

        Args:
            metadata_inferrer: For zkid, dates, title, author
            category_inferrer: Any CategoryInferrerProtocol implementation
                              (defaults to CategoryInferrerST)
            tag_inferrer: For tag suggestions
        """
        self.metadata_inferrer = metadata_inferrer or MetadataInferrer()
        self.category_inferrer: CategoryInferrerProtocol = category_inferrer or CategoryInferrerST()
        self.tag_inferrer = tag_inferrer or TagInferrer()

    def normalize(
        self,
        content: str,
        filepath: Path,
    ) -> NormalizationResult:
        """Normalize frontmatter for a document.

        Args:
            content: Full markdown content
            filepath: Path to the file (for metadata inference)

        Returns:
            NormalizationResult with normalized frontmatter and body
        """
        # Parse existing frontmatter
        existing_fm, body = parse_frontmatter(content)

        # Track what changed
        inferred_fields: list[str] = []
        needs_review = False

        # Migrate old field names
        migrated_fm = self._migrate_fields(existing_fm)

        # Filter to schema fields only (discard custom fields)
        filtered_fm = self._filter_schema_fields(migrated_fm)

        # Start building normalized frontmatter
        normalized: dict[str, Any] = {}

        # Process each schema field
        # zkid
        if 'zkid' in filtered_fm:
            normalized['zkid'] = str(filtered_fm['zkid'])
        else:
            normalized['zkid'] = self.metadata_inferrer.infer_zkid(filepath)
            inferred_fields.append('zkid')

        # author
        if 'author' in filtered_fm:
            normalized['author'] = filtered_fm['author']
        else:
            normalized['author'] = self.metadata_inferrer.infer_author()
            inferred_fields.append('author')

        # title
        if 'title' in filtered_fm:
            normalized['title'] = filtered_fm['title']
        else:
            inferred_title = self.metadata_inferrer.infer_title(content)
            if inferred_title:
                normalized['title'] = inferred_title
                inferred_fields.append('title')

        # description (optional, don't infer)
        if 'description' in filtered_fm:
            normalized['description'] = filtered_fm['description']

        # dates
        dates = self.metadata_inferrer.infer_dates(filepath)
        if 'date-created' in filtered_fm:
            normalized['date-created'] = filtered_fm['date-created']
        else:
            normalized['date-created'] = dates['date-created']
            inferred_fields.append('date-created')

        if 'date-edited' in filtered_fm:
            normalized['date-edited'] = filtered_fm['date-edited']
        else:
            normalized['date-edited'] = dates['date-edited']
            inferred_fields.append('date-edited')

        # category
        existing_category = filtered_fm.get('category')
        cat_result = self.category_inferrer.infer(content, existing_category)
        normalized['category'] = cat_result.category
        if existing_category != cat_result.category:
            inferred_fields.append('category')
        if cat_result.needs_review:
            needs_review = True

        # tags
        existing_tags = filtered_fm.get('tags')
        if isinstance(existing_tags, str):
            # Convert string tags to list
            existing_tags = self.tag_inferrer.parse_string_tags(existing_tags)

        tag_result = self.tag_inferrer.infer(content, existing_tags)

        # Combine existing tags with inferred tags
        if existing_tags:
            # Preserve existing tags, add inferred ones
            all_tags = list(existing_tags)
            for tag in tag_result.tags:
                if tag not in all_tags:
                    all_tags.append(tag)
            normalized['tags'] = all_tags
        elif tag_result.tags:
            normalized['tags'] = tag_result.tags
            inferred_fields.append('tags')

        if tag_result.needs_review:
            needs_review = True

        # publish
        if 'publish' in filtered_fm:
            normalized['publish'] = bool(filtered_fm['publish'])
        else:
            normalized['publish'] = DEFAULTS['publish']
            inferred_fields.append('publish')

        # status
        if 'status' in filtered_fm:
            normalized['status'] = filtered_fm['status']
        else:
            normalized['status'] = DEFAULTS['status']
            inferred_fields.append('status')

        # Determine if anything changed
        changed = self._has_changes(existing_fm, normalized, body, content)

        return NormalizationResult(
            changed=changed,
            frontmatter=normalized,
            body=body,
            inferred_fields=inferred_fields,
            needs_review=needs_review,
        )

    def _migrate_fields(self, frontmatter: dict[str, Any]) -> dict[str, Any]:
        """Migrate old field names to new names."""
        result = {}

        for key, value in frontmatter.items():
            # Check if this is an old field name
            if key in FIELD_MIGRATIONS:
                new_key = FIELD_MIGRATIONS[key]
                result[new_key] = value
            else:
                result[key] = value

        return result

    def _filter_schema_fields(self, frontmatter: dict[str, Any]) -> dict[str, Any]:
        """Keep only schema-valid fields, discard the rest."""
        return {
            k: v for k, v in frontmatter.items()
            if k in SCHEMA_FIELDS
        }

    def _has_changes(
        self,
        original: dict[str, Any],
        normalized: dict[str, Any],
        body: str,
        content: str,
    ) -> bool:
        """Determine if normalization made any changes."""
        # If no original frontmatter, definitely changed
        if not original:
            return True

        # Check if field count differs
        original_schema_fields = {
            k: v for k, v in original.items()
            if k in SCHEMA_FIELDS or k in FIELD_MIGRATIONS
        }

        if len(original_schema_fields) != len(normalized):
            return True

        # Check individual field values
        for key, value in normalized.items():
            # Map back to original key if migrated
            original_key = key
            for old_key, new_key in FIELD_MIGRATIONS.items():
                if new_key == key and old_key in original:
                    original_key = old_key
                    break

            if original_key not in original:
                return True

            original_value = original[original_key]

            # Compare lists as sets (order doesn't matter for tags)
            if isinstance(value, list) and isinstance(original_value, list):
                if set(value) != set(original_value):
                    return True
            elif original_value != value:
                return True

        # Check for discarded fields
        return any(key not in SCHEMA_FIELDS and key not in FIELD_MIGRATIONS for key in original)


def normalize(content: str, filepath: Path) -> NormalizationResult:
    """Convenience function for single-file normalization.

    Args:
        content: Full markdown content
        filepath: Path to the file

    Returns:
        NormalizationResult
    """
    normalizer = Normalizer()
    return normalizer.normalize(content, filepath)
