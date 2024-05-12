from typing import Optional, Sequence

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMainWindow, QWidget

from qtapp.common.widgets.NavigationBar import NavigationBarButton
from qtapp.utils.registrable import BaseRegistry, Registrable


class BasePlugin(Registrable):
    """Base class for Plugins.

    A Plugin extends the application by functionality and can add, e.g., new
    windows, docks, settings.

    Every Plugin has an unique identifier (id) througout the application.

    Description:
        The plugin system consists of two layers: Modules (also referred as
        Extensions) and Plugins. One Module ships one or more Plugins.
        This allows to split the application in multiple granular Plugins and
        provide a set of these Plugins to the user in form of a Module that
        can be load with the built-in ModuleManager.

        A Plugin can contain multiple docks or settings, but only one
        NavigationBarButton associated to exactly one widget.
        Therefore, if a Module should add multiple widgets (with each
        associated to a NavigationBarButton), it must contain at a minimum the
        amount of Plugins of the widgets that should be added. However, most
        modules will consist of one Plugin.
    """

    def __init__(
        self,
        priority: int = 10,
        qtaIconStr: Optional[str] = None,
        toolTip: Optional[str] = None,
    ) -> None:
        super().__init__()

        self._priority = priority

        if qtaIconStr and toolTip:
            self._navBarBtn = NavigationBarButton(qtaIconStr, toolTip)
        else:
            self._navBarBtn = None

    @property
    def priority(self) -> int:
        """Priority level for the Plugin.

        The priority level is used to order the associated NavigationBarButton
        in the NavigationBar.
        A Plugin with higher priority is placed above a Plugin with lower
        priority.

        If multiple Plugins have the same priority level, they are placed in
        loading order, which can be change on each run.

        Note: The lower the number, the higher the priority. Thus, Plugins with
        the priority level `0` have the highest priority.

        Returns:
            Optional[int]: Plugin priority level. Set to `10` by default.
        """

        return self._priority

    @property
    def registrables(self) -> list[Registrable]:
        """A list of Registrables that will be activated and added to the
        corresponding services if the Plugin gets enabled.

        Note: All Registrables should be created in the Plugin's constructor
        and not in this property, otherwise this property will return a new
        instance of the Registrables which will lead to unintended behaviour.

        Another approach to add Registrables to the application is by adding
        them to the corresponding services manually.

        Returns:
            list[Registrable]: A list of all Registrables that will be
                activated if the Plugin is enabled.
        """
        return []

    def widget(self, parent: QWidget = None) -> Optional[QMainWindow]:
        """Get the main widget of the Plugin.

        This widget is shown in the applications main window.
        If no widget is set, the Plugin get still loaded in memory but has
        no associated NavigationBarButton in the applications NavigationBar and
        no widget.

        This could be useful for Plugins that does not have a separate UI but
        add functionality to other parts of the application, e.g., docks,
        settings.

        Note: The widget should be created in the Plugins' constructor and
        not in this function, otherwise this function will return a new instance
        each time it is called which will lead to unintended behaviour.

        Args:
            parent (QWidget): The parent widget (optional).

        Returns:
            Optional[QMainWindow]: Main widget of the plugin.
        """

        return None

    def navigationBarButton(self) -> Optional[NavigationBarButton]:
        return self._navBarBtn


class PluginRegistry(BaseRegistry):
    """Registry for managing Plugins in the application.

    Inherits from BaseRegistry.
    """

    def __init__(self) -> None:
        super().__init__(class_=BasePlugin)
