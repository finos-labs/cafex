# Custom Encryption Module

## Overview

This module provides encryption and decryption of text using the AES algorithm. 
Users can encrypt and decrypt text using a specified key.

## Features

- **AES Encryption and Decryption**: Encrypt and decrypt text using the AES algorithm.
- **Static Methods**: Easy-to-use static methods for encryption and decryption.
- **Key Size Flexibility**: Supports key sizes of 16, 24, or 32 bytes.
- **Base64 Encoding**: Encrypted text is encoded in Base64 for easy storage and transmission.
- **Error Handling**: Proper error handling to manage encryption and decryption exceptions.

## Basic Usage

```python
from cafex_core.utils.custom_encryption import CustomEncryption
key = b"example!KeyLen24or16or32"
plain_text = "Hello, World!"
encrypted_text = CustomEncryption.custom_encrypt(plain_text, key)
print(f"Encrypted: {encrypted_text}")
decrypted_text = CustomEncryption.custom_decrypt(encrypted_text, key)
print(f"Decrypted: {decrypted_text}")
```
## Notes
- **The key size must be 16, 24, or 32 bytes.**
- **The same key used for encryption must be used for decryption.**