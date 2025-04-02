import os
import pandas as pd
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from snowflake.connector import *
from cafex_core.utils.exceptions import CoreExceptions


class SnowflakeUtil:
    """
    Description:
        |  This Class contains the methods to create connection with Snowflake and retrieve
        data from Snowflake tables

    """

    def __init__(self):
        self.__obj_generic_exception = CoreExceptions()

    def create_snowflake_connection(
        self,
        str_username,
        str_password,
        str_account,
        str_warehouse,
        str_database=None,
        str_schema=None,
    ):
        """
        Description:
            |  This method creates the connection with Snowflake based on the given information

        :param str_username: Username to connect with snowflake
        :type str_username: String
        :param str_password: Password to connect with snowflake
        :type str_password: String
        :param str_account: Snowflake warehouse account
        :type str_account: String
        :param str_warehouse: Warehouse in Snowflake in which database exist
        :type str_warehouse: String
        :param str_database: Database in Snowflake Warehouse in which required data exist
        :type str_database: String
        :param str_schema: Schema in Snowflake Database
        :type str_schema: String

        :return: Snowflake Connection
        """
        try:
            conn = snowflake.connector.connect(
                user=str_username,
                password=str_password,
                account=str_account,
                warehouse=str_warehouse,
                database=str_database,
                schema=str_schema,
            )

            return conn
        except Exception as ex:
            self.__obj_generic_exception.raise_generic_exception(str(ex))

    def create_snowflake_connection_by_pem(
        self,
        str_username,
        str_account,
        str_warehouse,
        private_pem_file_path,
        str_database=None,
        str_schema=None,
        str_role=None,
    ):
        """
        Description:
            |  This method creates the connection with Snowflake using PEM KEY

        :param str_username: Username to connect with snowflake
        :type str_username: String
        :param str_account: Snowflake warehouse account
        :type str_account: String
        :param str_warehouse: Warehouse in Snowflake in which database exist
        :type str_warehouse: String
        :param private_pem_file_path: Private pem file path
        :type private_pem_file_path: String
        :param str_database: Database in Snowflake Warehouse in which required data exist
        :type str_database: String
        :param str_schema: Schema in Snowflake Database
        :type str_schema: String
        :param str_role: role of user
        :type str_role: String
        :return: Snowflake Connection

        Examples:
            |  sf_util = SnowflakeUtil()
               sf_util.create_snowflake_connection_by_pem("user", "account", "warehouse", "pem_path", "database")
        """
        try:
            with open(private_pem_file_path, "rb") as private_key_file:
                private_key_pem = private_key_file.read()
            private_key_loaded = serialization.load_pem_private_key(private_key_pem, password=None)
            private_key_loaded.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
            conn = snowflake.connector.connect(
                user=str_username,
                account=str_account,
                warehouse=str_warehouse,
                database=str_database,
                schema=str_schema,
                role=str_role,
                private_key=private_key_loaded,
            )
            return conn
        except Exception as ex:
            self.__obj_generic_exception.raise_generic_exception(str(ex))

    def get_snowflake_table_count(self, obj_snowflake_conn, str_query):
        """
        Description:
            |  This method gets the count from Snowflake table and return it to the user

        :param obj_snowflake_conn: Snowflake connection
        :type obj_snowflake_conn: Snowflake connection object
        :param str_query: Count query for Snowflake table
        :type str_query: String

        example:
         str_query: Select Count(*) From TableName

        :return: Table count
        """
        try:
            str_result = {}
            cur = obj_snowflake_conn.cursor(DictCursor)
            cur.execute(str_query)

            for rec in cur:
                str_result = "{0}".format(rec["COUNT(*)"])

            return str_result
        except Exception as ex:
            self.__obj_generic_exception.raise_generic_exception(str(ex))

    def get_snowflake_table_data(self, obj_snowflake_conn, str_query, str_return_type="list"):
        """
        Description:
            |  This method gets the data form snowflake table and return it to the user in
                the form of list or data frame as specified by the user

        :param obj_snowflake_conn: Snowflake connection
        :type obj_snowflake_conn: Snowflake connection object
        :param str_query: Query to execute on Snowflake
        :type str_query: String
        :param str_return_type: Return type in which user wants to receive the data [list/df]
        :type str_return_type: String

        :return: Data from Snowflake table on the basis of query
        """
        try:
            cur = obj_snowflake_conn.cursor(DictCursor)
            dict_data = cur.execute(str_query).fetchall()

            if str_return_type == "list":
                result = dict_data
            elif str_return_type == "df":
                result = pd.DataFrame(dict_data)
            else:
                return "Please select the correct return type"

            return result
        except Exception as ex:
            self.__obj_generic_exception.raise_generic_exception(str(ex))

    def close_snowflake_connection(self, obj_snowflake_conn):
        """
        Description:
            |  This method closes the given snowflake connection

        :param obj_snowflake_conn: Snowflake connection
        :type objd_snowflake_conn: Snowflake connection object

        """
        try:
            cur = obj_snowflake_conn.cursor(DictCursor)
            cur.close()
            return True
        except Exception as ex:
            self.__obj_generic_exception.raise_generic_exception(str(ex))
