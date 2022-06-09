"""
Author: Sven Kleinhans
Version: 1.2
"""
from PyQt5 import QtCore

import crypt
import sys
import os
from GUI import Ui_MainWindow
from InfoDialog import Ui_Dialog
from SettingsDialog import Ui_settings
from custom_classes import DragDrop
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPropertyAnimation, QAbstractAnimation, QEasingCurve, QTranslator, QLocale, QEvent
from PyQt5.QtGui import QIcon
# The resource file wich contains the icons as bytes
import custom_icons_rc


GLOBAL_STATE = 0


class Settings(QDialog, Ui_settings):
    def __init__(self):
        super(Settings, self).__init__()
        self.setupUi(self)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.header = self.findChild(QFrame, 'header')
        self.close = self.findChild(QPushButton, 'close')
        self.language_slider = self.findChild(QSlider, 'language_slider')

        def move_window(event):
            """Calculate the new position of the window and move it"""
            if event.buttons() == Qt.MouseButton.LeftButton:
                self.move(self.pos() + event.globalPos() - self.drag_pos)
                self.drag_pos = event.globalPos()
                event.accept()
            else:
                event.ignore()
        self.header.mouseMoveEvent = move_window

        def window_pressed(event):
            """Save the global position of the window"""
            self.drag_pos = event.globalPos()
        self.header.mousePressEvent = window_pressed


class InfoDialog(QDialog, Ui_Dialog):
    def __init__(self):
        super(InfoDialog, self).__init__()
        self.setupUi(self)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.header = self.findChild(QFrame, 'header')
        self.close = self.findChild(QPushButton, 'close')

        def move_window(event):
            """Calculate the new position of the window and move it"""
            if event.buttons() == Qt.MouseButton.LeftButton:
                self.move(self.pos() + event.globalPos() - self.drag_pos)
                self.drag_pos = event.globalPos()
                event.accept()
            else:
                event.ignore()
        self.header.mouseMoveEvent = move_window

        def window_pressed(event):
            """Save the global position of the window"""
            self.drag_pos = event.globalPos()
        self.header.mousePressEvent = window_pressed


class Ui(QMainWindow, Ui_MainWindow):
    """
    Methods
    -------
    setup_ui():
        Setup UI and make definitions

    maximize_restore():
        Maximize the Window or restore the default size

    animate_sidemenu():
        Animate the Sidemenu
    """
    def __init__(self):
        super(Ui, self).__init__()
        self.setupUi(self)
        self.settings = Settings()
        self.info_dialog = InfoDialog()
        self.trans = QTranslator()
        # Check on startup if system has no german language
        if not QLocale().system().name() == "de_DE":
            self.trans.load("out.qm")
            QtCore.QCoreApplication.instance().installTranslator(self.trans)
            self.settings.language_slider.setValue(0)

        # Find objects in the UI-XML
        self.pass_input = self.findChild(QLineEdit, 'pass_input')
        self.remove_all = self.findChild(QPushButton, 'remove_all')
        self.close = self.findChild(QPushButton, 'close')
        self.minimize = self.findChild(QPushButton, 'minimize')
        self.maximize = self.findChild(QPushButton, 'maximize')
        self.remove_selected = self.findChild(QPushButton, 'remove_selected')
        self.start_button = self.findChild(QPushButton, 'start_button')
        self.slider = self.findChild(QPushButton, 'slider')
        self.sizegrip_bl = self.findChild(QFrame, 'sizegrip_bl')
        self.sizegrip_br = self.findChild(QFrame, 'sizegrip_br')
        self.progress_bar = self.findChild(QProgressBar, 'progress_bar')
        self.main_layout = self.findChild(QLayout, 'main_layout')
        self.main_frame = self.findChild(QFrame, 'main_frame')
        self.header = self.findChild(QFrame, 'header')
        self.enc = self.findChild(QRadioButton, 'enc')
        self.dec = self.findChild(QRadioButton, 'dec')
        self.message = self.findChild(QTextBrowser, 'message')
        self.drop_data = self.findChild(DragDrop, 'drop_data')
        self.delete_files = self.findChild(QCheckBox, 'delete_files')
        self.side_menu = self.findChild(QFrame, 'side_menu')
        self.info_btn = self.findChild(QPushButton, 'info_btn')
        self.settings_btn = self.findChild(QPushButton, 'settings_btn')
        self.anim = QPropertyAnimation(self.side_menu, b'maximumWidth')

        self.setup_ui()

        def move_window(event):
            """Calculate the new position of the window and move it"""
            if event.buttons() == Qt.MouseButton.LeftButton:
                self.move(self.pos() + event.globalPos() - self.drag_pos)
                self.drag_pos = event.globalPos()
                event.accept()
            else:
                event.ignore()
        self.header.mouseMoveEvent = move_window

        def window_pressed(event):
            """Save the global position of the window"""
            self.drag_pos = event.globalPos()
        self.header.mousePressEvent = window_pressed

    def setup_ui(self) -> None:
        """Setup UI and make definitions"""
        self.pass_input.textChanged.connect(lambda: self.start_button.setEnabled(True))
        self.slider.clicked.connect(self.animate_sidemenu)
        self.setWindowIcon(QIcon(r"UI-files/icons/logo.png"))
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        QSizeGrip(self.sizegrip_bl)
        QSizeGrip(self.sizegrip_br)
        self.minimize.clicked.connect(self.showMinimized)
        self.maximize.clicked.connect(self.maximize_restore)
        self.show()

    def maximize_restore(self) -> None:
        """Maximize the Window or restore the default size"""
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

    def animate_sidemenu(self) -> None:
        """Animate the Sidemenu"""
        if self.side_menu.frameGeometry().width() > 60:
            # Close Sidemenu
            start_value = self.side_menu.frameGeometry().width()
            end_value = 50
        else:
            # Open Sidemenu
            start_value = self.side_menu.frameGeometry().width()
            end_value = 200
        self.anim.DeletionPolicy(QAbstractAnimation.KeepWhenStopped)
        self.anim.setDuration(500)
        self.anim.setStartValue(start_value)
        self.anim.setEndValue(end_value)
        self.anim.setEasingCurve(QEasingCurve.InOutQuart)
        self.anim.start()

    @QtCore.pyqtSlot(int)
    def change_language(self, state):
        if state == 0:
            self.trans.load("UI-files/Translations_EN.qm")
            QApplication.instance().installTranslator(self.trans)
        else:
            QApplication.instance().removeTranslator(self.trans)

    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi(self)
            self.settings.retranslateUi(self)
            self.info_dialog.retranslateUi(self)


class Main:
    """
    worker():
        The worker for the encryption and decryption

    get_inputs():
        Create the input paths and get the password

    sort_input(input_list):
        Generate a file list from the input paths

    search_in_folder(paths):
        Search for files in folders

    extend_dir(path_list, path):
        Return a list with the full names of the files in the folder

    get_password():
        Get password from user input

    check_password(password):
        Return true if the password is valid

    check_enc_or_dec():
        Return the operation

    messages(num, file):
        Create the message

    set_colour(colour, msg):
        Set the colour of the message

    clear_all():
        Clear all for the next run

    remove_all_items():
        Remove all items from the QListWidget

    remove_selected_items():
        Remove all selected items from the QListWidget

    show_info():
        Show the Info Dialog

    show_settings():
        Show the Settings Dialog
    """
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
        """The worker for the encryption and decryption"""
        self.get_inputs()
        if self.password:
            self.ui.progress_bar.setValue(0)
            parts = round(100 / len(self.file_list))
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
                if self.ui.delete_files.isChecked() and num not in (101, 102):
                    os.remove(file)
                self.messages(num, file)
                self.ui.progress_bar.setValue(parts * (i + 1))
            self.ui.progress_bar.setValue(100)
            self.messages(2, '')  # Finished
            self.clear_all()

    def get_inputs(self) -> None:
        """Create the input paths and get the password"""
        paths = self.ui.drop_data.get_paths()
        if paths:
            self.sort_input(paths)
            self.get_password()
        else:
            self.messages(106, "")  # No files selected

    def sort_input(self, input_list: list) -> None:
        """Generate a file list from the input paths"""
        self.ui.message.clear()
        self.ui.pass_input.setEnabled(True)
        for path in input_list:
            if os.path.isdir(path):
                liste = self.extend_dir(os.listdir(path), path)
                self.search_in_folder(liste)
            else:
                self.file_list.append(path)

    def search_in_folder(self, paths: list) -> None:
        """Search for files in folders"""
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
        """Return a list with the full names of the files in the folder"""
        path_list = [path + "\\" + item for item in path_list]
        return path_list

    def get_password(self) -> None:
        """Get password from user input"""
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
        """Return true if the password is valid"""
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

    def check_enc_or_dec(self) -> str:
        """Return the operation"""
        if self.ui.enc.isChecked():
            return 'enc'
        return 'dec'

    def messages(self, num: int, file: str) -> None:
        """Create the message"""
        file = os.path.basename(file)
        colour = ""
        msg = ""
        if num == 1:
            msg = "Passwort entspricht den Kriterien!"
            colour = "green"
        elif num == 2:
            msg = "\nVorgang abgeschlossen!"
            colour = "green"
        elif num == 3:
            msg = f"Datei {file} erfolgreich entschlüsselt!"
            colour = "green"
        elif num == 4:
            msg = f"Datei {file} erfolgreich verschlüsselt!"
            colour = "green"
        elif num == 100:
            msg = "Passwort entspricht nicht den Kriterien!"
            colour = "red"
        elif num == 101:
            msg = f"Die Datei {file} existiert nicht!"
            colour = "red"
        elif num == 102:
            msg = "verschlüsseln oder entschlüsseln auswählen!"
            colour = "red"
        elif num == 103:
            msg = f"Passwort für Datei {file} ist falsch!"
            colour = "red"
        elif num == 104:
            msg = f"Datei {file} ist bereits verschlüsselt!"
            colour = "red"
        elif num == 105:
            msg = f"Datei {file} ist nicht verschlüsselt!"
            colour = "red"
        elif num == 106:
            msg = "Keine Dateien oder Ordner ausgewählt!"
            colour = "red"
        elif num == 107:
            msg = "Pfadreferenz ungültig!"
            colour = "red"
        elif num == 108:
            msg = f"Fehlende Berechtigung für die Datei {file}!"
            colour = "red"
        self.set_colour(colour, msg)

    def set_colour(self, colour: str, msg: str) -> None:
        """Set the colour of the message"""
        if colour == "red":
            msg = f'<span style=\" color: #ED422C;\">{msg}</span>'
        elif colour == "green":
            msg = f'<span style=\" color: #afb1b3;\">{msg}</span>'
        self.ui.message.append(msg)

    def clear_all(self) -> None:
        """Clear all for the next run"""
        self.ui.pass_input.clear()
        self.remove_all_items()
        self.file_list = []

    def remove_all_items(self) -> None:
        """Remove all items from the QListWidget"""
        self.ui.drop_data.clear()
        self.ui.drop_data.paths = []

    def remove_selected_items(self) -> None:
        """Remove all selected items from the QListWidget"""
        items = [self.ui.drop_data.item(x) for x in range(self.ui.drop_data.count())]
        for item in items:
            self.ui.drop_data.setCurrentItem(item)
            index = self.ui.drop_data.currentRow()
            if item.checkState() == Qt.CheckState.Checked:
                self.ui.drop_data.takeItem(index)
                del self.ui.drop_data.paths[index]

    def show_info(self) -> None:
        """Show the Info Dialog"""
        self.ui.info_dialog.close.clicked.connect(self.ui.info_dialog.accept)
        self.ui.info_dialog.exec_()

    def show_settings(self) -> None:
        """Show the Settings Dialog"""
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
