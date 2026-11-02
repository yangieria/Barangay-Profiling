from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget
)

import database as db
import dialogs
import widgets as W


class BackupRestorePage(QWidget):

    def __init__(self, shell):
        super().__init__()

        self.shell = shell
        self.backups = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(
            W.page_header(
                "Backups & Restore",
                "Create and restore backups of the Barangay Profiling System."
            )
        )

        layout.addSpacing(12)

        card = QFrame()
        card.setObjectName("tableCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(
            22,
            20,
            22,
            20
        )
        card_layout.setSpacing(12)

        title = QLabel("AVAILABLE BACKUPS")
        title.setStyleSheet(
            "font-size: 16px;"
            "font-weight: 700;"
        )

        card_layout.addWidget(title)

        self.table = QTableWidget()

        self.table.setColumnCount(3)

        self.table.setHorizontalHeaderLabels([
            "Backup File",
            "Date Created",
            "Status"
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

        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents
        )

        card_layout.addWidget(self.table)

        self.empty = QLabel(
            "No backups available yet."
        )

        self.empty.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.empty.setObjectName("subtitle")

        card_layout.addWidget(self.empty)

        buttons = QHBoxLayout()

        buttons.addStretch(1)

        create_btn = W.button(
            "Create Backup",
            self.create_backup,
            "dark",
            icon="save",
            width=170
        )

        restore_btn = W.button(
            "Restore Selected",
            self.restore_backup,
            "outline",
            width=170
        )

        delete_btn = W.button(
            "Delete Backup",
            self.delete_backup,
            "outline",
            icon="trash",
            width=160
        )

        buttons.addWidget(create_btn)
        buttons.addSpacing(8)
        buttons.addWidget(restore_btn)
        buttons.addSpacing(8)
        buttons.addWidget(delete_btn)

        card_layout.addLayout(buttons)

        layout.addWidget(card, 1)

        self.load_backups()

    def load_backups(self):
        self.backups = db.get_backups()

        self.table.setRowCount(
            len(self.backups)
        )

        if not self.backups:
            self.table.hide()
            self.empty.show()
            return

        self.empty.hide()
        self.table.show()

        for row, backup in enumerate(self.backups):

            created = backup["created_at"].strftime(
                "%B %d, %Y - %I:%M %p"
            )

            values = [
                backup["name"],
                created,
                "Available"
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

    def selected_backup(self):
        row = self.table.currentRow()

        if row < 0:
            dialogs.info(
                self,
                "No backup selected",
                "Please select a backup first."
            )
            return None

        if row >= len(self.backups):
            return None

        return self.backups[row]

    def create_backup(self):
        backup_path = db.create_backup()

        user = self.shell.user

        db.add_activity(
            user.get("id"),
            user.get(
                "full_name",
                "Administrator"
            ),
            user.get(
                "role",
                "Admin"
            ),
            "Created Backup",
            f"Created database backup {backup_path.name}."
        )

        self.load_backups()

        dialogs.info(
            self,
            "Backup created",
            f"Backup created successfully:\n\n{backup_path.name}"
        )

    def restore_backup(self):
        backup = self.selected_backup()

        if not backup:
            return

        ok = dialogs.ask(
            self,
            "Restore backup?",
            f"Restore {backup['name']}?\n\n"
            "The current database will be replaced with the selected backup. "
            "A safety backup of the current database will be created first.",
            confirm="Restore",
            icon="warning",
            danger=True
        )

        if not ok:
            return

        success = db.restore_backup(
            backup["path"]
        )

        if not success:
            dialogs.info(
                self,
                "Restore failed",
                "The selected backup could not be restored.",
                icon="warning",
                danger=True
            )
            return

        user = self.shell.user

        db.add_activity(
            user.get("id"),
            user.get(
                "full_name",
                "Administrator"
            ),
            user.get(
                "role",
                "Admin"
            ),
            "Restored Backup",
            f"Restored database from {backup['name']}."
        )

        self.load_backups()

        dialogs.info(
            self,
            "Backup restored",
            "The backup was restored successfully."
        )

    def delete_backup(self):
        backup = self.selected_backup()

        if not backup:
            return

        ok = dialogs.ask(
            self,
            "Delete backup?",
            f"Delete {backup['name']}?\n\n"
            "This backup file will be permanently deleted.",
            confirm="Delete",
            icon="trash",
            danger=True
        )

        if not ok:
            return

        success = db.delete_backup(
            backup["path"]
        )

        if success:
            user = self.shell.user

            db.add_activity(
                user.get("id"),
                user.get(
                    "full_name",
                    "Administrator"
                ),
                user.get(
                    "role",
                    "Admin"
                ),
                "Deleted Backup",
                f"Deleted backup {backup['name']}."
            )

            self.load_backups()

            dialogs.info(
                self,
                "Backup deleted",
                "The selected backup was deleted."
            )