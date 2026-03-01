
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QTableWidget, QLabel, QTableWidgetItem
)

class LastEntriesWidget(QWidget):
    def __init__(self, viewmodel=None):
        super().__init__()
        self.viewmodel = viewmodel

        self.layout = QVBoxLayout(self)

        self.title = QLabel("Ultime 10 sessioni di studio")
        self.layout.addWidget(self.title)

        # Tabella
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Materia", "Data", "Durata (min)", "Qualità", "Note"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.layout.addWidget(self.table)

        # Bottone refresh
        self.refresh_button = QPushButton("Aggiorna")
        self.refresh_button.clicked.connect(self.load_entries)
        self.layout.addWidget(self.refresh_button)
        # connect to viewmodel entries_changed to auto-refresh
        if self.viewmodel is not None and hasattr(self.viewmodel, 'entries_changed'):
            try:
                self.viewmodel.entries_changed.connect(self.load_entries)
            except Exception:
                pass

        self.load_entries()

    def load_entries(self):
        if self.viewmodel is None:
            return
        entries = self.viewmodel.get_last_entries()
        self.table.setRowCount(len(entries))
        for i, entry in enumerate(entries):
            self.table.setItem(i, 0, QTableWidgetItem(str(entry[0])))  # ID
            self.table.setItem(i, 1, QTableWidgetItem(entry[1]))       # Materia
            self.table.setItem(i, 2, QTableWidgetItem(entry[2]))       # Data
            self.table.setItem(i, 3, QTableWidgetItem(str(round(entry[3], 2)))) # Durata (min)
            self.table.setItem(i, 4, QTableWidgetItem(str(entry[4]))) # Qualità
            self.table.setItem(i, 5, QTableWidgetItem(entry[5]))       # Note

    def refresh_entries(self):
        self.load_entries()