from PyQt6.QtWidgets import QVBoxLayout, QWidget

import widgets as W

from screens.table import ResidentsTable


class AdminResidents(QWidget):

    def __init__(self, shell):
        super().__init__()

        self.shell = shell

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(
            W.page_header(
                "Residents Profile",
                "View all registered barangay residents."
            )
        )

        layout.addSpacing(12)

        self.table = ResidentsTable(
            shell,
            "view"
        )

        layout.addWidget(
            self.table,
            1
        )