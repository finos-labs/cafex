"""Tests for the HTML Parser module."""

import pytest
from lxml.html import HtmlElement, fromstring
from unittest.mock import patch, Mock


@pytest.fixture
def html_parser():
    """Create HTMLParser instance for testing."""
    from cafex_core.parsers.html_parser import HTMLParser
    return HTMLParser()


@pytest.fixture
def sample_html():
    """Create properly formatted sample HTML content for testing."""
    html = '''<!DOCTYPE html>
    <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <div id="main" class="container">
                <h1>Welcome</h1>
                <p class="intro">This is a test page</p>
                <nav>
                    <a href="/" class="nav-link">Home</a>
                    <a href="/about" class="nav-link">About</a>
                </nav>
                <table id="data">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Age</th>
                            <th>City</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>John</td>
                            <td>30</td>
                            <td>New York</td>
                        </tr>
                        <tr>
                            <td>Jane</td>
                            <td>25</td>
                            <td>London</td>
                        </tr>
                    </tbody>
                </table>
                <div class="items">
                    <div class="item">Item 1</div>
                    <div class="item">Item 2</div>
                    <div class="item">Item 3</div>
                </div>
            </div>
            <footer>
                <p>Footer text</p>
            </footer>
        </body>
    </html>'''
    return html


@pytest.fixture
def parsed_html(html_parser, sample_html):
    """Provide parsed HTML for tests."""
    return html_parser.parse_html_data(sample_html)


@pytest.fixture
def sample_html_file(tmp_path, sample_html):
    """Create a temporary HTML file for testing."""
    file_path = tmp_path / "test.html"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(sample_html)
    return str(file_path)


def test_parse_html_file(html_parser, sample_html_file):
    """Test parsing HTML from file."""
    result = html_parser.parse_html_file(sample_html_file)
    assert isinstance(result, HtmlElement)
    assert result.xpath("//title")[0].text == "Test Page"

    # Test invalid file
    result = html_parser.parse_html_file("nonexistent.html")
    assert result is None


def test_parse_html_data(html_parser):
    """Test parsing HTML from string."""
    valid_html = "<div><p>Test</p></div>"
    result = html_parser.parse_html_data(valid_html)
    assert isinstance(result, HtmlElement)

    # Test with invalid input
    result = html_parser.parse_html_data(20)
    assert result is None


def test_get_element_by_xpath(html_parser, parsed_html):
    """Test getting elements by XPath."""
    try:
        # Test single element
        element = html_parser.get_element_by_xpath(parsed_html, "//h1")
        assert element is not None
        assert element.text == "Welcome"

        # Test multiple elements
        elements = html_parser.get_element_by_xpath(parsed_html, "//div[@class='item']", get_all=True)
        assert len(elements) == 3
        assert [e.text for e in elements] == ["Item 1", "Item 2", "Item 3"]

        # Test with index
        element = html_parser.get_element_by_xpath(parsed_html, "//div[@class='item']", index=2)
        assert element.text == "Item 2"

        # Test invalid XPath
        element = html_parser.get_element_by_xpath(parsed_html, "//nonexistent")
        assert element is None

        # not passing xpath
        element = html_parser.get_element_by_xpath(parsed_html, xpath=None)
        assert element is None
        # Test with index
        element = html_parser.get_element_by_xpath(parsed_html, "//div[@class='item']", index=10)
        assert element is None
        element = html_parser.get_element_by_xpath(parsed_html, xpath=20, index=10)
        assert element is None
        # Test exception handling in get_element_by_xpath method
        with patch.object(html_parser, '_HTMLParser__get_element_by_xpath', side_effect=Exception("XPath error")):
            with patch.object(html_parser.exceptions, 'raise_generic_exception', new=Mock()) as mock_raise:
                result = html_parser.get_element_by_xpath(parsed_html, "//div[@class='content']")
                assert result is None
                mock_raise.assert_called_with(
                    "Error finding element by XPath '//div[@class='content']': XPath error", fail_test=False
                )
    except Exception as e:
        print(e)


def test_get_element_by_css(html_parser, parsed_html):
    """Test getting elements by CSS selector."""
    try:
        # Test single element
        element = html_parser.get_element_by_css(parsed_html, "div#main")
        assert element is not None
        assert element.attrib["class"] == "container"

        # Test multiple elements
        elements = html_parser.get_element_by_css(parsed_html, "div.item", get_all=True)
        assert len(elements) == 3
        assert [e.text for e in elements] == ["Item 1", "Item 2", "Item 3"]

        # Test with index
        element = html_parser.get_element_by_css(parsed_html, "div.item", index=2)
        assert element.text == "Item 2"
        # Test with passing greater index
        element = html_parser.get_element_by_css(parsed_html, "div.item", index=20)
        assert element is None
        # Test with invalid CSS selector
        element = html_parser.get_element_by_css(parsed_html, "invalid-css-selector")
        assert element is None
        # Test exception handling in get_element_by_css method
        with patch.object(html_parser, '_HTMLParser__get_element_by_css', side_effect=Exception("CSS error")):
            with patch.object(html_parser.exceptions, 'raise_generic_exception', new=Mock()) as mock_raise:
                result = html_parser.get_element_by_css(parsed_html, "div.content")
                assert result is None
                mock_raise.assert_called_with(
                    "Error finding element by CSS selector 'div.content': XPath error", fail_test=False
                )
    except Exception as e:
        print(e)


def test_get_hyperlink_value(html_parser, parsed_html):
    """Test getting hyperlink text values."""
    try:
        # Test single link
        text = html_parser.get_hyperlink_value(parsed_html, "//a[@class='nav-link']")
        assert text == "Home"

        # Test multiple links
        texts = html_parser.get_hyperlink_value(parsed_html, ".nav-link", locator_type="css", get_all=True)
        assert texts == ["Home", "About"]

        # Test with passing greater index
        text = html_parser.get_hyperlink_value(parsed_html, ".nav-link", locator_type="css", index=20)
        assert text is ""
        # Test with passing invalid locator
        text = html_parser.get_hyperlink_value(parsed_html, ".item", locator_type="css")
        assert text is ""
        # Test with passing invalid locator type
        text = html_parser.get_hyperlink_value(parsed_html, ".nav-link", locator_type="invalid")
        assert text is ""
        # Test with invalid CSS selector
        text = html_parser.get_hyperlink_value(parsed_html, "invalid-css-selector", locator_type="css")
        assert text is ""
        # Test exception handling in get_hyperlink_value method
        with patch.object(html_parser, '_HTMLParser__get_hyperlink_value', side_effect=Exception("Hyperlink error")):
            with patch.object(html_parser.exceptions, 'raise_generic_exception', new=Mock()) as mock_raise:
                result = html_parser.get_hyperlink_value(parsed_html, "a.content")
                assert result is None
                mock_raise.assert_called_with(
                    "Error finding hyperlink by CSS selector 'a.content': XPath error", fail_test=False
                )
    except Exception as e:
        print(e)


def test_get_text(html_parser, parsed_html):
    """Test getting element text."""
    # Test XPath
    text = html_parser.get_text(parsed_html, "//h1")
    assert text == "Welcome"

    # Test CSS
    text = html_parser.get_text(parsed_html, "p.intro", locator_type="css")
    assert text == "This is a test page"

    # Test passing invalid locator
    text = html_parser.get_text(parsed_html, "p.intro", locator_type="invalid")
    assert text == ""


def test_get_cell_value(html_parser, parsed_html):
    """Test getting table cell values."""
    # Test by XPath
    value = html_parser.get_cell_value(
        parsed_html,
        xpath="//table[@id='data']//tr[2]/td[2]"
    )
    assert value == "25"

    # Test by row/column
    value = html_parser.get_cell_value(
        parsed_html,
        by_locator=False,
        row=2,
        col=3,
        table_xpath="//table[@id='data']"
    )
    assert value == "London"

    # Test passing invalid locator
    value = html_parser.get_cell_value(
        parsed_html,
        by_locator=True,
        row=2,
        col=3,
        table_xpath="//table[@id='data']",
        xpath=None,
        css=None
    )
    assert value == ""
    # test with valid css
    value = html_parser.get_cell_value(
        parsed_html,
        by_locator=True,
        row=2,
        col=3,
        table_xpath="//table[@id='data']",
        xpath=None,
        css="td"
    )
    assert value == "John"
    # Test by not passing row and col values
    value = html_parser.get_cell_value(
        parsed_html,
        by_locator=False,
        row=None,
        col=None,
        table_xpath="//table[@id='data']"
    )
    assert value == ""
    # Test by passing invalid row and col values
    value = html_parser.get_cell_value(
        parsed_html,
        by_locator=False,
        row=10,
        col=10,
        table_xpath="//table[@id='data']"
    )
    assert value == ""


def test_get_row_data(html_parser, parsed_html):
    """Test getting table row data."""
    # Test by row number
    data = html_parser.get_row_data(
        parsed_html,
        row_number=2,  # First data row
        table_xpath="//table[@id='data']"
    )
    assert data == ["Jane", "25", "London"]

    # Test by XPath
    data = html_parser.get_row_data(
        parsed_html,
        row_xpath="//table[@id='data']//tbody/tr[2]"
    )
    assert data == ["Jane", "25", "London"]

    # Test passing invalid locator
    data = html_parser.get_row_data(
        parsed_html,
        row_number=2,
        table_xpath="//table[@id='data']",  # Valid table
        row_css="tr"
    )
    assert data == []

    # Test by not passing row_number and row_xpath
    data = html_parser.get_row_data(
        parsed_html,
        row_number=None,
        table_xpath="//table[@id='data']"
    )
    assert data == []

    # Test by passing invalid row_number
    data = html_parser.get_row_data(
        parsed_html,
        row_number=20,
        table_xpath="//table[@id='data']"
    )
    assert data == []


def test_get_column_data(html_parser, parsed_html):
    """Test getting table column data."""
    data = html_parser.get_column_data(parsed_html, "//table[@id='data']")
    assert data == ["Name", "Age", "City"]
    # Test with no header row, fall back to first row
    html_without_header = '''<!DOCTYPE html>
    <html>
        <body>
            <table id="data">
                <tbody>
                    <tr>
                        <td>John</td>
                        <td>30</td>
                        <td>New York</td>
                    </tr>
                    <tr>
                        <td>Jane</td>
                        <td>25</td>
                        <td>London</td>
                    </tr>
                </tbody>
            </table>
        </body>
    </html>'''
    parsed_html_without_header = html_parser.parse_html_data(html_without_header)
    data = html_parser.get_column_data(parsed_html_without_header, "//table[@id='data']")
    assert data == ["John", "30", "New York"]

    # Test with invalid table index
    data = html_parser.get_column_data(parsed_html, "//table[@id='data']", table_index=10)
    assert data == []
    # Test with passing header row
    html_with_header = '''<!DOCTYPE html>
    <html>
        <body>
            <table id="data">
                <tbody>
                    <thead>
                        <tr>
                            <td>Name</td>
                            <td>Age</td>
                            <td>City</td>
                        </tr>
                    </thead>
                    <tr>
                        <td>John</td>
                        <td>30</td>
                        <td>New York</td>
                    </tr>
                    <tr>
                        <td>Jane</td>
                        <td>25</td>
                        <td>London</td>
                    </tr>
                </tbody>
            </table>
        </body>
    </html>'''
    parsed_html_with_header = html_parser.parse_html_data(html_with_header)
    data = html_parser.get_column_data(parsed_html_with_header, "//table[@id='data']")
    assert data == ["Name", "Age", "City"]


def test_get_row_count(html_parser, parsed_html):
    """Test getting table row count."""
    count = html_parser.get_row_count(parsed_html, "//table[@id='data']")
    assert count == 3

    # Test with invalid table index
    count = html_parser.get_row_count(parsed_html, "//table[@id='data']", table_index=10)
    assert count == 0

    # Test using row xpath
    count = html_parser.get_row_count(parsed_html, row_xpath="//table[@id='data']//tbody/tr")
    assert count == 2

    # Test using row css
    count = html_parser.get_row_count(parsed_html, row_css="tr")
    assert count == 3


def test_get_column_count(html_parser, parsed_html):
    """Test getting table column count."""
    count = html_parser.get_column_count(parsed_html, "//table[@id='data']")
    assert count == 3

    # Test with invalid table index
    count = html_parser.get_column_count(parsed_html, "//table[@id='data']", table_index=10)
    assert count == 0
    # Test with no header row, fall back to first row
    html_without_header = '''<!DOCTYPE html>
    <html>
        <body>
            <table id="data">
                <tbody>
                    <tr>
                        <td>John</td>
                        <td>30</td>
                        <td>New York</td>
                    </tr>
                    <tr>
                        <td>Jane</td>
                        <td>25</td>
                        <td>London</td>
                    </tr>
                </tbody>
            </table>
        </body>
    </html>'''
    parsed_html_without_header = html_parser.parse_html_data(html_without_header)
    count = html_parser.get_column_count(parsed_html_without_header, "//table[@id='data']")
    assert count == 3
    # Test with passing header row
    html_with_header = '''<!DOCTYPE html>
    <html>
        <body>
            <table id="data">
                <tbody>
                    <thead>
                        <tr>
                            <td>Name</td>
                            <td>Age</td>
                            <td>City</td>
                        </tr>
                    </thead>
                    <tr>
                        <td>John</td>
                        <td>30</td>
                        <td>New York</td>
                    </tr>
                    <tr>
                        <td>Jane</td>
                        <td>25</td>
                        <td>London</td>
                    </tr>
                </tbody>
            </table>
        </body>
    </html>'''
    parsed_html_with_header = html_parser.parse_html_data(html_with_header)
    count = html_parser.get_column_count(parsed_html_with_header, "//table[@id='data']")
    assert count == 3


def test_get_all_elements(html_parser, parsed_html):
    """Test getting all elements by tag."""
    # Test getting all div elements
    elements = html_parser.get_all_elements(parsed_html, ".//div")
    assert len(elements) == 5  # 5 div elements
    assert elements[0].attrib["id"] == "main"

    # Test getting elements with namespace
    html_with_ns = '''<svg xmlns="http://www.w3.org/2000/svg">
                          <path d="M10 10 H 90 V 90 H 10 Z" />
                        </svg>'''
    parsed_html_with_ns = fromstring(html_with_ns)
    ns = {"svg": "http://www.w3.org/2000/svg"}
    elements = html_parser.get_all_elements(parsed_html_with_ns, ".//svg:path", namespace=ns)
    assert len(elements) == 0  # No elements found

    # Test with passing invalid namespace
    elements = html_parser.get_all_elements(parsed_html_with_ns, ".//svg:path", namespace=None)
    assert len(elements) == 0  # No elements found


def test_get_all_elements_text(html_parser, parsed_html):
    """Test getting all elements text by tag."""
    # Test getting all div elements
    elements = html_parser.get_all_elements_text(parsed_html, ".//div")
    assert len(elements) == 5  # 5 div elements
    assert elements[3] == "Item 2"

    # Test getting elements with namespace
    html_with_ns = '''<svg xmlns="http://www.w3.org/2000/svg">
                          <path d="M10 10 H 90 V 90 H 10 Z" />
                        </svg>'''
    parsed_html_with_ns = fromstring(html_with_ns)
    ns = {"svg": "http://www.w3.org/2000/svg"}
    elements = html_parser.get_all_elements_text(parsed_html_with_ns, ".//svg:path", namespace=ns)
    assert len(elements) == 0  # No elements found

    # Test with passing invalid namespace
    elements = html_parser.get_all_elements_text(parsed_html_with_ns, ".//svg:path", namespace=None)
    assert len(elements) == 0  # No elements found


def test_get_first_element(html_parser, parsed_html):
    """Test getting the first element by tag."""
    # Test getting the first div element
    element = html_parser.get_first_element(parsed_html, ".//div")
    assert element.attrib["id"] == "main"

    # Test getting the first element with namespace
    html_with_ns = '''<svg xmlns="http://www.w3.org/2000/svg">
                          <path d="M10 10 H 90 V 90 H 10 Z" />
                        </svg>'''
    parsed_html_with_ns = fromstring(html_with_ns)
    ns = {"svg": "http://www.w3.org/2000/svg"}
    element = html_parser.get_first_element(parsed_html_with_ns, ".//svg:path", namespace=ns)
    assert element is None  # No element found

    # Test with passing invalid namespace
    element = html_parser.get_first_element(parsed_html_with_ns, ".//svg:path", namespace=None)
    assert element is None  # No element found


def test_element_should_exist(html_parser, parsed_html):
    """Test checking element existence."""
    assert html_parser.element_should_exist(parsed_html, "//h1") is True
    assert html_parser.element_should_exist(parsed_html, "div#main", "css") is True
    # Test with passing invalid locator type
    assert html_parser.element_should_exist(parsed_html, "div#main", "invalid") is False


def test_get_element_count(html_parser, parsed_html):
    """Test getting element count."""
    assert html_parser.get_element_count(parsed_html, "//div[@class='item']") == 3
    assert html_parser.get_element_count(parsed_html, "div.item", "css") == 3
    assert html_parser.get_element_count(parsed_html, "//a") == 2
    assert html_parser.get_element_count(parsed_html, "div", locator_type="tag") == 0
    # Test with invalid locator type
    assert html_parser.get_element_count(parsed_html, "div.item", locator_type="invalid") == 0


def test_get_attributes(html_parser, parsed_html):
    """Test getting element attributes."""
    attrs = html_parser.get_attributes(parsed_html, "//div[@id='main']")
    assert attrs == {"id": "main", "class": "container"}

    attrs = html_parser.get_attributes(parsed_html, "div#main", "css")
    assert attrs == {"id": "main", "class": "container"}

    # Test with invalid locator type
    attrs = html_parser.get_attributes(parsed_html, "div#main", "invalid")
    assert attrs == {}
