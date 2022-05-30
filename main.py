"""
ToDo:
    - Drag & Drop
    - neue Class welche ein Drag n Drop Widget erstellt
    - Multiprocessing
    - CSS Styling
    - dash border
"""

import os
import sys
import crypt
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QDir
from PyQt6.uic import loadUi


class Ui(QMainWindow):
    """
    Methods
    -------
    setup_ui:
        UI laden und anpassungen an dieser vornehmen

    get_password:
        einlesen und überprüfung des Passworts. Aufruf des workers

    browse_files:
        Aufruf des Explorer Dialogs für einzelne oder mehrere Dateien

    browse_folder:
        Aufruf des Explorer Dialogs für ganze Ordner

    enable_ok_button:
        Aktivieren des O.K.-Buttons
    """
    def __init__(self):
        super(__class__, self).__init__()
        self.setup_ui()

        self.files.clicked.connect(self.browse_files)
        self.folder.clicked.connect(self.browse_folder)
        self.pass_input.textChanged.connect(self.enable_ok_button)

        self.pass_input.returnPressed.connect(self.get_password)
        self.ok_button.clicked.connect(self.get_password)

    def setup_ui(self):
        """UI laden und anpassungen an dieser vornehmen"""
        loadUi("GUI.ui", self)
        self.setWindowTitle("Daten schützen")
        self.setWindowIcon(QIcon("icon.png"))
        self.setFixedWidth(500)
        self.setFixedHeight(480)
        self.statusBar()

        # Erstellen einer Exit Action
        exit_button = QAction(QIcon('exit.png'), '&Exit', self)
        exit_button.setShortcut('Ctrl+Q')
        exit_button.setStatusTip('Beende Programm')
        exit_button.triggered.connect(app.quit)
        self.pass_input.setToolTip('Passwort Eingabe')

        # Erstellen einer Menübar
        mainmenu = self.menuBar()
        filemenu = mainmenu.addMenu('&Datei')
        filemenu.addAction(exit_button)
        self.show()

    def get_password(self):
        """einlesen und überprüfung des Passworts. Aufruf des workers"""
        password = self.pass_input.text()
        if Main.check_password(password):
            # Passwort gültig
            Main.messages(main, 1, '')
            Main.worker(main, password)
        else:
            # Passwort entspricht nicht den Kriterien
            Main.messages(main, 0, '')
            self.pass_input.clear()

    def browse_files(self):
        """Aufruf des Explorer Dialogs für einzelne oder mehrere Dateien"""
        file_list = QFileDialog.getOpenFileNames(self, "Dateien öffnen", QDir.currentPath())
        if not file_list == ([], ''):
            file_list = file_list[0]
            main.checking_files(file_list)

    def browse_folder(self):
        """Aufruf des Explorer Dialogs für ganze Ordner"""
        path = QFileDialog.getExistingDirectory(self, "Ordner öffnen", QDir.currentPath())
        if path:
            Main.checking_folder(main, path)

    def enable_ok_button(self):
        """Aktivieren des O.K.-Buttons"""
        self.ok_button.setEnabled(True)


class Main:
    """
    Methods
    --------
    checking_folder(path: str):
        start der Suche nach Dateien im ausgewähltem Ordner

    checking_files(file_list: list):
        Formatierung der einzelnen Pfade von den Dateien
        Den ausgewählten Pfad in der UI setzen,
        abhängig davon ob nur eine Datei ausgewählt wurde oder mehrere

    clear_message:
        Ablöschen des Nachrichten Ausgabefeldes. Freischalten der Passworteingabe

    open_directory(path: str):
        Überprüfung ob path ein Verzeichnis ist.
        Anschließender Aufruf der search_in_folder Methode

    search_in_folder(path: str):
        Durchsuchen des Ordners nach Dateien und nach Unterordnern.
        In den Unterordnern ebenfalls nach Dateien suchen.
        Die Pfade dieser Dateien, werden alle in file_list geschrieben

    check_enc_or_dec(password: str):
        Einlesen ob enc oder dec ausgewählt ist in der Ui.
        Passwort überprüfen, ob es den Kriterien entspricht.
        Wenn es nicht den Kriterien entspricht,
        die Methode messages mit 0 aufrufen, ansonsten mit 1.

    messages(num: int, file: str):
        Erzeugen der auszugebenden Nachricht. Auf Basis der num und der file

    change_color(color: str, msg: str):
        Ändern der Farbe der auszugebenden Nachricht

    clear_all():
        ablöschen des Pfadanzeigefeldes und der Passworteingabe

    extend_dir(path: str):
        Dateiname durch den restlichen Pfad erweitern

    check_password(password: str):
        überprüfung des Passworts ob es den vordefinierten Kriterien entspricht

    """
    def __init__(self):
        """Initialisieren einer leeren Liste für die Dateipfade"""
        self.file_list = []

    def checking_folder(self, path: str):
        """start der Suche nach Dateien im ausgewähltem Ordner"""
        self.clear_message()
        path = os.path.realpath(path)
        w.path.setText(path)
        self.open_directory(path)

    def checking_files(self, file_list: list):
        """
        Formatierung der einzelnen Pfade von den Dateien
        Den ausgewählten Pfad in der UI setzen,
        abhängig davon ob nur eine Datei ausgewählt wurde oder mehrere
        """
        self.clear_message()
        self.file_list = [os.path.realpath(path) for path in file_list]
        if len(self.file_list) == 1:
            w.path.setText(os.path.dirname(self.file_list[0]) + "\\" +
                           os.path.basename(self.file_list[0]))
        else:
            w.path.setText(os.path.dirname(self.file_list[0]) + "\\")

    @staticmethod
    def clear_message():
        """Ablöschen des Nachrichten Ausgabefeldes. Freischalten der Passworteingabe"""
        w.message.clear()
        w.pass_input.setEnabled(True)

    def open_directory(self, path: str):
        """
        Überprüfung ob path ein Verzeichnis ist.
        Anschließender Aufruf der search_in_folder Methode
        """
        liste = os.listdir(path)
        liste = self.extend_dir(liste, path)
        self.search_in_folder(liste)

    def search_in_folder(self, paths: list):
        """
        Durchsuchen des Ordners nach Dateien und nach Unterordnern.
        In den Unterordnern ebenfalls nach Dateien suchen.
        Die Pfade dieser Dateien, werden alle in file_list geschrieben
        """
        while paths:
            under_paths = []
            for path in paths:
                if os.path.isdir(path):
                    temp_list = os.listdir(path)
                    temp_list = self.extend_dir(temp_list, path)
                    under_paths += temp_list
                else:
                    self.file_list.append(path)
            if under_paths:
                paths = under_paths
            else:
                break

    def check_enc_or_dec(self, password: str) -> tuple:
        """
        Einlesen ob enc oder dec ausgewählt ist in der Ui.
        Passwort überprüfen, ob es den Kriterien entspricht.
        Wenn es nicht den Kriterien entspricht,
        die Methode messages mit 0 aufrufen, ansonsten mit 1.
        """
        if w.enc.isChecked():
            enc_or_dec = 'enc'
        else:
            enc_or_dec = 'dec'
        if not self.check_password(password):
            self.messages(0, '')
            state = False
        else:
            w.pass_input.clear()
            self.messages(1, '')
            state = True
        return enc_or_dec, state

    def messages(self, num: int, file: str):
        """Erzeugen der auszugebenden Nachricht. Auf Basis der num und der file"""
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
            msg = f"Passwort für Datei {os.path.basename(file)} ist falsch!"
            color = "red"
        elif num == 4:
            msg = f"Datei {os.path.basename(file)} ist bereits verschlüsselt!"
            color = "red"
        elif num == 5:
            msg = f"Datei {os.path.basename(file)} ist nicht verschlüsselt!"
            color = "red"
        elif num == 6:
            msg = "Vorgang abgeschlossen!"
            color = "green"
        self.change_color(color, msg)

    @staticmethod
    def change_color(color: str, msg: str):
        """Ändern der Farbe der auszugebenden Nachricht"""
        if color == "red":
            msg = f'<span style=\" color: #ED422C;\">{msg}</span>'
        elif color == "green":
            msg = f'<span style=\" color: #2CA94F;\">{msg}</span>'
        w.message.append(msg)

    @staticmethod
    def clear_all():
        """ablöschen des Pfadanzeigefeldes und der Passworteingabe"""
        w.path.clear()
        w.pass_input.clear()

    @staticmethod
    def extend_dir(path_list: list, path: str):
        """Dateiname durch den restlichen Pfad erweitern"""
        path_list = [path + "\\" + item for item in path_list]
        return path_list

    @staticmethod
    def check_password(password: str):
        """überprüfung des Passworts ob es den vordefinierten Kriterien entspricht"""
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
        return val

    def worker(self, password: str):
        """
        Abfrage ob verschlüsseln oder entschlüsseln in der UI ausgewählt wurde.
        Aufruf der verschlüsselungs/entschlüsselungs Algorithmen in der Datei crypt.
        Setzen der Statusmeldungen in der UI über die Methode messages.
        """
        enc_or_dec, state = self.check_enc_or_dec(password)
        if not state:
            for file in self.file_list:
                if file.lower().endswith('.pdf') and enc_or_dec == 'enc':
                    num = crypt.encrypt_pdf(file, password)
                elif file.lower().endswith('.pdf') and enc_or_dec == 'dec':
                    num = crypt.decrypt_pdf(file, password)
                elif enc_or_dec == 'enc':
                    num = crypt.encrypt(file, password)
                else:
                    num = crypt.decrypt(file, password)
                self.messages(num, file)
            # Setzen der Statusmeldung "Fertig"
            self.messages(6, '')
            self.clear_all()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    with open("Stylesheet.css", "r") as stylesheet:
        stylesheet = stylesheet.read()
        app.setStyleSheet(stylesheet)
    w = Ui()
    main = Main()
    sys.exit(app.exec())
