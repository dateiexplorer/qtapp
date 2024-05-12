from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Signal

from qtapp.plugins.schemas import Module, Repository
from qtapp.plugins.models import ModuleListModel
from qtapp.utils.registrable import RegistrableLoader

from . import BasePlugin, PluginRegistry


class PluginService(QObject):
    """Service for managing Modules and Plugins."""

    pluginAdded = Signal(BasePlugin)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        # Holds all available Plugins.
        self._registry = PluginRegistry()

        # Model which holds all Modules from all repositories.
        self._moduleListModel = ModuleListModel()

        self.registry.registrableAdded.connect(
            lambda plugin: self.pluginAdded.emit(plugin)
        )

    @property
    def registry(self) -> PluginRegistry:
        return self._registry

    @property
    def moduleListModel(self) -> ModuleListModel:
        """Get a model which holds all Modules from all Repositories.

        Returns:
            ModuleListModel: The model which holds all Modules.
        """

        return self._moduleListModel

    @property
    def enabledModules(self) -> list[Module]:
        """Get IDs of all currently enabled Module.

        Returns:
            list[str]: List of IDs of currently enabled Modules.
        """

        moduleList = self.moduleListModel.items
        return [module for module in moduleList if module.enabled]

    def load(self, repositoryFiles: list[Path], moduleIds: list[str]) -> None:
        for repositoryFile in repositoryFiles:
            repository = Repository.loadFromFile(repositoryFile)
            self.addModulesFromRepository(repository)

        for module in self.moduleListModel.items:
            if module.id in moduleIds:
                self.addPluginsFromModule(module)

    def addModulesFromRepository(self, repository: Repository) -> None:
        for metadata in repository.modulesMetadata:
            module = Module(repository.path, metadata)
            self.addModule(module)

    def addModule(self, module: Module) -> None:
        self._moduleListModel.appendItem(module)

    def addPluginsFromModule(self, module: Module) -> None:
        module.enabled = True
        plugins: list[BasePlugin] = RegistrableLoader.load(module.path, BasePlugin)
        for plugin in plugins:
            self.addPlugin(plugin)

    def addPlugin(self, plugin: BasePlugin) -> None:
        self._registry.add(plugin)

    def plugin(self, id: str) -> BasePlugin:
        """Retrieve a Plugin based on its ID.

        Args:
            id (str): The ID of the Plugin.

        Returns:
            BasePlugin: The Plugin corresponding to the ID, None if not found.
        """

        return self._registry.registrable(id)

    def plugins(self) -> dict[str, BasePlugin]:
        """Retrieve all registered Plugins.

        Returns:
            dict[str, BasePlugin]: A dictionary of all registered Plugins,
                with IDs as keys.
        """

        return self._registry.registrables()
