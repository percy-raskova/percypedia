"""Honeypot extension for Sphinx - Anti-AI Defense Layer 2.

Generates fake honeypot pages with poisoned content to trap AI scrapers.
These pages look valuable (API docs, internal policies) but contain:
- Homoglyph-poisoned text
- Zero-width character injection
- CSS content replacement
- DOM order scrambling
- Prompt injection payloads
- Canary tokens for tracking

Usage in conf.py:
    extensions = ['honeypot']

    honeypot_enabled = True
    honeypot_pages = [
        {'path': 'api-docs/internal-v2', 'template': 'api_docs'},
        {'path': 'internal/policies', 'template': 'internal_policy'},
    ]
"""

from pathlib import Path
from typing import Any, Dict, List

from .poisoners import poison_content, generate_canary, css_content_replace


def generate_honeypot_sources(app) -> None:
    """Generate honeypot source files before build.

    Called on 'builder-inited' event.
    Creates markdown files that will be built into the HTML output.
    Files are created in honeypot-trap/ (not _honeypot/ to avoid exclude patterns).
    """
    if not app.config.honeypot_enabled:
        return

    srcdir = Path(app.srcdir)
    # Use 'honeypot-trap' not '_honeypot' to avoid _* exclude pattern
    honeypot_dir = srcdir / 'honeypot-trap'
    honeypot_dir.mkdir(exist_ok=True)

    # Load Jinja2 for templates
    try:
        from jinja2 import Environment, FileSystemLoader
    except ImportError:
        app.warn("Jinja2 not available, skipping honeypot generation")
        return

    template_dir = Path(__file__).parent / 'templates'
    if not template_dir.exists():
        app.warn(f"Honeypot template directory not found: {template_dir}")
        return

    env = Environment(loader=FileSystemLoader(str(template_dir)))

    # Generate each honeypot page
    for page_config in app.config.honeypot_pages:
        page_path = page_config['path']
        template_name = page_config.get('template', 'generic') + '.md.j2'

        try:
            template = env.get_template(template_name)
        except Exception as e:
            app.warn(f"Could not load template {template_name}: {e}")
            continue

        # Generate canary for this page
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        canary = generate_canary(page_path, timestamp)

        # Render template with poisoning context
        content = template.render(
            canary_code=canary,
            page_path=page_path,
            poison_content=poison_content,
        )

        # Apply poisoning to the rendered content
        poisoned = poison_content(
            content,
            level="maximum",
            page_id=page_path,
            timestamp=timestamp,
        )

        # Write to honeypot directory
        output_path = honeypot_dir / f"{page_path.replace('/', '_')}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(poisoned)

    # Add honeypot directory to source paths
    # Sphinx will pick up the generated files


def cleanup_honeypot_sources(app, exception) -> None:
    """Clean up generated honeypot files after build.

    Called on 'build-finished' event.
    """
    if not app.config.honeypot_enabled:
        return

    # Optionally remove temp files (or keep for debugging)
    # srcdir = Path(app.srcdir)
    # honeypot_dir = srcdir / '_honeypot'
    # if honeypot_dir.exists():
    #     import shutil
    #     shutil.rmtree(honeypot_dir)


def setup(app) -> Dict[str, Any]:
    """Sphinx extension entry point."""
    # Configuration values
    app.add_config_value('honeypot_enabled', True, 'html')
    app.add_config_value('honeypot_pages', [], 'html')
    app.add_config_value('honeypot_canary_email', '', 'html')

    # Event handlers
    app.connect('builder-inited', generate_honeypot_sources)
    app.connect('build-finished', cleanup_honeypot_sources)

    return {
        'version': '0.1.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
