"""
Description: This module contains security-related functionality.
"""
import base64
import hashlib
import os
import smtplib
from ftplib import FTP, FTP_TLS
from typing import Optional

import boto3
import nipyapi
import paramiko
import requests
from boto3 import Session
from Cryptodome.Cipher import AES
from pypsexec.client import Client as Remote_client
from requests.auth import HTTPBasicAuth, HTTPProxyAuth, HTTPDigestAuth
from requests_ntlm import HttpNtlmAuth

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.reporting_.reporting import Reporting
from cafex_core.singletons_.session_ import SessionStore


def generate_fernet_key_for_file(passcode: bytes) -> bytes:
    """Generates a Fernet key from a given passcode."""
    try:
        assert isinstance(passcode, bytes)
        hlib = hashlib.md5()
        hlib.update(passcode)
        return base64.urlsafe_b64encode(hlib.hexdigest().encode("latin-1"))
    except Exception as e:
        CoreLogger(name=__name__).get_logger().exception("Error generating Fernet key: %s", e)
        raise e


def decrypt_password(encrypted_password: str) -> str | Exception:
    """Decrypts an encrypted password."""
    try:
        key = os.getenv("secure_key")
        if not key:
            raise ValueError("Secure key not found in .env file.")
        encrypted_data = base64.b64decode(encrypted_password)
        nonce = encrypted_data[:16]
        tag = encrypted_data[16:32]
        ciphertext = encrypted_data[32:]
        aes_obj = AES.new(eval(key), AES.MODE_GCM, nonce=nonce)
        decrypted_data = aes_obj.decrypt_and_verify(ciphertext, tag)
        return decrypted_data.decode('utf-8')
    except Exception as e:
        CoreLogger(name=__name__).get_logger().exception("Error decrypting password: %s", e)
        raise e


def use_secured_password() -> bool:
    """Decrypts an encrypted password."""
    try:
        if SessionStore().base_config is None:
            return False

        return SessionStore().base_config.get("use_secured_password", False)
    except Exception as e:
        CoreLogger(name=__name__).get_logger().exception("Error decrypting password: %s", e)
        raise e


class Security:
    """Base class for security-related functionality."""
    logger = CoreLogger(name=__name__).get_logger()

    @staticmethod
    def open_aws_session(
            aws_access_key_id: str,
            aws_secret_access_key: str,
            aws_session_token: Optional[str] = None,
            region_name: Optional[str] = None,
            botocore_session: Optional[Session] = None,
            profile_name: Optional[str] = None,
    ) -> boto3.Session:
        """Creates an AWS session."""

        try:
            if use_secured_password():
                aws_secret_access_key = decrypt_password(aws_secret_access_key)

            return boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token,
                region_name=region_name,
                botocore_session=botocore_session,
                profile_name=profile_name,
            )
        except Exception as e:
            Security.logger.exception("Error opening AWS session: %s", e)
            raise e

    @staticmethod
    def nifi_get_token(username: str, password: str) -> tuple[bool, str]:
        """Generates a Nifi token."""

        try:
            if use_secured_password():
                password = decrypt_password(password)

            nifi_token = nipyapi.nifi.AccessApi().create_access_token(
                username=username, password=password
            )
            if nifi_token:
                nipyapi.security.set_service_auth_token(token=nifi_token, service="nifi")
                bearer_token = "Bearer " + nifi_token
                Reporting().insert_step(
                    "Successfully generated Nifi token", "Successfully generated Nifi token", "Pass"
                )
                return True, bearer_token

            Reporting().insert_step(
                "Failed to generate Nifi token", "Failed to generate Nifi token", "Fail"
            )
            return False, ""
        except Exception as e:
            Security.logger.exception("Error generating Nifi token: %s", e)
            raise e

    @staticmethod
    def open_ftp_connection(ftp_host: str, ftp_username: str, ftp_password: str) -> FTP:
        """Opens an FTP connection."""

        try:
            ftp_conn = FTP(ftp_host)
            if use_secured_password():
                ftp_password = decrypt_password(ftp_password)
            ftp_conn.login(user=ftp_username, passwd=ftp_password)
            return ftp_conn
        except Exception as e:
            Security.logger.exception("Error opening FTP connection: %s", e)
            raise e

    @staticmethod
    def open_sftp_connection(
            sftp_host: str, sftp_port: int, sftp_username: str, sftp_password: str
    ) -> tuple[paramiko.SFTPClient, paramiko.Transport]:
        """Opens an SFTP connection."""

        try:
            if use_secured_password():
                sftp_password = decrypt_password(sftp_password)
            transport = paramiko.Transport((sftp_host, sftp_port))
            transport.connect(username=sftp_username, password=sftp_password)
            return paramiko.SFTPClient.from_transport(transport), transport
        except Exception as e:
            Security.logger.exception("Error opening SFTP connection: %s", e)
            raise e

    @staticmethod
    def ftps_connection(ftps_host: str, ftps_username: str,
                        ftps_password: str) -> FTP_TLS:
        """Opens an FTPS connection."""

        try:
            if use_secured_password():
                ftps_password = decrypt_password(ftps_password)
            ftps_conn = FTP_TLS(ftps_host)
            ftps_conn.login(user=ftps_username, passwd=ftps_password)
            ftps_conn.prot_p()
            return ftps_conn
        except Exception as e:
            Security.logger.exception("Error opening FTPS connection: %s", e)
            raise e

    @staticmethod
    def establish_ssh_connection(
            server_name: str,
            username: Optional[str] = None,
            password: Optional[str] = None,
            pem_file: Optional[str] = None,
    ) -> paramiko.SSHClient:
        """Establishes an SSH connection."""

        try:
            if username and password and pem_file:
                raise ValueError("Specify either password or key file, not both.")

            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if username and password:
                if use_secured_password():
                    password = decrypt_password(password)
                ssh_client.connect(hostname=server_name, username=username, password=password)
            elif username and pem_file:
                ssh_client.connect(hostname=server_name, username=username, key_filename=pem_file)
            else:
                raise ValueError(
                    "Missing username or authentication method (password or key file)."
                )

            return ssh_client
        except Exception as e:
            Security.logger.exception("Error establishing SSH "
                                      "connection: %s", e)
            raise e

    @staticmethod
    def establish_windows_remote_connection(
            server_name: str, username: str, password: str
    ) -> Remote_client:
        """Establishes a Windows remote connection."""

        try:
            if use_secured_password():
                password = decrypt_password(password)
            remote_client_obj = Remote_client(
                server=server_name, username=username, password=password, encrypt=False
            )
            remote_client_obj.connect()
            return remote_client_obj
        except Exception as e:
            Security.logger.exception("Error establishing Windows remote connection: %s", e)
            raise e

    @staticmethod
    def log_into_smtp_server(server: smtplib.SMTP, username: str, password: str,
                             ) -> None:
        """Logs into an SMTP server."""

        try:
            if use_secured_password():
                password = decrypt_password(password)
            server.login(username, password)
        except Exception as e:
            Security.logger.exception("Error logging into SMTP server: %s", e)
            raise e

    @staticmethod
    def get_auth_string(auth_type: str, username: str,
                        password: str) -> requests.auth.AuthBase:
        """Returns an authentication object based on the auth type."""

        try:
            auth_type = auth_type.lower()
            if use_secured_password():
                password = decrypt_password(password)
            if auth_type == "basic":
                return HTTPBasicAuth(username, password)
            if auth_type == "ntlm":
                return HttpNtlmAuth(username, password)
            if auth_type == "proxy":
                return HTTPProxyAuth(username, password)
            if auth_type == "digest":
                return HTTPDigestAuth(username, password)
            raise ValueError(f"Unsupported auth type: {auth_type}")
        except Exception as e:
            Security.logger.exception("Error getting auth string: %s", e)
            raise e
