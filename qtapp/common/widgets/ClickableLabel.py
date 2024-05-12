from PySide6.QtCore import QRect, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QLabel


class ClickableLabel(QLabel):
    """A QLabel emitting a clicked Signal if clicked on the text.

    Signals:
        clicked: A signal emitted whenever the label text is clicked with the
            mouse.
    """

    clicked = Signal()

    def __init__(self, text: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self.setText(text)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Override from QLabel."""

        if self.textRect().contains(event.pos()):
            self.clicked.emit()

        super().mousePressEvent(event)

    def textRect(self) -> QRect:
        """Calculate the rectangle around the text.

        Returns:
            QRect: The rectangle enclosing the text.
        """

        # First calculate the font metrics based on the text.
        # Afterwards create a new QRect, x and y set to zero. This is a
        # workaround and might not work for all texts.
        # The workaround is needed because boundingRect doesn't return the
        # correct x and y coordinates (they are negative and don't start at the
        # right position).
        rect = self.fontMetrics().boundingRect(self.text())
        return QRect(0, 0, rect.width(), rect.height())
