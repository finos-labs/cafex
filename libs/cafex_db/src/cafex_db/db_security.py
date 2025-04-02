import base64
import os
import urllib.parse

import cx_Oracle
import paramiko
import sqlalchemy as sc
from cafex_core.utils.config_utils import ConfigUtils
from cafex_core.utils.core_security import Security, decrypt_password
from cafex_core.utils.exceptions import CoreExceptions
from cafex_db.db_exceptions import DBExceptions

# from cassandra.auth import PlainTextAuthProvider
# from cassandra.cluster import Cluster
from Crypto.Cipher import AES
from pymongo import MongoClient

# from cassandra.auth import PlainTextAuthProvider
# from cassandra.cluster import Cluster


class DBSecurity(Security):
    """Class for database security-related functionality."""

    def __init__(self):
        super().__init__()
        self.crypt_bool_key = ConfigUtils().get_bool_decrypt_test_password()
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
        """Creates an SSH connection to a Hive server.

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

    def oracle(self, server_name: str, **kwargs) -> sc.engine.Connection:
        """Creates an Oracle connection."""

        try:
            username = kwargs.get("username")
            password = kwargs.get("password")
            port_number = kwargs.get("port_number")
            sid = kwargs.get("sid")
            service_name = kwargs.get("service_name")
            encoding = kwargs.get("encoding")

            if self.crypt_bool_key and password:
                password = decrypt_password(password)

            password = (
                self.encode_password(password)
                if kwargs.get("is_password_encoded", False)
                else password
            )

            if encoding:
                os.environ["NLS_LANG"] = f".{encoding.upper()}"

            if sid:
                tns = cx_Oracle.makedsn(server_name, port_number, sid=sid)
            elif service_name:
                tns = cx_Oracle.makedsn(server_name, port_number, service_name=service_name)
            else:
                raise ValueError("SID or SERVICE_NAME is required for Oracle connection.")

            if username and password:
                engine = sc.create_engine(f"oracle://{username}:{password}@{tns}")
                return engine.connect()
            else:
                raise ValueError("Username and password are required for Oracle connection.")
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(str(e))

    def cassandra_connection(self, server_name: str | list, **kwargs):
        """Creates a Cassandra connection.

        Args:
            server_name: Hostname or IP address of the Cassandra server, or a list of contact points.
            **kwargs: Keyword arguments for connection options.

        Keyword Args:
            username (str): The username for authentication.
            password (str): The password for authentication.
            port_number (int): The Cassandra port (default: 9042).
            control_connection_timeout (float): Control connection timeout in seconds.

        Returns:
            cassandra.cluster.Session: The Cassandra session object.

        Raises:
            CassandraConnectionError: If a connection error occurs.
        """
        port = kwargs.get("port_number", 9042)
        control_timeout = kwargs.get("control_connection_timeout")

        auth_provider = None
        if username := kwargs.get("username"):  # Walrus operator for cleaner assignment and check
            password = kwargs.get(
                "password"
            )  # Put password retrieval inside to avoid unused variable if no username

            if not password:
                raise ValueError("Password is required when username is provided")
            auth_provider = PlainTextAuthProvider(username=username, password=password)

        try:
            if isinstance(server_name, list):
                cluster = Cluster(
                    server_name,
                    auth_provider=auth_provider,
                    port=port,
                    control_connection_timeout=control_timeout,
                )
            else:
                cluster = Cluster(
                    [server_name],  # Always a list of contact points
                    auth_provider=auth_provider,
                    port=port,
                    control_connection_timeout=control_timeout,
                )

            session = cluster.connect(kwargs.get("database_name"))
            return session

        except Exception as e:
            raise e
            # raise self.__obj_generic_exception.raise_generic_exception(
            #     str(e) + f"Error connecting to Cassandra: {e}"
            # ) from e

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
