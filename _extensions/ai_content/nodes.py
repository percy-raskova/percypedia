"""
Custom docutils nodes for AI content rendering.
"""

from docutils import nodes


class ai_chat_node(nodes.General, nodes.Element):
    """Container node for a full AI chat conversation."""
    pass


class ai_message_node(nodes.General, nodes.Element):
    """Node for a single message in a chat."""
    pass


class ai_exchange_node(nodes.General, nodes.Element):
    """Node for a Q&A exchange pair."""
    pass


class ai_question_node(nodes.General, nodes.Element):
    """Node for the question part of an exchange."""
    pass


class ai_answer_node(nodes.General, nodes.Element):
    """Node for the answer part of an exchange."""
    pass


# HTML visitors

def visit_ai_chat_html(self, node: ai_chat_node) -> None:
    """Render ai_chat_node opening tag."""
    classes = ' '.join(node.get('classes', []))
    ids = ' '.join(f'id="{id}"' for id in node.get('ids', []))
    self.body.append(f'<div class="{classes}" {ids}>')


def depart_ai_chat_html(self, _node: ai_chat_node) -> None:
    """Render ai_chat_node closing tag."""
    self.body.append('</div>')


def visit_ai_message_html(self, node: ai_message_node) -> None:
    """Render ai_message_node opening tag."""
    classes = ' '.join(node.get('classes', []))
    sender = node.get('sender', 'unknown')
    self.body.append(f'<div class="{classes}" data-sender="{sender}">')


def depart_ai_message_html(self, _node: ai_message_node) -> None:
    """Render ai_message_node closing tag."""
    self.body.append('</div>')


def visit_ai_exchange_html(self, node: ai_exchange_node) -> None:
    """Render ai_exchange_node opening tag."""
    classes = ' '.join(node.get('classes', []))
    ids = ' '.join(f'id="{id}"' for id in node.get('ids', []))
    self.body.append(f'<div class="{classes}" {ids}>')


def depart_ai_exchange_html(self, _node: ai_exchange_node) -> None:
    """Render ai_exchange_node closing tag."""
    self.body.append('</div>')


def visit_ai_question_html(self, node: ai_question_node) -> None:
    """Render ai_question_node opening tag."""
    classes = ' '.join(node.get('classes', []))
    self.body.append(f'<div class="{classes}">')


def depart_ai_question_html(self, _node: ai_question_node) -> None:
    """Render ai_question_node closing tag."""
    self.body.append('</div>')


def visit_ai_answer_html(self, node: ai_answer_node) -> None:
    """Render ai_answer_node opening tag."""
    classes = ' '.join(node.get('classes', []))
    self.body.append(f'<div class="{classes}">')


def depart_ai_answer_html(self, _node: ai_answer_node) -> None:
    """Render ai_answer_node closing tag."""
    self.body.append('</div>')
