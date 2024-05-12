from enum import Enum
from typing import Optional

import qtawesome as qta
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from qtapp.common.widgets import ElidingLabel


class InlineNotification(QFrame):
    """An inline notification banner like in Microsoft Office products.

    Args:
        text (str): The text shown in the notification banner (default = "").
        type (NotificationType): The type of notification banner
            (default = NotificationType.INFORMATION).
        parent (QWidget): The parent widget (default = None).
    """

    class NotificationType(Enum):
        """Enumeration representing the type of notification abnners.

        Each notification type specififes a unique appearance, including a
        trailing icon, background color, and border color.

        Attributes:
            INFORMATION: Represents an informative notification banner.
                - Icon: "ph.info-light"
                - Background Color: "#e5effb"
                - Border Color: "#aac3d9"

            WARNING: Represents a warning notification banner.
                - Icon: "ph.warning-circle-light"
                - Background Color: "#fcf7b6"
                - Border Color: "#af8600"

            ERROR: Represents an error notification banner.
                - Icon: "ph.x-circle-light"
                - Background Color: "#f8d4d4"
                - Border Color: "#997d7c"
        """

        INFORMATION = ("ph.info-light", "#e5effb", "#aac3d9")
        WARNING = ("ph.warning-circle-light", "#fcf7b6", "#af8600")
        ERROR = ("ph.x-circle-light", "#f8d4d4", "#997d7c")

    def __init__(
        self,
        text: str = "",
        type=NotificationType.INFORMATION,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self._type = type
        self._text: str = text

        # Add drop shadow.
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(
            "InlineNotification {"
            f"background-color: {self._type.value[1]};"
            f"border-top: 1px solid {self._type.value[2]};"
            f"border-bottom: 1px solid {self._type.value[2]};"
            "}"
        )

        self._icon = QPushButton()
        self._icon.setIcon(qta.icon(self._type.value[0]))
        self._icon.setIconSize(QSize(22, 22))
        self._icon.setStyleSheet(
            "QPushButton { background-color: transparent; padding: 0px; }"
        )

        self._label = ElidingLabel(parent=self)
        self._label.setText(self._text)

        self._closeBtn = QPushButton()
        self._closeBtn.setStyleSheet("QPushButton { background-color: transparent; }")
        self._closeBtn.setIcon(qta.icon("ph.x-light"))
        self._closeBtn.clicked.connect(self.close_)

        self._actionBtnLayout = QHBoxLayout()

        self._layout = QHBoxLayout()
        self._layout.setContentsMargins(2, 2, 2, 2)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._layout.addWidget(self._icon)
        self._layout.addWidget(self._label, 1)
        self._layout.addLayout(self._actionBtnLayout)
        self._layout.addWidget(self._closeBtn)

        self.setLayout(self._layout)

    def setText(self, text: str) -> None:
        """Set the text for the notification banner.

        Args:
            text (str): The text to set.
        """

        self._text = text
        self._label.setText(text)

    def setClosable(self, closable: bool) -> None:
        """Decide wether this notification is closable by the user via a close
        button or not.

        Args:
            closable (bool): True makes the close button visible, False hides
                it.
        """

        self._closeBtn.setVisible(closable)

    def addAction(
        self,
        icon: Optional[QIcon] = None,
        text: Optional[str] = None,
        callable: Optional[object] = None,
    ) -> QPushButton:
        """Add a new QPushButton to the notification banner.

        Action buttons appear on the right side of the notification banner,
        before the optional close button.

        Args:
            icon (QIcon): An icon for the QPushButton.
            text (str): The text for the QPushButton.
            callable (object): The function called if the QPushButton gets
                clicked.

        Returns:
            QPushButton: The button created by this method.
        """

        button = QPushButton()
        if icon:
            button.setIcon(icon)
        if text:
            button.setText(text)
        if callable:
            button.clicked.connect(callable)

        self._actionBtnLayout.addWidget(button)
        return button

    def open(self) -> None:
        """Open the notification and show it to the user."""

        self.setVisible(True)

    def close_(self) -> None:
        """Close the notification by hiding it.

        The underscore avoids conflicts with the close function of the QFrame
        widget. Therefore, close and close_ don't share the same functionality.
        """

        self.setVisible(False)


class InlineNotificationList(QWidget):
    """A container for managing InlineNotifications.

    This widget is useful if multiple notifications should be shown at the same
    time. Notifications appear beneath each other to represent the natural
    order.

    Args:
        parent (Optional[QWidget]): The parent widget (default = None).
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setupUi()

        # Add drop shadow.
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

    def setupUi(self) -> None:
        self._layout = QVBoxLayout()
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self._layout)

    def addNotification(self, notification: InlineNotification) -> None:
        """Add a notification to the container.

        If the notification was already added, it will be pushed to the bottom
        of the widget.

        Args:
            notification (InlineNotification): The notification to add.
        """

        index = self._layout.indexOf(notification)
        if index != -1:
            self._layout.removeWidget(notification)
            notification.setParent(self)

        self._layout.addWidget(notification)

        notification.open()

    def closeNotification(self, notification: InlineNotification) -> None:
        """Close and hide the notification in the container.

        Args:
            notification (InlineNotification): The notification to remove.

        """

        notification.close_()
        notification.setParent(None)
