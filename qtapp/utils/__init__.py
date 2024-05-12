from pathlib import Path
from PySide6.QtCore import QFile, QTextStream

def formatBytes(num: float, suffix: str = "B") -> str:
    """Format a number of bytes into readable formats.

    Args:
        num (float): The number of bytes.
        suffix (str, optional): The suffix to append to the formatted result.
        Defaults to "B".

    Returns:
        str: The formatted string representing the number of bytes in a
        readable format.
            Examples: "1.2 KiB", "3.5 MiB", "500 B", etc.
    """

    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Yi{suffix}"


def readFileContent(path: Path) -> str:
    file = QFile(path)
    file.open(QFile.OpenModeFlag.ReadOnly)
    stream = QTextStream(file)
    content = stream.readAll()
    file.close()
    return content
