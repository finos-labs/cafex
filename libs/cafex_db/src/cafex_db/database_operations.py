# pylint: disable=too-many-public-methods, broad-exception-caught, broad-exception-raised

"""This module provides the DatabaseOperations class for various operations on
querying Database."""

import base64
import json
import os
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from Crypto.Cipher import AES  # noqa: F401

from cafex_core.logging.logger_ import CoreLogger  # type: ignore
from cafex_db.db_exceptions import DBExceptions
from cafex_db.db_security import DBSecurity


class DatabaseOperations:
    """This class provides a collection of methods for performing database
    operations.

    It includes functionalities for executing SQL queries, handling
    result sets, managing database connections, and comparing data
    between different sources.
    """

    def __init__(self):
        """Initializes the DatabaseOperations class."""
        self.__obj_db_decrypter = DBSecurity()
        self.logger_obj = CoreLogger(name=__name__).get_logger()
        self.__obj_db_exception = DBExceptions()

    def execute_statement(
        self,
        object_connection: Any,
        sql_query: str,
        str_return_type: str = "list",
    ) -> Union[List[Dict[str, Any]], Any, bool]:
        """Execute a SQL statement.

        Args:
            object_connection: Database connection object.
            sql_query: SQL query to execute.
            str_return_type: Return type, either 'list' or 'resultset'.

        Returns:
            List or ResultSet or Boolean
        """
        try:
            result = object_connection.execute(sql_query)
            if str_return_type == "list":
                return [dict(row) for row in result]
            if str_return_type == "resultset":
                return result
            return result.rowcount > 0
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def hive_execute_statement(
        self, object_hiveclient: Any, p_query: str, str_return_type: str = "list"
    ) -> Union[List[Any], Any, bool]:
        """Execute a HIVE database query statement using spark-sql.

        Args:
            object_hiveclient: Hive client object.
            p_query: Query to execute.
            str_return_type: Return type, either 'list' or 'resultset'
        Returns:
            List or ResultSet or Boolean
        """
        try:
            result = object_hiveclient.sql(p_query)
            if str_return_type == "list":
                return result.collect()
            if str_return_type == "resultset":
                return result
            return result.count() > 0
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def execute_query_from_file(self, object_connection: Any, pstr_filepath: str) -> Any:
        """Execute a SQL query from a file.

        Args:
            object_connection: Database connection object.
            pstr_filepath: File path of the SQL file.

        Returns:
            ResultSet
        """
        try:
            with open(pstr_filepath, "r", encoding="utf-8") as file:
                sql_query = file.read()
            return object_connection.execute(sql_query)
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def close(self, object_connection: Any) -> None:
        """Close the database connection.

        Args:
            object_connection: Database connection object.
        """
        try:
            object_connection.close()
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def check_table_exists(
        self,
        object_connection: Any,
        str_database_name: str,
        str_table_name: str,
        **kwargs,
    ) -> bool:
        """Check if a table exists in the database.

        Args:
            object_connection: Database connection object.
            str_database_name: Database name.
            str_table_name: Table name.
            kwargs: Additional arguments.

        Returns:
            Boolean indicating if the table exists.
        """
        try:
            query = (
                "SELECT * FROM information_schema.tables "
                f"WHERE table_schema = '{str_database_name}' "
                f"AND table_name = '{str_table_name}'"
            )
            result = object_connection.execute(query)
            return result.rowcount > 0
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def cassandra_resultset_to_list(self, prs_cassandra_resultset: Any) -> List[Any]:
        """Convert a Cassandra resultset to a list.

        Args:
            prs_cassandra_resultset: Cassandra resultset object.

        Returns:
            List representation of the resultset.
        """
        try:
            return list(prs_cassandra_resultset)
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def is_rowcount_zero(self, plist_resultlist: List[Any]) -> bool:
        """Check if the row count in the result list is zero.

        Args:
            plist_resultlist: Result list containing column headers and row values.

        Returns:
            Boolean indicating if the row count is zero.
        """
        try:
            return len(plist_resultlist) == 0
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def get_rowcount(self, plist_resultlist: List[Any]) -> int:
        """Get the row count from the result list.

        Args:
            plist_resultlist: Result list containing column headers and row values.

        Returns:
            Row count.
        """
        try:
            return len(plist_resultlist)
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def get_headers(self, plist_resultlist: List[Dict[str, Any]]) -> List[str]:
        """Get the headers from the result list.

        Args:
            plist_resultlist: Result list.

        Returns:
            List of headers.
        """
        try:
            return list(plist_resultlist[0].keys()) if plist_resultlist else []
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def resultset_to_list(
        self, prs_resultset: Any, pbool_include_headers: bool = True
    ) -> List[Any]:
        """Convert a resultset to a list.

        Args:
            prs_resultset: ResultSet object.
            pbool_include_headers: Whether to include headers in the list.

        Returns:
            List representation of the resultset.
        """
        try:
            result_list = [dict(row) for row in prs_resultset]
            if pbool_include_headers and result_list:
                result_list.insert(0, list(result_list[0].keys()))
            return result_list
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def decode_password(self, pkey: str, psecret_key: str) -> str:
        """Decode an encrypted password.

        Args:
            pkey: Encrypted password.
            psecret_key: Secret key for decryption.

        Returns:
            Decoded password.
        """
        try:
            cipher = AES.new(psecret_key.encode("utf-8"), AES.MODE_ECB)
            decoded = base64.b64decode(pkey)
            decrypted = cipher.decrypt(decoded).decode("utf-8").strip()
            return decrypted
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def check_value_exists_in_column(
        self, plist_resultlist: List[Dict[str, Any]], pstr_column_header: str, pstr_value: Any
    ) -> bool:
        """Check if a value exists in a specific column of the result list.

        Args:
            plist_resultlist: Result list.
            pstr_column_header: Column header to check.
            pstr_value: Value to check for.

        Returns:
            Boolean indicating if the value exists in the column.
        """
        try:
            return any(row[pstr_column_header] == pstr_value for row in plist_resultlist)
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def check_value_not_exists_in_column(
        self, plist_resultlist: List[Dict[str, Any]], pstr_column_header: str, pstr_value: Any
    ) -> bool:
        """Check if a value does not exist in a specific column of the result
        list.

        Args:
            plist_resultlist: Result list.
            pstr_column_header: Column header to check.
            pstr_value: Value to check for.

        Returns:
            Boolean indicating if the value does not exist in the column.
        """
        try:
            return all(row[pstr_column_header] != pstr_value for row in plist_resultlist)
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def get_column_data(
        self, plist_resultlist: List[Dict[str, Any]], pstr_column_header: str
    ) -> List[Any]:
        """Get data from a specific column in the result list.

        Args:
            plist_resultlist: Result list.
            pstr_column_header: Column header to get data from.

        Returns:
            List of data from the column.
        """
        try:
            return [row[pstr_column_header] for row in plist_resultlist]
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def compare_resultlists(
        self,
        plist_resultlist1: List[Dict[str, Any]],
        plist_resultlist2: List[Dict[str, Any]],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Compare two result lists.

        Args:
            plist_resultlist1: First result list.
            plist_resultlist2: Second result list.
            kwargs: Additional arguments.

        Returns:
            Comparison result.
        """
        try:
            set1 = set(tuple(row.items()) for row in plist_resultlist1)
            set2 = set(tuple(row.items()) for row in plist_resultlist2)
            return {
                "only_in_list1": [dict(items) for items in set1 - set2],
                "only_in_list2": [dict(items) for items in set2 - set1],
                "in_both": [dict(items) for items in set1 & set2],
            }
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def data_frame_diff(
        self, pdf_dataframe_source: pd.DataFrame, pdf_dataframe_destinition: pd.DataFrame, **kwargs
    ) -> pd.DataFrame:
        """Compare two dataframes and return the differences.

        Args:
            pdf_dataframe_source: Source dataframe.
            pdf_dataframe_destinition: Destination dataframe.
            kwargs: Additional arguments.

        Returns:
            Dataframe with differences.
        """
        try:
            diff = pd.concat([pdf_dataframe_source, pdf_dataframe_destinition]).drop_duplicates(
                keep=False
            )
            return diff
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def dataframe_to_resultset(self, pdf_dataframe: pd.DataFrame) -> List[Dict[str, Any]]:
        """Convert a dataframe to a resultset.

        Args:
            pdf_dataframe: Dataframe to convert.

        Returns:
            ResultSet
        """
        try:
            return pdf_dataframe.to_dict(orient="records")
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def file_to_resultlist(
        self, pstr_filepath: str, pstr_filetype: str = "csv", **kwargs
    ) -> List[Dict[str, Any]]:
        """Convert data in a file to a result list.

        Args:
            pstr_filepath: File path.
            pstr_filetype: File type, either 'csv', 'excel', or 'json'.
            kwargs: Additional arguments.

        Returns:
            Result list.
        """
        try:
            if pstr_filetype == "csv":
                return pd.read_csv(pstr_filepath, **kwargs).to_dict(orient="records")
            if pstr_filetype == "excel":
                return pd.read_excel(pstr_filepath, **kwargs).to_dict(orient="records")
            if pstr_filetype == "json":
                with open(pstr_filepath, "r", encoding="utf-8") as file:
                    return json.load(file)
            raise ValueError("Unsupported file type")
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def resultlist_to_csv(self, plist_resultlist: List[Dict[str, Any]], pstr_filepath: str) -> None:
        """Write a result list to a CSV file.

        Args:
            plist_resultlist: Result list.
            pstr_filepath: File path to save the CSV.
        """
        try:
            pd.DataFrame(plist_resultlist).to_csv(pstr_filepath, index=False)
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def dataframe_to_csv(self, pdf_dataframe: pd.DataFrame, pstr_path: str) -> None:
        """Write a dataframe to a CSV file.

        Args:
            pdf_dataframe: Dataframe to write.
            pstr_path: File path to save the CSV.
        """
        try:
            pdf_dataframe.to_csv(pstr_path, index=False)
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def list_to_dataframe(self, plist_data: List[Any]) -> pd.DataFrame:
        """Convert a list to a dataframe.

        Args:
            plist_data: List to convert.

        Returns:
            Dataframe
        """
        try:
            return pd.DataFrame(plist_data)
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def compare_dataframes_distinct(
        self, pdf_dataframe_source: pd.DataFrame, pdf_dataframe_target: pd.DataFrame, **kwargs
    ) -> pd.DataFrame:
        """Compare two dataframes and return distinct differences.

        Args:
            pdf_dataframe_source: Source dataframe.
            pdf_dataframe_target: Target dataframe.
            kwargs: Additional arguments.

        Returns:
            Dataframe with distinct differences.
        """
        try:
            diff = pd.concat([pdf_dataframe_source, pdf_dataframe_target]).drop_duplicates(
                keep=False
            )
            return diff
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def check_data_in_column(
        self, plist_resultlist: List[Dict[str, Any]], pdata_value: Any, **kwargs
    ) -> bool:
        """Check if a value is present in a column of the result list.

        Args:
            plist_resultlist: Result list.
            pdata_value: Value to check for.
            kwargs: Additional arguments.

        Returns:
            Boolean indicating if the value is present.
        """
        try:
            return any(pdata_value in row.values() for row in plist_resultlist)
        except Exception as e:  # pylint: disable=broad-exception-caught
            raise e

    def check_headers_in_resultlist(
        self, plist_resultlist: List[Dict[str, Any]], plist_headers: List[str], **kwargs
    ) -> List[str]:
        """Check if headers are present in the result list.

        Args:
            plist_resultlist: Result list.
            plist_headers: List of headers to check for.
            kwargs: Additional arguments.

        Returns:
            List of unmatched headers.
        """
        try:
            result_headers = set(self.get_headers(plist_resultlist))
            return [header for header in plist_headers if header not in result_headers]
        except Exception as e:  # pylint: disable=broad-exception-caught
            raise e

    def spark_execute_statement(
        self,
        pobject_sparkclient: Any,
        p_query: str,
        pbool_default_spark_command: bool,
        pstr_name: str,
        str_return_type: str = "list",
        **kwargs,
    ) -> Union[List[Any], Any, bool]:
        """Execute a HIVE database query statement using spark-sql.

        Args:
            pobject_sparkclient: Spark-Sql Database Connection Object.
            p_query: Query to execute.
            pbool_default_spark_command: If True, default spark command is used.
            pstr_name: Spark config name.
            str_return_type: Return type, either 'list' or 'resultset'.
            kwargs: Additional arguments.

        Returns:
            List or ResultSet or Boolean.
        """
        try:
            result = pobject_sparkclient.sql(p_query)
            if str_return_type == "list":
                return result.collect()
            if str_return_type == "resultset":
                return result
            return result.count() > 0
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(str(e))

    def check_db_exists(self, pobject_connection: Any, pstr_database_name: str) -> bool:
        """Check if a database exists in a particular DB server.

        Args:
            pobject_connection: Connection object provided by the user.
            pstr_database_name: DB name provided by the user.

        Returns:
            bool: True if database exists, False otherwise.

        Raises:
            DBExceptions: If connection object or database name is None.
            Exception: If the database type is not supported.
        """
        try:
            if pobject_connection is None:
                self.__obj_db_exception.raise_null_database_object()
            if pstr_database_name is None:
                self.__obj_db_exception.raise_null_database_name()

            if pobject_connection.engine.name == "postgresql":
                sql_query = (
                    f"SELECT * FROM pg_catalog.pg_database WHERE datname='{pstr_database_name}'"
                )
                rs_resultset = self.execute_statement(
                    pobject_connection, sql_query, str_return_type="resultset"
                )
                return rs_resultset.rowcount != 0

            if pobject_connection.engine.name == "mssql":
                sql_query = f"SELECT * FROM sys.databases WHERE name='{pstr_database_name}'"
                rs_resultset = self.execute_statement(
                    pobject_connection, sql_query, str_return_type="resultset"
                )
                return rs_resultset.rowcount != 0

            if pobject_connection.engine.name == "oracle":
                sql_query = (
                    f"SELECT owner FROM all_tab_columns WHERE Owner ='{pstr_database_name.upper()}'"
                )
                lst_result = self.execute_statement(
                    pobject_connection, sql_query, str_return_type="list"
                )
                return len(lst_result) >= 2

            raise self.__obj_db_exception.raise_generic_exception(
                message=f"Error -> Provided parameters are not supported",
                trim_log=True,
                fail_test=False,
            )

        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(
                message=f"Error -> DB not connected properly: {str(e)}",
                trim_log=True,
                fail_test=False,
            )

    def verify_column_metadata(
        self,
        pobj_connection: Any,
        pstr_db_name: str,
        str_table_name: str,
        pstr_col_name: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Verify metadata for a column in a database table.

        Args:
            pobj_connection: Database connection object.
            pstr_db_name: Database name.
            str_table_name: Table name.
            pstr_col_name: Column name.
            kwargs: Additional arguments for checking existence, data type, constraints, etc.

        Returns:
            Dictionary containing metadata information.
        """
        try:
            dict_result: Dict[str, Any] = {}
            if pobj_connection.engine.name not in ("mssql", "oracle", "postgresql"):
                raise self.__obj_db_exception.raise_generic_exception(
                    message=f"Error -> Provided parameters are not supported",
                    trim_log=True,
                    fail_test=False,
                )

            if "bln_col_existence" in kwargs:
                dict_result["bln_col_existence"] = self._check_column_existence(
                    pobj_connection, pstr_db_name, str_table_name, pstr_col_name
                )

            if "pstr_data_type" in kwargs:
                dict_result["pstr_data_type"] = self._get_column_data_type(
                    pobj_connection, pstr_db_name, str_table_name, pstr_col_name
                )

            if "pstr_max_length" in kwargs:
                dict_result["pstr_max_length"] = self._get_column_max_length(
                    pobj_connection, pstr_db_name, str_table_name, pstr_col_name
                )

            if "bln_is_null" in kwargs:
                dict_result["bln_is_null"] = self._check_column_nullable(
                    pobj_connection, pstr_db_name, str_table_name, pstr_col_name
                )

            if "bln_is_not_null" in kwargs:
                dict_result["bln_is_not_null"] = not self._check_column_nullable(
                    pobj_connection, pstr_db_name, str_table_name, pstr_col_name
                )

            if "bln_is_primary_key" in kwargs:
                dict_result["bln_is_primary_key"] = self._check_column_primary_key(
                    pobj_connection, pstr_db_name, str_table_name, pstr_col_name
                )

            if "bln_is_not_primary_key" in kwargs:
                dict_result["bln_is_not_primary_key"] = not self._check_column_primary_key(
                    pobj_connection, pstr_db_name, str_table_name, pstr_col_name
                )

            return dict_result

        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(
                message=f"Error -> Column information is not given properly: {str(e)}",
                trim_log=True,
                fail_test=False,
            )

    def _check_column_existence(
        self, pobj_connection: Any, pstr_db_name: str, str_table_name: str, pstr_col_name: str
    ) -> bool:
        """Helper method to check column existence."""
        if pobj_connection.engine.name == "oracle":
            lst_result = self.execute_statement(
                pobj_connection,
                f"SELECT * FROM all_tab_columns WHERE table_name = '{str_table_name.upper()}' "
                f"AND column_name ='{pstr_col_name.upper()}' AND owner='{pstr_db_name.upper()}'",
                str_return_type="list",
            )
            return len(lst_result) >= 2

        if pobj_connection.engine.name == "postgresql":
            rs_resultset = self.execute_statement(
                pobj_connection,
                f"SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{str_table_name}' "
                f"AND COLUMN_NAME = '{pstr_col_name}' AND table_schema='{pstr_db_name}'",
                str_return_type="resultset",
            )
            return rs_resultset.rowcount != 0

        if pobj_connection.engine.name == "mssql":
            rs_resultset = self.execute_statement(
                pobj_connection,
                f"USE {pstr_db_name} SELECT * FROM INFORMATION_SCHEMA.COLUMNS "
                f"WHERE TABLE_NAME = '{str_table_name}' AND COLUMN_NAME = '{pstr_col_name}'",
                str_return_type="resultset",
            )
            return rs_resultset.rowcount != 0

        return False

    def _get_column_data_type(
        self, pobj_connection: Any, pstr_db_name: str, str_table_name: str, pstr_col_name: str
    ) -> Optional[str]:
        """Helper method to get column data type."""
        if pobj_connection.engine.name == "oracle":
            rs_resultset = self.execute_statement(
                pobj_connection,
                f"SELECT data_type FROM all_tab_columns WHERE table_name = '{str_table_name.upper()}' "
                f"AND column_name ='{pstr_col_name.upper()}' AND owner='{pstr_db_name.upper()}'",
                str_return_type="resultset",
            )
            pstr_datatype = rs_resultset.fetchall()
            return pstr_datatype[0][0] if pstr_datatype[0][0] else None

        if pobj_connection.engine.name == "postgresql":
            rs_resultset = self.execute_statement(
                pobj_connection,
                f"SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{str_table_name}' "
                f"AND COLUMN_NAME = '{pstr_col_name}' AND table_schema='{pstr_db_name}'",
                str_return_type="resultset",
            )
            pstr_datatype = rs_resultset.fetchall()
            return pstr_datatype[0][0] if pstr_datatype[0][0] else None

        if pobj_connection.engine.name == "mssql":
            rs_resultset = self.execute_statement(
                pobj_connection,
                f"USE {pstr_db_name} SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS "
                f"WHERE TABLE_NAME = '{str_table_name}' AND COLUMN_NAME = '{pstr_col_name}'",
                str_return_type="resultset",
            )
            pstr_datatype = rs_resultset.fetchall()
            return pstr_datatype[0][0] if pstr_datatype[0][0] else None

        return None

    def _get_column_max_length(
        self, pobj_connection: Any, pstr_db_name: str, str_table_name: str, pstr_col_name: str
    ) -> Optional[int]:
        """Helper method to get column max length."""
        if pobj_connection.engine.name == "postgresql":
            rs_resultset = self.execute_statement(
                pobj_connection,
                f"SELECT character_maximum_length FROM INFORMATION_SCHEMA.COLUMNS "
                f"WHERE TABLE_NAME = '{str_table_name}' AND COLUMN_NAME = '{pstr_col_name}' "
                f"AND table_schema='{pstr_db_name}'",
                str_return_type="resultset",
            )
            pstr_maxlength = rs_resultset.fetchall()
            return int(pstr_maxlength[0][0]) if pstr_maxlength[0][0] else None

        if pobj_connection.engine.name == "mssql":
            rs_resultset = self.execute_statement(
                pobj_connection,
                f"USE {pstr_db_name} SELECT * FROM sys.columns WHERE name=N'{pstr_col_name}' "
                f"AND OBJECT_ID = OBJECT_ID(N'{str_table_name}')",
                str_return_type="resultset",
            )
            pstr_maxlength = rs_resultset.fetchall()
            return int(pstr_maxlength[0][5]) if pstr_maxlength[0][5] else None

        if pobj_connection.engine.name == "oracle":
            rs_resultset = self.execute_statement(
                pobj_connection,
                f"SELECT data_length FROM all_tab_columns WHERE table_name = '{str_table_name.upper()}' "
                f"AND column_name ='{pstr_col_name.upper()}' AND owner='{pstr_db_name.upper()}'",
                str_return_type="resultset",
            )
            pstr_maxlength = rs_resultset.fetchall()
            return int(pstr_maxlength[0][0]) if pstr_maxlength[0][0] else None

        return None

    def _check_column_nullable(
        self, pobj_connection: Any, pstr_db_name: str, str_table_name: str, pstr_col_name: str
    ) -> bool:
        """Helper method to check column nullable constraint."""
        if pobj_connection.engine.name == "oracle":
            rs_resultset = self.execute_statement(
                pobj_connection,
                f"SELECT nullable FROM all_tab_columns WHERE table_name = '{str_table_name.upper()}' "
                f"AND column_name ='{pstr_col_name.upper()}' AND owner='{pstr_db_name.upper()}'",
                str_return_type="resultset",
            )
            bln_isnull = rs_resultset.fetchall()
            return bln_isnull[0][0] == "Y"

        if pobj_connection.engine.name == "postgresql":
            rs_resultset = self.execute_statement(
                pobj_connection,
                f"SELECT is_nullable FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{str_table_name}' "
                f"AND COLUMN_NAME = '{pstr_col_name}' AND table_schema='{pstr_db_name}'",
                str_return_type="resultset",
            )
            bln_isnull = rs_resultset.fetchall()
            return bln_isnull[0][0] == "YES"

        if pobj_connection.engine.name == "mssql":
            rs_resultset = self.execute_statement(
                pobj_connection,
                f"USE {pstr_db_name} SELECT is_nullable FROM INFORMATION_SCHEMA.COLUMNS "
                f"WHERE TABLE_NAME = '{str_table_name}' AND COLUMN_NAME = '{pstr_col_name}'",
                str_return_type="resultset",
            )
            bln_isnull = rs_resultset.fetchall()
            return bln_isnull[0][0] == "YES"

        return False

    def _check_column_primary_key(
        self, pobj_connection: Any, pstr_db_name: str, str_table_name: str, pstr_col_name: str
    ) -> bool:
        """Helper method to check column primary key constraint."""
        if pobj_connection.engine.name == "oracle":
            rs_resultset = self.execute_statement(
                pobj_connection,
                f"SELECT cols.table_name, cols.column_name, cols.position, cons.status, cons.owner "
                f"FROM all_constraints cons, all_cons_columns cols WHERE cols.table_name ='{str_table_name.upper()}' "
                f"AND cols.column_name ='{pstr_col_name.upper()}' AND cons.constraint_type = 'P' "
                f"AND cons.constraint_name = cols.constraint_name AND cons.owner = cols.owner "
                f"ORDER BY cols.table_name, cols.position",
                str_return_type="list",
            )
            return len(rs_resultset) >= 2

        if pobj_connection.engine.name == "postgresql":
            rs_resultset = self.execute_statement(
                pobj_connection,
                f"SELECT K.TABLE_NAME, C.CONSTRAINT_TYPE, K.COLUMN_NAME, K.CONSTRAINT_NAME "
                f"FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS C JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS K "
                f"ON C.TABLE_NAME = K.TABLE_NAME AND C.CONSTRAINT_CATALOG = K.CONSTRAINT_CATALOG "
                f"AND C.CONSTRAINT_SCHEMA = K.CONSTRAINT_SCHEMA AND C.CONSTRAINT_NAME = K.CONSTRAINT_NAME "
                f"WHERE C.CONSTRAINT_TYPE = 'PRIMARY KEY' AND K.Table_Name='{str_table_name}' "
                f"AND K.Column_name='{pstr_col_name}' AND K.table_schema='{pstr_db_name}' "
                f"ORDER BY K.TABLE_NAME, C.CONSTRAINT_TYPE, K.CONSTRAINT_NAME",
                str_return_type="resultset",
            )
            return rs_resultset.rowcount != 0

        if pobj_connection.engine.name == "mssql":
            rs_resultset = self.execute_statement(
                pobj_connection,
                f"USE {pstr_db_name} SELECT K.TABLE_NAME, C.CONSTRAINT_TYPE, K.COLUMN_NAME, K.CONSTRAINT_NAME "
                f"FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS C JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS K "
                f"ON C.TABLE_NAME = K.TABLE_NAME AND C.CONSTRAINT_CATALOG = K.CONSTRAINT_CATALOG "
                f"AND C.CONSTRAINT_SCHEMA = K.CONSTRAINT_SCHEMA AND C.CONSTRAINT_NAME = K.CONSTRAINT_NAME "
                f"WHERE C.CONSTRAINT_TYPE = 'PRIMARY KEY' AND K.Table_Name='{str_table_name}' "
                f"AND K.Column_name='{pstr_col_name}' ORDER BY K.TABLE_NAME, C.CONSTRAINT_TYPE, K.CONSTRAINT_NAME",
                str_return_type="resultset",
            )
            return rs_resultset.rowcount != 0

        return False

    def modify_sql_query(
        self, pfile_path: str, pdict_data_dictionary: Dict[str, str], **kwargs
    ) -> str:
        """Modify SQL queries residing inside .sql, .txt, or .json files at
        runtime.

        Args:
            pfile_path: File path of the file that will be edited.
            pdict_data_dictionary: Dictionary in the format {'unique_identifiers1': 'actual_value1'}.
            kwargs: Additional arguments (e.g., pstr_key for JSON files).

        Returns:
            The query with unique identifiers replaced by actual values.
        """
        try:
            if pfile_path is None:
                self.__obj_db_exception.raise_null_filepath()
            if os.stat(pfile_path).st_size == 0:
                self.__obj_db_exception.raise_null_query()
            if pdict_data_dictionary is None:
                raise Exception("Dictionary passed is None. There is nothing to replace")

            if pfile_path.endswith((".sql", ".txt")):
                with open(pfile_path, "r", encoding="utf-8") as f:
                    str_query = f.read()

            elif pfile_path.endswith(".json"):
                if "pstr_key" not in kwargs:
                    raise Exception("Error-->Key missing from parameters for json file")

                json_key = str(kwargs.get("pstr_key"))
                with open(pfile_path, "r", encoding="utf-8") as f:
                    str_json = f.read()

                try:
                    pstr_json = json.loads(str_json)
                    str_query = pstr_json[json_key]
                except Exception as e:
                    raise Exception(f"Not a valid json file or invalid key-->{str(e)}") from e

            else:
                raise Exception("Accepted file formats are .sql, .txt & .json")

            for key, value in pdict_data_dictionary.items():
                if key in str_query:
                    str_query = str_query.replace(key, value)
                else:
                    raise Exception(f"Unique Identifier-->{key} not found in the query")

            return str_query

        except Exception as e:  # pylint: disable=broad-exception-caught
            self.__obj_db_exception.raise_generic_exception(
                message=f"Exception occurred in method--> modify_sql_query-->: {str(e)}",
                trim_log=True,
                fail_test=False,
            )
