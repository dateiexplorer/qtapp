from typing import Any, Optional, Self

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, Qt
from PySide6.QtGui import QStandardItem


class _TreeItem:
    """Represents an item in a tree structure."""

    def __init__(self, parent: Optional[Self] = None) -> None:
        self._itemData: list[QStandardItem] = (
            [QStandardItem() for i in range(parent.columnCount())]
            if parent is not None
            else []
        )

        self._parentItem = parent
        self._childItems: list[Self] = []

    def child(self, row: int) -> Self:
        """Get the child item at the specified row.

        Args:
            row (int): The row index.

        Returns:
            TreeItem: The child item at the specified row.
        """

        if row < 0 or row >= len(self._childItems):
            return None
        return self._childItems[row]

    def lastChild(self) -> Self:
        """Get the last child item.

        Returns:
            TreeItem: The last child item.
        """

        return self._childItems[-1] if self._childItems else None

    def data(
        self,
        column: int,
        role: Qt.ItemDataRole,
    ) -> Any:
        """Get the data for the specified column and role.

        Args:
            column (int): The column index.
            role (Qt.ItemDataRole): The role of the data.

        Returns:
            Any: The data for the specified column and role.
        """

        if column < 0 or column >= len(self._itemData):
            return None

        return self._itemData[column].data(role)

    def setData(
        self,
        column: int,
        value,
        role: Qt.ItemDataRole,
    ) -> bool:
        """Set the data for the specified column and role.

        Args:
            column (int): The column index.
            value (Any): The new value for the data.
            role (Qt.ItemDataRole): The role of the data.

        Returns:
            bool: True if the data was set successfully, False otherwise.
        """

        if column < 0 or column >= len(self._itemData):
            return False

        self._itemData[column].setData(value, role)
        return True

    def appendChild(self, child: Self) -> None:
        """Append a child item.

        Args:
            child (TreeItem): The child item to append.
        """

        self._childItems.append(child)

    def insertChildren(self, position: int, count: int) -> bool:
        """Insert an amount of child items at a specific position.

        Args:
            position (int): The position to insert.
            count (int): The number of items to insert.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """

        if position < 0 or position > len(self._childItems):
            return False

        for row in range(count):
            item = _TreeItem(self)
            self._childItems.insert(position, item)

        return True

    def removeChildren(self, position: int, count: int) -> bool:
        """Remove multiple child items starting from the specified position.

        Args:
            position (int): The starting position to remove child items.
            count (int): The number of child items to remove.

        Returns:
            bool: True if the child items were removed successfully, False
                otherwise.
        """

        if position < 0 or position + count > len(self._childItems):
            return False

        for row in range(count):
            self._childItems.pop(position)

        return True

    def childCount(self) -> int:
        """Get the number of child items.

        Returns:
            int: The number of child items.
        """

        return len(self._childItems)

    def appendColumn(self, item: Optional[QStandardItem] = None) -> None:
        """Append a column to this item's data.

        Args:
            item (QStandardItem, optional): The item to append as a column.
                Defaults to None.
        """

        self._itemData.append(item if item is not None else QStandardItem())

    def insertColumns(self, position: int, columns: int) -> bool:
        """Insert multiple child items at the specified position.

        Args:
            position (int): The position to insert the child items.
            count (int): The number of child items to insert.

        Returns:
            bool: True if the child items were inserted successfully, False
                otherwise.
        """

        if position < 0 or position > len(self._itemData):
            return False

        for _ in range(columns):
            self._itemData.insert(position, QStandardItem())

        for child in self._childItems:
            child.insertColumns(position, columns)

        return True

    def removeColumns(self, position: int, columns: int) -> bool:
        """Remove multiple columns from this item's data.

        Args:
            position (int): The starting position to remove columns.
            columns (int): The number of columns to remove.

        Returns:
            bool: True if the columns were removed successfully, False
                otherwise.
        """

        if position < 0 or position + columns > len(self._itemData):
            return False

        for column in range(columns):
            self._itemData.pop(position)

        for child in self._childItems:
            child.removeColumns(position, columns)

        return True

    def columnCount(self) -> int:
        """Get the number of columns in this item.

        Returns:
            int: The number of columns in this item.
        """

        return len(self._itemData)

    def parent(self) -> Self:
        """Get the parent item.

        Returns:
            TreeItem: The parent item.
        """

        return self._parentItem

    def row(self) -> int:
        """Get the row index of this item.

        Returns:
            int: The row index of this item.
        """

        if self._parentItem:
            return self._parentItem._childItems.index(self)
        return 0


class TreeModel(QAbstractItemModel):
    """A model for tree-based item views."""

    def __init__(self, headers: list[str], parent: Optional[QObject] = None) -> None:
        """Initialize a TreeModel object.

        Args:
            headers (list[str]): The headers for the model's columns.
            parent (Optional[QObject]): The parent object. (default = None)
        """

        super().__init__(parent)

        self._rootItem = _TreeItem()
        for header in headers:
            self._rootItem.appendColumn(QStandardItem(header))

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role=Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Override from QAbstractItemModel.

        Get header data for the specified section, orientation, and role.

        Args:
            section (int): The section index.
            orientation (Qt.Orientation): The orientation of the header.
            role (Qt.ItemDataRole, optional): The role of the data. Defaults to
                Qt.ItemDataRole.DisplayRole.

        Returns:
            Any: The header data for the specified section, orientation, and
                role.
        """

        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            return self._rootItem.data(section, role)

        return None

    def setHeaderData(
        self,
        section: int,
        orientation: Qt.Orientation,
        value: Any,
        role=Qt.ItemDataRole.DisplayRole,
    ) -> bool:
        """Override from QAbstractItemModel.

        Sets the header data for a specific section in the model.

        Args:
            section (int): The section (column index) for which to set the
                header data.
            orientation (Qt.Orientation): The orientation of the header,
                either horizontal or vertical.
            value: The new value to set as the header data.
            role (Qt.ItemDataRole, optional): The role of the data. Specifies
                the purpose or type of the data.
                Defaults to Qt.ItemDataRole.DisplayRole.

        Returns:
            bool: True if the header data was set successfully, False
                otherwise.
        """
        if role != Qt.ItemDataRole.EditRole or orientation != Qt.Orientation.Horizontal:
            return False

        result: bool = self._rootItem.setData(section, value, role)

        if result:
            self.headerDataChanged.emit(orientation, section, section)

        return result

    def data(
        self,
        index: QModelIndex,
        role=Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Override from QAbstractItemModel.

        Get the data for the specified index and role.

        Args:
            index (QModelIndex): The index of the item.
            role (Qt.ItemDataRole, optional): The role of the data. Defaults to
                None.

        Returns:
            Any: The data for the specified index and role.
        """

        if not index.isValid():
            return None

        item: _TreeItem = self.item(index)
        return item.data(index.column(), role)

    def setData(
        self,
        index: QModelIndex,
        value: Any,
        role: Qt.ItemDataRole,
    ) -> bool:
        """Override from QAbstractItemmodel.

        Set the data for the specified index and role.

        Args:
            index (QModelIndex): The index of the item.
            value (Any): The new value for the data.
            role (Qt.ItemDataRole, optional): The role of the data. Defaults to
                Qt.ItemDataRole.EditRole.

        Returns:
            bool: True if the data was set successfully, False otherwise.
        """

        item: _TreeItem = self.item(index)
        result: bool = item.setData(index.column(), value, role)

        if result:
            self.dataChanged.emit(
                index, index, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole]
            )

        return result

    def index(
        self,
        row: int,
        column: int,
        parent=QModelIndex(),
    ) -> QModelIndex:
        """Override from QAbstractItemModel.

        Create a model index for the specified row, column, and parent.

        Args:
            row (int): The row index.
            column (int): The column index.
            parent (QModelIndex, optional): The parent index. Defaults to
                QModelIndex().

        Returns:
            QModelIndex: The model index for the specified row, column, and
                parent.
        """

        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parent_item: _TreeItem = self.item(parent)
        if not parent_item:
            return QModelIndex()

        childItem: _TreeItem = parent_item.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        return QModelIndex()

    def parent(self, index=QModelIndex()) -> QModelIndex:
        """Override from QAbstractItemModel.

        Get the parent index of the specified index.

        Args:
            index (QModelIndex, optional): The index of the item. Defaults to
                QModelIndex().

        Returns:
            QModelIndex: The parent index of the specified index.
        """

        if not index.isValid():
            return QModelIndex()

        childItem: _TreeItem = self.item(index)
        if childItem:
            parentItem: _TreeItem = childItem.parent()
        else:
            parentItem = None

        if parentItem == self._rootItem or not parentItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Override from QAbstractItemModel.

        Get the flags for the specified index.

        Args:
            index (QModelIndex): The index of the item.

        Returns:
            Qt.ItemFlag: The flags for the specified index.
        """

        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return Qt.ItemFlag.ItemIsEditable | QAbstractItemModel.flags(self, index)

    def insertColumns(
        self,
        position: int,
        columns: int,
        parent=QModelIndex(),
    ) -> bool:
        """Override from QAbstractItemModel.

        Insert multiple columns into the model.

        Args:
            position (int): The position to insert the columns.
            columns (int): The number of columns to insert.
            parent (QModelIndex, optional): The parent index. Defaults to
                QModelIndex().

        Returns:
            bool: True if the columns were inserted successfully, False
                otherwise.
        """

        self.beginInsertColumns(parent, position, position + columns - 1)
        success: bool = self._rootItem.insertColumns(position, columns)
        self.endInsertColumns()

        return success

    def removeColumns(
        self,
        position: int,
        columns: int,
        parent=QModelIndex(),
    ) -> bool:
        """Override from QAbstractItemModel.

        Remove multiple columns from the model.

        Args:
            position (int): The starting position to remove columns.
            columns (int): The number of columns to remove.
            parent (QModelIndex, optional): The parent index. Defaults to
                QModelIndex().

        Returns:
            bool: True if the columns were removed successfully, False
                otherwise.
        """

        self.beginRemoveColumns(parent, position, position + columns - 1)
        success: bool = self._rootItem.removeColumns(position, columns)
        self.endRemoveColumns()

        if self._rootItem.columnCount() == 0:
            self.removeRows(0, self.rowCount())

        return success

    def insertRows(
        self,
        position: int,
        rows: int,
        parent=QModelIndex(),
    ) -> bool:
        """Override form QAbstractItemModel.

        Insert multiple rows into the model.

        Args:
            position (int): The position to insert the rows.
            rows (int): The number of rows to insert.
            parent (QModelIndex, optional): The parent index. Defaults to
                QModelIndex().

        Returns:
            bool: True if the rows were inserted successfully, False otherwise.
        """

        parentItem: _TreeItem = self.item(parent)
        if not parentItem:
            return False

        self.beginInsertRows(parent, position, position + rows - 1)
        columnCount = self._rootItem.columnCount()
        success: bool = parentItem.insertChildren(position, rows, columnCount)
        self.endInsertRows()

        return success

    def removeRows(
        self,
        position: int,
        rows: int,
        parent=QModelIndex(),
    ) -> bool:
        """Override from QAbstractItemModel.

        Remove multiple rows from the model.

        Args:
            position (int): The starting position to remove rows.
            rows (int): The number of rows to remove.
            parent (QModelIndex, optional): The parent index. Defaults to
                QModelIndex().

        Returns:
            bool: True if the rows were removed successfully, False otherwise.
        """

        parentItem: _TreeItem = self.item(parent)
        if not parentItem:
            return False

        self.beginRemoveRows(parent, position, position + rows - 1)
        success: bool = parentItem.removeChildren(position, rows)
        self.endRemoveRows()

        return success

    def appendItem(self, item: _TreeItem) -> None:
        """Append a child item to the parent item.

        Args:
            item (TreeItem): The child item to append.
        """

        item.parent().appendChild(item)

    def item(self, index=QModelIndex()) -> _TreeItem:
        """Get the TreeItem object associated with the specified index.

        Args:
            index (QModelIndex, optional): The index of the item. Defaults to
                QModelIndex().

        Returns:
            TreeItem: The TreeItem object associated with the index.
        """

        if index.isValid():
            item: _TreeItem = index.internalPointer()
            if item:
                return item

        return self._rootItem

    def root(self) -> _TreeItem:
        """Get the root item of the model.

        Returns:
            TreeItem: The root item.
        """

        return self._rootItem

    def columnCount(self, parent=QModelIndex()) -> int:
        """Override from QAbstractItemModel.

        Get the number of columns in the model.

        Args:
            parent (QModelIndex, optional): The parent index. Defaults to
                QModelIndex().

        Returns:
            int: The number of columns in the model.
        """

        return self._rootItem.columnCount()

    def rowCount(self, parent=QModelIndex()) -> int:
        """Override from QAbstractItemModel.

        Get the number of rows in the model.

        Args:
            parent (QModelIndex, optional): The parent index. Defaults to
                QModelIndex().

        Returns:
            int: The number of rows in the model.
        """

        if parent.isValid() and parent.column() > 0:
            return 0

        parentItem: _TreeItem = self.item(parent)
        if not parentItem:
            return 0
        return parentItem.childCount()
