from cafex_core.utils.exceptions import CoreExceptions


class DBExceptions(CoreExceptions):
    """Database specific exceptions that inherit from CoreExceptions.

    All database related custom exceptions should be raised through this
    class.
    """

    def __init__(self):
        super().__init__()

    def raise_null_server_name(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """Raise exception when database server name is null or empty.

        This method handles cases where the database server name is missing,
        which is required for establishing database connections.

        Args:
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Example:
            # Validating database connection parameters
            def create_db_connection(self, config):
                if not config.get('server_name'):
                    self.exceptions.raise_null_server_name(fail_test=True)
        """
        message = "Server name can not be null"
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_null_database_type(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """Raise exception when database type is not specified.

        This method is used when the type of database (e.g., MySQL, Oracle)
        is not provided but required for connection setup.

        Args:
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Example:
            # Initializing database connection factory
            def initialize_db_connection(self, db_config):
                if not db_config.get('db_type'):
                    self.exceptions.raise_null_database_type(fail_test=True)
        """
        message = "Database type can not be null"
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_null_password(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """Raise exception when database password is missing.

        This method handles cases where the database password is required
        but not provided in the connection parameters.

        Args:
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Example:
            # Validating database credentials
            def verify_db_credentials(self, credentials):
                if not credentials.get('password'):
                    self.exceptions.raise_null_password(fail_test=True)
        """
        message = "Password can not be null"
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_null_secret_key(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """Raise exception when database secret key is missing.

        This method is used when a secret key required for encrypted database
        connections or secure operations is not provided.

        Args:
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Example:
            # Setting up encrypted database connection
            def setup_secure_connection(self, config):
                if not config.get('secret_key'):
                    self.exceptions.raise_null_secret_key(fail_test=True)
        """
        message = "Secret key can not be null"
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_invalid_database_type(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """Raise exception when specified database type is not supported.

        This method handles cases where the provided database type is not
        among the supported database systems in the framework.

        Args:
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Example:
            # Validating database type before connection
            def validate_db_type(self, db_type):
                valid_types = ['mysql', 'postgresql', 'oracle']
                if db_type not in valid_types:
                    self.exceptions.raise_invalid_database_type(fail_test=True)
        """
        message = "The database type is invalid"
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_null_database_object(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """Raise exception when database connection object is null.

        This method is used when a database operation is attempted but the
        database connection object is not properly initialized.

        Args:
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Example:
            # Checking database connection before query
            def execute_select(self, query):
                if not self.db_connection:
                    self.exceptions.raise_null_database_object(fail_test=True)
        """
        message = "The database object is null"
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_null_hive_object(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """Raise exception when Hive connection object is null.

        This method handles cases where a Hive operation is attempted but the
        Hive client connection is not properly initialized.

        Args:
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Example:
            # Validating Hive connection
            def execute_hive_query(self, query):
                if not self.hive_client:
                    self.exceptions.raise_null_hive_object(fail_test=True)
        """
        message = "The hive client object is null"
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_null_database_name(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """Raise exception when database name is missing.

        This method is used when a database operation requires a specific
        database name but none is provided.

        Args:
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Example:
            # Setting up database connection
            def connect_to_database(self, params):
                if not params.get('database_name'):
                    self.exceptions.raise_null_database_name(fail_test=True)
        """
        message = "Database name cannot be null"
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_null_table_name(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """Raise exception when table name is missing for database operation.

        This method handles cases where a table operation is attempted but
        the target table name is not specified.

        Args:
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Example:
            # Performing table operation
            def get_table_data(self, table_name):
                if not table_name:
                    self.exceptions.raise_null_table_name(fail_test=True)
        """
        message = "Table name cannot be null"
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_null_query(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """Raise exception when SQL query string is null or empty.

        This method is used when attempting to execute a database query
        but no query string is provided.

        Args:
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Example:
            # Executing database query
            def execute_query(self, query):
                if not query or not query.strip():
                    self.exceptions.raise_null_query(fail_test=True)
        """
        message = "Query cannot be null"
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_null_filepath(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """Raise exception when file path for database operation is missing.

        This method handles cases where a file path is required (e.g., for
        importing/exporting data) but not provided.

        Args:
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Example:
            # Importing data from file
            def import_data_from_file(self, file_path):
                if not file_path:
                    self.exceptions.raise_null_filepath(fail_test=True)
        """
        message = "filepath cannot be null"
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_null_result_list(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """Raise exception when query result list is null.

        This method is used when a database query is expected to return
        a list of results but returns null instead.

        Args:
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Example:
            # Processing query results
            def process_query_results(self, results):
                if results is None:
                    self.exceptions.raise_null_result_list(fail_test=True)
        """
        message = "Result list cannot be null"
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_null_result_set(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """Raise exception when query result set is null.

        This method handles cases where a database query is expected to return
        a result set object but returns null instead.

        Args:
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Example:
            # Handling query result set
            def get_result_set(self, query):
                result_set = self.db.execute(query)
                if result_set is None:
                    self.exceptions.raise_null_result_set(fail_test=True)
        """
        message = "Result set cannot be null"
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_null_column_header(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """Raise exception when column headers are missing.

        This method is used when database operation requires column headers
        (e.g., for result processing or data mapping) but they are missing.

        Args:
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Example:
            # Processing result columns
            def validate_columns(self, headers):
                if not headers:
                    self.exceptions.raise_null_column_header(fail_test=True)
        """
        message = "columns/header names cannot be null"
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_null_dataframe(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """Raise exception when pandas DataFrame is null.

        This method handles cases where a pandas DataFrame is required for
        data processing but is null or empty.

        Args:
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Example:
            # Processing DataFrame
            def analyze_data(self, df):
                if df is None or df.empty:
                    self.exceptions.raise_null_dataframe(fail_test=True)
        """
        message = "dataframe cannot be null"
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_null_service_name(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """Raise exception when database service name is missing.

        This method is used when a database service name is required (e.g.,
        for Oracle TNS connections) but not provided.

        Args:
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Example:
            # Setting up Oracle connection
            def connect_to_oracle(self, config):
                if not config.get('service_name'):
                    self.exceptions.raise_null_service_name(fail_test=True)
        """
        message = "Service name cannot be null"
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )
