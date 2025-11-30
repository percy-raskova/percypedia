"""Shared testing utilities for Sphinx extensions.

Provides mock factories and fixtures for testing directive-based extensions.

Usage:
    from _common.testing import make_mock_app, make_mock_env, make_mock_directive
"""

from .mocks import (
    make_mock_app,
    make_mock_directive,
    make_mock_env,
    make_mock_inliner,
)

__all__ = [
    'make_mock_app',
    'make_mock_directive',
    'make_mock_env',
    'make_mock_inliner',
]
