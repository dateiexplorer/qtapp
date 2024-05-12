import sys
from typing import Optional

from PySide6.QtGui import Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget

from qtapp.app import BaseApplication
from qtapp.plugins import BasePlugin
from qtapp.plugins.widgets import ExtensionManagerDialog
from qtapp.settings.widgets import SettingsManagerDialog


class DemoWidget(QMainWindow):

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setupUi()

    def setupUi(self) -> None:
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(QLabel("Demo"))

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)


class DemoPlugin(BasePlugin):
    id = "demo"

    def __init__(
        self,
    ) -> None:
        super().__init__(10, "ph.ghost-light", "Demo")
        self._widget = DemoWidget()

    def widget(self, parent: Optional[QWidget] = None) -> Optional[QMainWindow]:
        if parent:
            self._widget.setParent(parent)

        return self._widget


app = BaseApplication(sys.argv)


def main():
    """Run the application."""

    extensionManager = ExtensionManagerDialog(app, app.mainWindow)
    settingManager = SettingsManagerDialog(app, app.mainWindow)

    app.pluginService.addPlugin(DemoPlugin())
    app.mainWindow.menuBar().addAction("Extensions", extensionManager.open)
    app.mainWindow.menuBar().addAction("Settings", settingManager.open)
    app.run()


if __name__ == "__main__":
    main()
