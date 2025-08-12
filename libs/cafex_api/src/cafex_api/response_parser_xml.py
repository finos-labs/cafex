from cafex_core.logging.logger_ import CoreLogger
from cafex_core.parsers.xml_parser import XMLParser
from lxml import etree


class ResponseParserXML:
    """
    Description:
        |  This class provides methods to parse the xml and retrieve values from the xml.

    """

    def __init__(self):
        self.logger = CoreLogger(name=__name__).get_logger()

    def get_root_arbitrary(self, source: str) -> etree.Element:
        """Parses XML data from a file or string and returns the root element.

        Args:
            source: The path to the XML file or the XML string itself.

        Returns:
            The root element of the parsed XML tree.

        Examples:
           1.get_root_arbitrary('Example.xml') as a file object
           2.get_root_arbitrary('xml_string') as a string
        """
        if not source:
            raise ValueError("source cannot be empty or None")
        try:
            obj = XMLParser()
            return obj.get_root_arbitrary(source)
        except Exception as e:
            self.logger.exception("Error in parsing XML data and returning the root element: %s", e)
            raise e

    def get_element_by_xpath(self, source: str, xpath: str) -> str | None:
        """Extracts the text content of the first element matching the given
        XPath expression.

        This method parses the XML data from the source, applies namespace cleaning,
        and then uses the XPath expression to locate and return the text content of the first matching element.

        Args:
            source: The path to the XML file or the XML string itself.
            xpath: The XPath expression to search for.

        Returns:
            The text content of the first matching element, or None if no element is found.

        Examples:
            get_element_by_xpath('Example.xml', './/country[3]/rank')
        """
        try:
            obj = XMLParser()
            return obj.get_element_by_xpath(source, xpath)
        except Exception as e:
            self.logger.exception("Error in extracting the text of the first element: %s", e)
            raise e

    def get_element_by_ancestors(self, source: str, parent: str, child: str) -> list[str]:
        """Extracts the text content of all child elements within the specified
        parent element.

        This method parses the XML data from the source, applies namespace cleaning,
        and then iterates through the XML tree to find all child elements within the specified parent element.
        It returns a list containing the text content of each matching child element.

        Args:
            source: The path to the XML file or the XML string itself.
            parent: The name of the parent element.
            child: The name of the child element.

        Returns:
            A list of strings representing the text content of all matching child elements.

        Examples:
            get_element_by_ancestors('Example.xml', 'country', 'rank')
        """
        if not source:
            raise ValueError("source cannot be empty or None")
        if not parent:
            raise ValueError("parent cannot be empty or None")
        if not child:
            raise ValueError("child cannot be empty or None")
        try:
            obj = XMLParser()
            return obj.get_element_by_ancestors(source, parent, child)
        except Exception as e:
            self.logger.exception(
                "Error in extracting the text of child elements under the parent element: %s", e
            )
            raise e

    def get_element_by_name(self, source: str, child: str) -> str | list[str]:
        """Extracts the text content of elements matching the given child
        element name.

        This method parses the XML data from the source, applies namespace cleaning,
        and then searches for elements with the specified child name.

        Args:
            source: The path to the XML file or the XML string itself.
            child: The name of the child element to search for.

        Returns:
            List of text content of all matching child elements.

        Examples:
          sample xml file

                <?xml version="1.0"?>
                <data name="Test" direction= "top" single ="single_attr" >
                <country name="Liechtenstein">
                <rank name = "Person1" last = "Person2" >1</rank>
                <year year_attr = "year">2008</year>
                <gdp attr_test = "attr_value" direction="E">141100</gdp>
                <neighbor name="Austria" direction="E"/>
                <data name1="Test" single ="single_attr1">123</data>
                <data name="Test1" direction= "bottom">1</data>
                <neighbor name="Switzerland" direction="W">
                    <test name = 'Test123' att_name = 'name to return1'>Test</test>
                </neighbor>
                </country>

          |   get_element_by_name('file1.xml','rank')
        """
        if not source:
            raise ValueError("source cannot be empty or None")
        if not child:
            raise ValueError("child cannot be empty or None")
        try:
            obj = XMLParser()
            return obj.get_element_by_name(source, child)
        except Exception as e:
            self.logger.exception(
                "Error in extracting the text of child elements matching the given name: %s", e
            )
            raise e

    def get_element_by_index(self, source: str, child: str, index: int) -> str:
        """Extracts the text content of the child element at the specified
        index.

        Args:
            source: The path to the XML file or the XML string itself.
            child: The name of the child element to search for.
            index: The index of the specific child element to extract (0-based).

        Returns:
            The text content of the child element at the specified index.

        Examples:
            get_element_by_index('Example.xml', 'rank', 2)
        """
        if not source:
            raise ValueError("source cannot be empty or None")
        if not child:
            raise ValueError("child cannot be empty or None")
        if not isinstance(index, int):
            raise ValueError("index must be an integer.")
        try:
            obj = XMLParser()
            return obj.get_element_by_index(source, child, index)
        except Exception as e:
            self.logger.exception(
                "Error in extracting the text of the child element at the specified index: %s", e
            )
            raise e

    def get_attribute(
        self,
        source: str,
        tag: str,
        attribute: str,
        index: int | None = None,
        parent: str | None = None,
        return_attribute_value: bool = False,
    ) -> str | list[str]:
        """Extracts attribute values or element text content based on tag and
        attribute.

        This method searches for elements matching the specified tag and attribute.
        It offers two extraction options:

        * Attribute Values: If `return_attribute_value` is True
          It returns the value of the specified attribute for each matching element.
        * Element Text Content: If `return_attribute_value` is False (default)
          It returns the text content of each matching element.

        The method can return either:

        * A single string: If an index is provided
          it returns the extracted value (attribute value or text content) of the element at that specific index.
        * A list of strings: If no index is provided
          it returns a list containing the extracted values of all matching elements.

        Args:
            source: The path to the XML file or the XML string itself.
            tag: The name of the XML tag to search for.
            attribute: The name of the attribute to extract the value from (if `return_attribute_value` is True).
            index: (Optional) The index of the specific element to extract (0-based).
            parent: (Optional) The name of the parent element to narrow down the search.
            return_attribute_value: (Optional) True(return attribute value)/False(return text)

        Returns:
            The extracted value (attribute value or text content) of the matching element (if index is provided)
            or a list of extracted values of all matching elements.

        Examples:
          |    get_attribute('file1.xml',"test","att_name")
          |    get_attribute('file1.xml',"test","att_name", index = 2)
          |    get_attribute('file1.xml',"test","att_name", index = 2, parent= 'Country')
          |    get_attribute('file1.xml',"test","att_name", parent = 'Country')
        """
        if not source:
            raise ValueError("source cannot be empty or None")
        if not tag:
            raise ValueError("tag cannot be empty or None")
        if not attribute:
            raise ValueError("attribute cannot be empty or None")
        try:
            obj = XMLParser()
            return obj.get_attribute(source, tag, attribute, index, parent, return_attribute_value)
        except Exception as e:
            self.logger.exception("Error in extracting attribute/text content of element: %s", e)
            raise e

    def element_should_exist(self, source: str, identifier: str) -> bool:
        """Checks if at least one element matching the given identifier exists
        in the XML data.

        This method supports two types of identifiers:

        * XPath expressions: If the identifier starts with ".", it is treated as an XPath expression
        * Element names: Otherwise, it is treated as the name of an XML element

        Args:
            source: The path to the XML file or the XML string itself.
            identifier: The XPath expression or element name to search for.

        Returns:
            True if at least one matching element is found, False otherwise.

        Examples:
            element_should_exist('Example.xml', './/country[3]/rank')
            element_should_exist('Example.xml', 'rank')
        """
        if not source:
            raise ValueError("source cannot be empty or None")
        if not identifier:
            raise ValueError("identifier cannot be empty or None")
        try:
            obj = XMLParser()
            return obj.element_should_exist(source, identifier)
        except Exception as e:
            self.logger.exception("Error in checking the existence of an element: %s", e)
            raise e

    def element_should_not_exist(self, source: str, identifier: str) -> bool:
        """Checks if no element matching the given identifier exists in the XML
        data.

        This method supports two types of identifiers:

        * XPath expressions: If the identifier starts with ".", it is treated as an XPath expression
        * Element names: Otherwise, it is treated as the name of an XML element

        Args:
            source: The path to the XML file or the XML string itself.
            identifier: The XPath expression or element name to search for.

        Returns:
            True if no matching element is found, False otherwise.

        Examples:
            element_should_not_exist('Example.xml', './/country[3]/rank')
            element_should_not_exist('Example.xml', 'rank')
        """
        if not source:
            raise ValueError("source cannot be empty or None")
        if not identifier:
            raise ValueError("identifier cannot be empty or None")
        try:
            obj = XMLParser()
            return obj.element_should_not_exist(source, identifier)
        except Exception as e:
            self.logger.exception("Error in checking the absence of an element: %s", e)
            raise e

    def get_element_count(self, source: str, xpath: str = ".") -> int:
        """Counts the number of XML elements matching the given XPath
        expression.

        This method parses the XML data from the source, applies namespace cleaning,
        and then uses the XPath expression to count the number of matching elements.

        Args:
            source: The path to the XML file or the XML string itself.
            xpath: The XPath expression to search for.

        Returns:
            The number of XML elements matching the XPath expression.

        Examples:
            get_element_count('Example.xml','rank')
        """
        if not source:
            raise ValueError("source cannot be empty or None")
        if not xpath:
            raise ValueError("xpath cannot be empty or None")
        try:
            obj = XMLParser()
            return obj.get_element_count(source, xpath)
        except Exception as e:
            self.logger.exception("Error in counting the number of XML elements: %s", e)
            raise e
