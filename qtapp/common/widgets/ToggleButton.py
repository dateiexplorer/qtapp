from typing import Optional

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton, QWidget


class ToggleButton(QPushButton):
    """A custom QPushButton that can be toggled on and off.

    Args:
        parent (QWidget, optional): The parent widget. Defaults to None.
        icon (QIcon, optional): The icon to set for the button. Defaults to
            None.
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        icon: Optional[QIcon] = None,
    ) -> None:
        super().__init__(parent, icon=icon)
        self.setCheckable(True)
