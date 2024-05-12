from typing import Optional

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QPainter, QPaintEvent, QTextLayout
from PySide6.QtWidgets import QLabel


class ElidingLabel(QLabel):
    """A QLabel with text elision.

    ElidingLabel is a QLabel that elides the text if it is too long to fit
    within the widget.
    The elision mode can be specified to determine where the ellipsis should
    appear when displaying texts that don't fit.

    Based on:
    https://doc-snapshots.qt.io/qtforpython-5.15/overviews/qtwidgets-widgets-elidedlabel-example.html

    Args:
        text (str): The label text.
        mode (Qt.TextElideMode, optional): The text elide mode. Defaults to
            Qt.TextElideMode.ElideRight.
        parent (QWidget, optional): The parent widget. Defaults to None.
        f (Qt.WindowFlags, optional): The window flags for the widget.
            Defaults to 0.

    Signals:
        elisionChanged: This signal is emitted when the text elision changes.
            It provides a boolean value indicating whether the text is
            currently elided.

    Description:
        ElidingLabel is a subclass of QLabel that provides an elision feature
        for long texts. It is based on the elidedText method of QFontMetrics,
        allowing the text to be elided on the left, in the middle, or on the
        right when it exceeds the available space.

        The label's text can be set using the setText method, and the elision
        mode can be changed using the setMode method. The current text can be
        retrieved using the text method.

        The elision_changed signal is emitted whenever the elision state of
        the text changes. It can be connected to other slots to perform actions
        based on the elision state.
    """

    elisionChanged = Signal(bool)

    def __init__(
        self,
        text: Optional[str] = "",
        mode=Qt.TextElideMode.ElideRight,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self._mode = mode
        self._isElided = False

        self.setText(text)

    def setText(self, text: str):
        """Set the text of the label.

        Args:
            text (str): The text to set.
        """

        self._contents = text

        # This line set for testing. Its value is the return value of
        # QFontMetrics.elidedText, set in paintEvent. The variable must be
        # initialized for testing. The value should always be the same as
        # contents when not elided.
        self._elidedLine = text

        self.update()

    def text(self) -> str:
        """Get the current text of the label.

        Returns:
            str: The current text.
        """

        return self._contents

    def paintEvent(self, event: QPaintEvent) -> None:
        """Override the paint event to elide the text if necessary.

        Args:
            event (QPaintEvent): The paint event.
        """

        super().paintEvent(event)

        didElide = False

        painter = QPainter(self)
        fontMetrics = painter.fontMetrics()
        textWidth = fontMetrics.horizontalAdvance(self.text())

        # Layout
        textLayout = QTextLayout(self._contents, painter.font())
        textLayout.beginLayout()

        while True:
            line = textLayout.createLine()

            if not line.isValid():
                break

            line.setLineWidth(self.width())
            point = self._calculateTextAlignment()

            if textWidth >= self.width():
                self._elidedLine = fontMetrics.elidedText(
                    self._contents, self._mode, self.width()
                )
                painter.drawText(
                    QPoint(
                        point.x(),
                        point.y() + fontMetrics.ascent(),
                    ),
                    self._elidedLine,
                )
                didElide = line.isValid()
                break
            else:
                line.draw(painter, point)

        textLayout.endLayout()

        if didElide != self._isElided:
            self._isElided = didElide
            self.elisionChanged.emit(didElide)

    def _calculateTextAlignment(self) -> QPoint:
        """Calculate the alignment position for the text based on the label's
        alignment flags.

        Returns:
            QPoint: The text alignment position.
        """

        alignment = self.alignment()
        textPosition = QPoint()

        if alignment & Qt.AlignmentFlag.AlignLeft:
            textPosition.setX(0)
        elif alignment & Qt.AlignmentFlag.AlignRight:
            textPosition.setX(
                self.width() - self.fontMetrics().boundingRect(self.text()).width()
            )
        elif alignment & Qt.AlignmentFlag.AlignHCenter:
            textPosition.setX(
                (self.width() - self.fontMetrics().boundingRect(self.text()).width())
                // 2
            )

        if alignment & Qt.AlignmentFlag.AlignTop:
            textPosition.setY(0)
        elif alignment & Qt.AlignmentFlag.AlignBottom:
            textPosition.setY(self.height() - self.fontMetrics().height())
        elif alignment & Qt.AlignmentFlag.AlignVCenter:
            textPosition.setY((self.height() - self.fontMetrics().height()) // 2)

        return textPosition
