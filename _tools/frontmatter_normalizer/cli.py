"""CLI interface for frontmatter normalizer.

Commands:
- normalize: Normalize frontmatter in files/directories
- report: Generate summary report
- validate: Check files against schema
"""

import fnmatch
import json
import sys
from pathlib import Path
from typing import List

import click

from .config import DEFAULT_EXCLUDE_PATTERNS
from .normalizer import Normalizer, NormalizationResult
from .parser import parse_file
from .writer import render_frontmatter, write_file


__version__ = "0.1.0"


def _matches_exclusion(rel_path: str, patterns: List[str]) -> bool:
    """Check if a relative path matches any exclusion pattern.

    Patterns support:
    - Directory prefixes: '_build' matches '_build/' and '_build/anything'
    - Wildcards: '*.pyc' matches any .pyc file
    - Glob patterns: '_build/*' matches anything in _build/
    """
    for pattern in patterns:
        # Directory pattern (e.g., '_build', '_build/*')
        if pattern.endswith('/*'):
            dir_prefix = pattern[:-2]
            if rel_path.startswith(dir_prefix + '/') or rel_path == dir_prefix:
                return True
        # File extension pattern (e.g., '*.pyc')
        elif pattern.startswith('*.'):
            if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(rel_path.split('/')[-1], pattern):
                return True
        # Exact match or directory prefix
        elif rel_path.startswith(pattern + '/') or rel_path == pattern:
            return True
        # General fnmatch pattern
        elif fnmatch.fnmatch(rel_path, pattern):
            return True

    return False


def find_markdown_files(
    path: Path,
    exclude_patterns: List[str],
) -> List[Path]:
    """Find all markdown files in a directory, respecting exclusions.

    Args:
        path: File or directory to search
        exclude_patterns: List of patterns to exclude (supports fnmatch globs)

    Returns:
        Sorted list of markdown file paths
    """
    path = Path(path)

    if path.is_file():
        return [path] if path.suffix == '.md' else []

    files = []
    for md_file in path.rglob('*.md'):
        rel_path = str(md_file.relative_to(path))
        if not _matches_exclusion(rel_path, exclude_patterns):
            files.append(md_file)

    return sorted(files)


@click.group()
@click.version_option(version=__version__)
def main():
    """Frontmatter normalizer - normalize YAML frontmatter in markdown files."""
    pass


@main.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--dry-run', is_flag=True, help='Show changes without writing')
@click.option('--no-backup', is_flag=True, help='Skip creating .bak files')
@click.option('--exclude', multiple=True, help='Additional exclusion patterns')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed output')
@click.option('--quiet', '-q', is_flag=True, help='Minimal output')
def normalize(
    path: str,
    dry_run: bool,
    no_backup: bool,
    exclude: tuple,
    verbose: bool,
    quiet: bool,
):
    """Normalize frontmatter in markdown files.

    PATH can be a file or directory.
    """
    path = Path(path)

    # Combine exclusion patterns
    exclude_patterns = DEFAULT_EXCLUDE_PATTERNS + list(exclude)

    # Find files
    files = find_markdown_files(path, exclude_patterns)

    if not files:
        if not quiet:
            click.echo("No markdown files found.")
        return

    normalizer = Normalizer()

    changed_count = 0
    review_count = 0

    for filepath in files:
        try:
            content = filepath.read_text(encoding='utf-8')
            result = normalizer.normalize(content, filepath)

            if result.changed:
                changed_count += 1

                if verbose:
                    rel_path = filepath.relative_to(path) if path.is_dir() else filepath.name
                    click.echo(f"\n{rel_path}:")
                    click.echo(f"  Inferred: {', '.join(result.inferred_fields)}")
                    if result.needs_review:
                        click.echo("  ⚠️  Needs review")

                if not dry_run:
                    write_file(
                        filepath,
                        result.frontmatter,
                        result.body,
                        backup=not no_backup,
                    )

            if result.needs_review:
                review_count += 1

        except Exception as e:
            if not quiet:
                click.echo(f"Warning: Error processing {filepath}: {e}", err=True)

    # Summary
    if not quiet:
        if dry_run:
            click.echo(f"\nDry run: {changed_count} files would be changed")
        else:
            click.echo(f"\n{changed_count} files processed")

        if review_count > 0:
            click.echo(f"{review_count} files need review")


@main.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--needs-review', is_flag=True, help='Only show files needing review')
@click.option('--json', 'json_output', is_flag=True, help='Output as JSON')
@click.option('--exclude', multiple=True, help='Additional exclusion patterns')
def report(
    path: str,
    needs_review: bool,
    json_output: bool,
    exclude: tuple,
):
    """Generate a report on frontmatter status.

    PATH can be a file or directory.
    """
    path = Path(path)
    exclude_patterns = DEFAULT_EXCLUDE_PATTERNS + list(exclude)
    files = find_markdown_files(path, exclude_patterns)

    normalizer = Normalizer()

    report_data = {
        'total': len(files),
        'compliant': 0,
        'needs_normalization': 0,
        'needs_review': 0,
        'files': [],
    }

    for filepath in files:
        try:
            content = filepath.read_text(encoding='utf-8')
            result = normalizer.normalize(content, filepath)

            rel_path = str(filepath.relative_to(path) if path.is_dir() else filepath.name)

            file_info = {
                'path': rel_path,
                'changed': result.changed,
                'needs_review': result.needs_review,
                'inferred_fields': result.inferred_fields,
            }

            if result.changed:
                report_data['needs_normalization'] += 1
            else:
                report_data['compliant'] += 1

            if result.needs_review:
                report_data['needs_review'] += 1

            if not needs_review or result.needs_review:
                report_data['files'].append(file_info)

        except Exception as e:
            report_data['files'].append({
                'path': str(filepath),
                'error': str(e),
            })

    if json_output:
        click.echo(json.dumps(report_data, indent=2))
    else:
        click.echo(f"Total files: {report_data['total']}")
        click.echo(f"Compliant: {report_data['compliant']}")
        click.echo(f"Needs normalization: {report_data['needs_normalization']}")
        click.echo(f"Needs review: {report_data['needs_review']}")

        if needs_review and report_data['files']:
            click.echo("\nFiles needing review:")
            for f in report_data['files']:
                click.echo(f"  - {f['path']}")


@main.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--exclude', multiple=True, help='Additional exclusion patterns')
def validate(
    path: str,
    exclude: tuple,
):
    """Validate files against the frontmatter schema.

    PATH can be a file or directory.
    """
    from .config import SCHEMA_FIELDS, VALID_CATEGORIES

    path = Path(path)
    exclude_patterns = DEFAULT_EXCLUDE_PATTERNS + list(exclude)
    files = find_markdown_files(path, exclude_patterns)

    valid_count = 0
    invalid_count = 0

    for filepath in files:
        try:
            frontmatter, _ = parse_file(filepath)
            issues = []

            # Check for non-schema fields
            for key in frontmatter:
                if key not in SCHEMA_FIELDS:
                    issues.append(f"Unknown field: {key}")

            # Check category validity
            if 'category' in frontmatter:
                if frontmatter['category'] not in VALID_CATEGORIES:
                    issues.append(f"Invalid category: {frontmatter['category']}")

            # Check tags format
            if 'tags' in frontmatter:
                if not isinstance(frontmatter['tags'], list):
                    issues.append("Tags should be a list")

            if issues:
                invalid_count += 1
                rel_path = filepath.relative_to(path) if path.is_dir() else filepath.name
                click.echo(f"\n{rel_path}:")
                for issue in issues:
                    click.echo(f"  - {issue}")
            else:
                valid_count += 1

        except Exception as e:
            invalid_count += 1
            click.echo(f"\n{filepath}: Error - {e}")

    click.echo(f"\n{valid_count} valid, {invalid_count} invalid")

    if invalid_count > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
