from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from qtapp.app import BaseApplication

from PySide6.QtCore import QRegularExpression, QRegularExpressionMatch, Qt, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QCompleter,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from qtapp.common.widgets import SearchEdit
from qtapp.settings.services import SettingService

from . import BaseSetting


class _SettingWidget(QWidget):
    def __init__(self, setting: BaseSetting, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setting: BaseSetting = setting

        self.setupUi()

    def setupUi(self) -> None:
        titleLbl = QLabel(self._setting.displayName)
        titleLbl.setStyleSheet("QLabel { font-weight: bold; }")
        titleLbl.setWordWrap(True)

        descriptionLbl = QLabel(self._setting.description)
        descriptionLbl.setWordWrap(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(titleLbl)
        layout.addWidget(descriptionLbl)
        layout.addWidget(self._setting.widget())

        self.setLayout(layout)

    def setting(self) -> BaseSetting:
        return self._setting


class SettingsManagerDialog(QDialog):
    def __init__(
        self,
        app: "BaseApplication",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._app = app

        self._widgets: list[_SettingWidget] = []
        self._completions: list[str] = []

        registry = self._app.settingService.registry
        registry.registrableAdded.connect(self._onSettingRegistryChanged)
        registry.registrableRemoved.connect(self._onSettingRegistryChanged)

        self.setupUi()

    def setupUi(self) -> None:
        self._paneLayout = QVBoxLayout()
        self._paneLayout.setSpacing(16)

        paneWidget = QWidget()
        paneWidget.setLayout(self._paneLayout)

        scrollArea = QScrollArea()
        scrollArea.setWidget(paneWidget)
        scrollArea.setWidgetResizable(True)

        actionBtns = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        closeBtn = actionBtns.button(QDialogButtonBox.StandardButton.Close)
        closeBtn.clicked.connect(self.close)

        completer = QCompleter(self._completions)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        self._search = SearchEdit()
        self._search.searchChanged.connect(self._onSearchChanged)
        self._search.setCompleter(completer)

        layout = QVBoxLayout()
        layout.addWidget(self._search)
        layout.addWidget(scrollArea)
        layout.addWidget(actionBtns)
        self.setLayout(layout)

        self.setWindowTitle("Settings")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setFixedSize(700, 400)

    @Slot()
    def _onSettingRegistryChanged(self, registrable: BaseSetting) -> None:
        # Don't perform this operation if the registrable doesn't change the
        # layout.
        if registrable.displayName is None or registrable.widget() is None:
            return

        managableSettings = list(
            filter(
                lambda s: s.displayName is not None and s.widget() is not None,
                list(self._app.settingService.settings().values()),
            )
        )

        # Sort settings.
        managableSettings.sort(key=lambda s: s.displayName)

        self._widgets.clear()
        for setting in managableSettings:
            self._widgets.append(_SettingWidget(setting))

        # Remove widgets from the pane layout.
        while self._paneLayout.count():
            item = self._paneLayout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        # Adding new widgets to the pane layout.
        for widget in self._widgets:
            self._paneLayout.addWidget(widget)

        self._paneLayout.addStretch()

        # Adjust the completions for the completer.
        self._completions.clear()
        self._completions.extend(
            [
                s.displayName
                for s in list(self._app.settingService.settings().values())
                if s.displayName
            ]
        )

    @Slot()
    def _onSearchChanged(self, text: str) -> None:
        regex = QRegularExpression(
            text,
            options=QRegularExpression.PatternOption.CaseInsensitiveOption,
        )

        self._paneLayout.parentWidget().setUpdatesEnabled(False)
        for widget in self._widgets:
            regexMatch: QRegularExpressionMatch = regex.match(
                widget.setting().displayName
            )
            widget.setVisible(regexMatch.hasMatch())
        self._paneLayout.parentWidget().setUpdatesEnabled(True)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Override from QMainWindow.

        Force to write the current settings to the file if window is closed.
        """

        self._app.settingService.forceWrite()
        event.accept()
