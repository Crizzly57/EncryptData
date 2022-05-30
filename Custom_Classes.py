from PyQt6.QtWidgets import *
from PyQt6 import QtGui


class DragDrop(QComboBox):
    def __init__(self, parent):
        super(DragDrop, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e: QtGui.QDragEnterEvent) -> None:
        print(e)

        if e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e: QtGui.QDropEvent) -> None:
        self.addItem(e.mimeData().text())
