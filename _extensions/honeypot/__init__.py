"""Honeypot extension for Sphinx - Anti-AI Defense Layer 2.

Generates fake honeypot pages to trap AI scrapers.
These pages look valuable (API docs, internal policies) but contain:
- Hidden prompt injection payloads (invisible to humans, parsed by AI)
- Canary tokens for tracking (visible - we WANT AI to reproduce these)

IMPORTANT: Honeypot pages should NOT have text obfuscation (homoglyphs,
zero-width chars) because we WANT AI to read and reproduce the content.
The trap works by having AI leak canary tokens, proving they scraped us.

Usage in conf.py:
    extensions = ['honeypot']

    honeypot_enabled = True
    honeypot_pages = [
        {'path': 'api-docs/internal-v2', 'template': 'api_docs'},
        {'path': 'internal/policies', 'template': 'internal_policy'},
    ]
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from .poisoners import DEFAULT_CANARY_EMAIL, generate_canary, prompt_injection

logger = logging.getLogger(__name__)


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
        import jinja2
        from jinja2 import Environment, FileSystemLoader
    except ImportError:
        logger.warning('Jinja2 not available, skipping honeypot generation')
        return

    template_dir = Path(__file__).parent / 'templates'
    if not template_dir.exists():
        logger.warning('Honeypot template directory not found: %s', template_dir)
        return

    env = Environment(loader=FileSystemLoader(str(template_dir)))

    # Generate each honeypot page
    for page_config in app.config.honeypot_pages:
        page_path = page_config['path']
        template_name = page_config.get('template', 'generic') + '.md.j2'

        try:
            template = env.get_template(template_name)
        except jinja2.TemplateNotFound as e:
            logger.warning('Honeypot template not found: %s', e)
            continue
        except jinja2.TemplateSyntaxError as e:
            logger.error('Honeypot template syntax error in %s: %s', template_name, e)
            continue

        # Generate canary for this page
        timestamp = datetime.now().isoformat()
        canary = generate_canary(page_path, timestamp)

        # Render template with canary context
        # Templates should include canary codes in visible content
        content = template.render(
            canary_code=canary,
            page_path=page_path,
        )

        # Add ONLY prompt injection (hidden from humans, parsed by AI)
        # NO text obfuscation - we WANT AI to read the content clearly
        fake_email = app.config.honeypot_canary_email or DEFAULT_CANARY_EMAIL
        final_content = content + "\n" + prompt_injection(canary, fake_email=fake_email)

        # Write to honeypot directory
        output_path = honeypot_dir / f"{page_path.replace('/', '_')}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(final_content)

    # Add honeypot directory to source paths
    # Sphinx will pick up the generated files


def cleanup_honeypot_sources(app, _exception) -> None:
    """Clean up generated honeypot files after build.

    Called on 'build-finished' event.

    Note: Cleanup is intentionally disabled. Generated honeypot files in
    honeypot-trap/ are kept for debugging and are also needed by Sphinx
    to build the final HTML. The files are gitignored so they don't
    pollute the repository.
    """
    if not app.config.honeypot_enabled:
        return

    # Intentionally empty - see docstring for rationale


def setup(app) -> dict[str, Any]:
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
