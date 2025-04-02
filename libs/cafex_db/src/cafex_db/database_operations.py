import base64
import csv
import json
import os

import cx_Oracle
import numpy as np
import pandas as pd
import paramiko as hive_SSH
import sqlalchemy as sc
from cafex_core.logging.logger_ import CoreLogger
from cafex_db.db_exceptions import DBExceptions
from cafex_db.db_security import DBSecurity

# from cassandra.auth import PlainTextAuthProvider
# from cassandra.cluster import Cluster
from Crypto.Cipher import AES
from sqlalchemy import create_engine


class DatabaseOperations:
    def __init__(self):
        """Initializes the DatabaseConnection class."""
        super().__init__()
        self.__obj_db_decrypter = DBSecurity()
        self.logger_obj = CoreLogger(name=__name__).get_logger()
        self.__obj_db_exception = DBExceptions()

    def execute_statement(self, object_connection, sql_query, str_return_type='list'):
        """
        Description:
            |  This method allows user to execute a database query statement.

        :param object_connection:
        :type object_connection: Database Connection Object
        :param sql_query:
        :type sql_query: String
        :param str_return_type: list/resultset
        :type str_return_type: String


        :return: List or ResultSet or Boolean

        .. notes::
            |  This method returns a list or a resultset based on the parameter str_return_type. 'select' statements will returns List/Resultset and other type of statements will return Boolean.

        .. warning::
            |  This method can not be used to execute HIVE statements.
        """
        try:

            if object_connection is None:
                self.__obj_db_exception.raise_null_database_object()
            if sql_query is None:
                self.__obj_db_exception.raise_null_query()

            if str_return_type is 'list':
                if str(sql_query).strip().lower().startswith('select'):
                    resultset = object_connection.execute(sql_query)
                    if 'cassandra' in repr(object_connection):
                        datalist = self.cassandra_resultset_to_list(resultset)
                    else:
                        datalist = self.resultset_to_list(resultset, pbool_include_headers=True)
                    result = datalist
                else:
                    self.__obj_db_exception.raise_generic_exception(
                        "For str_return_type == 'list', only select statements are allowed")

            elif str_return_type is 'resultset':

                if str(sql_query).strip().lower().startswith('select'):
                    resultset = object_connection.execute(sql_query)
                    result = resultset
                elif str(sql_query).strip().lower().startswith('insert'):
                    resultset = object_connection.execute(sql_query)
                    if (resultset.rowcount > 0):
                        self.logger_obj.info("Successully inserted")
                        result = True
                elif str(sql_query).strip().lower().startswith('update'):
                    resultset = object_connection.execute(sql_query)
                    if (resultset.rowcount > 0):
                        self.logger_obj.info("Successully Updated")
                        result = True
                elif str(sql_query).strip().lower().startswith('delete'):
                    object_connection.execute(sql_query)
                    result = True
                else:
                    resultset = object_connection.execute(sql_query)
                    result = resultset

            return result

        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def hive_execute_statement(
        self, object_hiveclient, p_query, str_return_type="list", **kwargs
    ):
        """
        Description:
            |  This method allows user to execute a HIVE database query statement.

        :param object_hiveclient:
        :type object_hiveclient: Hive Database Connection Object
        :param p_query:
        :type p_query: String
        :param str_return_type: list/resultset
        :type str_return_type: String
        :param pbool_include_header: default value is False, if set to true will print the headers also
        :type pbool_include_header: kwargs:bool
        :param pstr_server_connect: If the user needs to connect to a server then he can send the command to this pararmeter
        :type pstr_server_connect: kwargs:string


        :return: List or ResultSet or Boolean

        .. notes::
            |  This method returns a list or a resultset based on the parameter str_return_type. 'select' statements will returns List/Resultset and other type of statements will return Boolean.


        """
        try:
            bool_include_header = kwargs.get("pbool_include_header", False)
            str_server_connect = kwargs.get("pstr_server_connect", None)

            if object_hiveclient is None:
                self.__obj_db_exception.raise_null_hive_object()
            if p_query is None:
                self.__obj_db_exception.raise_null_query()

            object_hiveclient.invoke_shell()

            if str_server_connect is not None:
                object_hiveclient.exec_command(str_server_connect)
            if bool_include_header:
                object_hiveclient.exec_command("set hive.cli.print.header=true;")

            stdin, stdout, stderr = object_hiveclient.exec_command("hive -e '" + p_query + "'")
            df = pd.read_csv(stdout, sep="\t", header=None)
            rs = self.dataframe_to_resultset(df)
            if str_return_type == "list":
                rs = self.resultset_to_list(rs)
            return rs
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def execute_query_from_file(self, object_connection, pstr_filepath):
        """
        Description:
            |  This method allows user to execute a query available in a file.

        :param object_connection:
        :type object_connection: Database Connection Object
        :param pstr_filepath:
        :type pstr_filepath: String
        :type str_return_type: String


        :return: ResultSet

        .. notes::
            |  This method returns a list or a resultset based on the parameter str_return_type. 'select' statements will returns List/Resultset and other type of statements will return Boolean.
            |
            |  This method accepts only text/sql files.


        """
        try:
            if pstr_filepath is None:
                self.__obj_db_exception.raise_null_filepath()

            str_filepath = pstr_filepath.strip()
            if object_connection is None:
                self.__obj_db_exception.raise_null_database_object()

            if str_filepath.endswith((".sql", ".txt")):
                query = ""
                with open(str_filepath, "r") as f:
                    for line in f:
                        query = query + " " + line
                resultset = self.execute_statement(
                    object_connection, query, str_return_type="resultset"
                )  # object_connection.cursor().execute(query)
                return resultset
            else:
                raise Exception("Accepted file formats are .sql and .txt")

        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def close(self, object_connection):
        """
        Description:
            |  This method closes the database connection.

        :param object_connection:
        :type object_connection: Database Connection Object

        """
        try:
            if object_connection is None:
                self.__obj_db_exception.raise_null_database_object()

            if "cassandra" in repr(object_connection):
                object_connection.cluster.shutdown()
            elif "paramiko" in repr(object_connection):
                object_connection.close()
            elif any(
                s in repr(object_connection.dialect) for s in ("mssql","mysql", "postgres", "oracle")
            ):
                object_connection.close()
            self.logger_obj.warning("The connection " + repr(object_connection) + "is closed")
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def check_table_exists(self, object_connection, str_database_name, str_table_name, **kwargs):
        """
        Description:
            |  This method check if a table exists in a database.

        :param object_connection:
        :type object_connection: Database Connection Object
        :param str_database_name:
        :type str_database_name: String
        :param str_table_name:
        :type str_table_name: String


        :return: Boolean

        .. warning::
            |  The method does not support HIVE right now.

        """
        try:
            if object_connection is None:
                self.__obj_db_exception.raise_null_database_object()

            if str_database_name is None:
                self.__obj_db_exception.raise_null_database_name()

            if str_table_name is None:
                self.__obj_db_exception.raise_null_table_name()

            str_schema = kwargs.get("pstr_schema", None)
            bln_is_table_exists = False

            if "cassandra" in repr(object_connection):
                temp_engine = object_connection.cluster.connect(str_database_name)
                rs = self.execute_statement(
                    temp_engine,
                    "SELECT table_name FROM system_schema.tables WHERE keyspace_name='"
                    + str_database_name
                    + "' and table_name='"
                    + str_table_name
                    + "';",
                )
                if len(rs) > 1:
                    bln_is_table_exists = True
                else:
                    bln_is_table_exists = False

            elif any(s in repr(object_connection.dialect) for s in ("mssql", "postgres")):
                object_connection.engine.url.database = str_database_name
                temp_engine = sc.create_engine(object_connection.engine.url)
                if str_schema is None:
                    bln_is_table_exists = temp_engine.dialect.has_table(
                        temp_engine, str_table_name
                    )
                else:
                    bln_is_table_exists = temp_engine.dialect.has_table(
                        temp_engine, str_table_name, schema=str_schema
                    )

            elif any(s in repr(object_connection.dialect) for s in ("oracle")):
                bln_is_table_exists = object_connection.dialect.has_table(
                    object_connection, str_table_name, schema=str_database_name
                )

            return bln_is_table_exists

        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    ## This section deals with dataframe/resultset/list

    def cassandra_resultset_to_list(self, prs_cassandra_resultset):
        """
        Description:
            |  This method returns the headers and all the row values in a cassandra-driver resultset.

        :param prs_cassandra_resultset: This is a cassandra-driver resultset
        :type prs_cassandra_resultset: Cassandra Resultset Object


        :return: List

        .. notes::
            |  First index of the list will contain the column headers and the rest will have row values.


        .. warning::
            |  Only pass cassandra-driver resultset object to this method.

        """
        try:
            if prs_cassandra_resultset is None:
                self.__obj_db_exception.raise_null_resultset()

            list_rs_column_names = prs_cassandra_resultset.column_names
            list_rs_values = []
            list_rs_values.append(list_rs_column_names)
            for row in prs_cassandra_resultset:
                list_rs_values.append([val for val in row])
            return list_rs_values
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def is_rowcount_zero(self, plist_resultlist):
        """
        Description:
            |  This method checks if the row count is zero or not.

        :param plist_resultlist: This is a List that contains column headers and row values
        :type plist_resultlist: List


        :return: Boolean

        """
        try:
            if plist_resultlist is None:
                self.__obj_db_exception.raise_null_resultlist()

            bln_is_rowcount_zero = False
            int_rowcount = self.get_rowcount(plist_resultlist) - 1
            if int_rowcount <= 0:
                bln_is_rowcount_zero = True
            else:
                bln_is_rowcount_zero = False

            return bln_is_rowcount_zero
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def get_rowcount(self, plist_resultlist):
        """
        Description:
            |  This method returns the count of rows in a result list.

        :param plist_resultlist: This is a List that contains column headers and row values
        :type plist_resultlist: List


        :return: Integer

        """
        try:
            if plist_resultlist is None:
                self.__obj_db_exception.raise_null_resultlist()
            int_length = len(plist_resultlist)
            return int_length
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def get_headers(self, plist_resultlist):
        """
        Description:
            |  This method returns list of headers in a result list.

        :param plist_resultlist:
        :type plist_resultlist: List


        :return: List

        """
        try:
            if plist_resultlist is None:
                self.__obj_db_exception.raise_null_resultlist()
            lst_headers = plist_resultlist[0]
            return lst_headers
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def resultset_to_list(self, prs_resultset, pbool_include_headers=True):
        """
        Description:
            |  This method converts a ResultSet into a List.

        :param prs_resultset:
        :type prs_resultset: ResultSet
        :param pbool_include_headers:
        :type pbool_include_headers: Boolean


        :return: List

        .. notes::
            |  If pbool_include_headers=True, the return list will contain the headers in the first index.
            |  If pbool_include_headers=False, the return list will contain only the row values.


        """
        try:
            if prs_resultset is None:
                self.__obj_db_exception.raise_null_resultset()

            list_resultset_data = []
            if pbool_include_headers == True:
                lst_resultset_description = prs_resultset.cursor.description
                lst_headers = [column[0] for column in lst_resultset_description]
                list_resultset_data.append(lst_headers)
            list_resultset = prs_resultset.fetchall()
            for val in list_resultset:
                list_resultset_data.append(list(val))
            return list_resultset_data
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def decode_password(self, pkey, psecret_key):
        try:
            cipher = AES.new(psecret_key.encode("utf8"), AES.MODE_ECB)
            decoded = cipher.decrypt(base64.b64decode(pkey))
            password = (decoded.decode()).strip()
            return password
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def check_value_exists_in_column(self, plist_resultlist, pstr_column_header, pstr_value):
        """
        Description:
            |  This method returns True if a value exists under a column header, otherwise returns False.

        :param plist_resultlist:
        :type plist_resultlist: Result List
        :param pstr_column_header:
        :type pstr_header: String
        :param pstr_value:
        :type pstr_value: String


        :return: Boolean

        """
        try:
            if plist_resultlist is None:
                self.__obj_db_exception.raise_null_resultlist()

            if pstr_column_header is None:
                self.__obj_db_exception.raise_null_column_header()

            list_coldata = self.get_column_data(plist_resultlist, pstr_column_header)
            if pstr_value in list_coldata:
                return True
            else:
                return False
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def check_value_not_exists_in_column(self, plist_resultlist, pstr_column_header, pstr_value):
        """
        Description:
            |  This method returns True if a value does not exists under a column header, otherwise returns False.

        :param plist_resultlist:
        :type plist_resultlist: Result List
        :param pstr_column_header:
        :type pstr_header: String
        :param pstr_value:
        :type pstr_value: String


        :return: Boolean

        """
        try:
            if plist_resultlist is None:
                self.__obj_db_exception.raise_null_resultlist()
            if pstr_column_header is None:
                self.__obj_db_exception.raise_null_column_header()

            list_coldata = self.get_column_data(plist_resultlist, pstr_column_header)
            if pstr_value in list_coldata:
                return False
            else:
                return True
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def get_column_data(self, plist_resultlist, pstr_column_header):
        """
        Description:
            |  This method returns all the values in a column header.

        :param plist_resultlist:
        :type plist_resultlist: Result List
        :param pstr_column_header:
        :type pstr_column_header: String


        :return: List

        """
        try:
            if plist_resultlist is None:
                self.__obj_db_exception.raise_null_resultlist()
            if pstr_column_header is None:
                self.__obj_db_exception.raise_null_column_header()

            list_resultset_data = plist_resultlist
            int_resultset_length = len(list_resultset_data)
            pdf_resultset_dataframe = pd.DataFrame(
                list_resultset_data[1:int_resultset_length], columns=list_resultset_data[0]
            )
            list_coldata = pdf_resultset_dataframe[pstr_column_header].values
            return list_coldata
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def compare_resultlists(
        self,
        plist_resultlist_source,
        plist_resultlist_target,
        pstr_compare_mode="index",
        **kwargs,
    ):
        """
        Description:
            |  This method lets user compare two result lists and returns the difference in the form of a Dataframe.

        :param plist_resultlist_source:
        :type plist_resultlist_source: Result List
        :param plist_resultlist_target:
        :type plist_resultlist_target: Result List
        :param pstr_compare_mode: index/header
        :type pstr_compare_mode: String
        :param plist_headers: List of Headers to compare
        :type plist_headers: kwargs
        :param plist_headers_source: List of Source Headers to compare
        :type plist_headers_source: kwargs
        :param plist_headers_target: List of Source Headers to compare
        :type plist_headers_target: kwargs
        :param pint_rowcount: Number of rows to compare
        :type pint_rowcount: kwargs
        :param pbool_ignore_datatype:
        :type pbool_ignore_datatype: kwargs
        :param pbool_line_to_line: default value is False
        :type pbool_line_to_line: kwargs
        :param pbool_get_common: default value is False
        :type pbool_get_common: kwargs
        :param pbool_ignore_header_case: default value is False
        :type pbool_ignore_header_case: kwargs
        :param pbool_club: default value is False
        :type pbool_ignore_header_case: kwargs
        :param pdict_primary_keys: Dictionary in the format of {'source':[],'target':[]}
        :type pbool_ignore_header_case: kwargs


        :return: When pbool_line_to_line=False, returns two Dataframes, one contains (source - target) and the other contains (target - source)
                 When pbool_line_to_line=False and pbool_get_common=True, returns three Dataframes, first one is common data, second one contains (source - target) and the other contains (target - source)
                 When pbool_line_to_line=True, returns one Dataframe containing (source - target)

        Examples:
            |  1. Let us imagine we have 2 result sets rs_source=3 headers and rs_target=3 headers then usage would be
            |  compare_resultsets(rs_source, rs_target) or compare_resultsets(rs_source, rs_target, pstr_compare_mode='index')
            |  This will only work when both result sets have same no. of headers, otherwise an exception will be thrown.
            |  2. Let us imagine we have 2 result sets with headers as following rs_source=['id', 'name', 'age'] and (rs_target=['id', 'name', 'age'] or rs_target=['age', 'name', 'id'])
            |  compare_resultsets(rs_source, rs_target, pstr_compare_mode='header')
            |  This will only work when both result sets have same no. of headers, otherwise an exception will be thrown.
            |  3. Let us imagine we have 2 result sets with headers as following rs_source=['id', 'name', 'age', 'location', 'country'] and rs_target=['id', 'name', 'age']
            |  compare_resultsets(rs_source, rs_target, pstr_compare_mode='header', plist_headers=['id', 'name', 'age'])
            |  4. Let us imagine we have 2 result sets with headers as following rs_source=['id_source', 'name_source', 'age_source', 'location_source', 'country_source'] and rs_target=['id_target', 'name_target', 'age_target']
            |  compare_resultsets(rs_source, rs_target, pstr_compare_mode='header', plist_headers_source=['id_source', 'name_source', 'age_source'], plist_headers_target=['id_target', 'name_target', 'age_target'])
            |  In this case, id_source will be compared with id_target and so on.
            |  Make sure that plist_headers_source and plist_headers_target are used together, otherwise an exception will be thrown.
            |  Sizes of both the lists plist_headers_source and plist_headers_target must be same.
            |  5. Let us imagine the requirement is to compare only top few records from both result sets then use the **kwargs parameter pint_rowcount
            |  compare_resultsets(rs_source, rs_target, pint_rowcount=10)
            |  6. If user wants to perform row-to-row comparison of same sized(same no. of rows) data, then
            |  compare_resultlists(resultset1, resultset2, pint_row_count=10, pbool_line_to_line=True, pstr_compare_mode='header')
            |  7. If the user wants to fetch common data in both resultlists along with (source-target and target_source), then
            |  compare_resultlists(resultset1, resultset2, pstr_compare_mode='header', pbool_get_common=True)
            |  8. If the user wants to get only a single difference for source_target and target_source then the statment would be like
            |  difference_dataframe = obj.compare_resultlists(resultset1, resultset2,pbool_ignore_datatype=True,pstr_compare_mode="header",plist_headers_source=['TCExecuted','TEexecutiontime'],plist_headers_target=['TCExecutedold','TEexecutiontime'],pbool_club=True,pdict_primary_keys=data)



        .. notes::
            |  If there is no difference, then None will be returned.
            |  The source and target row count should be same
            |  The pbool_club is only applicable if the user performs the comparison with pstr_comparison_mode ='header' and pbool_line_to_line = False


        """
        try:
            plist_headers = kwargs.get("plist_headers", None)
            plist_headers_source = kwargs.get("plist_headers_source", None)
            plist_headers_target = kwargs.get("plist_headers_target", None)
            pint_row_count = kwargs.get("pint_row_count", None)
            bool_ignore_datatype = kwargs.get("pbool_ignore_datatype", True)
            line_to_line = kwargs.get("pbool_line_to_line", False)
            pbool_get_common = kwargs.get("pbool_get_common", False)
            pbool_ignore_header_case = kwargs.get("pbool_ignore_header_case", False)
            bool_club = kwargs.get("pbool_club", False)
            dict_primary_keys = kwargs.get("pdict_primary_keys", None)
            df_difference_dataframe = None

            if plist_resultlist_source is None or plist_resultlist_target is None:
                raise Exception(
                    "Method compare_resultlists : One or both of the result data is None"
                )

            if pint_row_count is not None and pint_row_count < 1:
                raise Exception(
                    "Method compare_resultlists : Given row count should be greater than 0 "
                )

            if line_to_line == True and pint_row_count is None:
                if len(plist_resultlist_source) != len(plist_resultlist_target):
                    raise Exception(
                        "Method compare_resultlists : line to line comparison is accepted only if the length of the source and target is same. If needed you can specify the kwarg that is rowcount"
                    )

            if pstr_compare_mode == "index":
                df_dataframe_source = pd.DataFrame(
                    plist_resultlist_source[1 : len(plist_resultlist_source)]
                )
                df_dataframe_target = pd.DataFrame(
                    plist_resultlist_target[1 : len(plist_resultlist_target)]
                )

                if len(plist_resultlist_source[0]) != len(plist_resultlist_target[0]):
                    raise Exception(
                        "The source and target header count is different, please make sure that the count is same"
                    )

                if line_to_line == True:
                    df_difference_dataframe = self.data_frame_diff(
                        df_dataframe_source,
                        df_dataframe_target,
                        pint_rowcount=pint_row_count,
                        pbool_ignore_datatype=bool_ignore_datatype,
                    )

                    if df_difference_dataframe is not None and not df_difference_dataframe.empty:
                        df_difference_dataframe.unstack()

                    return df_difference_dataframe

                else:
                    if pbool_get_common is True:
                        common, df_source_differences, df_target_differences = (
                            self.compare_dataframes_distinct(
                                df_dataframe_source,
                                df_dataframe_target,
                                pint_rowcount=pint_row_count,
                                pbool_get_common=pbool_get_common,
                                pbool_ignore_datatype=bool_ignore_datatype,
                            )
                        )
                        return common, df_source_differences, df_target_differences
                    else:
                        df_source_differences, df_target_differences = (
                            self.compare_dataframes_distinct(
                                df_dataframe_source,
                                df_dataframe_target,
                                pint_rowcount=pint_row_count,
                                pbool_get_common=pbool_get_common,
                                pbool_ignore_datatype=bool_ignore_datatype,
                            )
                        )
                        return df_source_differences, df_target_differences

            elif pstr_compare_mode == "header":
                list_source = plist_resultlist_source
                list_target = plist_resultlist_target

                if pbool_ignore_header_case is True:
                    source_headers_temp = [val.lower() for val in list_source[0]]
                    target_headers_temp = [val.lower() for val in list_target[0]]
                    if plist_headers is not None:
                        plist_headers = [valc.lower() for valc in plist_headers]
                    if plist_headers_source is not None and plist_headers_target is not None:
                        plist_headers_source = [vals.lower() for vals in plist_headers_source]
                        plist_headers_target = [valt.lower() for valt in plist_headers_target]
                else:
                    source_headers_temp = list_source[0]
                    target_headers_temp = list_target[0]

                df_dataframe_source = pd.DataFrame(
                    list_source[1 : len(list_source)], columns=source_headers_temp
                )
                df_dataframe_target = pd.DataFrame(
                    list_target[1 : len(list_target)], columns=target_headers_temp
                )

                if (
                    (plist_headers_source is None)
                    and (plist_headers_target is None)
                    and (plist_headers is None)
                ):
                    if len(plist_resultlist_source[0]) != len(plist_resultlist_target[0]):
                        raise Exception(
                            "The source and target header count is different, please make sure that the count is same"
                        )
                    list_source[0].sort()
                    list_target[0].sort()
                    plist_headers_source = source_headers_temp
                    plist_headers_target = target_headers_temp
                    if plist_headers_source != plist_headers_target:
                        raise Exception(
                            "The headers in the source and target results are different"
                        )

                if line_to_line == True:
                    df_difference_dataframe = self.data_frame_diff(
                        df_dataframe_source,
                        df_dataframe_target,
                        plist_headers=plist_headers,
                        plist_headers_source=plist_headers_source,
                        plist_headers_target=plist_headers_target,
                        pint_rowcount=pint_row_count,
                        pbool_ignore_datatype=bool_ignore_datatype,
                    )

                    if df_difference_dataframe is not None and not df_difference_dataframe.empty:
                        df_difference_dataframe.unstack()

                    return df_difference_dataframe
                else:
                    # added the distinct method call statement
                    if pbool_get_common is True:
                        if bool_club:
                            df_common_dataframe, df_dataframe_formatted = (
                                self.compare_dataframes_distinct(
                                    df_dataframe_source,
                                    df_dataframe_target,
                                    plist_headers=plist_headers,
                                    plist_headers_source=plist_headers_source,
                                    plist_headers_target=plist_headers_target,
                                    pint_rowcount=pint_row_count,
                                    pbool_get_common=pbool_get_common,
                                    pbool_ignore_datatype=bool_ignore_datatype,
                                    pbool_club=bool_club,
                                    pdict_primary_keys=dict_primary_keys,
                                )
                            )
                            return df_common_dataframe, df_dataframe_formatted
                        else:
                            (
                                df_common_dataframe,
                                df_source_differences,
                                df_target_differences,
                            ) = self.compare_dataframes_distinct(
                                df_dataframe_source,
                                df_dataframe_target,
                                plist_headers=plist_headers,
                                plist_headers_source=plist_headers_source,
                                plist_headers_target=plist_headers_target,
                                pint_rowcount=pint_row_count,
                                pbool_get_common=pbool_get_common,
                                pbool_ignore_datatype=bool_ignore_datatype,
                                pbool_club=bool_club,
                                pdict_primary_keys=dict_primary_keys,
                            )
                            return (
                                df_common_dataframe,
                                df_source_differences,
                                df_target_differences,
                            )
                    else:
                        if bool_club:
                            df_differences = self.compare_dataframes_distinct(
                                df_dataframe_source,
                                df_dataframe_target,
                                plist_headers=plist_headers,
                                plist_headers_source=plist_headers_source,
                                plist_headers_target=plist_headers_target,
                                pint_rowcount=pint_row_count,
                                pbool_get_common=pbool_get_common,
                                pbool_ignore_datatype=bool_ignore_datatype,
                                pbool_club=bool_club,
                                pdict_primary_keys=dict_primary_keys,
                            )
                            return df_differences
                        else:
                            df_source_differences, df_target_differences = (
                                self.compare_dataframes_distinct(
                                    df_dataframe_source,
                                    df_dataframe_target,
                                    plist_headers=plist_headers,
                                    plist_headers_source=plist_headers_source,
                                    plist_headers_target=plist_headers_target,
                                    pint_rowcount=pint_row_count,
                                    pbool_get_common=pbool_get_common,
                                    pbool_ignore_datatype=bool_ignore_datatype,
                                    pbool_club=bool_club,
                                    pdict_primary_keys=dict_primary_keys,
                                )
                            )
                            return df_source_differences, df_target_differences
            else:
                raise Exception("Given compare mode is invalid, please select index or header")
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def data_frame_diff(self, pdf_dataframe_source, pdf_dataframe_destinition, **kwargs):
        """
        Description:
            |  This method lets user compare two Dataframes and returns the difference in the form of a Dataframe.

        :param pdf_dataframe_source:
        :type pdf_dataframe_source: pandas Dataframe
        :param pdf_dataframe_destinition:
        :type pdf_dataframe_destinition: pandas Dataframe
        :param plist_headers:
        :type plist_headers: kwargs
        :param plist_headers_source:
        :type plist_headers_source: kwargs
        :param plist_headers_target:
        :type plist_headers_target: kwargs
        :param pint_rowcount:
        :type pint_rowcount: kwargs


        :return: Dataframe

        .. notes::
            |  If there is no difference, then None will be returned.

        .. warning::
            |  DO NOT try to call this method directly, this is a helper method for compare_resultlists()

        """
        try:
            list_headers = kwargs.get("plist_headers", None)
            list_headers_source = kwargs.get("plist_headers_source", None)
            list_headers_target = kwargs.get("plist_headers_target", None)
            int_rowcount = kwargs.get("pint_rowcount", None)
            bool_ignore_datatype = kwargs.get("pbool_ignore_datatype", None)
            df_stacked_dataframe = None
            if list_headers is None and list_headers_source is None and list_headers_target is None:

                if bool_ignore_datatype == True:
                    source_types = list(pdf_dataframe_source.dtypes)
                    target_types = list(pdf_dataframe_destinition.dtypes)
                    series_common_type = self.__datatype_conversion(source_types, target_types)
                    for i in range(0, len(series_common_type)):
                        pdf_dataframe_source[i] = pdf_dataframe_source[i].astype(
                            series_common_type[i]
                        )
                        pdf_dataframe_destinition[i] = pdf_dataframe_destinition[i].astype(
                            series_common_type[i]
                        )

                if int_rowcount != None and int_rowcount > 0:
                    bool_differences = (
                        pdf_dataframe_source.head(int_rowcount)
                        != pdf_dataframe_destinition.head(int_rowcount)
                    ).stack()
                    df_stacked_dataframe = pd.concat(
                        [
                            pdf_dataframe_source.head(int_rowcount).stack()[bool_differences],
                            pdf_dataframe_destinition.head(int_rowcount).stack()[bool_differences],
                        ],
                        axis=1,
                    )
                    df_stacked_dataframe.columns = ["Source_resultset", "Target_resultset"]

                else:
                    bool_differences = (pdf_dataframe_source != pdf_dataframe_destinition).stack()
                    df_stacked_dataframe = pd.concat(
                        [
                            pdf_dataframe_source.stack()[bool_differences],
                            pdf_dataframe_destinition.stack()[bool_differences],
                        ],
                        axis=1,
                    )
                    df_stacked_dataframe.columns = ["Source_resultset", "Target_resultset"]

            elif (
                list_headers is not None
                and list_headers_source is None
                and list_headers_target is None
            ):

                if bool_ignore_datatype == True:
                    source_types = list(pdf_dataframe_source[list_headers].dtypes)
                    target_types = list(pdf_dataframe_destinition[list_headers].dtypes)
                    series_common_type = self.__datatype_conversion(source_types, target_types)
                    for i in range(0, len(series_common_type)):
                        pdf_dataframe_source[list_headers[i]] = pdf_dataframe_source[
                            list_headers[i]
                        ].astype(series_common_type[i])
                        pdf_dataframe_destinition[list_headers[i]] = pdf_dataframe_destinition[
                            list_headers[i]
                        ].astype(series_common_type[i])

                if int_rowcount != None and int_rowcount > 0:
                    bool_differences = (
                        pdf_dataframe_source[list_headers].head(int_rowcount)
                        != pdf_dataframe_destinition[list_headers].head(int_rowcount)
                    ).stack()
                    df_stacked_dataframe = pd.concat(
                        [
                            pdf_dataframe_source[list_headers]
                            .head(int_rowcount)
                            .stack()[bool_differences],
                            pdf_dataframe_destinition[list_headers]
                            .head(int_rowcount)
                            .stack()[bool_differences],
                        ],
                        axis=1,
                    )
                    df_stacked_dataframe.columns = ["Source_resultset", "Target_resultset"]
                else:
                    bool_differences = (
                        pdf_dataframe_source[list_headers]
                        != pdf_dataframe_destinition[list_headers]
                    ).stack()
                    df_stacked_dataframe = pd.concat(
                        [
                            pdf_dataframe_source[list_headers].stack()[bool_differences],
                            pdf_dataframe_destinition[list_headers].stack()[bool_differences],
                        ],
                        axis=1,
                    )
                    df_stacked_dataframe.columns = ["Source_resultset", "Target_resultset"]

            elif (
                list_headers is None
                and list_headers_source is not None
                and list_headers_target is not None
            ):

                if bool_ignore_datatype == True:
                    source_types = list(pdf_dataframe_source[list_headers_source].dtypes)
                    target_types = list(pdf_dataframe_destinition[list_headers_target].dtypes)
                    series_common_type = self.__datatype_conversion(source_types, target_types)
                    for i in range(0, len(series_common_type)):
                        pdf_dataframe_source[list_headers_source[i]] = pdf_dataframe_source[
                            list_headers_source[i]
                        ].astype(series_common_type[i])
                        pdf_dataframe_destinition[list_headers_target[i]] = (
                            pdf_dataframe_destinition[list_headers_target[i]].astype(
                                series_common_type[i]
                            )
                        )

                if (len(list_headers_source) != 0) and (
                    len(list_headers_source) == len(list_headers_target)
                ):
                    if int_rowcount is not None and int_rowcount > 0:
                        list_difference = []
                        list_diff_headers = []
                        for i in range(0, len(list_headers_source)):
                            temp_diff = pdf_dataframe_source.head(int_rowcount).get(
                                list_headers_source[i]
                            ) != pdf_dataframe_destinition.head(int_rowcount).get(
                                list_headers_target[i]
                            )
                            list_difference.append(
                                pdf_dataframe_source[list_headers_source[i]].head(int_rowcount)[
                                    temp_diff
                                ]
                            )
                            list_difference.append(
                                pdf_dataframe_destinition[list_headers_target[i]].head(
                                    int_rowcount
                                )[temp_diff]
                            )
                            list_diff_headers.append(
                                "source_resultset/" + str(list_headers_source[i])
                            )
                            list_diff_headers.append(
                                "target_resultset/" + str(list_headers_target[i])
                            )
                        # df_stacked_dataframe = pd.DataFrame(list_difference,index= list_diff_headers).transpose()

                        df_stacked_dataframe = (
                            pd.DataFrame(list_difference, index=list_diff_headers)
                            .transpose()
                            .dropna(how="all")
                        )
                        if df_stacked_dataframe is not None:
                            df_stacked_dataframe.stack()

                    else:
                        list_difference = []
                        list_diff_headers = []
                        for i in range(0, len(list_headers_source)):
                            temp_diff = pdf_dataframe_source.get(
                                list_headers_source[i]
                            ) != pdf_dataframe_destinition.get(list_headers_target[i])
                            source_series = pdf_dataframe_source[list_headers_source[i]][temp_diff]
                            target_series = pdf_dataframe_destinition[list_headers_target[i]][
                                temp_diff
                            ]
                            if not source_series.empty and not target_series.empty:
                                list_difference.append(source_series)
                                list_difference.append(target_series)
                                list_diff_headers.append(
                                    "source_resultset_" + str(list_headers_source[i])
                                )
                                list_diff_headers.append(
                                    "target_resultset_" + str(list_headers_target[i])
                                )
                        # df_stacked_dataframe = pd.DataFrame(list_difference,index= list_diff_headers).transpose()
                        df_stacked_dataframe = (
                            pd.DataFrame(list_difference, index=list_diff_headers)
                            .transpose()
                            .dropna(how="all")
                        )
                        if df_stacked_dataframe is not None and not df_stacked_dataframe.empty:
                            df_stacked_dataframe.stack()
            else:
                raise Exception("Looks like there is a conflict in the kwargs parameters")

            return df_stacked_dataframe
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def dataframe_to_resultset(self, pdf_dataframe):
        """
        Description:
            |  This method converts a dataframe object to resultset object.

        :param pdf_dataframe:
        :type pdf_dataframe: Dataframe


        :return: ResultSet

        """
        try:
            if pdf_dataframe is None:
                self.__obj_db_exception.raise_null_dataframe()

            engine = create_engine("sqlite://", echo=False)
            # added the ignore index
            pdf_dataframe.to_sql("temp", con=engine, index=False)
            rs = engine.execute("SELECT * FROM temp")
            return rs
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def file_to_resultlist(self, pstr_filepath, pstr_filetype="csv", **kwargs):
        """
        Description:
            |  This method converts data in a csv/excel file into a Result List.

        :param pstr_filepath:
        :type pstr_filepath: String
        :param pstr_filetype:
        :type pstr_filetype: String
        :param pstr_column_separator:
        :type pstr_column_separator: kwargs
        :param pstr_row_separator:
        :type pstr_row_separator: kwargs
        :param pint_skiprows:
        :type pint_skiprows: kwargs
        :param pstr_quotechar:
        :type pstr_quotechar: kwargs
        :param pstr_encoding:
        :type pstr_encoding: kwargs
        :param pstr_sheetname:
        :type pstr_sheetname: kwargs
        :param plist_headers:
        :type plist_headers: kwargs
        :param pint_read_rows_count:
        :type pint_read_rows_count: kwargs


        :return: Result List

        Examples:
            |  file_to_resultset(path,pstr_filetype='csv')
            |  file_to_resultset(path,pstr_filetype='csv',pint_read_rows_count=5)
            |  file_to_resultset(path,pstr_filetype='csv',pint_read_rows_count=5,plist_headers=['first','second', 'third'])
            |  file_to_resultset(path,pstr_filetype='csv',pint_skiprows=100)
            |  obj.file_to_resultsetlist(path,pstr_filetype='excel')


        .. notes::
            |  Only csv and excel files are supported.


        """
        try:
            if pstr_filepath is None:
                self.__obj_db_exception.raise_null_filepath()

            # for csv
            str_column_separator = kwargs.get("pstr_column_separator", None)
            # str_row_separator = kwargs.get('pstr_row_separator',',')
            int_skiprows = kwargs.get("pint_skiprows", None)
            str_quotechar = kwargs.get("pstr_quotechar", '"')
            list_headers = kwargs.get("plist_headers", None)
            int_total_rows_to_read = kwargs.get("pint_read_rows_count", None)
            int_header_row = kwargs.get("pint_header_row", 0)
            # for excel
            str_sheetname = kwargs.get("pstr_sheetname", 0)
            # for both
            str_encoding = kwargs.get("pstr_encoding", None)
            rs_resultset = None
            df_csv_dataframe = None
            if list_headers is not None:
                int_header_row = None

            if pstr_filetype == "csv":
                df_csv_dataframe = pd.read_csv(
                    filepath_or_buffer=pstr_filepath,
                    sep=str_column_separator,
                    skiprows=int_skiprows,
                    nrows=int_total_rows_to_read,
                    encoding=str_encoding,
                    quotechar=str_quotechar,
                    engine="python",
                    header=int_header_row,
                )
            elif pstr_filetype == "excel":
                df_csv_dataframe = pd.read_excel(
                    pstr_filepath,
                    sheet_name=str_sheetname,
                    skiprows=int_skiprows,
                    names=list_headers,
                    header=int_header_row,
                    nrows=int_total_rows_to_read,
                    engine="xlrd",
                )
            elif pstr_filetype == "json":
                df_csv_dataframe = pd.read_json(path_or_buf=pstr_filepath)
            rs_resultset = self.dataframe_to_resultset(df_csv_dataframe)
            list_resultset = self.resultset_to_list(rs_resultset)
            return list_resultset
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def resultlist_to_csv(self, plist_resultlist, pstr_filepath):
        """
        Description:
            |  This method writes Result List to a csv file.

        :param plist_resultlist:
        :type plist_resultlist: Result List
        :param pstr_filepath:
        :type pstr_filepath: String


        :return: CSV File

        .. notes::
            |  Make sure to pass pstr_filepath with filename and extension as csv.


        """
        try:
            if plist_resultlist is None:
                self.__obj_db_exception.raise_null_resultlist()
            if pstr_filepath is None:
                self.__obj_db_exception.raise_null_filepath()

            list_resultset = plist_resultlist
            df_resultset = pd.DataFrame(
                list_resultset[1 : len(list_resultset)], columns=list_resultset[0]
            )
            df_resultset.to_csv(pstr_filepath, index=False)
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def dataframe_to_csv(self, pdf_dataframe, pstr_path):
        """
        Description:
            |  This method writes Dataframe to a csv file.

        :param pdf_dataframe:
        :type pdf_dataframe: Dataframe
        :param pstr_filepath:
        :type pstr_filepath: String


        :return: CSV File

        .. notes::
            |  Make sure to pass pstr_filepath with filename and extension as csv.


        """
        try:
            if pdf_dataframe is None:
                self.__obj_db_exception.raise_null_dataframe()
            if pstr_path is None:
                self.__obj_db_exception.raise_null_filepath()
            pdf_dataframe.to_csv(pstr_path)
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def list_to_dataframe(self, plist_data):
        """
        Description:
            |  This method is for converting the list to dataframes
        :param plist_data:
        :type plist_data: list
        :return:  Dataframe

        .. warning::
            |  The list which we should pass must be the output of the execute_statement with list as return data


        """
        try:
            return pd.DataFrame(plist_data[1 : len(plist_data)], columns=plist_data[0])
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def compare_dataframes_distinct(self, pdf_dataframe_source, pdf_dataframe_target, **kwargs):
        """
        .. warning::
            |  DO NOT try to call this method directly, this is a helper method for compare_resultlists()

        """
        try:
            list_headers = kwargs.get("plist_headers", None)
            list_headers_source = kwargs.get("plist_headers_source", None)
            list_headers_target = kwargs.get("plist_headers_target", None)
            int_rowcount = kwargs.get("pint_rowcount", None)
            pstr_compare_mode = kwargs.get("pstr_compare_mode", "header")
            pbool_get_common = kwargs.get("pbool_get_common", False)
            bool_ignore_datatype = kwargs.get("pbool_ignore_datatype", None)
            bool_club = kwargs.get("pbool_club", False)
            dict_primary_keys = kwargs.get("pdict_primary_keys", None)
            if pstr_compare_mode == "header":
                list_source_headers = pdf_dataframe_source.columns

            if int_rowcount is not None:
                df_dataframe_source = pdf_dataframe_source.head(int_rowcount)
                df_dataframe_target = pdf_dataframe_target.head(int_rowcount)
            else:
                df_dataframe_source = pdf_dataframe_source
                df_dataframe_target = pdf_dataframe_target

            df_filtered_source = None
            df_filtered_target = None
            df_dup2_source = None
            df_dup2_target = None
            if list_headers is None and list_headers_source is None and list_headers_target is None:

                if bool_ignore_datatype == True:
                    source_types = list(df_dataframe_source.dtypes)
                    target_types = list(df_dataframe_target.dtypes)
                    series_common_type = self.__datatype_conversion(source_types, target_types)
                    for i in range(0, len(series_common_type)):
                        df_dataframe_source[i] = df_dataframe_source[i].astype(
                            series_common_type[i]
                        )
                        df_dataframe_target[i] = df_dataframe_target[i].astype(
                            series_common_type[i]
                        )

                df_dup_source = df_dataframe_source.copy()
                df_dup_target = df_dataframe_target.copy()
                df_dup2_source = df_dup_source.copy()
                df_dup2_target = df_dup_target.copy()
                if pstr_compare_mode == "header":
                    df_dup2_source.set_axis(list_source_headers, axis=1, inplace=True)
                    df_dup2_target.set_axis(list_source_headers, axis=1, inplace=True)

            elif (
                list_headers is not None
                and list_headers_source is None
                and list_headers_target is None
            ):

                if bool_ignore_datatype == True:
                    source_types = list(df_dataframe_source[list_headers].dtypes)
                    target_types = list(df_dataframe_target[list_headers].dtypes)
                    series_common_type = self.__datatype_conversion(source_types, target_types)
                    for i in range(0, len(series_common_type)):
                        df_dataframe_source[list_headers[i]] = df_dataframe_source[
                            list_headers[i]
                        ].astype(series_common_type[i])
                        df_dataframe_target[list_headers[i]] = df_dataframe_target[
                            list_headers[i]
                        ].astype(series_common_type[i])

                df_dup_source = df_dataframe_source[list_headers].copy()
                df_dup_target = df_dataframe_target[list_headers].copy()
                df_dup2_source = df_dup_source.copy()
                df_dup2_target = df_dup_target.copy()

            elif (
                list_headers is None
                and list_headers_source is not None
                and list_headers_target is not None
            ):
                if bool_ignore_datatype == True:
                    source_types = list(df_dataframe_source[list_headers_source].dtypes)
                    target_types = list(df_dataframe_target[list_headers_target].dtypes)
                    series_common_type = self.__datatype_conversion(source_types, target_types)
                    for i in range(0, len(series_common_type)):
                        df_dataframe_source[list_headers_source[i]] = df_dataframe_source[
                            list_headers_source[i]
                        ].astype(series_common_type[i])
                        df_dataframe_target[list_headers_target[i]] = df_dataframe_target[
                            list_headers_target[i]
                        ].astype(series_common_type[i])

                if (len(list_headers_source) != 0) and (
                    len(list_headers_source) == len(list_headers_target)
                ):
                    df_dup_source = df_dataframe_source[list_headers_source].copy()
                    df_dup_target = df_dataframe_target[list_headers_target].copy()
                    df_dup2_source = df_dup_source.copy()
                    df_dup2_target = df_dup_target.copy()
                    df_dup2_source.set_axis(list_headers_source, axis=1, inplace=True)
                    df_dup2_target.set_axis(list_headers_source, axis=1, inplace=True)
                else:
                    raise Exception(
                        "The count of source header and target header list is not equal"
                    )
            else:
                raise Exception(
                    "Looks like there is a conflict in the given kwargs parameters, please check them"
                )

            if df_dup2_source is not None and df_dup2_target is not None:
                df_dup2_source.drop_duplicates(keep="first", inplace=True)
                df_dup2_target.drop_duplicates(keep="first", inplace=True)
                diffs = pd.concat([df_dup2_source, df_dup2_target], sort=False).drop_duplicates(
                    keep=False
                )
                df_filtered_source_temp = pd.concat([diffs, df_dup2_source], sort=False)
                df_filtered_source = df_filtered_source_temp[df_filtered_source_temp.duplicated()]
                df_filtered_target_temp = pd.concat([diffs, df_dup2_target], sort=False)
                df_filtered_target = df_filtered_target_temp[df_filtered_target_temp.duplicated()]
                if (
                    pstr_compare_mode == "header"
                    and list_headers_source is not None
                    and list_headers_target is not None
                ):
                    df_filtered_target.set_axis(list_headers_target, axis=1, inplace=True)
                if bool_club:
                    if dict_primary_keys is None:
                        raise Exception(
                            "When bool_club specified , please specify the headers also"
                        )
                    df_clubbed = self.__difference_formatter(
                        df_filtered_source,
                        df_filtered_target,
                        plist_source_headers=list_headers_source,
                        plist_target_headers=list_headers_target,
                        pdict_primary_keys=dict_primary_keys,
                    )
                if pbool_get_common is True:
                    if diffs.empty:
                        df_common = pd.concat(
                            [diffs, df_dup2_source, df_dup2_target], sort=False
                        ).drop_duplicates(keep="first")
                    else:
                        df_common = pd.concat(
                            [
                                diffs,
                                pd.concat([df_dup2_source, df_dup2_target]).drop_duplicates(
                                    keep="first"
                                ),
                            ]
                        ).drop_duplicates(keep=False)
                    if bool_club:
                        return df_common, df_clubbed
                    else:
                        return df_common, df_filtered_source, df_filtered_target
                else:
                    if bool_club:
                        return df_clubbed
                    else:
                        return df_filtered_source, df_filtered_target
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def __datatype_conversion(self, source_types, target_types):
        try:
            common_type = []
            for i in range(0, len(source_types)):
                if source_types[i].kind == "f" or target_types[i].kind == "f":
                    common_type.append(np.dtype("float64"))
                else:
                    common_type.append(np.dtype("O"))
            return pd.Series(common_type)
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def check_data_in_column(self, plist_resultlist, pdata_value, **kwargs):
        """
        Description:
            |  This method verifies if the value is present in the resultlist or not.
            |  It supports
            |      1. Check if value is available in a particular column
            |      2. Check if the value is present in multiple columns
            |      3. Check if the value is present in the resultlist irrespective of column name, just check if it exist or not
            |


        :param plist_resultlist:
        :type plist_resultlist: Result List
        :param pdata_column_header:
        :type pdata_column_header: Can be Int/String/Float/Datetime


        :return: bool/list of difference
        .. note::
                    |  Donot use this method directly into your code, please use the verify and assert method of assertion-datbase class


        """
        try:

            bool_ignore_case = kwargs.get("pbool_ignore_case", False)
            list_headers = kwargs.get("plist_headers", None)
            int_count = kwargs.get("pint_count", None)
            list_resultset_data = plist_resultlist
            int_resultset_length = len(list_resultset_data)
            if list_headers is not None:
                if len(list_headers) > 0:
                    df_resultset_dataframe = pd.DataFrame(
                        list_resultset_data[1:int_resultset_length],
                        columns=list_resultset_data[0],
                    )
                    columns = list_headers
                else:
                    raise Exception("The headers list should not be empty")
            else:
                df_resultset_dataframe = pd.DataFrame(list_resultset_data[1:int_resultset_length])
                columns = df_resultset_dataframe.columns

            if int_count is None:
                if list_headers is None:
                    for cols in columns:
                        if df_resultset_dataframe[cols].dtype.kind == "f":
                            if float(pdata_value) in list(df_resultset_dataframe[cols]):
                                return True
                        if df_resultset_dataframe[cols].dtype.kind == "i":
                            if int(pdata_value) in list(df_resultset_dataframe[cols]):
                                return True
                        if df_resultset_dataframe[cols].dtype.kind == "O":
                            list_temp_col_data = [
                                val.strip() for val in list(df_resultset_dataframe[cols])
                            ]
                            if bool_ignore_case:
                                list_col_data = [val.lower() for val in list_temp_col_data]
                                if str(pdata_value.lower()) in list_col_data:
                                    return True
                            else:
                                if str(pdata_value) in list_temp_col_data:
                                    return True
                        if df_resultset_dataframe[cols].dtype.kind == "M":
                            if pd.to_datetime(pdata_value) in list(df_resultset_dataframe[cols]):
                                return True
                    return False
                else:
                    dict_individual_check = {}
                    list_unmatched_headers = {}
                    for cols in columns:
                        int_fetch_count = 0
                        if df_resultset_dataframe[cols].dtype.kind == "f":
                            int_fetch_count = (
                                list(df_resultset_dataframe[cols]).count(float(pdata_value))
                                + int_fetch_count
                            )
                        if df_resultset_dataframe[cols].dtype.kind == "i":
                            int_fetch_count = (
                                list(df_resultset_dataframe[cols]).count(int(pdata_value))
                                + int_fetch_count
                            )
                        if df_resultset_dataframe[cols].dtype.kind == "O":
                            list_temp_col_data = [
                                val.strip() for val in list(df_resultset_dataframe[cols])
                            ]
                            if bool_ignore_case:
                                list_col_data = [val.lower() for val in list_temp_col_data]
                                int_fetch_count = (
                                    list_col_data.count(str(pdata_value)) + int_fetch_count
                                )
                            else:
                                int_fetch_count = (
                                    list_temp_col_data.count(str(pdata_value)) + int_fetch_count
                                )
                        if df_resultset_dataframe[cols].dtype.kind == "M":
                            int_fetch_count = (
                                list(df_resultset_dataframe[cols]).count(
                                    pd.to_datetime(pdata_value)
                                )
                                + int_fetch_count
                            )
                        # dict_individual_check[cols] = int_fetch_count
                        if not int_fetch_count >= 1:
                            list_unmatched_headers[cols] = int_fetch_count

                    return list_unmatched_headers

            # code logic for count based comparison
            elif int_count > 0:
                if list_headers is not None:
                    # dict_individual_check = {}
                    list_unmatched_headers = {}
                    for cols in columns:
                        int_fetch_count = 0
                        if df_resultset_dataframe[cols].dtype.kind == "f":
                            int_fetch_count = (
                                list(df_resultset_dataframe[cols]).count(float(pdata_value))
                                + int_fetch_count
                            )
                        if df_resultset_dataframe[cols].dtype.kind == "i":
                            int_fetch_count = (
                                list(df_resultset_dataframe[cols]).count(int(pdata_value))
                                + int_fetch_count
                            )
                        if df_resultset_dataframe[cols].dtype.kind == "O":
                            list_temp_col_data = [
                                val.strip() for val in list(df_resultset_dataframe[cols])
                            ]
                            if bool_ignore_case:
                                list_col_data = [val.lower() for val in list_temp_col_data]
                                int_fetch_count = (
                                    list_col_data.count(str(pdata_value)) + int_fetch_count
                                )
                            else:
                                int_fetch_count = (
                                    list_temp_col_data.count(str(pdata_value)) + int_fetch_count
                                )
                        if df_resultset_dataframe[cols].dtype.kind == "M":
                            int_fetch_count = (
                                list(df_resultset_dataframe[cols]).count(
                                    pd.to_datetime(pdata_value)
                                )
                                + int_fetch_count
                            )
                        if not int_fetch_count == int_count:
                            list_unmatched_headers[cols] = int_fetch_count

                    if len(list_unmatched_headers) == 0:
                        return True
                    else:
                        return list_unmatched_headers

                else:
                    int_fetch_count = 0
                    for cols in columns:
                        if df_resultset_dataframe[cols].dtype.kind == "f":
                            int_fetch_count = (
                                list(df_resultset_dataframe[cols]).count(float(pdata_value))
                                + int_fetch_count
                            )
                        if df_resultset_dataframe[cols].dtype.kind == "i":
                            int_fetch_count = (
                                list(df_resultset_dataframe[cols]).count(int(pdata_value))
                                + int_fetch_count
                            )
                        if df_resultset_dataframe[cols].dtype.kind == "O":
                            list_temp_col_data = [
                                val.strip() for val in list(df_resultset_dataframe[cols])
                            ]
                            if bool_ignore_case:
                                list_col_data = [val.lower() for val in list_temp_col_data]
                                int_fetch_count = (
                                    list_col_data.count(str(pdata_value)) + int_fetch_count
                                )
                            else:
                                int_fetch_count = (
                                    list_temp_col_data.count(str(pdata_value)) + int_fetch_count
                                )

                        if df_resultset_dataframe[cols].dtype.kind == "M":
                            int_fetch_count = (
                                list(df_resultset_dataframe[cols]).count(
                                    pd.to_datetime(pdata_value)
                                )
                                + int_fetch_count
                            )

                    if int_fetch_count == int_count:
                        return True
                    else:
                        return False
            else:
                raise Exception("the pint_count if specified must have positive value")
        except Exception as e:
            raise e

    def check_headers_in_resultlist(self, plist_resultlist, plist_headers, **kwargs):
        """
        Description:
            |   This method is for verifying whether the headers are available in the resultlist or not
            |   The resultlist that will be passed in this method should be the one that is returned by the execute_statement method
        :param plist_resultlist: resultlist generated by execute_statement
        :param plist_headers:  list of headers to check if available or not
        :return: invalid match list

        .. note::
            |  Donot use this method directly into your code, please use the verify and assert method of assertion-datbase class

        """
        try:
            bool_ignore_case = kwargs.get("pbool_ignore_case", False)
            list_source_headers = plist_resultlist[0]
            list_headers = plist_headers
            list_diff = []
            if bool_ignore_case:
                list_source_headers = [val.lower() for val in list_source_headers]
                list_headers = [val.lower() for val in list_headers]
            if len(list_source_headers) < len(list_headers):
                raise Exception(
                    "The list_source_headers contains more headers than the resultlist one"
                )

            for val in list_headers:
                if not (val in list_source_headers):
                    list_diff.append(val)
            return list_diff

        except Exception as e:
            raise e

    def spark_execute_statement(
        self,
        pobject_Sparkclient,
        p_query,
        pbool_default_spark_command,
        pstr_name,
        str_return_type="list",
        **kwargs,
    ):
        """
        Description:
            |  This method allows user to execute a HIVE database query statement using spark-sql.

        :param pobject_Sparkclient:
        :type pobject_Sparkclient: Spark-Sql Database Connection Object
        :param p_query:
        :type p_query: String
        :param str_return_type: list/resultset
        :type str_return_type: String
        :param pint_driver_memory: driver memory
        :type pint_driver_memory: int
        :param pint_executors: number of executors
        :type pint_executors: int
        :param pint_cores: number of cores
        :type pint_cores: int
        :param pint_executor_memory: executor memory
        :type pint_executor_memory: int
        :param pstr_other_param: accepts other parameters like --conf spark.yarn.am.nodeLabelExpression=xlarge --conf spark.dynamicAllocation.enabled=false
        :type pstr_other_param: string
        :param pbool_default_spark_command: if the value is True it none of the above parameters need to be passed in the method
        :type pbool_default_spark_command: boolean
        :param pstr_name: QA name
        :type pstr_name: string

        :return: List or ResultSet or Boolean

        .. notes::
            |  This method returns a list or a resultset based on the parameter str_return_type. 'select' statements will returns List/Resultset and other type of statements will return Boolean.


        """

        try:
            int_driver_memory = kwargs.get("pint_driver_memory", None)
            int_executors = kwargs.get("pint_executors", None)
            int_cores = kwargs.get("pint_cores", None)
            int_executor_memory = kwargs.get("pint_executor_memory", None)
            str_other_param = kwargs.get("pstr_other_param", None)

            if pobject_Sparkclient is None:
                raise Exception("Object is None")
            if p_query is None:
                raise Exception("The query is None")
            if pstr_name is None:
                raise Exception("The spark config name is None")

            pobject_Sparkclient.invoke_shell()
            str_sparkAppConfig = "spark-sql"
            if pbool_default_spark_command:
                str_sparkAppConfig = str_sparkAppConfig + " --name " + pstr_name + " -S -e "
            else:
                str_sparkAppConfig = str_sparkAppConfig + " --master yarn "
                if int_driver_memory is not None:
                    str_sparkAppConfig = (
                        str_sparkAppConfig + " --driver-memory " + str(int_driver_memory) + "g"
                    )
                if int_executors is not None:
                    str_sparkAppConfig = (
                        str_sparkAppConfig + " --num-executors " + str(int_executors)
                    )
                if int_cores is not None:
                    str_sparkAppConfig = str_sparkAppConfig + " --executor-cores=" + str(int_cores)
                if int_executor_memory is not None:
                    str_sparkAppConfig = (
                        str_sparkAppConfig + " --executor-memory " + str(int_executor_memory) + "g"
                    )
                if str_other_param is not None:
                    str_sparkAppConfig = str_sparkAppConfig + str_other_param
                if pstr_name is not None:
                    str_sparkAppConfig = str_sparkAppConfig + " --name " + pstr_name + " -S -e "

            stdin, stdout, stderr = pobject_Sparkclient.exec_command(
                str_sparkAppConfig + '"' + p_query + '"'
            )
            str_errResult = stderr.readlines()
            if len(str_errResult) > 0 and ("Error in query" in str(str_errResult)):
                raise hive_SSH.SSHException("Execute command Error:" + str(str_errResult))
            df = pd.read_csv(stdout, sep="\t", header=None)
            rs = self.dataframe_to_resultset(df)
            if str_return_type == "list":
                rs = self.resultset_to_list(rs)
            return rs

        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def __difference_formatter(self, df_source_target, df_target_source, **kwargs):
        """
        Description:
            | This method is for more focused difference between two dataframes
        :param diff1:
        :param diff2:
        :return:
        """
        try:
            list_source_headers = kwargs.get("plist_source_headers")
            list_target_headers = kwargs.get("plist_target_headers")
            dict_primary_keys = kwargs.get("pdict_primary_keys")
            if list_source_headers is None and list_target_headers is None:
                self.logger_obj.info("case of no special headers given")
            list_source_primary_keys = dict_primary_keys.get("source")
            list_target_primary_keys = dict_primary_keys.get("target")

            if len(list_source_primary_keys) != len(list_target_primary_keys):
                raise Exception("The number of primary keys for Source and Target are not same")
            if len(list_source_primary_keys) != 1:
                raise Exception("Only one primary key is allowed")

            # Arranging the list according to the primary key
            for source_val in list_source_primary_keys:
                list_source_headers.remove(source_val)
            list_sorted_source_headers = list_source_primary_keys + list_source_headers

            for target_val in list_target_primary_keys:
                list_target_headers.remove(target_val)
            list_sorted_target_headers = list_target_primary_keys + list_target_headers

            source_row_count, source_column_count = df_source_target.shape
            target_row_count, source_column_count = df_target_source.shape

            df_source_target = df_source_target.add_prefix("source_")
            df_target_source = df_target_source.add_prefix("target_")

            temp_list_full = []
            list_full = []
            for count in range(len(list_sorted_target_headers)):
                list_full.append("source_" + list_sorted_source_headers[count])
                list_full.append("target_" + list_sorted_target_headers[count])

            # dataframe_final = pd.DataFrame(columns=list_full)
            whole_data_list = []
            for sr_count in range(source_row_count):
                temp_value = df_source_target["source_" + list_source_primary_keys[0]][sr_count]
                temp_source_series = df_source_target.iloc[sr_count]
                temp_target_series = df_target_source.loc[
                    df_target_source["target_" + list_target_primary_keys[0]] == temp_value
                ]
                df_target_source.drop(
                    df_target_source.loc[
                        df_target_source["target_" + list_target_primary_keys[0]] == temp_value
                    ].index,
                    inplace=True,
                )
                temp_data = []
                for header_val in list_full:
                    if header_val.startswith("target_"):
                        if temp_target_series.empty:
                            temp_data.append("NA")
                        else:
                            temp_data.append(temp_target_series[header_val].values[0][0])
                    else:
                        # fix here
                        temp_data.append(temp_source_series.get(header_val))
                whole_data_list.append(temp_data)

            for sr_count in range(target_row_count):
                # temp_value = df_target_source["target_"+list_target_primary_keys[0]][sr_count]
                temp_data = []
                for val in list_full:
                    if val.startswith("source_"):
                        temp_data.append("NA")
                    else:
                        temp_data.append(df_target_source[val][sr_count])
                whole_data_list.append(temp_data)

            dataframe_final = pd.DataFrame(whole_data_list, columns=list_full)

            return dataframe_final

        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(str(e))

    def check_db_exists(self, object_connection, str_database_name):
        """
        Description:
            |  This method is used to verify the existence of DB in particular DB Server

        :param object_connection: This parameter contains the connection object provided by the user
        :type object_connection: Object
        :param str_database_name: This parameter contains the DB name provided by the user
        :type str_database_name: string

        :return: bool

        Examples:
            | check_db_exists(connection, database_name)
        .. warning::
            |  This method currently supports SQL Server, PostgreSQL and Oracle DB Servers.
        """

        try:
            if object_connection is None:
                self.__obj_db_exception.raise_null_database_object()

            if str_database_name is None:
                self.__obj_db_exception.raise_null_database_name()

            bln_is_database_exists = False

            if object_connection.engine.name == "postgresql":
                rs_resultset = self.execute_statement(
                    object_connection,
                    "SELECT * FROM pg_catalog.pg_database WHERE datname='"
                    + str_database_name
                    + "'",
                    str_return_type="resultset",
                )
                if rs_resultset.rowcount == 0:
                    bln_is_database_exists = False
                else:
                    bln_is_database_exists = True

            elif object_connection.engine.name == "mssql":
                rs_resultset = self.execute_statement(
                    object_connection,
                    "select * from sys.databases where name='" + str_database_name + "'",
                    str_return_type="resultset",
                )
                if rs_resultset.rowcount == 0:
                    bln_is_database_exists = False
                else:
                    bln_is_database_exists = True

            elif object_connection.engine.name == "oracle":
                lst_result = self.execute_statement(
                    object_connection,
                    "SELECT owner FROM all_tab_columns where Owner ='"
                    + str_database_name.upper()
                    + "'",
                    str_return_type="list",
                )
                if lst_result.__len__() < 2:
                    bln_is_database_exists = False
                else:
                    bln_is_database_exists = True

            else:
                raise self.__obj_db_exception.raise_custom_exception(
                    pstr_message="Error -> Provided parameters are not supported",
                    pbool_fail_on_exception=False,
                )

            return bln_is_database_exists

        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(
                pstr_message="Error -> DB not connected properly" + str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def verify_column_metadata(
        self, pobj_connection, pstr_db_name, str_table_name, pstr_col_name, **kwargs
    ):
        """
        Description:
            |  This method is used to perform different operation on any column like checking its existence, its datatype, its max length, its NULL and
               Primtary key constraints etc.

        :param pobj_connection: This parameter contains the connection object provided by the user
        :type pobj_connection: Object
        :param pstr_db_name: This parameter contains the database name provided by the user
        :type pstr_db_name: string
        :param str_table_name: This parameter contains the table name provided by the user
        :type str_table_name: string
        :param pstr_col_name: This parameter contains the column name provided by the user
        :type pstr_col_name: string
        :param bln_col_existence: This flag tells us that the user wants to check the column's existence
        :type bln_col_existence: bool
        :param bln_data_type: This flag tells us that the user wants to get the Data Type of particular column
        :type bln_data_type: bool
        :param bln_max_length: This flag tells us that the user wants to get the Maximum length of particular column
        :type bln_max_length: bool
        :param bln_is_null: This flag tells us that the user wants to verify the NULL constraint of respective column
        :type bln_is_null: bool
        :param bln_is_not_null: This flag tells us that the user wants to verify the Not NULL constraint of respective column
        :type bln_is_not_null: bool
        :param bln_is_primary_key: This flag tells us that the user wants to verify the Primary Key constraint of respective column
        :type bln_is_primary_key: bool
        :param bln_is_not_primary_key: This flag tells us that the user wants to verify the No Primary Key constraint of respective column
        :type bln_is_not_primary_key: bool

        :return: dictionary

        Examples:
            | verify_column_metadata(connection,database_name,table_name,column_name,bln_col_existence=True)
            | verify_column_metadata(connection,database_name,table_name,column_name,pstr_data_type=True)
            | verify_column_metadata(connection,database_name,table_name,column_name,pstr_max_length=True)
            | verify_column_metadata(connection,database_name,table_name,column_name,bln_is_null=True)
            | verify_column_metadata(connection,database_name,table_name,column_name,bln_is_not_null=True)
            | verify_column_metadata(connection,database_name,table_name,column_name,bln_is_primary_key=True)
            | verify_column_metadata(connection,database_name,table_name,column_name,bln_is_not_primary_key=True)
            | verify_column_metadata(connection,database_name,table_name,column_name)

        .. warning::
            |  This method currently supports SQL Server, PostgreSQL and Oracle DB Servers.

        """
        try:
            dict_result = {}
            rs_resultset = ""
            if pobj_connection.engine.name not in ("mssql", "oracle", "postgresql"):
                raise self.__obj_db_exception.raise_custom_exception(
                    pstr_message="Error -> Provided parameters are not supported",
                    pbool_fail_on_exception=False,
                )
            if "bln_col_existence" in kwargs:
                if pobj_connection.engine.name == "oracle":
                    lst_result = self.execute_statement(
                        pobj_connection,
                        "SELECT * FROM all_tab_columns WHERE table_name = '"
                        + str_table_name.upper()
                        + "' AND column_name ='"
                        + pstr_col_name.upper()
                        + "' and owner='"
                        + pstr_db_name.upper()
                        + "'",
                        str_return_type="list",
                    )
                    if lst_result.__len__() < 2:
                        dict_result["bln_col_existence"] = False
                    else:
                        dict_result["bln_col_existence"] = True
                if pobj_connection.engine.name == "postgresql":
                    rs_resultset = self.execute_statement(
                        pobj_connection,
                        "SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '"
                        + str_table_name
                        + "' AND COLUMN_NAME = '"
                        + pstr_col_name
                        + "' and table_schema='"
                        + pstr_db_name
                        + "'",
                        str_return_type="resultset",
                    )
                    if rs_resultset.rowcount == 0:
                        dict_result["bln_col_existence"] = False
                    else:
                        dict_result["bln_col_existence"] = True
                if pobj_connection.engine.name == "mssql":
                    rs_resultset = self.execute_statement(
                        pobj_connection,
                        "use "
                        + pstr_db_name
                        + " SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '"
                        + str_table_name
                        + "' AND COLUMN_NAME = '"
                        + pstr_col_name
                        + "'",
                        str_return_type="resultset",
                    )
                    if rs_resultset.rowcount == 0:
                        dict_result["bln_col_existence"] = False
                    else:
                        dict_result["bln_col_existence"] = True
            if "pstr_data_type" in kwargs:
                if pobj_connection.engine.name == "oracle":
                    rs_resultset = self.execute_statement(
                        pobj_connection,
                        "SELECT data_type FROM all_tab_columns WHERE table_name = '"
                        + str_table_name.upper()
                        + "' AND column_name ='"
                        + pstr_col_name.upper()
                        + "' and owner='"
                        + pstr_db_name.upper()
                        + "'",
                        str_return_type="resultset",
                    )
                    pstr_datatype = rs_resultset.fetchall()
                    if pstr_datatype[0][0] == "":
                        dict_result["pstr_data_type"] = False
                    else:
                        dict_result["pstr_data_type"] = pstr_datatype[0][0]
                if pobj_connection.engine.name == "postgresql":
                    rs_resultset = self.execute_statement(
                        pobj_connection,
                        "SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '"
                        + str_table_name
                        + "' AND COLUMN_NAME = '"
                        + pstr_col_name
                        + "' and table_schema='"
                        + pstr_db_name
                        + "'",
                        str_return_type="resultset",
                    )
                    pstr_datatype = rs_resultset.fetchall()
                    if pstr_datatype[0][0] == "":
                        dict_result["pstr_data_type"] = False
                    else:
                        dict_result["pstr_data_type"] = pstr_datatype[0][0]
                if pobj_connection.engine.name == "mssql":
                    rs_resultset = self.execute_statement(
                        pobj_connection,
                        "use "
                        + pstr_db_name
                        + " SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '"
                        + str_table_name
                        + "' AND COLUMN_NAME = '"
                        + pstr_col_name
                        + "'",
                        str_return_type="resultset",
                    )
                    pstr_datatype = rs_resultset.fetchall()
                    if pstr_datatype[0][0] == "":
                        dict_result["pstr_data_type"] = False
                    else:
                        dict_result["pstr_data_type"] = pstr_datatype[0][0]
            if "pstr_max_length" in kwargs:
                if pobj_connection.engine.name == "postgresql":
                    rs_resultset = self.execute_statement(
                        pobj_connection,
                        "SELECT character_maximum_length FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '"
                        + str_table_name
                        + "' AND COLUMN_NAME = '"
                        + pstr_col_name
                        + "' and table_schema='"
                        + pstr_db_name
                        + "'",
                        str_return_type="resultset",
                    )
                    pstr_maxlength = rs_resultset.fetchall()
                    if pstr_maxlength[0][0] == None:
                        dict_result["pstr_max_length"] = False
                    else:
                        dict_result["pstr_max_length"] = str(pstr_maxlength[0][0])
                if pobj_connection.engine.name == "mssql":
                    rs_resultset = self.execute_statement(
                        pobj_connection,
                        "use "
                        + pstr_db_name
                        + " Select * from sys.columns where name=N'"
                        + pstr_col_name
                        + "' and OBJECT_ID = OBJECT_ID(N'"
                        + str_table_name
                        + "')",
                        str_return_type="resultset",
                    )
                    pstr_maxlength = rs_resultset.fetchall()
                    if pstr_maxlength[0][5] == None:
                        dict_result["pstr_max_length"] = False
                    else:
                        dict_result["pstr_max_length"] = str(pstr_maxlength[0][5])
                if pobj_connection.engine.name == "oracle":
                    rs_resultset = self.execute_statement(
                        pobj_connection,
                        "SELECT data_length FROM all_tab_columns WHERE table_name = '"
                        + str_table_name.upper()
                        + "' AND column_name ='"
                        + pstr_col_name.upper()
                        + "' and owner='"
                        + pstr_db_name.upper()
                        + "'",
                        str_return_type="resultset",
                    )
                    pstr_maxlength = rs_resultset.fetchall()
                    if pstr_maxlength[0][0] == None:
                        dict_result["pstr_max_length"] = False
                    else:
                        dict_result["pstr_max_length"] = str(pstr_maxlength[0][0])
            if "bln_is_null" in kwargs:
                if pobj_connection.engine.name == "oracle":
                    rs_resultset = self.execute_statement(
                        pobj_connection,
                        "SELECT nullable FROM all_tab_columns WHERE table_name = '"
                        + str_table_name.upper()
                        + "' AND column_name ='"
                        + pstr_col_name.upper()
                        + "' and owner='"
                        + pstr_db_name.upper()
                        + "'",
                        str_return_type="resultset",
                    )
                    bln_isnull = rs_resultset.fetchall()
                    if bln_isnull[0][0] == "N":
                        dict_result["bln_is_null"] = False
                    else:
                        dict_result["bln_is_null"] = True

                if pobj_connection.engine.name == "postgresql":
                    rs_resultset = self.execute_statement(
                        pobj_connection,
                        "SELECT is_nullable FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '"
                        + str_table_name
                        + "' AND COLUMN_NAME = '"
                        + pstr_col_name
                        + "' and table_schema='"
                        + pstr_db_name
                        + "'",
                        str_return_type="resultset",
                    )
                    bln_isnull = rs_resultset.fetchall()
                    if bln_isnull[0][0] == "NO":
                        dict_result["bln_is_null"] = False
                    else:
                        dict_result["bln_is_null"] = True

                if pobj_connection.engine.name == "mssql":
                    rs_resultset = self.execute_statement(
                        pobj_connection,
                        "use "
                        + pstr_db_name
                        + " SELECT is_nullable FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '"
                        + str_table_name
                        + "' AND COLUMN_NAME = '"
                        + pstr_col_name
                        + "'",
                        str_return_type="resultset",
                    )
                    bln_isnull = rs_resultset.fetchall()
                    if bln_isnull[0][0] == "NO":
                        dict_result["bln_is_null"] = False
                    else:
                        dict_result["bln_is_null"] = True
            if "bln_is_not_null" in kwargs:
                if pobj_connection.engine.name == "oracle":
                    rs_resultset = self.execute_statement(
                        pobj_connection,
                        "SELECT nullable FROM all_tab_columns WHERE table_name = '"
                        + str_table_name.upper()
                        + "' AND column_name ='"
                        + pstr_col_name.upper()
                        + "' and owner='"
                        + pstr_db_name.upper()
                        + "'",
                        str_return_type="resultset",
                    )
                    bln_isnull = rs_resultset.fetchall()
                    if bln_isnull[0][0] == "N":
                        dict_result["bln_is_not_null"] = True
                    else:
                        dict_result["bln_is_not_null"] = False
                if pobj_connection.engine.name == "postgresql":
                    rs_resultset = self.execute_statement(
                        pobj_connection,
                        "SELECT is_nullable FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '"
                        + str_table_name
                        + "' AND COLUMN_NAME = '"
                        + pstr_col_name
                        + "' and table_schema='"
                        + pstr_db_name
                        + "'",
                        str_return_type="resultset",
                    )
                    bln_isnull = rs_resultset.fetchall()
                    if bln_isnull[0][0] == "NO":
                        dict_result["bln_is_not_null"] = True
                    else:
                        dict_result["bln_is_not_null"] = False
                if pobj_connection.engine.name == "mssql":
                    rs_resultset = self.execute_statement(
                        pobj_connection,
                        "use "
                        + pstr_db_name
                        + " SELECT is_nullable FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '"
                        + str_table_name
                        + "' AND COLUMN_NAME = '"
                        + pstr_col_name
                        + "'",
                        str_return_type="resultset",
                    )
                    bln_isnull = rs_resultset.fetchall()
                    if bln_isnull[0][0] == "NO":
                        dict_result["bln_is_not_null"] = True
                    else:
                        dict_result["bln_is_not_null"] = False
            if "bln_is_primary_key" in kwargs:
                if pobj_connection.engine.name == "oracle":
                    rs_resultset = self.execute_statement(
                        pobj_connection,
                        "SELECT cols.table_name, cols.column_name, cols.position, cons.status, cons.owner FROM all_constraints cons, all_cons_columns cols WHERE cols.table_name ='"
                        + str_table_name.upper()
                        + "'  and cols.owner='"
                        + pstr_db_name.upper()
                        + "' AND cols.column_name ='"
                        + pstr_col_name.upper()
                        + "' AND cons.constraint_type = 'P' AND cons.constraint_name = cols.constraint_name AND cons.owner = cols.owner ORDER BY cols.table_name, cols.position",
                        str_return_type="list",
                    )
                    if rs_resultset.__len__() < 2:
                        dict_result["bln_is_primary_key"] = False
                    else:
                        dict_result["bln_is_primary_key"] = True
                if pobj_connection.engine.name == "postgresql":
                    rs_resultset = self.execute_statement(
                        pobj_connection,
                        "SELECT K.TABLE_NAME, C.CONSTRAINT_TYPE, K.COLUMN_NAME, K.CONSTRAINT_NAME FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS C JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS K ON C.TABLE_NAME = K.TABLE_NAME AND C.CONSTRAINT_CATALOG = K.CONSTRAINT_CATALOG AND C.CONSTRAINT_SCHEMA = K.CONSTRAINT_SCHEMA AND C.CONSTRAINT_NAME = K.CONSTRAINT_NAME WHERE C.CONSTRAINT_TYPE = 'PRIMARY KEY' And K.Table_Name='"
                        + str_table_name
                        + "' And K.Column_name='"
                        + pstr_col_name
                        + "' and K.table_schema='"
                        + pstr_db_name
                        + "' ORDER BY K.TABLE_NAME, C.CONSTRAINT_TYPE, K.CONSTRAINT_NAME",
                        str_return_type="resultset",
                    )
                    if rs_resultset.rowcount == 0:
                        dict_result["bln_is_primary_key"] = False
                    else:
                        dict_result["bln_is_primary_key"] = True
                if pobj_connection.engine.name == "mssql":
                    rs_resultset = self.execute_statement(
                        pobj_connection,
                        "use "
                        + pstr_db_name
                        + " SELECT K.TABLE_NAME, C.CONSTRAINT_TYPE, K.COLUMN_NAME, K.CONSTRAINT_NAME FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS C JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS K ON C.TABLE_NAME = K.TABLE_NAME AND C.CONSTRAINT_CATALOG = K.CONSTRAINT_CATALOG AND C.CONSTRAINT_SCHEMA = K.CONSTRAINT_SCHEMA AND C.CONSTRAINT_NAME = K.CONSTRAINT_NAME WHERE C.CONSTRAINT_TYPE = 'PRIMARY KEY' And K.Table_Name='"
                        + str_table_name
                        + "' And K.Column_name='"
                        + pstr_col_name
                        + "' ORDER BY K.TABLE_NAME, C.CONSTRAINT_TYPE, K.CONSTRAINT_NAME",
                        str_return_type="resultset",
                    )
                    if rs_resultset.rowcount == 0:
                        dict_result["bln_is_primary_key"] = False
                    else:
                        dict_result["bln_is_primary_key"] = True
            if "bln_is_not_primary_key" in kwargs:
                if pobj_connection.engine.name == "oracle":
                    rs_resultset = self.execute_statement(
                        pobj_connection,
                        "SELECT cols.table_name, cols.column_name, cols.position, cons.status, cons.owner FROM all_constraints cons, all_cons_columns cols WHERE cols.table_name ='"
                        + str_table_name.upper()
                        + "' AND cols.column_name ='"
                        + pstr_col_name.upper()
                        + "' AND cons.constraint_type = 'P' AND cons.constraint_name = cols.constraint_name AND cons.owner = cols.owner ORDER BY cols.table_name, cols.position",
                        str_return_type="list",
                    )
                    if rs_resultset.__len__() < 2:
                        dict_result["bln_is_not_primary_key"] = True
                    else:
                        dict_result["bln_is_not_primary_key"] = False
                if pobj_connection.engine.name == "postgresql":
                    rs_resultset = self.execute_statement(
                        pobj_connection,
                        "SELECT K.TABLE_NAME, C.CONSTRAINT_TYPE, K.COLUMN_NAME, K.CONSTRAINT_NAME FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS C JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS K ON C.TABLE_NAME = K.TABLE_NAME AND C.CONSTRAINT_CATALOG = K.CONSTRAINT_CATALOG AND C.CONSTRAINT_SCHEMA = K.CONSTRAINT_SCHEMA AND C.CONSTRAINT_NAME = K.CONSTRAINT_NAME WHERE C.CONSTRAINT_TYPE = 'PRIMARY KEY' And K.Table_Name='"
                        + str_table_name
                        + "' And K.Column_name='"
                        + pstr_col_name
                        + "' and K.table_schema='"
                        + pstr_db_name
                        + "' ORDER BY K.TABLE_NAME, C.CONSTRAINT_TYPE, K.CONSTRAINT_NAME",
                        str_return_type="resultset",
                    )
                    if rs_resultset.rowcount == 0:
                        dict_result["bln_is_not_primary_key"] = True
                    else:
                        dict_result["bln_is_not_primary_key"] = False
                if pobj_connection.engine.name == "mssql":
                    rs_resultset = self.execute_statement(
                        pobj_connection,
                        "use "
                        + pstr_db_name
                        + " SELECT K.TABLE_NAME, C.CONSTRAINT_TYPE, K.COLUMN_NAME, K.CONSTRAINT_NAME FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS C JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS K ON C.TABLE_NAME = K.TABLE_NAME AND C.CONSTRAINT_CATALOG = K.CONSTRAINT_CATALOG AND C.CONSTRAINT_SCHEMA = K.CONSTRAINT_SCHEMA AND C.CONSTRAINT_NAME = K.CONSTRAINT_NAME WHERE C.CONSTRAINT_TYPE = 'PRIMARY KEY' And K.Table_Name='"
                        + str_table_name
                        + "' And K.Column_name='"
                        + pstr_col_name
                        + "' ORDER BY K.TABLE_NAME, C.CONSTRAINT_TYPE, K.CONSTRAINT_NAME",
                        str_return_type="resultset",
                    )
                    if rs_resultset.rowcount == 0:
                        dict_result["bln_is_not_primary_key"] = True
                    else:
                        dict_result["bln_is_not_primary_key"] = False
            else:
                if len(dict_result) == 0:
                    if pobj_connection.engine.name == "oracle":
                        rs_resultset = self.execute_statement(
                            pobj_connection,
                            "SELECT * FROM all_tab_columns WHERE table_name = '"
                            + str_table_name.upper()
                            + "' AND column_name = '"
                            + pstr_col_name.upper()
                            + "' and owner='"
                            + pstr_db_name.upper()
                            + "'",
                            str_return_type="resultset",
                        )
                        return rs_resultset.fetchall()
                    else:
                        rs_resultset = self.execute_statement(
                            pobj_connection,
                            "SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '"
                            + str_table_name
                            + "' AND COLUMN_NAME = '"
                            + pstr_col_name
                            + "'",
                            str_return_type="resultset",
                        )
                    return rs_resultset.fetchall()

            return dict_result

        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(
                pstr_message="Error -> Column information id not given properly " + str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def modify_sql_query(self, pfile_path, pdict_data_dictionary, **kwargs):
        """
        Description:
        |  This function edit sql queries residing inside .sql,.txt or .json files at run time
        |  The user has to save the file at a specific location
        |  Identify the variables that have to be changed
        |  Replace the variables with unique identifiers and save the file
        :param pfile_path: File path of the file that will be edited
        :type pfile_path: string
        :param pdict_data_dictionary: Dictionary in the format of {'unique_identifiers1': 'actual_value1','unique_identifiers2': ' actual_value2'}
        :type pdict_data_dictionary: dictionary
        :param pstr_key: key in case the query is saved in a json file
        :type pstr_key: kwargs
        :return: str_query : The query containing the actual value with the unique_Identifiers replaced
        :type str_query: string
            Examples:
        |  1. Let us imagine we have a sql file or a text file containing query
        |  Values that have to changed ; Replace them by Unique_Idetifiers : pstr_emailaddress , pstr_updoperation
        |  Actual Values :saurabhpiyush@spglobal.com , 1
        |  pdict_data_dictionary = { "pstr_emailaddress" : "saurabhpiyush@spglobal.com","pstr_updoperation" : "1"}
        |  Input call : modify_sql_query (pfile_path, pdict_data_dictionary)
        |  2. Let us imagine we have a sql query in a json format : {"key1" :"query1","key2" :"query2"}
        |  Query that has to be edited : query2
        |  Key Selected for query2 = key2
        |  pstr_key = key2
        |  Input call :  modify_sql_query (pfile_path, pdict_data_dictionary, pstr_key = 'key2' )
        """

        try:
            if pfile_path is None:
                self.__obj_db_exception.raise_null_filepath()
            if os.stat(pfile_path).st_size == 0:
                self.__obj_db_exception.raise_null_query()
            if pdict_data_dictionary is None:
                raise Exception("Dictionary passed is None. There is nothing to replace")
            if pfile_path.endswith((".sql", ".txt")):
                str_query = ""
                with open(pfile_path, "r") as f:
                    for line in f:
                        str_query = str_query + " " + line
                f.close()

            elif pfile_path.endswith(".json"):
                if kwargs.get("pstr_key") is not None:
                    json_key = str(kwargs.get("pstr_key"))
                    f1 = open(pfile_path, "r")
                    str_json = f1.read()
                    f1.close()
                    try:
                        pstr_json = json.loads(str_json)
                        str_query = pstr_json[json_key]
                    except Exception as e:
                        raise Exception("Not a valid json file or invalid key--->" + str(e))
                else:
                    raise Exception("Error-->Key missing from parameters for json file")
            else:
                raise Exception("Accepted file formats are .sql, .txt & .json")
            for key in pdict_data_dictionary:
                if key in str_query:
                    str_query = str_query.replace(key, pdict_data_dictionary[key])
                else:
                    raise Exception("Unique Identifier-->" + key + "not found in the query")
            return str_query
        except Exception as e:
            self.__obj_db_exception.raise_generic_exception(
                pstr_message="Exception occured in method--> modify_sql_query-->" + str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=True,
                pbool_use_pytest_format=True,
            )
