from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from qtapp.app import BaseApplication

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QLabel,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class AboutDialog(QDialog):
    def __init__(
        self,
        app: "BaseApplication",
        parent: Optional[QWidget] = None,
        **kwargs,
    ) -> None:
        super().__init__(parent)

        applicationVersion = kwargs.get("applicationVersion")
        applicationDescription = kwargs.get("applicationDescription")
        licenseFile: Path = Path(kwargs.get("licenseFile"))

        appVersionLabel = QLabel(f"Version {applicationVersion}")
        appDescriptionLabel = QLabel(applicationDescription)

        # Set a monospaced font. Use the StyleHint, because on Windows,
        # 'Monospace' font is not available.
        font = QFont("Monospace")
        font.setStyleHint(QFont.StyleHint.Monospace)

        license = QTextEdit()
        license.setReadOnly(True)
        license.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        license.setFont(font)
        licenseLayout = QVBoxLayout()
        licenseLayout.addWidget(license)
        licenseWidget = QGroupBox("License")
        licenseWidget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        licenseWidget.setLayout(licenseLayout)

        try:
            with open(licenseFile, "r", encoding="utf-8") as f:
                license.setText(f.read())
        except Exception as err:
            QMessageBox.critical(
                self, "LICENSE", f"Error while reading LICENSE file: {str(err)}"
            )

        # Add the close button
        actionBtns = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        closeBtn = actionBtns.button(QDialogButtonBox.StandardButton.Close)
        closeBtn.clicked.connect(self.close)

        layout = QVBoxLayout(self)
        layout.addWidget(appVersionLabel)
        layout.addWidget(appDescriptionLabel)
        layout.addWidget(licenseWidget)
        layout.addWidget(actionBtns)
        self.setLayout(layout)

        self.setWindowTitle(f"About {app.applicationName}")
        self.setFixedSize(700, 400)
