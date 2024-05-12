import signal
import sys
from pathlib import Path
from typing import Optional, Sequence

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QMainWindow,
    QMenuBar,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from qtapp import utils
from qtapp.common.services import FileService
from qtapp.common.widgets import (
    NavigationBar,
    NavigationBarButton,
    StatusBar,
    StatusBarButton,
)
from qtapp.docks import BaseDock
from qtapp.docks.services import DockService
from qtapp.plugins import BasePlugin
from qtapp.plugins.services import PluginService
from qtapp.plugins.settings import EnabledExtensionsSetting
from qtapp.settings import BaseSetting
from qtapp.settings.services import SettingService
from qtapp.utils.registrable import Registrable

_DEFAULT_ORGANIZATION_NAME = "qtapp"
_DEFAULT_APPLICATION_NAME = "qtapp"
_DEFAULT_APPLICATION_SIZE = QSize(1000, 600)


class BaseApplication:

    def __init__(self, args: Sequence[str], **kwargs) -> None:
        self._organizationName: str = kwargs.get(
            "organizationName",
            _DEFAULT_ORGANIZATION_NAME,
        )
        self._applicationName: str = kwargs.get(
            "applicationName",
            _DEFAULT_APPLICATION_NAME,
        )
        self._applicationSize: QSize = kwargs.get(
            "applicationSize",
            _DEFAULT_APPLICATION_SIZE,
        )
        self._styleSheet: Path = kwargs.get(
            "styleSheet",
            None,
        )

        self._app = QApplication(args)
        self._app.setOrganizationName(self.organizationName)
        self._app.setApplicationName(self.applicationName)

        self._setup()

        # Style must be applied before creating any windows.
        # Therefore the style is loaded at the very beginning in the application
        # lifecycle.
        self._setGlobalStyle()

        # Manage default services.
        self.pluginService = PluginService()
        self.pluginService.pluginAdded.connect(self.onPluginAdded)

        self.settingService = SettingService(
            self.organizationName, self.applicationName
        )
        self.settingService.addSetting(EnabledExtensionsSetting(self.settingService))

        self.dockService = DockService()
        self.fileService = FileService(self.settingService)

        self._mainWindow = _MainWindow(self)

    @property
    def organizationName(self) -> str:
        return self._organizationName

    @property
    def applicationName(self) -> str:
        return self._applicationName

    @property
    def mainWindow(self) -> QMainWindow:
        return self._mainWindow

    def run(self) -> None:
        plugins: list[BasePlugin] = list(self.pluginService.plugins().values())
        plugins.sort(key=lambda p: p.priority)
        for plugin in plugins:
            self._mainWindow.addPlugin(plugin)

        selectedPlugin = self.settingService.value(
            "application/selectedPlugin", None, str
        )
        if not selectedPlugin or not self.navigate(selectedPlugin, animate=False):
            actions = self._mainWindow._navBar.actions()
            if len(actions) > 0:
                button: NavigationBarButton = self._mainWindow._navBar.widgetForAction(
                    actions[0]
                )
                button.click()

        docks: list[BaseDock] = list(self.dockService.docks().values())
        for dock in docks:
            self._mainWindow.addDock(dock)

        self._showMainWindow()
        sys.exit(self._app.exec())

    def onPluginAdded(self, plugin: BasePlugin) -> None:
        for registrable in plugin.registrables:
            self.handleRegistrable(registrable)

    def handleRegistrable(self, registrable: Registrable) -> None:
        cls = type(registrable)
        if issubclass(cls, BaseDock):
            self.dockService.addDock(registrable)
        if issubclass(cls, BaseSetting):
            self.settingService.addSetting(registrable)

    def navigate(self, pluginId: str, animate: Optional[bool] = True) -> bool:
        """Navigate to the given plugin and select it.

        Args:
            plugin_id (str): The ID of the plugin to navigate to.

        Returns:
            bool: True if navigation was successfull, False otherwise.
        """

        plugin = self.pluginService.plugins().get(pluginId, None)
        self._mainWindow.setCurrentPlugin(plugin, animate)

    def setCurrentDock(self, dockId: str) -> None:
        """Open the dock with the specific ID in the UI.

        Args:
            id (str): The ID of the Dock.
        """

        dock = self.dockService.docks().get(dockId, None)
        if dock:
            dock.statusBarButton().animateClick()

    def _setup(self) -> None:
        # Make CTRL + C exit the program successfully.
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        # Workaround to set the icon of the application in the taskbar in
        # Windows.
        try:
            from ctypes import windll  # Only exists on Windows.

            appId = f"{self.organizationName}.{self.applicationName}"
            windll.shell32.SetCurrentProcessExplicitAppUserModelID(appId)
        except ImportError:
            pass

    def _setGlobalStyle(self) -> None:
        sheet = utils.readFileContent(Path(__file__).parent.joinpath("style.qss"))
        if self._styleSheet:
            customSheet = utils.readFileContent(self._styleSheet)
            sheet += customSheet

        self._app.setStyleSheet(sheet)

    def _showMainWindow(self) -> None:
        maximized = self.settingService.value(
            "application/maximized",
            False,
            bool,
        )
        if maximized:
            self._mainWindow.showMaximized()
        else:
            self._mainWindow.show()


class _MainWindow(QMainWindow):
    def __init__(self, app: BaseApplication) -> None:
        super().__init__(None)
        self._app = app

        self._selectedPlugin: BasePlugin = None

        self._currentDock: QDockWidget = None
        self._dockBtns: dict[str, StatusBarButton] = {}

        self.setupUi()
        self._applySettings()

    def setupUi(self) -> None:
        # Prevent showing a context menu to hide ToolBars on right click.
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        # NavigationBar
        self._navBar = NavigationBar(self)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self._navBar)

        # StatusBar
        self._statusBar = StatusBar(self)
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self._statusBar)

        # MenuBar
        self._menuBar = QMenuBar()
        self.setMenuBar(self._menuBar)

        # Central widget
        self._stack = QStackedWidget(self)

        centralLayout = QVBoxLayout()
        centralLayout.setContentsMargins(0, 0, 0, 0)
        centralLayout.addWidget(self._stack)
        centralWidget = QWidget()
        centralWidget.setLayout(centralLayout)
        self.setCentralWidget(centralWidget)

    def _applySettings(self) -> None:
        settings = self._app.settingService
        size = settings.value(
            "application/size",
            self._app._applicationSize,
            QSize,
        )
        maximized = settings.value(
            "application/maximized",
            False,
            bool,
        )
        if maximized:
            size = self._app._applicationSize

        self.resize(size)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Overwrite from QMainWindow."""

        settings = self._app.settingService
        settings.setValue("application/size", self.size())
        settings.setValue("application/maximized", self.isMaximized())

        event.accept()

    def addPlugin(self, plugin: BasePlugin) -> None:
        widget = plugin.widget(self)
        navBarBtn = plugin.navigationBarButton()
        if not widget or not navBarBtn:
            return

        widget.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self._stack.addWidget(widget)

        self._navBar.addButton(navBarBtn)
        navBarBtn.clicked.connect(lambda: self._stack.setCurrentWidget(widget))

    def addDock(self, dock: BaseDock) -> None:
        statusBarBtn = dock.statusBarButton()
        if not statusBarBtn:
            return

        self._statusBar.addButton(statusBarBtn)
        self._dockBtns[dock.id] = statusBarBtn

        widget = dock.widget(self)
        if not widget:
            return

        # Ensure that every QDockWidgets has at least the following
        # configurations set.
        widget.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)
        widget.setVisible(False)

        def _onVisibilityChanged(visible: bool):
            if not visible and self._currentDock == widget:
                self.setCurrentDockWidget(None)

        widget.visibilityChanged.connect(_onVisibilityChanged)

        # A click on the button causes to open the associated QDockWidget.
        statusBarBtn.clicked.connect(lambda: self.setCurrentDockWidget(widget))

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, widget)

    def setCurrentPlugin(self, plugin: BasePlugin, animate: bool = True) -> bool:
        if not plugin:
            return False

        button = plugin.navigationBarButton()
        if not button:
            return False

        button.animateClick() if animate else button.click()
        self._selectedPlugin = plugin
        return True

    def setCurrentDockWidget(self, dock: QDockWidget) -> None:
        """Set the current dock widget.

        Args:
            dock (QDockWidget): The dock widget to set.
        """

        if self._currentDock is not None:
            self._currentDock.setVisible(False)

        if dock is not None:
            dock.setVisible(True)

        self._currentDock = dock
