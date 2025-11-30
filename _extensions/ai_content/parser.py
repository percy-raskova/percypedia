"""
Parser for AI chat content.

Parses [human]/[assistant] markers from directive content.
"""

import re


def parse_chat_messages(content: str) -> list[dict[str, str]]:
    """
    Parse chat content with [human]/[assistant] markers.

    Args:
        content: Raw content string with markers

    Returns:
        List of message dicts with 'sender' and 'content' keys
    """
    if not content or not content.strip():
        return []

    messages = []

    # Pattern to match [human] or [assistant] markers
    # Captures the sender and everything until the next marker or end
    pattern = r'\[(human|assistant)\]\s*\n(.*?)(?=\n\[(human|assistant)\]|$)'

    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)

    for match in matches:
        sender = match[0].lower()
        msg_content = match[1].strip()

        if msg_content:  # Only add non-empty messages
            messages.append({
                'sender': sender,
                'content': msg_content,
            })

    return messages


def format_title(name: str) -> str:
    """
    Format a slug-style name as a human-readable title.

    Args:
        name: Slug like 'azure-discussion' or 'Azure Discussion'

    Returns:
        Formatted title like 'Azure Discussion'
    """
    # If already has spaces, just title case it
    if ' ' in name:
        return name.title()

    # Convert kebab-case to title case
    return name.replace('-', ' ').replace('_', ' ').title()


def parse_exchange(content: str) -> dict | None:
    """
    Parse exchange content with --- separator.

    Args:
        content: Raw content with question, ---, answer

    Returns:
        Dict with 'question' and 'answer' keys, or None if invalid
    """
    if not content or not content.strip():
        return None

    # Split on --- (must be on its own line)
    parts = content.split('\n---\n')

    if len(parts) < 2:
        # Try splitting on just ---
        parts = content.split('---')
        if len(parts) < 2:
            return None

    question = parts[0].strip()
    answer = '---'.join(parts[1:]).strip()  # Rejoin in case multiple ---

    if not question or not answer:
        return None

    return {
        'question': question,
        'answer': answer,
    }


def slugify(name: str) -> str:
    """
    Convert a name to a URL-safe slug.

    Args:
        name: Any string

    Returns:
        Lowercase slug with hyphens
    """
    # Lowercase
    slug = name.lower()
    # Replace spaces and underscores with hyphens
    slug = re.sub(r'[\s_]+', '-', slug)
    # Remove non-alphanumeric (except hyphens)
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Collapse multiple hyphens
    slug = re.sub(r'-+', '-', slug)
    # Strip leading/trailing hyphens
    slug = slug.strip('-')

    return slug
