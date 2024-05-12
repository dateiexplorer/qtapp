from typing import Any, Generic, Optional, Sequence, TypeVar

from PySide6.QtCore import (
    QAbstractTableModel,
    QMimeData,
    QModelIndex,
    QObject,
    Qt,
    Signal,
)

T = TypeVar("T")


class ItemTableModel(QAbstractTableModel, Generic[T]):
    """Custom QAbstractTableModel for displaying items.

    An item can be any Python object. However, the preferred approach is to use
    dataclass objects so that the 'isPresent' method not only compares the
    pointer addresses but the objects content by default. Otherwise, it is
    highly recommended to overwrite the 'isPresent' method.

    Signals:
        itemAdded: This Signal is emitted whenever an item is added to the
            model. It provides the added item.
        itemRemoved: This Signal is emitted whenever an item gets removed from
            the model. It provides the removed item.
    """

    ItemRole = Qt.ItemDataRole.UserRole + 1
    """A custom ItemDataRole for the ItemTableModel. Using this role, it is
    ensured that it always returns the item data object."""

    itemAdded = Signal(object)
    itemRemoved = Signal(object)

    def __init__(
        self,
        headers: Sequence[str],
        parent: Optional[QObject] = None,
    ) -> None:
        """Initialize the ItemTableModel.

        Args:
            headers (Sequence[str]): Column headers for the table model. These
                headers are displayed in views, such as QTreeView, QListView.
            parent (QObject): The parent of this model.
        """

        super().__init__(parent)
        self._headers = headers
        self._items: list[T] = []

    @property
    def items(self) -> list[T]:
        """Get the list of items.

        Returns:
            list[T]: The list of items.
        """

        return self._items

    def isPresent(self, item: T) -> bool:
        """Check if an item is present in the table.

        By default references are checked. If other criterias must be met to
        decide wether a item is already present, overwrite this function in the
        corresponding model.

        Args:
            item (T): The item to check.

        Returns:
            bool: True if the item is present, False otherwise.
        """

        return item in self.items

    def setItems(self, items: list[T]) -> None:
        """Set the list of items for the table.

        This method emits the dataChanged Signal, but not the itemAdded
        or itemRemoved Signal.

        Args:
            items (list[T]): The list of items.
        """

        self.beginResetModel()
        self._items = items
        self.endResetModel()
        self.dataChanged.emit(0, self.rowCount())

    def appendItem(self, item: T) -> bool:
        """Append an item to the end of the model.

        Args:
            item (T): The item to add.

        Returns:
            bool: True if the item was added successfully, False if the item is
                already present.
        """

        if self.isPresent(item):
            return False

        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.items.append(item)
        self.itemAdded.emit(item)
        self.endInsertRows()
        self.dataChanged.emit(self.rowCount(), self.rowCount())
        return True

    def insertItem(self, row: int, item: T) -> bool:
        """Insert an item at a specific row of the model.

        Args:
            row (int): The row index to insert the item.
            item (T): The item to add.

        Returns:
            bool: True if the item was added successfully, False if the item is
                already present.
        """

        if self.isPresent(item):
            return False

        self.beginInsertRows(QModelIndex(), row, row)
        self.items.insert(row, item)
        self.itemAdded.emit(item)
        self.endInsertRows()
        self.dataChanged.emit(row, row)
        return True

    def removeItem(self, item: T) -> bool:
        """Remove an item from the model.

        Args:
            item (T): The item to remove.

        Returns:
            bool: True if the item was removed successfully, False if the item
                was not found.
        """

        if item not in self.items:
            return False

        self.beginRemoveRows(QModelIndex(), 0, self.rowCount())
        self.items.remove(item)
        self.itemRemoved.emit(item)
        self.endRemoveRows()
        self.dataChanged.emit(0, self.rowCount())
        return True

    def item(self, index: QModelIndex) -> T:
        """Get the item at the specified index.

        This is the same like calling the data method with the index and the
        ItemRole.

        Args:
            index (QModelIndex): The index of the item.

        Returns:
            T: The item at the index.
        """

        return self.data(index, ItemTableModel.ItemRole)

    def indexOf(self, item: T) -> int:
        """Get the row index of an item in the model.

        Args:
            item (T): The item.

        Returns:
            int: The row index of the item in the model. If the item is not
                found, -1 is returned.
        """

        for index, value in enumerate(self.items):
            if value == item:
                return index

        return -1

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: Qt.ItemDataRole,
    ) -> Any:
        """Override from QAbstractItemModel.

        Get the header data for the specified section.

        Args:
            section (int): The section index.
            orientation (Qt.Orientation): The orientation of the header.
            role (Qt.ItemDataRole): The role of the header data.

        Returns:
            Any: The header data.
        """

        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignLeft

        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            return self._headers[section]

    def data(
        self,
        index: QModelIndex,
        role=Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Override from QAbstractItemModel.

        Get the data for the specified index and role.

        Args:
            index (QModelIndex): The index of the item.
            role (Qt.ItemDataRole): The role of the data.

        Returns:
            Any: The data for the specified index and role.
        """

        if not index.isValid():
            return None

        item: T = self.items[index.row()]
        if role == ItemTableModel.ItemRole:
            return item

        return None

    def rowCount(self, index=QModelIndex()) -> int:
        """Override from QAbstractItemModel.

        Get the number of rows in the model.

        Args:
            index (QModelIndex): The index of the item.

        Returns:
            int: The number of rows in the model.
        """

        return len(self.items)

    def columnCount(self, index=QModelIndex()) -> int:
        """Override from QAbstractItemModel.

        Get the number of columns in the model.

        Args:
            index (QModelIndex): The index of the item.

        Returns:
            int: The number of columns in the model.
        """

        return len(self._headers)


class ItemMimeData(QMimeData):
    """A custom QMimeData class which holds a list of items.

    An item can be any Python object.

    Args:
        items (list[Any]): The list of items.
    """

    def __init__(self, items: list[Any]) -> None:
        super().__init__()
        self._items = items
