from typing import Optional

import qtawesome as qta
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QToolBar, QToolButton, QWidget

from qtapp.common.widgets.ToolBarSpacer import ToolBarSpacer


class StatusBarButton(QToolButton):
    """A custom QToolButton for use in the applications StatusBar.

    Args:
        qta_icon (Optinal[str]): The name of the icon to set for the button
            (default = None).
        text (Optional[str]): The text to display beside the icon
            (default = None).
        parent: The parent widget (default = None).
    """

    def __init__(
        self,
        qtaIcon: Optional[str] = None,
        text: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        if qtaIcon:
            self.setIcon(qta.icon(qtaIcon, color="#484644"))

        if text:
            self.setText(text)


class StatusBar(QToolBar):

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setupUi()

    def setupUi(self) -> None:
        self.setMovable(False)
        self.setIconSize(QSize(18, 18))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setContentsMargins(4, 0, 4, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(2)

        self.addWidget(ToolBarSpacer())

    def addButton(self, statusBarBtn: StatusBarButton) -> None:
        """Add a button to the StatusBar.

        Args:
            dock (StatusBarButton): The button to add.
        """

        self.addWidget(statusBarBtn)
