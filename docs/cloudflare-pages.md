---
category: Meta
---

# Cloudflare Pages Deployment

This site is deployed to [Cloudflare Pages](https://pages.cloudflare.com/) with automatic builds on push to `main`.

## Build Configuration

### Dashboard Settings

| Setting | Value |
|---------|-------|
| **Build command** | `./build.sh` |
| **Build output directory** | `_build/html` |
| **Root directory** | *(empty)* |

### Environment Variables

| Variable | Value |
|----------|-------|
| `PYTHON_VERSION` | `3.13` |

## How It Works

1. Push to `main` branch triggers Cloudflare Pages build
2. `build.sh` installs pipenv and minimal dependencies from `Pipfile.ci`
3. Sphinx builds the site to `_build/html`
4. Site is deployed to Cloudflare's edge network

## Dependency Management

We use a **dual-Pipfile strategy** for fast CI builds:

| File | Purpose | Contents |
|------|---------|----------|
| `Pipfile` | Full development | Sphinx + SpaCy + ML tools |
| `Pipfile.ci` | CI builds only | Sphinx (minimal) |
| `Pipfile.lock` | Dev lock file | All dependencies locked |
| `Pipfile.ci.lock` | CI lock file | Minimal dependencies locked |

The `build.sh` script uses `PIPENV_PIPFILE=Pipfile.ci` to install only what's needed for building the site, skipping heavy ML dependencies (~800MB) that are only used for the frontmatter normalizer tool.

## Local Development

Local development uses **mise** instead of pipenv:

```bash
# One-time build
mise run build

# Live preview with auto-reload
mise run preview
```

Mise uses the local `.venv/` with full dependencies, while CI uses the minimal `Pipfile.ci`.

## Private Notes

The `private/` directory is:

- Excluded from Sphinx builds via `exclude_patterns` in `conf.py`
- Ignored by git via `.gitignore`
- Never published to Cloudflare Pages

Use this for personal notes not intended for publication.

## File Structure

```
rstnotes/
├── build.sh             # CI build script (uses Pipfile.ci)
├── Pipfile              # Full dev dependencies (SpaCy, ML)
├── Pipfile.lock         # Full dependencies locked
├── Pipfile.ci           # Minimal CI dependencies (Sphinx only)
├── Pipfile.ci.lock      # CI dependencies locked
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
