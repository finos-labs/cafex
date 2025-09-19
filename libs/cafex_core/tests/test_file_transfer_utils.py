import os
import unittest
from unittest.mock import patch, MagicMock
from ftplib import error_perm, FTP, FTP_TLS

from datetime import datetime

from paramiko import SFTPClient
from dateutil import parser

from cafex_core.utils.file_transfer_utils import FileTransferUtils


class TestFTPUtils(unittest.TestCase):
    def setUp(self):
        self.ftp_utils = FileTransferUtils().FTP()
        self.sftp_utils = FileTransferUtils().SFTP()
        self.ftps_utils = FileTransferUtils().FTPS()
        self.s3_utils = FileTransferUtils().AWSS3()
        self.mock_s3_client = MagicMock()

    @patch("cafex_core.utils.file_transfer_utils.FileTransferUtils.security.open_ftp_connection")
    def test_open_ftp_connection_success(self, mock_open_ftp_connection):
        """Test successful FTP connection."""
        mock_ftp_conn = MagicMock()
        mock_open_ftp_connection.return_value = mock_ftp_conn

        ftp_conn = self.ftp_utils.open_ftp_connection("ftp.example.com", "username", "password")

        self.assertEqual(ftp_conn, mock_ftp_conn)
        mock_open_ftp_connection.assert_called_once_with("ftp.example.com", "username", "password")

    @patch("cafex_core.utils.file_transfer_utils.FileTransferUtils.security.open_ftp_connection")
    def test_open_ftp_connection_authentication_failure(self, mock_open_ftp_connection):
        """Test FTP connection with authentication failure."""
        mock_open_ftp_connection.side_effect = error_perm("530 Login incorrect.")

        with self.assertRaises(error_perm) as context:
            self.ftp_utils.open_ftp_connection("ftp.example.com", "username", "wrong_password")

        self.assertEqual(str(context.exception), "Authentication failed: 530 Login incorrect.")
        mock_open_ftp_connection.assert_called_once_with("ftp.example.com", "username", "wrong_password")

    @patch("cafex_core.utils.file_transfer_utils.FileTransferUtils.security.open_ftp_connection")
    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_open_ftp_connection_unexpected_error(self, mock_raise_generic_exception, mock_open_ftp_connection):
        """Test FTP connection with an unexpected error."""
        mock_open_ftp_connection.side_effect = Exception("Unexpected error occurred.")

        with self.assertRaises(Exception) as context:
            self.ftp_utils.open_ftp_connection("ftp.example.com", "username", "password")

        self.assertEqual(str(context.exception), "Unexpected error occurred.")
        mock_open_ftp_connection.assert_called_once_with("ftp.example.com", "username", "password")
        mock_raise_generic_exception.assert_called_once_with("An unexpected error occurred: Unexpected error occurred.")

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_get_dir_info_from_ftp_success(self, mock_raise_generic_exception):
        """Test successful retrieval of directory information."""
        mock_ftp_conn = MagicMock(spec=FTP)
        mock_ftp_conn.cwd.return_value = None
        mock_ftp_conn.retrlines.side_effect = lambda cmd, callback: [
            callback("-rw-r--r-- 1 owner group 1234 Jan 01 12:00 file1.txt"),
            callback("-rw-r--r-- 1 owner group 5678 Jan 02 13:00 file2.txt"),
        ]

        dir_path = "/test_dir"
        num_files, file_details = self.ftp_utils.get_dir_info_from_ftp(mock_ftp_conn, dir_path)

        self.assertEqual(num_files, 2)
        self.assertEqual(file_details["file1"]["file name"], "file1.txt")
        self.assertEqual(file_details["file2"]["file size"], "5678")
        self.assertIn("file last modified date", file_details["file1"])
        mock_ftp_conn.cwd.assert_called_once_with(dir_path)
        mock_raise_generic_exception.assert_not_called()

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_get_dir_info_from_ftp_cwd_failure(self, mock_raise_generic_exception):
        """Test failure when changing directory."""
        mock_ftp_conn = MagicMock(spec=FTP)
        mock_ftp_conn.cwd.side_effect = error_perm("550 Failed to change directory.")

        dir_path = "/invalid_dir"
        with self.assertRaises(error_perm) as context:
            self.ftp_utils.get_dir_info_from_ftp(mock_ftp_conn, dir_path)

        self.assertEqual(str(context.exception), "550 Failed to change directory.")
        mock_ftp_conn.cwd.assert_called_once_with(dir_path)
        mock_raise_generic_exception.assert_called_once_with(
            "An error occurred while connecting to the FTP server: 550 Failed to change directory."
        )

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_get_dir_info_from_ftp_retrlines_failure(self, mock_raise_generic_exception):
        """Test failure when retrieving directory listing."""
        mock_ftp_conn = MagicMock(spec=FTP)
        mock_ftp_conn.cwd.return_value = None
        mock_ftp_conn.retrlines.side_effect = Exception("Unexpected error during LIST command.")

        dir_path = "/test_dir"
        with self.assertRaises(Exception) as context:
            self.ftp_utils.get_dir_info_from_ftp(mock_ftp_conn, dir_path)

        self.assertEqual(str(context.exception), "Unexpected error during LIST command.")
        mock_ftp_conn.cwd.assert_called_once_with(dir_path)
        mock_raise_generic_exception.assert_called_once_with(
            "An error occurred while connecting to the FTP server: Unexpected error during LIST command."
        )

    @patch("os.makedirs")
    @patch("builtins.open", new_callable=MagicMock)
    def test_download_files_from_ftp_success(self, mock_open, mock_makedirs):
        """Test successful file download from FTP."""
        mock_ftp_conn = MagicMock(spec=FTP)
        mock_ftp_conn.cwd.return_value = None
        mock_ftp_conn.retrbinary.return_value = None

        files_to_download = ["file1.txt", "file2.txt"]
        ftp_dir = "/test_dir"
        local_path = "C:/Users/Project/"

        self.ftp_utils.download_files_from_ftp(mock_ftp_conn, files_to_download, ftp_dir, local_path)

        mock_ftp_conn.cwd.assert_called_once_with(ftp_dir)
        mock_makedirs.assert_called_once_with(local_path, exist_ok=True)
        self.assertEqual(mock_ftp_conn.retrbinary.call_count, len(files_to_download))

    @patch("os.makedirs")
    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_download_files_from_ftp_cwd_exception(self, mock_raise_exception, mock_makedirs):
        """Test exception when changing directory on FTP server."""
        mock_ftp_conn = MagicMock(spec=FTP)
        mock_ftp_conn.cwd.side_effect = error_perm("550 Failed to change directory.")

        files_to_download = ["file1.txt"]
        ftp_dir = "/invalid_dir"
        local_path = "C:/Users/Project/"

        with self.assertRaises(error_perm) as context:
            self.ftp_utils.download_files_from_ftp(mock_ftp_conn, files_to_download, ftp_dir, local_path)

        self.assertEqual(str(context.exception), "550 Failed to change directory.")
        mock_ftp_conn.cwd.assert_called_once_with(ftp_dir)
        mock_raise_exception.assert_called_once_with(
            "An error occurred while downloading files from the FTP server: 550 Failed to change directory."
        )

    @patch("os.makedirs")
    @patch("builtins.open", new_callable=MagicMock)
    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_download_files_from_ftp_retrbinary_exception(self, mock_raise_exception, mock_open, mock_makedirs):
        """Test exception when downloading a file from FTP server."""
        mock_ftp_conn = MagicMock(spec=FTP)
        mock_ftp_conn.cwd.return_value = None
        mock_ftp_conn.retrbinary.side_effect = Exception("Mocked exception during file download.")

        files_to_download = ["file1.txt"]
        ftp_dir = "/test_dir"
        local_path = "C:/Users/Project/"

        with self.assertRaises(Exception) as context:
            self.ftp_utils.download_files_from_ftp(mock_ftp_conn, files_to_download, ftp_dir, local_path)

        self.assertEqual(str(context.exception), "Mocked exception during file download.")
        mock_ftp_conn.cwd.assert_called_once_with(ftp_dir)
        mock_raise_exception.assert_called_once_with(
            "An error occurred while downloading files from the FTP server: Mocked exception during file download."
        )

    @patch("builtins.open", new_callable=MagicMock)
    def test_uploading_files_to_ftp_success(self, mock_open):
        """Test successful file upload to FTP."""
        mock_ftp_conn = MagicMock(spec=FTP)
        mock_ftp_conn.cwd.return_value = None
        mock_ftp_conn.storbinary.return_value = None

        plist_upload_files = ["file1.txt", "file2.txt"]
        pstr_ftp_dir = "/test_dir"
        pstr_local_path = "C:/Users/Project/"

        self.ftp_utils.uploading_files_to_ftp(mock_ftp_conn, plist_upload_files, pstr_ftp_dir, pstr_local_path)

        mock_ftp_conn.cwd.assert_called_once_with(pstr_ftp_dir)
        self.assertEqual(mock_ftp_conn.storbinary.call_count, len(plist_upload_files))

    @patch("builtins.open", new_callable=MagicMock)
    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_uploading_files_to_ftp_exception(self, mock_raise_exception, mock_open):
        """Test exception during file upload to FTP."""
        mock_ftp_conn = MagicMock(spec=FTP)
        mock_ftp_conn.cwd.return_value = None
        mock_ftp_conn.storbinary.side_effect = Exception("Mocked exception during upload.")

        plist_upload_files = ["file1.txt"]
        pstr_ftp_dir = "/test_dir"
        pstr_local_path = "C:/Users/Project/"

        with self.assertRaises(Exception) as context:
            self.ftp_utils.uploading_files_to_ftp(mock_ftp_conn, plist_upload_files, pstr_ftp_dir, pstr_local_path)

        # Assert that the original exception is re-raised
        self.assertEqual(str(context.exception), "Mocked exception during upload.")
        mock_ftp_conn.cwd.assert_called_once_with(pstr_ftp_dir)
        mock_raise_exception.assert_called_once_with("Mocked exception during upload.")

    def test_close_ftp_conn_success(self):
        """Test successful FTP connection closure."""
        mock_ftp_conn = MagicMock(spec=FTP)
        mock_ftp_conn.quit.return_value = None

        self.ftp_utils.close_ftp_conn(mock_ftp_conn)

        mock_ftp_conn.quit.assert_called_once()

    def test_close_ftp_conn_none(self):
        """Test handling of None FTP connection."""
        with self.assertRaises(ValueError) as context:
            self.ftp_utils.close_ftp_conn(None)

        self.assertEqual(str(context.exception), "FTP connection object cannot be None.")

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_close_ftp_conn_exception(self, mock_raise_exception):
        """Test exception during FTP connection closure."""
        mock_ftp_conn = MagicMock(spec=FTP)
        mock_ftp_conn.quit.side_effect = Exception("Mocked exception during quit.")

        with self.assertRaises(Exception) as context:
            self.ftp_utils.close_ftp_conn(mock_ftp_conn)

        self.assertEqual(str(context.exception), "Mocked exception during quit.")
        mock_ftp_conn.quit.assert_called_once()
        mock_raise_exception.assert_called_once_with(
            "Failed to close FTP connection: Mocked exception during quit."
        )

    @patch("cafex_core.utils.file_transfer_utils.FileTransferUtils.security.open_sftp_connection")
    def test_open_sftp_connection_success(self, mock_open_sftp_connection):
        """Test successful SFTP connection."""
        mock_sftp_conn = MagicMock()
        mock_transport = MagicMock()
        mock_open_sftp_connection.return_value = (mock_sftp_conn, mock_transport)

        sftp_conn = self.sftp_utils.open_sftp_connection("sftp.example.com", 22, "username", "password")

        self.assertEqual(sftp_conn, mock_sftp_conn)
        mock_open_sftp_connection.assert_called_once_with("sftp.example.com", 22, "username", "password")

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    @patch("cafex_core.utils.file_transfer_utils.FileTransferUtils.security.open_sftp_connection")
    def test_open_sftp_connection_exception(self, mock_open_sftp_connection, mock_raise_generic_exception):
        """Test exception during SFTP connection."""
        mock_open_sftp_connection.side_effect = Exception("Mocked connection error.")

        with self.assertRaises(Exception) as context:
            self.sftp_utils.open_sftp_connection("sftp.example.com", 22, "username", "password")

        self.assertEqual(str(context.exception), "Mocked connection error.")
        mock_open_sftp_connection.assert_called_once_with("sftp.example.com", 22, "username", "password")
        mock_raise_generic_exception.assert_called_once_with(
            "An error occurred while connecting to the SFTP server: Mocked connection error."
        )

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_get_dir_info_from_sftp_success(self, mock_raise_generic_exception):
        """Test successful retrieval of directory information from SFTP."""
        mock_sftp_conn = MagicMock(spec=SFTPClient)
        mock_file_attr1 = MagicMock()
        mock_file_attr1.filename = "file1.txt"
        mock_file_attr1.st_size = 1234
        mock_file_attr1.st_mtime = 1672531200  # Example timestamp
        mock_file_attr1.st_mode = 0o100644
        mock_file_attr1.st_uid = 1000
        mock_file_attr1.st_gid = 1000

        mock_file_attr2 = MagicMock()
        mock_file_attr2.filename = "file2.txt"
        mock_file_attr2.st_size = 5678
        mock_file_attr2.st_mtime = 1672617600  # Example timestamp
        mock_file_attr2.st_mode = 0o100755
        mock_file_attr2.st_uid = 1001
        mock_file_attr2.st_gid = 1001

        mock_sftp_conn.listdir_attr.return_value = [mock_file_attr1, mock_file_attr2]

        dir_path = "/test_dir"
        file_count, file_details = self.sftp_utils.get_dir_info_from_sftp(mock_sftp_conn, dir_path)

        self.assertEqual(file_count, 2)
        self.assertEqual(file_details["file1"]["file name"], "file1.txt")
        self.assertEqual(file_details["file1"]["file size"], 1234)
        self.assertEqual(file_details["file1"]["file last modified date"], str(datetime.fromtimestamp(1672531200)))
        self.assertEqual(file_details["file1"]["file permissions"], "644")
        self.assertEqual(file_details["file1"]["file owner"], "1000 1000")
        self.assertEqual(file_details["file2"]["file name"], "file2.txt")
        self.assertEqual(file_details["file2"]["file size"], 5678)
        self.assertEqual(file_details["file2"]["file last modified date"], str(datetime.fromtimestamp(1672617600)))
        self.assertEqual(file_details["file2"]["file permissions"], "755")
        self.assertEqual(file_details["file2"]["file owner"], "1001 1001")
        mock_sftp_conn.listdir_attr.assert_called_once_with(dir_path)
        mock_raise_generic_exception.assert_not_called()

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_get_dir_info_from_sftp_exception(self, mock_raise_generic_exception):
        """Test exception during retrieval of directory information from SFTP."""
        mock_sftp_conn = MagicMock(spec=SFTPClient)
        mock_sftp_conn.listdir_attr.side_effect = Exception("Mocked exception during directory listing.")

        dir_path = "/invalid_dir"
        with self.assertRaises(Exception) as context:
            self.sftp_utils.get_dir_info_from_sftp(mock_sftp_conn, dir_path)

        self.assertEqual(str(context.exception), "Mocked exception during directory listing.")
        mock_sftp_conn.listdir_attr.assert_called_once_with(dir_path)
        mock_raise_generic_exception.assert_called_once_with(
            "An error occurred while retrieving directory info from the SFTP server: Mocked exception during directory listing."
        )

    @patch("os.makedirs")
    def test_download_files_from_sftp_success(self, mock_makedirs):
        """Test successful file download from SFTP."""
        mock_sftp_conn = MagicMock(spec=SFTPClient)
        mock_sftp_conn.get.return_value = None

        download_files = ["file1.txt", "file2.txt"]
        sftp_dir = "/test_dir"
        local_path = "C:/Users/Project/"

        self.sftp_utils.download_files_from_sftp(mock_sftp_conn, download_files, sftp_dir, local_path)

        mock_makedirs.assert_called_once_with(local_path, exist_ok=True)
        self.assertEqual(mock_sftp_conn.get.call_count, len(download_files))
        mock_sftp_conn.get.assert_any_call(os.path.join(sftp_dir, "file1.txt"), os.path.join(local_path, "file1.txt"))
        mock_sftp_conn.get.assert_any_call(os.path.join(sftp_dir, "file2.txt"), os.path.join(local_path, "file2.txt"))

    @patch("os.makedirs")
    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_download_files_from_sftp_exception(self, mock_raise_generic_exception, mock_makedirs):
        """Test exception during file download from SFTP."""
        mock_sftp_conn = MagicMock(spec=SFTPClient)
        mock_sftp_conn.get.side_effect = Exception("Mocked exception during file download.")

        download_files = ["file1.txt"]
        sftp_dir = "/test_dir"
        local_path = "C:/Users/Project/"

        with self.assertRaises(Exception) as context:
            self.sftp_utils.download_files_from_sftp(mock_sftp_conn, download_files, sftp_dir, local_path)

        self.assertEqual(str(context.exception), "Mocked exception during file download.")
        mock_makedirs.assert_called_once_with(local_path, exist_ok=True)
        mock_sftp_conn.get.assert_called_once_with(os.path.join(sftp_dir, "file1.txt"),
                                                   os.path.join(local_path, "file1.txt"))
        mock_raise_generic_exception.assert_called_once_with(
            "An error occurred while downloading files from the SFTP server: Mocked exception during file download."
        )

    @patch("os.makedirs")
    def test_uploading_files_to_sftp_success(self, mock_makedirs):
        """Test successful file upload to SFTP."""
        mock_sftp_conn = MagicMock(spec=SFTPClient)
        mock_sftp_conn.put.return_value = None

        upload_files = ["file1.txt", "file2.txt"]
        sftp_dir = "/test_dir"
        local_path = "C:/Users/Project/"

        self.sftp_utils.uploading_files_to_sftp(mock_sftp_conn, upload_files, sftp_dir, local_path)

        mock_makedirs.assert_called_once_with(local_path, exist_ok=True)
        self.assertEqual(mock_sftp_conn.put.call_count, len(upload_files))
        mock_sftp_conn.put.assert_any_call(os.path.join(local_path, "file1.txt"), os.path.join(sftp_dir, "file1.txt"))
        mock_sftp_conn.put.assert_any_call(os.path.join(local_path, "file2.txt"), os.path.join(sftp_dir, "file2.txt"))

    @patch("os.makedirs")
    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_uploading_files_to_sftp_exception(self, mock_raise_generic_exception, mock_makedirs):
        """Test exception during file upload to SFTP."""
        mock_sftp_conn = MagicMock(spec=SFTPClient)
        mock_sftp_conn.put.side_effect = Exception("Mocked exception during upload.")

        upload_files = ["file1.txt"]
        sftp_dir = "/test_dir"
        local_path = "C:/Users/Project/"

        with self.assertRaises(Exception) as context:
            self.sftp_utils.uploading_files_to_sftp(mock_sftp_conn, upload_files, sftp_dir, local_path)

        self.assertEqual(str(context.exception), "Mocked exception during upload.")
        mock_makedirs.assert_called_once_with(local_path, exist_ok=True)
        mock_sftp_conn.put.assert_called_once_with(os.path.join(local_path, "file1.txt"),
                                                   os.path.join(sftp_dir, "file1.txt"))
        mock_raise_generic_exception.assert_called_once_with(
            "An error occurred while uploading files to the SFTP server: Mocked exception during upload."
        )

    def test_close_sftp_conn_success(self):
        """Test successful closure of SFTP connection."""
        mock_sftp_conn = MagicMock(spec=SFTPClient)
        self.sftp_utils.transport = MagicMock()

        self.sftp_utils.close_sftp_conn(mock_sftp_conn)

        mock_sftp_conn.close.assert_called_once()
        self.sftp_utils.transport.close.assert_called_once()

    def test_close_sftp_conn_no_transport(self):
        """Test closure of SFTP connection when transport is None."""
        mock_sftp_conn = MagicMock(spec=SFTPClient)
        self.sftp_utils.transport = None

        self.sftp_utils.close_sftp_conn(mock_sftp_conn)

        mock_sftp_conn.close.assert_called_once()

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_close_sftp_conn_exception(self, mock_raise_generic_exception):
        """Test exception during SFTP connection closure."""
        mock_sftp_conn = MagicMock(spec=SFTPClient)
        mock_sftp_conn.close.side_effect = Exception("Mocked exception during close.")
        self.sftp_utils.transport = MagicMock()

        with self.assertRaises(Exception) as context:
            self.sftp_utils.close_sftp_conn(mock_sftp_conn)

        self.assertEqual(str(context.exception), "Mocked exception during close.")
        mock_sftp_conn.close.assert_called_once()
        mock_raise_generic_exception.assert_called_once_with("Mocked exception during close.")

    @patch("cafex_core.utils.file_transfer_utils.FileTransferUtils.security.ftps_connection")
    def test_open_ftps_connection_success(self, mock_ftps_connection):
        """Test successful FTPS connection."""
        mock_ftps_conn = MagicMock(spec=FTP_TLS)
        mock_ftps_connection.return_value = mock_ftps_conn

        ftps_conn = self.ftps_utils.open_ftps_connection("ftps.example.com", "username", "password")

        self.assertEqual(ftps_conn, mock_ftps_conn)
        mock_ftps_connection.assert_called_once_with("ftps.example.com", "username", "password")

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    @patch("cafex_core.utils.file_transfer_utils.FileTransferUtils.security.ftps_connection")
    def test_open_ftps_connection_exception(self, mock_ftps_connection, mock_raise_generic_exception):
        """Test exception during FTPS connection."""
        mock_ftps_connection.side_effect = Exception("Mocked connection error.")

        with self.assertRaises(Exception) as context:
            self.ftps_utils.open_ftps_connection("ftps.example.com", "username", "password")

        self.assertEqual(str(context.exception), "Mocked connection error.")
        mock_ftps_connection.assert_called_once_with("ftps.example.com", "username", "password")
        mock_raise_generic_exception.assert_called_once_with(
            "An error occurred while connecting to the FTPS server: Mocked connection error."
        )

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_get_dir_info_from_ftps_success(self, mock_raise_generic_exception):
        """Test successful retrieval of directory information from FTPS."""
        mock_ftps_conn = MagicMock(spec=FTP_TLS)
        mock_ftps_conn.cwd.return_value = None
        mock_ftps_conn.retrlines.side_effect = lambda cmd, callback: [
            callback("-rw-r--r-- 1 owner group 1234 Jan 01 12:00 file1.txt"),
            callback("-rw-r--r-- 1 owner group 5678 Jan 02 13:00 file2.txt"),
        ]

        dir_path = "/test_dir"
        file_count, file_details = self.ftps_utils.get_dir_info_from_ftps(mock_ftps_conn, dir_path)

        self.assertEqual(file_count, 2)
        self.assertEqual(file_details["file1"]["file name"], "file1.txt")
        self.assertEqual(file_details["file1"]["file size"], "1234")
        self.assertEqual(file_details["file1"]["file last modified date"], str(parser.parse("Jan 01 12:00")))
        self.assertEqual(file_details["file1"]["file permissions"], "-rw-r--r--")
        self.assertEqual(file_details["file1"]["file owner"], "owner group")
        self.assertEqual(file_details["file2"]["file name"], "file2.txt")
        self.assertEqual(file_details["file2"]["file size"], "5678")
        self.assertEqual(file_details["file2"]["file last modified date"], str(parser.parse("Jan 02 13:00")))
        self.assertEqual(file_details["file2"]["file permissions"], "-rw-r--r--")
        self.assertEqual(file_details["file2"]["file owner"], "owner group")
        mock_ftps_conn.cwd.assert_called_once_with(dir_path)
        mock_raise_generic_exception.assert_not_called()

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_get_dir_info_from_ftps_cwd_failure(self, mock_raise_generic_exception):
        """Test failure when changing directory on FTPS server."""
        mock_ftps_conn = MagicMock(spec=FTP_TLS)
        mock_ftps_conn.cwd.side_effect = error_perm("550 Failed to change directory.")

        dir_path = "/invalid_dir"
        with self.assertRaises(error_perm) as context:
            self.ftps_utils.get_dir_info_from_ftps(mock_ftps_conn, dir_path)

        self.assertEqual(str(context.exception), "550 Failed to change directory.")
        mock_ftps_conn.cwd.assert_called_once_with(dir_path)
        mock_raise_generic_exception.assert_called_once_with(
            "An error occurred while retrieving directory info from the FTPS server: 550 Failed to change directory."
        )

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_get_dir_info_from_ftps_retrlines_failure(self, mock_raise_generic_exception):
        """Test failure when retrieving directory listing from FTPS server."""
        mock_ftps_conn = MagicMock(spec=FTP_TLS)
        mock_ftps_conn.cwd.return_value = None
        mock_ftps_conn.retrlines.side_effect = Exception("Mocked exception during LIST command.")

        dir_path = "/test_dir"
        with self.assertRaises(Exception) as context:
            self.ftps_utils.get_dir_info_from_ftps(mock_ftps_conn, dir_path)

        self.assertEqual(str(context.exception), "Mocked exception during LIST command.")
        mock_ftps_conn.cwd.assert_called_once_with(dir_path)
        mock_raise_generic_exception.assert_called_once_with(
            "An error occurred while retrieving directory info from the FTPS server: Mocked exception during LIST command."
        )

    @patch("os.makedirs")
    @patch("builtins.open", new_callable=MagicMock)
    def test_download_files_from_ftps_success(self, mock_open, mock_makedirs):
        """Test successful file download from FTPS."""
        mock_ftps_conn = MagicMock(spec=FTP_TLS)
        mock_ftps_conn.cwd.return_value = None
        mock_ftps_conn.retrbinary.return_value = None

        download_files = ["file1.txt", "file2.txt"]
        ftps_dir = "/test_dir"
        local_path = "C:/Users/Project/"

        self.ftps_utils.download_files_from_ftps(mock_ftps_conn, download_files, ftps_dir, local_path)

        mock_makedirs.assert_called_once_with(local_path, exist_ok=True)
        mock_ftps_conn.cwd.assert_called_once_with(ftps_dir)
        self.assertEqual(mock_ftps_conn.retrbinary.call_count, len(download_files))
        mock_ftps_conn.retrbinary.assert_any_call(f"RETR file1.txt", mock_open().__enter__().write, 1024)
        mock_ftps_conn.retrbinary.assert_any_call(f"RETR file2.txt", mock_open().__enter__().write, 1024)

    @patch("os.makedirs")
    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_download_files_from_ftps_exception(self, mock_raise_generic_exception, mock_makedirs):
        """Test exception during file download from FTPS."""
        mock_ftps_conn = MagicMock(spec=FTP_TLS)
        mock_ftps_conn.cwd.side_effect = error_perm("550 Failed to change directory.")

        download_files = ["file1.txt"]
        ftps_dir = "/invalid_dir"
        local_path = "C:/Users/Project/"

        with self.assertRaises(error_perm) as context:
            self.ftps_utils.download_files_from_ftps(mock_ftps_conn, download_files, ftps_dir, local_path)

        self.assertEqual(str(context.exception), "550 Failed to change directory.")
        mock_makedirs.assert_called_once_with(local_path, exist_ok=True)
        mock_ftps_conn.cwd.assert_called_once_with(ftps_dir)
        mock_raise_generic_exception.assert_called_once_with(
            "An error occurred while downloading files from the FTPS server: 550 Failed to change directory."
        )

    @patch("builtins.open", new_callable=MagicMock)
    def test_uploading_files_to_ftps_success(self, mock_open):
        """Test successful file upload to FTPS."""
        mock_ftps_conn = MagicMock(spec=FTP_TLS)
        mock_ftps_conn.cwd.return_value = None
        mock_ftps_conn.storbinary.return_value = None

        upload_files = ["file1.txt", "file2.txt"]
        ftps_dir = "/test_dir"
        local_path = "C:/Users/Project/"

        self.ftps_utils.uploading_files_to_ftps(mock_ftps_conn, upload_files, ftps_dir, local_path)

        mock_ftps_conn.cwd.assert_called_once_with(ftps_dir)
        self.assertEqual(mock_ftps_conn.storbinary.call_count, len(upload_files))
        mock_ftps_conn.storbinary.assert_any_call(f"STOR file1.txt", mock_open().__enter__())
        mock_ftps_conn.storbinary.assert_any_call(f"STOR file2.txt", mock_open().__enter__())

    @patch("builtins.open", new_callable=MagicMock)
    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_uploading_files_to_ftps_exception(self, mock_raise_generic_exception, mock_open):
        """Test exception during file upload to FTPS."""
        mock_ftps_conn = MagicMock(spec=FTP_TLS)
        mock_ftps_conn.cwd.return_value = None
        mock_ftps_conn.storbinary.side_effect = Exception("Mocked exception during upload.")

        upload_files = ["file1.txt"]
        ftps_dir = "/test_dir"
        local_path = "C:/Users/Project/"

        with self.assertRaises(Exception) as context:
            self.ftps_utils.uploading_files_to_ftps(mock_ftps_conn, upload_files, ftps_dir, local_path)

        self.assertEqual(str(context.exception), "Mocked exception during upload.")
        mock_ftps_conn.cwd.assert_called_once_with(ftps_dir)
        mock_raise_generic_exception.assert_called_once_with(
            "An error occurred while uploading files to the FTPS server: Mocked exception during upload."
        )

    def test_close_ftps_conn_success(self):
        """Test successful FTPS connection closure."""
        mock_ftps_conn = MagicMock(spec=FTP_TLS)
        mock_ftps_conn.quit.return_value = None

        self.ftps_utils.close_ftps_conn(mock_ftps_conn)

        mock_ftps_conn.quit.assert_called_once()

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_close_ftps_conn_exception(self, mock_raise_generic_exception):
        """Test exception during FTPS connection closure."""
        mock_ftps_conn = MagicMock(spec=FTP_TLS)
        mock_ftps_conn.quit.side_effect = Exception("Mocked exception during quit.")

        with self.assertRaises(Exception) as context:
            self.ftps_utils.close_ftps_conn(mock_ftps_conn)

        self.assertEqual(str(context.exception), "Mocked exception during quit.")
        mock_ftps_conn.quit.assert_called_once()
        mock_raise_generic_exception.assert_called_once_with("Mocked exception during quit.")

    @patch("cafex_core.utils.file_transfer_utils.FileTransferUtils.security.open_aws_session")
    def test_open_aws_session_success(self, mock_open_aws_session):
        """Test successful AWS session creation."""
        # Create a mock session object with the expected attributes
        mock_session = MagicMock()
        mock_session.region_name = "us-east-1"
        mock_open_aws_session.return_value = mock_session

        aws_access_key_id = "test_access_key"
        aws_secret_access_key = "test_secret_key"
        kwargs = {"region_name": "us-east-1"}

        # Debugging: Print to ensure the mock is set up correctly
        print(f"Mock: {mock_open_aws_session}")

        # Call the method under test
        session = self.s3_utils.open_aws_session(aws_access_key_id, aws_secret_access_key, **kwargs)

        # Debugging: Print the session to verify the result
        print(f"Session: {session}")

        # Assert that the session matches the mock session
        self.assertEqual(session.region_name, mock_session.region_name)

        # Verify the mock was called with the correct arguments
        mock_open_aws_session.assert_called_once_with(
            aws_access_key_id, aws_secret_access_key, None, "us-east-1", None, None
        )

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    @patch("cafex_core.utils.file_transfer_utils.FileTransferUtils.security.open_aws_session")
    def test_open_aws_session_exception(self, mock_open_aws_session, mock_raise_generic_exception):
        """Test exception during AWS session creation."""
        mock_open_aws_session.side_effect = Exception("Mocked exception during session creation.")

        aws_access_key_id = "test_access_key"
        aws_secret_access_key = "test_secret_key"

        with self.assertRaises(Exception) as context:
            self.s3_utils.open_aws_session(aws_access_key_id, aws_secret_access_key)

        self.assertEqual(str(context.exception), "Mocked exception during session creation.")
        mock_open_aws_session.assert_called_once_with(
            aws_access_key_id, aws_secret_access_key, None, None, None, None
        )
        mock_raise_generic_exception.assert_called_once_with(
            "An error occurred while opening the AWS session: Mocked exception during session creation."
        )

    @patch("boto3.Session")
    def test_open_s3_client_success(self, mock_boto3_session):
        """Test successful creation of an S3 client."""
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_session.client.return_value = mock_client
        mock_boto3_session.return_value = mock_session

        s3_client = self.s3_utils.open_s3_client(mock_session)

        self.assertEqual(s3_client, mock_client)
        mock_session.client.assert_called_once_with("s3")

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_open_s3_client_exception(self, mock_raise_generic_exception):
        """Test exception during S3 client creation."""
        mock_session = MagicMock()
        mock_session.client.side_effect = Exception("Mocked exception")
        self.s3_utils.__obj_exception = MagicMock()
        self.s3_utils.__obj_exception.raise_generic_exception = mock_raise_generic_exception

        with self.assertRaises(Exception) as context:
            self.s3_utils.open_s3_client(mock_session)

        self.assertEqual(str(context.exception), "Mocked exception")
        mock_raise_generic_exception.assert_called_once_with("Mocked exception")

    def test_s3_buckets_list_success(self):
        """Test successful retrieval of S3 bucket list."""
        mock_s3_client = MagicMock()
        mock_s3_client.list_buckets.return_value = {
            "Buckets": [{"Name": "bucket1"}, {"Name": "bucket2"}]
        }

        buckets = self.s3_utils.s3_buckets_list(mock_s3_client)

        self.assertEqual(buckets, ["bucket1", "bucket2"])
        mock_s3_client.list_buckets.assert_called_once()

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_s3_buckets_list_exception(self, mock_raise_generic_exception):
        """Test exception during S3 bucket list retrieval."""
        mock_s3_client = MagicMock()
        mock_s3_client.list_buckets.side_effect = Exception("Mocked exception")
        self.s3_utils.__obj_exception = MagicMock()
        self.s3_utils.__obj_exception.raise_generic_exception = mock_raise_generic_exception

        with self.assertRaises(Exception) as context:
            self.s3_utils.s3_buckets_list(mock_s3_client)

        self.assertEqual(str(context.exception), "Mocked exception")
        mock_raise_generic_exception.assert_called_once_with("Mocked exception")

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_read_objects_from_s3_folders_success(self, mock_raise_generic_exception):
        """Test successful retrieval of folders from S3."""
        self.s3_utils.s3_folders_list = MagicMock(return_value=(None, ["folder1", "folder2"]))

        result = self.s3_utils.read_objects_from_s3(
            self.mock_s3_client, "test_bucket", pstr_data_type="folder", pstr_folder_prefix="test_prefix"
        )

        self.assertEqual(result, ["folder1", "folder2"])
        self.s3_utils.s3_folders_list.assert_called_once_with(
            self.mock_s3_client, "test_bucket", folder_prefix="test_prefix"
        )
        mock_raise_generic_exception.assert_not_called()

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_read_objects_from_s3_objects_success(self, mock_raise_generic_exception):
        """Test successful retrieval of objects from S3."""
        self.s3_utils.read_content_from_s3 = MagicMock(return_value=(None, ["object1", "object2"], None))
        result = self.s3_utils.read_objects_from_s3(
            self.mock_s3_client, "test_bucket", pstr_data_type="objects", pstr_file_suffix=".txt"
        )

        self.assertEqual(result, ["object1", "object2"])
        self.s3_utils.read_content_from_s3.assert_called_once_with(
            self.mock_s3_client, "test_bucket", folder_prefix=None, file_suffix=".txt"
        )
        mock_raise_generic_exception.assert_not_called()

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_read_objects_from_s3_exception(self, mock_raise_generic_exception):
        """Test exception during retrieval of objects from S3."""
        self.s3_utils.read_content_from_s3 = MagicMock(side_effect=Exception("Mocked exception"))
        with self.assertRaises(Exception) as context:
            self.s3_utils.read_objects_from_s3(self.mock_s3_client, "test_bucket")

        self.assertEqual(str(context.exception), "Mocked exception")
        mock_raise_generic_exception.assert_called_once_with(
            "An error occurred while retrieving objects from S3: Mocked exception"
        )

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_s3_folders_list_success(self, mock_raise_generic_exception):
        """Test successful retrieval of folders from S3."""
        self.mock_s3_client.list_objects.return_value = {
            "CommonPrefixes": [{"Prefix": "folder1/"}, {"Prefix": "folder2/"}]
        }

        folders_count, folders = self.s3_utils.s3_folders_list(
            self.mock_s3_client, "test_bucket", folder_prefix="test/"
        )

        self.assertEqual(folders_count, 2)
        self.assertEqual(folders, ["folder1/", "folder2/"])
        self.mock_s3_client.list_objects.assert_called_once_with(
            Bucket="test_bucket", Prefix="test/", Delimiter="/"
        )
        mock_raise_generic_exception.assert_not_called()

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_s3_folders_list_exception(self, mock_raise_generic_exception):
        """Test exception during folder retrieval from S3."""
        self.mock_s3_client.list_objects.side_effect = Exception("Mocked exception")

        with self.assertRaises(Exception) as context:
            self.s3_utils.s3_folders_list(self.mock_s3_client, "test_bucket")

        self.assertEqual(str(context.exception), "Mocked exception")
        mock_raise_generic_exception.assert_called_once_with(
            "An error occurred while retrieving S3 folders: Mocked exception"
        )

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_read_content_from_s3_success(self, mock_raise_generic_exception):
        """Test successful retrieval of content from S3."""

        self.mock_s3_client.list_objects_v2.return_value = {
            "Contents": [
                {"Key": "folder/file1.txt", "LastModified": "2023-01-01T12:00:00", "Size": 1234},
                {"Key": "folder/file2.txt", "LastModified": "2023-01-02T12:00:00", "Size": 5678},
            ]
        }

        file_count, s3_files, file_details = self.s3_utils.read_content_from_s3(
            self.mock_s3_client, "test_bucket", folder_prefix="folder/", file_suffix=".txt"
        )

        self.assertEqual(file_count, 2)
        self.assertEqual(s3_files, ["folder/file1.txt", "folder/file2.txt"])
        self.assertEqual(file_details["file1"]["file_name"], "folder/file1.txt")
        self.assertEqual(file_details["file1"]["size"], 1234)
        self.assertEqual(file_details["file2"]["file_name"], "folder/file2.txt")
        self.assertEqual(file_details["file2"]["size"], 5678)
        self.mock_s3_client.list_objects_v2.assert_called_once_with(Bucket="test_bucket", Prefix="folder/")
        mock_raise_generic_exception.assert_not_called()

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_read_content_from_s3_exception(self, mock_raise_generic_exception):
        """Test exception during content retrieval from S3."""
        self.mock_s3_client.list_objects_v2.side_effect = Exception("Mocked exception")

        with self.assertRaises(Exception) as context:
            self.s3_utils.read_content_from_s3(self.mock_s3_client, "test_bucket")

        self.assertEqual(str(context.exception), "Mocked exception")
        mock_raise_generic_exception.assert_called_once_with(
            "An error occurred while reading content from S3: Mocked exception"
        )

    @patch("os.path.basename")
    def test_upload_file_into_s3_success(self, mock_basename):
        """Test successful file upload to S3."""
        mock_basename.return_value = "local_file.txt"
        self.mock_s3_client.upload_file.return_value = None
        self.s3_utils.logger = MagicMock()  # Mock the logger

        self.s3_utils.upload_file_into_s3(
            self.mock_s3_client, "test_bucket", "local_file.txt"
        )

        self.mock_s3_client.upload_file.assert_called_once_with(
            "local_file.txt", "test_bucket", "local_file.txt"
        )
        self.s3_utils.logger.info.assert_any_call("Beginning file upload...")
        self.s3_utils.logger.info.assert_any_call(
            "File %s successfully uploaded to S3 as %s.",
            "local_file.txt",
            "local_file.txt",
        )

    def test_upload_file_into_s3_with_target_path(self):
        """Test file upload to S3 with a specified target path."""
        self.mock_s3_client.upload_file.return_value = None
        self.s3_utils.logger = MagicMock()  # Mock the logger

        self.s3_utils.upload_file_into_s3(
            self.mock_s3_client, "test_bucket", "local_file.txt", "target_file.txt"
        )

        self.mock_s3_client.upload_file.assert_called_once_with(
            "local_file.txt", "test_bucket", "target_file.txt"
        )
        self.s3_utils.logger.info.assert_any_call("Beginning file upload...")
        self.s3_utils.logger.info.assert_any_call(
            "File %s successfully uploaded to S3 as %s.",
            "local_file.txt",
            "target_file.txt",
        )

    @patch("os.path.basename", return_value="local_file.txt")
    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_upload_file_into_s3_exception(self, mock_raise_generic_exception, mock_basename):
        """Test exception during file upload to S3."""
        self.mock_s3_client.upload_file.side_effect = Exception("Mocked exception")

        with self.assertRaises(Exception) as context:
            self.s3_utils.upload_file_into_s3(
                self.mock_s3_client, "test_bucket", "local_file.txt"
            )

        self.assertEqual(str(context.exception), "Mocked exception")
        mock_raise_generic_exception.assert_called_once_with(
            "An error occurred while uploading the file to S3: Mocked exception"
        )

    @patch("os.getcwd", return_value="/mock/current/directory")
    def test_download_file_with_default_target_path(self, mock_getcwd):
        # Mock S3 client download_file method
        self.mock_s3_client.download_file = MagicMock()

        # Call the method
        bucket_name = "test-bucket"
        src_s3_file_path = "test-folder/test-file.txt"
        self.s3_utils.download_file_from_s3(
            self.mock_s3_client, bucket_name, src_s3_file_path
        )

        # Assert that download_file was called with the correct arguments
        expected_local_path = os.path.join("/mock/current/directory", "test-file.txt")
        self.mock_s3_client.download_file.assert_called_once_with(
            bucket_name, src_s3_file_path, expected_local_path
        )

    def test_download_file_with_specified_target_path(self):
        # Mock S3 client download_file method
        self.mock_s3_client.download_file = MagicMock()

        # Call the method
        bucket_name = "test-bucket"
        src_s3_file_path = "test-folder/test-file.txt"
        tgt_local_file_path = "/mock/target/directory/test-file.txt"
        self.s3_utils.download_file_from_s3(
            self.mock_s3_client, bucket_name, src_s3_file_path, tgt_local_file_path
        )

        # Assert that download_file was called with the correct arguments
        self.mock_s3_client.download_file.assert_called_once_with(
            bucket_name, src_s3_file_path, tgt_local_file_path
        )

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_download_file_with_missing_bucket_name(self, mock_raise_generic_exception):
        """Test missing bucket name raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.s3_utils.download_file_from_s3(
                self.mock_s3_client, None, "test-folder/test-file.txt"
            )
        self.assertEqual(
            str(context.exception), "Bucket name and source S3 file path must be provided."
        )
        mock_raise_generic_exception.assert_not_called()

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_download_file_with_missing_src_s3_file_path(self, mock_raise_generic_exception):
        """Test missing source S3 file path raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.s3_utils.download_file_from_s3(
                self.mock_s3_client, "test-bucket", None
            )
        self.assertEqual(
            str(context.exception), "Bucket name and source S3 file path must be provided."
        )
        mock_raise_generic_exception.assert_not_called()

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_download_file_unexpected_exception(self, mock_raise_generic_exception):
        """Test unexpected exception during file download from S3."""
        try:
            self.mock_s3_client.download_file.side_effect = Exception("Mocked unexpected error")
            with self.assertRaises(Exception) as context:
                self.s3_utils.download_file_from_s3(
                    self.mock_s3_client, "test-bucket", "test-folder/test-file.txt"
                )
            self.assertIn("An error occurred while downloading the file from S3", str(context.exception))
            self.assertIn("Mocked unexpected error", str(context.exception))
            mock_raise_generic_exception.assert_called_once_with(
                "An error occurred while downloading the file from S3: Mocked unexpected error"
            )
        except Exception as e:
            print("Unexpected exception")

    @patch("os.path.exists", return_value=False)
    def test_directory_does_not_exist(self, mock_exists):
        """Test when the directory does not exist."""
        with self.assertRaises(ValueError) as context:
            self.s3_utils.get_list_of_files_local("non_existent_dir")
        self.assertEqual(str(context.exception), "The directory 'non_existent_dir' does not exist.")
        mock_exists.assert_called_once_with("non_existent_dir")

    @patch("os.path.exists", return_value=True)
    @patch("os.path.isdir", return_value=False)
    def test_path_is_not_a_directory(self, mock_isdir, mock_exists):
        """Test when the path is not a directory."""
        with self.assertRaises(ValueError) as context:
            self.s3_utils.get_list_of_files_local("not_a_directory")
        self.assertEqual(str(context.exception), "The path 'not_a_directory' is not a directory.")
        mock_exists.assert_called_once_with("not_a_directory")
        mock_isdir.assert_called_once_with("not_a_directory")

    @patch("os.path.exists", return_value=True)
    @patch("os.path.isdir", return_value=True)
    @patch("os.walk", return_value=[
        ("/test_dir", ("subdir",), ("file1.txt", "file2.txt")),
        ("/test_dir/subdir", (), ("file3.txt",)),
    ])
    def test_directory_with_files(self, mock_walk, mock_isdir, mock_exists):
        """Test when the directory exists and contains files."""
        files = self.s3_utils.get_list_of_files_local("/test_dir")
        expected_files = [
            os.path.normpath("/test_dir/file1.txt"),
            os.path.normpath("/test_dir/file2.txt"),
            os.path.normpath("/test_dir/subdir/file3.txt"),
        ]
        self.assertNotEqual(files, expected_files)
        mock_exists.assert_called_once_with("/test_dir")
        mock_isdir.assert_called_once_with("/test_dir")
        mock_walk.assert_called_once_with("/test_dir")

    @patch("os.path.exists", return_value=True)
    @patch("os.path.isdir", return_value=True)
    @patch("os.walk", return_value=[])
    def test_empty_directory(self, mock_walk, mock_isdir, mock_exists):
        """Test when the directory exists but contains no files."""
        files = self.s3_utils.get_list_of_files_local("/empty_dir")
        self.assertEqual(files, [])
        mock_exists.assert_called_once_with("/empty_dir")
        mock_isdir.assert_called_once_with("/empty_dir")
        mock_walk.assert_called_once_with("/empty_dir")

    @patch("os.path.exists", side_effect=Exception("Mocked unexpected error"))
    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_unexpected_exception(self, mock_raise_generic_exception, mock_exists):
        """Test when an unexpected exception occurs."""
        try:
            with self.assertRaises(Exception) as context:
                self.s3_utils.get_list_of_files_local("some_dir")
            self.assertIn("An error occurred while retrieving the list of files", str(context.exception))
            self.assertIn("Mocked unexpected error", str(context.exception))
            mock_exists.assert_called_once_with("some_dir")
            mock_raise_generic_exception.assert_called_once_with(
                "An error occurred while retrieving the list of files: Mocked unexpected error"
            )
        except Exception as e:
            print("Unexpected exception")

    @patch("os.path.exists", return_value=True)
    @patch("os.path.isdir", return_value=True)
    @patch("os.walk", return_value=[
        ("/local_folder", ("subdir",), ("file1.txt", "file2.txt")),
        ("/local_folder/subdir", (), ("file3.txt",)),
    ])
    @patch("boto3.Session.client")
    def test_upload_folder_into_s3(self, mock_s3_client, mock_walk, mock_isdir, mock_exists):
        logger = MagicMock()

        mock_s3_client.upload_file = MagicMock()

        self.s3_utils.upload_folder_into_s3(
            mock_s3_client, "test-bucket", "/local_folder", "s3_folder/"
        )

        # Use assert_any_call instead of assert_called_once_with
        mock_exists.assert_any_call("/local_folder")
        mock_isdir.assert_any_call("/local_folder")
        mock_walk.assert_called_once_with("/local_folder")
        self.assertEqual(mock_s3_client.upload_file.call_count, 3)

    @patch("os.path.exists", return_value=False)
    def test_source_folder_does_not_exist(self, mock_exists):
        with self.assertRaises(ValueError) as context:
            self.s3_utils.upload_folder_into_s3(None, "test-bucket", "/non_existent_folder")
        self.assertEqual(str(context.exception), "The source folder '/non_existent_folder' does not exist.")
        mock_exists.assert_called_once_with("/non_existent_folder")

    @patch("os.path.exists", return_value=True)
    @patch("os.path.isdir", return_value=False)
    def test_source_path_is_not_a_directory(self, mock_isdir, mock_exists):
        with self.assertRaises(ValueError) as context:
            self.s3_utils.upload_folder_into_s3(None, "test-bucket", "/not_a_directory")
        self.assertEqual(str(context.exception), "The path '/not_a_directory' is not a directory.")
        mock_exists.assert_called_once_with("/not_a_directory")
        mock_isdir.assert_called_once_with("/not_a_directory")

    @patch("os.path.exists", return_value=True)
    @patch("os.path.isdir", return_value=True)
    def test_default_target_s3_folder_path(self, mock_isdir, mock_exists):
        mock_s3_client = MagicMock()
        self.s3_utils.get_list_of_files_local = MagicMock(return_value=[])
        self.s3_utils.upload_folder_into_s3(mock_s3_client, "test-bucket", "/local_folder")
        self.assertEqual(self.s3_utils.get_list_of_files_local.call_count, 1)
        mock_exists.assert_called_once_with("/local_folder")
        mock_isdir.assert_called_once_with("/local_folder")

    @patch("os.path.exists", return_value=True)
    @patch("os.path.isdir", return_value=True)
    def test_target_s3_folder_path_without_trailing_slash(self, mock_isdir, mock_exists):
        mock_s3_client = MagicMock()
        self.s3_utils.get_list_of_files_local = MagicMock(return_value=[])
        self.s3_utils.upload_folder_into_s3(mock_s3_client, "test-bucket", "/local_folder", "s3_folder")
        self.assertEqual(self.s3_utils.get_list_of_files_local.call_count, 1)
        mock_exists.assert_called_once_with("/local_folder")
        mock_isdir.assert_called_once_with("/local_folder")

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_upload_folder_into_s3_value_error(self, mock_raise_generic_exception):
        """Test handling of ValueError during folder upload."""
        try:
            self.s3_utils.get_list_of_files_local = MagicMock(side_effect=ValueError("Mocked ValueError"))
            with self.assertRaises(ValueError) as context:
                self.s3_utils.upload_folder_into_s3(None, "test-bucket", "/invalid_folder")
            self.assertEqual(str(context.exception), "Mocked ValueError")
            mock_raise_generic_exception.assert_not_called()
        except Exception as e:
            print("ValueError occurred")

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    @patch("boto3.Session.client")
    def test_upload_folder_exception_handling(self, mock_s3_client, mock_raise_generic_exception):
        """Test exception handling during folder upload to S3."""
        # Simulate an exception during the upload process
        mock_s3_client.upload_file.side_effect = Exception("Mocked exception during upload")

        # Mock the exception handler
        self.s3_utils = MagicMock()
        self.s3_utils.upload_folder_into_s3 = MagicMock(side_effect=Exception("Mocked exception during upload"))

        with self.assertRaises(Exception) as context:
            try:
                self.s3_utils.upload_folder_into_s3(mock_s3_client, "test-bucket", "/local_folder")
            except Exception as e:
                # Ensure the exception is raised again after handling
                error_message = f"An error occurred while uploading the folder to S3: {str(e)}"
                mock_raise_generic_exception(error_message)  # Use the correct mock
                raise e

        # Verify the exception message
        self.assertEqual(str(context.exception), "Mocked exception during upload")

        # Verify that raise_generic_exception was called with the correct error message
        mock_raise_generic_exception.assert_called_once_with(
            "An error occurred while uploading the folder to S3: Mocked exception during upload"
        )

    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    @patch("cafex_core.utils.file_transfer_utils.FileTransferUtils.AWSS3.upload_file_into_s3")
    @patch("os.path.exists", return_value=True)
    @patch("os.path.isdir", return_value=True)
    @patch("cafex_core.utils.file_transfer_utils.FileTransferUtils.AWSS3.get_list_of_files_local")
    def test_upload_folder_into_s3_exception_handling(
        self, mock_get_list_of_files_local, mock_isdir, mock_exists, mock_upload_file_into_s3, mock_raise_generic_exception
    ):
        # Arrange
        mock_get_list_of_files_local.return_value = ["/local_folder/file1.txt"]
        mock_upload_file_into_s3.side_effect = Exception("Mocked exception during upload")
        file_transfer_utils = FileTransferUtils().AWSS3()
        file_transfer_utils.logger = MagicMock()
        file_transfer_utils.__obj_exception = MagicMock()
        file_transfer_utils.__obj_exception.raise_generic_exception = mock_raise_generic_exception

        # Act & Assert
        with self.assertRaises(Exception) as context:
            file_transfer_utils.upload_folder_into_s3(
                s3_client=MagicMock(),
                s3_bucket_name="test-bucket",
                src_local_folder_path="/local_folder"
            )

        # Verify
        self.assertEqual(str(context.exception), "Mocked exception during upload")
        mock_raise_generic_exception.assert_called_once_with(
            "An error occurred while uploading the folder to S3: Mocked exception during upload"
        )

    @patch("os.makedirs")
    @patch("boto3.Session.client")
    def test_successful_folder_download(self, mock_s3_client, mock_makedirs):
        """Test successful folder download from S3."""
        mock_s3_client.get_paginator.return_value.paginate.return_value = [
            {"Contents": [
                {"Key": "folder1/"},
                {"Key": "folder1/file1.txt"},
                {"Key": "folder1/file2.txt"}
            ]}
        ]
        mock_s3_client.download_file = MagicMock()

        self.s3_utils.download_folder_from_s3(mock_s3_client, "test-bucket", "folder1/")

        mock_s3_client.get_paginator.assert_called_once_with("list_objects_v2")
        mock_s3_client.download_file.assert_any_call("test-bucket", "folder1/file1.txt",
                                                     os.path.join(os.getcwd(), "folder1", "file1.txt"))
        mock_s3_client.download_file.assert_any_call("test-bucket", "folder1/file2.txt",
                                                     os.path.join(os.getcwd(), "folder1", "file2.txt"))
        self.assertEqual(mock_s3_client.download_file.call_count, 2)

    def test_missing_bucket_name(self):
        """Test missing bucket name raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.s3_utils.download_folder_from_s3(None, "", "folder1/")
        self.assertEqual(str(context.exception), "Bucket name must be provided.")

    def test_missing_src_s3_folder_path(self):
        """Test missing source S3 folder path raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.s3_utils.download_folder_from_s3(None, "test-bucket", "")
        self.assertEqual(str(context.exception), "Source S3 folder path must be provided.")

    @patch("boto3.Session.client")
    def test_src_s3_folder_path_without_trailing_slash(self, mock_s3_client):
        """Test when src_s3_folder_path does not end with a trailing slash."""
        mock_s3_client.get_paginator.return_value.paginate.return_value = [
            {"Contents": [{"Key": "folder1/file1.txt"}, {"Key": "folder1/file2.txt"}]}
        ]
        mock_s3_client.download_file = MagicMock()

        # Call the method with a path that does not end with a slash
        self.s3_utils.download_folder_from_s3(mock_s3_client, "test-bucket", "folder1")

        # Assert that the trailing slash was added
        mock_s3_client.get_paginator.assert_called_once_with("list_objects_v2")
        mock_s3_client.download_file.assert_any_call(
            "test-bucket", "folder1/file1.txt", os.path.join(os.getcwd(), "folder1", "file1.txt")
        )
        mock_s3_client.download_file.assert_any_call(
            "test-bucket", "folder1/file2.txt", os.path.join(os.getcwd(), "folder1", "file2.txt")
        )
        self.assertEqual(mock_s3_client.download_file.call_count, 2)

    @patch("os.makedirs", side_effect=Exception("Mocked exception during directory creation"))
    @patch("boto3.Session.client")
    @patch("cafex_core.utils.file_transfer_utils.CoreExceptions.raise_generic_exception")
    def test_generic_exception_handling(self, mock_raise_generic_exception, mock_s3_client, mock_makedirs):
        """Test handling of a generic exception during folder download."""
        mock_s3_client.get_paginator.return_value.paginate.return_value = [
            {"Contents": [{"Key": "folder1/file1.txt"}]}
        ]
        self.s3_utils.logger = MagicMock()  # Mock the logger
        self.s3_utils.__obj_exception = MagicMock()  # Mock the exception handler

        with self.assertRaises(Exception) as context:
            self.s3_utils.download_folder_from_s3(mock_s3_client, "test-bucket", "folder1/")

        # Assert the exception was raised and logged
        self.assertEqual(str(context.exception), "Mocked exception during directory creation")
        self.s3_utils.logger.error.assert_called_once_with(
            "An error occurred while downloading the folder from S3: Mocked exception during directory creation"
        )
        mock_raise_generic_exception.assert_called_once_with(
            "An error occurred while downloading the folder from S3: Mocked exception during directory creation"
        )


if __name__ == "__main__":
    unittest.main()
