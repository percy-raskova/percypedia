"""
Custom docutils nodes for AI content rendering.

Uses the node factory from _common.nodes to reduce boilerplate.
"""

from _common.nodes import create_div_visitors, create_node_class

# Create node classes using the factory
# Note: Variable names MUST match class names for pickle support
ai_chat_node = create_node_class('ai_chat_node', 'Container node for a full AI chat conversation.', __name__)
ai_message_node = create_node_class('ai_message_node', 'Node for a single message in a chat.', __name__)
ai_exchange_node = create_node_class('ai_exchange_node', 'Node for a Q&A exchange pair.', __name__)
ai_question_node = create_node_class('ai_question_node', 'Node for the question part of an exchange.', __name__)
ai_answer_node = create_node_class('ai_answer_node', 'Node for the answer part of an exchange.', __name__)

# Create HTML visitors using the factory
# ai_chat: uses classes and IDs
visit_ai_chat_html, depart_ai_chat_html = create_div_visitors(include_ids=True)

# ai_message: uses classes and 'sender' data attribute (no IDs)
visit_ai_message_html, depart_ai_message_html = create_div_visitors(
    include_ids=False, data_attrs=['sender']
)

# ai_exchange: uses classes and IDs
visit_ai_exchange_html, depart_ai_exchange_html = create_div_visitors(include_ids=True)

# ai_question: uses classes only
visit_ai_question_html, depart_ai_question_html = create_div_visitors(include_ids=False)

# ai_answer: uses classes only
visit_ai_answer_html, depart_ai_answer_html = create_div_visitors(include_ids=False)
