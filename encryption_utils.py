import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()
key = os.environ.get("FERNET_KEY")
if not key:
    raise ValueError("FERNET_KEY environment variable is not set")

cipher = Fernet(key)

def encrypt_password(password: str) -> str:
    return cipher.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    return cipher.decrypt(encrypted_password.encode()).decode()