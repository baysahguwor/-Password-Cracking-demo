"""
Charts module: Pure PySide6 QPainter-based attempt timeline (no matplotlib required).
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QPolygon, QPainterPath

BG_COLOR   = QColor("#060C12")
GRID_COLOR = QColor("#1E2A38")
LINE_COLOR = QColor("#00BFFF")
FILL_COLOR = QColor(0, 191, 255, 35)
TEXT_COLOR = QColor("#5A7A94")
TITLE_COLOR = QColor("#00BFFF")

PAD_L, PAD_R, PAD_T, PAD_B = 52, 12, 22, 28


class AttemptsChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._times: list[float] = []
        self._attempts: list[int] = []
        self.setMinimumHeight(150)
        self.setStyleSheet("background: #060C12; border: 1px solid #1E2A38; border-radius: 4px;")

    def reset(self):
        self._times.clear()
        self._attempts.clear()
        self.update()

    def update_data(self, elapsed: float, attempts: int):
        self._times.append(elapsed)
        self._attempts.append(attempts)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        W = self.width()
        H = self.height()

        # Background
        painter.fillRect(0, 0, W, H, BG_COLOR)

        # Title
        painter.setPen(QPen(TITLE_COLOR))
        painter.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        painter.drawText(QRect(0, 4, W, 16), Qt.AlignmentFlag.AlignHCenter, "Attempts Over Time")

        plot_x = PAD_L
        plot_y = PAD_T
        plot_w = W - PAD_L - PAD_R
        plot_h = H - PAD_T - PAD_B

        if plot_w <= 0 or plot_h <= 0:
            return

        # Grid lines (5 horizontal)
        painter.setPen(QPen(GRID_COLOR, 1, Qt.PenStyle.DotLine))
        max_val = max(self._attempts) if self._attempts else 1
        max_time = max(self._times) if self._times else 1

        grid_steps = 4
        for i in range(grid_steps + 1):
            gy = plot_y + plot_h - int((i / grid_steps) * plot_h)
            painter.drawLine(plot_x, gy, plot_x + plot_w, gy)
            # Y axis label
            painter.setPen(QPen(TEXT_COLOR))
            painter.setFont(QFont("Consolas", 6))
            val_label = _fmt_num(int((i / grid_steps) * max_val))
            painter.drawText(QRect(0, gy - 8, PAD_L - 4, 16), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, val_label)
            painter.setPen(QPen(GRID_COLOR, 1, Qt.PenStyle.DotLine))

        # Axes
        painter.setPen(QPen(GRID_COLOR, 1))
        painter.drawLine(plot_x, plot_y, plot_x, plot_y + plot_h)
        painter.drawLine(plot_x, plot_y + plot_h, plot_x + plot_w, plot_y + plot_h)

        # X axis labels
        painter.setPen(QPen(TEXT_COLOR))
        painter.setFont(QFont("Consolas", 6))
        for i in range(grid_steps + 1):
            gx = plot_x + int((i / grid_steps) * plot_w)
            t_label = f"{(i / grid_steps) * max_time:.1f}s"
            painter.drawText(QRect(gx - 20, plot_y + plot_h + 4, 40, 14), Qt.AlignmentFlag.AlignHCenter, t_label)

        if len(self._times) < 2:
            return

        # Build polyline points
        def _to_px(t, a):
            x = plot_x + int((t / max_time) * plot_w)
            y = plot_y + plot_h - int((a / max_val) * plot_h)
            return x, y

        # Fill area
        path = QPainterPath()
        x0, y0 = _to_px(self._times[0], self._attempts[0])
        path.moveTo(plot_x, plot_y + plot_h)
        path.lineTo(x0, y0)
        for t, a in zip(self._times[1:], self._attempts[1:]):
            xp, yp = _to_px(t, a)
            path.lineTo(xp, yp)
        path.lineTo(plot_x + int((self._times[-1] / max_time) * plot_w), plot_y + plot_h)
        path.closeSubpath()
        painter.fillPath(path, FILL_COLOR)

        # Line
        painter.setPen(QPen(LINE_COLOR, 2))
        prev_x, prev_y = _to_px(self._times[0], self._attempts[0])
        for t, a in zip(self._times[1:], self._attempts[1:]):
            cx, cy = _to_px(t, a)
            painter.drawLine(prev_x, prev_y, cx, cy)
            prev_x, prev_y = cx, cy

        painter.end()


def _fmt_num(n: int) -> str:
    if n >= 1_000_000:
        return f"{n // 1_000_000}M"
    if n >= 1_000:
        return f"{n // 1_000}K"
    return str(n)

