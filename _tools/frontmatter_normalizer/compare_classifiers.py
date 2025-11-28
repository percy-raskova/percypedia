"""Compare SpaCy vs Sentence Transformers category classification."""

import time
from frontmatter_normalizer.inferrer.category import CategoryInferrer as SpaCyInferrer
from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST as STInferrer


# Test content samples
SAMPLES = {
    'Labor Aristocracy (Theory)': '''# Labor Aristocracy

The labor aristocracy refers to workers in imperialist countries who benefit
from super-profits extracted from the Global South. This stratum of the working
class has material interests aligned with imperialism.

## Historical Context

Lenin first developed this concept in his analysis of the split in the
socialist movement during World War I.

## Implications for Organizing

Understanding the labor aristocracy is crucial for building genuine
working-class solidarity across national boundaries.
''',
    'Dialectical Materialism (Philosophy)': '''---
category: Concepts
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
''',
    'Organizing Guide (Methods)': '''---
id: '202401011200'
Date: '2024-01-01'
category: Methods
---

# Organizing Guide

A guide to organizing. How to build power in your workplace.
Step by step instructions for union formation.
''',
    'Taxonomy Docs (Infrastructure)': '''---
category: Infrastructure
---

# Taxonomy Documentation

This document describes the three-layer taxonomy system.
Configuration and setup for the documentation infrastructure.
''',
    'Short Story (Stories)': '''---
description: A short story about contradictions.
---

# Schrödinger's Bathroom

The bathroom door creaked open. Inside, the lights were both on and off.
''',
    'Polemic (Argumentative)': '''---
description: A critique of liberal approaches.
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
''',
}


def main():
    print('=' * 80)
    print('CLASSIFICATION COMPARISON: SpaCy en_core_web_lg vs Sentence Transformers mpnet')
    print('=' * 80)

    spacy_inferrer = SpaCyInferrer()
    st_inferrer = STInferrer()

    agreements = 0
    total = 0

    for name, content in SAMPLES.items():
        print(f'\n### {name}')

        # SpaCy
        start = time.time()
        spacy_result = spacy_inferrer.infer(content)
        spacy_time = (time.time() - start) * 1000

        # Sentence Transformers
        start = time.time()
        st_result = st_inferrer.infer(content)
        st_time = (time.time() - start) * 1000

        print(f'  SpaCy:    {spacy_result.category:15} (conf: {spacy_result.confidence:.3f}) [{spacy_time:.1f}ms]')
        print(f'  ST-mpnet: {st_result.category:15} (conf: {st_result.confidence:.3f}) [{st_time:.1f}ms]')

        total += 1
        if spacy_result.category == st_result.category:
            agreements += 1
        else:
            print(f'  ** DIFFERENT **')

    print('\n' + '=' * 80)
    print('Summary')
    print('=' * 80)
    print(f'Agreement: {agreements}/{total} ({agreements/total*100:.0f}%)')


if __name__ == '__main__':
    main()
