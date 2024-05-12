from typing import Optional

from PySide6.QtWidgets import QDockWidget, QWidget

from qtapp.common.widgets import StatusBarButton
from qtapp.utils.registrable import BaseRegistry, Registrable


class BaseDock(Registrable):
    """Base class for dock widgets in the application.

    Inherits from Registrable.
    """

    def statusBarButton(self) -> Optional[StatusBarButton]:
        """Returns the status bar button associated with the dock widget.

        Returns:
            StatusBarButton: The status bar button associated with the dock
                widget.
        """

        return None

    def widget(self, parent: QWidget = None) -> Optional[QDockWidget]:
        """Returns the QDockWidget representing the dock widget.

        Args:
            parent (QWidget, optional): The parent widget for the dock widget.
                Defaults to None.

        Returns:
            QDockWidget: The QDockWidget representing the dock widget.
        """

        return None


class DocksRegistry(BaseRegistry):
    """Registry class for managing BaseDocks.

    Inherits from BaseRegistry.
    """

    def __init__(self) -> None:
        super().__init__(class_=BaseDock)
