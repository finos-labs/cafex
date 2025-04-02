"""Verify mongo db connection functionality """
import pytest
from pytest_bdd import scenario, when, given, then
from cafex_db.mongo_utils import MongoDBUtils

username = ""
password = ""
cluster_url = ""
database_name = ""
projection = {}
collection_name = ""


@pytest.fixture
def mongodb():
    mongo_object = MongoDBUtils(username, password, cluster_url, database_name)
    yield mongo_object
    return mongo_object


@pytest.mark.parametrize("run", range(1))  # Run the scenario 5 times
@scenario(r'mongodb.feature', 'Check mongodb connection')
def test_check_mongodb_connection(run):
    """Check mongodb connection."""
    print("Check mongodb connection")


@given('I have a mongodb connection')
def mongodb_connect():
    print("I have a mongodb connection")


@when('I check the connection')
def check_the_credentials(mongodb):
    print("I check the connection")
    if mongodb.client is not None:
        print("Connection established successfully")
        assert True


@then('I will execute the query')
def execute_the_query(mongodb):
    print("I will execute the query")
    document = mongodb.mongo_execute(database_name, collection_name)
    print(document)
    assert document is not None


@then("I will execute query with parameters")
def execute_query_with_parameters(mongodb):
    print("I will execute query with parameters")
    documents = mongodb.mongo_execute_parameters(database_name, collection_name, projection)
    print(documents)
    assert documents is not None


@then("I will get collection count")
def get_count(mongodb):
    count = mongodb.get_collection_count(database_name, collection_name)
    print(count)
    assert count is not None


@then("I will get specific document from the collection")
def get_specific_document(mongodb):
    document = mongodb.get_specific_document_from_collection(database_name, collection_name, {'_id': '43917'})
    print(document)
    assert document is not None


@then("I will close the connection")
def close_connection(mongodb):
    print("I will close the connection")
    mongodb.close_connection()
    assert True
