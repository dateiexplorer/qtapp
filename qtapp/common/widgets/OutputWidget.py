from typing import Optional

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices, QTextCursor
from PySide6.QtWidgets import QTextBrowser, QWidget


class OutputWidget(QTextBrowser):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setOpenLinks(False)
        self.setOpenExternalLinks(False)
        self.setLineWrapMode(QTextBrowser.LineWrapMode.NoWrap)
        self.anchorClicked.connect(self.openUrl)

    def openUrl(self, url: str | QUrl) -> None:
        QDesktopServices.openUrl(url)

    def print(self, text: str) -> None:
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(text)
        cursor.insertText("\n")
        self.setTextCursor(cursor)
