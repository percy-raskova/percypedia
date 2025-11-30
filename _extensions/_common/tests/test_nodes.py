"""Tests for node factory functions."""

from docutils import nodes

from _common.nodes import create_div_visitors, create_node_class, make_container_node


class TestCreateNodeClass:
    """Tests for create_node_class factory."""

    def test_creates_node_inheriting_from_general_element(self):
        """Created class inherits from nodes.General and nodes.Element."""
        MyNode = create_node_class('my_node')

        assert issubclass(MyNode, nodes.General)
        assert issubclass(MyNode, nodes.Element)

    def test_class_has_correct_name(self):
        """Created class has the specified name."""
        MyNode = create_node_class('custom_name')

        assert MyNode.__name__ == 'custom_name'

    def test_custom_docstring(self):
        """Created class has custom docstring when provided."""
        MyNode = create_node_class('my_node', 'A custom node for testing.')

        assert MyNode.__doc__ == 'A custom node for testing.'

    def test_default_docstring(self):
        """Created class has default docstring when not provided."""
        MyNode = create_node_class('special_node')

        assert 'special_node' in MyNode.__doc__

    def test_node_instance_works(self):
        """Created node class can be instantiated and used."""
        MyNode = create_node_class('test_node')
        node = MyNode()

        node['classes'] = ['my-class', 'other-class']
        node['ids'] = ['my-id']

        assert node['classes'] == ['my-class', 'other-class']
        assert node['ids'] == ['my-id']


class MockHTMLTranslator:
    """Mock HTML translator for testing visitors."""

    def __init__(self):
        self.body = []


class TestCreateDivVisitors:
    """Tests for create_div_visitors factory."""

    def test_creates_visit_and_depart_functions(self):
        """Factory returns a pair of functions."""
        visit, depart = create_div_visitors()

        assert callable(visit)
        assert callable(depart)

    def test_visit_renders_div_with_classes(self):
        """Visit function renders opening div with classes."""
        visit, _ = create_div_visitors()
        translator = MockHTMLTranslator()
        node = nodes.container()
        node['classes'] = ['my-class', 'another']

        visit(translator, node)

        assert '<div' in translator.body[0]
        assert 'class="my-class another"' in translator.body[0]

    def test_depart_renders_closing_div(self):
        """Depart function renders closing div."""
        _, depart = create_div_visitors()
        translator = MockHTMLTranslator()
        node = nodes.container()

        depart(translator, node)

        assert translator.body[0] == '</div>'

    def test_custom_tag(self):
        """Factory respects custom tag parameter."""
        visit, depart = create_div_visitors(tag='section')
        translator = MockHTMLTranslator()
        node = nodes.container()
        node['classes'] = ['test']

        visit(translator, node)
        depart(translator, node)

        assert '<section' in translator.body[0]
        assert '</section>' in translator.body[1]

    def test_includes_id_when_present(self):
        """Visit includes id attribute when node has ids."""
        visit, _ = create_div_visitors(include_ids=True)
        translator = MockHTMLTranslator()
        node = nodes.container()
        node['classes'] = ['cls']
        node['ids'] = ['my-anchor']

        visit(translator, node)

        assert 'id="my-anchor"' in translator.body[0]

    def test_excludes_id_when_disabled(self):
        """Visit excludes id when include_ids=False."""
        visit, _ = create_div_visitors(include_ids=False)
        translator = MockHTMLTranslator()
        node = nodes.container()
        node['classes'] = ['cls']
        node['ids'] = ['my-anchor']

        visit(translator, node)

        assert 'id=' not in translator.body[0]

    def test_data_attributes(self):
        """Visit renders data-* attributes."""
        visit, _ = create_div_visitors(data_attrs=['sender', 'type'])
        translator = MockHTMLTranslator()
        node = nodes.container()
        node['classes'] = ['cls']
        node['sender'] = 'human'
        node['type'] = 'message'

        visit(translator, node)

        assert 'data-sender="human"' in translator.body[0]
        assert 'data-type="message"' in translator.body[0]

    def test_missing_data_attributes_skipped(self):
        """Missing data attributes are not rendered."""
        visit, _ = create_div_visitors(data_attrs=['sender', 'type'])
        translator = MockHTMLTranslator()
        node = nodes.container()
        node['classes'] = ['cls']
        node['sender'] = 'human'
        # 'type' is not set

        visit(translator, node)

        assert 'data-sender="human"' in translator.body[0]
        assert 'data-type' not in translator.body[0]


class TestMakeContainerNode:
    """Tests for make_container_node convenience function."""

    def test_returns_node_class_and_visitors(self):
        """Factory returns (class, visitors_dict) tuple."""
        node_class, visitors = make_container_node('test_node')

        assert isinstance(node_class, type)
        assert 'html' in visitors
        assert len(visitors['html']) == 2

    def test_node_class_is_valid(self):
        """Returned node class works correctly."""
        node_class, _ = make_container_node('my_node', 'Doc string.')

        assert issubclass(node_class, nodes.General)
        assert node_class.__name__ == 'my_node'
        assert node_class.__doc__ == 'Doc string.'

    def test_visitors_work_correctly(self):
        """Returned visitors render HTML correctly."""
        node_class, visitors = make_container_node('test_node', data_attrs=['sender'])
        translator = MockHTMLTranslator()

        node = node_class()
        node['classes'] = ['my-class']
        node['ids'] = ['my-id']
        node['sender'] = 'assistant'

        visit, depart = visitors['html']
        visit(translator, node)
        depart(translator, node)

        assert '<div class="my-class" id="my-id" data-sender="assistant">' in translator.body[0]
        assert '</div>' in translator.body[1]

    def test_can_unpack_visitors_for_sphinx(self):
        """Visitors dict can be unpacked for app.add_node()."""
        _, visitors = make_container_node('n')

        # This is how it would be used: app.add_node(node_class, **visitors)
        assert 'html' in visitors
        visit, depart = visitors['html']
        assert callable(visit)
        assert callable(depart)
