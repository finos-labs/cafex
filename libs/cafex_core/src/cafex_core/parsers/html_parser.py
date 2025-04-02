"""
Module providing HTML parsing capabilities for the CAFEX framework.

This module provides a robust HTML parser with methods to extract and analyze HTML content from
files or strings. It supports both XPath and CSS selectors for element location.
"""

from typing import Dict, List, Optional, Union

from lxml import etree, html
from lxml.html import HtmlElement

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.utils.exceptions import CoreExceptions


class HTMLParser:
    """
    A modern HTML parser for parsing and analyzing HTML content.

    This class provides methods to parse HTML content and extract data using XPath and CSS selectors.
    It includes functionality for table operations, element finding, and attribute access.

    Features:
        - HTML file and string parsing
        - XPath and CSS selector support
        - Table data extraction
        - Element counting and validation
        - Attribute access

    Attributes:
    logger: Logger instance for debug/error logging
    exceptions: Exception handler for standardized error handling

    Example:
        >>> parser = HTMLParser()
        >>> html_content = parser.parse_html_file("table.html")
        >>> text = parser.get_text(html_content, "//table[@id='data']/tr[2]/td")
    """

    def __init__(self) -> None:
        """Initialize the HTML parser with logging and exception handling."""
        self.logger = CoreLogger(name=__name__).get_logger()
        self.exceptions = CoreExceptions()

    def parse_html_file(self, filepath: str) -> Optional[HtmlElement]:
        """
        Parse HTML content from a file.

        Args:
            filepath: Path to the HTML file

        Returns:
            Parsed HTML element tree

        Raises:
            Exception: If file reading or parsing fails

        Examples:
            >>> parser = HTMLParser()
            >>> html_tree = parser.parse_html_file("test.html")
            >>> title = html_tree.xpath("//title/text()")[0]
        """
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                return html.fromstring(file.read())
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Failed to parse HTML file '{filepath}': {str(e)}", fail_test=False
            )
            return None

    def parse_html_data(self, html_content: str) -> Optional[HtmlElement]:
        """
        Parse HTML content from a string.

        Args:
            html_content: HTML content as string

        Returns:
            Parsed HTML element tree

        Raises:
            Exception: If parsing fails

        Examples:
            >>> parser = HTMLParser()
            >>> html_data = '<div><p>Hello</p></div>'
            >>> tree = parser.parse_html_data(html_data)
            >>> text = tree.xpath("//p/text()")[0]
        """
        try:
            return html.fromstring(html_content)
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Failed to parse HTML content: {str(e)}", fail_test=False
            )
            return None

    def __validate_xpath(self, xpath: str) -> str:
        """
        Validate an XPath expression.

        Args:
            xpath: XPath expression to validate

        Returns:
            Validated XPath string

        Raises:
            Exception: If XPath is invalid
        """
        if not xpath:
            raise ValueError("No XPath provided")

        try:
            etree.XPath(xpath)  # pylint: disable=c-extension-no-member
            return xpath
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Invalid XPath expression '{xpath}': {str(e)}", fail_test=False
            )
            return ""

    def __get_element_by_xpath(
        self, html_elem: HtmlElement, xpath: str, get_all: bool = False, index: int = 1
    ) -> Union[HtmlElement, List[HtmlElement], None]:
        """
        Get element(s) using XPath.

        Args:
            html_elem: Parsed HTML element
            xpath: XPath selector
            get_all: Return all matching elements if True
            index: Element index (1-based) when get_all is False

        Returns:
            Single element or list of elements

        Raises:
            Exception: If element not found or invalid index
        """
        try:
            xpath = self.__validate_xpath(xpath)
            elements = html_elem.xpath(xpath)

            if not elements:
                raise ValueError(f"No elements found matching CSS selector: {xpath}")

            if get_all:
                return elements

            if index > len(elements):
                raise IndexError(
                    f"Requested index {index} exceeds number of elements ({len(elements)})"
                )

            return elements[index - 1]
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting element by XPath '{xpath}': {str(e)}", fail_test=False
            )
            return None

    def __get_element_by_css(
        self, html_elem: HtmlElement, css: str, get_all: bool = False, index: int = 1
    ) -> Union[HtmlElement, List[HtmlElement], None]:
        """
        Get element(s) using CSS selector.

        Args:
            html_elem: Parsed HTML element
            css: CSS selector
            get_all: Return all matching elements if True
            index: Element index (1-based) when get_all is False

        Returns:
            Single element or list of elements

        Raises:
            Exception: If element not found or invalid index
        """
        try:
            elements = html_elem.cssselect(css)

            if not elements:
                raise ValueError(f"No elements found matching CSS selector: {css}")

            if get_all:
                return elements

            if index > len(elements):
                raise IndexError(
                    f"Requested index {index} exceeds number of elements ({len(elements)})"
                )

            return elements[index - 1]
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting element by CSS '{css}': {str(e)}", fail_test=False
            )
            return None

    def get_element_by_xpath(
        self, html_tree: HtmlElement, xpath: str, get_all: bool = False, index: int = 1
    ) -> Union[HtmlElement, List[HtmlElement], None]:
        """
        Get element(s) by XPath with public interface.

        Args:
            html_tree: Parsed HTML element
            xpath: XPath selector
            get_all: Return all matching elements if True
            index: Element index (1-based) when get_all is False

        Returns:
            Single element or list of elements

        Examples:
            >>> parser = HTMLParser()
            >>> tree = parser.parse_html_file("test.html")
            >>> # Get single element
            >>> elem = parser.get_element_by_xpath(tree, "//div[@class='content']")
            >>> # Get all elements
            >>> elements = parser.get_element_by_xpath(
            ...     tree,
            ...     "//li[@class='item']",
            ...     get_all=True
            ... )
        """
        try:
            return self.__get_element_by_xpath(html_tree, xpath, get_all=get_all, index=index)
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error finding element by XPath '{xpath}': {str(e)}", fail_test=False
            )
            return None

    def get_element_by_css(
        self, html_tree: HtmlElement, css_selector: str, get_all: bool = False, index: int = 1
    ) -> Union[HtmlElement, List[HtmlElement], None]:
        """
        Get element(s) by CSS selector with public interface.

        Args:
            html_tree: Parsed HTML element
            css_selector: CSS selector
            index: Element index (1-based)
            get_all: Return all matching elements if True
            index: Element index (1-based) when get_all is False

        Returns:
            Single element or list of elements

        Examples:
            >>> parser = HTMLParser()
            >>> tree = parser.parse_html_file("test.html")
            >>> # Get single element
            >>> elem = parser.get_element_by_css(tree, "#main-content")
            >>> # Get all elements
            >>> elements = parser.get_element_by_css(
            ...     tree,
            ...     ".item",
            ...     get_all=True
            ... )
        """
        try:
            return self.__get_element_by_css(html_tree, css_selector, get_all=get_all, index=index)
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error finding element by CSS selector '{css_selector}': {str(e)}", fail_test=False
            )
            return None

    def get_hyperlink_value(
        self,
        html_tree: HtmlElement,
        locator: str,
        locator_type: str = "xpath",
        get_all: bool = False,
        index: int = 1,
    ) -> Union[str, List[str]]:
        """
        Get hyperlink text value(s).

        Args:
            html_tree: Parsed HTML element
            locator: Element locator
            locator_type: Type of locator ("xpath" or "css")
            get_all: Whether to return all matching link texts
            index: Element index when get_all is False

        Returns:
            Single hyperlink text, list of texts, or None if not found

        Examples:
            >>> parser = HTMLParser()
            >>> tree = parser.parse_html_file("test.html")
            >>> # Get single link text
            >>> link_text = parser.get_hyperlink_value(
            ...     tree,
            ...     "//a[@class='nav-link']"
            ... )
            >>> # Get all link texts
            >>> link_texts = parser.get_hyperlink_value(
            ...     tree,
            ...     ".nav-link",
            ...     locator_type="css",
            ...     get_all=True
            ... )
        """
        try:
            if locator_type.lower() == "xpath":
                elements = self.__get_element_by_xpath(html_tree, locator, get_all=True)
            elif locator_type.lower() == "css":
                elements = self.__get_element_by_css(html_tree, locator, get_all=True)
            else:
                raise ValueError(f"Invalid locator type: {locator_type}")

            # Filter for anchor elements
            links = [e for e in elements if e.tag == "a"]

            if not links:
                return [] if get_all else ""

            if get_all:
                return [link.text or "" for link in links]

            if index > len(links):
                raise IndexError(f"Requested index {index} exceeds number of links ({len(links)})")

            return links[index - 1].text or ""
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting hyperlink value from '{locator}': {str(e)}", fail_test=False
            )
            return [] if get_all else ""

    def get_text(
        self, html_tree: HtmlElement, locator: str, locator_type: str = "xpath", index: int = 1
    ) -> str:
        """
        Get text content of an element.

        Args:
            html_tree: Parsed HTML element
            locator: Element locator
            locator_type: Type of locator ("xpath" or "css")
            index: Element index if multiple matches exist

        Returns:
            Text content of the element

        Examples:
            >>> parser = HTMLParser()
            >>> tree = parser.parse_html_file("test.html")
            >>> # Get text using XPath
            >>> heading_text = parser.get_text(tree, "//h1")
            >>> # Get text using CSS
            >>> title_text = parser.get_text(tree, ".title", locator_type="css")
        """
        try:
            if locator_type.lower() == "xpath":
                element = self.__get_element_by_xpath(html_tree, locator, index=index)
            elif locator_type.lower() == "css":
                element = self.__get_element_by_css(html_tree, locator, index=index)
            else:
                raise ValueError(f"Invalid locator type: {locator_type}")

            return element.text or ""
        except Exception as e:
            self.exceptions.raise_generic_exception(str(e), fail_test=False)
            return ""

    def get_cell_value(
        self,
        html_tree: HtmlElement,
        by_locator: bool = True,
        table_xpath: str = "//table",
        xpath: Optional[str] = None,
        css: Optional[str] = None,
        row: Optional[int] = None,
        col: Optional[int] = None,
        table_index: int = 1,
    ) -> str:
        """
        Get value from a table cell.

        Args:
            html_tree: Parsed HTML element
            by_locator: Use XPath/CSS locator if True, row/col indices if False
            table_xpath: XPath to locate the table
            xpath: XPath to locate the cell (if by_locator is True)
            css: CSS selector to locate the cell (if by_locator is True)
            row: Row number (if by_locator is False)
            col: Column number (if by_locator is False)
            table_index: Index of table if multiple tables match table_xpath

        Returns:
            Cell text content

        Examples:
            >>> parser = HTMLParser()
            >>> tree = parser.parse_html_file("table.html")
            >>> # Get cell by xpath
            >>> value_locator = parser.get_cell_value(
            ...     tree,
            ...     xpath="//table[@id='data']/tr[2]/td[3]"
            ... )
            >>> # Get cell by row/column
            >>> value = parser.get_cell_value(
            ...     tree,
            ...     by_locator=False,
            ...     row=2,
            ...     col=3,
            ...     table_xpath="//table[@id='data']"
            ... )
        """
        try:
            if by_locator:
                if not xpath and not css:
                    raise ValueError("Must provide either xpath or css selector")
                if xpath:
                    return self.get_text(html_tree, xpath)
                return self.get_text(html_tree, css, "css")

            if row is None or col is None:
                raise ValueError("Must provide both row and column numbers")

            table = self.__get_element_by_xpath(html_tree, table_xpath, index=table_index)
            cell_xpath = f".//tr[{row}]/td[{col}]"
            cells = table.xpath(cell_xpath)

            if not cells:
                raise ValueError(f"No cell found at row {row}, column {col}")

            return cells[0].text or ""
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting cell value: {str(e)}", fail_test=False
            )
            return ""

    def get_row_data(
        self,
        html_tree: HtmlElement,
        row_number: Optional[int] = None,
        table_xpath: str = "//table",
        row_xpath: Optional[str] = None,
        row_css: Optional[str] = None,
        table_index: int = 1,
    ) -> List[str]:
        """
        Get all cell values from a table row.

        Args:
            html_tree: Parsed HTML element
            row_number: Row number to get data from
            table_xpath: XPath to locate the table
            row_xpath: XPath to locate the row directly
            row_css: CSS selector to locate the row directly
            table_index: Index of table if multiple tables match table_xpath

        Returns:
            List of cell text values from the row

        Examples:
            >>> parser = HTMLParser()
            >>> tree = parser.parse_html_file("table.html")
            >>> # Get row by number
            >>> row_data_by_number = parser.get_row_data(tree, row_number=2)
            >>> # Get row by xpath
            >>> row_data_by_xpath = parser.get_row_data(
            ...     tree,
            ...     row_xpath="//table[@id='data']/tr[2]"
            ... )
        """
        try:
            if row_xpath:
                row = self.__get_element_by_xpath(html_tree, row_xpath)
                cells = row.xpath(".//td")
            elif row_css:
                row = self.__get_element_by_css(html_tree, row_css)
                cells = row.xpath(".//td")
            else:
                if row_number is None:
                    raise ValueError("Must provide row number")
                table = self.__get_element_by_xpath(html_tree, table_xpath, index=table_index)
                row_xpath = f".//tr[{row_number}]"
                rows = table.xpath(row_xpath)
                if not rows:
                    raise ValueError(f"No row found at index {row_number}")
                cells = rows[0].xpath(".//td")

            return [cell.text or "" for cell in cells]

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting row data: {str(e)}", fail_test=False
            )
            return []

    def get_column_data(
        self, html_tree: HtmlElement, table_xpath: str = "//table", table_index: int = 1
    ) -> List[str]:
        """
        Get header/column names from a table.

        Args:
            html_tree: Parsed HTML element
            table_xpath: XPath to locate the table
            table_index: Index of table if multiple tables match

        Returns:
            List of column header texts

        Examples:
            >>> parser = HTMLParser()
            >>> tree = parser.parse_html_file("table.html")
            >>> table_headers = parser.get_column_data(
            ...     tree,
            ...     table_xpath="//table[@id='data']"
            ... )
        """
        try:
            table = self.__get_element_by_xpath(html_tree, table_xpath, index=table_index)

            # Try to find header cells first
            headers = table.xpath(".//th")

            if headers:
                return [header.text or "" for header in headers]

            # Try table header section
            header_row = table.xpath(".//thead//tr[1]//td")
            if header_row:
                return [cell.text or "" for cell in header_row]

            # Fall back to first row
            first_row = table.xpath(".//tr[1]//td")
            return [cell.text or "" for cell in first_row]
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting column data: {str(e)}", fail_test=False
            )
            return []

    def get_row_count(
        self,
        html_tree: HtmlElement,
        table_xpath: str = "//table",
        row_xpath: Optional[str] = None,
        row_css: Optional[str] = None,
        table_index: int = 1,
    ) -> int:
        """
        Get number of rows in a table.

        Args:
            html_tree: Parsed HTML element
            table_xpath: XPath to locate the table
            row_xpath: Optional XPath to locate rows directly
            row_css: Optional CSS selector to locate rows directly
            table_index: Index of table if multiple tables match

        Returns:
            Number of rows found

        Examples:
            >>> parser = HTMLParser()
            >>> tree = parser.parse_html_file("table.html")
            >>> count = parser.get_row_count(
            ...     tree,
            ...     table_xpath="//table[@id='data']"
            ... )
        """
        try:
            if row_xpath:
                rows = self.__get_element_by_xpath(html_tree, row_xpath, get_all=True)
            elif row_css:
                rows = self.__get_element_by_css(html_tree, row_css, get_all=True)
            else:
                table = self.__get_element_by_xpath(html_tree, table_xpath, index=table_index)
                rows = table.xpath(".//tr")

            return len(rows)
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting row count: {str(e)}", fail_test=False
            )
            return 0

    def get_column_count(
        self, html_tree: HtmlElement, table_xpath: str = "//table", table_index: int = 1
    ) -> int:
        """
        Get number of columns in a table.

        Args:
            html_tree: Parsed HTML element
            table_xpath: XPath to locate the table
            table_index: Index of table if multiple tables match

        Returns:
            Number of columns found

        Examples:
            >>> parser = HTMLParser()
            >>> tree = parser.parse_html_file("table.html")
            >>> count = parser.get_column_count(
            ...     tree,
            ...     table_xpath="//table[@id='data']"
            ... )
        """
        try:
            table = self.__get_element_by_xpath(html_tree, table_xpath, index=table_index)

            # Try header cells first
            headers = table.xpath(".//th")
            if headers:
                return len(headers)

            # Try table header section
            header_cells = table.xpath(".//thead//tr[1]//td")
            if header_cells:
                return len(header_cells)

            # Fall back to first row cells
            first_row_cells = table.xpath(".//tr[1]//td")
            return len(first_row_cells)
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting column count: {str(e)}", fail_test=False
            )
            return 0

    def get_all_elements(
        self, html_tree: HtmlElement, tag: str, namespace: Optional[Dict[str, str]] = None
    ) -> List[HtmlElement]:
        """
        Get all elements matching a given tag name.

        Args:
            html_tree: Parsed HTML element
            tag: Tag name or path (e.g., ".//div" or ".//h1")
            namespace: Optional namespace mapping for XML documents

        Returns:
            List of matching elements

        Examples:
            >>> parser = HTMLParser()
            >>> tree = parser.parse_html_file("test.html")
            >>> # Get all divs
            >>> divs = parser.get_all_elements(tree, ".//div")
            >>> # Get all list items
            >>> items = parser.get_all_elements(tree, ".//ul/li")
            >>> # With namespace
            >>> ns = {"svg": "http://www.w3.org/2000/svg"}
            >>> paths = parser.get_all_elements(
            ...     tree,
            ...     ".//svg:path",
            ...     namespace=ns
            ... )
        """
        try:
            elements = html_tree.findall(tag, namespace)
            return elements if elements else []

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting elements with tag '{tag}': {str(e)}", fail_test=False
            )
            return []

    def get_all_elements_text(
        self, html_tree: HtmlElement, tag: str, namespace: Optional[Dict[str, str]] = None
    ) -> List[str]:
        """
        Get text content from all elements matching a tag.

        Args:
            html_tree: Parsed HTML element
            tag: Tag name or path (e.g., ".//div" or ".//h1")
            namespace: Optional namespace mapping for XML documents

        Returns:
            List of text content from matching elements

        Examples:
            >>> parser = HTMLParser()
            >>> tree = parser.parse_html_file("test.html")
            >>> # Get all paragraph texts
            >>> p_texts = parser.get_all_elements_text(tree, ".//p")
            >>> # Get all heading texts
            >>> h1_texts = parser.get_all_elements_text(tree, ".//h1")
        """
        try:
            elements = html_tree.findall(tag, namespace)
            return [element.text or "" for element in elements]

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting text from elements with tag '{tag}': {str(e)}", fail_test=False
            )
            return []

    def get_first_element(
        self, html_tree: HtmlElement, tag: str, namespace: Optional[Dict[str, str]] = None
    ) -> Optional[HtmlElement]:
        """
        Get first element matching a tag name.

        Args:
            html_tree: Parsed HTML element
            tag: Tag name or path (e.g., ".//div" or ".//h1")
            namespace: Optional namespace mapping for XML documents

        Returns:
            First matching element or None if not found

        Examples:
            >>> parser = HTMLParser()
            >>> tree = parser.parse_html_file("test.html")
            >>> # Get first heading
            >>> heading = parser.get_first_element(tree, ".//h1")
            >>> # Get first div with class
            >>> div = parser.get_first_element(tree, ".//div[@class='content']")
            >>> # With namespace
            >>> ns = {"svg": "http://www.w3.org/2000/svg"}
            >>> svg = parser.get_first_element(
            ...     tree,
            ...     ".//svg:svg",
            ...     namespace=ns
            ... )
        """
        try:
            element = html_tree.find(tag, namespace)
            return element if element is not None else None

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting first element with tag '{tag}': {str(e)}", fail_test=False
            )
            return None

    def element_should_exist(
        self, html_tree: HtmlElement, locator: str, locator_type: str = "xpath", index: int = 1
    ) -> bool:
        """
        Check if an element exists.

        Args:
            html_tree: Parsed HTML element
            locator: Element locator
            locator_type: Type of locator ("xpath" or "css")
            index: Element index if multiple matches exist

        Returns:
            True if element exists, False otherwise

        Examples:
            >>> parser = HTMLParser()
            >>> tree = parser.parse_html_file("test.html")
            >>> exists = parser.element_should_exist(
            ...     tree,
            ...     "//div[@class='content']"
            ... )
        """
        try:
            if locator_type.lower() == "xpath":
                elements = html_tree.xpath(locator)
            elif locator_type.lower() == "css":
                elements = html_tree.cssselect(locator)
            else:
                raise ValueError(f"Invalid locator type: {locator_type}")

            return len(elements) >= index

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error checking element existence: {str(e)}", fail_test=False
            )
            return False

    def get_element_count(
        self, html_tree: HtmlElement, locator: str, locator_type: str = "xpath"
    ) -> int:
        """
        Get count of matching elements.

        Args:
            html_tree: Parsed HTML element
            locator: Element locator
            locator_type: Type of locator ("xpath", "css", or "tag")

        Returns:
            Number of matching elements

        Examples:
            >>> parser = HTMLParser()
            >>> tree = parser.parse_html_file("test.html")
            >>> count = parser.get_element_count(
            ...     tree,
            ...     "//div[@class='item']"
            ... )
        """
        try:
            if locator_type.lower() == "xpath":
                return len(html_tree.xpath(locator))
            if locator_type.lower() == "css":
                return len(html_tree.cssselect(locator))
            if locator_type.lower() == "tag":
                return len(html_tree.findall(locator))

            raise ValueError(f"Invalid locator type: {locator_type}")

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting element count: {str(e)}", fail_test=False
            )
            return 0

    def get_attributes(
        self, html_tree: HtmlElement, locator: str, locator_type: str = "xpath", index: int = 1
    ) -> Dict[str, str]:
        """
        Get all attributes of an element.

        Args:
            html_tree: Parsed HTML element
            locator: Element locator
            locator_type: Type of locator ("xpath" or "css")
            index: Element index if multiple matches exist

        Returns:
            Dictionary of attribute names and values

        Examples:
            >>> parser = HTMLParser()
            >>> tree = parser.parse_html_file("test.html")
            >>> attrs = parser.get_attributes(
            ...     tree,
            ...     "//img[@class='logo']"
            ... )
            >>> src = attrs.get('src')
        """
        try:
            if locator_type.lower() == "xpath":
                element = self.__get_element_by_xpath(html_tree, locator, index=index)
            elif locator_type.lower() == "css":
                element = self.__get_element_by_css(html_tree, locator, index=index)
            else:
                raise ValueError(f"Invalid locator type: {locator_type}")

            return dict(element.attrib)

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting element attributes: {str(e)}", fail_test=False
            )
            return {}
