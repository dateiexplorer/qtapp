from importlib import util
from pathlib import Path
from types import ModuleType
from typing import Optional, TypeVar

from PySide6.QtCore import QObject, Signal

from qtapp.exceptions import RegistrableAlreadyExistsError, RegistrableNotFoundError


class Registrable(QObject):
    """Base class for objects that can be registered in a Registry.

    This can be all types of objects that can be defined and searched by a
    unique identifier.
    """

    id: str = None

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)


T = TypeVar("T", bound=Registrable)


class RegistrableLoader:

    @staticmethod
    def _loadRegistrablesFromModule(
        module: Path, class_: T, *args, **kwargs
    ) -> list[T]:
        """Load an instance of each Registrable of type class_ from the
        specified module into memory.

        Args:
            module (Path): The path to the module containing the Registrables
                objects to load.
            class_ (Type[T]): The class type of the Registrables to load from
                the module.

        Returns:
            list[T]: A list of instances loaded from the module.

        Raises:
            FileNotFoundError: If the specified module file is not found.
            Exception: If any other error occurs while loading the module file.
        """

        if not _isValidModule(module.name, module.suffix):
            return []

        try:
            module = _loadModule(module.stem, str(module))
        except FileNotFoundError as err:
            raise err
        except Exception as err:
            raise err

        registrables: list[T] = []
        for _, obj in module.__dict__.items():
            if isinstance(obj, type) and issubclass(obj, class_) and obj != class_:
                registrable: T = obj(*args, **kwargs)
                registrables.append(registrable)

        return registrables

    @staticmethod
    def load(path: str | Path, class_: T, *args, **kwargs) -> list[T]:
        """Load an instance of each Registrable of type class_ from the
        specified path (modules and all submodules).

        Recursively searches for valid module files and instanciates each
        Registrable of class_ or subclasses and returns it in a list.

        Args:
            path (Union[str, Path]): The path to the file or directory
                containing the Registrables.
            class_ (Type[T]): The class type of the Registrables to load.

        Returns:
            list[T]: A list of instances of Registrables of class class_ found
                in modules or submodules of the specific path.

        Raises:
            FileNotFoundError: If the specified path is not found.
            PermissionError: If permission is denied while accessing the
                specified path.
            Exception: If any other error occurs while loading the module or
                instanciate the Registrable.
        """

        path = Path(path)
        registrables: list[T] = []
        try:
            if path.is_dir():
                for itemFile in path.iterdir():
                    if itemFile.is_dir():
                        registrables.extend(
                            RegistrableLoader.load(itemFile, class_, *args, **kwargs)
                        )
                    else:
                        registrables.extend(
                            RegistrableLoader._loadRegistrablesFromModule(
                                itemFile,
                                class_,
                                *args,
                                **kwargs,
                            )
                        )
            else:
                registrables.extend(
                    RegistrableLoader._loadRegistrablesFromModule(
                        path,
                        class_,
                        *args,
                        **kwargs,
                    )
                )
        except FileNotFoundError as err:
            raise err
        except PermissionError as err:
            raise err
        except Exception as err:
            raise err

        return registrables


class BaseRegistry(QObject):
    """Base class for Registries, that hold and manage Registrable objects.

    Loading Registrable into the Registry takes two steps. First, with the
    RegistrableLoader Registrables get detected and load into memory. Second,
    the add method actually add loaded Registrables to the Registry.

    Signals:
        registrableAdded (Signal): Signal emitted when an Registrable is added
            to the Registry. The signal carries the added Registrable as a
            parameter.
        registrableRemoved (Signal): Signal emitted when a Registrable is
            removed from the Registry. The signal carries the removed
            Registrable as a parameter.
    """

    registrableAdded = Signal(object)
    registrableRemoved = Signal(object)

    def __init__(self, class_: T) -> None:
        """Initialize the BaseRegistry instance.

        Args:
            class_ (Type[T]): A Registrable object type that this Registry
                manages.
        """

        super().__init__()

        self._registrables: dict[str, T] = {}
        self._class = class_

    def registrable(self, id: str) -> Optional[T]:
        return self._registrables.get(id, None)

    def registrables(self) -> dict[str, T]:
        """Retrieve all Registrables stored in the Registry by their unique
        identifier.

        Returns:
            dict[str, T]: A dictionary containing all Registrables in the
                Registry where unique identifierts are keys and Registrables
                the corresponding values.
        """

        return self._registrables

    def add(self, registrable: T | list[T]) -> None:
        """Add a Registrable or list of Registrables to the Registry.

        Args:
            registrable (T | list[T]): The Registrable or list of Registrables
                to add to the Registry.

        Raises:
            RegistrableAlreadyExistsError: If Registrable already exists in the
                Registry.
        """
        if isinstance(registrable, list):
            for r in registrable:
                self.add(r)
        else:
            if self._registrables.get(registrable.id) is not None:
                raise RegistrableAlreadyExistsError()
            else:
                self._registrables[registrable.id] = registrable
                self.registrableAdded.emit(registrable)

    def remove(self, registrable: T | list[T]) -> None:
        """Remove a Registrable or list of Registrables from the Registry.

        Args:
            registrable (T | list[T]): The Registrable or list of Registrables
                to remove from the Registry.

        Raises:
            RegistrableNotFoundError: If Registrable not found in the Registry.
        """

        if isinstance(registrable, list):
            for r in registrable:
                self.remove(r)
        else:
            if self._registrables.get(registrable.id) is None:
                raise RegistrableNotFoundError()
            else:
                self._registrables.pop(registrable.id)
                self.registrableRemoved.emit(registrable)


def _loadModule(name: str, path: str) -> ModuleType:
    """Load a Python module from a specific file path.

    Args:
        name (str): The name of the module.
        path (str): The path to the module file.

    Returns:
        ModuleType: The loaded module.

    Raises:
        FileNotFoundError: If the specified module file cannot be found.
        Exception: If any other error occurs while loading the module.
    """

    try:
        spec = util.spec_from_file_location(name, path)
        module = util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except FileNotFoundError as err:
        raise err
    except Exception as err:
        # Catch any exception that can occur by loading the module.
        raise err

    return module


def _isValidModule(modname: str, ext: str) -> bool:
    """Check if the given module has a valid module name.

    Args:
        modname (str): The module name.
        ext (str): The file extension.

    Returns:
        bool: True if the module name is valid, False otherwise.
    """

    return ext == ".py" and not modname.startswith(".")
