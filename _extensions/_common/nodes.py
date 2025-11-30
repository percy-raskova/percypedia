"""Node factory functions for Sphinx extensions.

Provides utilities to create docutils nodes and HTML visitors
without repetitive boilerplate.

This is the single source of truth for node creation patterns.
"""

from collections.abc import Callable
from typing import Any

from docutils import nodes

__all__ = [
    'create_div_visitors',
    'create_node_class',
    'make_container_node',
]


def create_node_class(name: str, doc: str = "", module: str = "") -> type:
    """Factory for creating custom docutils node classes.

    Creates a node class that inherits from (nodes.General, nodes.Element).
    This is the standard pattern for container-like nodes.

    IMPORTANT: For Sphinx pickle support, the returned class must be assigned
    to a module-level variable with the same name. Sphinx serializes doctrees
    using pickle and needs to find the class by its __module__.__qualname__.

    Args:
        name: Class name for the node
        doc: Optional docstring
        module: Module name for pickle support (defaults to caller's module)

    Returns:
        A new node class

    Example:
        >>> # At module level:
        >>> my_node = create_node_class('my_node', 'A custom container node.', __name__)
        >>> # The variable name MUST match the class name for pickle to work
    """
    node_class = type(
        name,
        (nodes.General, nodes.Element),
        {'__doc__': doc or f'Custom {name} node.'}
    )
    # Set module for pickle support
    if module:
        node_class.__module__ = module
    return node_class


def create_div_visitors(
    tag: str = 'div',
    include_ids: bool = True,
    data_attrs: list[str] | None = None,
) -> tuple[Callable, Callable]:
    """Create standard HTML visitors for div-like container nodes.

    Creates a pair of visit/depart functions that render the node
    as an HTML element with classes, optional IDs, and optional data attributes.

    Args:
        tag: HTML tag to use (default: 'div')
        include_ids: Whether to include 'id' attribute from node['ids']
        data_attrs: List of node attributes to render as data-* attributes

    Returns:
        Tuple of (visit_function, depart_function)

    Example:
        >>> visit, depart = create_div_visitors(data_attrs=['sender'])
        >>> # In setup(): app.add_node(MyNode, html=(visit, depart))
    """
    def visit_html(self: Any, node: nodes.Element) -> None:
        """Render opening tag."""
        classes = ' '.join(node.get('classes', []))
        parts = [f'<{tag}']

        if classes:
            parts.append(f' class="{classes}"')

        if include_ids:
            ids = node.get('ids', [])
            if ids:
                parts.append(f' id="{ids[0]}"')

        if data_attrs:
            for attr in data_attrs:
                value = node.get(attr)
                if value is not None:
                    parts.append(f' data-{attr}="{value}"')

        parts.append('>')
        self.body.append(''.join(parts))

    def depart_html(self: Any, _node: nodes.Element) -> None:
        """Render closing tag."""
        self.body.append(f'</{tag}>')

    return visit_html, depart_html


def make_container_node(
    name: str,
    doc: str = "",
    tag: str = 'div',
    include_ids: bool = True,
    data_attrs: list[str] | None = None,
) -> tuple[type, dict[str, tuple[Callable, Callable]]]:
    """Create a container node class with matching HTML visitors.

    Convenience function that combines create_node_class and create_div_visitors.

    Args:
        name: Class name for the node
        doc: Optional docstring
        tag: HTML tag to use (default: 'div')
        include_ids: Whether to include 'id' attribute
        data_attrs: Node attributes to render as data-* attributes

    Returns:
        Tuple of (node_class, visitors_dict) where visitors_dict can be
        passed directly to app.add_node()

    Example:
        >>> my_node, my_visitors = make_container_node('my_node', data_attrs=['type'])
        >>> # In setup():
        >>> app.add_node(my_node, **my_visitors)
        >>> # Or equivalently:
        >>> app.add_node(my_node, html=my_visitors['html'])
    """
    node_class = create_node_class(name, doc)
    visit, depart = create_div_visitors(
        tag=tag,
        include_ids=include_ids,
        data_attrs=data_attrs,
    )
    return node_class, {'html': (visit, depart)}
