from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from qtapp.app import BaseApplication

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from qtapp.common.widgets import TreeView
from qtapp.plugins.models import ModuleListModel
from qtapp.plugins.settings import EnabledExtensionsSetting


class _ModuleListView(TreeView):
    """A TreeView used by the ModuleManagerDialog to show available Modules.

    Args:
        model (ModuleListModel): The ModuleListModel to show.
        parent (QWidget): The parent widget (default = None).
    """

    def __init__(
        self,
        model: ModuleListModel,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setModel(model)
        self.setPlaceholderText("No extensions available")

        self.header().setStretchLastSection(True)
        self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)


class ExtensionManagerDialog(QDialog):
    """A dialog that manages Modules and Plugins."""

    def __init__(
        self,
        app: "BaseApplication",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent, Qt.WindowType.Dialog)
        self._app = app

        self._model = self._app.pluginService.moduleListModel
        self.setupUi()

    def setupUi(self) -> None:
        self._moduleListView = _ModuleListView(self._model)

        self._label = QLabel(
            "Application restart is required to apply changes.",
        )
        self._label.setStyleSheet("QLabel { font-weight: bold; color: #cc0000; }")

        actionBtns = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        closeBtn = actionBtns.button(QDialogButtonBox.StandardButton.Close)
        closeBtn.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self._moduleListView, stretch=1)
        layout.addWidget(self._label)
        layout.addWidget(actionBtns)
        self.setLayout(layout)

        self.setWindowTitle("Extensions")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setFixedSize(700, 400)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Override from QMainWindow."""

        enabledModulesSetting: EnabledExtensionsSetting = (
            self._app.settingService.setting(EnabledExtensionsSetting.id)
        )
        enabledModulesSetting.writeList(
            [module.id for module in self._app.pluginService.enabledModules]
        )
        self._app.settingService.forceWrite()
        event.accept()
