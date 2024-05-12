import logging

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger("qtapp")


class GuiLoggingFormatter(logging.Formatter):
    format = "%(asctime)s [%(levelname)s] %(message)s"

    _formats = {
        logging.DEBUG: f'<span style="color: black;">{format}</span>',
        logging.INFO: f'<span style="color: black;">{format}</span>',
        logging.WARNING: f'<span style="color: orange;">{format}</span>',
        logging.ERROR: f'<span style="color: red;">{format}</span>',
        logging.CRITICAL: f'<span style="color: red;">{format}</span>',
    }

    def format(self, record):
        logFmt = self._formats.get(record.levelno)
        formatter = logging.Formatter(logFmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


class GuiStream(QObject):
    textWritten = Signal(str)

    def flush(self):
        pass

    def write(self, text):
        self.textWritten.emit(str(text))
