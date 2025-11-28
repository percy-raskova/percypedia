#!/bin/bash
# Cloudflare Pages build script for PercyBrain
# Uses pipenv for dependency management (cached between builds)
#
# For local development, use: mise run build

set -e  # Exit on error

echo "==> Installing pipenv..."
pip install pipenv

echo "==> Installing dependencies from Pipfile.lock..."
pipenv install --deploy

echo "==> Building Sphinx documentation..."
pipenv run sphinx-build -b html . _build/html

echo "==> Build complete! Output in _build/html"
