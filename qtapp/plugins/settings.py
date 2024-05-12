from typing import Optional

from PySide6.QtCore import QObject

from qtapp.settings import BaseSetting
from qtapp.settings.services import SettingService


class EnabledExtensionsSetting(BaseSetting):
    """Setting for managing enabled modules.

    This setting has no UI and can only be changed programmatically.
    """

    id = "application/enabledExtensions"

    def __init__(
        self,
        settingService: SettingService,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self._settingService = settingService

    def writeList(self, enabled_modules: list[str]):
        """Write the enabled module IDs to the settings file.

        Args:
            enabled_modules (list[str]): The list of enabled module IDs.
        """

        settings = self._settingService.internal
        size = len(enabled_modules)
        settings.beginWriteArray(self.id, size)

        for i in range(size):
            settings.setArrayIndex(i)
            settings.setValue("id", enabled_modules[i])

        settings.endArray()

    def readList(self) -> list[str]:
        """Read enabled module IDs from the settings file.

        Returns:
            list[str]; The list of enabled module IDs.
        """

        settings = self._settingService.internal
        size = settings.beginReadArray(self.id)

        enabled_modules: list[str] = []
        for i in range(size):
            settings.setArrayIndex(i)
            enabled_modules.append(settings.value("id"))

        settings.endArray()
        return enabled_modules
