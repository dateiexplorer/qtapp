import sys
import traceback

from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class Worker(QRunnable):
    """An easy way to provide asynchronous background tasks with standard and
    most common Signals.

    See https://www.pythonguis.com/tutorials/multithreading-pyside6-applications-qthreadpool/.
    """

    def __init__(self, fn, *args, **kwargs) -> None:
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            excType, value = sys.exc_info()[:2]
            self.signals.error.emit((excType, value, traceback.format_exc()))
        else:
            # Return the result of the processing
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
