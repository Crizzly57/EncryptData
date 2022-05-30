"""
Dieses Modul beinhaltet alle Algorithmen und Funktionen um Dateien und PDF Dokumente,
zu verschlüsseln oder zu entschlüsseln.
Benutzt werden hier die Module Cryptography und PikePDF.
"""
import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pikepdf import Pdf, Encryption, PasswordError


def gen_key(password: bytes) -> bytes:
    """Generierung des Keys. Salt mit os.urandom(16) erzeugt"""
    salt = b'\x81\xd2n\xb1!\xcd\xa9\xd7n\xda\x89u\xfe`\x9a\xd8'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA512(),
        length=32,
        salt=salt,
        iterations=100000
    )
    return base64.urlsafe_b64encode(kdf.derive(key_material=password))


def make_encrypted_file(path: str) -> str:
    """verschlüsselte Datei schreiben. Suffix _encrypted hinzufügen"""
    name, end = os.path.splitext(os.path.basename(path))
    new_string = name + "_encrypted" + end
    return os.path.dirname(path) + "\\" + new_string


def make_decrypted_file(path: str) -> str:
    """entschlüsselte Datei schreiben und Suffix _encrypted entfernen"""
    name = os.path.basename(path)
    new_string = name.replace("_encrypted", "")
    return os.path.dirname(path) + "\\" + new_string


def check_encryption(path: str) -> bool:
    """überprüfung ob Datei verschlüsselt ist, anhang vom Suffix _encrypted"""
    file_name = os.path.basename(path)
    return bool("_encrypted" in file_name)


def encrypt(file: str, password: str) -> int:
    """
    verschlüsseln der Datei mit dem Modul Cryptography.
    Key wird erzeugt, danach eine neue Datei erstellt
    und in diese die verschlüsselten Daten geschrieben.
    Falls Datei bereits verschlüsselt ist, return code an den worker
    """
    fernet = Fernet(gen_key(password.encode()))
    if not check_encryption(file):
        with open(file, "rb") as input_file:
            file_data = input_file.read()
            encrypted_data = fernet.encrypt(file_data)
        with open(make_encrypted_file(file), "wb") as out:
            out.write(encrypted_data)
        # Datei erfolgreich verschlüsselt
        num = 8
    else:
        # Datei in "xy" ist schon verschlüsselt
        num = 4
    return num


def decrypt(file: str, password: str) -> int:
    """
    entschlüsseln einer Datei mit dem Modul Cryptography.
    Key wird erzeugt und mit diesem wird versucht die Datei zu entschlüsseln.
    Return codes an den worker falls nicht verschlüsselt oder das falsche Passwort eingegeben wurde
    """
    fernet = Fernet(gen_key(password.encode()))
    if check_encryption(file):
        with open(file, "rb") as input_file:
            encrypted_data = input_file.read()
            try:
                decrypted_data = fernet.decrypt(encrypted_data)
                with open(make_decrypted_file(file), 'wb') as out:
                    out.write(decrypted_data)
                # Datei erfolgreich entschlüsselt
                num = 7
            except InvalidToken:
                # Flasches Passwort für Datei in "xy"
                num = 3
    else:
        # Datei in "xy" ist nicht verschlüsselt
        num = 5
    return num


def encrypt_pdf(file, password: str) -> int:
    """
    Falls eine PDF erkannt wurde, wird diese Funktion benutzt.
    PDF mit dem Modul PikePDF öffnen und diese wieder verschlüsselt speichern.
    Return code an den worker falls PDF bereits verschlüsselt ist
    """
    out_path = make_encrypted_file(file)
    try:
        with Pdf.open(os.path.normpath(file)) as input_file:
            input_file.save(out_path, encryption=Encryption(owner=password, user=password))
        os.remove(file)
        # Datei erfolgreich verschlüsselt
        num = 8
    except PasswordError:
        # Datei in "xy" ist schon verschlüsselt
        num = 4
    return num


def decrypt_pdf(file, password: str) -> int:
    """
    Falls eine PDF erkannt wurde, wird diese Funktion benutzt.
    PDF mit dem Modul PikePDF öffnen und diese wieder entschlüsselt speichern.
    Return code an den worker falls PDF nicht verschlüsselt ist oder,
    das falsche Passwort eingeben wurde
    """
    out_path = make_decrypted_file(file)
    try:
        with Pdf.open(os.path.normpath(file), password) as input_file:
            if input_file.is_encrypted:
                input_file.save(out_path)
                os.remove(file)
                # Datei erfolgreich entschlüsselt
                num = 7
            else:
                # Datei ist nicht verschlüsselt
                num = 5
    except PasswordError:
        # Falsches Passwort
        num = 3
    return num
