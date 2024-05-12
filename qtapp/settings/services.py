from pathlib import Path
from typing import Any, Optional, Union

from PySide6.QtCore import QObject, QSettings, Signal

from qtapp.utils.registrable import RegistrableLoader

from . import BaseSetting, SettingsRegistry


class SettingService(QObject):
    """Service for managing application settings."""

    settingAdded = Signal(BaseSetting)

    def __init__(
        self,
        organization: str,
        application: str,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        # Holds all available Settings
        self._registry = SettingsRegistry()

        self._setup(organization, application)

    def _setup(self, organization: str, application: str) -> None:
        self._internal = QSettings(
            QSettings.Format.IniFormat,
            QSettings.Scope.UserScope,
            organization,
            application,
        )

    @property
    def registry(self) -> SettingsRegistry:
        return self._registry

    @property
    def internal(self) -> QSettings:
        return self._internal

    def addSetting(self, setting: BaseSetting):
        """Add a setting to the registry.

        Args:
            setting (BaseSetting): The setting to be added.
        """

        self._registry.add(setting)

    def setting(self, id: str) -> BaseSetting:
        """Retrieve a setting based on its ID.

        Args:
            id (str): The ID of the setting.

        Returns:
            BaseSetting: The setting corresponding to the ID, or None if not
                found.
        """

        return self._registry.registrables().get(id, None)

    def settings(self) -> dict[str, BaseSetting]:
        """Retrieve all registered settings.

        Returns:
            dict[str, BaseSetting]: A dictionary of all registered settings,
                with IDs as keys.
        """

        return self._registry.registrables()

    def load(self, path: Union[str, Path]):
        """Load settings from a specific path into the SettingsRegistry.

        Args:
            path (Union[str, Path]): The path to the settings.
        """

        settings = RegistrableLoader.load(path, BaseSetting, settingService=self)
        self._registry.add(settings)

    def setValue(self, key: str, value: Any):
        """Set the value of a setting.

        Args:
            key (str): The key of the setting.
            value (Any): The value to be set.
        """

        self._internal.setValue(key, value)

        setting: BaseSetting = self._registry.registrables().get(key, None)
        if setting is not None:
            setting.dataChanged.emit(value)

    def value(
        self,
        key: str,
        default_value: Optional[Any] = ...,
        type: Optional[object] = ...,
    ) -> object:
        """
        Retrieve the value of a setting.

        Args:
            key (str): The key of the setting.
            default_value (Optional[Any]): The default value to be returned if
                the setting is not found. Defaults to Ellipsis.
            type (Optional[object]): The type of the value to be returned.
                Defaults to Ellipsis.

        Returns:
            object: The value of the setting.
        """

        return self._internal.value(key, default_value, type)

    def forceWrite(self):
        """Forces the settings to be written to storage."""

        self._internal.sync()
