"""
Autor: Sven Kleinhans
"""

import os
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtGui import QDropEvent, QDragEnterEvent, QDragMoveEvent, QIcon
from PyQt5.QtCore import Qt


class DragDrop(QListWidget):
    """
    Methods
    -------
    set_check_state(item):
        Beim anklicken eines Items wird die Checkbox aktiviert oder deaktiviert.

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
        Gibt die Pfade zurück.
    """

    def __init__(self, parent):
        super(DragDrop, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setToolTip("Dateien hier ablegen")
        self.paths = []
        self.itemClicked.connect(self.set_check_state)

    @staticmethod
    def set_check_state(item):
        """Beim anklicken eines Items wird die Checkbox aktiviert oder deaktiviert."""
        if item.checkState() != Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Checked)
        else:
            item.setCheckState(Qt.CheckState.Unchecked)

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
                    # self.messages(9, "")
                    event.ignore()
        else:
            event.ignore()

    @staticmethod
    def check_typ(url: str) -> str:
        """überprüfung ob url ein Ordner oder eine Datei ist und entsprechendes Icon setzen."""
        if os.path.isdir(url):
            return r"icon\folder.ico"
        return r"icon\file.ico"

    def get_paths(self) -> list:
        """Gibt die Pfade zurück."""
        return self.paths
