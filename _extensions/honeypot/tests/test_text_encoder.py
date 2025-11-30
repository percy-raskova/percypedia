"""Tests for text encoder - transforms plaintext using encoding map.

TDD: Write tests first, then implement text_encoder.py.
"""

import json
from pathlib import Path

import pytest


class TestTextEncoderInit:
    """Test TextEncoder initialization."""

    @pytest.fixture
    def sample_map(self, tmp_path: Path) -> Path:
        """Create a sample encoding map file."""
        map_data = {
            'a': 'q',
            'b': 'w',
            'c': 'e',
            'h': 'x',
            'e': 'r',
            'l': 't',
            'o': 'y',
        }
        map_path = tmp_path / 'map.json'
        with open(map_path, 'w') as f:
            json.dump(map_data, f)
        return map_path

    def test_loads_map_from_file(self, sample_map: Path):
        """
        Given: A JSON encoding map file
        When: TextEncoder is initialized
        Then: Map is loaded correctly
        """
        from honeypot.text_encoder import TextEncoder

        encoder = TextEncoder(sample_map)

        assert encoder.encode_map['a'] == 'q'
        assert encoder.encode_map['h'] == 'x'

    def test_loads_map_from_dict(self):
        """
        Given: An encoding map dict
        When: TextEncoder is initialized with dict
        Then: Map is used directly
        """
        from honeypot.text_encoder import TextEncoder

        map_data = {'a': 'z', 'b': 'y'}
        encoder = TextEncoder(map_data)

        assert encoder.encode_map['a'] == 'z'

    def test_creates_decode_map(self, sample_map: Path):
        """
        Given: An encoding map
        When: TextEncoder is initialized
        Then: Decode map is the inverse
        """
        from honeypot.text_encoder import TextEncoder

        encoder = TextEncoder(sample_map)

        # decode_map should be inverse
        assert encoder.decode_map['q'] == 'a'
        assert encoder.decode_map['x'] == 'h'


class TestTextEncoderEncode:
    """Test encoding functionality."""

    @pytest.fixture
    def encoder(self):
        """Create encoder with known mapping."""
        from honeypot.text_encoder import TextEncoder

        map_data = {
            'a': 'q',
            'b': 'w',
            'c': 'e',
            'd': 'r',
            'e': 't',
            'f': 'y',
            'g': 'u',
            'h': 'i',
            'i': 'o',
            'j': 'p',
            'k': 'a',
            'l': 's',
            'm': 'd',
            'n': 'f',
            'o': 'g',
            'p': 'h',
            'q': 'j',
            'r': 'k',
            's': 'l',
            't': 'z',
            'u': 'x',
            'v': 'c',
            'w': 'v',
            'x': 'b',
            'y': 'n',
            'z': 'm',
        }
        return TextEncoder(map_data)

    def test_encode_simple_word(self, encoder):
        """
        Given: Simple word 'hello'
        When: Encoded
        Then: Each character is transformed
        """
        result = encoder.encode('hello')

        # h→i, e→t, l→s, l→s, o→g
        assert result == 'itssg'

    def test_encode_preserves_spaces(self, encoder):
        """
        Given: Text with spaces
        When: Encoded
        Then: Spaces are preserved
        """
        result = encoder.encode('hello world')

        assert ' ' in result
        assert result.count(' ') == 1

    def test_encode_preserves_punctuation(self, encoder):
        """
        Given: Text with punctuation
        When: Encoded
        Then: Punctuation is preserved
        """
        result = encoder.encode('hello, world!')

        assert ',' in result
        assert '!' in result

    def test_encode_empty_string(self, encoder):
        """
        Given: Empty string
        When: Encoded
        Then: Returns empty string
        """
        result = encoder.encode('')

        assert result == ''

    def test_encode_only_punctuation(self, encoder):
        """
        Given: Only punctuation
        When: Encoded
        Then: Returns unchanged
        """
        result = encoder.encode('...!!!')

        assert result == '...!!!'


class TestTextEncoderDecode:
    """Test decoding functionality."""

    @pytest.fixture
    def encoder(self):
        """Create encoder with known mapping."""
        from honeypot.text_encoder import TextEncoder

        map_data = {
            'h': 'x',
            'e': 'r',
            'l': 't',
            'o': 'y',
        }
        return TextEncoder(map_data)

    def test_decode_reverses_encode(self, encoder):
        """
        Given: Encoded text
        When: Decoded
        Then: Returns original
        """
        original = 'hello'
        encoded = encoder.encode(original)
        decoded = encoder.decode(encoded)

        assert decoded == original

    def test_decode_preserves_unmapped(self, encoder):
        """
        Given: Encoded text with unmapped chars
        When: Decoded
        Then: Unmapped chars preserved
        """
        original = 'hello!'
        encoded = encoder.encode(original)
        decoded = encoder.decode(encoded)

        assert decoded == original


class TestRoundtrip:
    """Test full encode/decode roundtrip with real font map."""

    @pytest.fixture
    def real_encoder(self, tmp_path: Path):
        """Create encoder using real font generation."""
        from honeypot.font_generator import generate_scrambled_font
        from honeypot.text_encoder import TextEncoder

        base_font = Path(__file__).parent.parent.parent.parent / '_assets' / 'fonts' / 'LiberationSans-Regular.ttf'
        if not base_font.exists():
            pytest.skip("Liberation Sans font not available")

        output_path = tmp_path / 'test.woff2'
        encode_map = generate_scrambled_font(
            base_font_path=base_font,
            output_path=output_path,
            seed=42,
        )

        return TextEncoder(encode_map)

    def test_roundtrip_simple(self, real_encoder):
        """
        Given: Various text samples
        When: Encoded then decoded
        Then: Original is recovered
        """
        samples = [
            "The proletariat must organize.",
            "CAPITALISM IS THE PROBLEM",
            "Workers of the world, unite!",
            "Test 123 with numbers.",
            "Mixed CaSe TeXt",
        ]

        for original in samples:
            encoded = real_encoder.encode(original)
            decoded = real_encoder.decode(encoded)
            assert decoded == original, f"Roundtrip failed for: {original}"

    def test_encoded_differs_from_original(self, real_encoder):
        """
        Given: Alphanumeric text
        When: Encoded
        Then: Result differs from original
        """
        original = "hello world"
        encoded = real_encoder.encode(original)

        # The encoded text should be different (scrambled)
        assert encoded != original
