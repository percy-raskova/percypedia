"""Shared test fixtures for frontmatter normalizer tests."""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import os


# =============================================================================
# Content Fixtures - Various Frontmatter States
# =============================================================================

@pytest.fixture
def file_no_frontmatter():
    """theory/labor-aristocracy.md style - pure content, no frontmatter."""
    return """# Labor Aristocracy

The labor aristocracy refers to workers in imperialist countries who benefit
from super-profits extracted from the Global South. This stratum of the working
class has material interests aligned with imperialism.

## Historical Context

Lenin first developed this concept in his analysis of the split in the
socialist movement during World War I.

## Implications for Organizing

Understanding the labor aristocracy is crucial for building genuine
working-class solidarity across national boundaries.
"""


@pytest.fixture
def file_custom_fields():
    """sample/concepts style - has non-schema fields that should be discarded."""
    return """---
category: Theory
Confidence: high
Date: '2024-11-20'
Related: '{doc}`theory/materialism`'
Status: foundational
Tags: theory, philosophy, foundations
Updated: '2024-11-26'
---

# Dialectical Materialism

Dialectical materialism is the philosophical and scientific framework
developed by Marx and Engels. It combines materialist ontology with
dialectical methodology.

## Core Principles

1. The primacy of matter over consciousness
2. The interconnection of all phenomena
3. The constant motion and change of reality
4. Contradiction as the motor of change
"""


@pytest.fixture
def file_schema_compliant():
    """Already correct - should not change (idempotent test)."""
    return """---
zkid: '202411281430'
author: Percy
title: Test Document
description: A test document for validation.
date-created: '2024-11-28'
date-edited: '2024-11-28'
category: Theory
tags:
  - theory/marxism
  - philosophy/dialectics
publish: false
status: draft
---

# Test Document

This document already has schema-compliant frontmatter.
"""


@pytest.fixture
def file_partial_frontmatter():
    """Has some fields, missing others - should fill gaps."""
    return """---
category: Meta
---

# Taxonomy Documentation

This document describes the three-layer taxonomy system.
"""


@pytest.fixture
def file_old_field_names():
    """Uses old field names that need migration."""
    return """---
id: '202401011200'
Date: '2024-01-01'
Updated: '2024-01-15'
Tags: organizing, strategy
Status: draft
category: Praxis
---

# Organizing Guide

A guide to organizing.
"""


@pytest.fixture
def file_string_tags():
    """Tags as comma-separated string instead of array."""
    return """---
category: Theory
Tags: theory, philosophy, marxism
---

# Some Concept

Content here.
"""


@pytest.fixture
def file_creative_writing():
    """Creative content with non-standard metadata."""
    return """---
description: A short story about contradictions.
permalink: /stories/bathroom
---

# Schrödinger's Bathroom

The bathroom door creaked open. Inside, the lights were both on and off.
"""


@pytest.fixture
def file_polemic():
    """Polemic/argumentative content."""
    return """---
description: A critique of liberal approaches.
cover: /images/corruption.jpg
---

# On Corruption

The liberal conception of corruption fundamentally misunderstands the nature
of capitalist society. What they call corruption is often simply the normal
functioning of a system designed to serve capital.

## The Liberal Framework

Liberals treat corruption as an aberration, a deviation from the otherwise
healthy functioning of democratic capitalism.

## A Materialist Analysis

From a materialist perspective, corruption is not a bug but a feature.
"""


# =============================================================================
# Temporary File System Fixtures
# =============================================================================

@pytest.fixture
def temp_md_file(tmp_path):
    """Factory fixture to create temporary markdown files."""
    def _create(content: str, name: str = "test.md") -> Path:
        file_path = tmp_path / name
        file_path.write_text(content)
        return file_path
    return _create


@pytest.fixture
def temp_srcdir(tmp_path):
    """Create a realistic source directory structure for integration tests."""
    # Root files
    (tmp_path / "index.md").write_text("# Index\n\nWelcome.")
    (tmp_path / "glossary.md").write_text("# Glossary\n\nTerms.")

    # Theory directory (no frontmatter)
    theory = tmp_path / "theory"
    theory.mkdir()
    (theory / "labor-aristocracy.md").write_text(
        "# Labor Aristocracy\n\nThe labor aristocracy refers to..."
    )
    (theory / "dialectics.md").write_text(
        "# Dialectics\n\nDialectics is the study of contradiction..."
    )

    # Sample/concepts (custom fields)
    concepts = tmp_path / "sample" / "concepts"
    concepts.mkdir(parents=True)
    (concepts / "materialism.md").write_text("""---
category: Theory
Confidence: high
Date: '2024-11-20'
Tags: theory, philosophy
---

# Dialectical Materialism

Content here.
""")

    # Docs (partial frontmatter)
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "taxonomy.md").write_text("""---
category: Meta
---

# Taxonomy

Documentation about taxonomy.
""")

    # Exclude directories
    (tmp_path / "_build").mkdir()
    (tmp_path / "_build" / "output.md").write_text("# Build output")
    (tmp_path / ".venv").mkdir()
    (tmp_path / "private").mkdir()
    (tmp_path / "private" / "secret.md").write_text("# Secret")

    return tmp_path


# =============================================================================
# Mock Inferrer Fixtures
# =============================================================================

@pytest.fixture
def mock_category_result():
    """Factory for mock CategoryResult."""
    from typing import NamedTuple

    class CategoryResult(NamedTuple):
        category: str
        confidence: float
        needs_review: bool
        alternatives: list

    def _create(category="Theory", confidence=0.85, needs_review=False):
        return CategoryResult(
            category=category,
            confidence=confidence,
            needs_review=needs_review,
            alternatives=[("Praxis", 0.6), ("Polemics", 0.5)]
        )
    return _create


@pytest.fixture
def mock_tag_result():
    """Factory for mock TagResult."""
    from typing import NamedTuple

    class TagResult(NamedTuple):
        tags: list
        suggested_new: list
        needs_review: bool

    def _create(tags=None, suggested_new=None, needs_review=False):
        return TagResult(
            tags=tags or ["theory/marxism"],
            suggested_new=suggested_new or [],
            needs_review=needs_review
        )
    return _create


# =============================================================================
# Schema Fields Reference
# =============================================================================

@pytest.fixture
def schema_fields():
    """Set of valid schema field names."""
    return {
        "zkid", "author", "title", "description",
        "date-created", "date-edited", "category",
        "tags", "publish", "status"
    }


@pytest.fixture
def field_migrations():
    """Mapping of old field names to new."""
    return {
        "id": "zkid",
        "Date": "date-created",
        "Updated": "date-edited",
        "Tags": "tags",
        "Status": "status",
    }


# =============================================================================
# Session-Scoped ML Model Fixtures (Performance Optimization)
# =============================================================================
# These fixtures load expensive ML models once per test session instead of
# once per test, reducing test time by ~70%.

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
