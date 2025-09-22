import base64
import os
import sys
import urllib.parse

import oracledb
import paramiko
import sqlalchemy as sc
from cafex_core.utils.core_security import (
    Security,
    decrypt_password,
    use_secured_password,
)
from cafex_core.utils.exceptions import CoreExceptions
# from cassandra.auth import PlainTextAuthProvider
# from cassandra.cluster import Cluster
# from cassandra.io.asyncioreactor import AsyncioConnection
from Crypto.Cipher import AES
from pymongo import MongoClient

from .db_exceptions import DBExceptions

oracledb.version = "8.3.0"
sys.modules["cx_Oracle"] = oracledb


class DBSecurity(Security):
    """Class for database security-related functionality."""

    def __init__(self):
        super().__init__()
        self.crypt_bool_key = use_secured_password()
        self.__obj_db_exception = DBExceptions()
        self.__obj_generic_exception = CoreExceptions()

    @staticmethod
    def encode_password(password: str) -> str | None:
        """Encodes a password for URL parsing."""

        if password is not None:
            return urllib.parse.quote_plus(password)
        return None

    def decode_password(self, pkey: str, psecret_key: str) -> str:
        """Decodes a password using AES."""

        try:
            cipher = AES.new(psecret_key.encode("utf8"), AES.MODE_ECB)
            decoded = cipher.decrypt(base64.b64decode(pkey.encode("latin-1")))
            return decoded.decode("latin-1").strip()
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(str(e))

    def mssql(self, server_name: str, **kwargs) -> sc.engine.Connection:
        """Creates an MSSQL connection."""

        try:
            username = kwargs.get("username")
            password = kwargs.get("password")
            port_number = kwargs.get("port_number")
            query_timeout = kwargs.get("query_timeout", 0)
            database_name = kwargs.get("database_name")
            if self.crypt_bool_key and password:
                password = decrypt_password(password)

            password = (
                self.encode_password(password)
                if kwargs.get("is_password_encoded", False)
                else password
            )

            if username and password and port_number:
                engine = sc.create_engine(
                    f"mssql+pymssql://{username}:{password}@{server_name}:{port_number}/{database_name}",
                    connect_args={"timeout": query_timeout},
                )
            elif username and password:
                engine = sc.create_engine(
                    f"mssql+pymssql://{username}:{password}@{server_name}/{database_name}",
                    connect_args={"timeout": query_timeout},
                )
            elif port_number:
                engine = sc.create_engine(
                    f"mssql+pymssql://{server_name}:{port_number}/{database_name}",
                    connect_args={"timeout": query_timeout},
                )
            else:
                engine = sc.create_engine(
                    f"mssql+pymssql://{server_name}/{database_name}",
                    connect_args={"timeout": query_timeout},
                )

            connection = engine.connect().execution_options(isolation_level="AUTOCOMMIT")
            return connection
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(str(e))

    def mysql(self, server_name: str, database_name: str, **kwargs) -> sc.engine.Connection:
        """Creates a MySQL connection."""

        try:
            username = kwargs.get("username")
            password = kwargs.get("password")
            port_number = kwargs.get("port_number")

            if self.crypt_bool_key and password:
                password = decrypt_password(password)

            password = (
                self.encode_password(password)
                if kwargs.get("is_password_encoded", False)
                else password
            )

            if username and password and port_number:
                engine = sc.create_engine(
                    f"mysql+pymysql://{username}:{password}@{server_name}:{port_number}/{database_name}"
                )
            elif username and password:
                engine = sc.create_engine(
                    f"mysql+pymysql://{username}:{password}@{server_name}/{database_name}"
                )
            elif port_number:
                engine = sc.create_engine(
                    f"mysql+pymysql://{server_name}:{port_number}/{database_name}"
                )
            else:
                engine = sc.create_engine(f"mysql+pymysql://{server_name}/{database_name}")

            return engine.connect()
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(str(e))

    def postgres(self, server_name: str, database_name: str, **kwargs) -> sc.engine.Connection:
        """Creates a PostgreSQL connection."""

        try:
            username = kwargs.get("username")
            password = kwargs.get("password")
            port_number = kwargs.get("port_number")

            if self.crypt_bool_key and password:
                password = decrypt_password(password)

            password = (
                self.encode_password(password)
                if kwargs.get("is_password_encoded", False)
                else password
            )

            if username and password and port_number:
                engine = sc.create_engine(
                    f"postgresql://{username}:{password}@{server_name}:{port_number}/{database_name}"
                )
            elif username and password:
                engine = sc.create_engine(
                    f"postgresql://{username}:{password}@{server_name}/{database_name}"
                )
            elif port_number:
                engine = sc.create_engine(
                    f"postgresql://{server_name}:{port_number}/{database_name}"
                )
            else:
                engine = sc.create_engine(f"postgresql://{server_name}/{database_name}")

            return engine.connect()
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(str(e))

    def hive_connection(self, server_name: str, **kwargs) -> paramiko.SSHClient:
        """
        Creates an SSH connection to a Hive server.

        Args:
            server_name: The hostname or IP address of the Hive server.
            **kwargs: Keyword arguments for connection parameters.

        Keyword Args:
            username (str):  The SSH username. (Required)
            password (str): The SSH password.
            pem_file (str): Path to the PEM key file.
            port_number (int): The SSH port (default: 22).
            is_password_encoded (bool): Whether the password is encoded.
                                        If True, `secret_key` is required.
            secret_key (str): The secret key to decode the password.

        Returns:
            paramiko.SSHClient: The SSH client object.

        Raises:
            ValueError: If authentication parameters are incorrect.
            HiveConnectionError: For other connection errors.
        """
        username = kwargs.get("username")
        password = kwargs.get("password")
        pem_file = kwargs.get("pem_file")
        port_number = kwargs.get("port_number", 22)

        if not username:
            raise ValueError("Username is required.")

        if password and pem_file:
            raise ValueError("Specify either password or pem_file, not both.")

        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if password:
                if kwargs.get("is_password_encoded"):
                    secret_key = kwargs.get("secret_key")
                    if not secret_key:
                        raise ValueError("Secret key required to decode password.")
                    password = self.decode_password(
                        password, secret_key
                    )  # Assuming you have a decode method

                ssh_client.connect(
                    hostname=server_name, username=username, password=password, port=port_number
                )
            elif pem_file:
                ssh_client.connect(
                    hostname=server_name, username=username, key_filename=pem_file, port=port_number
                )
            else:
                raise ValueError("Either password or pem_file is required.")

            return ssh_client

        except paramiko.SSHException as e:
            raise self.__obj_generic_exception.raise_generic_exception(
                str(e) + f"SSH connection error: {e}"
            ) from e
        except Exception as e:
            raise self.__obj_generic_exception.raise_generic_exception(
                str(e) + f"Error creating Hive connection: {e}"
            ) from e

    def oracle(self, server_name: str = None, **kwargs) -> sc.engine.Connection:
        """
        Creates an Oracle connection using oracledb.

        This method supports multiple connection methods:
        1. Wallet-based connection (most secure, recommended for Oracle Autonomous Database)
        2. Direct connection with service name (thin mode, no wallet needed)
        3. Direct connection with SID

        Args:
            server_name: The hostname or IP address of the Oracle server.
                         For wallet connections, can be empty or None.
            **kwargs: Additional connection parameters.

        Keyword Args:
            username (str): The database username.
            password (str): The database password.
            port_number (int): The database port (default: 1521 for regular, 1522 for Oracle Cloud).
            sid (str): The Oracle SID.
            service_name (str): The Oracle service name or TNS alias from tnsnames.ora.
            encoding (str): The character encoding.
            thick_mode (bool): Whether to use thick mode (requires Oracle Client).
            tns_admin (str): Path to the wallet directory (for connections using wallet).
            use_wallet (bool): Force using wallet-based connection (default: auto-detect).

        Returns:
            sqlalchemy.engine.Connection: A connection to the Oracle database.

        Raises:
            ValueError: If required parameters are missing.
        """
        try:
            username = kwargs.get("username")
            password = kwargs.get("password")
            port_number = kwargs.get("port_number")
            sid = kwargs.get("sid")
            service_name = kwargs.get("service_name")
            encoding = kwargs.get("encoding")
            thick_mode = kwargs.get("thick_mode", False)
            tns_admin = kwargs.get("tns_admin")
            use_wallet = kwargs.get("use_wallet")

            # Auto-detect if we should use wallet-based connection
            if use_wallet is None:
                use_wallet = tns_admin is not None

            if tns_admin:
                tns_admin = os.path.normpath(tns_admin)

            if self.crypt_bool_key and password:
                password = decrypt_password(password)

            password = (
                self.encode_password(password)
                if kwargs.get("is_password_encoded", False)
                else password
            )

            if encoding:
                os.environ["NLS_LANG"] = f".{encoding.upper()}"

            # Initialize Oracle Client if needed (thick mode or wallet)
            if thick_mode or use_wallet:
                try:
                    if tns_admin:
                        oracledb.init_oracle_client(config_dir=tns_admin)
                    else:
                        oracledb.init_oracle_client()
                except Exception as init_err:
                    self.logger.warning(f"Oracle Client initialization note: {init_err}")

            # Choose connection approach based on parameters and use_wallet
            if use_wallet:
                if not service_name:
                    raise ValueError("service_name is required for wallet-based connection")

                # For wallet, service_name is just the TNS alias
                # No need for server_name, port, etc. as they're in the wallet
                connect_string = f"oracle://{username}:{password}@"

                engine = sc.create_engine(connect_string, connect_args={"dsn": service_name})

            elif sid:
                # SID-BASED CONNECTION
                if thick_mode:
                    dsn = oracledb.makedsn(server_name, port_number, sid=sid)
                    connect_string = f"oracle://{username}:{password}@{dsn}"
                else:
                    connect_string = (
                        f"oracle://{username}:{password}@{server_name}:{port_number}/?sid={sid}"
                    )

                engine = sc.create_engine(connect_string)

            elif service_name:
                # SERVICE NAME CONNECTION
                if thick_mode:
                    dsn = oracledb.makedsn(server_name, port_number, service_name=service_name)
                    connect_string = f"oracle://{username}:{password}@{dsn}"
                else:
                    connect_string = f"oracle://{username}:{password}@{server_name}:{port_number}/?service_name={service_name}"

                engine = sc.create_engine(connect_string)

            else:
                raise ValueError(
                    "Either sid, service_name, or use_wallet with service_name must be provided"
                )

            # Try to connect with the primary approach
            try:
                return engine.connect()
            except Exception as primary_error:
                self.logger.warning(f"Primary connection approach failed: {primary_error}")

                # If service_name is provided and we're not using wallet, try alternative formats
                if service_name and not use_wallet:
                    try:
                        # Try alternative 1: direct path format
                        connect_string = f"oracle://{username}:{password}@{server_name}:{port_number}/{service_name}"
                        engine = sc.create_engine(connect_string)
                        return engine.connect()
                    except Exception as alt1_error:
                        self.logger.warning(f"Alternative connection 1 failed: {alt1_error}")

                        try:
                            # Try alternative 2: DSN format
                            connect_string = f"oracle://{username}:{password}@/?dsn={server_name}:{port_number}/{service_name}"
                            engine = sc.create_engine(connect_string)
                            return engine.connect()
                        except Exception as alt2_error:
                            self.logger.warning(f"Alternative connection 2 failed: {alt2_error}")

                            # Re-raise primary error if all alternatives fail
                            raise primary_error
                else:
                    # Re-raise the original error if no alternatives to try
                    raise primary_error

        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(str(e))

    # def cassandra_connection(self, server_name: str | list, **kwargs):
    #     """Creates a Cassandra connection.
    #
    #     Args:
    #         server_name: Hostname or IP address of the Cassandra server, or a list of contact points.
    #         **kwargs: Keyword arguments for connection options.
    #
    #     Keyword Args:
    #         username (str): The username for authentication.
    #         password (str): The password for authentication.
    #         port_number (int): The Cassandra port (default: 9042).
    #         control_connection_timeout (float): Control connection timeout in seconds.
    #
    #     Returns:
    #         cassandra.cluster.Session: The Cassandra session object.
    #
    #     Raises:
    #         CassandraConnectionError: If a connection error occurs.
    #     """
    #     port = kwargs.get("port_number", 9042)
    #     control_timeout = kwargs.get("control_connection_timeout")
    #
    #     auth_provider = None
    #     if username := kwargs.get("username"):  # Walrus operator for cleaner assignment and check
    #         password = kwargs.get(
    #             "password"
    #         )  # Put password retrieval inside to avoid unused variable if no username
    #
    #         if not password:
    #             raise ValueError("Password is required when username is provided")
    #         auth_provider = PlainTextAuthProvider(username=username, password=password)
    #
    #     try:
    #         if isinstance(server_name, list):
    #             cluster = Cluster(
    #                 server_name,
    #                 auth_provider=auth_provider,
    #                 port=port,
    #                 control_connection_timeout=control_timeout,connection_class=AsyncioConnection
    #             )
    #         else:
    #             cluster = Cluster(
    #                 [server_name],  # Always a list of contact points
    #                 auth_provider=auth_provider,
    #                 port=port,
    #                 control_connection_timeout=control_timeout,
    #             )
    #
    #         session = cluster.connect(kwargs.get("database_name"))
    #         return session
    #
    #     except Exception as e:
    #         raise self.__obj_generic_exception.raise_generic_exception(
    #             str(e) + f"Error connecting to Cassandra: {e}"
    #         ) from e

    def establish_mongodb_connection(self, username, password, cluster_url, database_name):
        try:
            if self.crypt_bool_key and password:
                password = decrypt_password(password)
            if username is None or password is None or cluster_url is None or database_name is None:
                raise Exception("Please provide all the required parameters")
            elif (
                username is None
                and password is None
                and cluster_url is not None
                and database_name is None
            ):
                connection_string = (
                    f"mongodb+srv://{cluster_url}?retryWrites=true&w=majority&authSource=admin"
                )
            elif (
                username is None
                and password is None
                and cluster_url is not None
                and database_name is not None
            ):
                connection_string = f"mongodb+srv://{cluster_url}/{database_name}?retryWrites=true&w=majority&authSource=admin"
            else:
                connection_string = f"mongodb+srv://{username}:{password}@{cluster_url}/{database_name}?retryWrites=true&w=majority&authSource=admin"
            client = MongoClient(connection_string, maxPoolSize=1, minPoolSize=1)
            return client
        except Exception as e:
            print("Error occurred in establish_mongodb_connection: " + str(e))
            # self.__obj_generic_exception.raise_generic_exception(str(e))
