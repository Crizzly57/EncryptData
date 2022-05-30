from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from PyPDF2 import PdfFileReader
from PyPDF2 import utils
from PyPDF2 import PdfFileWriter
import os


def gen_key(password):
    salt = b'\x81\xd2n\xb1!\xcd\xa9\xd7n\xda\x89u\xfe`\x9a\xd8'  # Mit os.urandom(16) erzeugt

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA512(),
        length=32,
        salt=salt,
        iterations=100000
    )
    return base64.urlsafe_b64encode(kdf.derive(key_material=password))


def make_encrypted_file(path):
    name, end = os.path.splitext(os.path.basename(path))
    new_string = name + "_encrypted" + end          # '_encrypted' hinzufügen
    os.remove(path)                                 # löschen der alten Datei
    return os.path.dirname(path) + "\\" + new_string


def make_decrypted_file(path):
    name = os.path.basename(path)
    new_string = name.replace("_encrypted", "")     # '_encrypted' entfernen
    os.remove(path)                                 # löschen der alten Datei
    return os.path.dirname(path) + "\\" + new_string


def check_encryption(path):
    file_name = os.path.basename(path)
    if "_encrypted" in file_name:
        return True
    else:
        return False


def encrypt(file, password):
    f = Fernet(gen_key(password.encode()))
    if not check_encryption(file):
        with open(file, "rb") as input_file:
            file_data = input_file.read()
            encrypted_data = f.encrypt(file_data)
            input_file.close()

        with open(make_encrypted_file(file), "wb") as out:
            out.write(encrypted_data)
            out.close()
    else:
        return 4  # Datei in "xy" ist schon verschlüsselt


def decrypt(file, password):
    f = Fernet(gen_key(password.encode()))
    if check_encryption(file):
        with open(file, "rb") as input_file:
            encrypted_data = input_file.read()
            try:
                decrypted_data = f.decrypt(encrypted_data)
                input_file.close()
                with open(make_decrypted_file(file), 'wb') as out:
                    out.write(decrypted_data)
                    out.close()

            except InvalidToken:
                return 3    # Flasches Passwort für Datei in "xy"
            input_file.close()
    else:
        return 5    # Datei in "xy" ist nicht verschlüsselt


def encrypt_pdf(file, password):
    file_data = PdfFileReader(file)
    if not file_data.isEncrypted:
        encrypted_data = PdfFileWriter()
        encrypted_data.appendPagesFromReader(file_data)
        encrypted_data.encrypt(password)

        with open(make_encrypted_file(file), 'wb') as out_file:
            encrypted_data.write(out_file)
    else:
        return 4  # Datei in "xy" ist schon verschlüsselt


def decrypt_pdf(file, password):
    out = PdfFileWriter()
    file_data = PdfFileReader(file)
    if file_data.isEncrypted:
        try:
            file_data.decrypt(password)
            for i in range(file_data.numPages):
                page = file_data.getPage(i)
                out.addPage(page)

            with open(make_decrypted_file(file), "wb") as out_file:
                out.write(out_file)
        except utils.PdfReadError:
            return 3  # Flasches Passwort für Datei in "xy"
    else:
        return 5  # Datei in "xy" ist nicht verschlüsselt
