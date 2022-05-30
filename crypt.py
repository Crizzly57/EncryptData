"""
Author: Sven Kleinhans
"""

import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pikepdf import Pdf, Encryption, PasswordError


def gen_key(password: bytes) -> bytes:
    """Returns the Key"""
    salt = b'\x81\xd2n\xb1!\xcd\xa9\xd7n\xda\x89u\xfe`\x9a\xd8'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA512(),
        length=32,
        salt=salt,
        iterations=100000
    )
    return base64.urlsafe_b64encode(kdf.derive(key_material=password))


def make_encrypted_file(path: str) -> str:
    """Returns new string for encrypted file"""
    name, end = os.path.splitext(os.path.basename(path))
    new_string = name + "_encrypted" + end
    return os.path.dirname(path) + "\\" + new_string


def make_decrypted_file(path: str) -> str:
    """Returns new string for decrypted file"""
    name = os.path.basename(path)
    new_string = name.replace("_encrypted", "")
    return os.path.dirname(path) + "\\" + new_string


def check_encryption(path: str) -> bool:
    """Return True if file is encrypted"""
    file_name = os.path.basename(path)
    return bool("_encrypted" in file_name)


def encrypt(file: str, password: str) -> int:
    """Encrypt the file. Return statuscode"""
    fernet = Fernet(gen_key(password.encode()))
    if not check_encryption(file):
        try:
            with open(file, "rb") as input_file, open(make_encrypted_file(file), "wb") as out:
                file_data = input_file.read()
                encrypted_data = fernet.encrypt(file_data)
                out.write(encrypted_data)
            return 4    # File successfully encrypted
        except FileNotFoundError:
            return 101   # File does not exist
        except PermissionError:
            return 108  # Wrong permission
    return 104    # File is not encrypted


def decrypt(file: str, password: str) -> int:
    """Decrypt the file. Return statuscode"""
    fernet = Fernet(gen_key(password.encode()))
    if check_encryption(file):
        try:
            with open(file, "rb") as input_file, open(make_decrypted_file(file), 'wb') as out:
                encrypted_data = input_file.read()
                decrypted_data = fernet.decrypt(encrypted_data)
                out.write(decrypted_data)
                return 3    # File successfully decrypted
        except InvalidToken:
            return 103    # Wrong password
        except FileNotFoundError:
            return 101   # File does not exist
        except PermissionError:
            return 108  # Wrong permission
    return 105    # File is not encrypted


def encrypt_pdf(file, password: str) -> int:
    """Encrypt PDF. Return statuscode"""
    out_path = make_encrypted_file(file)
    try:
        with Pdf.open(os.path.normpath(file)) as input_file:
            input_file.save(out_path, encryption=Encryption(owner=password, user=password))
        return 4    # File successfully encrypted
    except PasswordError:
        return 104    # File already encrypted
    except FileNotFoundError:
        return 101   # File does not exist
    except PermissionError:
        return 108   # Wrong permission


def decrypt_pdf(file, password: str) -> int:
    """Decrypt PDF. Return statuscode"""
    out_path = make_decrypted_file(file)
    try:
        with Pdf.open(os.path.normpath(file), password) as input_file:
            if input_file.is_encrypted:
                input_file.save(out_path)
                return 3    # File successfully decrypted
            return 105    # File is not encrypted
    except PasswordError:
        return 103    # Wrong password
    except FileNotFoundError:
        return 101   # File does not exist
    except PermissionError:
        return 108   # Wrong permission
