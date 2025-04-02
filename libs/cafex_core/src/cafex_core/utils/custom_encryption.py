"""
Description: This module provides encryption and decryption of text using AES algorithm.
User can encrypt and decrypt text using a specified key.
"""
import base64

from Crypto.Cipher import AES


class CustomEncryption:
    """A class that provides static methods to encrypt and decrypt text using
    an AES algorithm.

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
            aes_obj = AES.new(secret_key, AES.MODE_ECB)
            hex_enc = aes_obj.encrypt(bytes(plain_text, encoding='latin_1').rjust(32))
            encoded_pwd = base64.b64encode(hex_enc).decode('latin_1')
            return encoded_pwd
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
            decrypted = TextEncryptor.decrypt("encrypted", b"example!KeyLen24or16or32")
        Notes:
            Size of a key (in bytes)
            key_size = (16, 24, 32)
        """
        try:
            aes_obj = AES.new(secret_key, AES.MODE_ECB)
            hex_dec = base64.b64decode(cipher_text.encode('latin_1'))
            bytes_decoded = aes_obj.decrypt(hex_dec)
            decoded_pwd = bytes_decoded.strip().decode('latin_1')
            return decoded_pwd
        except Exception as e:
            raise e


if __name__ == "__main__":
    key = b"example!KeyLen24or16or32"
    text = "Hello, World!"
    encrypted = CustomEncryption.custom_encrypt(text, key)
    print(f"Encrypted: {encrypted}")
    decrypted = CustomEncryption.custom_decrypt(encrypted, key)
    print(f"Decrypted: {decrypted}")
