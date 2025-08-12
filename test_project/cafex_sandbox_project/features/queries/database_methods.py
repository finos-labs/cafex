from cafex_db.db_exceptions import DBExceptions
from cafex_db.database_handler import DatabaseConnection
from cafex_core.utils.config_utils import ConfigUtils
from cafex_core.parsers.json_parser import ParseJsonData
import os

class EmployeeDbQueries:
    database_handler = DatabaseConnection()
    db_config_object = ConfigUtils('mi_api_db_config.yml')
    json_parser = ParseJsonData()

    def __init__(self):
        self.resultset_list = []
        self.resultset = None
        self.__obj_db_exception = DBExceptions()

    def mi_establish_connection(self, pstr_server):
        try:
            config = self.db_config_object.get_db_configuration(pstr_server, True)
            connection_params = {
                "database_name": config["db_name"],
                "username": config["username"],
                "password": config["password"],
                "port_number": config["port"]
            }
            self.connection_object = self.database_handler.create_db_connection(
                config["db_type"], config["db_server"], **{k: v for k, v in connection_params.items() if v}
            )
            return self.connection_object is not None
        except Exception as e:
            print(f'Exception occurred in mi_establish_connection method: {e}')

    def query_execute_with_file(self, str_filepath):
        try:
            full_path = os.path.join(self.db_config_object.fetch_testdata_path(), str_filepath)
            if not full_path:
                self.__obj_db_exception.raise_null_filepath()

            with open(full_path.strip(), 'r') as f:
                query = ' '.join(f.readlines())

            self.resultset = self.database_handler.execute_statement(self.connection_object, query, 'resultset')
            self.resultset_list = self.resultset.fetchall()
            print(self.resultset_list)
            self.database_handler.close(self.connection_object)
        except Exception as e:
            print(f'Exception occurred in query_execute_with_file method: {e}')

    def compare_resultsets(self, resultset):
        try:
            return self.resultset is not None
        except Exception as e:
            print(f'Exception occurred in compare_resultsets method: {e}')