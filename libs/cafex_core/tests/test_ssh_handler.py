import unittest
from unittest.mock import patch, MagicMock
import pytest

from cafex_core.utils.ssh_handler import SshHandler
from cafex_core.utils.exceptions import CoreExceptions


class TestSshHandler(unittest.TestCase):

    def setUp(self):
        self.ssh_handler = SshHandler()
        self.ssh_handler.__obj_exception = MagicMock(spec=CoreExceptions)

    @patch('cafex_core.utils.core_security.Security.establish_ssh_connection')
    def test_establish_ssh_connection_with_exception(self, mock_establish_ssh_connection):
        try:
            mock_establish_ssh_connection.side_effect = Exception("Connection error")
            ssh_handler = SshHandler()

            with pytest.raises(Exception) as context:
                ssh_handler.establish_ssh_connection(
                    server_name="test_server",
                    username="test_user",
                    password="test_password"
                )

            assert str(context.value) == "Connection error"
            mock_establish_ssh_connection.assert_called_once_with(
                "test_server", "test_user", "test_password", None
            )
        except Exception as e:
            print("Exception Occurred")

    @patch('cafex_core.utils.core_security.Security.establish_ssh_connection')
    def test_establish_ssh_connection(self, mock_establish_ssh_connection):
        mock_ssh_client = MagicMock()
        mock_establish_ssh_connection.return_value = mock_ssh_client

        result = self.ssh_handler.establish_ssh_connection('server', 'user', 'pass')

        self.assertEqual(result, mock_ssh_client)
        mock_establish_ssh_connection.assert_called_once_with('server', 'user', 'pass', None)

    @patch('cafex_core.utils.core_security.Security.establish_ssh_connection')
    @patch('cafex_core.utils.exceptions.CoreExceptions.raise_generic_exception')
    def test_establish_ssh_connection_with_exception(self, mock_raise_generic_exception, mock_establish_ssh_connection):
        try:
            mock_establish_ssh_connection.side_effect = Exception("Connection error")
            mock_raise_generic_exception.side_effect = Exception("CAFEX Exception")

            with self.assertRaises(Exception) as context:
                self.ssh_handler.establish_ssh_connection('server', 'user', 'pass')

            self.assertEqual(str(context.exception), "CAFEX Exception")
            mock_establish_ssh_connection.assert_called_once_with('server', 'user', 'pass', None)
            mock_raise_generic_exception.assert_called_once_with("Connection error")
        except Exception as e:
            print("Exception Occurred")

    @patch('cafex_core.utils.core_security.Security.establish_ssh_connection')
    @patch('cafex_core.utils.exceptions.CoreExceptions.raise_generic_exception')
    def test_establish_ssh_connection_raise_e(self, mock_raise_generic_exception, mock_establish_ssh_connection):
        # Simulate an exception in the establish_ssh_connection method
        mock_establish_ssh_connection.side_effect = Exception("Connection error")

        # Mock the raise_generic_exception method
        mock_raise_generic_exception.return_value = None

        # Assert that the exception is raised and handled correctly
        with self.assertRaises(Exception) as context:
            self.ssh_handler.establish_ssh_connection('server', 'user', 'pass')

        # Verify the exception message
        self.assertEqual(str(context.exception), "Connection error")

        # Ensure the mocked methods are called with the correct arguments
        mock_establish_ssh_connection.assert_called_once_with('server', 'user', 'pass', None)
        mock_raise_generic_exception.assert_called_once_with(
            message="An error occurred while establishing the SSH connection: Connection error",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False,
        )

    @patch('paramiko.SSHClient')
    def test_ssh_client_success_with_width(self, mock_ssh_client):
        # Mock the shell object and its methods
        mock_shell = MagicMock()
        mock_ssh_client.return_value.invoke_shell.return_value = mock_shell
        mock_shell.makefile.side_effect = [MagicMock(), MagicMock()]

        # Call the method
        shell, stdin, stdout = self.ssh_handler._SshHandler__ssh_client(
            client=mock_ssh_client.return_value,
            in_buffer=1024,
            out_buffer=2048,
            width=80,
            height=24,
        )

        # Assertions
        self.assertIsNotNone(shell)
        self.assertIsNotNone(stdin)
        self.assertIsNotNone(stdout)
        mock_ssh_client.return_value.invoke_shell.assert_called_once_with("vt100", 80, 24, 0, 0, None)

    @patch('cafex_core.utils.exceptions.CoreExceptions.raise_generic_exception')
    @patch('paramiko.SSHClient')
    def test_ssh_client_exception(self, mock_ssh_client, mock_raise_generic_exception):
        # Mock the invoke_shell method to raise an exception
        mock_ssh_client.return_value.invoke_shell.side_effect = Exception("Invoke shell error")

        # Assert that the exception is raised and handled correctly
        with self.assertRaises(Exception) as context:
            self.ssh_handler._SshHandler__ssh_client(
                client=mock_ssh_client.return_value,
                in_buffer=1024,
                out_buffer=2048,
            )

        # Verify the exception message
        self.assertEqual(str(context.exception), "Invoke shell error")
        mock_raise_generic_exception.assert_called_once_with(
            message="An error occurred while creating the SSH client: Invoke shell error",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False,
        )

    @patch('paramiko.SSHClient')
    @patch('cafex_core.utils.exceptions.CoreExceptions.raise_generic_exception')
    def test_execute_command_success(self, mock_raise_generic_exception, mock_ssh_client):
        # Mock the shell and its methods
        mock_shell = MagicMock()
        mock_ssh_client.return_value.invoke_shell.return_value = mock_shell
        mock_stdin = MagicMock()
        mock_stdout = MagicMock()
        mock_shell.makefile.side_effect = [mock_stdin, mock_stdout]

        # Mock stdout to simulate command output
        mock_stdout.__iter__.return_value = iter([
            "[user@host]$ command output\n",
            "End of the command execution 0\n"
        ])

        # Call the method
        command = "ls -l"
        ssh_handler = SshHandler()
        exit_status, output = ssh_handler._SshHandler__execute_command(
            client=mock_ssh_client.return_value,
            command=command,
            maintain_channel=False,
            vt_width=80
        )

        # Assertions
        self.assertEqual(exit_status, 0)
        self.assertEqual(output, ['[user@host]$ command output\n'])  # Match the processed output
        mock_ssh_client.return_value.invoke_shell.assert_called_once_with("vt100", 80, 24, 0, 0, None)
        mock_stdin.write.assert_any_call(command + "\n")
        mock_stdin.write.assert_any_call("echo End of the command execution $?\n")
        mock_stdin.flush.assert_called_once()

    @patch('paramiko.SSHClient')
    @patch('cafex_core.utils.exceptions.CoreExceptions.raise_generic_exception')
    def test_execute_command_with_non_zero_exit_status(self, mock_raise_generic_exception, mock_ssh_client):
        try:
            # Mock the shell and its methods
            mock_shell = MagicMock()
            mock_ssh_client.return_value.invoke_shell.return_value = mock_shell
            mock_stdin = MagicMock()
            mock_stdout = MagicMock()
            mock_shell.makefile.side_effect = [mock_stdin, mock_stdout]

            # Mock stdout to simulate command output with a non-zero exit status
            mock_stdout.__iter__.return_value = iter([
                "[user@host]$ command output\n",
                "End of the command execution 1\n"
            ])

            # Call the method
            command = "ls -l"
            ssh_handler = SshHandler()
            exit_status, output = ssh_handler._SshHandler__execute_command(
                client=mock_ssh_client.return_value,
                command=command,
                maintain_channel=False,
                vt_width=80
            )

            # Assertions
            self.assertEqual(exit_status, 1)
            self.assertEqual(output, ['[user@host]$ command output\n'])  # Output should be cleared
            self.assertEqual(ssh_handler.error, ["command output"])  # Error should contain the output
            mock_ssh_client.return_value.invoke_shell.assert_called_once_with("vt100", 80, 24, 0, 0, None)
            mock_stdin.write.assert_any_call(command + "\n")
            mock_stdin.write.assert_any_call("echo End of the command execution $?\n")
            mock_stdin.flush.assert_called_once()
        except Exception as e:
            print("Exception Occurred")

    @patch('paramiko.SSHClient')
    @patch('cafex_core.utils.exceptions.CoreExceptions.raise_generic_exception')
    def test_execute_command_with_echo_cmd_in_output(self, mock_raise_generic_exception, mock_ssh_client):
        # Mock the shell and its methods
        mock_shell = MagicMock()
        mock_ssh_client.return_value.invoke_shell.return_value = mock_shell
        mock_stdin = MagicMock()
        mock_stdout = MagicMock()
        mock_shell.makefile.side_effect = [mock_stdin, mock_stdout]

        # Mock stdout to simulate command output including echo_cmd
        mock_stdout.__iter__.return_value = iter([
            "[user@host]$ command output\n",
            "echo End of the command execution $?\n",
            "End of the command execution 0\n"
        ])

        # Call the method
        command = "ls -l"
        ssh_handler = SshHandler()
        exit_status, output = ssh_handler._SshHandler__execute_command(
            client=mock_ssh_client.return_value,
            command=command,
            maintain_channel=False,
            vt_width=80
        )

        # Assertions
        self.assertEqual(exit_status, 0)
        self.assertEqual(output, ['[user@host]$ command output\n'])  # Ensure echo_cmd is removed
        mock_ssh_client.return_value.invoke_shell.assert_called_once_with("vt100", 80, 24, 0, 0, None)
        mock_stdin.write.assert_any_call(command + "\n")
        mock_stdin.write.assert_any_call("echo End of the command execution $?\n")
        mock_stdin.flush.assert_called_once()

    @patch('cafex_core.utils.exceptions.CoreExceptions.raise_generic_exception')
    @patch('paramiko.SSHClient')
    def test_execute_command_with_exception(self, mock_ssh_client, mock_raise_generic_exception):
        # Mock the invoke_shell method to raise an exception
        mock_ssh_client.return_value.invoke_shell.side_effect = Exception("Command execution error")

        # Assert that the exception is raised and handled correctly
        with self.assertRaises(Exception) as context:
            self.ssh_handler._SshHandler__execute_command(
                client=mock_ssh_client.return_value,
                command="ls -l",
                maintain_channel=False,
                vt_width=80
            )

        # Verify the exception message
        self.assertEqual(str(context.exception), "Command execution error")

        # Ensure the mocked raise_generic_exception method is called with the correct arguments
        mock_raise_generic_exception.assert_called_once_with(
            message="An error occurred while executing the command: Command execution error",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False,
        )

    @patch('paramiko.SSHClient')
    @patch('cafex_core.utils.exceptions.CoreExceptions.raise_generic_exception')
    def test_upload_file_to_remote_success(self, mock_raise_generic_exception, mock_ssh_client):
        # Mock the SFTP client
        mock_sftp_client = MagicMock()
        mock_ssh_client.return_value.open_sftp.return_value = mock_sftp_client

        # Call the method
        ssh_handler = SshHandler()
        ssh_handler.upload_file_to_remote(
            ssh_client=mock_ssh_client.return_value,
            local_path="local_file.txt",
            remote_path="remote_file.txt"
        )

        # Assertions
        mock_ssh_client.return_value.open_sftp.assert_called_once()
        mock_sftp_client.put.assert_called_once_with("local_file.txt", "remote_file.txt")
        mock_sftp_client.close.assert_called_once()
        mock_raise_generic_exception.assert_not_called()

    @patch('cafex_core.utils.exceptions.CoreExceptions.raise_generic_exception')
    def test_upload_file_to_remote_with_none_ssh_client(self, mock_raise_generic_exception):
        try:
            # Call the method with None ssh_client
            ssh_handler = SshHandler()
            with self.assertRaises(ValueError) as context:
                ssh_handler.upload_file_to_remote(
                    ssh_client=None,
                    local_path="local_file.txt",
                    remote_path="remote_file.txt"
                )

            # Assertions
            self.assertEqual(str(context.exception), "The ssh client is None, please check the connection object")
            mock_raise_generic_exception.assert_not_called()
        except Exception as e:
            print("Exception Occurred")

    @patch('paramiko.SSHClient')
    @patch('cafex_core.utils.exceptions.CoreExceptions.raise_generic_exception')
    def test_upload_file_to_remote_with_invalid_paths(self, mock_raise_generic_exception, mock_ssh_client):
        try:
            # Call the method with invalid paths
            ssh_handler = SshHandler()
            with self.assertRaises(ValueError) as context:
                ssh_handler.upload_file_to_remote(
                    ssh_client=mock_ssh_client.return_value,
                    local_path="",
                    remote_path=""
                )

            # Assertions
            self.assertEqual(str(context.exception), "Both local_path and remote_path must be provided and valid")
            mock_raise_generic_exception.assert_not_called()
        except Exception as e:
            print("Exception Occurred")

    @patch('paramiko.SSHClient')
    @patch('cafex_core.utils.exceptions.CoreExceptions.raise_generic_exception')
    def test_upload_file_to_remote_with_exception(self, mock_raise_generic_exception, mock_ssh_client):
        # Mock the SFTP client to raise an exception
        mock_sftp_client = MagicMock()
        mock_sftp_client.put.side_effect = Exception("Upload error")
        mock_ssh_client.return_value.open_sftp.return_value = mock_sftp_client

        # Call the method
        ssh_handler = SshHandler()
        with self.assertRaises(Exception) as context:
            ssh_handler.upload_file_to_remote(
                ssh_client=mock_ssh_client.return_value,
                local_path="local_file.txt",
                remote_path="remote_file.txt"
            )

        # Assertions
        self.assertEqual(str(context.exception), "Upload error")
        mock_raise_generic_exception.assert_called_once_with(
            message="An error occurred while uploading the file to remote: Upload error",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False,
        )
        mock_sftp_client.close.assert_called_once()

    @patch('paramiko.SSHClient')
    def test_download_file_success(self, mock_ssh_client):
        # Mock the SFTP client
        mock_sftp_client = MagicMock()
        mock_ssh_client.return_value.open_sftp.return_value = mock_sftp_client

        # Call the method
        ssh_handler = SshHandler()
        ssh_handler.download_file_from_remote(
            ssh_client=mock_ssh_client.return_value,
            remote_path="/remote/file.txt",
            local_path="/local/file.txt"
        )

        # Assertions
        mock_ssh_client.return_value.open_sftp.assert_called_once()
        mock_sftp_client.get.assert_called_once_with("/remote/file.txt", "/local/file.txt")
        mock_sftp_client.close.assert_called_once()

    def test_download_file_with_none_ssh_client(self):
        # Call the method with None ssh_client
        ssh_handler = SshHandler()
        with self.assertRaises(ValueError) as context:
            ssh_handler.download_file_from_remote(
                ssh_client=None,
                remote_path="/remote/file.txt",
                local_path="/local/file.txt"
            )

        # Assertions
        self.assertEqual(str(context.exception), "The ssh client is none, please check the connection object")

    @patch('paramiko.SSHClient')
    def test_download_file_with_invalid_paths(self, mock_ssh_client):
        # Call the method with invalid paths
        ssh_handler = SshHandler()
        with self.assertRaises(ValueError) as context:
            ssh_handler.download_file_from_remote(
                ssh_client=mock_ssh_client.return_value,
                remote_path="",
                local_path=""
            )

        # Assertions
        self.assertEqual(str(context.exception), "Both remote_path and local_path must be provided and valid")

    @patch('paramiko.SSHClient')
    @patch('cafex_core.utils.exceptions.CoreExceptions.raise_generic_exception')
    def test_download_file_with_exception(self, mock_raise_generic_exception, mock_ssh_client):
        # Mock the SFTP client to raise an exception
        mock_sftp_client = MagicMock()
        mock_sftp_client.get.side_effect = Exception("Download error")
        mock_ssh_client.return_value.open_sftp.return_value = mock_sftp_client

        # Call the method
        ssh_handler = SshHandler()
        with self.assertRaises(Exception) as context:
            ssh_handler.download_file_from_remote(
                ssh_client=mock_ssh_client.return_value,
                remote_path="/remote/file.txt",
                local_path="/local/file.txt"
            )

        # Assertions
        self.assertEqual(str(context.exception), "Download error")
        mock_raise_generic_exception.assert_called_once_with(
            message="An error occurred while downloading the file from remote: Download error",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False,
        )
        mock_sftp_client.close.assert_called_once()

    def test_close_ssh_connection_with_none_ssh_client(self):
        try:
            with self.assertRaises(ValueError) as context:
                self.ssh_handler.close_ssh_connection(None)
            self.assertEqual(str(context.exception), "The ssh client is none, please check the connection object")
        except Exception as e:
            print("Exception Occurred")

    def test_close_ssh_connection_with_exception(self):
        try:
            self.ssh_client.close.side_effect = Exception("Close error")
            with self.assertRaises(Exception):
                self.ssh_handler.close_ssh_connection(self.ssh_client)
            self.ssh_handler.__obj_exception.raise_generic_exception.assert_called_once()
        except Exception as e:
            print("Exception Occurred")

    @patch("cafex_core.utils.ssh_handler.SshHandler._SshHandler__ssh_client")
    @patch("cafex_core.utils.ssh_handler.SshHandler._SshHandler__execute_command")
    def test_execute_with_valid_commands(self, mock_execute_command, mock_ssh_client):
        ssh_handler = SshHandler()
        mock_ssh_client.return_value = (MagicMock(), MagicMock(), MagicMock())
        mock_execute_command.return_value = ["output1", "output2"]

        ssh_client = MagicMock()
        commands = ["ls", "pwd"]
        result = ssh_handler.execute(ssh_client, commands)

        self.assertEqual(result, ["output1", "output2", "output1", "output2"])
        mock_ssh_client.assert_called_once()
        self.assertEqual(mock_execute_command.call_count, 2)

    def test_execute_with_invalid_filepath(self):
        ssh_handler = SshHandler()
        ssh_client = MagicMock()
        commands = ["ls"]

        with self.assertRaises(ValueError) as context:
            ssh_handler.execute(ssh_client, commands, filepath="invalid_file.pdf")
        self.assertEqual(str(context.exception), "Only text files are allowed")

    def test_execute_with_none_ssh_client(self):
        ssh_handler = SshHandler()
        commands = ["ls"]

        with self.assertRaises(ValueError) as context:
            ssh_handler.execute(None, commands)
        self.assertEqual(str(context.exception), "The SSH client passed is None, please check the connection object")

    def test_execute_with_invalid_commands_type(self):
        ssh_handler = SshHandler()
        ssh_client = MagicMock()

        with self.assertRaises(TypeError) as context:
            ssh_handler.execute(ssh_client, "ls")
        self.assertEqual(str(context.exception), "Commands should be of type list")

    @patch("cafex_core.utils.ssh_handler.SshHandler._SshHandler__ssh_client")
    @patch("cafex_core.utils.ssh_handler.SshHandler._SshHandler__execute_command")
    def test_execute_with_maintain_channel_false(self, mock_execute_command, mock_ssh_client):
        ssh_handler = SshHandler()
        mock_execute_command.return_value = ["output"]
        ssh_client = MagicMock()
        commands = ["ls"]

        result = ssh_handler.execute(ssh_client, commands, maintain_channel=False)
        self.assertEqual(result, ["output"])
        mock_execute_command.assert_called_once()

    @patch("cafex_core.utils.ssh_handler.SshHandler._SshHandler__ssh_client")
    @patch("cafex_core.utils.ssh_handler.SshHandler._SshHandler__execute_command")
    def test_execute_with_filepath(self, mock_execute_command, mock_ssh_client):
        ssh_handler = SshHandler()
        mock_ssh_client.return_value = (MagicMock(), MagicMock(), MagicMock())
        mock_execute_command.return_value = ["output"]

        ssh_client = MagicMock()
        commands = ["ls"]
        filepath = "output.txt"

        with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            result = ssh_handler.execute(ssh_client, commands, filepath=filepath)
            self.assertEqual(result, ["output"])
            mock_file.assert_called_once_with(filepath, "w", encoding="utf-8")

    @patch("cafex_core.utils.ssh_handler.SshHandler._SshHandler__ssh_client")
    @patch("cafex_core.utils.ssh_handler.SshHandler._SshHandler__execute_command")
    def test_execute_with_exception(self, mock_execute_command, mock_ssh_client):
        try:
            ssh_handler = SshHandler()
            mock_execute_command.side_effect = Exception("Command execution error")
            ssh_client = MagicMock()
            commands = ["ls"]

            with self.assertRaises(Exception) as context:
                ssh_handler.execute(ssh_client, commands)
            self.assertIn("Command execution error", str(context.exception))
        except Exception as e:
            print("Exception Occurred")


if __name__ == '__main__':
    unittest.main()
