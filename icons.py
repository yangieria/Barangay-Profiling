"""Small icons drawn with QPainter (no image files needed).

Put a PNG named like the icon in assets/icons/ (for example home.png) and it
replaces the drawn one.
"""
from functools import lru_cache

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (QBrush, QColor, QIcon, QImage, QPainter, QPainterPath, QPen,
                         QPixmap, QPolygonF)

import resources

SS = 4  # render at 4x then let Qt scale, so edges stay sharp on any screen


def _poly(*pts):
    return QPolygonF([QPointF(x, y) for x, y in pts])


class _Pen:
    """Tiny helper so the shapes below read like a drawing script."""

    def __init__(self, p, color):
        self.p, self.color = p, QColor(color)

    def fill(self):
        self.p.setPen(Qt.PenStyle.NoPen)
        self.p.setBrush(QBrush(self.color))

    def stroke(self, w):
        self.p.setBrush(Qt.BrushStyle.NoBrush)
        self.p.setPen(QPen(self.color, w, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                           Qt.PenJoinStyle.RoundJoin))

    def cut(self, on=True):
        mode = QPainter.CompositionMode.CompositionMode_Clear if on else \
            QPainter.CompositionMode.CompositionMode_SourceOver
        self.p.setCompositionMode(mode)

    def line(self, *pts, w=6):
        self.stroke(w)
        path = QPainterPath(QPointF(*pts[0]))
        for pt in pts[1:]:
            path.lineTo(QPointF(*pt))
        self.p.drawPath(path)

    def rrect(self, x, y, w, h, r):
        self.p.drawRoundedRect(QRectF(x, y, w, h), r, r)

    def ellipse(self, x, y, w, h):
        self.p.drawEllipse(QRectF(x, y, w, h))


def _draw(name, d):
    if name == "home":
        d.fill(); d.p.drawPolygon(_poly((32, 7), (59, 31), (50, 31), (50, 57), (38, 57), (38, 40),
                                        (26, 40), (26, 57), (14, 57), (14, 31), (5, 31)))
    elif name == "user_plus":
        d.fill(); d.ellipse(14, 8, 20, 20); d.ellipse(4, 34, 40, 40)
        d.line((45, 28), (61, 28), w=6); d.line((53, 20), (53, 36), w=6)
    elif name == "document":
        d.fill(); d.rrect(12, 4, 40, 56, 6)
        d.cut()
        for y in (20, 31, 42):
            d.line((20, y), (44, y), w=4)
        d.cut(False)
    elif name == "pencil":
        d.fill()
        d.p.drawPolygon(_poly((14, 38), (40, 12), (52, 24), (26, 50)))
        d.p.drawPolygon(_poly((12, 42), (22, 52), (6, 58)))
        d.p.drawPolygon(_poly((43, 9), (48, 4), (60, 16), (55, 21)))
    elif name == "trash":
        d.fill(); d.rrect(10, 14, 44, 7, 3); d.rrect(24, 6, 16, 9, 3)
        d.p.drawPolygon(_poly((15, 25), (49, 25), (46, 58), (18, 58)))
        d.cut()
        for x in (25, 32, 39):
            d.line((x, 31), (x, 51), w=3.6)
        d.cut(False)
    elif name == "bars":
        d.fill()
        for r in ((7, 38, 14, 20), (25, 24, 14, 34), (43, 8, 14, 50)):
            d.rrect(*r, 3)
    elif name == "logout":
        d.line((30, 10), (12, 10), (12, 54), (30, 54), w=6)
        d.line((24, 32), (54, 32), w=6); d.line((44, 21), (55, 32), (44, 43), w=6)
    elif name == "mail":
        d.stroke(4); d.rrect(7, 15, 50, 34, 6); d.line((9, 18), (32, 36), (55, 18), w=4)
    elif name == "lock":
        d.fill(); d.rrect(13, 28, 38, 31, 7)
        d.stroke(5)
        path = QPainterPath(QPointF(22, 31)); path.lineTo(22, 22)
        path.arcTo(QRectF(22, 12, 20, 20), 180, -180); path.lineTo(42, 31)
        d.p.drawPath(path)
        d.fill(); d.cut(); d.ellipse(28, 38, 8, 8); d.cut(False)
    elif name in ("eye", "eye_off"):
        d.stroke(4); d.ellipse(5, 18, 54, 28)
        d.fill(); d.ellipse(24, 24, 16, 16)
        if name == "eye_off":
            d.cut(); d.line((10, 56), (54, 8), w=10); d.cut(False)
            d.line((10, 56), (54, 8), w=5)
    elif name == "search":
        d.stroke(6); d.ellipse(11, 11, 28, 28); d.line((38, 38), (55, 55), w=7)
    elif name == "chevron_right":
        d.line((23, 10), (45, 32), (23, 54), w=7)
    elif name == "chevron_down":
        d.line((10, 22), (32, 44), (54, 22), w=7)
    elif name == "save":
        d.fill(); d.rrect(8, 8, 48, 48, 7)
        d.cut(); d.rrect(18, 13, 26, 14, 2); d.rrect(16, 36, 32, 16, 3); d.cut(False)
        d.fill(); d.p.drawRect(QRectF(36, 16, 5, 8))
    elif name == "arrow_left":
        d.line((56, 32), (10, 32), w=7); d.line((28, 14), (10, 32), (28, 50), w=7)
    elif name == "arrow_right":
        d.line((8, 32), (54, 32), w=7); d.line((36, 14), (54, 32), (36, 50), w=7)
    elif name == "check":
        d.line((10, 34), (26, 48), (54, 16), w=8)
    elif name == "plus":
        d.line((32, 8), (32, 56), w=8); d.line((8, 32), (56, 32), w=8)
    elif name == "person":
        d.fill(); d.ellipse(18, 6, 28, 28); d.ellipse(6, 38, 52, 58)
    elif name == "warning":
        d.fill(); d.p.drawPolygon(_poly((32, 6), (60, 56), (4, 56)))
        d.cut(); d.line((32, 22), (32, 38), w=6); d.ellipse(28.5, 43, 7, 7); d.cut(False)
    elif name == "download":
        d.line((32, 8), (32, 40), w=7); d.line((17, 27), (32, 42), (47, 27), w=7)
        d.line((10, 56), (54, 56), w=7)
    else:
        d.fill(); d.ellipse(16, 16, 32, 32)


@lru_cache(maxsize=None)
def pixmap(name, size=24, color="#FFFFFF"):
    custom = resources.asset(f"icons/{name}.png")
    if custom is not None:
        pm = QPixmap(str(custom)).scaled(size * SS, size * SS, Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation)
        pm.setDevicePixelRatio(SS)
        return pm
    px = size * SS
    img = QImage(px, px, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
    p.scale(px / 64, px / 64)
    _draw(name, _Pen(p, color))
    p.end()
    pm = QPixmap.fromImage(img)
    pm.setDevicePixelRatio(SS)
    return pm


@lru_cache(maxsize=None)
def icon(name, size=24, color="#FFFFFF"):
    return QIcon(pixmap(name, size, color))


def save_png(name, size, color, path):
    """Write an icon to disk (the stylesheet needs files for its url() images)."""
    img = pixmap(name, size, color).toImage()
    img.save(str(path))
    return path


@lru_cache(maxsize=None)
def logo_pixmap(px):
    """assets/logo.png at px x px, or a generated "LOGO" seal if the file isn't there yet."""
    path = resources.asset("logo.png")
    ratio = 2
    if path is not None:
        pm = QPixmap(str(path)).scaled(px * ratio, px * ratio, Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
        pm.setDevicePixelRatio(ratio)
        return pm
    img = QImage(px * ratio, px * ratio, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
    n = px * ratio
    p.setPen(Qt.PenStyle.NoPen)
    for inset, color in ((0, "#E8B824"), (0.07, "#C43028"), (0.17, "#FFFFFF")):
        p.setBrush(QColor(color))
        p.drawEllipse(QRectF(n * inset, n * inset, n * (1 - 2 * inset), n * (1 - 2 * inset)))
    p.setPen(QColor("#C43028"))
    f = p.font()
    f.setPixelSize(int(n * 0.2))
    p.setFont(f)
    p.drawText(QRectF(0, 0, n, n), Qt.AlignmentFlag.AlignCenter, "LOGO")
    p.end()
    pm = QPixmap.fromImage(img)
    pm.setDevicePixelRatio(ratio)
    return pm
