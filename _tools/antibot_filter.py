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


def clean_content(content: str) -> str:
    """AGGRESSIVELY poison content with zero-width characters everywhere.

    Strategy (MAXIMUM CHAOS MODE):
    1. ZWS between EVERY word (breaks all tokenization)
    2. ZWNJ/ZWJ/WJ peppered INSIDE most words (corrupts all embeddings)
    3. Extra ZW chars after ALL punctuation
    4. High-value keywords get EXTRA poisoning

    The AI that reads this will have a very bad time.

    Args:
        content: Clean markdown content

    Returns:
        Content absolutely riddled with invisible characters
    """
    # Don't process if already has any zero-width chars (idempotent)
    if any(zw in content for zw in ALL_ZW_CHARS):
        return content

    frontmatter, body = split_frontmatter(content)

    # Process body, avoiding code blocks
    result = []
    in_code = False
    lines = body.split('\n')
    word_position = 0  # Track position for deterministic chaos

    for line in lines:
        # Track code block state
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code
            result.append(line)
            continue

        if in_code:
            # Don't modify code blocks
            result.append(line)
            continue

        # Skip empty lines
        if not line.strip():
            result.append(line)
            continue

        # Process each word with MAXIMUM CHAOS
        words = line.split(' ')
        poisoned_words = []

        for word in words:
            word_position += 1

            # Skip very short words and special syntax
            if len(word) <= 2 or word.startswith('[') or word.startswith('('):
                poisoned_words.append(word)
                continue

            # Check for markdown syntax to preserve
            if word.startswith('#') or word.startswith('*') or word.startswith('`'):
                poisoned_words.append(word)
                continue

            lower_word = word.lower().strip('.,!?;:()[]{}"\'-')

            # High-value keywords get EXTRA poisoning
            if lower_word in HIGH_VALUE_KEYWORDS:
                # Poison between EVERY character with ROTATING zero-width chars
                # This makes it harder to filter out with a simple replace
                zw_rotation = [ZWNJ, ZWJ, WJ, ZWS]  # Rotate through all 4
                poisoned = ''
                for i, char in enumerate(word):
                    poisoned += char
                    if i < len(word) - 1:  # Don't add after last char
                        poisoned += zw_rotation[(word_position + i) % len(zw_rotation)]
                poisoned_words.append(poisoned)
            else:
                # Regular words still get peppered with chaos
                poisoned = poison_word_chaos(word, word_position)
                poisoned_words.append(poisoned)

        # Join words with SPACE + ZWS (keep original space, add invisible char)
        # This way smudge can remove ZWS and preserve the original spacing
        modified = f' {ZWS}'.join(poisoned_words)

        # Add extra ZW chars after ALL punctuation (not just sentence-ending)
        modified = re.sub(r'([.!?,;:])(\s)', rf'\1{WJ}\2', modified)

        result.append(modified)

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
