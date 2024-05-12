from typing import Optional

import qtawesome as qta
from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLineEdit, QWidget


class PasswordEdit(QLineEdit):
    """A custom QLineEdit for showing and editing passwords.

    Args:
        parent (Optional[QWidget]): The parent widget. (default = None).
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(None, parent)

        self.setEchoMode(QLineEdit.EchoMode.Password)
        self.setPlaceholderText("Password...")

        self._action = self.addAction(
            QIcon(),
            QLineEdit.ActionPosition.TrailingPosition,
        )
        self._action.setCheckable(True)
        self._action.toggled.connect(self.showPassword)

        self.showPassword(False)

    @Slot()
    def showPassword(self, show: bool) -> None:
        if show:
            self.setEchoMode(QLineEdit.EchoMode.Normal)
            self._action.setIcon(qta.icon("ph.eye-slash-light"))
        else:
            self.setEchoMode(QLineEdit.EchoMode.Password)
            self._action.setIcon(qta.icon("ph.eye-light"))
