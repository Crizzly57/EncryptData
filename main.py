"""
ToDo:
    - Multiprocessing
    - CSS Styling
    - dash border
"""

import os
import sys
import crypt
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon, QAction, QDropEvent, QDragEnterEvent, QDragMoveEvent, QFont, QPalette, QBrush, QColor
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.uic import loadUi


class DragDrop(QListWidget):
    """
    Methods
    -------
    dragEnterEvent(event: QDragEnterEvent):
        Überprüfung ob gedroppte Daten dem Format Urls entsprechen.
        Dem Widget wird hierdurch gesagt welche Daten es bekommt.

    dragMoveEvent(event: QDragMoveEvent):
        Dem Widget wird gesagt, dass das Drag Event im gange ist.
        Wird außerdem benötigt, dass die Funktion "dropEvent" aufgerufen wird.

    dropEvent(event: QDropEvent):
        Auswerten der gedroppten Daten und diese ins richtige Format konvertieren.
        Falls eine Verknüpfung gedroppt wurde, Fehlermeldung generieren.
        Items in die QWidgetListe einfügen und in die self.paths Liste.

    check_typ():
        überprüfung ob url ein Ordner oder eine Datei ist und entsprechendes Icon setzen.

    get_paths():
        Gibt die Pfade an die Main-Klasse zurück.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.paths = []

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """
        Überprüfung ob gedroppte Daten dem Format Urls entsprechen.
        Dem Widget wird hierdurch gesagt welche Daten es bekommt.
        """
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        """
        Dem Widget wird gesagt, dass das Drag Event im gange ist.
        Wird außerdem benötigt, dass die Funktion "dropEvent" aufgerufen wird.
        """
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        """
        Auswerten der gedroppten Daten und diese ins richtige Format konvertieren.
        Falls eine Verknüpfung gedroppt wurde, Fehlermeldung generieren.
        Items in die QWidgetListe einfügen und in die self.paths Liste.
        """
        if event.mimeData().hasUrls():
            event.accept()
            for url in event.mimeData().urls():
                if url.toLocalFile() not in self.paths and not url.toLocalFile().endswith(
                        ".lnk") and os.path.exists(url.toLocalFile()):
                    item = QListWidgetItem(url.toLocalFile())
                    item.setCheckState(Qt.CheckState.Unchecked)
                    item.setIcon(QIcon(self.check_typ(url.toLocalFile())))
                    self.addItem(item)
                    self.paths.append(url.toLocalFile())
                else:
                    main.messages(9, url.toLocalFile())
        else:
            event.ignore()

    @staticmethod
    def check_typ(url: str) -> str:
        """überprüfung ob url ein Ordner oder eine Datei ist und entsprechendes Icon setzen."""
        if os.path.isdir(url):
            return r"icon\folder.ico"
        return r"icon\file.ico"

    def get_paths(self) -> list:
        """Gibt die Pfade an die Main-Klasse zurück."""
        return self.paths


class Ui(QMainWindow):
    """
    Methods
    -------
    setup_ui():
        UI laden und anpassungen an dieser vornehmen.

    show_info():
        Anzeigen des Info Festers und formatieren von diesem.

    get_password():
        einlesen und überprüfung des Passworts. Aufruf des workers

    remove_all_items():
        Alle Items im QListWidget löschen.

    remove_selected_items():
        Alle ausgewählten Items im QListWidget löschen.
    """

    def __init__(self):
        super().__init__()
        loadUi("GUI.ui", self)
        self.setup_ui()
        self.pass_input.textChanged.connect(lambda: self.start_button.setEnabled(True))
        self.remove_all.clicked.connect(self.remove_all_items)
        self.remove_selected.clicked.connect(self.remove_selected_items)

    def setup_ui(self) -> None:
        """UI laden und anpassungen an dieser vornehmen."""
        self.setWindowIcon(QIcon(r"icon\icon.png"))

        # Erstellen einer Exit Action
        exit_button = QAction(QIcon(r'icon\exit.png'), '&Exit', self)
        exit_button.setShortcut('Ctrl+Q')
        exit_button.setStatusTip('Beende Programm')
        exit_button.triggered.connect(app.quit)

        # Erstellen einer Info Action
        info_button = QAction(QIcon(r'icon\Info.png'), 'Info', self)
        info_button.setShortcut('Ctrl+I')
        info_button.setStatusTip('Zeige Info über Programm')
        info_button.triggered.connect(self.show_info)

        # Erstellen einer Menübar
        mainmenu = self.menuBar()
        filemenu = mainmenu.addMenu('&Datei')
        filemenu.setObjectName("filemenu")
        helpmenu = mainmenu.addMenu('&Hilfe')
        helpmenu.setObjectName("helpmenu")
        filemenu.addAction(exit_button)
        helpmenu.addAction(info_button)
        self.show()

    @staticmethod
    def show_info() -> None:
        """Anzeigen des Info Festers und formatieren von diesem."""
        info_message = QMessageBox()
        info_message.setWindowIcon(QIcon("icon\\Info.png"))
        info_message.setWindowTitle("Info")
        info_message.setText("1. Datei oder Verzeichnis auswählen\n"
                             "2. Wählen zwischen entschlüsseln und verschlüsseln\n"
                             "3. Passwort eingeben\n"
                             "Ein sicheres Passwort muss mindestens:\n"
                             "  - 10 Zeichen beinhalten\n"
                             "  - Einen Groß- und Kleinbuchstaben beinhalten\n"
                             "  - Ein '#', '%', '@' oder '$' beinhalten\n")
        info_message.show()
        info_message.exec()

    def remove_all_items(self) -> None:
        """Alle Items im QListWidget löschen."""
        self.drop_data.clear()
        self.drop_data.paths = []

    def remove_selected_items(self) -> None:
        """Alle ausgewählten Items im QListWidget löschen."""
        for i in range(self.drop_data.count()):
            if self.drop_data.item(i).checkState() == Qt.CheckState.Checked:
                self.drop_data.takeItem(i)  # Item aus dem QListWidget löschen
                del self.drop_data.paths[i]  # Item aus der self.paths Liste löschen


class Main:
    """
    Methods
    --------
    worker():
        Aufruf der Funktion "get_inputs", um die Pfade und das Passwort einzulesen.
        Abfrage ob verschlüsseln oder entschlüsseln in der UI ausgewählt wurde.
        Aufruf der verschlüsselungs/entschlüsselungs Algorithmen in der Datei "crypt.py".
        Überprüfung ob Dateien nach dem Vorgang gelöscht werden sollen.
        Setzen der Statusmeldungen in der UI über die Funktion "messages".

    get_inputs():
        Einlesen der Pfade und des Passworts.

    sort_input(input_list: list):
        Sortieren der gedroppten Dateien/Ordner.
        Dadurch wird eine Liste mit allen Dateipfaden erstellt.

    checking_folder(path: str):
        Ablöschen des Messagefensters.
        Start der Suche nach Dateien im ausgewähltem Ordner.

    open_directory(path: str):
        Überprüfung ob path ein Verzeichnis ist.
        Anschließender Aufruf der "search_in_folder" Funktion.

    search_in_folder(paths: list):
        Durchsuchen des Ordners nach Dateien und nach Unterordnern.
        In den Unterordnern ebenfalls nach Dateien suchen.
        Die Pfade dieser Dateien, werden alle in "self.file_list" geschrieben.

    extend_dir(path_list: list, path: str):
        Dateiname durch den restlichen Pfad erweitern.

    get_password():
        Einlesen und überprüfung des Passworts, sowie generierung von Fehlermeldung.

    check_password(password: str):
        überprüfung des Passworts ob es den vordefinierten Kriterien entspricht.

    check_enc_or_dec():
        Einlesen ob enc oder dec ausgewählt ist in der UI.

    messages(num: int, file: str):
        Erzeugen der auszugebenden Nachricht. Auf Basis der Variablen "num" und "file".

    change_colour(colour: str, msg: str):
        Ändern der Farbe der auszugebenden Nachricht.

    clear_message():
        Ablöschen des Messagefensters und freischalten der Passworteingabe.

    clear_all():
        Ablöschen der Passworteingabe, desr QListWidgetItems und der "self.file_list".
    """

    def __init__(self):
        """
        Initialisieren einer leeren Liste für die Dateipfade.
        Initialisieren einer leeren Strin-Variable für das Passwort.
        Überwachung ob start_button oder Enter gedrückt wurde.
        """
        self.file_list = []
        self.password = ""
        w.pass_input.returnPressed.connect(self.worker)
        w.start_button.clicked.connect(self.worker)

    def worker(self) -> None:
        """
        Aufruf der Funktion "get_inputs", um die Pfade und das Passwort einzulesen.
        Abfrage ob verschlüsseln oder entschlüsseln in der UI ausgewählt wurde.
        Aufruf der verschlüsselungs/entschlüsselungs Algorithmen in der Datei "crypt.py".
        Überprüfung ob Dateien nach dem Vorgang gelöscht werden sollen.
        Setzen der Statusmeldungen in der UI über die Funktion "messages".
        """
        self.get_inputs()
        if self.password:
            w.progress_bar.setValue(0)
            parts = round(100 / len(self.file_list))    # Prozentteile je Datei
            enc_or_dec = self.check_enc_or_dec()
            for i, file in enumerate(self.file_list):
                if file.lower().endswith('.pdf') and enc_or_dec == 'enc':
                    num = crypt.encrypt_pdf(file, self.password)
                elif file.lower().endswith('.pdf') and enc_or_dec == 'dec':
                    num = crypt.decrypt_pdf(file, self.password)
                elif enc_or_dec == 'enc':
                    num = crypt.encrypt(file, self.password)
                else:
                    num = crypt.decrypt(file, self.password)
                if w.delete_files.isChecked():
                    os.remove(file)
                self.messages(num, file)
                w.progress_bar.setValue(parts * (i + 1))
            self.messages(6, '')  # Setzen der Statusmeldung "Fertig"
            self.clear_all()

    def get_inputs(self):
        """Einlesen der Pfade und des Passworts."""
        self.sort_input(w.drop_data.get_paths())  # Pfade aus der Klasse DragDrop lesen
        self.get_password()  # Passwort einlesen und prüfen

    def sort_input(self, input_list: list) -> None:
        """
        Sortieren der gedroppten Dateien/Ordner.
        Dadurch wird eine Liste mit allen Dateipfaden erstellt.
        """
        for path in input_list:
            if os.path.isdir(path):
                self.checking_folder(path)
            else:
                self.file_list.append(path)

    def checking_folder(self, path: str) -> None:
        """
        Ablöschen des Messagefensters.
        Start der Suche nach Dateien im ausgewähltem Ordner.
        """
        self.clear_message()
        self.open_directory(path)

    def open_directory(self, path: str) -> None:
        """
        Überprüfung ob path ein Verzeichnis ist.
        Anschließender Aufruf der "search_in_folder" Funktion.
        """
        liste = self.extend_dir(os.listdir(path), path)
        self.search_in_folder(liste)

    def search_in_folder(self, paths: list) -> None:
        """
        Durchsuchen des Ordners nach Dateien und nach Unterordnern.
        In den Unterordnern ebenfalls nach Dateien suchen.
        Die Pfade dieser Dateien, werden alle in "self.file_list" geschrieben.
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

    @staticmethod
    def extend_dir(path_list: list, path: str) -> list:
        """Dateiname durch den restlichen Pfad erweitern."""
        path_list = [path + "\\" + item for item in path_list]
        return path_list

    def get_password(self) -> None:
        """Einlesen und überprüfung des Passworts, sowie generierung von Fehlermeldung."""
        if not self.check_password(w.pass_input.text()):
            self.messages(0, '')  # Passwort entspricht nicht den Kriterien
            self.file_list = []
            w.pass_input.clear()
        elif not self.file_list:
            self.messages(10, '')  # keine Dateien ausgewählt
        else:
            self.messages(1, '')  # Passwort gültig
            self.password = w.pass_input.text()

    @staticmethod
    def check_password(password: str) -> bool:
        """überprüfung des Passworts ob es den vordefinierten Kriterien entspricht."""
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

    @staticmethod
    def check_enc_or_dec() -> str:
        """Einlesen ob enc oder dec ausgewählt ist in der UI."""
        if w.enc.isChecked():
            return 'enc'
        return 'dec'

    def messages(self, num: int, file: str) -> None:
        """Erzeugen der auszugebenden Nachricht. Auf Basis der Variablen "num" und "file"."""
        colour = ""
        msg = ""
        if num == 0:
            msg = "Passwort entspricht nicht den Kriterien!"
            colour = "red"
        elif num == 1:
            msg = "Passwort entspricht den Kriterien!"
            colour = "green"
        elif num == 2:
            msg = "verschlüsseln oder entschlüsseln auswählen!"
            colour = "red"
        elif num == 3:
            msg = f"Passwort für Datei {os.path.basename(file)} ist falsch!"
            colour = "red"
        elif num == 4:
            msg = f"Datei {os.path.basename(file)} ist bereits verschlüsselt!"
            colour = "red"
        elif num == 5:
            msg = f"Datei {os.path.basename(file)} ist nicht verschlüsselt!"
            colour = "red"
        elif num == 6:
            msg = "\nVorgang abgeschlossen!"
            colour = "green"
        elif num == 7:
            msg = f"Datei {os.path.basename(file)} erfolgreich entschlüsselt!"
            colour = "green"
        elif num == 8:
            msg = f"Datei {os.path.basename(file)} erfolgreich verschlüsselt!"
            colour = "green"
        elif num == 9:
            msg = "Pfadreferenz ungültig!"
            colour = "red"
        elif num == 10:
            msg = "Keine Dateien oder Ordner ausgewählt!"
            colour = "red"
        self.change_colour(colour, msg)

    @staticmethod
    def change_colour(colour: str, msg: str) -> None:
        """Ändern der Farbe der auszugebenden Nachricht."""
        if colour == "red":
            msg = f'<span style=\" color: #ED422C;\">{msg}</span>'
        elif colour == "green":
            msg = f'<span style=\" color: #2CA94F;\">{msg}</span>'
        w.message.append(msg)

    @staticmethod
    def clear_message() -> None:
        """Ablöschen des Messagefensters und freischalten der Passworteingabe."""
        w.message.clear()
        w.pass_input.setEnabled(True)

    def clear_all(self) -> None:
        """Ablöschen der Passworteingabe, des QListWidgetItems und der "self.file_list"."""
        w.pass_input.clear()
        w.remove_all_items()
        self.file_list = []
        self.password = ""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    with open("Stylesheet.css", "r", encoding="utf-8") as stylesheet:
        stylesheet = stylesheet.read()
        app.setStyleSheet(stylesheet)
    w = Ui()
    main = Main()
    sys.exit(app.exec())
