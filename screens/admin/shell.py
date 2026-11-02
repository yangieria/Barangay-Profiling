"""Separate application shell for Administrator accounts."""

from datetime import datetime

from PyQt6.QtCore import QPoint, QRectF, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget
)

import icons
import theme as T
import widgets as W

from screens.admin.dashboard import AdminDashboard
from screens.admin.residents import AdminResidents
from screens.admin.staff import StaffAccountsPage
from screens.admin.reports import AdminReports
from screens.admin.activity import ActivityLogsPage
from screens.admin.backup import BackupRestorePage


ADMIN_NAV = [
    (
        "dashboard",
        "Dashboard",
        "home"
    ),
    (
        "residents",
        "Residents Profile",
        "document"
    ),
    (
        "staff",
        "Staff Accounts",
        "person"
    ),
    (
        "reports",
        "Reports",
        "bars"
    ),
    (
        "activity",
        "Activity Logs",
        "document"
    ),
    (
        "backup",
        "Backups & Restore",
        "save"
    )
]


CRUMBS = {
    "residents": "Residents Profile",
    "staff": "Staff Accounts",
    "reports": "Reports",
    "activity": "Activity Logs",
    "backup": "Backups & Restore"
}


class AdminNavButton(QPushButton):
    def __init__(self, text, icon):
        super().__init__()

        self._text = text
        self._icon = icon
        self._active = False
        self._hover = False

        self.setFixedHeight(46)

        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

    def set_active(self, flag):
        self._active = flag
        self.update()

    def enterEvent(self, event):
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.TextAntialiasing
        )

        if self._active:
            fill = QColor(
                T.NAV_ACTIVE
            )

        elif self._hover:
            fill = QColor(
                255,
                255,
                255,
                30
            )

        else:
            fill = None

        if fill:
            painter.setPen(
                Qt.PenStyle.NoPen
            )

            painter.setBrush(
                fill
            )

            painter.drawRoundedRect(
                QRectF(
                    self.rect()
                ),
                14,
                14
            )

        height = self.height()

        pixmap = icons.pixmap(
            self._icon,
            24,
            "#FFFFFF"
        )

        painter.drawPixmap(
            QRectF(
                26,
                (height - 24) / 2,
                24,
                24
            ),
            pixmap,
            QRectF(
                0,
                0,
                pixmap.width(),
                pixmap.height()
            )
        )

        font = QFont(
            T.family()
        )

        font.setPixelSize(16)

        font.setWeight(
            QFont.Weight.Normal
        )

        painter.setFont(font)

        painter.setPen(
            QColor("#FFFFFF")
        )

        painter.drawText(
            QRectF(
                64,
                0,
                self.width() - 72,
                height
            ),
            Qt.AlignmentFlag.AlignVCenter
            | Qt.AlignmentFlag.AlignLeft,
            self._text
        )


class AdminSidebar(QWidget):
    def __init__(
        self,
        on_nav,
        on_logout
    ):
        super().__init__()

        self.setFixedWidth(
            T.SIDEBAR_W
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16,
            22,
            16,
            18
        )

        layout.setSpacing(0)

        logo = QLabel()

        logo.setPixmap(
            icons.logo_pixmap(92)
        )

        logo.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(logo)
        layout.addSpacing(12)

        name = QLabel(
            "Barangay\nAdministration"
        )

        name.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        name.setStyleSheet(
            "font-size: 17px;"
            "font-weight: 700;"
            "color: white;"
        )

        layout.addWidget(name)
        layout.addSpacing(16)

        layout.addWidget(
            self._line()
        )

        layout.addSpacing(18)

        self.buttons = {}

        for key, label, icon in ADMIN_NAV:
            button = AdminNavButton(
                label,
                icon
            )

            button.clicked.connect(
                lambda checked=False, k=key:
                on_nav(k)
            )

            self.buttons[key] = button

            layout.addWidget(
                button
            )

            layout.addSpacing(10)

        layout.addStretch(1)

        layout.addWidget(
            self._line()
        )

        layout.addSpacing(14)

        logout = AdminNavButton(
            "Logout",
            "logout"
        )

        logout.clicked.connect(
            lambda:
            on_logout()
        )

        layout.addWidget(
            logout
        )

    @staticmethod
    def _line():
        line = QFrame()

        line.setFixedHeight(2)

        line.setStyleSheet(
            "background: #3F7C6A;"
            "border: none;"
        )

        box = QWidget()

        layout = QHBoxLayout(box)

        layout.setContentsMargins(
            40,
            0,
            40,
            0
        )

        layout.addWidget(line)

        return box

    def set_active(self, key):
        for name, button in self.buttons.items():
            button.set_active(
                name == key
            )

    def paintEvent(self, event):
        painter = QPainter(self)

        gradient = QLinearGradient(
            0,
            0,
            0,
            self.height()
        )

        gradient.setColorAt(
            0.0,
            QColor(
                15,
                77,
                59
            )
        )

        gradient.setColorAt(
            0.7,
            QColor(
                11,
                96,
                73
            )
        )

        gradient.setColorAt(
            1.0,
            QColor(
                9,
                82,
                62
            )
        )

        painter.fillRect(
            self.rect(),
            gradient
        )


class AdminShell(QWidget):
    def __init__(
        self,
        window,
        user
    ):
        super().__init__()

        self.win = window
        self.user = user

        root = QHBoxLayout(self)

        root.setContentsMargins(
            0,
            0,
            0,
            0
        )

        root.setSpacing(0)

        self.sidebar = AdminSidebar(
            self.navigate,
            window.confirm_logout
        )

        root.addWidget(
            self.sidebar
        )

        main = QWidget()

        main_layout = QVBoxLayout(
            main
        )

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        main_layout.setSpacing(0)

        main_layout.addWidget(
            self._topbar()
        )

        self.holder = QVBoxLayout()

        self.holder.setContentsMargins(
            48,
            0,
            48,
            14
        )

        main_layout.addLayout(
            self.holder,
            1
        )

        rule = QFrame()

        rule.setFixedHeight(2)

        rule.setStyleSheet(
            "background: #E3E8E6;"
            "border: none;"
        )

        main_layout.addWidget(
            rule
        )

        root.addWidget(
            main,
            1
        )

        self.page = None

        self.navigate(
            "dashboard"
        )

        self._timer = QTimer(self)

        self._timer.timeout.connect(
            self._tick
        )

        self._timer.start(
            15000
        )

        self._tick()

    def _topbar(self):
        bar = QWidget()

        bar.setFixedHeight(74)

        layout = QHBoxLayout(
            bar
        )

        layout.setContentsMargins(
            48,
            0,
            36,
            0
        )

        self.crumbs = QHBoxLayout()

        self.crumbs.setSpacing(4)

        crumb_widget = QWidget()

        crumb_widget.setLayout(
            self.crumbs
        )

        layout.addWidget(
            crumb_widget,
            0,
            Qt.AlignmentFlag.AlignBottom
        )

        layout.addStretch(1)

        clock = QVBoxLayout()

        clock.setSpacing(0)

        clock.addStretch(1)

        self.clock1 = QLabel()
        self.clock2 = QLabel()

        for label in (
            self.clock1,
            self.clock2
        ):
            label.setObjectName(
                "subtitle"
            )

            label.setStyleSheet(
                "font-size: 11px;"
            )

            label.setAlignment(
                Qt.AlignmentFlag.AlignRight
            )

            clock.addWidget(
                label
            )

        clock.addStretch(1)

        layout.addLayout(clock)

        layout.addSpacing(14)

        divider = QFrame()

        divider.setFixedSize(
            2,
            46
        )

        divider.setStyleSheet(
            "background: #C9CFCC;"
            "border: none;"
        )

        layout.addWidget(
            divider
        )

        layout.addSpacing(14)

        who = W.ClickableFrame()

        who_layout = QHBoxLayout(
            who
        )

        who_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        who_layout.setSpacing(10)

        who_layout.addWidget(
            W.circle(
                48,
                T.GREEN_DARK,
                "person",
                26
            )
        )

        names = QVBoxLayout()

        names.setSpacing(0)

        names.addStretch(1)

        full_name = self.user[
            "full_name"
        ]

        if len(full_name) < 22:
            display_name = full_name
        else:
            display_name = (
                full_name[:20]
                + "…"
            )

        name = QLabel(
            display_name
        )

        name.setStyleSheet(
            f"font-size: 13px;"
            f"font-weight: 700;"
            f"color: {T.GREEN_TITLE};"
        )

        role = QLabel(
            "Administrator"
        )

        role.setObjectName(
            "subtitle"
        )

        role.setStyleSheet(
            "font-size: 11px;"
        )

        names.addWidget(name)
        names.addWidget(role)
        names.addStretch(1)

        who_layout.addLayout(
            names
        )

        arrow = QLabel()

        arrow.setPixmap(
            icons.pixmap(
                "chevron_down",
                14,
                "#555F5B"
            )
        )

        who_layout.addWidget(
            arrow
        )

        W.make_transparent_to_mouse(
            who
        )

        menu = QMenu(self)

        menu.addAction(
            "Logout",
            self.win.confirm_logout
        )

        who.clicked.connect(
            lambda:
            menu.exec(
                who.mapToGlobal(
                    QPoint(
                        0,
                        who.height() + 6
                    )
                )
            )
        )

        layout.addWidget(
            who
        )

        return bar

    def _tick(self):
        now = datetime.now()

        self.clock1.setText(
            f"{now:%B} "
            f"{now.day}, "
            f"{now.year}"
        )

        self.clock2.setText(
            f"{now:%A} | "
            f"{now.strftime('%I:%M %p').lstrip('0')}"
        )

    def _set_crumbs(
        self,
        key
    ):
        while self.crumbs.count():
            item = self.crumbs.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        if key == "dashboard":
            return

        self.crumbs.addWidget(
            W.button(
                "Dashboard",
                lambda:
                self.navigate(
                    "dashboard"
                ),
                "link",
                width=0,
                height=24
            )
        )

        arrow = QLabel()

        arrow.setPixmap(
            icons.pixmap(
                "chevron_right",
                12,
                "#555F5B"
            )
        )

        self.crumbs.addWidget(
            arrow
        )

        current = QLabel(
            CRUMBS.get(
                key,
                key
            )
        )

        current.setStyleSheet(
            f"font-size: 13px;"
            f"color: {T.MUTED};"
        )

        self.crumbs.addWidget(
            current
        )

    def navigate(
        self,
        key,
        **kwargs
    ):
        pages = {
            "dashboard":
                lambda:
                AdminDashboard(
                    self
                ),

            "residents":
                lambda:
                AdminResidents(
                    self
                ),

            "staff":
                lambda:
                StaffAccountsPage(
                    self
                ),

            "reports":
                lambda:
                AdminReports(
                    self
                ),

            "activity":
                lambda:
                ActivityLogsPage(
                    self
                ),

            "backup":
                lambda:
                BackupRestorePage(
                    self
                )
        }

        if key not in pages:
            return

        if self.page is not None:
            self.holder.removeWidget(
                self.page
            )

            self.page.deleteLater()

        self.page = pages[key]()

        self.holder.addWidget(
            self.page
        )

        self.sidebar.set_active(
            key
        )

        self._set_crumbs(
            key
        )