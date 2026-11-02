"""Login, create-account and reset-password screen."""
import re

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPixmap
from PyQt6.QtWidgets import (QCheckBox, QFrame, QHBoxLayout, QLabel, QStackedWidget, QVBoxLayout,
                             QWidget)

import database as db
import icons
import resources
import theme as T
import widgets as W

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class BrandPanel(QWidget):
    """Left side: photo (or gradient), seal, title and tagline."""

    def __init__(self):
        super().__init__()
        path = resources.asset("login_bg.png")
        self.bg = QPixmap(str(path)) if path else None

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing
                         | QPainter.RenderHint.SmoothPixmapTransform)
        w, h = self.width(), self.height()
        if self.bg is not None:
            pm = self.bg.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                Qt.TransformationMode.SmoothTransformation)
            p.drawPixmap((w - pm.width()) // 2, (h - pm.height()) // 2, pm)
            p.fillRect(0, 0, w, h, QColor(9, 82, 62, 175))
        else:
            g = QLinearGradient(0, 0, 0, h)
            g.setColorAt(0, QColor(12, 84, 64))
            g.setColorAt(1, QColor(18, 96, 72))
            p.fillRect(0, 0, w, h, g)
            p.setPen(Qt.PenStyle.NoPen)
            for cx, cy, r, a in ((0.15, 0.55, 0.55, 22), (0.95, 0.35, 0.45, 18), (0.5, 1.0, 0.7, 20)):
                p.setBrush(QColor(255, 255, 255, a))
                p.drawEllipse(QRectF(w * (cx - r), h * cy - w * r, w * 2 * r, w * 2 * r))
        band_top = int(h * 0.835)
        p.fillRect(0, band_top, w, h - band_top, QColor(T.GREEN_DEEP))

        size = int(min(h * 0.24, w * 0.42))
        p.drawPixmap((w - size) // 2, int(h * 0.085), icons.logo_pixmap(size))

        def text(x, y, s, font, color):
            p.setFont(font)
            p.setPen(QColor(color))
            fh = p.fontMetrics().height()
            p.drawText(QRectF(x, y - fh / 2, w, fh), Qt.AlignmentFlag.AlignLeft |
                       Qt.AlignmentFlag.AlignVCenter, s)

        script = QFont(T.script_family())
        script.setItalic(True)
        script.setPixelSize(max(int(w * 0.058), 20))
        text(w * 0.085, h * 0.385, "Welcome to the", script, T.GOLD)
        big = QFont(T.family())
        big.setBold(True)
        big.setItalic(True)
        big.setPixelSize(max(int(w * 0.078), 28))
        for i, word in enumerate(("BARANGAY", "PROFILING", "SYSTEM")):
            text(w * 0.225, h * 0.47 + i * big.pixelSize() * 1.28, word, big, "#FFFFFF")
        tag = QFont(T.script_family())
        tag.setItalic(True)
        tag.setPixelSize(max(int(w * 0.043), 15))
        mid = band_top + (h - band_top) / 2
        text(w * 0.17, mid - tag.pixelSize() * 0.7, "A better barangay", tag, "#7FB3A1")
        text(w * 0.33, mid + tag.pixelSize() * 0.8, "A brighter tomorrow", tag, "#7FB3A1")


def _titles(lay, title, subtitle):
    t = QLabel(title)
    t.setObjectName("title")
    t.setStyleSheet("font-size: 38px;")
    s = QLabel(subtitle)
    s.setObjectName("subtitle")
    s.setWordWrap(True)
    s.setStyleSheet("font-size: 14px;")
    s.setContentsMargins(4, 0, 0, 0)
    lay.addWidget(t)
    lay.addWidget(s)
    lay.addSpacing(18)


def _form(spacing=10):
    f = QWidget()
    f.setFixedWidth(540)
    lay = QVBoxLayout(f)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(spacing)
    return f, lay


class LoginScreen(QWidget):
    def __init__(self, window):
        super().__init__()
        self.win = window
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(BrandPanel(), 43)

        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        self.stack = QStackedWidget()
        self.stack.setFixedWidth(540)
        rl.addStretch(1)
        rl.addWidget(self.stack, 0, Qt.AlignmentFlag.AlignHCenter)
        rl.addStretch(1)
        root.addWidget(right, 57)

        self.forms = {"login": self._login_form(), "register": self._register_form(),
                      "reset": self._reset_form()}
        for f in self.forms.values():
            self.stack.addWidget(f)
        self.show_form("login")

    # ---- helpers --------------------------------------------------------
    def show_form(self, name, notice="", ok=False):
        self.stack.setCurrentWidget(self.forms[name])
        self._say(name, notice, ok)
        {"login": self.email_in, "register": self.r_name, "reset": self.x_email}[name].setFocus()

    def _msg_label(self):
        lbl = QLabel("")
        lbl.setWordWrap(True)
        lbl.setMinimumHeight(20)
        lbl.setContentsMargins(6, 0, 0, 0)
        return lbl

    def _say(self, form, text, ok=False):
        lbl = {"login": self.l_msg, "register": self.r_msg, "reset": self.x_msg}[form]
        lbl.setText(text)
        lbl.setStyleSheet(f"font-size: 12px; color: {T.GREEN if ok else T.RED};")

    @staticmethod
    def _back_button(callback):
        return W.button("Back to Login", callback, "ghost", width=200)

    # ---- login ----------------------------------------------------------
    def _login_form(self):
        f, lay = _form()
        _titles(lay, "Welcome Back",
                "Login to access the Barangay Profiling System and manage community records.")
        self.email_in = W.IconLineEdit("mail", "Email Address")
        self.pw_in = W.IconLineEdit("lock", "Password", password=True)
        lay.addWidget(self.email_in)
        lay.addWidget(self.pw_in)
        row = QHBoxLayout()
        self.remember = QCheckBox("Remember Me")
        self.remember.setCursor(Qt.CursorShape.PointingHandCursor)
        forgot = W.button("Forgot Password?", lambda: self.show_form("reset"), "ghost",
                          width=0, height=26)
        row.addWidget(self.remember)
        row.addStretch(1)
        row.addWidget(forgot)
        lay.addLayout(row)
        self.l_msg = self._msg_label()
        lay.addWidget(self.l_msg)
        lay.addWidget(W.button("Login", self._login, icon="arrow_right", icon_right=True,
                               width=540, height=54))
        lay.addSpacing(6)

        div = QHBoxLayout()
        for i in range(3):
            if i == 1:
                o = QLabel("OR")
                o.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {T.MUTED};")
                div.addWidget(o)
            else:
                line = QFrame()
                line.setFixedHeight(2)
                line.setStyleSheet("background: #B9C2BE; border: none;")
                div.addWidget(line, 1)
            div.addSpacing(10) if i < 2 else None
        lay.addLayout(div)
        lay.addSpacing(4)
        q = QLabel("Don’t have an account?")
        q.setAlignment(Qt.AlignmentFlag.AlignCenter)
        q.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {T.MUTED};")
        lay.addWidget(q)
        lay.addWidget(W.button("Create New Account", lambda: self.show_form("register"),
                               "outline", icon="user_plus", width=300, height=48),
                      0, Qt.AlignmentFlag.AlignHCenter)

        saved = resources.load_settings().get("email", "")
        if saved:
            self.email_in.setText(saved)
            self.remember.setChecked(True)
        self.email_in.returnPressed.connect(self.pw_in.setFocus)
        self.pw_in.returnPressed.connect(self._login)
        return f

    def _login(self):
        email, pw = self.email_in.text(), self.pw_in.text()
        self.email_in.set_error(False)
        self.pw_in.set_error(False)
        if not email or not pw:
            self.email_in.set_error(not email)
            self.pw_in.set_error(not pw)
            return self._say("login", "Enter your email and password.")
        user = db.check_login(email, pw)
        if not user:
            if not db.has_users():
                return self._say("login", "There are no accounts yet. Create one first.")
            self.pw_in.set_error(True)
            return self._say("login", "Incorrect email or password.")
        resources.save_settings(email=email if self.remember.isChecked() else "")
        self.win.login(user)

    # ---- register -------------------------------------------------------
    def _register_form(self):
        f, lay = _form(8)
        _titles(lay, "Create Account",
                "Set up an official account. The recovery key lets you reset your password "
                "later, so keep it somewhere safe.")
        self.r_name = W.IconLineEdit("person", "Full Name", height=48)
        self.r_email = W.IconLineEdit("mail", "Email Address", height=48)
        self.r_pw = W.IconLineEdit("lock", "Password (at least 6 characters)", True, 48)
        self.r_pw2 = W.IconLineEdit("lock", "Confirm Password", True, 48)
        self.r_key = W.IconLineEdit("lock", "Recovery Key (at least 4 characters)", True, 48)
        for w in (self.r_name, self.r_email, self.r_pw, self.r_pw2, self.r_key):
            lay.addWidget(w)
        self.r_msg = self._msg_label()
        lay.addWidget(self.r_msg)
        lay.addWidget(W.button("Create Account", self._register, icon="check", width=540, height=50))
        lay.addWidget(self._back_button(lambda: self.show_form("login")), 0,
                      Qt.AlignmentFlag.AlignHCenter)
        self.r_key.returnPressed.connect(self._register)
        return f

    def _register(self):
        name, email = self.r_name.text(), self.r_email.text()
        pw, pw2, key = self.r_pw.text(), self.r_pw2.text(), self.r_key.text()
        fields = [self.r_name, self.r_email, self.r_pw, self.r_pw2, self.r_key]
        for e in fields:
            e.set_error(False)
        checks = [
            (self.r_name, bool(name), "Enter your full name."),
            (self.r_email, bool(EMAIL_RE.match(email)), "Enter a valid email address."),
            (self.r_pw, len(pw) >= 6, "Use a password with at least 6 characters."),
            (self.r_pw2, pw == pw2, "The two passwords don't match."),
            (self.r_key, len(key) >= 4, "The recovery key needs at least 4 characters."),
        ]
        for field, ok, msg in checks:
            if not ok:
                field.set_error()
                return self._say("register", msg)
        if not db.create_user(name, email, pw, key):
            self.r_email.set_error()
            return self._say("register", "That email is already registered.")
        for e in fields:
            e.clear()
        self.email_in.setText(email)
        self.pw_in.clear()
        self.show_form("login", "Account created. You can log in now.", ok=True)
        self.pw_in.setFocus()

    # ---- reset ----------------------------------------------------------
    def _reset_form(self):
        f, lay = _form(8)
        _titles(lay, "Reset Password",
                "Enter your email, the recovery key you set when creating the account, and a "
                "new password.")
        self.x_email = W.IconLineEdit("mail", "Email Address", height=50)
        self.x_key = W.IconLineEdit("lock", "Recovery Key", True, 50)
        self.x_pw = W.IconLineEdit("lock", "New Password (at least 6 characters)", True, 50)
        self.x_pw2 = W.IconLineEdit("lock", "Confirm New Password", True, 50)
        for w in (self.x_email, self.x_key, self.x_pw, self.x_pw2):
            lay.addWidget(w)
        self.x_msg = self._msg_label()
        lay.addWidget(self.x_msg)
        lay.addWidget(W.button("Reset Password", self._reset, icon="check", width=540, height=50))
        lay.addWidget(self._back_button(lambda: self.show_form("login")), 0,
                      Qt.AlignmentFlag.AlignHCenter)
        self.x_pw2.returnPressed.connect(self._reset)
        return f

    def _reset(self):
        email, key, pw, pw2 = (self.x_email.text(), self.x_key.text(), self.x_pw.text(),
                               self.x_pw2.text())
        if not (email and key and pw):
            return self._say("reset", "Fill in every field.")
        if len(pw) < 6:
            return self._say("reset", "Use a password with at least 6 characters.")
        if pw != pw2:
            return self._say("reset", "The two passwords don't match.")
        if not db.reset_password(email, key, pw):
            return self._say("reset", "Email or recovery key is incorrect.")
        for e in (self.x_key, self.x_pw, self.x_pw2):
            e.clear()
        self.email_in.setText(email)
        self.pw_in.clear()
        self.show_form("login", "Password updated. You can log in now.", ok=True)
