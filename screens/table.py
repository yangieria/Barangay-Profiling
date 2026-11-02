"""View Resident Profiles and Delete Profile (same table, two modes)."""
from PyQt6.QtCore import QEvent, Qt, QTimer
from PyQt6.QtWidgets import (QAbstractItemView, QFrame, QHBoxLayout, QHeaderView, QLabel,
                             QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

import database as db
import dialogs
import theme as T
import widgets as W

ROW_H = 38
# title, fixed width (None = flexible), weight for flexible columns
COLS = [("ID", 74, 0), ("Full Name", None, 3), ("Age", 52, 0), ("Gender", 90, 0),
        ("Address", None, 3), ("Civil Status", 104, 0), ("Contact #", 124, 0),
        ("Occupation", None, 2)]


class ResidentsTable(QWidget):
    def __init__(self, shell, mode="view"):
        super().__init__()
        self.shell, self.mode = shell, mode
        self.page, self.per_page, self.total = 1, 0, 0
        self.term, self.records = "", []
        view = mode == "view"

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(W.page_header(
            "View Resident Profiles" if view else "Delete Profile",
            "List of all registered residents in the barangay. Click a row to see the full record."
            if view else "Select a resident from the list, then press Delete Profile."))
        lay.addSpacing(10)

        top = QHBoxLayout()
        top.setSpacing(12)
        self.search = W.IconLineEdit("search", "Search by name, ID, address or occupation",
                                     height=46)
        top.addWidget(self.search, 1)
        if view:
            top.addWidget(W.button("Add New Profile", lambda: shell.navigate("add"), icon="plus",
                                   width=190, height=46))
        else:
            top.addWidget(W.button("SEARCH", self._run_search, width=130, height=46))
        lay.addLayout(top)
        lay.addSpacing(10)

        card = QFrame()
        card.setObjectName("tableCard")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(8, 8, 8, 8)
        cl.setSpacing(6)
        self.table = self._make_table()
        cl.addWidget(self.table, 1)
        cl.addWidget(self._make_footer())
        lay.addWidget(card, 1)

        self.empty = QLabel("", self.table.viewport())
        self.empty.setStyleSheet(f"font-size: 13px; color: {T.MUTED};")
        self.empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty.hide()

        if not view:
            lay.addSpacing(10)
            foot = QHBoxLayout()
            foot.addStretch(1)
            self.del_btn = W.button("Delete Profile", self._delete, "danger", icon="trash",
                                    width=190)
            self.del_btn.setEnabled(False)
            foot.addWidget(self.del_btn)
            foot.addSpacing(12)
            foot.addWidget(W.button("Back", lambda: shell.navigate("home"), "outline",
                                    icon="arrow_left", width=130))
            lay.addLayout(foot)

        self._type_timer = QTimer(self, singleShot=True, interval=250)
        self._type_timer.timeout.connect(self._run_search)
        self.search.edit.textChanged.connect(lambda _: self._type_timer.start())
        self.search.returnPressed.connect(self._run_search)
        self._fit_timer = QTimer(self, singleShot=True, interval=40)
        self._fit_timer.timeout.connect(self._fit)
        self.table.viewport().installEventFilter(self)
        QTimer.singleShot(0, self._fit)

    # ---- building -------------------------------------------------------
    def _make_table(self):
        t = QTableWidget(0, len(COLS))
        t.setProperty("mode", self.mode)
        t.setHorizontalHeaderLabels([c[0] for c in COLS])
        t.verticalHeader().setVisible(False)
        t.verticalHeader().setDefaultSectionSize(ROW_H)
        hdr = t.horizontalHeader()
        hdr.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        hdr.setHighlightSections(False)
        hdr.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        hdr.setSectionsClickable(False)
        t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        t.setShowGrid(False)
        t.setWordWrap(False)
        t.setAlternatingRowColors(True)
        t.setFrameShape(QFrame.Shape.NoFrame)
        t.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        t.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        t.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        t.setTextElideMode(Qt.TextElideMode.ElideRight)
        t.setMouseTracking(True)
        if self.mode == "view":
            t.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
            t.cellClicked.connect(self._clicked)
            t.viewport().setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            t.itemSelectionChanged.connect(self._selection_changed)
        return t

    def _make_footer(self):
        foot = QFrame()
        foot.setObjectName("footer")
        foot.setFixedHeight(50)
        fl = QHBoxLayout(foot)
        fl.setContentsMargins(18, 0, 12, 0)
        self.info = QLabel("")
        self.info.setStyleSheet("font-size: 12px;")
        fl.addWidget(self.info)
        fl.addStretch(1)
        self.pager = QHBoxLayout()
        self.pager.setSpacing(4)
        fl.addLayout(self.pager)
        return foot

    # ---- sizing ---------------------------------------------------------
    def eventFilter(self, obj, ev):
        if obj is self.table.viewport() and ev.type() == QEvent.Type.Resize:
            self._fit_timer.start()
        return super().eventFilter(obj, ev)

    def _fit(self):
        vp = self.table.viewport()
        width = vp.width()
        fixed = sum(c[1] for c in COLS if c[1])
        flex_total = sum(c[2] for c in COLS if c[1] is None)
        free = max(width - fixed, 360)
        for i, (_, w, weight) in enumerate(COLS):
            self.table.setColumnWidth(i, w if w else int(free * weight / flex_total))
        n = max(3, vp.height() // ROW_H)
        if n != self.per_page:
            self.per_page = n
            self.page = 1
        self.refresh()
        self.empty.setGeometry(0, 0, vp.width(), max(vp.height() - 20, 60))

    # ---- data -----------------------------------------------------------
    def _run_search(self):
        self.term = self.search.text()
        self.page = 1
        self.refresh()

    def refresh(self):
        if not self.per_page:
            return
        self.total = db.count_residents(self.term)
        pages = max(1, -(-self.total // self.per_page))
        self.page = min(self.page, pages)
        self.records = db.list_residents(self.term, self.per_page, (self.page - 1) * self.per_page)
        self.table.clearSelection()
        self.table.setRowCount(len(self.records))
        for row, r in enumerate(self.records):
            vals = [db.fmt_id(r["id"]), db.full_name(r), str(db.age_of(r["birth_date"])), r["sex"],
                    r["address"], r["civil_status"], r["contact"], r["occupation"]]
            for col, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setToolTip(v)
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                self.table.setItem(row, col, item)
        if self.total == 0:
            self.empty.setText("No residents found." if self.term else
                               "No residents yet. Use Add New Profile to register the first one.")
            self.empty.show()
        else:
            self.empty.hide()
        first = (self.page - 1) * self.per_page + 1 if self.total else 0
        last = min(self.page * self.per_page, self.total)
        self.info.setText(f"Showing {first} to {last} of {self.total} "
                          f"{'resident' if self.total == 1 else 'residents'}")
        self._build_pager(pages)
        if self.mode == "delete":
            self._selection_changed()

    def _build_pager(self, pages):
        while self.pager.count():
            item = self.pager.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        def btn(text, page, current=False, enabled=True, width=34):
            b = W.button(text, lambda p=page: self._goto(p), "page", width=width, height=30)
            b.setProperty("current", current)
            b.setEnabled(enabled)
            self.pager.addWidget(b)

        btn("Previous", self.page - 1, enabled=self.page > 1, width=78)
        start = max(1, min(self.page - 2, pages - 4))
        for p in range(start, min(pages, start + 4) + 1):
            btn(str(p), p, current=p == self.page)
        btn("Next", self.page + 1, enabled=self.page < pages, width=64)

    def _goto(self, page):
        self.page = page
        self.refresh()

    # ---- row actions ----------------------------------------------------
    def _selected_record(self):
        rows = self.table.selectionModel().selectedRows()
        return self.records[rows[0].row()] if rows and rows[0].row() < len(self.records) else None

    def _selection_changed(self):
        self.del_btn.setEnabled(self._selected_record() is not None)

    def _clicked(self, row, _col):
        if row < len(self.records):
            dialogs.resident_details(self, self.records[row], on_edit=lambda rid:
                                     self.shell.navigate("update", resident_id=rid))

    def _delete(self):
        r = self._selected_record()

        if not r:
            return

        ok = dialogs.ask(
            self,
            "Delete profile?",
            f"{db.full_name(r)} ({db.fmt_id(r['id'])}) will be permanently removed "
            "from the system. This can't be undone.",
            confirm="Delete",
            icon="trash",
            danger=True
        )

        if ok:
            resident_name = db.full_name(r)
            resident_id = db.fmt_id(r["id"])

            user = self.shell.user
            user_id = user.get("id")
            user_name = user.get("full_name", "Unknown User")
            user_role = user.get("role", "Staff")

            db.delete_resident(r["id"])

            db.add_activity(
                user_id,
                user_name,
                user_role,
                "Deleted Resident",
                f"Deleted resident {resident_name} ({resident_id})."
            )

            self.refresh()
