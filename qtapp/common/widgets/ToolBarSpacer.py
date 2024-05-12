from typing import Optional

from PySide6.QtWidgets import QSizePolicy, QWidget


class ToolBarSpacer(QWidget):
    """A widget that acts as a spacer in a QToolBar."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )
