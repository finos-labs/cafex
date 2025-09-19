from cafex_core.utils.config_utils import ConfigUtils
from cafex_db.database_handler import DatabaseConnection


class CassandraConnection:

    database_handler = DatabaseConnection()
    db_config_object = ConfigUtils('mi_api_db_config.yml')

    def cassandra_establish_connection(self, pstr_server):
        try:
            config = self.db_config_object.get_db_configuration(pstr_server, True)
            connection_params = {
                "database_name": config["keyspace"],
                "username": config["username"],
                "password": config["password"],
                "port_number": config["port"]
            }
            self.connection_object = self.database_handler.create_db_connection(
                config["db_type"], config["db_server"], **{k: v for k, v in connection_params.items() if v}
            )
            return self.connection_object is not None
        except Exception as e:
            print(f'Exception occurred in cassandra establish connection method: {e}')
