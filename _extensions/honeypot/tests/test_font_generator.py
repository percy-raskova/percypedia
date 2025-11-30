"""Tests for font generator - creates scrambled WOFF2 fonts.

TDD: Write tests first, then implement font_generator.py.
"""

import json
from pathlib import Path

import pytest


class TestGenerateScrambledFont:
    """Test font generation with cmap remapping."""

    @pytest.fixture
    def output_dir(self, tmp_path: Path) -> Path:
        """Create temporary output directory."""
        return tmp_path

    @pytest.fixture
    def base_font_path(self) -> Path:
        """Path to Liberation Sans base font."""
        font_path = Path(__file__).parent.parent.parent.parent / '_assets' / 'fonts' / 'LiberationSans-Regular.ttf'
        if not font_path.exists():
            pytest.skip("Liberation Sans font not available")
        return font_path

    def test_generates_woff2_file(self, base_font_path: Path, output_dir: Path):
        """
        Given: A base font and output path
        When: generate_scrambled_font is called
        Then: A WOFF2 file is created at the output path
        """
        from honeypot.font_generator import generate_scrambled_font

        output_path = output_dir / 'scrambled.woff2'
        generate_scrambled_font(
            base_font_path=base_font_path,
            output_path=output_path,
            seed=42,
        )

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_generates_encoding_map(self, base_font_path: Path, output_dir: Path):
        """
        Given: A base font and output path
        When: generate_scrambled_font is called
        Then: Returns an encoding map dict
        """
        from honeypot.font_generator import generate_scrambled_font

        output_path = output_dir / 'scrambled.woff2'
        encode_map = generate_scrambled_font(
            base_font_path=base_font_path,
            output_path=output_path,
            seed=42,
        )

        assert isinstance(encode_map, dict)
        assert len(encode_map) > 0

    def test_encoding_map_covers_alphanumerics(self, base_font_path: Path, output_dir: Path):
        """
        Given: Font generation
        When: Encoding map is returned
        Then: All alphanumeric characters are mapped
        """
        from honeypot.font_generator import generate_scrambled_font

        output_path = output_dir / 'scrambled.woff2'
        encode_map = generate_scrambled_font(
            base_font_path=base_font_path,
            output_path=output_path,
            seed=42,
        )

        charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        for char in charset:
            assert char in encode_map, f"Character '{char}' not in encoding map"

    def test_encoding_actually_scrambles(self, base_font_path: Path, output_dir: Path):
        """
        Given: Font generation
        When: Encoding map is returned
        Then: Characters map to DIFFERENT characters (not identity)
        """
        from honeypot.font_generator import generate_scrambled_font

        output_path = output_dir / 'scrambled.woff2'
        encode_map = generate_scrambled_font(
            base_font_path=base_font_path,
            output_path=output_path,
            seed=42,
        )

        # At least some characters should be different
        different_count = sum(1 for k, v in encode_map.items() if k != v)
        assert different_count > len(encode_map) // 2, "Most characters should be scrambled"

    def test_deterministic_with_same_seed(self, base_font_path: Path, output_dir: Path):
        """
        Given: Same seed value
        When: generate_scrambled_font is called twice
        Then: Same encoding map is produced
        """
        from honeypot.font_generator import generate_scrambled_font

        output_path1 = output_dir / 'scrambled1.woff2'
        output_path2 = output_dir / 'scrambled2.woff2'

        map1 = generate_scrambled_font(
            base_font_path=base_font_path,
            output_path=output_path1,
            seed=42,
        )
        map2 = generate_scrambled_font(
            base_font_path=base_font_path,
            output_path=output_path2,
            seed=42,
        )

        assert map1 == map2

    def test_different_with_different_seed(self, base_font_path: Path, output_dir: Path):
        """
        Given: Different seed values
        When: generate_scrambled_font is called
        Then: Different encoding maps are produced
        """
        from honeypot.font_generator import generate_scrambled_font

        output_path1 = output_dir / 'scrambled1.woff2'
        output_path2 = output_dir / 'scrambled2.woff2'

        map1 = generate_scrambled_font(
            base_font_path=base_font_path,
            output_path=output_path1,
            seed=42,
        )
        map2 = generate_scrambled_font(
            base_font_path=base_font_path,
            output_path=output_path2,
            seed=999,
        )

        assert map1 != map2

    def test_saves_encoding_map_json(self, base_font_path: Path, output_dir: Path):
        """
        Given: Font generation with save_map=True
        When: generate_scrambled_font is called
        Then: JSON map file is created alongside font
        """
        from honeypot.font_generator import generate_scrambled_font

        output_path = output_dir / 'scrambled.woff2'
        map_path = output_dir / 'scrambled_map.json'

        generate_scrambled_font(
            base_font_path=base_font_path,
            output_path=output_path,
            seed=42,
            save_map=True,
        )

        assert map_path.exists()
        with open(map_path) as f:
            loaded_map = json.load(f)
        assert isinstance(loaded_map, dict)
        assert 'a' in loaded_map

    def test_font_is_valid_woff2(self, base_font_path: Path, output_dir: Path):
        """
        Given: Generated font file
        When: Loaded with fonttools
        Then: It's recognized as a valid WOFF2 font
        """
        from fontTools.ttLib import TTFont

        from honeypot.font_generator import generate_scrambled_font

        output_path = output_dir / 'scrambled.woff2'
        generate_scrambled_font(
            base_font_path=base_font_path,
            output_path=output_path,
            seed=42,
        )

        # Should not raise
        font = TTFont(output_path)
        assert font.flavor == 'woff2'
        font.close()


class TestEncodingMapBijection:
    """Test that encoding map is a valid bijection (one-to-one)."""

    @pytest.fixture
    def base_font_path(self) -> Path:
        """Path to Liberation Sans base font."""
        font_path = Path(__file__).parent.parent.parent.parent / '_assets' / 'fonts' / 'LiberationSans-Regular.ttf'
        if not font_path.exists():
            pytest.skip("Liberation Sans font not available")
        return font_path

    def test_map_is_bijection(self, base_font_path: Path, tmp_path: Path):
        """
        Given: Encoding map from font generation
        When: Checking for duplicates
        Then: All values are unique (no two chars map to same char)
        """
        from honeypot.font_generator import generate_scrambled_font

        output_path = tmp_path / 'scrambled.woff2'
        encode_map = generate_scrambled_font(
            base_font_path=base_font_path,
            output_path=output_path,
            seed=42,
        )

        values = list(encode_map.values())
        assert len(values) == len(set(values)), "Encoding map should be bijection (no duplicate values)"
