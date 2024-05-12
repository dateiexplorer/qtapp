from typing import Optional

import qtawesome as qta
from PySide6.QtCore import QSize
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QButtonGroup, QToolBar, QToolButton, QWidget


class NavigationBarButton(QToolButton):
    """A custom QToolButton for use in the applications NavigationBar."""

    def __init__(
        self,
        qtaIconStr: str,
        toolTip: Optional[str] = None,
        parent: Optional[QWidget] = None,
        **kwargs,
    ) -> None:
        super().__init__(parent)

        icon = qta.icon(
            qtaIconStr,
            color=kwargs.get("color", "#484644"),
            color_on=kwargs.get("color_on", "#106EBE"),
            color_active=kwargs.get("color_active", "#484644"),
            color_selected=kwargs.get("color_selected", "#484644"),
        )

        self.setIcon(icon)
        self.setToolTip(toolTip)
        self.setCheckable(True)


class NavigationBar(QToolBar):

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._btnGroup = QButtonGroup(self)
        self.setupUi()

    def setupUi(self) -> None:
        self.setMovable(False)
        self.setOrientation(Qt.Orientation.Vertical)
        self.setIconSize(QSize(28, 28))
        self.setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

    def addButton(self, navBarBtn: NavigationBarButton) -> None:
        """Add a button to the NavigationBar.

        Args:
            navBarBtn (NavigationBarButton): The button to add.
        """

        self.addWidget(navBarBtn)
        self._btnGroup.addButton(navBarBtn)
