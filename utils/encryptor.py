# -*- coding: utf-8 -*-

from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from infra import ENCRYPTATION_KEY


class Encryptor:
    """Encryptor
    """
    
    def __init__(self) -> None:
        if isinstance(ENCRYPTATION_KEY, str):
            self.encryptation_key: bytes = ENCRYPTATION_KEY.encode()
        elif isinstance(ENCRYPTATION_KEY, bytes):
            self.encryptation_key: bytes = ENCRYPTATION_KEY
        else:
            raise TypeError("ENCRYPTATION_KEY must be a string or bytes!")
        
        if not self.encryptation_key:
            raise ValueError("ENCRYPTATION_KEY environment variable is not set!")

    def get_encryption_key(self) -> bytes:
        salt = b"salt_"

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=50_000,
        )
        key: bytes = urlsafe_b64encode(kdf.derive(self.encryptation_key))

        return key


    def encrypt_api_key(self, api_key: str) -> str:
        encryption_key: bytes = self.get_encryption_key()
        
        f = Fernet(encryption_key)
        encrypted_data: bytes = f.encrypt(api_key.encode())

        return urlsafe_b64encode(encrypted_data).decode()


    def decrypt_api_key(self, encrypted_api_key: str) -> str:
        encryption_key = self.get_encryption_key()
        
        f = Fernet(encryption_key)
        decrypted_data = f.decrypt(urlsafe_b64decode(encrypted_api_key))
        
        return decrypted_data.decode()


if __name__ == "__main__":
    raw_text = "UUDT7DJgG8D"

    print("Raw:", raw_text)

    encrypted_api_key = Encryptor().encrypt_api_key(raw_text)
    print("Encrypted text:", encrypted_api_key)

    decrypted_api_key = Encryptor().decrypt_api_key(encrypted_api_key)
    print("Decrypted text:", decrypted_api_key)
