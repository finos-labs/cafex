import os

from cafex_core.utils.config_utils import ConfigUtils
from cafex_db import CafeXDB
from cafex_db.db_exceptions import DBExceptions
from cafex_core.logging.logger_ import CoreLogger


# --- Connection Management ---
class CompareDB:

    def __init__(self):
        self.resultset_list = []
        self.resultset = None
        self.__obj_db_exception = DBExceptions()
        self.logger = CoreLogger(name=__name__).get_logger()

    def database_establish_connection(self, pstr_server, config_file):
        try:
            if config_file:
                self.db_config_object = ConfigUtils(config_file)
            config = self.db_config_object.get_db_configuration(pstr_server, True)
            connection_params = {
                "database_name": config["db_name"],
                "username": config["username"],
                "password": config["password"],
                "port_number": config["port"]
            }
            self.connection_object = CafeXDB().create_db_connection(
                config["db_type"], config["db_server"], **{k: v for k, v in connection_params.items() if v}
            )
            return self.connection_object is not None
        except Exception as e:
            print(f'Exception occurred in database establish connection method: {e}')

    def query_execute_with_file(self, str_filepath):
        try:
            full_path = os.path.join(self.db_config_object.fetch_testdata_path(), str_filepath)
            if not full_path:
                self.__obj_db_exception.raise_null_filepath()

            with open(full_path.strip(), 'r') as f:
                query = ' '.join(f.readlines())

            self.resultset = CafeXDB().execute_statement(self.connection_object, query, 'resultset')
            self.resultset_list = self.resultset.fetchall()
            print(self.resultset_list)
            return self.resultset_list
        except Exception as e:
            print(f'Exception occurred in query_execute_with_file method: {e}')

    def close_establish_connection(self):
        CafeXDB().close(self.connection_object)
