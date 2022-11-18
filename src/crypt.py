"""
Author: Sven Kleinhans
"""

import base64
import os

from PIL import Image, UnidentifiedImageError
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pikepdf import Pdf, Encryption, PasswordError

MAGIC_STRING = b"ENCRYPTED"


class Crypt:
    def __init__(self, file: str, password: str, encryption: bool):
        self.file = file
        self.password = password
        self.encryption = encryption

    def start(self):
        if self.encryption:
            return self.encrypt()
        else:
            return self.decrypt()

    def get_hashed_pass(self) -> bytes:
        digest = hashes.Hash(hashes.SHA512())
        digest.update(self.password.encode())
        return digest.finalize()

    def make_encrypted_file(self) -> str:
        name, end = os.path.splitext(os.path.basename(self.file))
        new_string = name + "_encrypted" + end
        return os.path.dirname(self.file) + "\\" + new_string

    def make_decrypted_file(self) -> str:
        name = os.path.basename(self.file)
        if "_encrypted" in name:
            return os.path.dirname(self.file) + "\\" + name.replace("_encrypted", "")
        return self.file

    def check_encryption(self) -> bool:
        with open(self.file, "rb") as file:
            header = file.read(len(MAGIC_STRING))
        return MAGIC_STRING == header

    def encrypt(self) -> int:
        fernet = Fernet(self._gen_key())
        if not self.check_encryption():
            try:
                with open(self.file, "rb") as input_file, open(self.make_encrypted_file(), "wb") as out:
                    data = self.get_hashed_pass() + input_file.read()
                    encrypted_data = fernet.encrypt(data)
                    out.write(MAGIC_STRING)
                    out.write(encrypted_data)
                return 4  # File successfully encrypted
            except FileNotFoundError:
                return 101  # File does not exist
            except PermissionError:
                return 108  # Wrong permission
        return 104  # File is not encrypted

    def decrypt(self) -> int:
        fernet = Fernet(self._gen_key())
        if self.check_encryption():
            try:
                with open(self.file, "rb") as input_file, open(self.make_decrypted_file(), 'wb') as out:
                    encrypted_data = input_file.read()[len(MAGIC_STRING):]
                    decrypted_data = fernet.decrypt(encrypted_data)
                    hashed_pass = decrypted_data[:64]
                    if hashed_pass == self.get_hashed_pass():
                        out.write(decrypted_data[64:])
                        return 3  # File successfully decrypted
                    return 103  # Wrong password
            except InvalidToken:
                return 103  # Wrong password
            except FileNotFoundError:
                return 101  # File does not exist
            except PermissionError:
                return 108  # Wrong permission
        return 105  # File is not encrypted

    def _gen_key(self, length: int = 32) -> bytes:
        salt = b'\x81\xd2n\xb1!\xcd\xa9\xd7n\xda\x89u\xfe`\x9a\xd8'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=length,
            salt=salt,
            iterations=100000
        )
        return base64.urlsafe_b64encode(kdf.derive(key_material=self.password.encode()))


class PDFHandler(Crypt):
    def __init__(self, **kwargs):
        super(PDFHandler, self).__init__(**kwargs)

    def start(self):
        if self.encryption:
            return self.encrypt()
        else:
            return self.decrypt()

    def encrypt(self) -> int:
        try:
            with Pdf.open(os.path.normpath(self.file)) as input_file:
                input_file.save(self.make_encrypted_file(),
                                encryption=Encryption(owner=self.password, user=self.password))
            return 4  # File successfully encrypted
        except PasswordError:
            return 104  # File already encrypted
        except FileNotFoundError:
            return 101  # File does not exist
        except PermissionError:
            return 108  # Wrong permission

    def decrypt(self) -> int:
        try:
            with Pdf.open(os.path.normpath(self.file), password=self.password) as input_file:
                if input_file.is_encrypted:
                    input_file.save(self.make_decrypted_file())
                    return 3  # File successfully decrypted
                return 105  # File is not encrypted
        except PasswordError:
            return 103  # Wrong password
        except FileNotFoundError:
            return 101  # File does not exist
        except PermissionError:
            return 108  # Wrong permission


class ImageHandler(Crypt):
    def __init__(self, **kwargs):
        super(ImageHandler, self).__init__(**kwargs)
        self.data = bytes()

    def start(self):
        return self.process_image()

    def process_image(self):
        try:
            img = Image.open(self.file)
        except FileNotFoundError:
            return 101  # File does not exist
        except UnidentifiedImageError:
            return 107  # Path reference invalid

        self.data = img.convert("RGB").tobytes()

        original = len(self.data)
        self.data = self.pad(self.data)

        if self.encryption:
            new_data = self.encrypt()
            out_path = self.make_encrypted_file()
        else:
            new_data = self.decrypt()
            out_path = self.make_decrypted_file()
        new_img = self.convert_to_rgb(new_data[:original])

        img2 = Image.new("RGB", img.size)
        img2.putdata(new_img)
        img2.save(f"{out_path}", img.format)

    def encrypt(self):
        aes = Cipher(algorithms.AES(self._gen_key(length=16)), modes.CBC(self.get_initialization_vector()))
        encryptor = aes.encryptor()
        new_data = encryptor.update(self.data) + encryptor.finalize()
        return new_data

    def decrypt(self):
        aes = Cipher(algorithms.AES(self._gen_key(length=16)), modes.CBC(self.get_initialization_vector()))
        decryptor = aes.decryptor()
        new_data = decryptor.update(self.data) + decryptor.finalize()
        return new_data

    @staticmethod
    def convert_to_rgb(data):
        r, g, b = tuple(map(lambda d: [data[i] for i in range(0, len(data)) if i % 3 == d], [0, 1, 2]))
        pixels = tuple(zip(r, g, b))
        return pixels

    @staticmethod
    def get_initialization_vector():
        return os.urandom(16)

    @staticmethod
    def pad(data):
        # AES requires that plaintexts be a multiple of 16, so we have to pad the data
        return data + b"\x00" * (16 - len(data) % 16)
