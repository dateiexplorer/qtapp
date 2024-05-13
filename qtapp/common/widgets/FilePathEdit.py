from pathlib import Path
from typing import Optional

import qtawesome as qta
from PySide6.QtCore import QFileInfo, Qt, QUrl, Slot
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QMouseEvent
from PySide6.QtWidgets import QFileDialog, QLineEdit, QWidget


class FilePathEdit(QLineEdit):
    """A custom QLineEdit for editing file paths.

    Args:
        dialog (QFileDialog): The file dialog to open.
        parent (Optional[QWidget]): The parent widget. (default = None).
        filter (Optional[str]): Filter for specific file types (default = None).
    """

    def __init__(
        self,
        dialog: QFileDialog,
        parent: Optional[QWidget] = None,
        filter: Optional[str] = None,
    ) -> None:

        super().__init__(None, parent)

        self._dialog = dialog
        self._filter = filter

        self.setReadOnly(True)
        self.setPlaceholderText("Drag and drop a file here or double click")

        icon = qta.icon("ph.folder-open-light")
        self._action = self.addAction(icon, QLineEdit.ActionPosition.TrailingPosition)
        self._action.triggered.connect(self._onOpenFileBtnClicked)

    def setText(self, text: str) -> None:
        """Override from QLineEdit."""

        # Convert text first to path to get the right slashes (forward or backslash).
        # If text is None or empty, set an empty string.
        text = Path(text) if text else ""
        super().setText(str(text))

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Override from QLineEdit."""

        mimeData = event.mimeData()

        # Check if the dragged data contains file paths.
        if mimeData.hasUrls() and all(url.isLocalFile() for url in mimeData.urls()):
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        """Override from QLineEdit."""

        mimeData = event.mimeData()

        # Handle the dropped file paths.
        if mimeData.hasUrls() and all(url.isLocalFile() for url in mimeData.urls()):
            fileInfo = QFileInfo(mimeData.urls()[0].toLocalFile())
            self.setText(fileInfo.absoluteFilePath())

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Override from QLineEdit."""

        button = event.button()
        if button == Qt.MouseButton.LeftButton:
            self._action.trigger()

        event.accept()

    @Slot()
    def _onOpenFileBtnClicked(self) -> None:
        """Open a file dialog and set the selected file path as the text of the
        edit.
        """

        path, _ = self._dialog.getOpenFileName(filter=self._filter)
        if path:
            self.setText(path)
