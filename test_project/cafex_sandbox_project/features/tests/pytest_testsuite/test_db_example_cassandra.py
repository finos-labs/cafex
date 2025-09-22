from test_project.cafex_sandbox_project.features.queries.cassandra_connection import cassandra_connection
import pytest


class CassandraTestConnection:
    def __init__(self):
        self.connection = cassandra_connection.CassandraConnection()

@pytest.mark.db
def test_connect_cassandra_server(self):
    try:
        print("write execute query statement")
    except Exception as e:
        print(e)
    finally:
        self.connection.shutdown()

