"""
Description: This module provides methods to interact with File transfer protocols
 - FTP, SFTP, and FTPS.
"""
import os
import pathlib
from datetime import datetime
from ftplib import FTP, error_perm, FTP_TLS

import boto3
import paramiko
from dateutil import parser

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.utils.core_security import Security
from cafex_core.utils.exceptions import CoreExceptions


class FileTransferUtils:
    """
    Description:
        |  This class provides methods to interact with File transfer protocols
        - FTP, SFTP, and FTPS.
    """
    security = Security()

    class FTP:
        """
        Description:
            |  This class provides methods to interact with FTP.
        """

        def __init__(self):
            self.__obj_exception = CoreExceptions()
            self.logger_class = CoreLogger(name=__name__)
            self.logger = self.logger_class.get_logger()

        def open_ftp_connection(self, ftp_host: str, ftp_username: str, ftp_password: str, ) -> FTP:
            """
            Establishes an FTP connection to the specified server.

            Args:
                ftp_host (str): The hostname of the FTP server.
                ftp_username (str): The username for authentication on the FTP server.
                ftp_password (str): The password for authentication on the FTP server.

            Returns:
                FTP: An FTP connection object upon successful connection.

            Raises:
                Exception: If the connection to the FTP server fails or authentication fails.

            Examples:
                >> ftp_conn = FileTransferUtils().FTP().
                open_ftp_connection('ftp.example.com', 'username', 'password')
            """
            try:
                ftp_connection = FileTransferUtils().security.open_ftp_connection(
                    ftp_host, ftp_username, ftp_password
                )
                return ftp_connection
            except error_perm as e:
                raise error_perm(f"Authentication failed: {str(e)}") from e
            except Exception as e:
                error_message = f"An unexpected error occurred: {str(e)}"
                self.__obj_exception.raise_generic_exception(error_message)
                raise e

        def get_dir_info_from_ftp(self, ftp_conn: FTP, dir_path: str) -> tuple[int, dict]:
            """
            Retrieves file details like name, size, last modified date, permissions, and owner
            from an FTP directory.

            Args:
                ftp_conn (FTP): The FTP connection object.
                dir_path (str): Directory from which to retrieve file details.

            Returns:
                tuple: Number of files present in the directory and their details in a nested
                dictionary format.
            """
            try:
                file_details = {}
                ftp_conn.cwd(dir_path)  # Change to the specified directory
                file_list = []

                # Retrieve directory listing
                ftp_conn.retrlines("LIST", callback=file_list.append)

                for index, line in enumerate(file_list, start=1):
                    tokens = line.split(maxsplit=9)
                    file_details[f"file{index}"] = {
                        "file name": tokens[8],
                        "file size": tokens[4],
                        "file last modified date": str(parser.parse(" ".join(tokens[5:8]))),
                        "file permissions": tokens[0],
                        "file owner": f"{tokens[2]} {tokens[3]}"
                    }
                return len(file_details), file_details
            except Exception as e:
                error_message = f"An error occurred while connecting to the FTP server: {str(e)}"
                self.__obj_exception.raise_generic_exception(error_message)
                raise e

        def download_files_from_ftp(
                self, ftp_conn: FTP, files_to_download: list, ftp_dir: str, local_path: str
        ) -> None:
            """
            Downloads files from an FTP server.

            Args:
                ftp_conn (FTP): The FTP connection object.
                files_to_download (list): List of filenames to download.
                ftp_dir (str): Directory on the FTP server from which to download files.
                local_path (str): Local directory where the files will be saved.

            Examples:
                >> FileTransferUtils().FTP().download_files_from_ftp(ftp_conn,
                ['file1.pdf'], '/Inbox/', 'C:/Users/Project/')
            """
            try:
                ftp_conn.cwd(ftp_dir)
                os.makedirs(local_path, exist_ok=True)
                for file in files_to_download:
                    local_file_path = os.path.join(local_path, file)
                    with open(local_file_path, "wb") as local_file:
                        ftp_conn.retrbinary(f"RETR {file}", local_file.write, 1024)
            except Exception as e:
                error_message = f"An error occurred while downloading files from the FTP " \
                                f"server: {str(e)}"
                self.__obj_exception.raise_generic_exception(error_message)
                raise e

        def uploading_files_to_ftp(
                self, pobject_ftp_conn: FTP, plist_upload_files: list,
                pstr_ftp_dir: str, pstr_local_path: str
        ) -> None:
            """
            This method uploads files to FTP.

            Args:
                pobject_ftp_conn (FTP Connection Object): The FTP connection object.
                plist_upload_files (list): List of files that need to be uploaded.
                pstr_ftp_dir (str): Directory to where the files need to be uploaded.
                pstr_local_path (str): Local path from where the files need to be uploaded.

            Examples:
                >> FileTransferUtils().FTP().uploading_files_to_ftp(ftp_conn,
                ['file1.pdf'], '/Inbox/', 'C:/Users/Project/')
            """
            try:
                pobject_ftp_conn.cwd(pstr_ftp_dir)
                for file in plist_upload_files:
                    str_file_local = os.path.join(pstr_local_path, file)
                    with open(str_file_local, "rb") as local_file:
                        pobject_ftp_conn.storbinary("STOR " + file, local_file)
                    local_file.close()
            except Exception as e:
                self.__obj_exception.raise_generic_exception(str(e))
                raise e

        def close_ftp_conn(self, ftp_conn: FTP) -> None:
            """
            Closes the FTP connection.

            Args:
                ftp_conn (FTP): The FTP connection object to be closed.

            Examples:
                >> FileTransferUtils().FTP().close_ftp_conn(ftp_conn)
            """
            if ftp_conn is None:
                raise ValueError("FTP connection object cannot be None.")

            try:
                ftp_conn.quit()
            except Exception as e:
                error_message = f"Failed to close FTP connection: {str(e)}"
                self.__obj_exception.raise_generic_exception(error_message)
                raise e

    class SFTP:
        """ This class provides methods to interact with SFTP. """

        def __init__(self):
            self.__obj_exception = CoreExceptions()
            self.logger_class = CoreLogger(name=__name__)
            self.logger = self.logger_class.get_logger()
            self.transport = None

        def open_sftp_connection(
                self, sftp_host: str, sftp_port: int, sftp_username: str,
                sftp_password: str
        ) -> paramiko.SFTPClient:
            """
            This method creates an SFTP connection.

            Args:
                sftp_host (str): Host name of the SFTP server.
                sftp_port (int): Port number for the SFTP server.
                sftp_username (str): Username for the SFTP server.
                sftp_password (str): Password for the SFTP server.

            Returns:
                SFTP Connection Object: The created SFTP connection object.

            Examples:
                >> sftp_conn = FileTransferUtils().SFTP().
                open_sftp_connection('sftp.example.com', 22, 'username', 'password')
            """
            try:

                sftp_connection, self.transport = FileTransferUtils().security.open_sftp_connection(
                    sftp_host, sftp_port, sftp_username, sftp_password
                )
                return sftp_connection
            except Exception as e:
                error_message = f"An error occurred while connecting to the SFTP server: {str(e)}"
                self.__obj_exception.raise_generic_exception(error_message)
                raise e

        def get_dir_info_from_sftp(self, sftp_conn: paramiko.SFTPClient,
                                   dir_path: str) -> tuple[int, dict]:
            """
            This method retrieves file details like name, size, last modified date, permissions,
             and owner from SFTP.

            Args:
                sftp_conn (SFTP Connection Object): The SFTP connection object.
                dir_path (str): Directory from where the file details need to be retrieved.

            Returns:
                tuple: Number of files present in the directory and their details in a nested
                dictionary format.

            Examples:
                >> file_count, file_details = FileTransferUtils().SFTP().
                get_dir_info_from_sftp(sftp_conn, '/Inbox/')
            """
            try:
                file_details = {}
                file_list = sftp_conn.listdir_attr(dir_path)

                for index, file_attr in enumerate(file_list, start=1):
                    file_details[f"file{index}"] = {
                        "file name": file_attr.filename,
                        "file size": file_attr.st_size,
                        "file last modified date": str(datetime.fromtimestamp(file_attr.st_mtime)),
                        "file permissions": oct(file_attr.st_mode)[-3:],
                        "file owner": f"{file_attr.st_uid} {file_attr.st_gid}"
                    }
                return len(file_details), file_details
            except Exception as e:
                error_message = f"An error occurred while retrieving directory info from " \
                                f"the SFTP server: {str(e)}"
                self.__obj_exception.raise_generic_exception(error_message)
                raise e

        def download_files_from_sftp(
                self, sftp_conn: paramiko.SFTPClient, download_files: list, sftp_dir: str,
                local_path: str
        ) -> None:
            """
            This method downloads files from SFTP.

            Args:
                sftp_conn (SFTP Connection Object): The SFTP connection object.
                download_files (list): List of files that need to be downloaded.
                sftp_dir (str): Directory from where the files are to be downloaded.
                local_path (str): Target path to download the files.

            Examples:
                >> FileTransferUtils().SFTP().download_files_from_sftp(sftp_conn,
                ['file1.pdf'], '/Inbox/', 'C:/Users/Project/')
            """
            try:
                os.makedirs(local_path, exist_ok=True)
                for file in download_files:
                    remote_file_path = os.path.join(sftp_dir, file)
                    local_file_path = os.path.join(local_path, file)
                    self.logger.info("Downloading from %s to %s", remote_file_path, local_file_path)
                    sftp_conn.get(remote_file_path, local_file_path)
            except Exception as e:
                error_message = f"An error occurred while downloading files from the " \
                                f"SFTP server: {str(e)}"
                self.__obj_exception.raise_generic_exception(error_message)
                raise e

        def uploading_files_to_sftp(
                self, sftp_conn: paramiko.SFTPClient, upload_files: list, sftp_dir: str,
                local_path: str
        ) -> None:
            """
            This method uploads files to SFTP.

            Args:
                sftp_conn (SFTP Connection Object): The SFTP connection object.
                upload_files (list): List of files that need to be uploaded.
                sftp_dir (str): Directory to where the files need to be uploaded.
                local_path (str): Local path from where the files need to be uploaded.

            Examples:
                >> FileTransferUtils().SFTP().uploading_files_to_sftp(sftp_conn,
                ['file1.pdf'], '/Inbox/', 'C:/Users/Project/')
            """
            try:
                os.makedirs(local_path, exist_ok=True)
                for file in upload_files:
                    remote_file_path = os.path.join(sftp_dir, file)
                    local_file_path = os.path.join(local_path, file)
                    self.logger.info("Uploading from %s to %s", local_file_path, remote_file_path)
                    sftp_conn.put(local_file_path, remote_file_path)
            except Exception as e:
                error_message = f"An error occurred while uploading files to the " \
                                f"SFTP server: {str(e)}"
                self.__obj_exception.raise_generic_exception(error_message)
                raise e

        def close_sftp_conn(self, sftp_conn: paramiko.SFTPClient) -> None:
            """
            This method closes the SFTP connection.

            Args:
                sftp_conn (SFTP Connection Object): The SFTP connection object.

            Examples:
                >> FileTransferUtils().SFTP().close_sftp_conn(sftp_conn)
            """
            try:
                sftp_conn.close()
                if self.transport is not None:
                    self.transport.close()
            except Exception as e:
                self.__obj_exception.raise_generic_exception(str(e))
                raise e

    class FTPS:
        """ This class provides methods to interact with FTPS. """

        def __init__(self):
            self.__obj_exception = CoreExceptions()
            self.logger_class = CoreLogger(name=__name__)
            self.logger = self.logger_class.get_logger()

        def open_ftps_connection(self, ftps_host: str, ftps_username: str, ftps_password: str
                                 ) -> FTP_TLS:
            """
            This method creates an FTPS connection.

            Args:
                ftps_host (str): Host name of the FTPS server.
                ftps_username (str): Username for the FTPS server.
                ftps_password (str): Password for the FTPS server.

            Returns:
                FTPS Connection Object: The created FTPS connection object.

            Examples:
                >> ftps_conn = FileTransferUtils().FTPS().
                open_ftps_connection('ftps.example.com', 'username', 'password')
            """
            try:
                ftps_conn = FileTransferUtils().security.ftps_connection(
                    ftps_host, ftps_username, ftps_password
                )
                self.logger.info("Connected to FTPS server.")
                return ftps_conn
            except Exception as e:
                error_message = f"An error occurred while connecting to the " \
                                f"FTPS server: {str(e)}"
                self.__obj_exception.raise_generic_exception(error_message)
                raise e

        def get_dir_info_from_ftps(self, ftps_conn: FTP_TLS, dir_path: str) -> tuple[int, dict]:
            """
            This method retrieves file details like name, size, last modified date, permissions,
             and owner from FTPS.

            Args:
                ftps_conn (FTPS Connection Object): The FTPS connection object.
                dir_path (str): Directory from where the file details need to be retrieved.

            Returns:
                tuple: Number of files present in the directory and their details in a nested
                dictionary format.

            Examples:
                >> file_count, file_details = FileTransferUtils().FTPS().
                get_dir_info_from_ftps(ftps_conn, '/Inbox/')
            """
            try:
                file_details = {}
                ftps_conn.cwd(dir_path)  # Change to the specified directory

                # Retrieve directory listing
                list_log = []
                ftps_conn.retrlines("LIST", callback=list_log.append)

                for index, line in enumerate(list_log, start=1):
                    tokens = line.split(maxsplit=9)
                    file_details[f"file{index}"] = {
                        "file name": tokens[8],
                        "file size": tokens[4],
                        "file last modified date": str(parser.parse(" ".join(tokens[5:8]))),
                        "file permissions": tokens[0],
                        "file owner": f"{tokens[2]} {tokens[3]}"
                    }
                return len(file_details), file_details
            except Exception as e:
                error_message = f"An error occurred while retrieving directory info " \
                                f"from the FTPS server: {str(e)}"
                self.__obj_exception.raise_generic_exception(error_message)
                raise e

        def download_files_from_ftps(
                self, ftps_conn: FTP_TLS, download_files: list, ftps_dir: str, local_path: str
        ) -> None:
            """
            This method downloads files from FTPS.

            Args:
                ftps_conn (FTPS Connection Object): The FTPS connection object.
                download_files (list): List of files that need to be downloaded.
                ftps_dir (str): Directory from where the files are to be downloaded.
                local_path (str): Target path to download the files.

            Examples:
                >> FileTransferUtils().FTPS().download_files_from_ftps(ftps_conn,
                ['file1.pdf'], '/Inbox/', 'C:/Users/Project/')
            """
            try:
                os.makedirs(local_path, exist_ok=True)
                ftps_conn.cwd(ftps_dir)
                for file in download_files:
                    local_file_path = os.path.join(local_path, file)
                    with open(local_file_path, "wb") as local_file:
                        ftps_conn.retrbinary(f"RETR {file}", local_file.write, 1024)
            except Exception as e:
                error_message = f"An error occurred while downloading files from the" \
                                f" FTPS server: {str(e)}"
                self.__obj_exception.raise_generic_exception(error_message)
                raise e

        def uploading_files_to_ftps(
                self, ftps_conn: FTP_TLS, upload_files: list, ftps_dir: str, local_path: str
        ) -> None:
            """
            This method uploads files to FTPS.

            Args:
                ftps_conn (FTPS Connection Object): The FTPS connection object.
                upload_files (list): List of files that need to be uploaded.
                ftps_dir (str): Directory to where the files need to be uploaded.
                local_path (str): Local path from where the files need to be uploaded.

            Examples:
                >> FileTransferUtils().FTPS().uploading_files_to_ftps(ftps_conn,
                 ['file1.pdf'], '/Inbox/', 'C:/Users/Project/')
            """
            try:
                ftps_conn.cwd(ftps_dir)
                for file in upload_files:
                    local_file_path = os.path.join(local_path, file)
                    with open(local_file_path, "rb") as local_file:
                        ftps_conn.storbinary(f"STOR {file}", local_file)
            except Exception as e:
                error_message = f"An error occurred while uploading files to the " \
                                f"FTPS server: {str(e)}"
                self.__obj_exception.raise_generic_exception(error_message)
                raise e

        def close_ftps_conn(self, ftps_conn: FTP_TLS) -> None:
            """
            This method closes the FTPS connection.

            Args:
                ftps_conn (FTPS Connection Object): The FTPS connection object.

            Examples:
                >> FileTransferUtils().FTPS().close_ftps_conn(ftps_conn)
            """
            try:
                ftps_conn.quit()
            except Exception as e:
                self.__obj_exception.raise_generic_exception(str(e))
                raise e

    class AWSS3:
        """
        Description:
            |  This class provides methods to interact with AWS S3.
        """

        def __init__(self):
            self.__obj_exception = CoreExceptions()
            self.logger_class = CoreLogger(name=__name__)
            self.logger = self.logger_class.get_logger()

        def open_aws_session(self, aws_access_key_id: str, aws_secret_access_key: str,
                             **kwargs) -> boto3.Session:
            """
            Creates an AWS session.

            Args:
                aws_access_key_id (str): Access key ID for AWS.
                aws_secret_access_key (str): Secret key for AWS.
                **kwargs: Optional parameters for session configuration.
                    - aws_session_token (str, optional): Session token for AWS (if applicable).
                    - region_name (str, optional): Name of the region to connect to.
                    - botocore_session (Botocore session, optional): Botocore session object.
                    - profile_name (str, optional): Profile name for AWS credentials.

            Returns:
                Session: The created AWS session object.

            Examples:
                >> aws_session = FileTransferUtils().AWSS3().
                open_aws_session('XXXXXX', 'XXXXX')
            """
            try:
                aws_session_token = kwargs.get("aws_session_token")
                region_name = kwargs.get("region_name")
                botocore_session = kwargs.get("botocore_session")
                profile_name = kwargs.get("profile_name")

                aws_session = FileTransferUtils().security.open_aws_session(
                    aws_access_key_id,
                    aws_secret_access_key,
                    aws_session_token,
                    region_name,
                    botocore_session,
                    profile_name,
                )

                return aws_session
            except Exception as e:
                error_message = f"An error occurred while opening the AWS session: {str(e)}"
                self.__obj_exception.raise_generic_exception(error_message)
                raise e

        def open_s3_client(self, session: boto3.Session) -> boto3.Session.client:
            """
            This method creates an S3 client object.

            Args:
                session (Session): The AWS session object.

            Returns:
                S3 Client: The created S3 client connection object.

            Examples:
                >> s3_client = FileTransferUtils().AWSS3().open_s3_client(aws_session)
            """
            try:
                s3_client = session.client("s3")
                return s3_client
            except Exception as e:
                self.__obj_exception.raise_generic_exception(str(e))
                raise e

        def s3_buckets_list(self, s3_client: boto3.Session.client) -> list:
            """
            This method retrieves a list of buckets under the AWS S3 connection.

            Args:
                s3_client (S3 Client): The AWS S3 client connection object.

            Returns:
                list: A list of bucket names under the AWS S3 connection.

            Examples:
                >> buckets = FileTransferUtils().AWSS3().s3_buckets_list(s3_client)
            """
            try:
                response = s3_client.list_buckets()
                buckets = [bucket["Name"] for bucket in response["Buckets"]]
                return buckets
            except Exception as e:
                self.__obj_exception.raise_generic_exception(str(e))
                raise e

        def read_objects_from_s3(self, client: boto3.Session.client, bucket_name: str,
                                 **kwargs) -> list:
            """
            Retrieves a list of objects or folders under the specified AWS S3 bucket.

            Args:
                client (S3.Client): The AWS S3 client connection object.
                bucket_name (str): The name of the bucket.
                **kwargs: Optional parameters for filtering objects:
                    - pstr_folder_prefix (str, optional): The prefix for folder names.
                    - pstr_file_suffix (str, optional): The suffix for file names.
                    - pstr_data_type (str, optional): Type of data to retrieve ('folder'
                     or 'objects'). Defaults to 'objects'.

            Returns:
                list: A list of folders or objects under the specified bucket.

            Examples:
                >> objects = FileTransferUtils().AWSS3().read_objects_from_s3(s3_client,
                'my_bucket', pstr_data_type='folder')
            """
            try:
                folder_prefix = kwargs.get("pstr_folder_prefix")
                file_suffix = kwargs.get("pstr_file_suffix", "")
                data_type = kwargs.get("pstr_data_type", "objects")

                if data_type == "folder":
                    _, list_folders = self.s3_folders_list(client, bucket_name,
                                                           folder_prefix=folder_prefix)
                    return list_folders
                _, list_objects, _ = self. \
                    read_content_from_s3(client, bucket_name,
                                         folder_prefix=folder_prefix,
                                         file_suffix=file_suffix)
                return list_objects
            except Exception as e:
                error_message = f"An error occurred while retrieving objects from S3: {str(e)}"
                self.__obj_exception.raise_generic_exception(error_message)
                raise e

        def s3_folders_list(self, s3_client: boto3.Session.client, bucket_name: str,
                            folder_prefix: str = None) -> tuple[int, list]:
            """
            Retrieves a list of folders under the specified AWS S3 bucket.

            Args:
                s3_client (S3.Client): The AWS S3 client connection object.
                bucket_name (str): The name of the bucket.
                folder_prefix (str, optional): An optional prefix to filter the folders.

            Returns:
                tuple: A tuple containing the count of folders and a list of folder names
                under the specified bucket.

            Examples:
                >> folders_count, folders = FileTransferUtils().AWSS3().
                s3_folders_list(s3_client, 'my_bucket', 'folder/')
            """
            try:
                response = s3_client.list_objects(
                    Bucket=bucket_name,
                    Prefix=folder_prefix,
                    Delimiter="/"
                )
                s3_folders_list = []
                for content in response.get("CommonPrefixes", []):
                    s3_folders_list.append(content.get("Prefix"))

                folders_count = len(s3_folders_list)
                return folders_count, s3_folders_list
            except Exception as e:
                error_message = f"An error occurred while retrieving S3 folders: {str(e)}"
                self.__obj_exception.raise_generic_exception(error_message)
                raise e

        def read_content_from_s3(self, s3_client: boto3.Session.client,
                                 bucket_name: str, folder_prefix: str = None,
                                 file_suffix: str = "") -> tuple[int, list, dict]:
            """
            Retrieves a list of objects under the specified AWS S3 bucket.

            Args:
                s3_client (S3.Client): The AWS S3 client connection object.
                bucket_name (str): The name of the bucket.
                folder_prefix (str, optional): An optional prefix to filter the objects.
                file_suffix (str, optional): An optional suffix to filter the objects.

            Returns:
                tuple: A tuple containing the count of files, a list of file names, and
                a dictionary of file details.

            Examples:
                >> file_count, objects, file_details = FileTransferUtils().
                AWSS3().read_content_from_s3(s3_client, 'my_bucket',
                 folder_prefix='folder/')
            """
            try:
                if folder_prefix:
                    response = s3_client.list_objects_v2(Bucket=bucket_name,
                                                         Prefix=folder_prefix)
                else:
                    response = s3_client.list_objects_v2(Bucket=bucket_name)

                s3_files = []
                dict_s3_file_details = {}

                for index, content in enumerate(response.get("Contents", []), start=1):
                    if content.get("Key").endswith(file_suffix):
                        s3_files.append(content.get("Key"))
                        dict_s3_file_details[f"file{index}"] = {
                            "file_name": content.get("Key"),
                            "last_modified": str(content.get("LastModified")),
                            "size": content.get("Size")
                        }

                file_count = len(s3_files)
                return file_count, s3_files, dict_s3_file_details
            except Exception as e:
                error_message = f"An error occurred while reading content from S3: {str(e)}"
                self.__obj_exception.raise_generic_exception(error_message)
                raise e

        def upload_file_into_s3(
                self,
                s3_client: boto3.Session.client,
                bucket_name: str,
                src_local_file_path: str,
                tgt_s3_file_path: str = None,
        ):
            """
            Uploads a file into the specified AWS S3 bucket.

            Args:
                s3_client (S3.Client): The AWS S3 client connection object.
                bucket_name (str): The name of the S3 bucket.
                src_local_file_path (str): Local source file path.
                tgt_s3_file_path (str, optional): Target file path in S3. If not provided,
                the local file name will be used.

            Returns:
                None

            Examples:
                >> FileTransferUtils().AWSS3().upload_file_into_s3(s3_client,
                 'my_bucket', 'local_file.txt')
            """
            try:
                if tgt_s3_file_path is None:
                    tgt_s3_file_path = os.path.basename(src_local_file_path)

                self.logger.info("Beginning file upload...")
                s3_client.upload_file(
                    src_local_file_path,
                    bucket_name,
                    tgt_s3_file_path,
                )
                self.logger.info("File %s successfully uploaded to S3 as %s."
                                 , src_local_file_path, tgt_s3_file_path)

            except Exception as e:
                error_message = f"An error occurred while uploading the file to S3: {str(e)}"
                self.__obj_exception.raise_generic_exception(error_message)
                raise e

        def download_file_from_s3(
                self,
                s3_client: boto3.Session.client,
                bucket_name: str,
                src_s3_file_path: str,
                tgt_local_file_path: str = None,
        ):
            """
            Downloads a file from the specified AWS S3 bucket.

            Args:
                s3_client (S3.Client): The AWS S3 client connection object.
                bucket_name (str): The name of the S3 bucket.
                src_s3_file_path (str): The source file path in S3.
                tgt_local_file_path (str, optional): Optional local target file path.
                If not provided, the file will be saved in the current working directory
                with the same name as in S3.

            Returns:
                None

            Examples:
                >> FileTransferUtils().AWSS3().download_file_from_s3(s3_client,
                'my_bucket', 's3_file.txt', 'local_file.txt')
            """
            try:
                if not bucket_name or not src_s3_file_path:
                    raise ValueError("Bucket name and source S3 file path must be provided.")

                if tgt_local_file_path is None:
                    tgt_local_file_path = os.path.join(os.getcwd(), os.path.basename(src_s3_file_path))

                self.logger.info("Starting download from bucket '%s', file '%s' to '%s'.",
                                 bucket_name, src_s3_file_path, tgt_local_file_path)

                s3_client.download_file(
                    bucket_name,
                    src_s3_file_path,
                    tgt_local_file_path,
                )

                self.logger.info("File '%s' successfully downloaded to '%s'.",
                                 src_s3_file_path, tgt_local_file_path)
            except ValueError as e:
                raise e
            except Exception as e:
                error_message = f"An error occurred while downloading the file from S3: {str(e)}"
                self.__obj_exception.raise_generic_exception(error_message)
                raise e

        def download_folder_from_s3(
                self,
                s3_client: boto3.Session.client,
                bucket_name: str,
                src_s3_folder_path: str,
                tgt_local_folder_path: str = None,
        ):
            """
            Downloads a folder and its contents from the specified AWS S3 bucket.

            Args:
                s3_client (S3.Client): The AWS S3 client connection object.
                bucket_name (str): The name of the S3 bucket.
                src_s3_folder_path (str): The source folder path in S3.
                tgt_local_folder_path (str, optional): Optional local target folder path.
                 If not provided, the folder will be created in the current
                 working directory.

            Returns:
                None
            """
            try:
                if not bucket_name:
                    raise ValueError("Bucket name must be provided.")
                if not src_s3_folder_path:
                    raise ValueError("Source S3 folder path must be provided.")

                if tgt_local_folder_path is None:
                    tgt_local_folder_path = os.path.join(
                        os.getcwd(), os.path.basename(os.path.normpath(src_s3_folder_path))
                    )

                if not src_s3_folder_path.endswith("/"):
                    src_s3_folder_path += "/"

                paginator = s3_client.get_paginator("list_objects_v2")

                for result in paginator.paginate(Bucket=bucket_name, Prefix=src_s3_folder_path):
                    for key in result.get("Contents", []):
                        rel_path = key["Key"][len(src_s3_folder_path):]
                        local_file_path = os.path.normpath(os.path.join(tgt_local_folder_path, rel_path))

                        if key["Key"].endswith("/"):
                            os.makedirs(local_file_path, exist_ok=True)
                            self.logger.info("Directory created: %s", local_file_path)
                        else:
                            local_file_dir = os.path.dirname(local_file_path)
                            os.makedirs(local_file_dir, exist_ok=True)
                            self.logger.info("Starting file download: %s", key["Key"])
                            s3_client.download_file(bucket_name, key["Key"], local_file_path)
                            self.logger.info("File %s successfully downloaded to %s.",
                                             key["Key"], local_file_path)
            except ValueError as ve:
                self.logger.error("Validation error: %s", str(ve))
                raise ve
            except Exception as e:
                error_message = f"An error occurred while downloading the folder from S3: {str(e)}"
                self.logger.error(error_message)
                self.__obj_exception.raise_generic_exception(error_message)
                raise e

        def upload_folder_into_s3(
                self,
                s3_client: boto3.Session.client,
                s3_bucket_name: str,
                src_local_folder_path: str,
                tgt_s3_folder_path: str = None,
        ):
            """
            Uploads a folder and its contents to the specified AWS S3 bucket.

            Args:
                s3_client (S3.Client): The AWS S3 client connection object.
                s3_bucket_name (str): The name of the S3 bucket.
                src_local_folder_path (str): Local source folder path.
                tgt_s3_folder_path (str, optional): Optional target folder path in
                S3. If not provided, the folder will be created in S3 with the same
                name as the local folder.

            Returns:
                None
            """
            try:
                if not os.path.exists(src_local_folder_path):
                    raise ValueError(f"The source folder '{src_local_folder_path}' does not exist.")
                if not os.path.isdir(src_local_folder_path):
                    raise ValueError(f"The path '{src_local_folder_path}' is not a directory.")

                if tgt_s3_folder_path is None:
                    tgt_s3_folder_path = pathlib.PurePath(src_local_folder_path).name

                if not tgt_s3_folder_path.endswith("/"):
                    tgt_s3_folder_path += "/"
                list_of_local_files = self.get_list_of_files_local(src_local_folder_path)

                for full_path in list_of_local_files:
                    source_full_path = os.path.normpath(full_path)
                    relative_path = os.path.relpath(source_full_path, src_local_folder_path)
                    target_full_path = os.path.join(tgt_s3_folder_path, relative_path).replace("\\", "/")
                    self.logger.info("Beginning file upload from %s to %s...", source_full_path, target_full_path)
                    self.upload_file_into_s3(
                        s3_client, s3_bucket_name, source_full_path, target_full_path
                    )
                    self.logger.info("Successfully transferred file %s to S3.", source_full_path)

            except ValueError as ve:
                raise ve
            except Exception as e:
                error_message = f"An error occurred while uploading the folder to S3: {str(e)}"
                self.__obj_exception.raise_generic_exception(error_message)
                raise e

        def get_list_of_files_local(self, local_dir_name: str) -> list:
            """
            Lists all the files in a given local directory, including files in subdirectories.

            Args:
                local_dir_name (str): Local directory name.

            Returns:
                list: A list of file paths under the given directory.

            Examples:
                >> files = FileTransferUtils().AWSS3().get_list_of_files_local('local_directory/')
            """
            try:
                if not os.path.exists(local_dir_name):
                    raise ValueError(f"The directory '{local_dir_name}' does not exist.")
                if not os.path.isdir(local_dir_name):
                    raise ValueError(f"The path '{local_dir_name}' is not a directory.")

                all_files = []
                for root, _, files in os.walk(local_dir_name):
                    for file in files:
                        all_files.append(os.path.join(root, file))

                return all_files
            except ValueError as ve:
                raise ve
            except Exception as e:
                error_message = f"An error occurred while listing files in the directory" \
                                f" '{local_dir_name}': {str(e)}"
                self.__obj_exception.raise_generic_exception(error_message)
                raise e
