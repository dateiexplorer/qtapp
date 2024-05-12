from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QFileDialog

from qtapp.settings.services import SettingService


class FileService:
    def __init__(self, settingService: SettingService):
        self._settingService = settingService
        self._dialog = QFileDialog()

        # FIXME: Loading the state doesn't work.
        # state = settingsService.value("application/fileDialogState", None, bytes)
        # success = self._dialog.restoreState(QByteArray(state))
        success = False

        if not success:
            documentsLocations = QStandardPaths.standardLocations(
                QStandardPaths.StandardLocation.DocumentsLocation
            )
            if documentsLocations:
                standardPath = documentsLocations[0]
            else:
                standardPath = QStandardPaths.standardLocations(
                    QStandardPaths.StandardLocation.HomeLocation
                )[0]

            self._dialog.setDirectory(standardPath)

    @property
    def dialog(self) -> QFileDialog:
        return self._dialog

    def saveState(self):
        state = self._dialog.saveState()
        self._settingService.setValue(
            "application/fileDialogState",
            state,
        )
