import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self, Union


@dataclass(frozen=True)
class ModuleMetadata:
    id: str
    relativePath: str
    displayName: str
    description: str = None


@dataclass(frozen=True)
class Repository:
    """A Repository represents a collection of Modules."""

    path: Path
    modulesMetadata: list[ModuleMetadata]

    @classmethod
    def loadFromFile(cls, path: Union[str, Path]) -> Self:
        """Load and create a Repository from the provided json file.

        Args:
            path (Untion[str, Path]): Path to the Repository file.

        Returns:
            Self: A Repository instance.
        """

        path = Path(path).resolve()
        with open(path, "r", encoding="utf-8") as file:
            jsonData: list[dict[str, Any]] = json.load(file)

        # Create ModuleMetadata from this Repository.
        modulesMetadata = [ModuleMetadata(**obj) for obj in jsonData]

        return cls(
            path=path.parent,
            modulesMetadata=modulesMetadata,
        )


class Module:
    """A Module represents a set of Plugins that can be loaded as one piece
    of the application.

    Signals:
        statusChanged: This signal is emitted when the enabled status of this
            Module changes. It provides a boolean, wether the Module is enabled
            or not.
    """

    def __init__(self, dirPath: Path, metadata: ModuleMetadata):
        self._id = metadata.id
        self._displayName = metadata.displayName
        self._description = metadata.description
        self._path = dirPath.joinpath(metadata.relativePath)
        self._enabled = False

    @property
    def id(self) -> str:
        return self._id

    @property
    def displayName(self) -> str:
        return self._displayName

    @property
    def description(self) -> str:
        return self._description

    @property
    def path(self) -> Path:
        return self._path

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        self._enabled = enabled
