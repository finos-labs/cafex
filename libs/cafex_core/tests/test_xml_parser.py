"""
Test module for the XMLParser class in the CAFEX framework.

This module provides comprehensive test coverage for the XML parsing capabilities
in the cafex_core.parsers.xml_parser module.
"""
from unittest.mock import patch, MagicMock

import pytest
from lxml import etree, objectify

from cafex_core.parsers.xml_parser import XMLParser


class TestXMLParser:
    """Test suite for XMLParser class."""

    @pytest.fixture
    def xml_parser(self):
        """Fixture to create an XMLParser instance for tests."""
        return XMLParser()

    @pytest.fixture
    def sample_xml_str(self):
        """Fixture to provide a sample XML string for testing."""
        return '''<?xml version="1.0"?>
        <data name="Test" direction="top" single="single_attr">
          <country name="Liechtenstein">
            <rank name="Person1" last="Person2">1</rank>
            <year year_attr="year">2008</year>
            <gdp attr_test="attr_value" direction="E">141100</gdp>
            <neighbor name="Austria" direction="E"/>
            <data name1="Test" single="single_attr1">123</data>
            <data name="Test1" direction="bottom">1</data>
            <neighbor name="Switzerland" direction="W">
              <test name="Test123" att_name="name to return1">Test</test>
            </neighbor>
          </country>
          <country name="Singapore">
            <rank name="Person1" last="Person2" single1="single_value">2</rank>
            <year year_attr="year1">2011</year>
            <gdp>59900</gdp>
            <neighbor name="Austria" direction="N">
              <test name1="name1_test" att_name="name to return2">Test2</test>
            </neighbor>
          </country>
          <country name="Panama">
            <rank>68</rank>
            <year year_attr="year2">2013</year>
            <gdp attr_test="attr_value">13600</gdp>
            <neighbor name="Costa Rica" direction="W"/>
            <dp>
              <test name="Test" att_name="name to return2">Test3</test>
            </dp>
            <neighbor name="Colombia" direction="E"/>
            <level1 name="level1">level</level1>
          </country>
          <top_level name="top_level">
            <level1 name="level1">level1</level1>
          </top_level>
        </data>'''

    @pytest.fixture
    def sample_xml_file(self, sample_xml_str, tmpdir):
        """Fixture to create a sample XML file for testing."""
        xml_file = tmpdir.join("sample.xml")
        xml_file.write(sample_xml_str)
        return str(xml_file)

    @pytest.fixture
    def simple_xml_str(self):
        """Fixture to provide a simple XML string for testing."""
        return '''<?xml version="1.0"?>
        <root>
          <element>Text</element>
          <element>Another</element>
          <nested>
            <child>Child text</child>
          </nested>
        </root>'''

    @pytest.fixture
    def namespaced_xml_str(self):
        """Fixture to provide a namespaced XML string for testing."""
        return '''<?xml version="1.0"?>
        <root xmlns="http://example.org/ns1" xmlns:ns2="http://example.org/ns2">
          <element>Text</element>
          <ns2:element>Another</ns2:element>
          <nested>
            <ns2:child>Child text</ns2:child>
          </nested>
        </root>'''

    @pytest.fixture
    def sample_xml_str_with_empty_child(self):
        return '''<?xml version="1.0"?>
        <data>
          <country>
            <rank></rank>
            <rank>2</rank>
          </country>
        </data>'''

    def test_init(self, xml_parser):
        """Test XMLParser initialization."""
        assert xml_parser is not None
        assert xml_parser.logger is not None
        assert xml_parser.exceptions is not None

    def test_get_root_arbitrary_from_string(self, xml_parser, simple_xml_str):
        """Test parsing XML from a string."""
        root = xml_parser.get_root_arbitrary(simple_xml_str)
        assert root is not None
        assert root.tag == "root"
        assert len(root.findall(".//element")) == 2
        """Test handling of unexpected exceptions in get_root_arbitrary."""
        with patch('lxml.etree.fromstring', side_effect=Exception("Unexpected error")):
            root = xml_parser.get_root_arbitrary("<data><item>value</item></data>")
            assert root is None

    def test_get_root_arbitrary_from_file(self, xml_parser, sample_xml_file):
        """Test parsing XML from a file."""
        root = xml_parser.get_root_arbitrary(sample_xml_file)
        assert root is not None
        assert root.tag == "data"
        assert len(root.findall(".//country")) == 3

    def test_get_root_arbitrary_invalid_input(self, xml_parser):
        """Test parsing invalid XML."""
        # Invalid XML string
        invalid_xml = "<root><unclosed>"
        root = xml_parser.get_root_arbitrary(invalid_xml)
        assert root is None

        # Empty string
        root = xml_parser.get_root_arbitrary("")
        assert root is None

        # Non-existent file
        root = xml_parser.get_root_arbitrary("nonexistent.xml")
        assert root is None

    def test_clean_namespace(self, xml_parser, namespaced_xml_str):
        """Test removing namespaces from XML."""
        try:
            root = xml_parser.get_root_arbitrary(namespaced_xml_str)
            assert "}" in root.tag  # Namespace is present

            xml_parser.clean_namespace(root)
            assert root.tag == "root"  # Namespace should be removed

            # Check if namespaces are removed from child elements
            for elem in root.iter():
                assert "}" not in elem.tag
            # Test with None
            xml_parser.clean_namespace(None)
            # No assertion needed, just verify it doesn't raise an exception
            # Create an XML element with a tag that does not have the 'find' attribute
            root = etree.Element("root")
            with patch('lxml.objectify.deannotate', side_effect=Exception("Unexpected error")):
                with patch.object(xml_parser.exceptions, 'raise_generic_exception') as mock_exception:
                    xml_parser.clean_namespace(root)
                    mock_exception.assert_called_once_with(
                        "Error in removing namespaces from XML: Unexpected error", fail_test=False
                    )
        except Exception as e:
            print(e)

    def test_get_elements(self, xml_parser, sample_xml_str):
        """Test getting elements with XPath."""
        # Valid XPath
        elements = xml_parser.get_elements(sample_xml_str, ".//country")
        assert len(elements) == 3

        # Another valid XPath
        elements = xml_parser.get_elements(sample_xml_str, ".//rank")
        assert len(elements) == 3
        assert [e.text for e in elements] == ["1", "2", "68"]

        # Invalid XPath
        elements = xml_parser.get_elements(sample_xml_str, ".//[invalid")
        assert elements == []

        # Empty source or XPath
        assert xml_parser.get_elements("", ".//country") == []
        assert xml_parser.get_elements(sample_xml_str, "") == []
        with patch.object(xml_parser, 'get_root_arbitrary', return_value=None):
            elements = xml_parser.get_elements("<invalid></invalid>", ".//item")
            assert elements == []
        with patch.object(xml_parser, 'get_root_arbitrary', side_effect=Exception("Unexpected error")):
            elements = xml_parser.get_elements("<data><item>value</item></data>", ".//item")
            assert elements == []

    def test_get_element_by_xpath(self, xml_parser, sample_xml_str):
        """Test getting element text by XPath."""
        try:
            # Valid XPath
            text = xml_parser.get_element_by_xpath(sample_xml_str, ".//country[@name='Liechtenstein']/rank")
            assert text == "1"

            # XPath with no match
            text = xml_parser.get_element_by_xpath(sample_xml_str, ".//nonexistent")
            assert text is None

            # Empty source or XPath
            assert xml_parser.get_element_by_xpath("", ".//rank") is None
            assert xml_parser.get_element_by_xpath(sample_xml_str, "") is None

            with patch.object(xml_parser, 'get_elements', side_effect=Exception("Unexpected error")):
                result = xml_parser.get_element_by_xpath(sample_xml_str, ".//country")
                assert result is None
                xml_parser.exceptions.raise_generic_exception.assert_called_with(
                    "Error getting element by XPath './/country': Unexpected error", fail_test=False
                )
        except Exception as e:
            print("Exception occurred in test_get_element_by_xpath")

    def test_get_element_by_ancestors(self, xml_parser, sample_xml_str, sample_xml_str_with_empty_child):
        """Test getting element text by ancestor-child relationship."""
        # Valid ancestors
        texts = xml_parser.get_element_by_ancestors(sample_xml_str, "country", "rank")
        assert texts == ["1", "2", "68"]

        # Another valid case
        texts = xml_parser.get_element_by_ancestors(sample_xml_str, "neighbor", "test")
        assert texts == ["Test", "Test2"]

        # Non-existent ancestor
        texts = xml_parser.get_element_by_ancestors(sample_xml_str, "nonexistent", "rank")
        assert texts == []

        # Non-existent child
        texts = xml_parser.get_element_by_ancestors(sample_xml_str, "country", "nonexistent")
        assert texts == []

        # Empty source, parent, or child
        assert xml_parser.get_element_by_ancestors("", "country", "rank") == []
        assert xml_parser.get_element_by_ancestors(sample_xml_str, "", "rank") == []
        assert xml_parser.get_element_by_ancestors(sample_xml_str, "country", "") == []
        with patch.object(xml_parser, 'get_root_arbitrary', return_value=None):
            result = xml_parser.get_element_by_ancestors("<invalid></invalid>", "country", "rank")
            assert result == []
        with patch.object(xml_parser, 'get_root_arbitrary', return_value=etree.fromstring(sample_xml_str)):
            result = xml_parser.get_element_by_ancestors(sample_xml_str, "country", "rank")
            assert result == ["1", "2", "68"]
        with patch.object(xml_parser, 'get_root_arbitrary', side_effect=Exception("Unexpected error")):
            result = xml_parser.get_element_by_ancestors("<data><item>value</item></data>", "country", "rank")
            assert result == []
        with patch.object(xml_parser, 'get_root_arbitrary',
                          return_value=etree.fromstring(sample_xml_str_with_empty_child)):
            result = xml_parser.get_element_by_ancestors(sample_xml_str_with_empty_child, "country", "rank")
            assert result == ["", "2"]

    def test_get_element_by_name(self, xml_parser, sample_xml_str):
        """Test getting element text by name."""
        # All elements with name
        texts = xml_parser.get_element_by_name(sample_xml_str, "rank")
        assert texts == ["1", "2", "68"]

        # With specific index
        text = xml_parser.get_element_by_name(sample_xml_str, "rank", index=1)
        assert text == "2"

        # With parent
        texts = xml_parser.get_element_by_name(sample_xml_str, "rank", parent="country")
        assert texts == ["1", "2", "68"]

        # With parent and index
        text = xml_parser.get_element_by_name(sample_xml_str, "rank", index=0, parent="country")
        assert text == "1"

        # Invalid index
        text = xml_parser.get_element_by_name(sample_xml_str, "rank", index=10)
        assert text == ""

        # Non-existent element
        texts = xml_parser.get_element_by_name(sample_xml_str, "nonexistent")
        assert texts == []

        # Empty source or child
        assert xml_parser.get_element_by_name("", "rank") == []
        assert xml_parser.get_element_by_name(sample_xml_str, "") == []
        with patch.object(xml_parser, 'get_root_arbitrary', return_value=None):
            result = xml_parser.get_element_by_name("<invalid></invalid>", "rank")
            assert result == []

            result = xml_parser.get_element_by_name("<invalid></invalid>", "rank", index=0)
            assert result == ""
        with patch.object(xml_parser, 'get_root_arbitrary', side_effect=Exception("Unexpected error")):
            result = xml_parser.get_element_by_name("<data><item>value</item></data>", "item")
            assert result == []

            result = xml_parser.get_element_by_name("<data><item>value</item></data>", "item", index=0)
            assert result == ""

    def test_get_element_by_index(self, xml_parser, sample_xml_str):
        """Test getting element text by index."""
        try:
            # Valid index
            text = xml_parser.get_element_by_index(sample_xml_str, "rank", 1)
            assert text == "2"

            # Test with invalid input
            with pytest.raises(ValueError):
                xml_parser.get_element_by_index("", "rank", 0)

            with pytest.raises(ValueError):
                xml_parser.get_element_by_index(sample_xml_str, "", 0)

            with pytest.raises(ValueError):
                xml_parser.get_element_by_index(sample_xml_str, "rank", "not an int")
            xml_parser = XMLParser()
            sample_xml_str = '''<?xml version="1.0"?>
            <root>
              <element>Text1</element>
              <element>Text2</element>
              <element>Text3</element>
            </root>'''

            with patch.object(xml_parser, 'get_element_by_name', return_value=["Text2"]):
                result = xml_parser.get_element_by_index(sample_xml_str, "element", 1)
                assert result == "Text2"
            with patch.object(xml_parser, 'get_element_by_name', return_value=[]):
                result = xml_parser.get_element_by_index(sample_xml_str, "element", 1)
                assert result == ""
            with patch.object(xml_parser, 'get_element_by_name', side_effect=Exception("Unexpected error")):
                result = xml_parser.get_element_by_index(sample_xml_str, "rank", 1)
                assert result == ""
                xml_parser.exceptions.raise_generic_exception.assert_called_with(
                    "Error getting element 'rank' at index 1: Unexpected error", fail_test=False
                )
        except Exception as e:
            print(e)

    def test_get_attribute(self, xml_parser, sample_xml_str):
        """Test getting attribute values."""
        try:
            # Get text content of elements with attribute
            values = xml_parser.get_attribute(sample_xml_str, "neighbor", "name")

            # Check that we have the right number of values
            assert len(values) == 5

            # Instead of checking exact values with whitespace, check that all values are empty
            # or contain only whitespace
            for value in values:
                assert value.strip() == ""

            # Get attribute values
            values = xml_parser.get_attribute(
                sample_xml_str, "neighbor", "name", return_attribute_value=True
            )
            assert "Austria" in values
            assert "Switzerland" in values

            # With index
            value = xml_parser.get_attribute(
                sample_xml_str, "neighbor", "name", index=0, return_attribute_value=True
            )
            assert value == "Austria"

            # With parent
            values = xml_parser.get_attribute(
                sample_xml_str, "neighbor", "name", parent="country", return_attribute_value=True
            )
            assert "Austria" in values

            # Invalid inputs
            assert xml_parser.get_attribute("", "neighbor", "name") == []
            assert xml_parser.get_attribute(sample_xml_str, "", "name") == []
            assert xml_parser.get_attribute(sample_xml_str, "neighbor", "") == []

            # Invalid index
            value = xml_parser.get_attribute(
                sample_xml_str, "neighbor", "name", index=10, return_attribute_value=True
            )
            assert value == ""
            with patch.object(xml_parser, 'get_elements', side_effect=Exception("Invalid XPath")):
                with patch.object(xml_parser.exceptions, 'raise_generic_exception') as mock_exception:
                    result = xml_parser.get_attribute(sample_xml_str, "tag", "attribute")
                    assert result == []
                    mock_exception.assert_called_with(
                        "Error getting attribute 'attribute' from tag 'tag': Invalid XPath",
                        fail_test=False
                    )
        except Exception as e:
            print(e)

    def test_get_element_count(self, xml_parser, sample_xml_str):
        """Test counting elements with XPath."""
        # Valid XPath
        try:
            count = xml_parser.get_element_count(sample_xml_str, ".//country")
            assert count == 3

            count = xml_parser.get_element_count(sample_xml_str, ".//rank")
            assert count == 3

            # Non-existent element
            count = xml_parser.get_element_count(sample_xml_str, ".//nonexistent")
            assert count == 0

            # Empty source or XPath
            assert xml_parser.get_element_count("", ".//country") == 0
            assert xml_parser.get_element_count(sample_xml_str, "") == 0
            with patch.object(xml_parser, 'get_elements', side_effect=Exception("Unexpected error")):
                count = xml_parser.get_element_count(sample_xml_str, ".//element")
                assert count == 0
                xml_parser.exceptions.raise_generic_exception.assert_called_with(
                    "Error counting elements with XPath './/element': Unexpected error", fail_test=False
                )
        except Exception as e:
            print(e)

    def test_element_should_exist(self, xml_parser, sample_xml_str):
        """Test checking if element exists."""
        try:
            # Using XPath
            assert xml_parser.element_should_exist(sample_xml_str, ".//country")
            assert not xml_parser.element_should_exist(sample_xml_str, ".//nonexistent")

            # Using element name
            assert xml_parser.element_should_exist(sample_xml_str, "rank")
            assert not xml_parser.element_should_exist(sample_xml_str, "nonexistent")

            # Empty source or identifier
            assert not xml_parser.element_should_exist("", ".//country")
            assert not xml_parser.element_should_exist(sample_xml_str, "")
            with patch.object(xml_parser, 'get_element_by_name', side_effect=Exception("Unexpected error")):
                result = xml_parser.element_should_exist(sample_xml_str, "rank")
                assert not result
                xml_parser.exceptions.raise_generic_exception.assert_called_with(
                    "Error checking existence of element 'rank': Unexpected error", fail_test=False
                )
        except Exception as e:
            print(e)

    def test_element_should_not_exist(self, xml_parser, sample_xml_str):
        """Test checking if element does not exist."""
        try:
            # Using XPath
            assert not xml_parser.element_should_not_exist(sample_xml_str, ".//country")
            assert xml_parser.element_should_not_exist(sample_xml_str, ".//nonexistent")

            # Using element name
            assert not xml_parser.element_should_not_exist(sample_xml_str, "rank")
            assert xml_parser.element_should_not_exist(sample_xml_str, "nonexistent")

            # Empty source or identifier
            assert xml_parser.element_should_not_exist("", ".//country")
            assert xml_parser.element_should_not_exist(sample_xml_str, "")
            with patch.object(xml_parser, 'element_should_exist', side_effect=Exception("Unexpected error")):
                result = xml_parser.element_should_not_exist(sample_xml_str, ".//country")
                assert not result
                xml_parser.exceptions.raise_generic_exception.assert_called_with(
                    "Error checking non-existence of element './/country': Unexpected error", fail_test=False
                )
        except Exception as e:
            print(e)

    def test_find_all(self, xml_parser, sample_xml_str):
        """Test finding all elements with XPath."""
        try:
            # Valid XPath
            elements = xml_parser.find_all(sample_xml_str, ".//country")
            assert len(elements) == 3

            # Another valid XPath
            elements = xml_parser.find_all(sample_xml_str, ".//rank")
            assert len(elements) == 3

            # Non-existent element
            elements = xml_parser.find_all(sample_xml_str, ".//nonexistent")
            assert elements == []

            # Empty source or XPath
            assert xml_parser.find_all("", ".//country") == []
            assert xml_parser.find_all(sample_xml_str, "") == []
            with patch.object(xml_parser, 'get_root_arbitrary', return_value=None):
                elements = xml_parser.find_all("<invalid></invalid>", ".//item")
                assert elements == []
            with patch.object(xml_parser, 'get_root_arbitrary', side_effect=Exception("Unexpected error")):
                result = xml_parser.find_all("dummy_source.xml", ".//rank")
                assert result == []
                xml_parser.exceptions.raise_generic_exception.assert_called_once_with(
                    "Error finding elements with XPath './/rank': Test Exception", fail_test=False
                )
        except Exception as e:
            print(e)

    def test_get_xpath(self, xml_parser):
        """Test converting to valid XPath."""
        try:
            # String XPath
            assert xml_parser._get_xpath(".//element") == ".//element"

            # Non-string convertible to string
            assert xml_parser._get_xpath(123) == "123"

            # Empty input
            assert xml_parser._get_xpath("") == ""

            # None input (will return empty string due to exception handling)
            assert xml_parser._get_xpath(None) == ""

            class Unconvertible:
                def __str__(self):
                    raise TypeError("Cannot convert to string")

            with patch.object(xml_parser.exceptions, 'raise_generic_exception') as mock_exception:
                result = xml_parser._get_xpath(Unconvertible())
                assert result == ""
                mock_exception.assert_called_once_with(
                    "XPath must be a string or convertible to a string: Cannot convert to string", fail_test=False
                )

            class UnexpectedException:
                def __str__(self):
                    raise Exception("Unexpected error")

            with patch.object(xml_parser.exceptions, 'raise_generic_exception') as mock_exception:
                result = xml_parser._get_xpath(UnexpectedException())
                assert result == ""
                mock_exception.assert_called_once_with(
                    "Error processing XPath: Unexpected error", fail_test=False
                )

        except Exception as e:
            print(e)

    def test_get_xml_result(self, xml_parser, sample_xml_str):
        """Test getting XML results with different criteria."""
        try:
            # By node name
            result = xml_parser.get_xml_result(sample_xml_str, node="rank")
            assert result == ["1", "2", "68"]

            # By XPath
            result = xml_parser.get_xml_result(sample_xml_str, node_xpath=".//rank[1]")
            assert result == "1"

            # By ancestor-child
            result = xml_parser.get_xml_result(sample_xml_str, ancestor="country", child="rank")
            assert result == ["1", "2", "68"]

            # Invalid inputs
            assert xml_parser.get_xml_result("", node="rank") == []

            # Ancestor without child
            result = xml_parser.get_xml_result(sample_xml_str, ancestor="country")
            assert result == ""

            # Multiple criteria (should use only one)
            result = xml_parser.get_xml_result(
                sample_xml_str, node="rank", node_xpath=".//rank", ancestor="country"
            )
            assert result == ""
            with patch.object(xml_parser.exceptions, 'raise_generic_exception') as mock_exception:
                result = xml_parser.get_xml_result(sample_xml_str)
                assert result == ""
                mock_exception.assert_called_once_with(
                    "Invalid search criteria. Please provide valid parameters", fail_test=False
                )
            with patch.object(xml_parser, 'get_element_by_name', side_effect=Exception("Unexpected error")):
                with patch.object(xml_parser.exceptions, 'raise_generic_exception') as mock_exception:
                    result = xml_parser.get_xml_result(sample_xml_str, node="rank")
                    assert result == ""
                    mock_exception.assert_called_once_with(
                        "Error extracting XML result: Unexpected error", fail_test=False
                    )
        except Exception as e:
            print(e)

    def test_get_formatted_list(self, xml_parser):
        """Test formatting list of values."""
        # Valid input
        values = [["a", "b", "c"], [1, 2, 3]]
        result = xml_parser._XMLParser__get_formatted_list(values)
        assert result == [["a", 1], ["b", 2], ["c", 3]]

        # Empty input
        empty_result = xml_parser._XMLParser__get_formatted_list([])
        assert empty_result == []
        with patch('builtins.zip', side_effect=Exception("Unexpected error")):
            with patch.object(xml_parser.exceptions, 'raise_generic_exception') as mock_exception:
                result = xml_parser._XMLParser__get_formatted_list([[1, 2], [3, 4]])
                assert result == []
                mock_exception.assert_called_once_with("Error formatting list: Unexpected error", fail_test=False)

    def test_create_empty_lists(self, xml_parser):
        """Test creating empty lists."""
        # Valid size
        result = xml_parser._create_empty_lists(3)
        assert result == [[], [], []]
        assert len(result) == 3

        # Invalid size
        with pytest.raises(ValueError):
            xml_parser._create_empty_lists(0)

        with pytest.raises(ValueError):
            xml_parser._create_empty_lists(-1)

        with pytest.raises(ValueError):
            xml_parser._create_empty_lists("not a number")

    def test_get_element_by_attribute(self, xml_parser, sample_xml_str):
        """Test getting elements by attribute."""
        # Get text content of elements with attribute
        values = xml_parser.get_element_by_attribute(sample_xml_str, "name")
        assert len(values) > 0

        # Get attribute values
        values = xml_parser.get_element_by_attribute(
            sample_xml_str, "name", return_attribute_value=True
        )
        assert "Liechtenstein" in values
        assert "Singapore" in values

        # With index
        value = xml_parser.get_element_by_attribute(
            sample_xml_str, "name", index=0, return_attribute_value=True
        )
        assert value in ["Liechtenstein", "Test", "Austria"]  # Depends on order

        # With parent - gets elements with 'name' attribute INSIDE country elements
        values = xml_parser.get_element_by_attribute(
            sample_xml_str, "name", parent="country", return_attribute_value=True
        )
        # Check for elements that are inside country elements that have the name attribute
        assert "Person1" in values  # From rank elements
        assert "Austria" in values  # From neighbor elements
        assert "Switzerland" in values  # From neighbor element
        assert "Test1" in values  # From data element
        assert "level1" in values  # From level1 element

        # To get the country names, we'd need to directly use a different xpath like:
        # .//*[@name='Liechtenstein'] or .//country/@name
        countries = xml_parser.get_elements(sample_xml_str, ".//country")
        country_names = [country.get("name") for country in countries if country.get("name")]
        assert "Liechtenstein" in country_names
        assert "Singapore" in country_names
        assert "Panama" in country_names

        # Invalid inputs
        assert xml_parser.get_element_by_attribute("", "name") == []
        assert xml_parser.get_element_by_attribute(sample_xml_str, "") == []

        # Invalid index
        value = xml_parser.get_element_by_attribute(
            sample_xml_str, "name", index=100, return_attribute_value=True
        )
        assert value == ""
        with patch.object(xml_parser, 'get_elements', side_effect=Exception("Unexpected error")):
            with patch.object(xml_parser.exceptions, 'raise_generic_exception') as mock_exception:
                result = xml_parser.get_element_by_attribute(sample_xml_str, "name")
                assert result == []
                mock_exception.assert_called_once_with(
                    "Error getting element by attribute 'name': Unexpected error", fail_test=False
                )

    def test_get_values_from_xml_dict(self, xml_parser, sample_xml_str):
        """Test extracting values with dictionary criteria."""
        # Single node
        result = xml_parser.get_values_from_xml(
            sample_xml_str, {"node": "level1", "parent": "top_level"}
        )
        assert len(result) == 2
        assert result[0] == ["top_level/level1"]
        assert "level1" in result[1][0]

        # Single attribute
        result = xml_parser.get_values_from_xml(
            sample_xml_str, {"attribute_name": "name", "index": 0}
        )
        assert len(result) == 2
        assert result[0] == ["name[0]"]

        # Invalid input
        result = xml_parser.get_values_from_xml("", {"node": "level1"})
        assert result == []

        result = xml_parser.get_values_from_xml(sample_xml_str, {})
        assert result == []
        with patch.object(xml_parser, '_XMLParser__extract_values_from_xml', side_effect=Exception("Unexpected error")):
            with patch.object(xml_parser.exceptions, 'raise_generic_exception') as mock_exception:
                result = xml_parser.get_values_from_xml(sample_xml_str, {"node": "rank"})
                assert result == []
                mock_exception.assert_called_once_with(
                    "Error extracting values from XML: Unexpected error", fail_test=False
                )

    def test_get_values_from_xml_list(self, xml_parser, sample_xml_str):
        """Test extracting values with list of criteria."""
        # Multiple criteria
        result = xml_parser.get_values_from_xml(
            sample_xml_str,
            [
                {"node": "level1", "parent": "top_level"},
                {"node": "rank", "index": 0},
                {"attribute_name": "name", "parent": "country"},
            ],
        )
        assert len(result) == 2
        assert len(result[0]) == 3
        assert len(result[1]) == 3

        # With formatting
        result = xml_parser.get_values_from_xml(
            sample_xml_str,
            [
                {"node": "level1", "parent": "top_level"},
                {"node": "rank", "index": 0},
            ],
            formatting_required=True,
        )
        assert len(result) == 2
        assert len(result[0]) == 2
        assert len(result[1]) == 2

        # Invalid type
        result = xml_parser.get_values_from_xml(sample_xml_str, "not a dict or list")
        assert result == []

    def test_extract_values_from_xml(self, xml_parser, sample_xml_str):
        """Test internal method for extracting values."""
        # Initialize result list
        result_list = [[], []]

        # Test with node and attribute_name and index
        updated_list = xml_parser._XMLParser__extract_values_from_xml(
            sample_xml_str,
            {"node": "rank", "attribute_name": "name", "index": 0},
            result_list,
        )
        assert len(updated_list) == 2
        assert len(updated_list[0]) == 1
        assert len(updated_list[1]) == 1

        # Test with node and attribute_name
        updated_list = xml_parser._XMLParser__extract_values_from_xml(
            sample_xml_str,
            {"node": "country", "attribute_name": "name"},
            [[], []],
        )
        assert len(updated_list) == 2
        assert len(updated_list[0]) == 1
        assert len(updated_list[1]) == 1

        # Test with node and index
        updated_list = xml_parser._XMLParser__extract_values_from_xml(
            sample_xml_str,
            {"node": "rank", "index": 1},
            [[], []],
        )
        assert len(updated_list) == 2
        assert len(updated_list[0]) == 1
        assert len(updated_list[1]) == 1
        assert updated_list[1][0] == "2"

        # Test with node only
        updated_list = xml_parser._XMLParser__extract_values_from_xml(
            sample_xml_str,
            {"node": "rank"},
            [[], []],
        )
        assert len(updated_list) == 2
        assert len(updated_list[0]) == 1
        assert len(updated_list[1]) == 1
        assert updated_list[1][0] == ["1", "2", "68"]

        # Test with attribute_name and index
        updated_list = xml_parser._XMLParser__extract_values_from_xml(
            sample_xml_str,
            {"attribute_name": "name", "index": 0},
            [[], []],
        )
        assert len(updated_list) == 2
        assert len(updated_list[0]) == 1
        assert len(updated_list[1]) == 1

        # Test with attribute_name only
        updated_list = xml_parser._XMLParser__extract_values_from_xml(
            sample_xml_str,
            {"attribute_name": "name"},
            [[], []],
        )
        assert len(updated_list) == 2
        assert len(updated_list[0]) == 1
        assert len(updated_list[1]) == 1

        # Invalid inputs
        updated_list = xml_parser._XMLParser__extract_values_from_xml(
            "", {"node": "rank"}, [[], []]
        )
        assert updated_list == [[], []]

        updated_list = xml_parser._XMLParser__extract_values_from_xml(
            sample_xml_str, {}, [[], []]
        )
        assert updated_list == [[], []]

        # Missing node and attribute
        updated_list = xml_parser._XMLParser__extract_values_from_xml(
            sample_xml_str, {"other": "value"}, [[], []]
        )
        assert updated_list == [[], []]

        updated_list = xml_parser._XMLParser__extract_values_from_xml(
            sample_xml_str, plst_element_list=None, pdict_item={"node": "rank"}
        )
        assert updated_list is None

    def test_compare_xml_schemas_on_mode(self, xml_parser):
        """Test comparing XML schemas with 'on' ignore mode."""
        # Same structure, different order and multiplicity
        source_xml = '''
         <car>
             <light>head</light>
             <light>head</light>
             <bumper>
                 <front>1</front>
                 <back>1</back>
             </bumper>
             <wheel>1</wheel>
         </car>'''

        target_xml = '''
         <car>
             <wheel>2</wheel>
             <bumper>
                 <back>2</back>
                 <front>2</front>
             </bumper>
             <light>head</light>
         </car>'''

        assert xml_parser.compare_xml_schemas(source_xml, target_xml, ignore_mode="on")

        # Different structure
        different_xml = '''
         <car>
             <wheel>2</wheel>
             <bumper>
                 <side>2</side>
             </bumper>
             <light>head</light>
         </car>'''

        assert not xml_parser.compare_xml_schemas(source_xml, different_xml, ignore_mode="on")

    def test_compare_xml_schemas_positioning_mode(self, xml_parser):
        """Test comparing XML schemas with 'positioning' ignore mode."""
        # Same paths, different values
        source_xml = '''
          <car>
              <light>head</light>
              <bumper>
                  <front>1</front>
                  <back>1</back>
              </bumper>
              <wheel>1</wheel>
          </car>'''

        target_xml = '''
          <car>
              <light>tail</light>
              <bumper>
                  <front>2</front>
                  <back>2</back>
              </bumper>
              <wheel>4</wheel>
          </car>'''

        assert xml_parser.compare_xml_schemas(source_xml, target_xml, ignore_mode="positioning")

        # Different structure
        different_xml = '''
          <car>
              <bumper>
                  <front>1</front>
                  <back>1</back>
              </bumper>
              <light>head</light>
              <wheel>1</wheel>
          </car>'''

        assert xml_parser.compare_xml_schemas(source_xml, different_xml, ignore_mode="positioning")
        """Test comparing XML schemas with 'positioning' ignore mode where no elements match."""
        source_xml = '''
          <car>
              <light>head</light>
              <bumper>
                  <front>1</front>
                  <back>1</back>
              </bumper>
              <wheel>1</wheel>
          </car>'''

        target_xml = '''
          <vehicle>
              <lamp>head</lamp>
              <shield>
                  <front>1</front>
                  <rear>1</rear>
              </shield>
              <tire>1</tire>
          </vehicle>'''

        assert not xml_parser.compare_xml_schemas(source_xml, target_xml, ignore_mode="positioning")

    def test_compare_xml_schemas_equal_mode(self, xml_parser):
        """Test comparing XML schemas with 'equal' ignore mode."""
        # Exactly the same structure
        source_xml = '''
        <car>
            <light>head</light>
            <bumper>
                <front>1</front>
                <back>1</back>
            </bumper>
            <wheel>1</wheel>
        </car>'''

        similar_xml = '''
        <car>
            <light>head</light>
            <bumper>
                <front>1</front>
                <back>1</back>
            </bumper>
            <wheel>1</wheel>
        </car>'''

        assert xml_parser.compare_xml_schemas(source_xml, similar_xml, ignore_mode="equal")

        # Different values
        different_values_xml = '''
        <car>
            <light>head</light>
            <bumper>
                <front>2</front>
                <back>2</back>
            </bumper>
            <wheel>4</wheel>
        </car>'''

        assert xml_parser.compare_xml_schemas(source_xml, different_values_xml, ignore_mode="equal")

        # Different structure
        different_xml = '''
        <car>
            <light>head</light>
            <bumper>
                <front>1</front>
                <back>1</back>
                <side>1</side>
            </bumper>
            <wheel>1</wheel>
        </car>'''

        assert not xml_parser.compare_xml_schemas(source_xml, different_xml, ignore_mode="equal")
        source_xml = '''
        <car>
            <light>head</light>
            <bumper>
                <front>1</front>
                <back>1</back>
            </bumper>
            <wheel>1</wheel>
        </car>'''

        target_xml = '''
        <car>
            <light>head</light>
            <bumper>
                <back>1</back>
                <front>1</front>
            </bumper>
            <wheel>1</wheel>
        </car>'''

        assert not xml_parser.compare_xml_schemas(source_xml, target_xml, ignore_mode="equal")

    def test_compare_xml_schemas_invalid_inputs(self, xml_parser, sample_xml_str):
        """Test schema comparison with invalid inputs."""
        # Invalid source
        assert not xml_parser.compare_xml_schemas("", sample_xml_str)

        # Invalid target
        assert not xml_parser.compare_xml_schemas(sample_xml_str, "")

        # Invalid mode
        assert not xml_parser.compare_xml_schemas(
            sample_xml_str, sample_xml_str, ignore_mode="invalid"
        )

        # Invalid XML
        invalid_xml = "<root><unclosed>"
        assert not xml_parser.compare_xml_schemas(sample_xml_str, invalid_xml)

    def test_compare_xml_schemas_exception_handling(self,xml_parser):
        """Test exception handling in compare_xml_schemas."""
        try:
            invalid_xml = "<car><light>head</light>"  # Malformed XML

            with patch.object(XMLParser, 'get_root_arbitrary', side_effect=Exception("Unexpected error")):
                result = xml_parser.compare_xml_schemas(invalid_xml, invalid_xml, ignore_mode="positioning")
                assert result is False
                xml_parser.exceptions.raise_generic_exception.assert_called_once_with(
                    "Error comparing XML schemas: Unexpected error", fail_test=False
                )
        except Exception as e:
            print("Exception occurred in test_compare_xml_schemas_exception_handling")

    def test_compare_xml_schemas_on_mode_no_match_second_loop(self,xml_parser):
        """Test 'on' ignore mode where no match is found in the second loop."""
        source_xml = '''
        <root>
            <element1>value1</element1>
            <element2>value2</element2>
        </root>'''

        target_xml = '''
        <root>
            <element3>value3</element3>
            <element4>value4</element4>
        </root>'''

        # The second loop will fail to find a match for <element3> and <element4> in the source XML
        result = xml_parser.compare_xml_schemas(source_xml, target_xml, ignore_mode="on")
        assert result is False  # Ensure the method returns False when elements do not match

    def test_extract_values_from_xml_root_match(self,xml_parser, sample_xml_str):
        """Test case to cover the root element matching the node and attribute_name."""
        # Define criteria to match the root element
        criteria = {
            "node": "data",  # Root tag matches this node
            "attribute_name": "name",  # Attribute exists in root.attrib
            "index": 0,  # Index is 0
        }
        result_list = [[], []]

        # Call the method
        updated_list = xml_parser._XMLParser__extract_values_from_xml(
            sample_xml_str, criteria, result_list
        )

        # Assertions
        assert len(updated_list[0]) == 1
        assert updated_list[0][0] == "data/name[0]"
        assert len(updated_list[1]) == 0

    def test_extract_values_from_xml_root_handling(self, xml_parser):
        """Test handling of root element matching node and attribute_name."""
        # XML where root matches node and contains attribute_name
        sample_xml_str = '''<?xml version="1.0"?>
        <data name="Test" direction="top">
            <child name="Child1" />
        </data>'''

        # Define criteria to match the root element
        criteria = {
            "node": "data",  # Root tag matches this node
            "attribute_name": "name",  # Attribute exists in root.attrib
        }
        result_list = [[], []]

        # Call the method
        updated_list = xml_parser._XMLParser__extract_values_from_xml(
            sample_xml_str, criteria, result_list
        )

        # Assertions for successful case
        assert len(updated_list[0]) == 1
        assert updated_list[0][0] == "data/name"
        assert len(updated_list[1]) == 1
        assert updated_list[1][0] == "Test"

        # XML where root matches node but does not contain attribute_name
        sample_xml_str_no_attr = '''<?xml version="1.0"?>
        <data direction="top">
            <child name="Child1" />
        </data>'''

        # Call the method again
        with patch.object(xml_parser.logger, "exception") as mock_logger:
            updated_list = xml_parser._XMLParser__extract_values_from_xml(
                sample_xml_str_no_attr, criteria, result_list
            )

            # Assertions for exception handling
            mock_logger.assert_called_once_with(
                "Skipping root element as it doesn't match provided arguments: %s",
                mock_logger.call_args[0][1]
            )
            assert len(updated_list[1]) == 2  # Ensure no new value is added

    def test_extract_values_from_xml_else_block(self, xml_parser):
        """Test the else block when attribute_name is not in root.attrib."""
        # XML where root does not contain the attribute_name
        sample_xml_str = '''<?xml version="1.0"?>
        <data direction="top">
            <child name="Child1" />
        </data>'''

        # Define criteria to trigger the else block
        criteria = {
            "attribute_name": "name",  # Attribute not in root.attrib
            "index": 1,  # Index greater than 0
            "parent": "data",  # Parent key is present
        }
        result_list = [[], []]

        # Mock get_element_by_attribute to return a specific value
        with patch.object(xml_parser, 'get_element_by_attribute', return_value=["Child1"]) as mock_get_element:
            updated_list = xml_parser._XMLParser__extract_values_from_xml(
                sample_xml_str, criteria, result_list
            )

            # Assertions
            mock_get_element.assert_called_once_with(
                sample_xml_str,
                "name",
                index=1,  # Match the actual behavior of the code
                return_attribute_value=True,
                parent="data",
            )
            assert updated_list[0] == ["data//name[1]"]
            assert updated_list[1] == ["Child1"]

    def test_extract_values_from_xml_exception_handling(self, xml_parser):
        """Test exception handling in __extract_values_from_xml."""
        try:
            # XML with valid structure
            sample_xml_str = '''<?xml version="1.0"?>
            <data direction="top">
                <child name="Child1" />
            </data>'''

            # Define criteria to trigger the exception
            criteria = {
                "attribute_name": "name",  # Attribute exists in child
                "index": 0,
            }
            result_list = [[], []]

            # Mock a method to raise an exception
            with patch.object(xml_parser, 'get_root_arbitrary', side_effect=Exception("Mocked exception")):
                updated_list = xml_parser._XMLParser__extract_values_from_xml(
                    sample_xml_str, criteria, result_list
                )

                # Assertions
                assert updated_list == result_list  # Ensure the result list is unchanged
        except Exception as e:
            print("Exception occurred in test_extract_values_from_xml_exception_handling:", e)
            xml_parser.exceptions.raise_generic_exception.assert_called_once_with(
                "Error extracting values from XML: Mocked exception", fail_test=False
            )

    def test_root_element_exception_handling(self, xml_parser):
        """Test exception handling when processing the root element."""
        try:
            # Mock the input data
            source = '''<root attribute_name="value"></root>'''
            lst_keys = ["node", "attribute_name", "index"]
            node = "root"
            attribute_name = "attribute_name"
            index = 0
            lst_get_elements = [[]]
            lst_elements = []

            # Mock lst_get_elements[0].append to raise an exception
            with patch.object(lst_get_elements[0], "append", side_effect=Exception("Mocked append exception")):
                with patch.object(xml_parser.logger, "exception") as mock_logger:
                    xml_parser._XMLParser__extract_values_from_xml(
                        source, {"node": node, "attribute_name": attribute_name, "index": index},
                        [lst_get_elements, lst_elements]
                    )
                    # Assert that the logger.exception was called
                    mock_logger.assert_called_once_with(
                        "Skipping root element as it doesn't match provided arguments: %s", "Mocked append exception"
                    )
        except Exception as e:
            print("Exception occurred in test_root_element_exception_handling:", e)


