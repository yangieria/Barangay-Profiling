"""Barangay Profiling System (PyQt6). Run this file:  python main.py"""
import sys

from PyQt6.QtGui import QColor, QIcon, QPalette
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget

import database as db
import dialogs
import icons
import resources
import theme as T
from screens.login import LoginScreen
from screens.shell import Shell
from screens.admin.shell import AdminShell


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Barangay Profiling System")
        ico = resources.asset("logo.ico") or resources.asset("logo.png")
        self.setWindowIcon(QIcon(str(ico)) if ico else QIcon(icons.logo_pixmap(64)))
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self._place()
        self.show_login()

    def _place(self):
        area = self.screen().availableGeometry()
        w, h = min(1366, area.width() - 60), min(800, area.height() - 90)
        self.setMinimumSize(min(1180, w), min(680, h))
        self.resize(w, h)
        self.move(area.x() + (area.width() - w) // 2, area.y() + max((area.height() - h) // 2 - 10, 0))

    def _swap(self, widget):
        old = self.stack.currentWidget()
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)
        if old is not None:
            self.stack.removeWidget(old)
            old.deleteLater()

    def show_login(self):
        self._swap(LoginScreen(self))

    def login(self, user):
        if user.get("role") == "Admin":
            self._swap(
            AdminShell(
                self,
                user
            )
        )
        else:
            self._swap(
            Shell(
                self,
                user
            )
        )
    def confirm_logout(self):
        ok = dialogs.ask(
            self,
            "Log Out?",
            "Are you sure you want to log out?",
             confirm="Logout",
             icon="logout"
    )

        if ok:
            self.show_login()



def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    T.init_fonts(app)
    pal = app.palette()
    for role, color in ((QPalette.ColorRole.PlaceholderText, T.PLACEHOLDER),
                        (QPalette.ColorRole.Text, T.TEXT), (QPalette.ColorRole.Base, T.WHITE),
                        (QPalette.ColorRole.Window, T.WHITE)):
        pal.setColor(role, QColor(color))
    app.setPalette(pal)
    # the stylesheet needs real image files for the dropdown arrow and the checkbox tick
    resources.CACHE.mkdir(parents=True, exist_ok=True)
    arrow = icons.save_png("chevron_down", 14, "#2F5E4F", resources.CACHE / "arrow.png")
    check = icons.save_png("check", 14, "#FFFFFF", resources.CACHE / "check.png")
    app.setStyleSheet(T.stylesheet(arrow.as_posix(), check.as_posix()))
    db.init()
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
