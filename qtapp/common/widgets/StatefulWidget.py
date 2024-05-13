from typing import Generic, Optional, TypeVar

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QMainWindow, QWidget

T = TypeVar("T")


class StatefulWidget(QWidget, Generic[T]):
    """A generic stateful widget that emits a signal when the state changes.

    Args:
        init_state (T): The initial state of the widget.
        parent (Optional[QWidget]): The parent widget. Defaults to None.
        flags (Optional[Qt.WindowType]): The window flags for the widget.
            Defaults to Qt.WindowType.Widget.

    Signals:
        stateChanged: This signal is emitted when the state of the widget
            changes. It provides the current state and the previous state as
            arguments to any connected slots.

    Properties:
        state (T): The current state of the widget.

    Slots:
        onStateChanged(): This slot is called when the state_changed signal
            is emitted. It can be overridden in subclasses to perform custom
            actions when the state changes.

    Description:
        StatefulWidget is a generic class that serves as a base for creating
        stateful widgets. It inherits from QMainWindow and Generic[T] to allow
        specifying the type of the state.

        The widget emits a state_changed signal whenever the state is modified.
        This signal can be connected to other slots to perform actions based on
        state changes.

        The state property provides access to the current state of the widget.
        It can be used to get or set the state.

        The on_state_changed slot is called when the state_changed signal is
        emitted. By default, it does nothing. Subclasses can override this slot
        to implement custom behavior when the state changes.
    """

    stateChanged = Signal(object, object)

    def __init__(
        self,
        initState: T,
        parent: Optional[QWidget] = None,
        flags=Qt.WindowType.Widget,
    ) -> None:
        """Initializes the StatefulWidget.

        Args:
            initState (T): The initial state of the widget.
            parent (QWidget, optional): The parent widget. Defaults to None.
            flags (Qt.WindowType, optional): The window flags for the widget.
                Defaults to Qt.WindowType.Widget.
        """

        super().__init__(parent, flags)

        self._state = initState
        self.stateChanged.connect(self.onStateChanged)

    @property
    def state(self) -> T:
        """Get the current state of the widget.

        Returns:
            T: The current state.
        """

        return self._state

    @state.setter
    def state(self, state: T) -> None:
        """Set the state of the widget and emits the state_changed signal if
        the state has changed.

        Args:
            state (T): The new state.
        """

        previousState = self._state
        if previousState != state:
            self._state = state
            self.stateChanged.emit(state, previousState)

    @Slot()
    def onStateChanged(self, current: T, previous: T) -> None:
        """Slot called when the state_changed signal is emitted.

        Can be overwritten by subclasses.

        Args:
            current (T): The current state.
            previous (T): The previous state.
        """

        return None


class StatefulMainWindow(QMainWindow, Generic[T]):
    """A generic stateful widget that emits a signal when the state changes.

    Args:
        init_state (T): The initial state of the widget.
        parent (Optional[QWidget]): The parent widget. Defaults to None.
        flags (Optional[Qt.WindowType]): The window flags for the widget.
            Defaults to Qt.WindowType.Widget.

    Signals:
        stateChanged: This signal is emitted when the state of the widget
            changes. It provides the current state and the previous state as
            arguments to any connected slots.

    Properties:
        state (T): The current state of the widget.

    Slots:
        onStateChanged(): This slot is called when the state_changed signal
            is emitted. It can be overridden in subclasses to perform custom
            actions when the state changes.

    Description:
        StatefulWidget is a generic class that serves as a base for creating
        stateful widgets. It inherits from QMainWindow and Generic[T] to allow
        specifying the type of the state.

        The widget emits a state_changed signal whenever the state is modified.
        This signal can be connected to other slots to perform actions based on
        state changes.

        The state property provides access to the current state of the widget.
        It can be used to get or set the state.

        The on_state_changed slot is called when the state_changed signal is
        emitted. By default, it does nothing. Subclasses can override this slot
        to implement custom behavior when the state changes.
    """

    stateChanged = Signal(object, object)

    def __init__(
        self,
        initState: T,
        parent: Optional[QWidget] = None,
        flags=Qt.WindowType.Widget,
    ) -> None:
        """Initializes the StatefulWidget.

        Args:
            init_state (T): The initial state of the widget.
            parent (QWidget, optional): The parent widget. Defaults to None.
            flags (Qt.WindowType, optional): The window flags for the widget.
                Defaults to Qt.WindowType.Widget.
        """

        super().__init__(parent, flags)

        self._state = initState
        self.stateChanged.connect(self.onStateChanged)

    @property
    def state(self) -> T:
        """Get the current state of the widget.

        Returns:
            T: The current state.
        """

        return self._state

    @state.setter
    def state(self, state: T) -> None:
        """Set the state of the widget and emits the state_changed signal if
        the state has changed.

        Args:
            state (T): The new state.
        """

        previousState = self._state
        if previousState != state:
            self._state = state
            self.stateChanged.emit(state, previousState)

    @Slot()
    def onStateChanged(self, current: T, previous: T) -> None:
        """Slot called when the state_changed signal is emitted.

        Can be overwritten by subclasses.

        Args:
            current (T): The current state.
            previous (T): The previous state.
        """

        return None
