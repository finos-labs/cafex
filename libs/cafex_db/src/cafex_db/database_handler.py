"""This module provides the DatabaseConnection class for establishing connections to various
database types.
"""

import sqlite3

from cafex_core.logging.logger_ import CoreLogger

from .database_operations import DatabaseOperations
from .db_exceptions import DBExceptions
from .db_security import DBSecurity


class DatabaseConnection(DatabaseOperations):
    """Establishes database connections for various database types."""

    SUPPORTED_DATABASE_TYPES = [
        "mssql",
        "mysql",
        "oracle",
        "hive",
        "postgresql",
        "cassandra",
        "spark",
        "ec2_hive",
        "SQLite",
    ]

    def __init__(self):
        """Initializes the DatabaseConnection class."""
        super().__init__()
        self.__obj_db_decrypter = DBSecurity()
        self.logger = CoreLogger(name=__name__).get_logger()
        self.__obj_db_exception = DBExceptions()

    def create_db_connection(self, database_type, server_name=None, **kwargs):
        """
        Creates a database connection based on the provided parameters.

        Parameters:
            database_type (str): The type of database. Supported types:
                'mssql', 'mysql', 'oracle', 'hive', 'PostgreSQL',
                'cassandra', 'spark', 'ec2_hive','SQLite'.
            server_name (str, optional): The name or IP address of the database server.
                For Oracle wallet connections (with tns_admin specified), this can be None.
            **kwargs: Additional keyword arguments specific to each database type.

        Keyword Arguments:
            database_name (str): The name of the database.
            username (str): The username for authentication.
            password (str): The password for authentication.
            port_number (int): The port number of the database server.
            is_password_encoded (bool): Whether the password is URL encoded.
                                        Defaults to False.
            pem_file (str): Path to the SSH key file (Hive).
            secret_key (str): Secret key for encoded passwords.
            sid (str): The Oracle SID.
            service_name (str): The Oracle service name.
            encoding (str): Encoding format (Oracle).
            thick_mode (bool): Whether to use Oracle thick mode (Oracle).
            tns_admin (str): Path to the wallet directory (Connections using Oracle wallet).
            use_wallet (bool): Force using wallet-based connection. default: auto-detect (Oracle).
            control_timeout (int/float): Query timeout (Cassandra, MSSQL).
        Note: Cassandra driver will only with python 3.12.0 and lower version
        Returns:
            object: The database connection object.
            None: If an error occurs or the database type is not supported.

        Raises:
            ValueError: For invalid database types or missing required parameters.
            DatabaseConnectionError: For connection errors.

        Examples:
            >>> db_conn = DatabaseConnection()
            >>> # Standard MSSQL connection
            >>> conn = db_conn.create_db_connection(
            ...     'mssql', 'dbserver', database_name='my_db',
            ...     username='user', password='password'
            ... )
            >>> # Standard Oracle connection
            >>> db_conn.create_db_connection(
            ...     'oracle', 'dbhost', username='user', password='password',
            ...     port_number=1521, service_name='my_service'
            ... )
            >>> # Hive connection
            >>> db_conn.create_db_connection(
            ...     'hive', 'hiveserver', username='user',
            ...     pem_file='/path/to/key.pem'
            ... )
            >>> # Standard Oracle thin mode connection
            >>> db_conn.create_db_connection(
            ...     'oracle', 'dbhost', username='user', password='pass',
            ...     service_name='service'
            ... )
            >>> # Oracle thick mode connection
            >>> db_conn.create_db_connection(
            ...     'oracle', 'dbhost', username='user', password='pass',
            ...     service_name='service', thick_mode=True
            ... )
            >>> # Oracle wallet connection (server_name can be None)
            >>> db_conn.create_db_connection(
            ...     'oracle', None, username='user', password='pass',
            ...     service_name='high_service', tns_admin='/path/to/wallet',
            ...     thick_mode=True
            ... )
        """
        database_type = database_type.lower()

        if database_type not in self.SUPPORTED_DATABASE_TYPES:
            self.__obj_db_exception.raise_null_database_type()

        # Only raise null_server_name exception if:
        # - It's not an Oracle connection, OR
        # - It is an Oracle connection but tns_admin is not provided (not a wallet connection)
        if server_name is None:
            if database_type != "oracle" or (
                database_type == "oracle" and not kwargs.get("tns_admin")
            ):
                self.__obj_db_exception.raise_null_server_name()

        if database_type in ["mssql", "mysql", "oracle", "postgresql", "cassandra"]:
            if kwargs.get("username") is not None and kwargs.get("password") is None:
                self.__obj_db_exception.raise_null_password()

        is_password_encoded = kwargs.get("is_password_encoded")
        secret_key = kwargs.get("secret_key")

        if is_password_encoded and secret_key is None:
            if database_type.lower() not in ["mssql", "mysql", "oracle", "postgres"]:
                self.__obj_db_exception.raise_null_secret_key()

        if database_type in ["hive", "spark", "ec2_hive"]:
            password = kwargs.get("password")
            pem_file = kwargs.get("pem_file")
            if password is None and pem_file is None:
                self.__obj_db_exception.raise_generic_exception(
                    "For hive/Spark/ec2_hive, Password and pem file cannot be null"
                )

        try:
            if database_type == "mssql":
                connection = self._create_mssql_connection(server_name, **kwargs)
            elif database_type == "mysql":
                connection = self._create_mysql_connection(server_name, **kwargs)
            elif database_type == "oracle":
                connection = self._create_oracle_connection(server_name, **kwargs)
            elif database_type == "hive":
                connection = self._create_hive_connection(server_name, **kwargs)
            elif database_type == "postgresql":
                connection = self._create_postgresql_connection(server_name, **kwargs)
            elif database_type == "cassandra":
                connection = self._create_cassandra_connection(server_name, **kwargs)
            elif database_type == "sqlite":
                connection = self._create_sqlite_connection(**kwargs)
            else:
                raise ValueError(f"Database type not yet implemented: {database_type}")

            return connection

        except ValueError as ve:
            self.logger.error("ValueError creating %s connection: %s", database_type, ve)
            return None
        except (ConnectionError, TimeoutError) as e:
            self.logger.error("Connection error creating %s connection: %s", database_type, e)
            return None
        except Exception as e:  # pylint: disable=broad-except
            self.logger.error("Error creating %s connection: %s", database_type, e)
            return None

    def _create_mssql_connection(self, server_name, **kwargs):
        """Creates and returns an MSSQL connection object.
        Description:
            |  This method deals with creating a connection to mssql database.

        :return: Database Connection Object

        .. notes::
                |  For input parameters, refer to the method description of create_db_connection
                |  Autocommit is set to True
        """
        try:
            mssql_connection = self.__obj_db_decrypter.mssql(server_name, **kwargs)
            return mssql_connection
        except Exception as e:  # pylint: disable=broad-except
            self.__obj_db_exception.raise_generic_exception(str(e))
            return None

    def _create_mysql_connection(self, server_name, **kwargs):
        """Creates and returns a MySQL connection object.
        Description:
            |  This method deals with creating a connection to mysql database

        :return: Database Connection Object

        .. notes::
         |  For input parameters, refer to the method description of create_db_connection

        """
        try:
            mysql_connection = self.__obj_db_decrypter.mysql(server_name, **kwargs)
            return mysql_connection
        except Exception as e:  # pylint: disable=broad-except
            self.__obj_db_exception.raise_generic_exception(str(e))
            return None

    def _create_oracle_connection(self, server_name=None, **kwargs):
        """
        Description:
            |  This method deals with creating a connection to Oracle database

        :param server_name: The hostname or IP address of the Oracle server.
                            For wallet connections with tns_admin specified, this can be None.
        :type server_name: str, optional
        :return: Database Connection Object

        .. notes::
            |  For input parameters, refer to the method description of create_db_connection
            |  For wallet-based connections (with tns_admin specified), server_name is optional
            |  Both thick mode and thin mode connections are supported:
            |    - Thick mode requires Oracle Instant Client installation
            |    - Thin mode is pure Python and doesn't require client libraries
            |    - Wallet connections typically use thick mode (set thick_mode=True)

        .. warning::
            |  For thick mode or wallet connections, Oracle Instant Client must be available on the host.
            |  Refer: https://python-oracledb.readthedocs.io/en/latest/user_guide/initialization.html
            |  For information about different Oracle encodings, see:
            |  https://www.oracle.com/database/technologies/faq-nls-lang.html
        """
        try:
            oracle_connection = self.__obj_db_decrypter.oracle(server_name, **kwargs)
            return oracle_connection
        except Exception as e:  # pylint: disable=broad-except
            self.__obj_db_exception.raise_generic_exception(str(e))
            return None

    def _create_hive_connection(self, server_name, **kwargs):
        """
        Description:
            |  This method deals with creating a connection to HIVE database using the SSH protocol
        :return: Database Connection Object

        .. notes::
            |  For input parameters, refer to the method description of create_db_connection
        """
        try:
            hive_client = self.__obj_db_decrypter.hive_connection(server_name, **kwargs)
            return hive_client
        except Exception as e:  # pylint: disable=broad-except
            self.__obj_db_exception.raise_generic_exception(str(e))
            return None

    def _create_postgresql_connection(self, server_name, **kwargs):
        """
        Description:
            |  This method deals with creating a connection to postgres database

        :param pint_port_number: port
        :type pint_port_number: kwargs
        :return: Database Connection Object

        .. notes::
                |  For input parameters, refer to the method description of create_db_connection
        """
        try:
            postgres_connection = self.__obj_db_decrypter.postgres(server_name, **kwargs)
            return postgres_connection
        except Exception as e:  # pylint: disable=broad-except
            self.__obj_db_exception.raise_generic_exception(str(e))
            return None

    def _create_cassandra_connection(self, server_name, **kwargs):
        """
        Description:
            |  This method deals with creating a connection to cassandra database

        :return: Database Connection Object

        . notes::
            |  For input parameters, refer to the method description of create_db_connection
        """
        try:
            cassandra_connection = self.__obj_db_decrypter.cassandra_connection(
                server_name, **kwargs
            )
            return cassandra_connection
        except Exception as e:  # pylint: disable=broad-except
            self.__obj_db_exception.raise_generic_exception(str(e))
            return None

    def _create_sqlite_connection(self, **kwargs):
        """Creates and returns an SQLite connection object."""
        try:
            db_file = kwargs.get("database_name")  # Get the database file path
            if not db_file:
                self.__obj_db_exception.raise_generic_exception(
                    "Database file path (database_name) is required for SQLite."
                )
                return None
            sqlite_connection = sqlite3.connect(db_file)
            return sqlite_connection
        except sqlite3.Error as e:
            self.__obj_db_exception.raise_generic_exception(str(e))
            return None
        except Exception as e:  # pylint: disable=broad-except
            self.__obj_db_exception.raise_generic_exception(str(e))
            return None
