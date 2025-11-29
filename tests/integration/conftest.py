"""Fixtures for integration tests."""

import pytest
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
EXTENSIONS_DIR = PROJECT_ROOT / '_extensions'
TOOLS_DIR = PROJECT_ROOT / '_tools'
