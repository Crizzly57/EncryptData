"""
Author: Sven Kleinhans
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
        Activate the checkbox of the selected item

    dragEnterEvent(event: QDragEnterEvent):
        Check if dropped data has Urls

    dragMoveEvent(event: QDragMoveEvent):
        Drag Event is active

    dropEvent(event: QDropEvent):
        Add the dropped files to the QListWidget

    check_typ():
        Returns the icons for the dropped data

    get_paths():
        Returns the paths
    """
    def __init__(self, parent):
        super(DragDrop, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setToolTip("Dateien hier ablegen")
        self.paths = []
        self.itemClicked.connect(self.set_check_state)

    @staticmethod
    def set_check_state(item):
        """Activate the checkbox of the selected item"""
        if item.checkState() != Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Checked)
        else:
            item.setCheckState(Qt.CheckState.Unchecked)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Check if dropped data has Urls"""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        """Drag Event is active"""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        """Add the dropped files to the QListWidget"""
        for url in event.mimeData().urls():
            if url.toLocalFile() not in self.paths and not url.toLocalFile().endswith(
                    ".lnk") and os.path.exists(url.toLocalFile()):
                item = QListWidgetItem(url.toLocalFile())
                item.setCheckState(Qt.CheckState.Unchecked)
                item.setIcon(QIcon(self.check_typ(url.toLocalFile())))
                self.addItem(item)
                self.paths.append(url.toLocalFile())
            else:
                event.ignore()

    @staticmethod
    def check_typ(url: str) -> str:
        """Returns the icons for the dropped data"""
        if os.path.isdir(url):
            return r"UI-files\icons\folder.ico"
        return r"UI-files\icons\file.ico"

    def get_paths(self) -> list:
        """Returns the paths"""
        return self.paths
