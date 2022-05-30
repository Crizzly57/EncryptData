import os
from time import time
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QFileDialog, QApplication, QMainWindow, QDialog
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QIcon
import sys
import Crypto


class Ui(QMainWindow, QDialog):
    def __init__(self):
        super(Ui, self).__init__()
        self.file_list = []
        self.password = ""
        self.enc_or_dec = ""
        self.setup_ui()
        self.start()

    def setup_ui(self):
        loadUi("GUI.ui", self)
        self.setWindowTitle("Daten schützen")
        self.setWindowIcon(QIcon("icon.png"))
        self.setFixedWidth(500)
        self.setFixedHeight(480)
        self.show()

    def start(self):
        self.files.clicked.connect(self.browsefiles)
        self.folder.clicked.connect(self.browsefolder)
        self.pass_input.textChanged.connect(self.on_text_changed)
        self.connect_to_get_password()

    def browsefiles(self):
        self.file_list = QFileDialog.getOpenFileNames(self, "Dateien öffnen", QDir.currentPath())
        if not self.file_list == ([], ''):
            self.message.clear()    # clear des Ausgabefeldes
            self.pass_input.setEnabled(True)
            self.file_list = self.file_list[0]  # tupel aus Liste und String
            for i, path in enumerate(self.file_list):   # Pfade formatieren
                self.file_list[i] = os.path.realpath(path)
            self.path.setText(os.path.dirname(self.file_list[0]) + "\\")   # Ordnerverzeichnis aller Dateien setzen

    def browsefolder(self):
        path = QFileDialog.getExistingDirectory(self, "Ordner öffnen", QDir.currentPath())
        if not path == "":
            self.message.clear()    # clear des Ausgabefeldes
            self.pass_input.setEnabled(True)
            path = os.path.realpath(path)   # Pfad formatieren
            self.path.setText(path)
            self.file_list = self.open_directory(path)

    def on_text_changed(self):
        self.ok_button.setEnabled(True)

    def get_password(self):
        self.check_enc_or_dec()
        if self.enc_or_dec == 'enc':
            self.password = self.pass_input.text()
            if self.check_password(self.password):
                self.password = self.pass_input.text()
                self.messages(1, "")  # Passwort gültig
                self.worker()
            else:
                self.messages(0, "")  # ungültiges Passwort
                self.pass_input.clear()  # clear Eingabefeld
        else:
            self.password = self.pass_input.text()
            self.worker()

    def connect_to_get_password(self):
        self.pass_input.returnPressed.connect(self.get_password)
        self.ok_button.clicked.connect(self.get_password)

    def check_enc_or_dec(self):
        while self.enc_or_dec == "":
            if self.enc.isChecked():
                self.enc_or_dec = "enc"
            elif self.dec.isChecked():
                self.enc_or_dec = "dec"
            else:
                self.messages(1, None)  # enc/dec nicht ausgewählt

    def messages(self, num, file):
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
            msg = "Passwort für Datei " + file + " ist falsch!"
            color = "red"
        elif num == 4:
            msg = "Datei " + file + " ist bereits verschlüsselt!"
            color = "red"
        elif num == 5:
            msg = "Datei " + file + " ist nicht verschlüsselt!"
            color = "red"
        elif num == 6:
            msg = "Vorgang abgeschlossen!"
            color = "green"
        self.change_color(color, msg)

    def change_color(self, color, msg):
        if color == "red":
            msg = '<span style=\" color: #ED422C;\">%s</span>' % msg
        elif color == "green":
            msg = '<span style=\" color: #2CA94F;\">%s</span>' % msg
        return self.message.append(msg)

    def worker(self):
        for file in self.file_list:
            if file.lower().endswith('.pdf'):
                if self.enc_or_dec == 'enc':
                    num = Crypto.encrypt_pdf(file, self.password)
                else:
                    num = Crypto.decrypt_pdf(file, self.password)
            else:
                if self.enc_or_dec == 'enc':
                    num = Crypto.encrypt(file, self.password)
                else:
                    num = Crypto.decrypt(file, self.password)
            self.messages(num, file)
        self.messages(6, "")
        self.clear_all()

    def clear_all(self):
        self.path.clear()
        self.pass_input.clear()
        self.password = ""
        self.enc_or_dec = ""

    def extend_dir(self, path_list, path):
        for i, item in enumerate(path_list):  # Dateiname durch den restlichen Pfad erweitern
            path_list[i] = path + "\\" + item
        return path_list

    def search_in_path(self, path, file_list):
        under_paths = []
        for i in path:  # Jedes Element in "path" überprüfen ob es ein Verzeichnis ist
            if os.path.isdir(i):
                temp_list = os.listdir(i)  # Liste aller Elemente des Verzeichnisses temporär abspeichern
                temp_list = self.extend_dir(temp_list, i)  # temporäre Liste erweitern durch den restlichen Pfad
                under_paths += temp_list  # temporäre Liste an "under_paths" anhängen
            else:
                file_list.append(i)

        if under_paths:
            return self.search_in_path(under_paths, file_list)  # rekursion der Funktion wenn ein weiteres Unterverzeichnis gefunden wurde
        else:
            return file_list

    def open_directory(self, path):
        file_list = []
        if os.path.isdir(path):  # Überprüfen ob "path" ein Verzeichnis ist
            liste = os.listdir(path)
            liste = self.extend_dir(liste, path)
            return self.search_in_path(liste, file_list)  # rekursive Funktion für das durchsuchen der Unterverzeichnisse aufrufen
        else:
            file_list.append(path)
            return file_list

    @staticmethod
    def check_password(password):
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Ui()
    sys.exit(app.exec_())

