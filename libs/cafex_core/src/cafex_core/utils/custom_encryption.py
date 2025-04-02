"""
Description: This module provides encryption and decryption of text using AES algorithm.
User can encrypt and decrypt text using a specified key.
"""
from Cryptodome.Cipher import AES
import base64


class CustomEncryption:
    """A class that provides static methods to encrypt and decrypt text using
    an AES algorithm in GCM mode.

    Methods:
        - custom_encrypt(plain_text, secret_key) : Encrypts the given text using a specified key.
        - custom_decrypt(encrypted_text, key): Decrypts the given encrypted text using
        the specified key.

    Usage:
        encrypted = CustomEncryption.custom_encrypt("Hello, World!", b"example!KeyLen24or16or32")
        decrypted = CustomEncryption.custom_decrypt(encrypted, b"example!KeyLen24or16or32")
    """

    @staticmethod
    def custom_encrypt(plain_text, secret_key):
        """Encrypts the given text using a specified key.

        Args:
            plain_text (str): The text to be encrypted.
            secret_key (bytes): The encryption key ex: b"example!KeyLen24or16or32"

        Returns:
            str: The encrypted text.

        Example:
            encrypted = CustomEncryption.custom_encrypt("Hello, World!",
            b"example!KeyLen24or16or32")
        Notes:
            Size of a key (in bytes)
            key_size = (16, 24, 32)
        """
        try:
            aes_obj = AES.new(secret_key, AES.MODE_GCM)
            nonce = aes_obj.nonce
            ciphertext, tag = aes_obj.encrypt_and_digest(plain_text.encode('utf-8'))
            encrypted_data = base64.b64encode(nonce + tag + ciphertext).decode('utf-8')
            return encrypted_data
        except Exception as e:
            raise e

    @staticmethod
    def custom_decrypt(cipher_text, secret_key):
        """Decrypts the given encrypted text using the specified key.

        Args:
            cipher_text (str): The text to be decrypted.
            secret_key (bytes): The decryption key. The decryption key ex:
            b"example!KeyLen24or16or32" (same as encryption key)

        Returns:
            str: The decrypted text.

        Example:
            decrypted = CustomEncryption.custom_decrypt("encrypted", b"example!KeyLen24or16or32")
        Notes:
            Size of a key (in bytes)
            key_size = (16, 24, 32)
        """
        try:
            encrypted_data = base64.b64decode(cipher_text)
            nonce = encrypted_data[:16]
            tag = encrypted_data[16:32]
            ciphertext = encrypted_data[32:]
            aes_obj = AES.new(secret_key, AES.MODE_GCM, nonce=nonce)
            decrypted_data = aes_obj.decrypt_and_verify(ciphertext, tag)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            raise e


if __name__ == "__main__":
    key = b"example!KeyLen24or16or32"
    text = "Hello, World!"
    encrypted = CustomEncryption.custom_encrypt(text, key)
    print(f"Encrypted: {encrypted}")
    decrypted = CustomEncryption.custom_decrypt(encrypted, key)
    print(f"Decrypted: {decrypted}")
