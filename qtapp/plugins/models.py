from typing import Any

from PySide6.QtCore import QModelIndex, Qt

from qtapp.common.models import ItemTableModel
from qtapp.plugins.schemas import Module


class ModuleListModel(ItemTableModel[Module]):
    def __init__(self):
        super().__init__(["Extension", "Description"])

    def data(
        self,
        index: QModelIndex,
        role=Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Override from ItemTableModel."""

        if not index.isValid():
            return None

        module: Module = self.items[index.row()]
        if role == Qt.ItemDataRole.CheckStateRole:
            if index.column() == 0:
                return (
                    Qt.CheckState.Checked if module.enabled else Qt.CheckState.Unchecked
                )

        if role == Qt.ItemDataRole.DisplayRole:
            match index.column():
                case 0:
                    return module.displayName
                case 1:
                    return module.description
            return None

        return super().data(index, role)

    def setData(
        self,
        index: QModelIndex,
        value: Any,
        role=Qt.ItemDataRole.EditRole,
    ) -> bool:
        """Override from ItemTableModel."""

        if index.column() == 0:
            if role == Qt.ItemDataRole.CheckStateRole:
                module = self.items[index.row()]
                module.enabled = bool(value)
                self.dataChanged.emit(index, index)
                return True

        return super().setData(index, value, role)

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Override from ItemTableModel."""

        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        if index.column() == 0:
            flags |= Qt.ItemFlag.ItemIsUserCheckable

        return flags
