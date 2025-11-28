---
category: Infrastructure
---

# Cloudflare Pages Deployment

This site is deployed to [Cloudflare Pages](https://pages.cloudflare.com/) with automatic builds on push to `main`.

## Build Configuration

### Dashboard Settings

| Setting | Value |
|---------|-------|
| **Build command** | `pip install pipenv && pipenv install --deploy && pipenv run sphinx-build -b html . _build/html` |
| **Build output directory** | `_build/html` |
| **Root directory** | *(empty)* |

### Environment Variables

| Variable | Value |
|----------|-------|
| `PYTHON_VERSION` | `3.13` |

## How It Works

1. Push to `main` branch triggers Cloudflare Pages build
2. Cloudflare installs pipenv and dependencies from `Pipfile.lock`
3. Sphinx builds the site to `_build/html`
4. Site is deployed to Cloudflare's edge network

## Dependency Management

We use **pipenv** for reproducible builds:

- `Pipfile` - declares dependencies
- `Pipfile.lock` - locks exact versions (cached between builds)

The `--deploy` flag ensures Cloudflare uses the exact locked versions.

## Local Development

Local development uses **mise** instead of pipenv:

```bash
# One-time build
mise run build

# Live preview with auto-reload
mise run preview
```

Mise uses the local `.venv/` while CI uses pipenv - same packages, different tooling.

## Private Notes

The `private/` directory is:

- Excluded from Sphinx builds via `exclude_patterns` in `conf.py`
- Ignored by git via `.gitignore`
- Never published to Cloudflare Pages

Use this for personal notes not intended for publication.

## File Structure

```
rstnotes/
├── Pipfile              # CI dependencies
├── Pipfile.lock         # Locked versions
├── mise.toml            # Local dev tasks
├── conf.py              # Sphinx configuration
├── index.md             # Site root
├── private/             # Never published
└── _build/html/         # Build output
```

## Troubleshooting

### Build fails with dependency error

Regenerate the lock file:

```bash
pipenv lock
git add Pipfile.lock
git commit -m "chore: update Pipfile.lock"
git push
```

### Python version mismatch

Ensure `PYTHON_VERSION` environment variable matches `Pipfile`:

```toml
[requires]
python_version = "3.13"
```
