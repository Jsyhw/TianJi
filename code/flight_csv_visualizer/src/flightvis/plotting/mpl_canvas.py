from __future__ import annotations

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, width: float = 5, height: float = 4, dpi: int = 100, projection: str | None = None):
        self.figure = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        if projection:
            self.axes = self.figure.add_subplot(111, projection=projection)
        else:
            self.axes = self.figure.add_subplot(111)
        super().__init__(self.figure)

    def clear(self):
        self.figure.clear()
        self.axes = self.figure.add_subplot(111)
        return self.axes

    def clear_3d(self):
        self.figure.clear()
        self.axes = self.figure.add_subplot(111, projection="3d")
        return self.axes
