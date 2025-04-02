from cafex_core.logging.logger_ import CoreLogger
from cafex_db.database_operations import DatabaseOperations
from cafex_db.db_exceptions import DBExceptions
# from cassandra.cluster import Cluster
from cafex_db.db_security import DBSecurity

class DatabaseConnection(DatabaseOperations):
    """Establishes database connections for various database types."""

    SUPPORTED_DATABASE_TYPES = [
        "mssql",
        "mysql",
        "oracle",
        "hive",
        "PostgreSQL",
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

    def create_db_connection(self, database_type, server_name, **kwargs):
        """Creates a database connection based on the provided parameters.

        Parameters:
            database_type (str): The type of database. Supported types:
                'mssql', 'mysql', 'oracle', 'hive', 'PostgreSQL',
                'cassandra', 'spark', 'ec2_hive','SQLite'.
            server_name (str): The name or IP address of the database server.
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
            control_timeout (int/float): Query timeout (Cassandra, MSSQL).

        Returns:
            object: The database connection object.
            None: If an error occurs or the database type is not supported.

        Raises:
            ValueError: For invalid database types or missing required parameters.
            DatabaseConnectionError: For connection errors.

        Examples:
            >>> db_conn = DatabaseConnection()
            >>> conn = db_conn.create_db_connection(
            ...     'mssql', 'dbserver', database_name='my_db',
            ...     username='user', password='password'
            ... )
            >>> db_conn.create_db_connection(
            ...     'oracle', 'dbhost', username='user', password='password',
            ...     port_number=1521, service_name='my_service'
            ... )
            >>> db_conn.create_db_connection(
            ...     'hive', 'hiveserver', username='user',
            ...     pem_file='/path/to/key.pem'
            ... )
        """
        database_type = database_type.lower()

        if database_type not in self.SUPPORTED_DATABASE_TYPES:
            self.__obj_db_exception.raise_null_database_type()

        if server_name is None:
            self.__obj_db_exception.raise_null_server_name()

        if database_type in ["mssql", "mysql", "oracle", "postgres", "cassandra"]:
            if kwargs.get("username") is not None and kwargs.get("password") is None:
                self.__obj_db_exception.raise_null_password()

        if kwargs.get("is_password_encoded") and kwargs.get("secret_key") is None:
            if database_type.lower() not in ["mssql", "mysql", "oracle", "postgres"]:
                self.__obj_db_exception.raise_null_secret_key()

        if database_type in ["hive", "spark", "ec2_hive"]:
            if kwargs.get("password") is None and kwargs.get("pem_file") is None:
                self.__obj_db_exception.raise_generic_exception(
                    "For hive/Spark/ec2_hive, Password and ppem file cannot be null"
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
            elif database_type == "PostgreSQL":
                connection = self._create_postgresql_connection(server_name, **kwargs)
            elif database_type == "cassandra":
                connection = self._create_cassandra_connection(server_name, **kwargs)
            else:
                raise ValueError(f"Database type not yet implemented: {database_type}")

            return connection

        except Exception as e:
            self.logger.error(f"Error creating {database_type} connection: {e}")

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
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

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
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def _create_oracle_connection(self, server_name, **kwargs):
        """
        Description:
            |  This method deals with creating a connection to Oracle database

        :return: Database Connection Object

        . notes::
            |  For input parameters, refer to the method description of create_db_connection


        . warning::
            |  Oracle instant client is a must be available on the host where this method is called. Refer to the documentation at https://cx-oracle.readthedocs.io/en/latest/installation.html#installing-cx-oracle-on-windows to understand the setup process.
            |  More information different oracle encoding can be seen at https://www.oracle.com/database/technologies/faq-nls-lang.html.

        Examples:
            |  mi_data_ingestion.mi_establish_connection(server,pstr_encoding="utf8")

        """
        try:
            oracle_connection = self.__obj_db_decrypter.oracle(server_name, **kwargs)
            return oracle_connection
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def _create_hive_connection(self, server_name, **kwargs):
        """
        Description:
            |  This method deals with creating a connection to HIVE database using the SSH protocol
        :return: Database Connection Object

        .. notes::
            |  For input parameters, refer to the method description of create_db_connection
        """
        try:
            HiveClient = self.__obj_db_decrypter.hive_connection(server_name, **kwargs)
            return HiveClient
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

        pass

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
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

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
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))
