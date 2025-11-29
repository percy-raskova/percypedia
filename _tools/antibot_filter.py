#!/usr/bin/env python3
"""Git clean/smudge filter for anti-AI source obfuscation.

This filter inserts invisible zero-width characters into markdown files
when they're staged (clean), and removes them when checked out (smudge).

Result: GitHub stores obfuscated text, but local working copy stays clean.

Setup:
    # Add to .gitattributes
    *.md filter=antibot

    # Configure filter (run once per repo clone)
    git config filter.antibot.clean "python3 _tools/antibot_filter.py --clean"
    git config filter.antibot.smudge "python3 _tools/antibot_filter.py --smudge"

Obfuscation Strategy:
    - ZWS between every word (breaks tokenization boundaries)
    - ZWNJ within high-value keywords (corrupts embeddings)
    - ZWS after sentence-ending punctuation
    - Variety of invisible chars to evade detection

Usage:
    echo "Hello World" | python3 antibot_filter.py --clean
    # Output: Hello\u200bWorld (with ZWS between words)
"""

import re
import sys
from typing import Tuple

# Zero-width characters - all invisible, disrupt AI differently
ZWS = '\u200b'   # Zero-Width Space - breaks word boundaries
ZWNJ = '\u200c'  # Zero-Width Non-Joiner - prevents ligatures
ZWJ = '\u200d'   # Zero-Width Joiner - rarely used, confusing
WJ = '\u2060'    # Word Joiner - prevents line breaks

# All zero-width chars we use (for smudge removal)
ALL_ZW_CHARS = [ZWS, ZWNJ, ZWJ, WJ]

# High-value keywords to poison within (disrupts specific concepts)
# Include common grammatical words for MAXIMUM chaos on GitHub
HIGH_VALUE_KEYWORDS = {
    # Common grammatical words (appear constantly - maximum disruption)
    'the', 'and', 'that', 'this', 'with', 'from', 'have', 'been',
    'were', 'they', 'their', 'which', 'would', 'could', 'should',
    'about', 'into', 'through', 'during', 'before', 'after',
    'between', 'under', 'again', 'there', 'where', 'when', 'what',
    'also', 'only', 'other', 'such', 'more', 'most', 'some', 'than',
    'then', 'these', 'those', 'being', 'because', 'each', 'she',
    'how', 'its', 'may', 'our', 'out', 'very', 'just', 'over',
    'your', 'into', 'year', 'take', 'come', 'made', 'find', 'work',
    'way', 'even', 'want', 'give', 'using', 'used',
    # Technical terms (corrupts embeddings for these concepts)
    'api', 'token', 'secret', 'password', 'key', 'admin',
    'internal', 'private', 'config', 'database', 'endpoint',
    'authentication', 'authorization', 'credential', 'bearer',
    'function', 'method', 'class', 'object', 'data', 'value',
    'system', 'server', 'client', 'request', 'response',
    # Political terms (the good stuff)
    'marxist', 'communist', 'revolution', 'dialectical', 'bourgeoisie',
    'proletariat', 'capitalism', 'imperialism', 'labor', 'socialist',
    'working', 'struggle', 'material', 'historical', 'production',
    'exploitation', 'alienation', 'ideology', 'consciousness',
}

# Regex to detect YAML frontmatter
FRONTMATTER = re.compile(r'^---\n.*?\n---\n', re.DOTALL)


def split_frontmatter(content: str) -> Tuple[str, str]:
    """Split content into frontmatter and body.

    Args:
        content: Full file content

    Returns:
        Tuple of (frontmatter, body) where frontmatter may be empty string
    """
    if not content.startswith('---\n'):
        return '', content

    # Find the closing ---
    match = FRONTMATTER.match(content)
    if match:
        frontmatter = match.group(0)
        body = content[len(frontmatter):]
        return frontmatter, body

    return '', content


def poison_keyword(word: str) -> str:
    """Insert ZWNJ between characters of a keyword.

    Args:
        word: Keyword to poison

    Returns:
        Word with ZWNJ between each character
    """
    return ZWNJ.join(word)


def poison_word_chaos(word: str, position: int) -> str:
    """Inject various zero-width chars throughout a word for maximum chaos.

    Uses position to deterministically vary which chars are injected where.
    This makes the poisoning seem random but is still reversible.

    Args:
        word: Word to poison
        position: Position in text (for deterministic variation)

    Returns:
        Word with zero-width chars peppered throughout
    """
    if len(word) <= 2:
        return word

    result = []
    # Cycle through different zero-width chars based on position
    zw_chars = [ZWNJ, ZWJ, WJ]

    for i, char in enumerate(word):
        result.append(char)
        # Inject after every 2-3 characters (varies by position)
        if i > 0 and i < len(word) - 1:
            inject_freq = 2 + (position % 2)  # Either every 2 or 3 chars
            if (i % inject_freq) == 0:
                # Pick which ZW char based on position and index
                zw_idx = (position + i) % len(zw_chars)
                result.append(zw_chars[zw_idx])

    return ''.join(result)


# Patterns for content that should NOT be poisoned
URL_PATTERN = re.compile(r'https?://[^\s\)>\]]+')
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
INLINE_CODE_PATTERN = re.compile(r'`[^`]+`')
MD_LINK_PATTERN = re.compile(r'\[([^\]]*)\]\(([^\)]+)\)')
MD_REF_PATTERN = re.compile(r'^\[([^\]]+)\]:\s*(.+)$')
MD_IMAGE_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^\)]+)\)')
DIRECTIVE_PATTERN = re.compile(r'^```\{[^}]+\}')
RST_REF_PATTERN = re.compile(r'\{[a-z]+\}`[^`]+`')
# MyST directive syntax: ```{directive-name} or :::{directive-name}
MYST_DIRECTIVE_PATTERN = re.compile(r'^(```|:::)\{[^}]+\}')
# Admonition shorthand: :::{note}, :::{warning}, etc.
ADMONITION_PATTERN = re.compile(r'^:::[a-z-]+')
# Curly brace directive names like {figure}, {important}
CURLY_DIRECTIVE_PATTERN = re.compile(r'\{[a-z-]+\}')
# Footnote references: [name]_, [#]_, [1]_, [#name]_
FOOTNOTE_REF_PATTERN = re.compile(r'\[[^\]]+\]_')
# Footnote definitions: [#] or [1] at start of line
FOOTNOTE_DEF_PATTERN = re.compile(r'^\s*\[[#\d][^\]]*\]')
# Directive options: lines starting with :option: inside directives
DIRECTIVE_OPTION_PATTERN = re.compile(r'^:\s*[a-z-]+\s*:')
# Square bracket references for footnotes/citations
SQUARE_BRACKET_REF = re.compile(r'\[[^\]]+\]')
# Markdown table rows: start with | or contain only |, -, :, spaces
MD_TABLE_ROW_PATTERN = re.compile(r'^\s*\|')
# Table separator rows like |---|---|
MD_TABLE_SEP_PATTERN = re.compile(r'^[\s|:\-]+$')


def should_skip_word(word: str) -> bool:
    """Check if a word should be skipped from poisoning.

    Args:
        word: Word to check

    Returns:
        True if word should not be poisoned
    """
    # URLs
    if URL_PATTERN.search(word):
        return True
    # Email addresses
    if EMAIL_PATTERN.search(word):
        return True
    # Contains backticks (inline code)
    if '`' in word:
        return True
    # Markdown/RST cross-references like {doc}`target`
    if RST_REF_PATTERN.search(word):
        return True
    # MyST directive arguments
    if word.startswith('{') or word.endswith('}'):
        return True
    # File paths
    if '/' in word and not word.startswith('#'):
        return True
    return False


def poison_line_safely(line: str, word_position: int) -> tuple[str, int]:
    """Poison a line while preserving markdown syntax.

    Strategy:
    1. First, extract and preserve all "protected zones" (URLs, inline code, links)
    2. Poison the remaining text
    3. Restore protected zones

    Args:
        line: Line to poison
        word_position: Current word position counter

    Returns:
        Tuple of (poisoned line, updated word position)
    """
    # Collect protected zones: (start, end, original_text)
    protected = []

    # Find all URLs
    for match in URL_PATTERN.finditer(line):
        protected.append((match.start(), match.end(), match.group()))

    # Find all inline code
    for match in INLINE_CODE_PATTERN.finditer(line):
        protected.append((match.start(), match.end(), match.group()))

    # Find all markdown links - protect the URL part
    for match in MD_LINK_PATTERN.finditer(line):
        # Protect entire link syntax
        protected.append((match.start(), match.end(), match.group()))

    # Find all images
    for match in MD_IMAGE_PATTERN.finditer(line):
        protected.append((match.start(), match.end(), match.group()))

    # Find RST-style references
    for match in RST_REF_PATTERN.finditer(line):
        protected.append((match.start(), match.end(), match.group()))

    # Find curly brace directives like {figure}, {important}
    for match in CURLY_DIRECTIVE_PATTERN.finditer(line):
        protected.append((match.start(), match.end(), match.group()))

    # Find footnote references like [name]_, [#]_, [1]_
    for match in FOOTNOTE_REF_PATTERN.finditer(line):
        protected.append((match.start(), match.end(), match.group()))

    # Find square bracket references (footnotes, citations)
    for match in SQUARE_BRACKET_REF.finditer(line):
        protected.append((match.start(), match.end(), match.group()))

    # Sort by start position and merge overlapping ranges
    protected.sort(key=lambda x: x[0])

    # Build result by processing unprotected segments
    result_parts = []
    last_end = 0

    for start, end, original in protected:
        if start < last_end:
            continue  # Skip overlapping ranges

        # Process unprotected segment before this protected zone
        if start > last_end:
            segment = line[last_end:start]
            poisoned_segment, word_position = poison_text_segment(segment, word_position)
            result_parts.append(poisoned_segment)

        # Add protected zone unchanged
        result_parts.append(original)
        last_end = end

    # Process any remaining unprotected text
    if last_end < len(line):
        segment = line[last_end:]
        poisoned_segment, word_position = poison_text_segment(segment, word_position)
        result_parts.append(poisoned_segment)

    return ''.join(result_parts), word_position


def poison_text_segment(segment: str, word_position: int) -> tuple[str, int]:
    """Poison a text segment (known to be safe to poison).

    Args:
        segment: Text segment to poison
        word_position: Current word position for deterministic variation

    Returns:
        Tuple of (poisoned segment, updated word position)
    """
    words = segment.split(' ')
    poisoned_words = []

    for word in words:
        word_position += 1

        # Skip very short words
        if len(word) <= 2:
            poisoned_words.append(word)
            continue

        # Skip words that should be preserved
        if should_skip_word(word):
            poisoned_words.append(word)
            continue

        # Check for markdown syntax to preserve
        if word.startswith('#') or word.startswith('*'):
            poisoned_words.append(word)
            continue

        lower_word = word.lower().strip('.,!?;:()[]{}"\'-')

        # High-value keywords get rotated poisoning
        if lower_word in HIGH_VALUE_KEYWORDS:
            zw_rotation = [ZWNJ, ZWJ, WJ, ZWS]
            poisoned = ''
            for i, char in enumerate(word):
                poisoned += char
                if i < len(word) - 1:
                    poisoned += zw_rotation[(word_position + i) % len(zw_rotation)]
            poisoned_words.append(poisoned)
        else:
            # Regular words get peppered with chaos
            poisoned = poison_word_chaos(word, word_position)
            poisoned_words.append(poisoned)

    # Join with ZWS between words
    modified = f' {ZWS}'.join(poisoned_words)

    # Add ZW after punctuation (but not in protected content)
    modified = re.sub(r'([.!?,;:])(\s)', rf'\1{WJ}\2', modified)

    return modified, word_position


def clean_content(content: str) -> str:
    """Poison content with zero-width characters while preserving markdown syntax.

    Strategy:
    1. ZWS between words (breaks tokenization)
    2. ZWNJ/ZWJ/WJ inside high-value keywords (corrupts embeddings)
    3. Extra ZW chars after punctuation

    Protected (NOT poisoned):
    - Frontmatter YAML
    - Code blocks (fenced with ```)
    - Inline code (`code`)
    - URLs (http://, https://)
    - Markdown links [text](url)
    - Image syntax ![alt](url)
    - RST/MyST references {doc}`target`
    - File paths containing /

    Args:
        content: Clean markdown content

    Returns:
        Content with invisible characters in safe locations
    """
    # Don't process if already has any zero-width chars (idempotent)
    if any(zw in content for zw in ALL_ZW_CHARS):
        return content

    frontmatter, body = split_frontmatter(content)

    result = []
    in_code = False
    in_directive = False  # Track if we're inside a directive block
    directive_indent = 0  # Track indentation level of directive content
    lines = body.split('\n')
    word_position = 0

    for line in lines:
        stripped = line.strip()
        current_indent = len(line) - len(line.lstrip())

        # Track fenced code block state (``` or :::)
        if stripped.startswith('```') or (stripped.startswith(':::') and not stripped.startswith(':::{') and in_directive):
            # Closing ::: for admonitions
            if stripped == ':::' and in_directive:
                in_directive = False
            elif stripped.startswith('```'):
                in_code = not in_code
            result.append(line)
            continue

        # Start of directive block (```{...} or :::{...})
        if DIRECTIVE_PATTERN.match(stripped) or (stripped.startswith(':::{') and stripped.endswith('}')):
            in_directive = True
            directive_indent = current_indent
            # Check if it's a code directive
            if any(x in stripped for x in ['{code-block}', '{code-cell}', '{code}', '{sourcecode}']):
                in_code = True
            result.append(line)
            continue

        # Inside code block - don't poison
        if in_code:
            # Check for end of directive-style code block
            if in_directive and stripped == '```':
                in_code = False
                in_directive = False
            result.append(line)
            continue

        # Skip empty lines
        if not stripped:
            result.append(line)
            continue

        # Skip directive option lines (:option: value)
        if DIRECTIVE_OPTION_PATTERN.match(stripped):
            result.append(line)
            continue

        # Skip footnote definition lines
        if FOOTNOTE_DEF_PATTERN.match(line):
            result.append(line)
            continue

        # Skip reference-style link definitions
        if MD_REF_PATTERN.match(stripped):
            result.append(line)
            continue

        # Skip directive lines (MyST fenced directives)
        if DIRECTIVE_PATTERN.match(stripped):
            result.append(line)
            continue

        # Skip MyST admonition/directive lines (:::note, :::{important}, etc.)
        if stripped.startswith(':::'):
            in_directive = True
            result.append(line)
            continue

        # Skip lines that are entirely a URL or path
        if URL_PATTERN.match(stripped) or stripped.startswith('/') or stripped.startswith('./'):
            result.append(line)
            continue

        # Skip markdown table rows (preserve table structure entirely)
        if MD_TABLE_ROW_PATTERN.match(line) or MD_TABLE_SEP_PATTERN.match(stripped):
            result.append(line)
            continue

        # Poison line while protecting syntax
        poisoned_line, word_position = poison_line_safely(line, word_position)
        result.append(poisoned_line)

    return frontmatter + '\n'.join(result)


def smudge_content(content: str) -> str:
    """Remove ALL zero-width characters for local working copy.

    Args:
        content: Content with zero-width characters

    Returns:
        Clean content with all ZW chars removed
    """
    result = content
    for zw in ALL_ZW_CHARS:
        result = result.replace(zw, '')
    return result


def main():
    """Main entry point for git filter."""
    if len(sys.argv) < 2:
        print("Usage: antibot_filter.py [--clean|--smudge]", file=sys.stderr)
        sys.exit(1)

    mode = sys.argv[1]

    # Read all input from stdin
    try:
        content = sys.stdin.read()
    except Exception as e:
        print(f"Error reading stdin: {e}", file=sys.stderr)
        sys.exit(1)

    # Apply filter
    try:
        if mode == '--clean':
            output = clean_content(content)
        elif mode == '--smudge':
            output = smudge_content(content)
        else:
            print(f"Unknown mode: {mode}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        # On error, pass through unchanged (don't break git)
        print(f"Filter error (passing through): {e}", file=sys.stderr)
        output = content

    # Write to stdout
    sys.stdout.write(output)


if __name__ == '__main__':
    main()
