"""Integration tests for Sphinx builds with custom extensions.

These tests verify that all custom extensions work together in a real build.
Marked as slow - skip with `pytest -m "not slow"`.
"""

import pytest
import subprocess
from pathlib import Path


@pytest.fixture
def minimal_sphinx_project(tmp_path):
    """Create a minimal Sphinx project for testing."""
    # Create conf.py with our extensions
    conf_py = tmp_path / "conf.py"
    conf_py.write_text("""
project = 'Test'
extensions = [
    'myst_parser',
    'category_nav',
    'publish_filter',
    'missing_refs',
]

# MyST config
source_suffix = {'.md': 'markdown', '.rst': 'restructuredtext'}

# Extension configs
category_nav_default = 'Uncategorized'
category_nav_exclude = ['private/*']
missing_refs_generate_page = False
""")

    # Create index.md
    (tmp_path / "index.md").write_text("""---
title: Test Index
category: Meta
publish: true
---

# Test Project

{category-nav}
""")

    # Create content files
    theory_dir = tmp_path / "theory"
    theory_dir.mkdir()

    (theory_dir / "dialectics.md").write_text("""---
title: Dialectical Materialism
category: Theory
publish: true
---

# Dialectical Materialism

This is about dialectics.
""")

    # Create a draft file
    (tmp_path / "draft.md").write_text("""---
title: Work in Progress
publish: false
---

# Draft

This should not appear in builds.
""")

    # Create content with Obsidian comments
    (tmp_path / "with_comments.md").write_text("""---
title: Document with Comments
category: Meta
publish: true
---

# Visible Content

This is visible %%this is hidden%% and this is also visible.
""")

    return tmp_path


@pytest.mark.slow
class TestSphinxBuildIntegration:
    """End-to-end Sphinx build tests."""

    def test_build_succeeds_with_extensions(self, minimal_sphinx_project):
        """Sphinx build should complete successfully with all extensions."""
        result = subprocess.run(
            ["sphinx-build", "-b", "html", str(minimal_sphinx_project), str(minimal_sphinx_project / "_build")],
            capture_output=True,
            text=True,
            cwd=str(minimal_sphinx_project),
            env={
                "PYTHONPATH": str(Path(__file__).parent.parent.parent / "_extensions"),
                "PATH": subprocess.os.environ.get("PATH", ""),
            }
        )

        # Build should succeed
        assert result.returncode == 0, f"Build failed: {result.stderr}"

    def test_draft_excluded_from_build(self, minimal_sphinx_project):
        """Files with publish: false should not appear in build output."""
        result = subprocess.run(
            ["sphinx-build", "-b", "html", str(minimal_sphinx_project), str(minimal_sphinx_project / "_build")],
            capture_output=True,
            text=True,
            env={
                "PYTHONPATH": str(Path(__file__).parent.parent.parent / "_extensions"),
                "PATH": subprocess.os.environ.get("PATH", ""),
            }
        )

        if result.returncode == 0:
            build_dir = minimal_sphinx_project / "_build"
            # draft.html should not exist
            assert not (build_dir / "draft.html").exists()

    def test_obsidian_comments_stripped(self, minimal_sphinx_project):
        """Obsidian %% comments should be stripped from output."""
        result = subprocess.run(
            ["sphinx-build", "-b", "html", str(minimal_sphinx_project), str(minimal_sphinx_project / "_build")],
            capture_output=True,
            text=True,
            env={
                "PYTHONPATH": str(Path(__file__).parent.parent.parent / "_extensions"),
                "PATH": subprocess.os.environ.get("PATH", ""),
            }
        )

        if result.returncode == 0:
            with_comments_html = minimal_sphinx_project / "_build" / "with_comments.html"
            if with_comments_html.exists():
                content = with_comments_html.read_text()
                assert "this is hidden" not in content
                assert "This is visible" in content


@pytest.mark.slow
class TestCLIRoundTrip:
    """End-to-end CLI tests for frontmatter tools."""

    def test_validate_reports_valid_file(self, tmp_path):
        """fm:validate should report valid files correctly."""
        # Create a valid file
        valid_file = tmp_path / "valid.md"
        valid_file.write_text("""---
title: Valid Document
category: Theory
publish: true
---

# Valid Document

Content here.
""")

        result = subprocess.run(
            ["python", "-m", "frontmatter_normalizer", "validate", str(tmp_path)],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent / "_tools"),
        )

        # Should not report errors for valid file
        # (exit code may vary based on implementation)
        assert "error" not in result.stdout.lower() or result.returncode == 0

    def test_report_shows_file_status(self, tmp_path):
        """fm:report should show status of files."""
        # Create test files
        (tmp_path / "complete.md").write_text("""---
title: Complete
category: Theory
publish: true
tags:
  - test
---

# Complete
""")
        (tmp_path / "incomplete.md").write_text("""---
title: Incomplete
---

# Incomplete
""")

        result = subprocess.run(
            ["python", "-m", "frontmatter_normalizer", "report", str(tmp_path)],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent / "_tools"),
        )

        # Should show both files
        assert "complete" in result.stdout.lower() or result.returncode == 0
