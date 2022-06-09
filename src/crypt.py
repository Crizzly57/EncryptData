"""
Author: Sven Kleinhans
"""

import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pikepdf import Pdf, Encryption, PasswordError

MAGIC_STRING = b"ENCRYPTED"


def gen_key(password: bytes) -> bytes:
    """Return the Key"""
    salt = b'\x81\xd2n\xb1!\xcd\xa9\xd7n\xda\x89u\xfe`\x9a\xd8'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA512(),
        length=32,
        salt=salt,
        iterations=100000
    )
    return base64.urlsafe_b64encode(kdf.derive(key_material=password))


def get_hashed_pass(password: str) -> bytes:
    """Return the hash of the given password"""
    digest = hashes.Hash(hashes.SHA512())
    digest.update(password.encode())
    return digest.finalize()


def make_encrypted_file(path: str) -> str:
    """Return new string for encrypted file"""
    name, end = os.path.splitext(os.path.basename(path))
    new_string = name + "_encrypted" + end
    return os.path.dirname(path) + "\\" + new_string


def make_decrypted_file(path: str) -> str:
    """Return new string for decrypted file"""
    name = os.path.basename(path)
    if "_encrypted" in name:
        return os.path.dirname(path) + "\\" + name.replace("_encrypted", "")
    return path


def check_encryption(path: str) -> bool:
    """Return True if file is encrypted"""
    with open(path, "rb") as file:
        header = file.read(len(MAGIC_STRING))
    return MAGIC_STRING == header


def encrypt(file: str, password: str) -> int:
    """Encrypt the file. Return statuscode"""
    fernet = Fernet(gen_key(password.encode()))
    if not check_encryption(file):
        try:
            with open(file, "rb") as input_file, open(make_encrypted_file(file), "wb") as out:
                data = get_hashed_pass(password) + input_file.read()
                encrypted_data = fernet.encrypt(data)
                out.write(MAGIC_STRING)
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
                encrypted_data = input_file.read()[len(MAGIC_STRING):]
                decrypted_data = fernet.decrypt(encrypted_data)
                hashed_pass = decrypted_data[:64]
                if hashed_pass == get_hashed_pass(password):
                    out.write(decrypted_data[64:])
                    return 3    # File successfully decrypted
                return 103  # Wrong password
        except InvalidToken:
            return 103    # Wrong password
        except FileNotFoundError:
            return 101   # File does not exist
        except PermissionError:
            return 108  # Wrong permission
    return 105    # File is not encrypted


def encrypt_pdf(file: str, password: str) -> int:
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


def decrypt_pdf(file: str, password: str) -> int:
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
