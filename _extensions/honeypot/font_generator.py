"""Font generator for anti-AI text obfuscation.

Creates a WOFF2 font where character-to-glyph mappings are scrambled.
The encoding map is used to transform plaintext so the font renders it correctly.

Example:
    To display 'hello', we encode it as 'xqnns' (using the map).
    The font renders 'x' using the 'h' glyph, 'q' using 'e' glyph, etc.
    Result: Browser shows 'hello', scrapers see 'xqnns'.
"""

import json
import random
from pathlib import Path

from fontTools.ttLib import TTFont

__all__ = ['generate_scrambled_font']

# Characters to scramble (alphanumerics)
CHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def generate_scrambled_font(
    base_font_path: Path,
    output_path: Path,
    seed: int,
    save_map: bool = False,
) -> dict[str, str]:
    """Generate a font with scrambled character-to-glyph mappings.

    Args:
        base_font_path: Path to the base TrueType font (e.g., LiberationSans-Regular.ttf)
        output_path: Output path for the WOFF2 font
        seed: Random seed for deterministic scrambling
        save_map: If True, save encoding map as JSON next to font

    Returns:
        Encoding map: dict mapping original char → replacement char.
        To display 'a', put encode_map['a'] in HTML; the font will render 'a' glyph.
    """
    # Create deterministic shuffle
    rng = random.Random(seed)
    charset_list = list(CHARSET)
    shuffled = charset_list.copy()
    rng.shuffle(shuffled)

    # Build encoding map: original_char → replacement_char
    # When we want to display 'a', we put shuffled[i] in HTML
    # The font maps shuffled[i] codepoint to 'a' glyph
    encode_map = {}
    for i, original_char in enumerate(charset_list):
        replacement_char = shuffled[i]
        encode_map[original_char] = replacement_char

    # Load base font
    font = TTFont(str(base_font_path))

    # Get the best cmap (character to glyph mapping)
    cmap = font['cmap'].getBestCmap()

    # Build new cmap: for each (original, replacement) pair,
    # map the REPLACEMENT codepoint to the ORIGINAL glyph
    # Effect: when browser sees replacement char, it renders original glyph
    new_cmap = {}

    # First, copy all non-scrambled characters (punctuation, etc.)
    for codepoint, glyph_name in cmap.items():
        char = chr(codepoint)
        if char not in CHARSET:
            new_cmap[codepoint] = glyph_name

    # Now remap scrambled characters
    for original_char, replacement_char in encode_map.items():
        original_codepoint = ord(original_char)
        replacement_codepoint = ord(replacement_char)

        # Get the glyph for the ORIGINAL character
        if original_codepoint in cmap:
            glyph_name = cmap[original_codepoint]
            # Map REPLACEMENT codepoint to ORIGINAL glyph
            new_cmap[replacement_codepoint] = glyph_name

    # Update only format 4 cmap tables (Windows Unicode BMP)
    # Format 4 is the standard format used by browsers
    # Avoid format 6 which has a 16-bit length limitation
    for table in font['cmap'].tables:
        if hasattr(table, 'cmap') and table.format == 4:
            table.cmap = new_cmap.copy()

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save as WOFF2
    font.flavor = 'woff2'
    font.save(str(output_path))
    font.close()

    # Save encoding map as JSON if requested
    if save_map:
        map_path = output_path.with_name(output_path.stem + '_map.json')
        with open(map_path, 'w') as f:
            json.dump(encode_map, f, indent=2)

    return encode_map
