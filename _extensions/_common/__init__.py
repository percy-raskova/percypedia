"""Shared utilities for Sphinx extensions.

Exports:
    - collector: BaseCollector, CollectorEntry, make_merge_handler
    - directive_utils: build_header_node, build_content_section, ensure_env_storage
    - file_ops: compute_docname, read_markdown_file, write_json_file, write_text_file
    - frontmatter: extract_frontmatter, parse_frontmatter
    - nodes: create_node_class, create_div_visitors, make_container_node
    - traversal: iter_markdown_files
"""

# Core utilities (original)
from .frontmatter import extract_frontmatter, parse_frontmatter
from .traversal import iter_markdown_files

# New foundation layer
from .collector import BaseCollector, CollectorEntry, make_merge_handler
from .directive_utils import build_content_section, build_header_node, ensure_env_storage
from .file_ops import compute_docname, read_markdown_file, write_json_file, write_text_file
from .nodes import create_div_visitors, create_node_class, make_container_node

__all__ = [
    # Collector
    'BaseCollector',
    'CollectorEntry',
    'make_merge_handler',
    # Directive utilities
    'build_content_section',
    'build_header_node',
    'ensure_env_storage',
    # File operations
    'compute_docname',
    'read_markdown_file',
    'write_json_file',
    'write_text_file',
    # Frontmatter (original)
    'extract_frontmatter',
    'parse_frontmatter',
    # Node utilities
    'create_div_visitors',
    'create_node_class',
    'make_container_node',
    # Traversal (original)
    'iter_markdown_files',
]
