from pathlib import Path
from typing import Any, Optional, Sequence

from PySide6.QtCore import QMimeData, QModelIndex, QObject, Qt, QUrl

from qtapp.common.models import ItemMimeData, ItemTableModel


class PathListModel(ItemTableModel[Path]):
    """Model for managing a list of Paths.

    Inherits from ItemTableModel.
    """

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(["Path"], parent)

    def data(
        self,
        index: QModelIndex,
        role=Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Override from ItemTableModel."""

        if not index.isValid():
            return None

        item: Path = self.items[index.row()]
        if role in [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole]:
            match index.column():
                case 0:
                    return str(item.absolute())
            return None

        return super().data(index, role)

    def setData(
        self,
        index: QModelIndex,
        value: Any,
        role: Qt.ItemDataRole,
    ) -> bool:
        """Override from ItemDataModel."""

        if not index.isValid():
            return False

        if role == Qt.ItemDataRole.EditRole:
            path = Path(value)
            if not path.exists():
                return False

            self.items[index.row()] = path
            self.dataChanged.emit(index, index)
            return True

        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Override from ItemTableModel."""

        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return (
            super().flags(index)
            | Qt.ItemFlag.ItemIsEditable
            | Qt.ItemFlag.ItemIsDragEnabled
            | Qt.ItemFlag.ItemIsDropEnabled
        )

    def mimeData(self, indexes: Sequence[QModelIndex]) -> QMimeData:
        """Override from ItemTableModel."""

        items = [self.item(index) for index in indexes]
        mimedata = ItemMimeData(items)
        mimedata.setText(
            "\n".join([str(index.data(ItemTableModel.ItemRole) for index in indexes)])
        )
        mimedata.setParent(self)
        return mimedata

    def dropMimeData(
        self,
        data: QMimeData,
        action: Qt.DropAction,
        row: int,
        column: int,
        parent: QModelIndex,
    ) -> bool:
        """Override from ItemTableModel."""

        if action == Qt.DropAction.IgnoreAction:
            return True

        dest_row = parent.row() if parent.row() > -1 else self.rowCount()

        # Drop from internal.
        if isinstance(data, ItemMimeData):
            data: ItemMimeData = data
            for path in data._items:
                removed = self.removeItem(path)
                if removed:
                    self.insertItem(dest_row, path)
                    dest_row += 1

            return True
        elif not data.hasText():
            return False
        # Drop from external.
        else:
            paths = data.text().split("\n")
            for path in paths:
                if path:
                    self.insertItem(dest_row, Path(QUrl.toLocalFile(QUrl(path))))
                    dest_row += 1

            return True
