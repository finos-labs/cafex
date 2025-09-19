from .database_handler import DatabaseConnection
from .db_exceptions import DBExceptions
from .database_operations import DatabaseOperations
from .mongo_utils import MongoDBUtils
from .databricks_utils import DatabricksUtils
from .snowflake_utils import SnowflakeUtil

__version__ = "0.0.38"


class DBUtils(MongoDBUtils,
              DatabricksUtils,
              SnowflakeUtil):
    """
    This class inherits from MongoDBUtils, DatabricksUtils, SnowflakeUtil
    It provides a unified interface for database operations across different database systems.
    """
    pass


class CafeXDB(DatabaseConnection, DatabaseOperations, DBExceptions, DBUtils):
    """
    This class inherits from DatabaseConnection, DatabaseOperations, DBExceptions
    It provides a unified interface for database operations across different database systems.
    """
    pass
