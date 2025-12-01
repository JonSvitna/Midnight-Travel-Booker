import bcrypt
from base64 import b64encode, b64decode
from cryptography.fernet import Fernet
from config import Config

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def get_cipher():
    """Get Fernet cipher instance"""
    key = Config.ENCRYPTION_KEY
    if not key:
        # Generate a key for development if not set
        key = Fernet.generate_key()
    elif isinstance(key, str):
        key = key.encode('utf-8')
    return Fernet(key)

def encrypt_data(data: str) -> bytes:
    """Encrypt sensitive data"""
    cipher = get_cipher()
    return cipher.encrypt(data.encode('utf-8'))

def decrypt_data(encrypted_data: bytes) -> str:
    """Decrypt sensitive data"""
    cipher = get_cipher()
    return cipher.decrypt(encrypted_data).decode('utf-8')
