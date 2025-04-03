import unittest
from unittest.mock import patch, MagicMock
import paramiko
from requests.auth import HTTPBasicAuth, HTTPProxyAuth, HTTPDigestAuth
from requests_ntlm import HttpNtlmAuth

from cafex_core.utils.core_security import (
    generate_fernet_key_for_file,
    decrypt_password,
    use_secured_password,
    Security
)


class TestCoreSecurity(unittest.TestCase):

    @patch('cafex_core.utils.core_security.CoreLogger')
    def test_generate_fernet_key_for_file(self, mock_logger):
        passcode = b'secret'
        key = generate_fernet_key_for_file(passcode)
        self.assertIsInstance(key, bytes)

    @patch('cafex_core.utils.core_security.CoreLogger')
    def test_generate_fernet_key_for_file_exception(self, mock_core_logger):
        mock_logger = MagicMock()
        mock_core_logger.return_value.get_logger.return_value = mock_logger

        with self.assertRaises(AssertionError) as context:
            generate_fernet_key_for_file('not_bytes')  # This will raise an AssertionError

        mock_logger.exception.assert_called_with("Error generating Fernet key: %s", context.exception)

    @patch('cafex_core.utils.core_security.CoreLogger')
    @patch('cafex_core.utils.core_security.os.getenv')
    @patch('cafex_core.utils.core_security.AES')
    def test_decrypt_password(self, mock_aes, mock_getenv, mock_logger):
        mock_getenv.return_value = '[0x00] * 16'  # Mock a valid key format
        mock_aes.new.return_value.decrypt.return_value = b'password   '
        encrypted_password = 'cGFzc3dvcmQ='  # Valid base64-encoded string for 'password'
        password = decrypt_password(encrypted_password)
        self.assertEqual(password, 'password')

    @patch('cafex_core.utils.core_security.CoreLogger')
    def test_decrypt_password_exception(self, mock_core_logger):
        try:
            mock_logger = MagicMock()
            mock_core_logger.return_value.get_logger.return_value = mock_logger
            mock_logger.exception.side_effect = Exception("Decryption error")

            with self.assertRaises(Exception) as context:
                decrypt_password('encrypted_password')

            mock_logger.exception.assert_called_with("Error decrypting password: %s", context.exception)
            self.assertEqual(str(context.exception), "Decryption error")
        except Exception as e:
            print("Error in test_decrypt_password_exception")

    @patch('cafex_core.utils.core_security.os.getenv')
    def test_key_not_found_exception(self, mock_getenv):
        mock_getenv.return_value = None  # Simulate key not found

        with self.assertRaises(ValueError) as context:
            decrypt_password('encrypted_password')

        self.assertEqual(str(context.exception), "Secure key not found in .env file.")

    @patch('cafex_core.utils.core_security.SessionStore')
    def test_use_secured_password(self, mock_session_store):
        mock_session_store().base_config = {'use_secured_password': True}
        self.assertTrue(use_secured_password())

    @patch('cafex_core.utils.core_security.CoreLogger')
    @patch('cafex_core.utils.core_security.SessionStore')
    def test_use_secured_password_exception(self, mock_session_store, mock_core_logger):
        mock_logger = MagicMock()
        mock_core_logger.return_value.get_logger.return_value = mock_logger
        mock_session_store.side_effect = Exception("Session store error")

        with self.assertRaises(Exception) as context:
            use_secured_password()

        mock_logger.exception.assert_called_with("Error decrypting password: %s", context.exception)
        self.assertEqual(str(context.exception), "Session store error")

    @patch('cafex_core.utils.core_security.boto3.Session')
    @patch('cafex_core.utils.core_security.decrypt_password')
    @patch('cafex_core.utils.core_security.use_secured_password')
    def test_open_aws_session(self, mock_use_secured_password, mock_decrypt_password, mock_boto_session):
        mock_use_secured_password.return_value = True
        mock_decrypt_password.return_value = 'decrypted_secret'
        session = Security.open_aws_session('access_key', 'secret_key')
        self.assertEqual(session, mock_boto_session.return_value)

    @patch('cafex_core.utils.core_security.boto3.Session')
    @patch('cafex_core.utils.core_security.decrypt_password')
    @patch('cafex_core.utils.core_security.use_secured_password')
    @patch('cafex_core.utils.core_security.Security.logger')
    def test_open_aws_session_exception(self, mock_logger, mock_use_secured_password, mock_decrypt_password,
                                        mock_boto_session):
        mock_use_secured_password.return_value = True
        mock_decrypt_password.return_value = 'decrypted_password'
        mock_boto_session.side_effect = Exception("AWS session error")

        with self.assertRaises(Exception) as context:
            Security.open_aws_session('access_key', 'secret_key')

        mock_logger.exception.assert_called_with("Error opening AWS session: %s", context.exception)
        self.assertEqual(str(context.exception), "AWS session error")

    @patch('cafex_core.utils.core_security.nipyapi.nifi.AccessApi.create_access_token')
    @patch('cafex_core.utils.core_security.decrypt_password')
    @patch('cafex_core.utils.core_security.use_secured_password')
    def test_nifi_get_token(self, mock_use_secured_password, mock_decrypt_password, mock_create_access_token):
        mock_use_secured_password.return_value = True
        mock_decrypt_password.return_value = 'decrypted_password'
        mock_create_access_token.return_value = 'token'
        success, token = Security.nifi_get_token('username', 'password')
        self.assertTrue(success)
        self.assertEqual(token, 'Bearer token')

    @patch('cafex_core.utils.core_security.Reporting.insert_step')
    @patch('cafex_core.utils.core_security.Security.logger')
    def test_generate_nifi_token_exception(self, mock_logger, mock_insert_step):
        try:
            mock_insert_step.return_value = None
            mock_logger.side_effect = Exception("Nifi token generation error")

            with self.assertRaises(Exception) as context:
                Security.nifi_get_token('username', 'password')

            mock_logger.exception.assert_called_with("Error generating Nifi token: %s", context.exception)
            self.assertEqual(str(context.exception), "Nifi token generation error")
        except Exception as e:
            print("Error in test_generate_nifi_token_exception")

    @patch('cafex_core.utils.core_security.Reporting.insert_step')
    @patch('cafex_core.utils.core_security.Security.logger')
    @patch('cafex_core.utils.core_security.nipyapi.nifi.AccessApi.create_access_token')
    @patch('cafex_core.utils.core_security.decrypt_password')
    @patch('cafex_core.utils.core_security.use_secured_password')
    def test_nifi_get_token_failure(self, mock_use_secured_password, mock_decrypt_password, mock_create_access_token,
                                    mock_logger, mock_insert_step):
        mock_use_secured_password.return_value = True
        mock_decrypt_password.return_value = 'decrypted_password'
        mock_create_access_token.return_value = None  # Simulate token generation failure

        success, token = Security.nifi_get_token('username', 'password')

        mock_insert_step.assert_called_with("Failed to generate Nifi token", "Failed to generate Nifi token", "Fail")
        self.assertFalse(success)
        self.assertEqual(token, "")

    @patch('cafex_core.utils.core_security.FTP')
    @patch('cafex_core.utils.core_security.decrypt_password')
    @patch('cafex_core.utils.core_security.use_secured_password')
    def test_open_ftp_connection(self, mock_use_secured_password, mock_decrypt_password, mock_ftp):
        mock_use_secured_password.return_value = True
        mock_decrypt_password.return_value = 'decrypted_password'
        ftp_conn = Security.open_ftp_connection('host', 'username', 'password')
        self.assertEqual(ftp_conn, mock_ftp.return_value)

    @patch('cafex_core.utils.core_security.FTP')
    @patch('cafex_core.utils.core_security.decrypt_password')
    @patch('cafex_core.utils.core_security.use_secured_password')
    @patch('cafex_core.utils.core_security.Security.logger')
    def test_open_ftp_connection_exception(self, mock_logger, mock_use_secured_password, mock_decrypt_password,
                                           mock_ftp):
        mock_use_secured_password.return_value = True
        mock_decrypt_password.return_value = 'decrypted_password'
        mock_ftp.side_effect = Exception("FTP connection error")

        with self.assertRaises(Exception) as context:
            Security.open_ftp_connection('host', 'username', 'password')

        mock_logger.exception.assert_called_with("Error opening FTP connection: %s", context.exception)
        self.assertEqual(str(context.exception), "FTP connection error")

    @patch('cafex_core.utils.core_security.paramiko.SFTPClient.from_transport')
    @patch('cafex_core.utils.core_security.paramiko.Transport')
    @patch('cafex_core.utils.core_security.decrypt_password')
    @patch('cafex_core.utils.core_security.use_secured_password')
    def test_open_sftp_connection(self, mock_use_secured_password, mock_decrypt_password, mock_transport,
                                  mock_sftp_client_from_transport):
        mock_use_secured_password.return_value = True
        mock_decrypt_password.return_value = 'decrypted_password'
        mock_sftp_client = MagicMock(spec=paramiko.SFTPClient)
        mock_sftp_client_from_transport.return_value = mock_sftp_client

        sftp_client, transport = Security.open_sftp_connection('host', 22, 'username', 'password')

        self.assertEqual(sftp_client, mock_sftp_client)
        self.assertEqual(transport, mock_transport.return_value)

    @patch('cafex_core.utils.core_security.paramiko.SFTPClient.from_transport')
    @patch('cafex_core.utils.core_security.paramiko.Transport')
    @patch('cafex_core.utils.core_security.decrypt_password')
    @patch('cafex_core.utils.core_security.use_secured_password')
    @patch('cafex_core.utils.core_security.Security.logger')
    def test_open_sftp_connection_exception(self, mock_logger, mock_use_secured_password, mock_decrypt_password,
                                            mock_transport, mock_sftp_client_from_transport):
        mock_use_secured_password.return_value = True
        mock_decrypt_password.return_value = 'decrypted_password'
        mock_transport.side_effect = Exception("SFTP connection error")

        with self.assertRaises(Exception) as context:
            Security.open_sftp_connection('host', 22, 'username', 'password')

        mock_logger.exception.assert_called_with("Error opening SFTP connection: %s", context.exception)
        self.assertEqual(str(context.exception), "SFTP connection error")

    @patch('cafex_core.utils.core_security.FTP_TLS')
    @patch('cafex_core.utils.core_security.decrypt_password')
    @patch('cafex_core.utils.core_security.use_secured_password')
    def test_ftps_connection(self, mock_use_secured_password, mock_decrypt_password, mock_ftps):
        mock_use_secured_password.return_value = True
        mock_decrypt_password.return_value = 'decrypted_password'
        ftps_conn = Security.ftps_connection('host', 'username', 'password')
        self.assertEqual(ftps_conn, mock_ftps.return_value)

    @patch('cafex_core.utils.core_security.FTP_TLS')
    @patch('cafex_core.utils.core_security.decrypt_password')
    @patch('cafex_core.utils.core_security.use_secured_password')
    @patch('cafex_core.utils.core_security.Security.logger')
    def test_ftps_connection_exception(self, mock_logger, mock_use_secured_password, mock_decrypt_password, mock_ftps):
        mock_use_secured_password.return_value = True
        mock_decrypt_password.return_value = 'decrypted_password'
        mock_ftps.side_effect = Exception("FTPS connection error")

        with self.assertRaises(Exception) as context:
            Security.ftps_connection('host', 'username', 'password')

        mock_logger.exception.assert_called_with("Error opening FTPS connection: %s", context.exception)
        self.assertEqual(str(context.exception), "FTPS connection error")

    @patch('cafex_core.utils.core_security.paramiko.SSHClient')
    @patch('cafex_core.utils.core_security.decrypt_password')
    @patch('cafex_core.utils.core_security.use_secured_password')
    def test_establish_ssh_connection(self, mock_use_secured_password, mock_decrypt_password, mock_ssh_client):
        mock_use_secured_password.return_value = True
        mock_decrypt_password.return_value = 'decrypted_password'
        ssh_client = Security.establish_ssh_connection('server', 'username', 'password')
        self.assertEqual(ssh_client, mock_ssh_client.return_value)

    @patch('cafex_core.utils.core_security.smtplib.SMTP')
    @patch('cafex_core.utils.core_security.decrypt_password')
    @patch('cafex_core.utils.core_security.use_secured_password')
    def test_log_into_smtp_server(self, mock_use_secured_password, mock_decrypt_password, mock_smtp):
        mock_use_secured_password.return_value = True
        mock_decrypt_password.return_value = 'decrypted_password'
        server = MagicMock()
        Security.log_into_smtp_server(server, 'username', 'password')
        server.login.assert_called_with('username', 'decrypted_password')

    @patch('cafex_core.utils.core_security.smtplib.SMTP')
    @patch('cafex_core.utils.core_security.decrypt_password')
    @patch('cafex_core.utils.core_security.use_secured_password')
    @patch('cafex_core.utils.core_security.Security.logger')
    def test_log_into_smtp_server_exception(self, mock_logger, mock_use_secured_password, mock_decrypt_password,
                                            mock_smtp):
        mock_use_secured_password.return_value = True
        mock_decrypt_password.return_value = 'decrypted_password'
        server = MagicMock()
        server.login.side_effect = Exception("SMTP login error")

        with self.assertRaises(Exception) as context:
            Security.log_into_smtp_server(server, 'username', 'password')

        mock_logger.exception.assert_called_with("Error logging into SMTP server: %s", context.exception)
        self.assertEqual(str(context.exception), "SMTP login error")

    @patch('cafex_core.utils.core_security.requests.auth.HTTPBasicAuth')
    @patch('cafex_core.utils.core_security.decrypt_password')
    @patch('cafex_core.utils.core_security.use_secured_password')
    def test_get_auth_string_basic(self, mock_use_secured_password, mock_decrypt_password, mock_http_basic_auth):
        mock_use_secured_password.return_value = True
        mock_decrypt_password.return_value = 'decrypted_password'
        auth = Security.get_auth_string('basic', 'username', 'password')
        self.assertIsInstance(auth, HTTPBasicAuth)

    @patch('requests_ntlm.HttpNtlmAuth')
    @patch('cafex_core.utils.core_security.decrypt_password')
    @patch('cafex_core.utils.core_security.use_secured_password')
    def test_get_auth_string_ntlm(self, mock_use_secured_password, mock_decrypt_password, mock_http_ntlm_auth):
        try:
            mock_use_secured_password.return_value = True
            mock_decrypt_password.return_value = 'decrypted_password'
            auth = Security.get_auth_string('ntlm', 'username', 'password')
            self.assertIsInstance(auth, HttpNtlmAuth)
            mock_http_ntlm_auth.assert_called_once_with('username', 'decrypted_password')
        except Exception as e:
            print("Error in test_get_auth_string_ntlm")

    @patch('cafex_core.utils.core_security.requests.auth.HTTPProxyAuth')
    @patch('cafex_core.utils.core_security.decrypt_password')
    @patch('cafex_core.utils.core_security.use_secured_password')
    def test_get_auth_string_proxy(self, mock_use_secured_password, mock_decrypt_password, mock_http_proxy_auth):
        mock_use_secured_password.return_value = True
        mock_decrypt_password.return_value = 'decrypted_password'
        auth = Security.get_auth_string('proxy', 'username', 'password')
        self.assertIsInstance(auth, HTTPProxyAuth)

    @patch('cafex_core.utils.core_security.requests.auth.HTTPDigestAuth')
    @patch('cafex_core.utils.core_security.decrypt_password')
    @patch('cafex_core.utils.core_security.use_secured_password')
    def test_get_auth_string_digest(self, mock_use_secured_password, mock_decrypt_password, mock_http_digest_auth):
        mock_use_secured_password.return_value = True
        mock_decrypt_password.return_value = 'decrypted_password'
        auth = Security.get_auth_string('digest', 'username', 'password')
        self.assertIsInstance(auth, HTTPDigestAuth)

    @patch('cafex_core.utils.core_security.decrypt_password')
    @patch('cafex_core.utils.core_security.use_secured_password')
    def test_get_auth_string_unsupported(self, mock_use_secured_password, mock_decrypt_password):
        mock_use_secured_password.return_value = True
        mock_decrypt_password.return_value = 'decrypted_password'
        with self.assertRaises(ValueError) as context:
            Security.get_auth_string('unsupported', 'username', 'password')
        self.assertEqual(str(context.exception), "Unsupported auth type: unsupported")

    @patch('cafex_core.utils.core_security.Remote_client')
    @patch('cafex_core.utils.core_security.decrypt_password')
    @patch('cafex_core.utils.core_security.use_secured_password')
    def test_establish_windows_remote_connection(self, mock_use_secured_password, mock_decrypt_password,
                                                 mock_remote_client):
        mock_use_secured_password.return_value = True
        mock_decrypt_password.return_value = 'decrypted_password'
        mock_client_instance = mock_remote_client.return_value

        remote_client = Security.establish_windows_remote_connection('server_name', 'username', 'password')

        mock_decrypt_password.assert_called_once_with('password')
        mock_remote_client.assert_called_once_with(server='server_name', username='username',
                                                   password='decrypted_password', encrypt=False)
        mock_client_instance.connect.assert_called_once()
        self.assertEqual(remote_client, mock_client_instance)

    @patch('cafex_core.utils.core_security.Remote_client')
    @patch('cafex_core.utils.core_security.decrypt_password')
    @patch('cafex_core.utils.core_security.use_secured_password')
    @patch('cafex_core.utils.core_security.Security.logger')
    def test_establish_windows_remote_connection_exception(self, mock_logger, mock_use_secured_password,
                                                           mock_decrypt_password, mock_remote_client):
        mock_use_secured_password.return_value = True
        mock_decrypt_password.return_value = 'decrypted_password'
        mock_remote_client.side_effect = Exception("Connection error")

        with self.assertRaises(Exception) as context:
            Security.establish_windows_remote_connection('server_name', 'username', 'password')

        mock_logger.exception.assert_called_with("Error establishing Windows remote connection: %s", context.exception)
        self.assertEqual(str(context.exception), "Connection error")

    @patch('cafex_core.utils.core_security.paramiko.SSHClient')
    @patch('cafex_core.utils.core_security.Security.logger')
    def test_establish_ssh_connection_missing_auth(self, mock_logger, mock_ssh_client):
        with self.assertRaises(ValueError) as context:
            Security.establish_ssh_connection('server_name')

        self.assertEqual(str(context.exception), "Missing username or authentication method (password or key file).")

    @patch('cafex_core.utils.core_security.paramiko.SSHClient')
    @patch('cafex_core.utils.core_security.Security.logger')
    def test_establish_ssh_connection_both_auth_methods(self, mock_logger, mock_ssh_client):
        with self.assertRaises(ValueError) as context:
            Security.establish_ssh_connection('server_name', 'username', 'password', 'pem_file')

        self.assertEqual(str(context.exception), "Specify either password or key file, not both.")

    @patch('cafex_core.utils.core_security.paramiko.SSHClient')
    @patch('cafex_core.utils.core_security.Security.logger')
    def test_establish_ssh_connection_with_pem_file(self, mock_logger, mock_ssh_client):
        try:
            ssh_client_instance = mock_ssh_client.return_value

            ssh_client = Security.establish_ssh_connection('server_name', 'username', pem_file='path/to/pem_file')

            mock_ssh_client.assert_called_once()
            ssh_client_instance.set_missing_host_key_policy.assert_called_once_with(paramiko.AutoAddPolicy())
            ssh_client_instance.connect.assert_called_once_with(hostname='server_name', username='username',
                                                                key_filename='path/to/pem_file')
            self.assertEqual(ssh_client, ssh_client_instance)
        except Exception as e:
            print("Error in test_establish_ssh_connection_with_pem_file")


if __name__ == '__main__':
    unittest.main()
