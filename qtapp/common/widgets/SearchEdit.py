from typing import Optional

import qtawesome as qta
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QLineEdit


class SearchEdit(QLineEdit):
    """A custom QLineEdit for searching.

    Signals:
        searchChanged: Emitted when the search string is changed. The Signal
            provides the search string.

    Args:
        parent (QObject): The parent widget (default = None).
    """

    searchChanged = Signal(str)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)

        self.textChanged.connect(self.searchChanged.emit)
        self.setPlaceholderText("Search...")

        self._clear_btn = self.addAction(
            qta.icon("ph.x-light"),
            QLineEdit.ActionPosition.TrailingPosition,
        )
        self._clear_btn.triggered.connect(self._onClearBtnClicked)

    @Slot()
    def _onClearBtnClicked(self):
        """Slot triggered when the clear button is pressed.

        Resets the input text.
        """

        self.setText(None)
