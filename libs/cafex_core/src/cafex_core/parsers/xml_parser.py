"""
Module providing XML parsing capabilities for the CAFEX framework.

This module provides a robust XML parser with methods to extract and analyze XML content from files
or strings. It supports XPath queries, element extraction, and attribute access.
"""

import re
from typing import Any, Dict, List, Optional, Union

from lxml import etree, objectify

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.utils.exceptions import CoreExceptions


class XMLParser:
    """
    A modern XML parser for extracting and analyzing XML data.

    This class provides methods to parse XML content from files or strings and extract data
    using various methods including XPath, element names, and attribute-based searches.

    Features:
        - XML file and string parsing with namespace handling
        - XPath querying support
        - Element access by name, ancestors, or attributes
        - Element existence verification
        - Schema comparison capabilities

    Attributes:
        logger: Logger instance for debug/error logging
        exceptions: Exception handler for standardized error handling

    Example:
        >>> parser = XMLParser()
        >>> root = parser.get_root_arbitrary("data.xml")
        >>> element_text = parser.get_element_by_xpath("data.xml", ".//rank")
    """

    def __init__(self) -> None:
        """Initialize the XML parser with logging and exception handling."""
        self.logger = CoreLogger(name=__name__).get_logger()
        self.exceptions = CoreExceptions()

    def clean_namespace(self, root: etree.Element) -> None:
        """
        Remove namespaces from an XML element tree.

        This simplifies working with XML by removing namespace prefixes from element tags,
        making them easier to reference in XPath expressions.

        Args:
            root: The XML element tree to clean namespaces from

        Raises:
            Exception: If any errors occur during processing

        Examples:
            >>> parser = XMLParser()
            >>> root_ = parser.get_root_arbitrary("data.xml")
            >>> parser.clean_namespace(root_)
            >>> # Now all elements can be accessed without namespace prefixes
        """
        try:
            if root is None:
                self.exceptions.raise_generic_exception(
                    "Cannot clean namespaces: root element cannot be None", fail_test=False
                )
                return None

            objectify.deannotate(root, cleanup_namespaces=True)
            for elem in root.iter():
                if not hasattr(elem.tag, "find"):
                    continue
                i = elem.tag.find("}")
                if i >= 0:
                    elem.tag = elem.tag[i + 1:]
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error in removing namespaces from XML: {str(e)}", fail_test=False
            )
            return None

    def get_root_arbitrary(self, source: str) -> etree.Element:
        """
        Parse XML data from a file or string and return the root element.

        This method automatically detects whether the source is a file path or XML string
        and parses it accordingly.

        Args:
            source: The path to the XML file or the XML string itself

        Returns:
            The root element of the parsed XML tree

        Raises:
            Exception: If parsing fails or if source is invalid

        Examples:
            >>> parser = XMLParser()
            >>> # Parse from file
            >>> root_file = parser.get_root_arbitrary("data.xml")
            >>> # Parse from string
            >>> xml_str = "<data><item>value</item></data>"
            >>> root_str = parser.get_root_arbitrary(xml_str)
        """
        try:
            if not source:
                self.exceptions.raise_generic_exception(
                    "Cannot parse XML: source cannot be empty or None", fail_test=False
                )
                return None

            if source.endswith(".xml"):
                try:
                    tree = etree.parse(source)
                    strip = (etree.Comment, etree.ProcessingInstruction)
                    etree.strip_elements(tree, *strip, **dict(with_tail=False))
                    return tree.getroot()
                except (IOError, etree.XMLSyntaxError) as e:
                    self.exceptions.raise_generic_exception(
                        f"Error reading or parsing XML file '{source}': {str(e)}", fail_test=False
                    )
                    return None
            else:
                try:
                    return etree.fromstring(
                        source.encode("utf-8") if isinstance(source, str) else source
                    )
                except etree.XMLSyntaxError as e:
                    self.exceptions.raise_generic_exception(
                        f"Error parsing XML string: {str(e)}", fail_test=False
                    )
                    return None
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Unexpected error parsing XML: {str(e)}", fail_test=False
            )
            return None

    def get_elements(self, source: str, xpath: str) -> list[etree.Element]:
        """
        Extract a list of XML elements matching the given XPath expression.

        This method parses the XML data from the source, applies namespace cleaning,
        and then uses the XPath expression to locate and return a list of matching elements.

        Args:
            source: The path to the XML file or the XML string itself
            xpath: The XPath expression to search for

        Returns:
            A list of Element objects representing the matching XML elements

        Raises:
            Exception: If XPath is invalid or if parsing fails

        Examples:
            >>> parser = XMLParser()
            >>> elements = parser.get_elements("data.xml", ".//item")
            >>> for element in elements:
            >>>     print(element.tag)
        """
        try:
            if not source:
                self.exceptions.raise_generic_exception(
                    "Cannot get elements: source cannot be empty or None", fail_test=False
                )
                return []

            if not xpath:
                self.exceptions.raise_generic_exception(
                    "Cannot get elements: xpath cannot be empty or None", fail_test=False
                )
                return []

            root = self.get_root_arbitrary(source)
            if root is None:
                return []

            self.clean_namespace(root)
            try:
                return root.xpath(xpath)
            except etree.XPathError as e:
                self.exceptions.raise_generic_exception(
                    f"Invalid XPath expression '{xpath}': {str(e)}", fail_test=False
                )
                return []
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error extracting elements using XPath '{xpath}': {str(e)}", fail_test=False
            )
            return []

    def get_element_by_xpath(self, source: str, xpath: str = ".") -> Optional[str]:
        """
        Extract the text content of the first element matching the given XPath expression.

        This method parses the XML data from the source, applies namespace cleaning,
        and then uses the XPath expression to locate and return the text content of the first matching element.

        Args:
            source: The path to the XML file or the XML string itself
            xpath: The XPath expression to search for

        Returns:
            The text content of the first matching element, or None if no element is found

        Examples:
            >>> parser = XMLParser()
            >>> # Get content of third country's rank element
            >>> text = parser.get_element_by_xpath("countries.xml", ".//country[3]/rank")
        """
        try:
            if not source or not xpath:
                self.exceptions.raise_generic_exception(
                    "Cannot get element by XPath: source and xpath must be provided",
                    fail_test=False,
                )
                return None

            elements = self.get_elements(source, xpath)
            return elements[0].text if elements else None
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting element by XPath '{xpath}': {str(e)}", fail_test=False
            )
            return None

    def get_element_by_ancestors(self, source: str, parent: str, child: str) -> List[str]:
        """
        Extract the text content of all child elements within the specified parent element.

        This method parses the XML data from the source, applies namespace cleaning,
        and then iterates through the XML tree to find all child elements within the specified parent element.
        It returns a list containing the text content of each matching child element.

        Args:
            source: The path to the XML file or the XML string itself
            parent: The name of the parent element
            child: The name of the child element

        Returns:
            A list of strings representing the text content of all matching child elements

        Examples:
            >>> parser = XMLParser()
            >>> # Get all rank elements under country elements
            >>> texts = parser.get_element_by_ancestors("countries.xml", "country", "rank")
        """
        try:
            if not source or not parent or not child:
                self.exceptions.raise_generic_exception(
                    "Cannot get elements by ancestors: source, parent, and child must all be provided",
                    fail_test=False,
                )
                return []

            root = self.get_root_arbitrary(source)
            if root is None:
                return []

            self.clean_namespace(root)

            child_nodes = []
            for parent_element in root.iter(parent):
                for child_element in parent_element.iter(child):
                    if child_element.text is not None:
                        child_nodes.append(child_element.text)
                    else:
                        child_nodes.append("")
            return child_nodes
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting elements by ancestors (parent: {parent}, child: {child}): {str(e)}",
                fail_test=False,
            )
            return []

    def get_element_by_name(
        self, source: str, child: str, index: Optional[int] = None, parent: Optional[str] = None
    ) -> Union[str, List[str]]:
        """
        Extract the text content of elements matching the given child element name.

        This method parses the XML data from the source, applies namespace cleaning,
        and then searches for elements with the specified child name.

        Args:
            source: The path to the XML file or the XML string itself
            child: The name of the child element to search for
            index: (Optional) The index of the specific child element to extract (0-based)
            parent: (Optional) The name of the parent element to narrow down the search

        Returns:
            The text content of the matching child element (if index is provided)
            or a list of text content of all matching child elements

        Examples:
            >>> parser = XMLParser()
            >>> # Get all rank elements
            >>> ranks = parser.get_element_by_name("countries.xml", "rank")
            >>> # Get second rank element
            >>> second_rank = parser.get_element_by_name("countries.xml", "rank", index=1)
            >>> # Get rank elements under country elements
            >>> country_ranks = parser.get_element_by_name(
            ...     "countries.xml", "rank", parent="country"
            ... )
        """
        try:
            if not source or not child:
                self.exceptions.raise_generic_exception(
                    "Cannot get element by name: source and child must be provided", fail_test=False
                )
                return [] if index is None else ""

            root = self.get_root_arbitrary(source)
            if root is None:
                return [] if index is None else ""

            self.clean_namespace(root)

            child_nodes = []
            if parent is None:
                for element in root.iter():
                    if child in element.tag:
                        child_nodes.append(element.text or "")
            else:
                for parent_element in root.iter(parent):
                    for child_element in parent_element.iter(child):
                        child_nodes.append(child_element.text or "")

            if index is not None:
                if not child_nodes or index < 0 or index >= len(child_nodes):
                    self.exceptions.raise_generic_exception(
                        f"Index {index} out of range for elements named '{child}'", fail_test=False
                    )
                    return ""
                return child_nodes[index]

            return child_nodes
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting element by name '{child}': {str(e)}", fail_test=False
            )
            return [] if index is None else ""

    def get_element_by_index(self, source: str, child: str, index: int) -> str:
        """
        Extract the text content of the child element at the specified index.

        Args:
            source: The path to the XML file or the XML string itself
            child: The name of the child element to search for
            index: The index of the specific child element to extract (0-based)

        Returns:
            The text content of the child element at the specified index

        Examples:
            >>> parser = XMLParser()
            >>> # Get the third rank element
            >>> third_rank = parser.get_element_by_index("countries.xml", "rank", 2)
        """
        if not source:
            raise ValueError("source cannot be empty or None")
        if not child:
            raise ValueError("child cannot be empty or None")
        if not isinstance(index, int):
            raise ValueError("index must be an integer.")
        try:
            result = self.get_element_by_name(source, child, index=index)
            if isinstance(result, list):
                return result[0] if result else ""
            return result
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting element '{child}' at index {index}: {str(e)}", fail_test=False
            )
            return ""

    def get_attribute(
        self,
        source: str,
        tag: str,
        attribute: str,
        index: Optional[int] = None,
        parent: Optional[str] = None,
        return_attribute_value: bool = False,
    ) -> Union[str, List[str]]:
        """
        Extract attribute values or element text content based on tag and attribute.

        This method searches for elements matching the specified tag and attribute,
        and extracts either the attribute values or the element text content.

        Args:
            source: The path to the XML file or the XML string itself
            tag: The name of the XML tag to search for
            attribute: The name of the attribute to extract or filter by
            index: (Optional) The index of the specific element to extract (0-based)
            parent: (Optional) The name of the parent element to narrow down the search
            return_attribute_value: If True, return the attribute value; if False, return element text

        Returns:
            The extracted value (attribute value or text content) of the matching element(s)

        Examples:
            >>> parser = XMLParser()
            >>> # Get the text content of elements with the name attribute
            >>> values = parser.get_attribute("countries.xml", "neighbor", "name")
            >>> # Get the attribute value instead of text content
            >>> attr_values = parser.get_attribute(
            ...     "countries.xml", "neighbor", "name", return_attribute_value=True
            ... )
            >>> # Get a specific element by index
            >>> specific = parser.get_attribute(
            ...     "countries.xml", "neighbor", "name", index=1
            ... )
        """
        try:
            if not source or not tag or not attribute:
                self.exceptions.raise_generic_exception(
                    "Cannot get attribute: source, tag, and attribute must all be provided",
                    fail_test=False,
                )
                return [] if index is None else ""

            xpath = f".//{parent}/{tag}[@{attribute}]" if parent else f".//{tag}[@{attribute}]"
            elements = self.get_elements(source, xpath)

            extracted_values = []
            for element in elements:
                if return_attribute_value:
                    extracted_values.append(element.get(attribute) or "")
                else:
                    extracted_values.append(element.text or "")

            if index is not None:
                if index < 0 or index >= len(extracted_values):
                    self.exceptions.raise_generic_exception(
                        f"Index {index} out of range for elements with tag '{tag}' and attribute '{attribute}'",
                        fail_test=False,
                    )
                    return ""
                return extracted_values[index]

            return extracted_values
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting attribute '{attribute}' from tag '{tag}': {str(e)}", fail_test=False
            )
            return [] if index is None else ""

    def get_element_count(self, source: str, xpath: str = ".") -> int:
        """
        Count the number of XML elements matching the given XPath expression.

        Args:
            source: The path to the XML file or the XML string itself
            xpath: The XPath expression to search for

        Returns:
            The number of XML elements matching the XPath expression

        Examples:
            >>> parser = XMLParser()
            >>> # Count all rank elements
            >>> element_count = parser.get_element_count("countries.xml", ".//rank")
        """
        try:
            if not source or not xpath:
                self.exceptions.raise_generic_exception(
                    "Cannot get element count: source and xpath must be provided", fail_test=False
                )
                return 0

            elements = self.get_elements(source, xpath)
            return len(elements)
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error counting elements with XPath '{xpath}': {str(e)}", fail_test=False
            )
            return 0

    def element_should_exist(self, source: str, identifier: str) -> bool:
        """
        Check if at least one element matching the given identifier exists in the XML data.

        This method supports two types of identifiers:
        * XPath expressions: If the identifier starts with ".", it is treated as an XPath expression
        * Element names: Otherwise, it is treated as the name of an XML element

        Args:
            source: The path to the XML file or the XML string itself
            identifier: The XPath expression or element name to search for

        Returns:
            True if at least one matching element is found, False otherwise

        Examples:
            >>> parser = XMLParser()
            >>> # Check if a specific element exists using XPath
            >>> exists_xpath = parser.element_should_exist(
            ...     "countries.xml", ".//country[3]/rank"
            ... )
            >>> # Check if any rank elements exist
            >>> exists_name = parser.element_should_exist("countries.xml", "rank")
        """
        try:
            if not source or not identifier:
                self.exceptions.raise_generic_exception(
                    "Cannot check element existence: source and identifier must be provided",
                    fail_test=False,
                )
                return False

            if identifier.startswith("."):
                count = self.get_element_count(source, identifier)
                return count > 0

            elements = self.get_element_by_name(source, identifier)
            return len(elements) > 0 if isinstance(elements, list) else elements != ""
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error checking existence of element '{identifier}': {str(e)}", fail_test=False
            )
            return False

    def element_should_not_exist(self, source: str, identifier: str) -> bool:
        """
        Check if no element matching the given identifier exists in the XML data.

        This method supports two types of identifiers:
        * XPath expressions: If the identifier starts with ".", it is treated as an XPath expression
        * Element names: Otherwise, it is treated as the name of an XML element

        Args:
            source: The path to the XML file or the XML string itself
            identifier: The XPath expression or element name to search for

        Returns:
            True if no matching element is found, False otherwise

        Examples:
            >>> parser = XMLParser()
            >>> # Check if a specific element doesn't exist using XPath
            >>> not_exists_xpath = parser.element_should_not_exist(
            ...     "countries.xml", ".//country[3]/invalid"
            ... )
            >>> # Check if no invalid elements exist
            >>> not_exists_name = parser.element_should_not_exist("countries.xml", "invalid")
        """
        try:
            return not self.element_should_exist(source, identifier)
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error checking non-existence of element '{identifier}': {str(e)}", fail_test=False
            )
            return False

    def find_all(self, source: str, xpath: str) -> list[etree.Element]:
        """
        Find all XML elements matching the given XPath expression.

        This method is similar to get_elements but uses findall() instead of xpath().

        Args:
            source: The path to the XML file or the XML string itself
            xpath: The XPath expression to search for

        Returns:
            A list of Element objects representing all matching XML elements

        Examples:
            >>> parser = XMLParser()
            >>> # Find all rank elements
            >>> elements = parser.find_all("countries.xml", ".//rank")
        """
        try:
            if not source or not xpath:
                self.exceptions.raise_generic_exception(
                    "Cannot find elements: source and xpath must be provided", fail_test=False
                )
                return []

            root = self.get_root_arbitrary(source)
            if root is None:
                return []

            self.clean_namespace(root)
            xpath = self._get_xpath(xpath)
            return root.findall(xpath)
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error finding elements with XPath '{xpath}': {str(e)}", fail_test=False
            )
            return []

    def _get_xpath(self, xpath) -> str:
        """
        Ensure the provided xpath is a string.

        Args:
            xpath: The XPath expression or identifier

        Returns:
            The xpath as a string

        Raises:
            ValueError: If the xpath is empty
            TypeError: If the xpath is not a string or cannot be converted to one
        """
        try:
            if not xpath:
                self.exceptions.raise_generic_exception(
                    "XPath cannot be empty or None", fail_test=False
                )
                return ""

            if isinstance(xpath, str):
                return xpath

            try:
                return str(xpath)
            except (TypeError, ValueError) as e:
                self.exceptions.raise_generic_exception(
                    f"XPath must be a string or convertible to a string: {str(e)}", fail_test=False
                )
                return ""

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error processing XPath: {str(e)}", fail_test=False
            )
            return ""

    def get_xml_result(
        self,
        xml_data: str,
        node: Optional[str] = None,
        node_xpath: Optional[str] = None,
        ancestor: Optional[str] = None,
        child: Optional[str] = None,
    ) -> Union[str, List[str]]:
        """
        Extract values from XML data based on different search criteria.

        This method provides various options for extracting values from XML data:
        * By Node Name: Extract the text content of the first element with that name
        * By XPath: Extract the text content of the first element matching the XPath expression
        * By Ancestor-Child Relationship: Extract the text content of child elements within parent elements

        Args:
            xml_data: The XML data as a string or xml file path
            node: (Optional) The name of the XML node to extract the value from
            node_xpath: (Optional) The XPath expression to search for
            ancestor: (Optional) The name of the ancestor element
            child: (Optional) The name of the child element

        Returns:
            The extracted value(s) based on the search criteria

        Examples:
            >>> parser = XMLParser()
            >>> # Get value using node name
            >>> node_value = parser.get_xml_result(xml_data, node="rank")
            >>> # Get value using XPath
            >>> xpath_value = parser.get_xml_result(xml_data, node_xpath="//country/rank")
            >>> # Get values using ancestor-child relationship
            >>> child_values = parser.get_xml_result(
            ...     xml_data, ancestor="country", child="rank"
            ... )
        """
        try:
            if sum(x is not None for x in [node, node_xpath, ancestor]) > 1:
                self.exceptions.raise_generic_exception(
                    "Only one of 'node', 'node_xpath', or 'ancestor' should be provided",
                    fail_test=False,
                )
                return ""

            if ancestor and not child:
                self.exceptions.raise_generic_exception(
                    "Both 'ancestor' and 'child' must be provided together", fail_test=False
                )
                return ""

            if node:
                return self.get_element_by_name(xml_data, node)
            elif node_xpath:
                return self.get_element_by_xpath(xml_data, node_xpath) or ""
            elif ancestor and child:
                return self.get_element_by_ancestors(xml_data, ancestor, child)
            else:
                self.exceptions.raise_generic_exception(
                    "Invalid search criteria. Please provide valid parameters", fail_test=False
                )
                return ""
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error extracting XML result: {str(e)}", fail_test=False
            )
            return ""

    def __get_formatted_list(self, values: List[List]) -> List[Union[str, List[Any]]]:
        """
        Format a list of values for structured output.

        Args:
            values: A list of lists where each inner list contains values to be paired

        Returns:
            A new list of lists where each inner list contains a pair of values from the input list

        Raises:
            ValueError: If the input list is empty
        """
        try:
            if not values:
                self.exceptions.raise_generic_exception("Cannot format empty list", fail_test=False)
                return []

            lst_return_list = [list(pair) for pair in zip(*values)]
            return lst_return_list
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error formatting list: {str(e)}", fail_test=False
            )
            return []

    @staticmethod
    def _create_empty_lists(size: int) -> List[List[Any]]:
        """
        Create a list of empty lists with the specified size.

        Args:
            size: The desired number of inner lists

        Returns:
            A list of empty lists with the specified size

        Examples:
            >>> parser = XMLParser()
            >>> empty_lists = parser._create_empty_lists(3)
            >>> # Result: [[], [], []]
        """
        try:
            if size <= 0:
                raise ValueError("Size must be a positive integer")
            return [[] for _ in range(size)]
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid size for list creation: {str(e)}")

    def get_element_by_attribute(
        self,
        source: str,
        attribute: str,
        index: Optional[int] = None,
        parent: Optional[str] = None,
        return_attribute_value: bool = False,
    ) -> Union[str, List[str]]:
        """
        Extract attribute values or element text content based on the given attribute.

        This method parses the XML data, cleans namespaces, and then searches for elements
        with the specified attribute.

        Args:
            source: The path to the XML file or the XML string itself
            attribute: The name of the attribute to extract or filter by
            index: (Optional) The index of the specific element to extract (0-based)
            parent: (Optional) The name of the parent element to narrow down the search
            return_attribute_value: If True, return attribute value; if False, return element text

        Returns:
            The extracted value(s) of the matching element(s)

        Examples:
            >>> parser = XMLParser()
            >>> # Get text content of all elements with the 'name' attribute
            >>> texts = parser.get_element_by_attribute("countries.xml", "name")
            >>> # Get the value of the 'name' attribute instead
            >>> values = parser.get_element_by_attribute(
            ...     "countries.xml", "name", return_attribute_value=True
            ... )
            >>> # Get a specific element by index
            >>> specific = parser.get_element_by_attribute(
            ...     "countries.xml", "name", index=1
            ... )
        """
        try:
            if not source or not attribute:
                self.exceptions.raise_generic_exception(
                    "Cannot get element by attribute: source and attribute must be provided",
                    fail_test=False,
                )
                return [] if index is None else ""

            xpath = f".//{parent}/*[@{attribute}]" if parent else f".//*[@{attribute}]"
            elements = self.get_elements(source, xpath)

            extracted_values = []
            for element in elements:
                if return_attribute_value:
                    extracted_values.append(element.get(attribute) or "")
                else:
                    extracted_values.append(element.text or "")

            if index is not None:
                if not extracted_values or index < 0 or index >= len(extracted_values):
                    self.exceptions.raise_generic_exception(
                        f"Index {index} out of range for elements with attribute '{attribute}'",
                        fail_test=False,
                    )
                    return ""
                return extracted_values[index]
            else:
                return extracted_values
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting element by attribute '{attribute}': {str(e)}", fail_test=False
            )
            return [] if index is None else ""

    def get_values_from_xml(
        self,
        source: str,
        extraction_criteria: Union[List[Dict], Dict],
        formatting_required: bool = False,
    ) -> Union[List, List[List[Any]]]:
        """
        Extract values from XML data based on various criteria and formatting options.

        This method allows you to specify extraction criteria as either a list of dictionaries
        or a single dictionary. Each dictionary defines the criteria for extracting a specific
        value from the XML data.

        Args:
            source: The path to the XML file or the XML string itself
            extraction_criteria: Criteria defining what values to extract (dict or list of dicts)
                Supported keys include:
                * "node": The name of the XML node to extract the value from
                * "parent": The name of the parent element
                * "attribute_name": The name of the attribute to extract the value from
                * "index": The index of the specific element or attribute to extract (0-based)
            formatting_required: Whether to return a formatted structure or standard list

        Returns:
            A list of lists containing the extracted values, formatted according to the
            formatting_required parameter

        Examples:
            >>> parser = XMLParser()
            >>> # Extract multiple values with different criteria
            >>> values = parser.get_values_from_xml(
            ...     "countries.xml",
            ...     [
            ...         {"node": "rank"},
            ...         {"node": "country", "attribute_name": "name", "index": 0},
            ...         {"attribute_name": "direction"}
            ...     ]
            ... )
            >>> # Extract a single value
            >>> value = parser.get_values_from_xml(
            ...     "countries.xml",
            ...     {"node": "rank", "parent": "country"}
            ... )
            >>> # Get formatted output
            >>> formatted = parser.get_values_from_xml(
            ...     "countries.xml",
            ...     [{"node": "rank"}, {"attribute_name": "name"}],
            ...     formatting_required=True
            ... )
        """
        try:
            if not source:
                self.exceptions.raise_generic_exception(
                    "Cannot extract values: source XML cannot be empty", fail_test=False
                )
                return []

            if not extraction_criteria:
                self.exceptions.raise_generic_exception(
                    "Cannot extract values: extraction criteria cannot be empty", fail_test=False
                )
                return []

            lst_get_elements = [[], []]

            if isinstance(extraction_criteria, dict):
                lst_get_elements = self.__extract_values_from_xml(
                    source, extraction_criteria, lst_get_elements
                )
            elif isinstance(extraction_criteria, list):
                for item in extraction_criteria:
                    lst_get_elements = self.__extract_values_from_xml(
                        source, item, lst_get_elements
                    )
            else:
                self.exceptions.raise_generic_exception(
                    "Extraction criteria must be a dictionary or list of dictionaries",
                    fail_test=False,
                )
                return []

            return (
                self.__get_formatted_list(lst_get_elements)
                if formatting_required
                else lst_get_elements
            )
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error extracting values from XML: {str(e)}", fail_test=False
            )
            return []

    def __extract_values_from_xml(
        self, source: str, pdict_item: Dict, plst_element_list: List[List]
    ) -> List[List[Any]]:
        """
        Extract values from XML data based on the provided criteria.

        This internal helper method processes a single extraction criterion and appends the
        extracted values to the provided element_list.

        Args:
            source: The path to the XML file or the XML string itself
            pdict_item: A dictionary defining the extraction criteria
            plst_element_list: A list of lists to store the extracted values and identifiers

        Returns:
            The updated element_list with the extracted values and identifiers

        Raises:
            Exception: If the criteria are invalid or conflicting
        """
        try:
            if not source:
                self.exceptions.raise_generic_exception(
                    "Source cannot be empty or None", fail_test=False
                )
                return plst_element_list

            if not pdict_item:
                self.exceptions.raise_generic_exception(
                    "Extraction criteria item cannot be empty", fail_test=False
                )
                return plst_element_list

            if not plst_element_list:
                self.exceptions.raise_generic_exception(
                    "Element list cannot be empty", fail_test=False
                )
                return plst_element_list

            lst_get_elements = plst_element_list
            lst_elements = []
            lst_keys = pdict_item.keys()

            node = pdict_item.get("node")
            parent = pdict_item.get("parent")
            attribute_name = pdict_item.get("attribute_name")
            index = pdict_item.get("index")

            if "node" in lst_keys and "attribute_name" in lst_keys and "index" in lst_keys:
                root = self.get_root_arbitrary(source)
                if (
                    root.tag == node
                    and attribute_name in root.attrib
                    and index == 0
                    and "parent" not in lst_keys
                ):
                    try:
                        lst_get_elements[0].append(f"{node}/{attribute_name}[{index}]")
                        lst_elements.insert(0, root.attrib[attribute_name])
                    except Exception as e:
                        self.logger.exception(
                            "Skipping root element as it doesn't match provided arguments: %s", e
                        )
                else:
                    int_index = index - (
                        root.tag == node
                        and attribute_name in root.attrib
                        and "parent" not in lst_keys
                    )
                    parent_str = parent + "/" if "parent" in lst_keys else ""
                    lst_elements = self.get_attribute(
                        source,
                        node,
                        attribute_name,
                        index=int_index,
                        return_attribute_value=True,
                        parent=parent,
                    )
                    lst_get_elements[0].append(f"{parent_str}{node}/{attribute_name}[{index}]")
                    lst_get_elements[1].append(
                        lst_elements[0]
                        if isinstance(lst_elements, list) and len(lst_elements) == 1
                        else lst_elements
                    )

            elif "node" in lst_keys and "attribute_name" in lst_keys:
                parent_str = parent + "/" if "parent" in lst_keys else ""
                lst_elements = self.get_attribute(
                    source, node, attribute_name, return_attribute_value=True, parent=parent
                )
                lst_get_elements[0].append(f"{parent_str}{node}/{attribute_name}")
                root = self.get_root_arbitrary(source)
                if root.tag == node and "parent" not in lst_keys:
                    try:
                        lst_elements.insert(0, root.attrib[attribute_name])
                    except Exception as e:
                        self.logger.exception(
                            "Skipping root element as it doesn't match provided arguments: %s", e
                        )

                lst_get_elements[1].append(
                    lst_elements[0]
                    if isinstance(lst_elements, list) and len(lst_elements) == 1
                    else lst_elements
                )

            elif "node" in lst_keys and "index" in lst_keys:
                parent_str = parent + "/" if "parent" in lst_keys else ""
                lst_elements = self.get_element_by_name(source, node, index=index, parent=parent)
                lst_get_elements[0].append(f"{parent_str}{node}[{index}]")
                lst_get_elements[1].append(
                    lst_elements[0]
                    if isinstance(lst_elements, list) and len(lst_elements) == 1
                    else lst_elements
                )

            elif "node" in lst_keys:
                parent_str = parent + "/" if "parent" in lst_keys else ""
                lst_elements = self.get_element_by_name(source, node, parent=parent)
                lst_get_elements[0].append(f"{parent_str}{node}")
                lst_get_elements[1].append(
                    lst_elements[0]
                    if isinstance(lst_elements, list) and len(lst_elements) == 1
                    else lst_elements
                )

            elif "attribute_name" in lst_keys and "index" in lst_keys:
                root = self.get_root_arbitrary(source)

                if (attribute_name in root.attrib and index == 0 and "parent" not in lst_keys) or (
                    attribute_name in root.attrib and index == 0 or "parent" not in lst_keys
                ):
                    self.logger.info("Root element identified")
                    lst_get_elements[0].append(f"{attribute_name}[{index}]")
                else:
                    int_index = index - (attribute_name in root.attrib and "parent" not in lst_keys)
                    parent_str = parent + "/" if "parent" in lst_keys else ""
                    lst_elements = self.get_element_by_attribute(
                        source,
                        attribute_name,
                        index=int_index,
                        return_attribute_value=True,
                        parent=parent,
                    )
                    lst_get_elements[0].append(f"{parent_str}/{attribute_name}[{index}]")
                try:
                    if "parent" not in lst_keys:
                        lst_elements.insert(0, root.attrib[attribute_name])
                except Exception as e:
                    self.logger.exception(
                        "Skipping root element as it doesn't match provided arguments: %s", e
                    )
                lst_get_elements[1].append(
                    lst_elements[0]
                    if isinstance(lst_elements, list) and len(lst_elements) == 1
                    else lst_elements
                )

            elif "attribute_name" in lst_keys:
                parent_str = parent + "/" if "parent" in lst_keys else ""
                lst_elements = self.get_element_by_attribute(
                    source, attribute_name, return_attribute_value=True, parent=parent
                )
                lst_get_elements[0].append(f"{parent_str}{attribute_name}")
                root = self.get_root_arbitrary(source)
                try:
                    if attribute_name in root.attrib:
                        lst_elements.insert(0, root.attrib[attribute_name])
                except Exception as e:
                    self.logger.exception(
                        "Skipping root element as it doesn't match provided arguments: %s", e
                    )
                lst_get_elements[1].append(
                    lst_elements[0]
                    if isinstance(lst_elements, list) and len(lst_elements) == 1
                    else lst_elements
                )
            else:
                self.exceptions.raise_generic_exception(
                    "Please provide proper node_name or attribute_name for XML parsing",
                    fail_test=False,
                )

            return lst_get_elements
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error extracting values from XML: {str(e)}", fail_test=False
            )
            return plst_element_list

    def compare_xml_schemas(
        self,
        source_xml: str,
        target_xml: str,
        ignore_mode: str = "on",
    ) -> bool:
        """
        Compare two XML schemas based on the specified ignore mode.

        This method parses the XML data from both sources and then compares the schemas
        according to the chosen ignore mode:

        * "on" (default): Ignores the order and multiplicity of elements
        * "positioning": Considers the order of elements but ignores multiplicity
        * "equal": Requires the schemas to be exactly equal, including order and multiplicity

        Args:
            source_xml: The path to the source XML file or the XML string itself
            target_xml: The path to the target XML file or the XML string itself
            ignore_mode: The comparison mode ("on", "positioning", or "equal")

        Returns:
            True if the schemas match according to the ignore mode, False otherwise

        Examples:
            >>> parser = XMLParser()
            >>> # Compare schemas ignoring order and multiplicity
            >>> match_flexible = parser.compare_xml_schemas(
            ...     source_xml, target_xml, ignore_mode="on"
            ... )
            >>> # Compare schemas considering exact equality
            >>> match_exact = parser.compare_xml_schemas(
            ...     source_xml, target_xml, ignore_mode="equal"
            ... )
        """
        try:
            if not source_xml or not target_xml:
                self.exceptions.raise_generic_exception(
                    "Source and target XML must be provided for comparison", fail_test=False
                )
                return False

            if ignore_mode.lower() not in ("on", "positioning", "equal"):
                self.exceptions.raise_generic_exception(
                    "Invalid ignore_mode. Please choose from 'on', 'positioning', or 'equal'",
                    fail_test=False,
                )
                return False

            regex = r"\[.*?\]"
            source_root = self.get_root_arbitrary(source_xml)
            target_root = self.get_root_arbitrary(target_xml)

            if source_root is None or target_root is None:
                return False

            source_tree = etree.ElementTree(source_root)
            target_tree = etree.ElementTree(target_root)
            flag = False

            if ignore_mode.lower() == "on":
                for e in source_root.iter():
                    flag = False
                    source_result = re.sub(regex, "", source_tree.getpath(e))
                    for f in target_root.iter():
                        target_result = re.sub(regex, "", target_tree.getpath(f))
                        if source_result == target_result:
                            flag = True
                            break
                    if not flag:
                        break
                if flag:
                    for f in target_root.iter():
                        flag = False

                        target_result = re.sub(regex, "", target_tree.getpath(f))
                        for e in source_root.iter():
                            source_result = re.sub(regex, "", source_tree.getpath(e))
                            if target_result == source_result:
                                flag = True
                                break
                        if not flag:
                            break
            elif ignore_mode.lower() == "positioning":
                for e in source_root.iter():
                    flag = False
                    for f in target_root.iter():
                        if source_tree.getpath(e) == target_tree.getpath(f):
                            flag = True
                            break
                    if not flag:
                        break
            elif ignore_mode.lower() == "equal":
                flag = True
                source_elements = list(source_root.iter())
                target_elements = list(target_root.iter())

                if len(source_elements) != len(target_elements):
                    return False

                for e, f in zip(source_elements, target_elements):
                    if source_tree.getpath(e) != target_tree.getpath(f):
                        flag = False
                        break
            return flag
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error comparing XML schemas: {str(e)}", fail_test=False
            )
            return False
