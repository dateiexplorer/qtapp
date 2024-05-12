from typing import Any, Optional, Self, Union

from PySide6.QtCore import (
    QAbstractItemModel,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QRegularExpression,
    Qt,
)


class _JsonTreeItem:
    """A item corresponding to a line in QTreeView."""

    def __init__(self, parent: Optional[Self] = None) -> None:
        """Initialize the _JsonTreeItem.

        Args:
            parent (Optional[_JsonTreeItem]): The parent item.
                (default = None).
        """

        self._parent = parent
        self._key = ""
        self._value = ""
        self._valueType = None
        self._children = []

    @property
    def key(self) -> str:
        """Get the key name.

        Returns:
            str: The key name.
        """

        return self._key

    @key.setter
    def key(self, key: str) -> None:
        """Set the key name of the current item.

        Args:
            key (str): The key name to set.
        """

        self._key = key

    @property
    def value(self) -> str:
        """Get the value name of the current item.

        Returns:
            str: The value name.
        """

        return self._value

    @value.setter
    def value(self, value: str) -> None:
        """Set the value name of the current item.

        Args:
            value (str): The value name to set.
        """

        self._value = value

    @property
    def valueType(self) -> None:
        """Get the Python type of the item's value.

        Returns:
            value_type (type): The Python type of the item's value.
        """

        return self._valueType

    @valueType.setter
    def valueType(self, value):
        """Set the Python type of the item's value.

        Args:
            value_type (type): The Python type of the item's value.
        """
        self._valueType = value

    def appendChild(self, item: Self):
        """Add an item as a child.

        Args:
            item (_JsonTreeItem): The child item to add.
        """

        self._children.append(item)

    def child(self, row: int) -> Self:
        """Get the child item at the specified row.

        Args:
            row (int): The row index of the child item.

        Returns:
            _JsonTreeItem: The child item at the specified row.
        """

        return self._children[row]

    def parent(self) -> Self:
        """Get the parent item.

        Returns:
            JsonTreeItem: The parent item.
        """

        return self._parent

    def row(self) -> int:
        """Get the row index where the current item occupies in the parent.

        Returns:
            int: The row index of the current item in the parent.
        """

        return self._parent._children.index(self) if self._parent else 0

    def childCount(self) -> int:
        """Get the number of children of the current item.

        Returns:
            int: The number of children of the current item.
        """

        return len(self._children)

    @classmethod
    def load(
        cls,
        value: Union[list, dict],
        parent: Optional[Self] = None,
        sort: Optional[bool] = True,
    ) -> Self:
        """Create a root _JsonTreeItem from a nested list or a nested
        dictonary.

        Examples:
            with open("file.json") as file:
                data = json.dump(file)
                root = _JsonTreeItem.load(data)

        This method is a recursive function that calls itself.

        Returns:
            _JsonTreeItem: A _JsonTreeItem.
        """

        rootItem = _JsonTreeItem(parent)
        rootItem.key = "root"

        if isinstance(value, dict):
            items = sorted(value.items()) if sort else value.items()

            for key, value in items:
                child = cls.load(value, rootItem)
                child.key = key
                child.valueType = type(value)
                rootItem.appendChild(child)

        elif isinstance(value, list):
            for index, value in enumerate(value):
                child = cls.load(value, rootItem)
                child.key = index
                child.valueType = type(value)
                rootItem.appendChild(child)

        else:
            rootItem.value = value
            rootItem.valueType = type(value)

        return rootItem


class JsonModel(QAbstractItemModel):
    """An editable model of JSON data."""

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)

        self._rootItem = _JsonTreeItem()
        self._headers = ["Identifier", "Value"]
        self._indexVisitOrder = []

    def _calculateIndexVisitOrder(self) -> list[QModelIndex]:
        """Calculate the order of index traversal.

        Returns:
            list[QModelIndex]: The list of QModelIndex objects in the traversal
                order.
        """

        rootIndex = self.index(0, 0)
        result: list[QModelIndex] = [rootIndex]

        index = rootIndex
        while True:
            index = self._nextIndex(index)

            # If root is reached again all indexes were visited.
            if index == rootIndex:
                break

            result.append(index)

        return result

    def beginResetModel(self) -> None:
        """Override from QAbstractItemModel."""

        super().beginResetModel()
        self._indexVisitOrder.clear()

    def endResetModel(self) -> None:
        """Override from QAbstractItemModel."""

        super().endResetModel()
        self._indexVisitOrder = self._calculateIndexVisitOrder()

    def clear(self) -> None:
        """Clear data from the model."""

        self.load({})

    def load(self, document: dict) -> bool:
        """Load model from a nested dictionary returned by json.loads().

        Args:
            document (dict): JSON-compatible dictionary

        Returns:
            bool: True if the loading was successful.
        """

        assert isinstance(
            document, (dict, list, tuple)
        ), f"`document` must be of dict, list or tuple, not {type(document)}"

        self.beginResetModel()
        self._rootItem = _JsonTreeItem.load(document)
        self._rootItem.valueType = type(document)
        self.endResetModel()

        return True

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role=Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Override from QAbstractItemModel.

        Get header data for columns (orientation = Horizontal).

        Args:
            section (int): The section of the header.
            orientation (Qt.Orientation): The orientation of the header.
            role (Qt.ItemDataRole): The role of the data.

        Returns:
            Any: The header data.
        """

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

        Return data from a JSON item according to the index and role.

        Args:
            index (QModelIndex): The index of the item.
            role (Qt.ItemDataRole): The role of the data.

        Returns:
            Any: The JSON data requested.
        """

        if not index.isValid():
            return None

        item: _JsonTreeItem = index.internalPointer()

        if role == Qt.ItemDataRole.DisplayRole:
            match index.column():
                case 0:
                    return item.key
                case 1:
                    return item.value
            return None

        if role == Qt.ItemDataRole.EditRole:
            if index.column() == 1:
                return item.value

        return None

    def setData(
        self,
        index: QModelIndex,
        value: Any,
        role: Qt.ItemDataRole,
    ) -> bool:
        """Override from QAbstractItemModel.

        Set JSON item according to index and role.

        Args:
            index (QModelIndex): The index of the item.
            value (Any): The value to set.
            role (Qt.ItemDataRole): The role of the data.

        Returns:
            bool: True if the setting was successful, False otherwise.
        """

        if role == Qt.ItemDataRole.EditRole:
            if index.column() == 1:
                item: _JsonTreeItem = index.internalPointer()
                item.value = str(value)

                self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                return True

        return False

    def index(
        self,
        row: int,
        column: int,
        parent=QModelIndex(),
    ) -> QModelIndex:
        """Override from QAbstractItemModel.

        Return the index according to row, column, and parent.

        Args:
            row (int): The row of the index.
            column (int): The column of the index.
            parent (QModelIndex, optional): The parent index. Defaults to
                QModelIndex().

        Returns:
            QModelIndex: The created index.
        """

        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index=QModelIndex()) -> QModelIndex:
        """Override from QAbstractItemModel.

        Return the parent index of the given index.

        Args:
            index (QModelIndex): The child index.

        Returns:
            QModelIndex: The parent index.
        """

        if not index.isValid():
            return QModelIndex()

        childItem: _JsonTreeItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self._rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Override from QAbstractItemModel."""

        flags = super().flags(index)

        # Identifier (keys) are not editable, values are editable.
        if index.column() == 1:
            return Qt.ItemFlag.ItemIsEditable | flags
        else:
            return flags

    def match(
        self,
        start: QModelIndex | QPersistentModelIndex,
        role: int,
        value: Any,
        hits: Optional[int] = 1,
        flags: Optional[Qt.MatchFlag] = (
            Qt.MatchFlag.MatchStartsWith | Qt.MatchFlag.MatchWrap
        ),
    ) -> list[QModelIndex | QPersistentModelIndex]:
        """Override from QAbstractItemModel.

        This implementation is heavily influenced by the original
        implementation, which can be found at: https://github.com/qt/qtbase

        Searches the tree row-wise (key and value, including child nodes).

        Args:
            start (Union[QModelIndex, QPersistentModelIndex]): The starting
                index.
            role (int): The role to match against.
            value (Any): The value to match.
            hits (int, optional): The number of hits to find. Defaults to 1.
            flags (Qt.MatchFlag, optional): The matching flags. Defaults to
                Qt.MatchFlag.MatchStartsWith | Qt.MatchFlag.MatchWrap.

        Returns:
            List[Union[QModelIndex, QPersistentModelIndex]]: The indexes of
                matching values.
        """

        result: list[QModelIndex] = []
        matchType = flags & Qt.MatchFlag.MatchTypeMask
        cs = (
            Qt.CaseSensitivity.CaseSensitive
            if (
                flags & Qt.MatchFlag.MatchCaseSensitive
                == Qt.MatchFlag.MatchCaseSensitive
            )
            else Qt.CaseSensitivity.CaseInsensitive
        )
        wrap = flags & Qt.MatchFlag.MatchWrap == Qt.MatchFlag.MatchWrap
        allHits = hits == -1

        # Regular expressions
        rx = QRegularExpression()
        if matchType == Qt.MatchFlag.MatchRegularExpression:
            if type(value) == QRegularExpression:
                rx = value
            else:
                rx.setPattern(str(value))
        elif matchType == Qt.MatchFlag.MatchWildcard:
            pattern = QRegularExpression.wildcardToRegularExpression(str(value))
            rx.setPattern(pattern)

        if cs == Qt.CaseSensitivity.CaseInsensitive:
            rx.setPatternOptions(QRegularExpression.PatternOption.CaseInsensitiveOption)

        # Index range
        fromIndex = self._indexVisitOrder.index(start)
        length = len(self._indexVisitOrder)
        toIndex = length + fromIndex if wrap else length

        # Iteration
        for index in (self._indexVisitOrder * 2)[fromIndex:toIndex]:
            if not index.isValid():
                continue

            v = self.data(index, role)
            if matchType == Qt.MatchFlag.MatchExactly:
                if value == v:
                    result.append(index)
            else:
                value: str = str(value)
                t: str = str(v)
                if cs == Qt.CaseSensitivity.CaseInsensitive:
                    value = value.lower()
                    t = t.lower()
                match matchType:
                    case (
                        Qt.MatchFlag.MatchRegularExpression | Qt.MatchFlag.MatchWildcard
                    ):
                        if rx.match(t).hasMatch():
                            result.append(index)
                    case Qt.MatchFlag.MatchStartsWith:
                        if t.startswith(value):
                            result.append(index)
                    case Qt.MatchFlag.MatchEndsWith:
                        if t.endswith(value):
                            result.append(index)
                    case Qt.MatchFlag.MatchFixedString:
                        if t == value:
                            result.append(index)
                    case Qt.MatchFlag.MatchContains | _:
                        if value in t:
                            result.append(index)

            # Check for hits
            if (not allHits) and len(result) >= hits:
                break

        return result

    def _nextIndex(self, current=QModelIndex()) -> QModelIndex:
        """Return the next index after the given index.

        Args:
            current (QModelIndex, optional): The current index. Defaults to
                QModelIndex().

        Returns:
            QModelIndex: The next index.
        """

        # If index is invalid return the root index for convenience.
        if not current.isValid():
            return self.index(0, 0)

        key_index = current.siblingAtColumn(0)
        # Search the tree row-wise (key, value).
        if current.column() < self.columnCount(key_index) - 1:
            return current.siblingAtColumn(current.column() + 1)

        current = key_index

        # Check if the current item has childs. If the item has childs, return
        # the index of the first child.
        if self.hasChildren(current):
            current_item: _JsonTreeItem = current.internalPointer()
            child_item = current_item.child(0)
            return self.createIndex(0, 0, child_item)

        # Check if there are items on the same level in the tree
        while not current == QModelIndex():
            if current.row() < self.rowCount(current.parent()) - 1:
                return current.sibling(current.row() + 1, 0)

            current = current.parent()

        # Return an invalid index to mark the end of the list
        return QModelIndex()

    def to_dict(self, item: Optional[_JsonTreeItem] = None) -> Any:
        """Converts a _JsonTreeItem and its children to a JSON-compatible data
        structure.

        Args:
            item (_JsonTreeItem): The _JsonTreeItem to convert. If not provided,
                the root item is used.

        Returns:
            dict or list or Any: The converted JSON data structure.

        Notes:
            This method recursively converts the _JsonTreeItem and its children
                to a JSON-compatible data structure.
            The resulting structure can be a dictionary, a list, or a simple
                value, depending on the item's value_type.

        Example Usage:
            json_data = model.to_json()
        """

        if item is None:
            item = self._rootItem

        nchild = item.childCount()

        if item.valueType is dict:
            document = {}
            for i in range(nchild):
                ch = item.child(i)
                document[ch.key] = self.to_dict(ch)
            return document

        elif item.valueType == list:
            document = []
            for i in range(nchild):
                ch = item.child(i)
                document.append(self.to_dict(ch))
            return document

        else:
            return item.value

    def rowCount(self, parent=QModelIndex()) -> int:
        """Override from QAbstractItemModel.

        Return the number of rows under the parent index.

        Args:
            parent (Optional[QModelIndex]): The parent index. Defaults to
                QModelIndex().

        Returns:
            int: The number of rows.
        """

        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_item = self._rootItem
        else:
            parent_item = parent.internalPointer()

        return parent_item.childCount()

    def columnCount(self, parent=QModelIndex()) -> int:
        """Override from QAbstractItemModel.

        Return the number of columns.

        Args:
            parent (Optional[QModelIndex]): The parent index. Defaults to
                QModelIndex().

        Returns:
            int: The number of columns.
        """

        return 2
