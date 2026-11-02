from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget
)

import database as db
import widgets as W


class ActivityLogsPage(QWidget):

    def __init__(self, shell):
        super().__init__()

        self.shell = shell

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(
            W.page_header(
                "Activity Logs",
                "View activities performed by system users."
            )
        )

        layout.addSpacing(12)

        card = QFrame()
        card.setObjectName("tableCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(
            12,
            12,
            12,
            12
        )

        self.table = QTableWidget()
        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels([
            "User",
            "Role",
            "Action",
            "Description",
            "Date & Time"
        ])

        self.table.verticalHeader().setVisible(False)

        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.Stretch
        )

        header.setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.ResizeToContents
        )

        card_layout.addWidget(self.table)

        self.empty = QLabel(
            "No activity logs available yet."
        )

        self.empty.setObjectName("subtitle")

        self.empty.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        card_layout.addWidget(self.empty)

        layout.addWidget(card, 1)

        self.load_logs()

    def load_logs(self):
        logs = db.get_activity_logs()

        self.table.setRowCount(len(logs))

        if not logs:
            self.table.hide()
            self.empty.show()
            return

        self.empty.hide()
        self.table.show()

        for row, log in enumerate(logs):
            created_at = log["created_at"]

            try:
                date_part, time_part = created_at.split("T")

                year, month, day = date_part.split("-")

                created_at = (
                    f"{month}/{day}/{year} "
                    f"{time_part}"
                )

            except ValueError:
                pass

            values = [
                log["user_name"],
                log["user_role"],
                log["action"],
                log["description"],
                created_at
            ]

            for column, value in enumerate(values):
                item = QTableWidgetItem(
                    str(value)
                )

                item.setFlags(
                    Qt.ItemFlag.ItemIsEnabled
                    | Qt.ItemFlag.ItemIsSelectable
                )

                self.table.setItem(
                    row,
                    column,
                    item
                )