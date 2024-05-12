from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent, QPainter, QPaintEvent
from PySide6.QtWidgets import QTreeView, QWidget


class TreeView(QTreeView):
    """A custom QTreeView with additional features.

    Signals:
        emptySpaceDoubleClicked: Emitted whenever an empty space in the
            TreeView is double clicked by the mouse. Provides the QMouseEvent.

    Args:
        parent (QWidget): The parent widget (default = None).
    """

    emptySpaceDoubleClicked = Signal(QMouseEvent)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setSelectionMode(QTreeView.SelectionMode.SingleSelection)
        self.setRootIsDecorated(False)

        self._placeholderText: str = None

    def setPlaceholderText(self, text: str) -> None:
        """Set a placeholder text.

        This text is displayed if no items are displayed.

        Args:
            text (str): The placeholder text.
        """

        self._placeholderText = text

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Override from QTreeView."""

        index = self.indexAt(event.pos())
        if not index.isValid():
            self.emptySpaceDoubleClicked.emit(event)

        super().mouseDoubleClickEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Override form QTreeView."""

        super().paintEvent(event)
        if self._placeholderText:
            self._drawPlaceholderText(self._placeholderText)

    def _drawPlaceholderText(self, text: str) -> None:
        """Helper function to draw the placeholder text if the underlying
        model has no items to display.

        Args:
            text (str): The text to render.
        """

        if self.model() and self.model().rowCount(self.rootIndex()) > 0:
            return

        painter = QPainter(self.viewport())
        painter.setPen(Qt.GlobalColor.darkGray)
        painter.drawText(
            self.rect(),
            Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
            text,
        )
