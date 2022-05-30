import os
from time import time
from psutil import cpu_count
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QFileDialog, QApplication, QMainWindow, QDialog
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QIcon
import math
import multiprocessing as mp
from multiprocessing import freeze_support
import sys
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from pikepdf import Pdf, Encryption, PasswordError


class Ui(QMainWindow, QDialog):
    # Initializerien
    def __init__(self):
        super(Ui, self).__init__()
        self.file_list = []
        self.password = ""
        self.enc_or_dec = ""
        self.setup_ui()
        self.start()

    # Anzeigen der UI
    def setup_ui(self):
        loadUi("GUI.ui", self)
        self.setWindowTitle("Daten schützen")
        self.setWindowIcon(QIcon("icon.png"))
        self.setFixedWidth(500)
        self.setFixedHeight(480)
        self.show()

    # Aufruf der jeweiligen action, ob ganzer Ordner oder einzelne Datei / Dateien ausgewählt werden sollen
    def start(self):
        self.files.clicked.connect(self.browse_files)
        self.folder.clicked.connect(self.browse_folder)
        self.pass_input.textChanged.connect(self.enable_ok_button)
        self.connect_to_get_password()

    # Aufruf des Explorer Dialogs für einzelne oder mehrere Dateien
    def browse_files(self):
        self.file_list = QFileDialog.getOpenFileNames(self, "Dateien öffnen", QDir.currentPath())
        # clear des Ausgabefeldes
        self.message.clear()
        self.pass_input.setEnabled(True)
        # tupel aus Liste und String auflösen
        self.file_list = self.file_list[0]
        # Pfade formatieren
        for i, path in enumerate(self.file_list):
            self.file_list[i] = os.path.realpath(path)
        # Überprüfung ob nur eine Datei ausgewählt wurde, dann exakt diesen Pfad angeben
        if len(self.file_list) == 1:
            self.path.setText(os.path.dirname(self.file_list[0]) + "\\" + os.path.basename(self.file_list[0]))
        else:
            # Ordnerverzeichnis aller Dateien setzen
            self.path.setText(os.path.dirname(self.file_list[0]) + "\\")

    # Aufruf des Explorer Dialogs für ganze Ordner
    def browse_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Ordner öffnen", QDir.currentPath())
        # clear des Ausgabefeldes
        self.message.clear()
        self.pass_input.setEnabled(True)
        # Pfad formatieren
        path = os.path.realpath(path)
        self.path.setText(path)
        self.open_directory(path)

    # Hilfsfunktion für das aktivieren des O.K.-Buttons
    def enable_ok_button(self):
        self.ok_button.setEnabled(True)

    # Einlesen des Passworts
    def get_password(self):
        self.check_enc_or_dec()
        self.password = self.pass_input.text()
        if self.enc_or_dec == 'enc':
            if self.check_password(self.password):
                # Passwort gültig
                self.messages(1, "")
                # Start der verschlüsselung
                self.worker()
            else:
                # ungültiges Passwort
                self.messages(0, "")
                # clear Eingabefeld
                self.pass_input.clear()
        else:
            # Start der entschlüsselung
            self.worker()

    # Hilfsfunktion für das einlesen des Passworts
    def connect_to_get_password(self):
        self.pass_input.returnPressed.connect(self.get_password)
        self.ok_button.clicked.connect(self.get_password)

    # Überprüfung ob verschlüsselt oder entschlüsselt werden soll
    def check_enc_or_dec(self):
        if self.enc.isChecked():
            self.enc_or_dec = "enc"
        elif self.dec.isChecked():
            self.enc_or_dec = "dec"

    # Statusmeldung für die UI
    def messages(self, num: int, file: str):
        color = ""
        msg = ""
        if num == 0:
            msg = "Passwort entspricht nicht den Kriterien!"
            color = "red"
        elif num == 1:
            msg = "Passwort gültig!"
            color = "green"
        elif num == 2:
            msg = "Verschlüsseln oder Entschlüsseln auswählen!"
            color = "red"
        elif num == 3:
            msg = "Passwort für Datei " + os.path.basename(file) + " ist falsch!"
            color = "red"
        elif num == 4:
            msg = "Datei " + os.path.basename(file) + " ist bereits verschlüsselt!"
            color = "red"
        elif num == 5:
            msg = "Datei " + os.path.basename(file) + " ist nicht verschlüsselt!"
            color = "red"
        elif num == 6:
            msg = "Vorgang abgeschlossen!"
            color = "green"
        self.change_color(color, msg)

    # Wechsel der Schriftfarbe für die Statusmeldungen
    def change_color(self, color: str, msg: str):
        if color == "red":
            msg = '<span style=\" color: #ED422C;\">%s</span>' % msg
        elif color == "green":
            msg = '<span style=\" color: #2CA94F;\">%s</span>' % msg
        self.message.append(msg)

    # Ablöschen aller Inputparameter
    def clear_all(self):
        self.path.clear()
        self.pass_input.clear()
        self.password = ""
        self.enc_or_dec = ""

    # Einzelne Dateiname mit Ursprungspfad zusammenfügen
    @staticmethod
    def extend_dir(path_list: list, path: str):
        # Dateiname durch den restlichen Pfad erweitern
        for i, item in enumerate(path_list):
            path_list[i] = path + "\\" + item
        return path_list

    # Suchalgorithmus für die Ordnerstruktur
    def search_in_path(self, paths: list):
        under_paths = []
        # Jedes Element in "path" überprüfen ob es ein Verzeichnis ist
        for i in paths:
            if os.path.isdir(i):
                # Liste aller Elemente des Verzeichnisses temporär abspeichern
                temp_list = os.listdir(i)
                # temporäre Liste erweitern durch den restlichen Pfad
                temp_list = self.extend_dir(temp_list, i)
                # temporäre Liste an "under_paths" anhängen
                under_paths += temp_list
            else:
                self.file_list.append(i)
        if under_paths:
            # rekursion der Funktion wenn ein weiteres Unterverzeichnis gefunden wurde
            return self.search_in_path(under_paths)

    # Öffnen des ausgewählten Ordners
    def open_directory(self, path: str):
        # Überprüfen ob "path" ein Verzeichnis ist
        liste = os.listdir(path)
        liste = self.extend_dir(liste, path)
        # rekursive Funktion für das durchsuchen der Unterverzeichnisse aufrufen
        self.search_in_path(liste)

    # Überprüfung des Passworts, ob es den Kriterien entspricht
    @staticmethod
    def check_password(password: str):
        special_sym = ['#', '%', '@', '$']
        val = True
        if len(password) < 10:
            val = False
        if not any(char.isdigit() for char in password):
            val = False
        if not any(char.isupper() for char in password):
            val = False
        if not any(char.islower() for char in password):
            val = False
        if not any(char in special_sym for char in password):
            val = False
        if val:
            return val

    def worker(self):
        for file in self.file_list:
            # Überprüfung ob Datei mit ".pdf" endet
            if file.lower().endswith('.pdf') and self.enc_or_dec == 'enc':
                num = encrypt_pdf(file, self.password)
            elif file.lower().endswith('.pdf') and self.enc_or_dec == 'dec':
                num = decrypt_pdf(file, self.password)
            elif self.enc_or_dec == 'enc':
                num = encrypt(file, self.password)
            else:
                num = decrypt(file, self.password)
            # Ausgabe der jeweiligen Statusmeldung
            self.messages(num, file)
        # Setzen der Statusmeldung "Fertig"
        self.messages(6, "")
        self.clear_all()


# Generierung des Keys
def gen_key(password: bytes):
    # Mit os.urandom(16) erzeugt
    salt = b'\x81\xd2n\xb1!\xcd\xa9\xd7n\xda\x89u\xfe`\x9a\xd8'

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA512(),
        length=32,
        salt=salt,
        iterations=100000
    )
    return base64.urlsafe_b64encode(kdf.derive(key_material=password))


# Verschlüsselte Datei schreiben
def make_encrypted_file(path: str):
    name, end = os.path.splitext(os.path.basename(path))
    # '_encrypted' hinzufügen
    new_string = name + "_encrypted" + end

    return os.path.dirname(path) + "\\" + new_string


# Entschlüsselte Datei schreiben
def make_decrypted_file(path: str):
    name = os.path.basename(path)
    # '_encrypted' entfernen
    new_string = name.replace("_encrypted", "")
    # löschen der alten Datei
    os.remove(path)
    return os.path.dirname(path) + "\\" + new_string


# "schlechte" Überprüfung ob Datei verschlüsselt ist
def check_encryption(path: str):
    file_name = os.path.basename(path)
    if "_encrypted" in file_name:
        return True
    else:
        return False


# verschlüsseln der Datei
def encrypt(file: str, password: str):
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
        # Datei in "xy" ist schon verschlüsselt
        return 4


# entschlüsseln einer Datei
def decrypt(file: str, password: str):
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
                # Flasches Passwort für Datei in "xy"
                return 3
            input_file.close()
    else:
        # Datei in "xy" ist nicht verschlüsselt
        return 5


# Verschlüsseln einer PDF
def encrypt_pdf(file: str, password: str):
    out_path = make_encrypted_file(file)
    try:
        with Pdf.open(os.path.normpath(file)) as input_file:
            input_file.save(out_path, encryption=Encryption(owner=password, user=password))
            # löschen der alten Datei
            os.remove(input_file)
    except PasswordError:
        # Datei in "xy" ist schon verschlüsselt
        return 4
    input_file.close()


# Entschlüsseln einer PDF
def decrypt_pdf(file: str, password: str):
    out_path = make_decrypted_file(file)
    try:
        with Pdf.open(os.path.normpath(file), password) as input_file:
            if input_file.is_encrypted:
                input_file.save(out_path)
                # löschen der alten Datei
                os.remove(input_file)
            else:
                # Datei ist nicht verschlüsselt
                return 5
    except PasswordError:
        # Falsches Passwort
        return 3
    input_file.close()

# Modul: PyPDF2
""" 
def encrypt_pdf(file, password):
    file_data = PdfFileReader(file)
    if not file_data.isEncrypted:
        encrypted_data = PdfFileWriter()
        encrypted_data.appendPagesFromReader(file_data)
        encrypted_data.encrypt(password)

        with open(make_encrypted_file(file), 'wb') as out_file:
            encrypted_data.write(out_file)
            # löschen der alten Datei
            os.remove(file)
    else:
        # Datei in "xy" ist schon verschlüsselt
        return 4  


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
                # löschen der alten Datei
                os.remove(file)
        except utils.PdfReadError:
            # Flasches Passwort für Datei in "xy"
            return 3  
    else:
        # Datei in "xy" ist nicht verschlüsselt
        return 5  
"""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Ui()
    sys.exit(app.exec_())
