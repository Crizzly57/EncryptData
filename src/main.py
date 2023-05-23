"""
Author: Sven Kleinhans
Version: 1.2
"""
import os
import sys

from PIL import Image, UnidentifiedImageError
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPropertyAnimation, QAbstractAnimation, QEasingCurve, QTranslator, QLocale, QEvent
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *

from GUI import Ui_MainWindow
from InfoDialog import Ui_Dialog
from SettingsDialog import Ui_settings
from crypt import Crypt, ImageHandler, PDFHandler

GLOBAL_STATE = 0


class Settings(QDialog, Ui_settings):
    def __init__(self):
        super(Settings, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        def move_window(event):
            if event.buttons() == Qt.MouseButton.LeftButton:
                self.move(self.pos() + event.globalPos() - self.drag_pos)
                self.drag_pos = event.globalPos()
                event.accept()
            else:
                event.ignore()

        self.header.mouseMoveEvent = move_window

        def window_pressed(event):
            self.drag_pos = event.globalPos()

        self.header.mousePressEvent = window_pressed


class InfoDialog(QDialog, Ui_Dialog):
    def __init__(self):
        super(InfoDialog, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        def move_window(event):
            if event.buttons() == Qt.MouseButton.LeftButton:
                self.move(self.pos() + event.globalPos() - self.drag_pos)
                self.drag_pos = event.globalPos()
                event.accept()
            else:
                event.ignore()

        self.header.mouseMoveEvent = move_window

        def window_pressed(event):
            self.drag_pos = event.globalPos()

        self.header.mousePressEvent = window_pressed

    def change_label_lang(self, lang: str):
        if lang == "EN":
            self.info_text.setText(open("./UI-files/InfoLabel_EN.html", "r").read())
        elif lang == "DE":
            self.info_text.setText(open("./UI-files/InfoLabel_DE.html", "r", encoding='utf-8').read())


class Ui(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        self.setupUi(self)
        self.settings = Settings()
        self.info_dialog = InfoDialog()
        self.trans = QTranslator()
        self.lang = "DE"
        # Check on startup if system has no german language
        if not QLocale().system().name().split("_")[0] == "de":
            self.trans.load("./UI-files/Translations_EN.qm")
            QtCore.QCoreApplication.instance().installTranslator(self.trans)
            self.settings.language_slider.setValue(0)
            self.info_dialog.change_label_lang("EN")
            self.lang = "EN"
        self.anim = QPropertyAnimation(self.side_menu, b'maximumWidth')

        self.setup_ui()

        def move_window(event):
            if event.buttons() == Qt.MouseButton.LeftButton:
                self.move(self.pos() + event.globalPos() - self.drag_pos)
                self.drag_pos = event.globalPos()
                event.accept()
            else:
                event.ignore()

        self.header.mouseMoveEvent = move_window

        def window_pressed(event):
            self.drag_pos = event.globalPos()

        self.header.mousePressEvent = window_pressed

    def setup_ui(self) -> None:
        self.pass_input.textChanged.connect(lambda: self.start_button.setEnabled(True))
        self.slider.clicked.connect(self.animate_side_menu)
        self.setWindowIcon(QIcon(r"./UI-files/icons/logo.png"))
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        QSizeGrip(self.sizegrip_bl)
        QSizeGrip(self.sizegrip_br)
        self.minimize.clicked.connect(self.showMinimized)
        self.maximize.clicked.connect(self.maximize_restore)
        self.show()

    def maximize_restore(self) -> None:
        global GLOBAL_STATE
        if GLOBAL_STATE == 1:
            self.showNormal()
            GLOBAL_STATE = 0
            self.main_layout.setContentsMargins(10, 10, 10, 10)
            stylesheet = self.main_frame.styleSheet() + "\n" + "QFrame{border-radius: 10px;}"
            self.main_frame.setStyleSheet(stylesheet)
        else:
            self.showMaximized()
            GLOBAL_STATE = 1
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            stylesheet = self.main_frame.styleSheet() + "\n" + "QFrame{border-radius: 0px;}"
            self.main_frame.setStyleSheet(stylesheet)

    def animate_side_menu(self) -> None:
        if self.side_menu.frameGeometry().width() > 60:
            # Close Side menu
            start_value = self.side_menu.frameGeometry().width()
            end_value = 50
        else:
            # Open Side menu
            start_value = self.side_menu.frameGeometry().width()
            end_value = 200
        self.anim.DeletionPolicy(QAbstractAnimation.KeepWhenStopped)
        self.anim.setDuration(500)
        self.anim.setStartValue(start_value)
        self.anim.setEndValue(end_value)
        self.anim.setEasingCurve(QEasingCurve.InOutQuart)
        self.anim.finished.connect(self.set_side_menu_icon)
        self.anim.start()

    def set_side_menu_icon(self):
        width = self.side_menu.frameGeometry().width()
        if width > 50:
            self.slider.setIcon(QIcon(r"./UI-files/icons/align-right"))
        else:
            self.slider.setIcon(QIcon(r"./UI-files/icons/align-left"))

    @QtCore.pyqtSlot(int)
    def change_language(self, state):
        if state == 0:
            self.trans.load("./UI-files/Translations_EN.qm")
            QApplication.instance().installTranslator(self.trans)
            self.info_dialog.change_label_lang("EN")
            self.lang = "EN"
        else:
            QApplication.instance().removeTranslator(self.trans)
            self.info_dialog.change_label_lang("DE")
            self.lang = "DE"

    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi(self)
            self.settings.retranslateUi(self)
            # self.info_dialog.retranslateUi(self)    # Not working


class Main:
    def __init__(self):
        self.file_list = []
        self.password = ""
        self.ui = Ui()
        # Define Events for the UI
        self.ui.remove_all.clicked.connect(self.remove_all_items)
        self.ui.remove_selected.clicked.connect(self.remove_selected_items)
        self.ui.pass_input.returnPressed.connect(self.worker)
        self.ui.start_button.clicked.connect(self.worker)
        self.ui.info_btn.clicked.connect(self.show_info)
        self.ui.settings_btn.clicked.connect(self.show_settings)
        self.ui.close.clicked.connect(app.quit)

    def worker(self) -> None:
        self.get_inputs()
        if self.password:
            self.ui.progress_bar.setValue(0)
            parts = round(100 / len(self.file_list))
            encryption = self.check_encryption()
            for i, file in enumerate(self.file_list):
                try:
                    Image.open(file).verify()
                    status_code = ImageHandler(file=file, password=self.password, encryption=encryption).start()
                except UnidentifiedImageError:
                    if file.lower().endswith('.pdf'):
                        status_code = PDFHandler(file=file, password=self.password, encryption=encryption).start()
                    else:
                        status_code = Crypt(file=file, password=self.password, encryption=encryption).start()

                if self.ui.settings.delete_files.isChecked() and status_code in (3, 4):
                    os.remove(file)
                self.messages(status_code, file)
                self.ui.progress_bar.setValue(parts * (i + 1))
            self.ui.progress_bar.setValue(100)
            self.messages(2, '')  # Finished
            self.clear_all()

    def get_inputs(self) -> None:
        paths = self.ui.drop_data.get_paths()
        if paths:
            self.sort_input(paths)
            self.get_password()
        else:
            self.messages(106, "")  # No files selected

    def sort_input(self, input_list: list) -> None:
        self.ui.message.clear()
        self.ui.pass_input.setEnabled(True)
        for path in input_list:
            if os.path.isdir(path):
                liste = self.extend_dir(os.listdir(path), path)
                self.search_in_folder(liste)
            else:
                self.file_list.append(path)

    def search_in_folder(self, paths: list) -> None:
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
        path_list = [path + "\\" + item for item in path_list]
        return path_list

    def get_password(self) -> None:
        self.password = self.ui.pass_input.text()
        if not self.check_password(self.password):
            self.messages(100, '')  # Password not valid
            self.file_list = []
            self.password = ""
            self.ui.pass_input.clear()
        elif not self.file_list:
            self.messages(106, '')  # No files selected
        else:
            self.messages(1, '')  # Password valid

    @staticmethod
    def check_password(password: str) -> bool:
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

    def check_encryption(self) -> bool:
        if self.ui.enc.isChecked():
            return True
        return False

    def messages(self, status_code: int, file: str) -> None:
        file = os.path.basename(file)
        colour = ""
        msg = ""
        if status_code == 1:
            if self.ui.lang == "EN":
                msg = "Password does match the requirements!"
            else:
                msg = "Passwort entspricht den Kriterien!"
            colour = "green"
        elif status_code == 2:
            if self.ui.lang == "EN":
                msg = "\nOperation completed"
            else:
                msg = "\nVorgang abgeschlossen!"
            colour = "green"
        elif status_code == 3:
            if self.ui.lang == "EN":
                msg = f"File {file} successfully decrypted!"
            else:
                msg = f"Datei {file} erfolgreich entschlüsselt!"
            colour = "green"
        elif status_code == 4:
            if self.ui.lang == "EN":
                msg = f"File {file} successfully encrypted!"
            else:
                msg = f"Datei {file} erfolgreich verschlüsselt!"
            colour = "green"
        elif status_code == 100:
            if self.ui.lang == "EN":
                msg = "Password does not match the requirements!"
            else:
                msg = "Passwort entspricht nicht den Kriterien!"
            colour = "red"
        elif status_code == 101:
            if self.ui.lang == "EN":
                msg = f"The file {file} does not exist!"
            else:
                msg = f"Die Datei {file} existiert nicht!"
            colour = "red"
        elif status_code == 102:
            if self.ui.lang == "EN":
                msg = "select encrypt or decrypt!"
            else:
                msg = "verschlüsseln oder entschlüsseln auswählen!"
            colour = "red"
        elif status_code == 103:
            if self.ui.lang == "EN":
                msg = f"Password for the file {file} is wrong!"
            else:
                msg = f"Passwort für Datei {file} ist falsch!"
            colour = "red"
        elif status_code == 104:
            if self.ui.lang == "EN":
                msg = f"File {file} is already encrypted!"
            else:
                msg = f"Datei {file} ist bereits verschlüsselt!"
            colour = "red"
        elif status_code == 105:
            if self.ui.lang == "EN":
                msg = f"File {file} is not encrypted!"
            else:
                msg = f"Datei {file} ist nicht verschlüsselt!"
            colour = "red"
        elif status_code == 106:
            if self.ui.lang == "EN":
                msg = "No files or folders selected!"
            else:
                msg = "Keine Dateien oder Ordner ausgewählt!"
            colour = "red"
        elif status_code == 107:
            if self.ui.lang == "EN":
                msg = "Invalid path reference!"
            else:
                msg = "Pfadreferenz ungültig!"
            colour = "red"
        elif status_code == 108:
            if self.ui.lang == "EN":
                msg = f"Missing permissions for the file {file}!"
            else:
                msg = f"Fehlende Berechtigung für die Datei {file}!"
            colour = "red"
        self.set_colour(colour, msg)

    def set_colour(self, colour: str, msg: str) -> None:
        if colour == "red":
            msg = f'<span style=\" color: #ED422C;\">{msg}</span>'
        elif colour == "green":
            msg = f'<span style=\" color: #afb1b3;\">{msg}</span>'
        self.ui.message.append(msg)

    def clear_all(self) -> None:
        self.ui.pass_input.clear()
        self.remove_all_items()
        self.file_list = []

    def remove_all_items(self) -> None:
        self.ui.drop_data.clear()
        self.ui.drop_data.paths = []

    def remove_selected_items(self) -> None:
        items = [self.ui.drop_data.item(x) for x in range(self.ui.drop_data.count())]
        for item in items:
            self.ui.drop_data.setCurrentItem(item)
            index = self.ui.drop_data.currentRow()
            if item.checkState() == Qt.CheckState.Checked:
                self.ui.drop_data.takeItem(index)
                del self.ui.drop_data.paths[index]

    def show_info(self) -> None:
        self.ui.info_dialog.close.clicked.connect(self.ui.info_dialog.accept)
        self.ui.info_dialog.exec_()

    def show_settings(self) -> None:
        self.ui.settings.close.clicked.connect(self.ui.settings.accept)
        self.ui.settings.language_slider.valueChanged.connect(self.ui.change_language)
        self.ui.settings.exec_()


if __name__ == "__main__":
    # Enable High DPI Display
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec())
