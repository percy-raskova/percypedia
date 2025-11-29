#!/bin/bash
# Cloudflare Pages build script for PercyBrain
# Uses Pipfile.ci (minimal deps) for fast CI builds
#
# For local development, use: mise run build

set -e  # Exit on error

echo "==> Installing pipenv..."
pip install pipenv

echo "==> Installing minimal build dependencies from Pipfile.ci..."
export PIPENV_PIPFILE=Pipfile.ci
pipenv install --deploy

echo "==> Building Sphinx documentation..."
pipenv run sphinx-build -b html content _build/html

echo "==> Build complete! Output in _build/html"
