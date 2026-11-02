"""Add New Profile / Update Profile (same form, two modes)."""
import re

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

import database as db
import dialogs
import theme as T
import widgets as W

PHONE_RE = re.compile(r"^(09\d{9}|\+639\d{9})$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
REQUIRED = ("last_name", "first_name", "birth_date", "birth_place", "sex", "civil_status",
            "address", "contact")


def _tidy(text):
    text = " ".join(text.split())
    return text.title() if text.islower() or text.isupper() else text


class ResidentForm(QWidget):
    def __init__(self, shell, mode="add", resident_id=None):
        super().__init__()
        self.shell, self.mode = shell, mode
        self.current_id = None
        add = mode == "add"
        self.compact = shell.win.height() < 760           # short laptop screens get tighter rows

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(W.page_header(
            "Add New Profile" if add else "Update Profile",
            "Encode the resident’s information below." if add else
            "Look up a resident by ID, then edit their information.",
            size=30 if self.compact else 36))

        if not add:
            lay.addSpacing(6 if self.compact else 10)
            row = QHBoxLayout()
            row.setSpacing(12)
            self.id_entry = W.IconLineEdit("search", "Resident ID (example: R0007)", height=44)
            row.addWidget(self.id_entry, 1)
            row.addWidget(W.button("SEARCH", self._search, width=130, height=44))
            lay.addLayout(row)
            self.id_entry.returnPressed.connect(self._search)

        lay.addSpacing(8 if self.compact else 12)
        card = QFrame()
        card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(34, 12 if self.compact else 20, 34, 12 if self.compact else 16)
        cl.setSpacing(0)

        self.heading = QLabel("RESIDENT INFORMATION" if add else "EDIT RESIDENT INFORMATION")
        self.heading.setStyleSheet(f"font-size: 17px; font-weight: 700; color: {T.GREEN_TITLE};")
        if not self.compact:                                # short screens skip it to save space
            hr = QHBoxLayout()
            hr.addWidget(self.heading)
            rule = QFrame()
            rule.setFixedHeight(2)
            rule.setStyleSheet("background: #8FB0A5; border: none;")
            hr.addWidget(rule, 1, Qt.AlignmentFlag.AlignVCenter)
            cl.addLayout(hr)
            cl.addSpacing(8)
        cl.addLayout(self._fields())
        cl.addStretch(1)

        line = QFrame()
        line.setObjectName("divider")
        line.setFixedHeight(1)
        cl.addWidget(line)
        cl.addSpacing(8)
        foot = QHBoxLayout()
        self.msg = QLabel("")
        self.msg.setWordWrap(True)
        foot.addWidget(self.msg, 1)
        h = 42 if self.compact else T.BTN_H
        self.save_btn = W.button("Save Profile", self._save, "dark", icon="save", width=170, height=h)
        foot.addWidget(self.save_btn)
        foot.addSpacing(12)
        foot.addWidget(W.button("Back", lambda: shell.navigate("home"), "outline",
                                icon="arrow_left", width=130, height=h))
        cl.addLayout(foot)
        lay.addWidget(card, 1)

        if not add:
            self._set_enabled(False)
            if resident_id:
                self.id_entry.setText(db.fmt_id(resident_id))
                self._search()
        else:
            self.f["last_name"].focus()

    # ---- layout ---------------------------------------------------------
    def _fields(self):
        fh = 34 if self.compact else None
        f = self.f = {}
        f["last_name"] = W.LabeledField("Last name", required=True, height=fh)
        f["first_name"] = W.LabeledField("First name", required=True, height=fh)
        f["middle_name"] = W.LabeledField("Middle name", height=fh)
        f["ext_name"] = W.LabeledField("Ext.", placeholder="Jr., III", height=fh)
        f["birth_date"] = W.DateField(height=fh)
        f["birth_place"] = W.LabeledField("Place of birth", required=True, height=fh)
        f["sex"] = W.LabeledField("Sex", "combo", db.SEX, required=True, height=fh)
        f["civil_status"] = W.LabeledField("Civil status", "combo", db.CIVIL_STATUS,
                                           required=True, height=fh)
        f["education"] = W.LabeledField("Highest educational attainment", "combo", db.EDUCATION,
                                        height=fh)
        f["occupation"] = W.LabeledField("Occupation", height=fh)
        f["address"] = W.LabeledField("Resident address", required=True, height=fh,
                                      placeholder="House no., street, purok / sitio")
        f["contact"] = W.LabeledField("Contact number", required=True, placeholder="09XXXXXXXXX",
                                      height=fh)
        f["email"] = W.LabeledField("Email", placeholder="name@example.com", height=fh)
        layout = [
            [("last_name", 4), ("first_name", 4), ("middle_name", 2), ("ext_name", 2)],
            [("birth_date", 5), ("birth_place", 7)],
            [("sex", 2), ("civil_status", 3), ("education", 7)],
        ]
        if self.compact:
            layout += [[("occupation", 6), ("contact", 6)], [("address", 7), ("email", 5)]]
        else:
            layout += [[("occupation", 12)], [("address", 12)], [("contact", 6), ("email", 6)]]
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(3 if self.compact else 8)
        for c in range(12):
            grid.setColumnStretch(c, 1)
        for r, row in enumerate(layout):
            col = 0
            for key, span in row:
                grid.addWidget(f[key], r, col, 1, span)
                col += span
        return grid

    # ---- helpers --------------------------------------------------------
    def _set_enabled(self, flag):
        for w in self.f.values():
            w.set_enabled(flag)
        self.save_btn.setEnabled(flag)

    def _say(self, text, ok=False):
        self.msg.setText(text)
        self.msg.setStyleSheet(f"font-size: 12px; color: {T.GREEN if ok else T.RED};")

    def _collect(self):
        """Validate and return the data dict, or None after flagging the problem."""
        for w in self.f.values():
            w.set_error(False)
        data = {k: w.get() for k, w in self.f.items() if k != "birth_date"}
        try:
            data["birth_date"] = self.f["birth_date"].get()
        except ValueError as err:
            self.f["birth_date"].set_error()
            self._say(str(err))
            return None
        missing = [k for k in REQUIRED if not data.get(k)]
        if missing:
            for k in missing:
                self.f[k].set_error()
            self._say("Fill in the highlighted fields.")
            return None
        data["contact"] = re.sub(r"[\s-]", "", data["contact"])
        if not PHONE_RE.match(data["contact"]):
            self.f["contact"].set_error()
            self._say("Contact number should look like 09123456789 or +639123456789.")
            return None
        if data["email"] and not EMAIL_RE.match(data["email"]):
            self.f["email"].set_error()
            self._say("That email address doesn't look right.")
            return None
        for k in ("last_name", "first_name", "middle_name", "birth_place", "occupation"):
            data[k] = _tidy(data[k])
        self._say("")
        return data

    # ---- actions --------------------------------------------------------
    def _save(self):
        data = self._collect()

        if data is None:
            return

        name = f"{data['first_name']} {data['last_name']}"

        user = self.shell.user
        user_id = user.get("id")
        user_name = user.get("full_name", "Unknown User")
        user_role = user.get("role", "Staff")

        if self.mode == "add":
            rid = db.add_resident(data)

            db.add_activity(
                user_id,
                user_name,
                user_role,
                "Added Resident",
                f"Added resident {name} ({db.fmt_id(rid)})."
            )

            dialogs.info(
                self,
                "Profile saved",
                f"{name} was registered as {db.fmt_id(rid)}."
            )

            for w in self.f.values():
                w.clear()

            self.f["last_name"].focus()

        elif self.current_id:
            db.update_resident(
                self.current_id,
                data
            )

            db.add_activity(
                user_id,
                user_name,
                user_role,
                "Updated Resident",
                f"Updated resident {name} ({db.fmt_id(self.current_id)})."
            )

            dialogs.info(
                self,
                "Profile updated",
                f"The record of {name} ({db.fmt_id(self.current_id)}) has been updated."
            )

    def _search(self):
        rid = db.parse_id(self.id_entry.text())
        self.id_entry.set_error(False)
        if rid is None:
            self.id_entry.set_error()
            return self._say("Type the resident ID first, for example R0007.")
        r = db.get_resident(rid)
        if not r:
            self.current_id = None
            self._set_enabled(False)
            for w in self.f.values():
                w.clear()
            self.heading.setText("EDIT RESIDENT INFORMATION")
            self.id_entry.set_error()
            return self._say(f"No resident found with ID {db.fmt_id(rid)}.")
        self.current_id = rid
        self._set_enabled(True)
        for k, w in self.f.items():
            w.set(r[k])
        self.heading.setText(f"EDIT RESIDENT INFORMATION  ·  {db.fmt_id(rid)}")
        self._say(f"Loaded {db.full_name(r)}  ({db.fmt_id(rid)})", ok=True)
