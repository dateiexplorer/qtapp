from typing import Optional

import qtawesome as qta
from PySide6.QtCore import (
    QAbstractAnimation,
    QParallelAnimationGroup,
    QPropertyAnimation,
    Qt,
)
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLayout,
    QProxyStyle,
    QScrollArea,
    QSizePolicy,
    QStyle,
    QStyleOption,
    QToolButton,
    QWidget,
)


class _ToolButtonProxyStyle(QProxyStyle):
    """A custom proxy style for tool buttons.

    Based on: https://stackoverflow.com/a/68141638

    This style is used to modify the pixel metrics of tool buttons.
    """

    def pixelMetric(
        self,
        metric: QStyle.PixelMetric,
        option: Optional[QStyleOption] = None,
        widget: Optional[QWidget] = None,
    ) -> None:
        """Get the pixel metric for the given metric.

        Args:
            metric (QStyle.PixelMetric): The pixel metric to retrieve.
            option (Optional[QStyleOption]): The style option.
                Defaults to None.
            widget (Optional[QWidget]): The widget. Defaults to None.

        Returns:
            int: The pixel metric value.
        """

        ret = 0
        if (
            metric == QStyle.PixelMetric.PM_ButtonShiftHorizontal
            or metric == QStyle.PixelMetric.PM_ButtonShiftVertical
        ):
            ret = 0
        else:
            ret = super().pixelMetric(metric, option, widget)
        return ret


class Section(QWidget):
    """A collapsible section widget with a toggle button.

    This widget displays a toggle button and a content area that can be
    collapsed or expanded. The toggle button controls the visibility of the
    content area, and the content area can hold any layout.

    Based on: https://stackoverflow.com/a/47469795

    Args:
        title (Optional[str]): The title of the section. Defaults to an empty string.
        animation_duration (Optional[int]): The duration of the animation in
            milliseconds (default = 100).
        parent (Optional[QWidget]): The parent widget (default = None).
    """

    def __init__(
        self,
        title: Optional[str] = "",
        animationDuration: Optional[int] = 100,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the Section widget.

        Args:
            title (str): The title of the section (default = "").
            animation_duration (int): The duration of the animation in
                milliseconds (default = 100).
            parent (QWidget): The parent widget (default = None).
        """

        super().__init__(parent)
        self._animDuration = animationDuration

        self._toggleBtn = QToolButton()
        self._toggleBtn.setStyleSheet("QToolButton { border: none; }")
        self._toggleBtn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._toggleBtn.setStyle(_ToolButtonProxyStyle())
        self._toggleBtn.setIcon(qta.icon("ph.caret-right", color="grey"))
        self._toggleBtn.setText(str(title))
        self._toggleBtn.setCheckable(True)
        self._toggleBtn.setChecked(False)

        self._headerLine = QFrame()
        self._headerLine.setStyleSheet("QFrame { color: lightgray; }")
        self._headerLine.setFrameShape(QFrame.Shape.HLine)
        self._headerLine.setFrameShadow(QFrame.Shadow.Plain)
        self._headerLine.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Maximum,
        )

        self._contentArea = QScrollArea()
        self._contentArea.setStyleSheet("QScrollArea { border: none; }")
        self._contentArea.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self._contentArea.setMaximumHeight(0)
        self._contentArea.setMinimumHeight(0)

        self._toggleAnim = QParallelAnimationGroup()
        self._toggleAnim.addAnimation(QPropertyAnimation(self, b"minimumHeight"))
        self._toggleAnim.addAnimation(QPropertyAnimation(self, b"maximumHeight"))
        self._toggleAnim.addAnimation(
            QPropertyAnimation(self._contentArea, b"maximumHeight")
        )

        self._mainLayout = QGridLayout()
        self._mainLayout.setVerticalSpacing(0)
        self._mainLayout.setContentsMargins(0, 0, 0, 0)
        self._mainLayout.addWidget(
            self._toggleBtn,
            0,
            0,
            1,
            1,
            Qt.AlignmentFlag.AlignLeft,
        )
        self._mainLayout.addWidget(self._headerLine, 0, 2, 1, 1)
        self._mainLayout.addWidget(self._contentArea, 1, 0, 1, 3)
        self.setLayout(self._mainLayout)

        self._toggleBtn.toggled.connect(self.toggle)

    def setTitle(self, title: str) -> None:
        """Set the title of the section.

        Args:
            title (str): The title to set.
        """

        self._toggleBtn.setText(title)

    def setContentLayout(self, layout: QLayout) -> None:
        """
        Set the content layout of the section.

        Args:
            layout (QLayout): The layout to set as the content.
        """

        self._contentArea.setLayout(layout)
        self._contentArea.destroy()
        collapsedHeight = self.sizeHint().height() - self._contentArea.maximumHeight()
        contentHeight = layout.sizeHint().height()

        for i in range(self._toggleAnim.animationCount() - 1):
            expandAnim: QPropertyAnimation = self._toggleAnim.animationAt(i)
            expandAnim.setDuration(self._animDuration)
            expandAnim.setStartValue(collapsedHeight)
            expandAnim.setEndValue(collapsedHeight + contentHeight)

        contentAnim: QPropertyAnimation = self._toggleAnim.animationAt(
            self._toggleAnim.animationCount() - 1
        )
        contentAnim.setDuration(self._animDuration)
        contentAnim.setStartValue(0)
        contentAnim.setEndValue(contentHeight)

    def toggle(self, collapsed: bool) -> None:
        """Toggle the visibility of the content area.

        Args:
            collapsed (bool): True if the content area should be collapsed,
                False if it should be expanded.
        """

        arrowType = "ph.caret-down" if collapsed else "ph.caret-right"
        direction = (
            QAbstractAnimation.Direction.Forward
            if collapsed
            else QAbstractAnimation.Direction.Backward
        )

        self._toggleBtn.setIcon(qta.icon(arrowType, color="grey"))
        self._toggleAnim.setDirection(direction)

        self._toggleAnim.start()
