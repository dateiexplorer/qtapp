from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from qtapp.settings.services import SettingService

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget

from qtapp.utils.registrable import BaseRegistry, Registrable


class BaseSetting(Registrable):
    """Base class for settings in the application.

    Signals:
        dataChanged: Signal emitted when the setting's data is changed.
    """

    dataChanged = Signal(object)

    def __init__(
        self,
        settingService: "SettingService",
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self._settingService = settingService

    @property
    def displayName(self) -> Optional[str]:
        """Display name of the setting.

        Returns:
            str: The display name of the setting (optional).
        """

        return None

    @property
    def description(self) -> Optional[str]:
        """Description of the setting.

        Returns:
            str: The description of the setting (optional).
        """

        return None

    @property
    def defaultValue(self) -> Optional[Any]:
        """Default value of the setting.

        Returns:
            Any: The default value of the setting (optional).
        """

        return None

    def widget(self) -> Optional[QWidget]:
        """Returns a QWidget for the setting.

        This widget is used by the settings dialog to change the setting's
        value. Subclasses should override this method to provide a widget
        for the setting.

        Returns:
            QWidget: The widget for the setting (optional).
        """

        return None


class SettingsRegistry(BaseRegistry):
    """Registry for managing settings in the application.

    Inherits from BaseRegistry.
    """

    def __init__(self) -> None:
        super().__init__(class_=BaseSetting)
