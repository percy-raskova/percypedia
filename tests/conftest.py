"""Root conftest - establishes pytest fixture hierarchy for all tests."""

# This file establishes the conftest chain for pytest fixture discovery.
# Fixtures are organized hierarchically:
#   tests/conftest.py (this file) - universal fixtures (none currently)
#   tests/extensions/conftest.py - Sphinx extension fixtures
#   tests/tools/conftest.py - Tool fixtures (non-ML)
#   tests/tools/normalizer/conftest.py - Session-scoped ML fixtures
