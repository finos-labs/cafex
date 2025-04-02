import os

import pandas as pd
import snowflake.connector
from cafex_core.utils.exceptions import Exceptions
from cryptography.hazmat.primitives import serialization
from snowflake.connector import *


class SnowflakeUtil:
    """
    Description:
        |  This Class contains the methods to create connection with Snowflake and retrieve
        data from Snowflake tables

    """

    def __init__(self):
        self.__obj_exception = Exceptions(os.getcwd())
        self.__obj_generic_exception = self.__obj_exception.Generic()

    def create_snowflake_connection(
        self,
        pstr_username,
        pstr_password,
        pstr_account,
        pstr_warehouse,
        pstr_database=None,
        pstr_schema=None,
    ):
        """
        Description:
            |  This method creates the connection with Snowflake based on the given information

        :param pstr_username: Username to connect with snowflake
        :type pstr_username: String
        :param pstr_password: Password to connect with snowflake
        :type pstr_password: String
        :param pstr_account: Snowflake warehouse account
        :type pstr_account: String
        :param pstr_warehouse: Warehouse in Snowflake in which database exist
        :type pstr_warehouse: String
        :param pstr_database: Database in Snowflake Warehouse in which required data exist
        :type pstr_database: String
        :param pstr_schema: Schema in Snowflake Database
        :type pstr_schema: String

        :return: Snowflake Connection
        """
        try:
            conn = snowflake.connector.connect(
                user=pstr_username,
                password=pstr_password,
                account=pstr_account,
                warehouse=pstr_warehouse,
                database=pstr_database,
                schema=pstr_schema,
            )

            return conn
        except Exception as ex:
            self.__obj_generic_exception.raise_custom_exception(str(ex))

    def create_snowflake_connection_by_pem(
        self,
        pstr_username,
        pstr_account,
        pstr_warehouse,
        private_pem_file_path,
        pstr_database=None,
        pstr_schema=None,
        pstr_role=None,
    ):
        """
        Description:
            |  This method creates the connection with Snowflake using PEM KEY

        :param pstr_username: Username to connect with snowflake
        :type pstr_username: String
        :param pstr_account: Snowflake warehouse account
        :type pstr_account: String
        :param pstr_warehouse: Warehouse in Snowflake in which database exist
        :type pstr_warehouse: String
        :param private_pem_file_path: Private pem file path
        :type private_pem_file_path: String
        :param pstr_database: Database in Snowflake Warehouse in which required data exist
        :type pstr_database: String
        :param pstr_schema: Schema in Snowflake Database
        :type pstr_schema: String
        :param pstr_role: role of user
        :type pstr_role: String
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
                user=pstr_username,
                account=pstr_account,
                warehouse=pstr_warehouse,
                database=pstr_database,
                schema=pstr_schema,
                role=pstr_role,
                private_key=private_key_loaded,
            )
            return conn
        except Exception as ex:
            self.__obj_generic_exception.raise_custom_exception(str(ex))

    def get_snowflake_table_count(self, pobj_snowflake_conn, pstr_query):
        """
        Description:
            |  This method gets the count from Snowflake table and return it to the user

        :param pobj_snowflake_conn: Snowflake connection
        :type pobj_snowflake_conn: Snowflake connection object
        :param pstr_query: Count query for Snowflake table
        :type pstr_query: String

        example:
         pstr_query: Select Count(*) From TableName

        :return: Table count
        """
        try:
            str_result = {}
            cur = pobj_snowflake_conn.cursor(DictCursor)
            cur.execute(pstr_query)

            for rec in cur:
                str_result = "{0}".format(rec["COUNT(*)"])

            return str_result
        except Exception as ex:
            self.__obj_generic_exception.raise_custom_exception(str(ex))

    def get_snowflake_table_data(self, pobj_snowflake_conn, pstr_query, pstr_return_type="list"):
        """
        Description:
            |  This method gets the data form snowflake table and return it to the user in
                the form of list or data frame as specified by the user

        :param pobj_snowflake_conn: Snowflake connection
        :type pobj_snowflake_conn: Snowflake connection object
        :param pstr_query: Query to execute on Snowflake
        :type pstr_query: String
        :param pstr_return_type: Return type in which user wants to receive the data [list/df]
        :type pstr_return_type: String

        :return: Data from Snowflake table on the basis of query
        """
        try:
            cur = pobj_snowflake_conn.cursor(DictCursor)
            dict_data = cur.execute(pstr_query).fetchall()

            if pstr_return_type == "list":
                result = dict_data
            elif pstr_return_type == "df":
                result = pd.DataFrame(dict_data)
            else:
                return "Please select the correct return type"

            return result
        except Exception as ex:
            self.__obj_generic_exception.raise_custom_exception(str(ex))

    def close_snowflake_connection(self, pobj_snowflake_conn):
        """
        Description:
            |  This method closes the given snowflake connection

        :param pobj_snowflake_conn: Snowflake connection
        :type pobj_snowflake_conn: Snowflake connection object

        """
        try:
            cur = pobj_snowflake_conn.cursor(DictCursor)
            cur.close()
            return True
        except Exception as ex:
            self.__obj_generic_exception.raise_custom_exception(str(ex))
