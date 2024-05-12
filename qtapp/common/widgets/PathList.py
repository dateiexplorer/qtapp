from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from qtapp.common.models import PathListModel
from qtapp.common.widgets.TreeView import TreeView


class _PathListView(TreeView):
    """A TreeView used by the PathList widget to show the PathListModel.

    Args:
        model (PathListModel): The PathListModel to show.
        parent (Optional[QWidget]): The parent widget (default = None).
    """

    def __init__(self, model: PathListModel, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setModel(model)
        self.setSelectionMode(TreeView.SelectionMode.ExtendedSelection)
        self.setEditTriggers(
            TreeView.EditTrigger.DoubleClicked | TreeView.EditTrigger.EditKeyPressed
        )

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

        self.setHeaderHidden(True)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Override from TreeView."""

        super().dragEnterEvent(event)
        event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        """Override from TreeView."""

        super().dragMoveEvent(event)
        event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        """Override form TreeView."""

        super().dropEvent(event)
        event.acceptProposedAction()


class PathList(QWidget):
    """A widget for managing a list of file paths.

    This widget provides functionality for adding, removing, editing and
    displaying file paths.

    Signals:
        dataChanged: Emitted when the underlying model data is changed.

    Args:
        model (PathListModel): The model for managing file paths. If no model
            is provided a new model will be created.
        parent (QWidget): The parent widget (default = None).
    """

    dataChanged = Signal(list)

    def __init__(
        self,
        model: Optional[PathListModel] = None,
        parent: Optional[QWidget] = None,
        dialog: Optional[QFileDialog] = None,
        filter: Optional[str] = "dir",
    ) -> None:
        super().__init__(parent)
        self._model = model if model is not None else PathListModel()
        self._dialog = dialog
        self._filter = filter

        self.dataChanged.connect(self._onDataChanged)

        # Every time the model data changes, emit the dataChanged Signal of
        # the widget.
        self.model.dataChanged.connect(lambda: self.dataChanged.emit(self.model.items))

        self.setupUi()

        # Set initial state.
        self.setPaths([])

    @property
    def model(self) -> PathListModel:
        """Get the model.

        Returns:
            PathListModel: The model managing the list of file paths.
        """

        return self._model

    @property
    def view(self) -> _PathListView:
        return self._pathListView

    def setupUi(self) -> None:
        self._pathListView = _PathListView(self.model)
        self._pathListView.selectionModel().selectionChanged.connect(
            self._onSelectionChanged
        )

        self._addBtn = QPushButton("Add")
        self._addBtn.clicked.connect(self.addPath)

        self._deleteBtn = QPushButton("Delete")
        self._deleteBtn.clicked.connect(self.removePaths)

        buttonLayout = QVBoxLayout()
        buttonLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        buttonLayout.addWidget(self._addBtn)
        buttonLayout.addWidget(self._deleteBtn)

        layout = QHBoxLayout()
        layout.addWidget(self._pathListView)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)
        self.layout().setContentsMargins(0, 0, 0, 0)

    @Slot()
    def _onDataChanged(self) -> None:
        """Slot triggered when the dataChanged Signal is emitted."""

        self._onSelectionChanged()

    @Slot()
    def _onSelectionChanged(self) -> None:
        """Slot triggered when the selection in the _PathListView changes."""

        self._deleteBtn.setEnabled(len(self._pathListView.selectedIndexes()) > 0)

    @Slot()
    def setPaths(self, paths: list[Path]) -> None:
        """Set the paths.

        Args:
            paths (list[Path]): The list of file paths to set.
        """

        self.model.setItems(paths)

    @Slot()
    def addPath(self) -> None:
        """Open a file dialog to add a new Path."""

        if self._filter == "dir":
            paths = [self._dialog.getExistingDirectory()]
        else:
            paths, _ = self._dialog.getOpenFileNames(filter=self._filter)

        for path in paths:
            if path:
                self.model.appendItem(Path(path))

    @Slot()
    def removePaths(self) -> None:
        """Remove selected paths."""

        indexes = self._pathListView.selectionModel().selectedRows()
        items = [self.model.item(index) for index in indexes]
        for item in items:
            self.model.removeItem(item)

    def paths(self) -> list[Path]:
        """Get the list of Paths.

        Returns:
            list[Path]: The list of file paths.
        """

        return self.model.items
