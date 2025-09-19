import unittest
from cafex_core.utils.custom_encryption import CustomEncryption


class TestCustomEncryption(unittest.TestCase):

    def setUp(self):
        self.key = b"example!KeyLen24or16or32"
        self.plain_text = "Hello, World!"
        self.encrypted_text = CustomEncryption.custom_encrypt(self.plain_text, self.key)

    def test_custom_encrypt(self):
        encrypted = CustomEncryption.custom_encrypt(self.plain_text, self.key)
        self.assertIsInstance(encrypted, str)
        self.assertNotEqual(encrypted, self.plain_text)

    def test_custom_decrypt(self):
        decrypted = CustomEncryption.custom_decrypt(self.encrypted_text, self.key)
        self.assertIsInstance(decrypted, str)
        self.assertEqual(decrypted, self.plain_text)

    def test_custom_encrypt_invalid_key(self):
        with self.assertRaises(ValueError):
            CustomEncryption.custom_encrypt(self.plain_text, b"short_key")

    def test_custom_decrypt_invalid_key(self):
        with self.assertRaises(ValueError):
            CustomEncryption.custom_decrypt(self.encrypted_text, b"short_key")

    def test_custom_decrypt_invalid_cipher_text(self):
        with self.assertRaises(Exception):
            CustomEncryption.custom_decrypt("invalid_cipher_text", self.key)


if __name__ == "__main__":
    unittest.main()
