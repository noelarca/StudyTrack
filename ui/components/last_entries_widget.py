
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHeaderView, QWidget, QVBoxLayout, QPushButton,
    QTableWidget, QLabel, QTableWidgetItem,
    QHBoxLayout, QApplication, QStyle
)

class LastEntriesWidget(QWidget):
    edit_entry_requested = Signal(int)

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
            ["Materia", "Data", "Durata", "Qualità", "Note", "Azioni"]
        )

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)    # Materia
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Data
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Durata
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)          # Qualità (fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)        # Note (fills remaining)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)          # Azioni (fixed)

        # Apply desired fixed widths AFTER setting resize modes
        self.table.setColumnWidth(3, 40)   # Qualità
        self.table.setColumnWidth(5, 60)   # Azioni (enough for two 24px buttons + margins)
        self.table.setColumnWidth(0, 100)  # Materia

        self.layout.addWidget(self.table)

        # Bottone refresh
        self.refresh_button = QPushButton("Aggiorna")
        self.refresh_button.clicked.connect(self.load_entries)
        self.layout.addWidget(self.refresh_button)

        # Connetti il segnale di aggiornamento del viewmodel
        if self.viewmodel is not None and hasattr(self.viewmodel, 'entries_changed'):    
            self.viewmodel.entries_changed.connect(self.load_entries)

        self.load_entries()

    def load_entries(self):
        if self.viewmodel is None:
            return
        entries = self.viewmodel.get_last_entries()
        self.table.setRowCount(len(entries))
        for i, entry in enumerate(entries):
            self.table.setItem(i, 0, QTableWidgetItem(entry[1]))       # Materia
            self.table.setItem(i, 1, QTableWidgetItem(entry[2]))       # Data
            
            # Formattazione durata HH:mm:ss
            hours_total = entry[3]
            h = int(hours_total)
            m = int((hours_total - h) * 60)
            s = int(round(((hours_total - h) * 60 - m) * 60))
            if s == 60:
                s = 0
                m += 1
            if m == 60:
                m = 0
                h += 1
            duration_str = f"{h:02}:{m:02}:{s:02}"
            
            self.table.setItem(i, 2, QTableWidgetItem(duration_str)) # Durata
            self.table.setItem(i, 3, QTableWidgetItem(str(entry[4]))) # Qualità
            self.table.setItem(i, 4, QTableWidgetItem(entry[5]))       # Note

            self.table.setRowHeight(i, 40)  # Imposta un'altezza fissa per ogni riga

            buttons = QWidget()
            button_layout = QHBoxLayout(buttons)

            buttons.setFixedSize(60, 35)  # Imposta una dimensione fissa per il widget dei bottoni

            delete_button = QPushButton()
            delete_button.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
            delete_button.setFixedSize(24, 24)
            delete_button.clicked.connect(lambda _, e=entry: self.delete_entry(e[0]))
            button_layout.addWidget(delete_button)

            edit_button = QPushButton()
            edit_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
            edit_button.setFixedSize(24, 24)
            button_layout.addWidget(edit_button)
            edit_button.clicked.connect(lambda _, e=entry: self.edit_entry(e[0]))

            self.table.setCellWidget(i, 5, buttons) 

    def delete_entry(self, entry_id):
        if self.viewmodel is not None:
            self.viewmodel.delete_entry(entry_id)
            self.load_entries()  # Aggiorna la tabella dopo l'eliminazione
    
    def edit_entry(self, entry_id):
        # Ad esempio, potresti emettere un segnale o aprire un dialogo di modifica
        self.edit_entry_requested.emit(entry_id)

    def refresh_entries(self):
        self.load_entries()