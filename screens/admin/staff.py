from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
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
import theme as T
import widgets as W


class StaffAccountsPage(QWidget):

    def __init__(self, shell):
        super().__init__()

        self.shell = shell
        self.user = shell.user

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        lay.addWidget(
            W.page_header(
                "Staff Accounts",
                "Manage staff accounts and administrator access."
            )
        )

        lay.addSpacing(12)

        card = QFrame()
        card.setObjectName("tableCard")

        card_lay = QVBoxLayout(card)

        card_lay.setContentsMargins(
            22,
            18,
            22,
            18
        )

        title = QLabel(
            "ACCOUNT MANAGEMENT"
        )

        title.setStyleSheet(
            f"font-size: 17px;"
            f"font-weight: 700;"
            f"color: {T.GREEN_TITLE};"
        )

        card_lay.addWidget(title)

        self.table = QTableWidget()

        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Full Name",
            "Email",
            "Role",
            "Action"
        ])

        self.table.verticalHeader().setVisible(
            False
        )

        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection
        )

        self.table.setShowGrid(False)
        self.table.setFocusPolicy(
            Qt.FocusPolicy.NoFocus
        )

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Stretch
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.ResizeToContents
        )

        card_lay.addWidget(self.table)

        lay.addWidget(card, 1)

        self.refresh()

    def refresh(self):
        users = db.get_users()

        self.table.setRowCount(
            len(users)
        )

        for row, user in enumerate(users):
            item = QTableWidgetItem(
                f"{user['id']:03d}"
            )

            item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            self.table.setItem(
                row,
                0,
                item
            )

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(
                    user["full_name"]
                )
            )

            self.table.setItem(
                row,
                2,
                QTableWidgetItem(
                    user["email"]
                )
            )

            role = QComboBox()

            role.addItems([
                "Admin",
                "Staff"
            ])

            role.setCurrentText(
                user["role"]
            )

            role.setFixedWidth(120)
            role.setFixedHeight(36)

            if user["id"] == self.user["id"]:
                role.setEnabled(False)
            else:
                role.currentTextChanged.connect(
                    lambda new_role,
                    uid=user["id"]:
                    self.change_role(
                        uid,
                        new_role
                    )
                )

            role_box = QWidget()

            role_layout = QHBoxLayout(
                role_box
            )

            role_layout.setContentsMargins(
                5,
                2,
                5,
                2
            )

            role_layout.addWidget(role)

            self.table.setCellWidget(
                row,
                3,
                role_box
            )

            if user["id"] == self.user["id"]:
                current = QLabel(
                    "Current User"
                )

                current.setAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                self.table.setCellWidget(
                    row,
                    4,
                    current
                )

            else:
                delete = W.button(
                    "Delete",
                    lambda checked=False,
                    uid=user["id"]:
                    self.delete_user(uid),
                    "danger",
                    icon="trash",
                    width=110,
                    height=36
                )

                action = QWidget()

                action_layout = QHBoxLayout(
                    action
                )

                action_layout.setContentsMargins(
                    5,
                    2,
                    5,
                    2
                )

                action_layout.addWidget(delete)

                self.table.setCellWidget(
                    row,
                    4,
                    action
                )

            self.table.setRowHeight(
                row,
                48
            )

    def change_role(
        self,
        user_id,
        new_role
    ):
        user = db.get_user(user_id)

        if not user:
            return

        if user["role"] == new_role:
            return

        if (
            user["role"] == "Admin"
            and new_role == "Staff"
            and db.count_admins() <= 1
        ):
            dialogs.info(
                self,
                "Admin Required",
                "The system must have at least one administrator.",
                icon="warning",
                danger=True
            )

            self.refresh()
            return

        ok = dialogs.ask(
            self,
            "Change Account Role?",
            f"Change {user['full_name']}'s role to {new_role}?",
            confirm="Change Role",
            icon="person"
        )

        if not ok:
            self.refresh()
            return

        db.update_user_role(
            user_id,
            new_role
        )

        dialogs.info(
            self,
            "Role Updated",
            f"{user['full_name']} is now {new_role}."
        )

        self.refresh()

    def delete_user(
        self,
        user_id
    ):
        if user_id == self.user["id"]:
            return

        user = db.get_user(user_id)

        if not user:
            return

        if (
            user["role"] == "Admin"
            and db.count_admins() <= 1
        ):
            dialogs.info(
                self,
                "Admin Required",
                "The last administrator account cannot be deleted.",
                icon="warning",
                danger=True
            )

            return

        ok = dialogs.ask(
            self,
            "Delete Account?",
            f"{user['full_name']}'s account will be permanently deleted.",
            confirm="Delete",
            icon="trash",
            danger=True
        )

        if not ok:
            return

        db.delete_user(user_id)

        dialogs.info(
            self,
            "Account Deleted",
            f"{user['full_name']}'s account has been deleted."
        )

        self.refresh()