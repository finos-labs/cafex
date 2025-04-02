"""Tests for the HTML Parser module."""

import pytest
from lxml.html import HtmlElement, fromstring


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

    # Test malformed HTML
    malformed_html = "<not>valid</html>"
    result = html_parser.parse_html_data(malformed_html)
    assert result is not None  # lxml tries to fix malformed HTML


def test_get_element_by_xpath(html_parser, parsed_html):
    """Test getting elements by XPath."""
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


def test_get_element_by_css(html_parser, parsed_html):
    """Test getting elements by CSS selector."""
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


def test_get_hyperlink_value(html_parser, parsed_html):
    """Test getting hyperlink text values."""
    # Test single link
    text = html_parser.get_hyperlink_value(parsed_html, "//a[@class='nav-link']")
    assert text == "Home"

    # Test multiple links
    texts = html_parser.get_hyperlink_value(parsed_html, ".nav-link", locator_type="css", get_all=True)
    assert texts == ["Home", "About"]


def test_get_text(html_parser, parsed_html):
    """Test getting element text."""
    # Test XPath
    text = html_parser.get_text(parsed_html, "//h1")
    assert text == "Welcome"

    # Test CSS
    text = html_parser.get_text(parsed_html, "p.intro", locator_type="css")
    assert text == "This is a test page"


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


def test_get_column_data(html_parser, parsed_html):
    """Test getting table column data."""
    data = html_parser.get_column_data(parsed_html, "//table[@id='data']")
    assert data == ["Name", "Age", "City"]


def test_element_should_exist(html_parser, parsed_html):
    """Test checking element existence."""
    assert html_parser.element_should_exist(parsed_html, "//h1") is True
    assert html_parser.element_should_exist(parsed_html, "div#main", "css") is True
    assert html_parser.element_should_exist(parsed_html, "//nonexistent") is False


def test_get_element_count(html_parser, parsed_html):
    """Test getting element count."""
    assert html_parser.get_element_count(parsed_html, "//div[@class='item']") == 3
    assert html_parser.get_element_count(parsed_html, "div.item", "css") == 3
    assert html_parser.get_element_count(parsed_html, "//a") == 2


def test_get_attributes(html_parser, parsed_html):
    """Test getting element attributes."""
    attrs = html_parser.get_attributes(parsed_html, "//div[@id='main']")
    assert attrs == {"id": "main", "class": "container"}

    attrs = html_parser.get_attributes(parsed_html, "div#main", "css")
    assert attrs == {"id": "main", "class": "container"}