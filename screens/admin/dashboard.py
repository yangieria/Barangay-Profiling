from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget
)

import database as db
import theme as T
import widgets as W


class AdminDashboard(QWidget):

    def __init__(self, shell):
        super().__init__()

        self.shell = shell

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(
            W.page_header(
                "Admin Dashboard",
                "Overview of the Barangay Profiling System."
            )
        )

        layout.addSpacing(16)

        stats = QHBoxLayout()
        stats.setSpacing(14)

        stats.addWidget(
            self._card(
                "Registered Residents",
                db.count_residents()
            )
        )

        stats.addWidget(
            self._card(
                "Staff Accounts",
                self._staff_count()
            )
        )

        stats.addWidget(
            self._card(
                "Administrators",
                db.count_admins()
            )
        )

        layout.addLayout(stats)
        layout.addStretch(1)

    def _staff_count(self):
        users = db.get_users()

        return sum(
            1
            for user in users
            if user["role"] == "Staff"
        )

    def _card(self, title, value):
        card = QFrame()
        card.setObjectName("statCard")
        card.setFixedHeight(110)

        layout = QVBoxLayout(card)

        layout.setContentsMargins(
            20,
            18,
            20,
            18
        )

        number = QLabel(str(value))

        number.setStyleSheet(
            f"font-size: 30px;"
            f"font-weight: 700;"
            f"color: {T.GREEN_TITLE};"
        )

        label = QLabel(title)
        label.setObjectName("subtitle")

        layout.addWidget(number)
        layout.addWidget(label)

        return card