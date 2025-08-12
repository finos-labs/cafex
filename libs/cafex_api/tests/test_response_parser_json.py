import pytest
from cafex_api.response_parser_json import ResponseParserJSON

@pytest.fixture
def parser():
    return ResponseParserJSON()

@pytest.fixture
def sample_json():
    return {"a": 1, "b": {"c": 2, "d": {"e": 3}}}

def test_get_key_value_valid(parser, sample_json):
    assert parser.get_key_value(json=sample_json, key="a") == 1
    assert parser.get_key_value(json=sample_json, key="c", nested=True) == 2

def test_get_key_value_invalid(parser):
    with pytest.raises(ValueError):
        parser.get_key_value(json={}, key="missing")

def test_compare_json_identical(parser):
    json1 = {"a": 1, "b": 2}
    json2 = {"a": 1, "b": 2}
    assert parser.compare_json(json1, json2) is True

def test_compare_json_different(parser):
    json1 = {"a": 1, "b": 2}
    json2 = {"a": 1, "b": 3}
    assert parser.compare_json(json1, json2) == (False, ['Expected value for b is 2 but found 3'])

def test_convert_json_to_xml_valid(parser):
    json_data = {"a": 1}
    xml_result = parser.convert_json_to_xml(json_data)
    assert "<a>1</a>" in xml_result

def test_get_all_keys(parser, sample_json):
    keys = parser.get_all_keys(sample_json)
    assert sorted(keys) == ["a", "b", "c", "d", "e"]

def test_key_exists(parser, sample_json):
    assert parser.key_exists(sample_json, "a") is True
    assert parser.key_exists(sample_json, "z") is False

def test_get_occurrence_of_key(parser, sample_json):
    assert parser.get_occurrence_of_key(sample_json, "e") == 1

def test_get_key_path_value_absolute(parser, sample_json):
    assert parser.get_key_path_value(sample_json, "b.d.e") == 3