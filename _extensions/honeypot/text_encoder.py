"""Text encoder for anti-AI font obfuscation.

Transforms plaintext to encoded text using the font's encoding map.
The scrambled font renders the encoded text as readable.

Example:
    encoder = TextEncoder(map_path_or_dict)
    encoded = encoder.encode('hello')  # Returns 'xqnns' or similar
    decoded = encoder.decode(encoded)  # Returns 'hello'
"""

import json
from pathlib import Path

__all__ = ['TextEncoder']


class TextEncoder:
    """Encode/decode text using a character mapping.

    The encoding map transforms plaintext to scrambled text that,
    when rendered with the corresponding scrambled font, displays
    as the original text.
    """

    def __init__(self, map_source: Path | str | dict):
        """Initialize encoder with encoding map.

        Args:
            map_source: Either:
                - Path to JSON file containing encoding map
                - String path to JSON file
                - Dict with the encoding map directly
        """
        if isinstance(map_source, dict):
            self.encode_map = map_source
        else:
            map_path = Path(map_source)
            with open(map_path) as f:
                self.encode_map = json.load(f)

        # Build reverse map for decoding
        self.decode_map = {v: k for k, v in self.encode_map.items()}

    def encode(self, plaintext: str) -> str:
        """Transform readable text to scrambled text.

        Characters in the encoding map are replaced with their
        mapped values. Other characters (spaces, punctuation)
        pass through unchanged.

        Args:
            plaintext: Human-readable text to encode

        Returns:
            Encoded text that looks like gibberish but renders
            correctly with the scrambled font
        """
        result = []
        for char in plaintext:
            if char in self.encode_map:
                result.append(self.encode_map[char])
            else:
                # Punctuation, spaces, etc. pass through unchanged
                result.append(char)
        return ''.join(result)

    def decode(self, encoded: str) -> str:
        """Reverse transform for testing/debugging.

        Args:
            encoded: Scrambled text from encode()

        Returns:
            Original plaintext
        """
        result = []
        for char in encoded:
            if char in self.decode_map:
                result.append(self.decode_map[char])
            else:
                result.append(char)
        return ''.join(result)
