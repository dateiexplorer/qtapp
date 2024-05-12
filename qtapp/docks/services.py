from . import BaseDock, DocksRegistry


class DockService:
    """Service class for managing Docks. A Dock is a container attached to the
    right side of the main application window.

    This class manages the registration and retrieval of dock widgets through
    the DocksRegistry.
    """

    def __init__(self) -> None:
        super().__init__()
        self._registry = DocksRegistry()

    def registry(self) -> DocksRegistry:
        """Get the DocksRegistry containing the available Docks in the service.

        Returns;
            DocksRegistry: The DocksRegistry containing the available Docks.
        """

        return self._registry

    def addDock(self, dock: BaseDock) -> None:
        """Add a dock widget to the registry.

        Args:
            dock (BaseDock): The dock widget to be added.
        """

        self._registry.add(dock)

    def dock(self, id: str) -> BaseDock:
        """Retrieve a Dock based on its ID.

        Args:
            id (str); The ID of the Dock.

        Returns:
            BaseDock. The dock corresponding to the ID, None if not found.
        """

        return self._registry.registrables().get(id, None)

    def docks(self) -> dict[str, BaseDock]:
        """Get the dictionary of registered dock widgets.

        The dictionary contains the dock widgets categorized by their ID.

        Returns:
            dict[str, DocksRegistry]: The dictionary of registered dock
                widgets.
        """

        return self._registry.registrables()
