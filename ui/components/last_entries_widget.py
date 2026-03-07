# ui/components/last_entries_widget.py
"""
Widget for displaying a table of the most recent study sessions.
Includes functionality to view, edit, and delete study entries.
"""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHeaderView, QWidget, QVBoxLayout, QPushButton,
    QTableWidget, QLabel, QTableWidgetItem,
    QHBoxLayout, QApplication, QStyle
)

class LastEntriesWidget(QWidget):
    """
    Displays the last 10 study entries in a tabular format.
    
    Signals:
        edit_entry_requested (int): Emitted when the edit button for an entry is clicked.
    """
    edit_entry_requested = Signal(int)

    def __init__(self, viewmodel=None):
        super().__init__()
        self.viewmodel = viewmodel

        self.layout = QVBoxLayout(self)

        self.title = QLabel("Ultime 10 sessioni di studio")
        self.title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addWidget(self.title)

        # Table setup
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Materia", "Data", "Durata", "Qualità", "Note", "Azioni"]
        )

        # Configure column resizing behaviors
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)    # Subject
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Date
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Duration
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Quality
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)           # Notes
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)             # Actions

        # Manual column width adjustments
        self.table.setColumnWidth(3, 50)
        self.table.setColumnWidth(5, 70)
        self.table.setColumnWidth(0, 100)

        self.layout.addWidget(self.table)

        # Refresh button
        self.refresh_button = QPushButton("Aggiorna")
        self.refresh_button.clicked.connect(self.load_entries)
        self.layout.addWidget(self.refresh_button)

        # Listen for data changes in the viewmodel
        if self.viewmodel is not None and hasattr(self.viewmodel, 'entries_changed'):    
            self.viewmodel.entries_changed.connect(self.load_entries)

        self.load_entries()

    def load_entries(self):
        """Fetches recent entries from the viewmodel and populates the table."""
        if self.viewmodel is None:
            return
            
        entries = self.viewmodel.get_last_entries()
        self.table.setRowCount(len(entries))
        
        for i, entry in enumerate(entries):
            # entry structure: (id, subject_name, date, duration, quality, notes)
            self.table.setItem(i, 0, QTableWidgetItem(entry[1]))
            self.table.setItem(i, 1, QTableWidgetItem(entry[2]))
            
            # Format duration from decimal hours to HH:mm:ss
            hours_total = entry[3]
            h = int(hours_total)
            m = int((hours_total - h) * 60)
            s = int(round(((hours_total - h) * 60 - m) * 60))
            if s == 60: s = 0; m += 1
            if m == 60: m = 0; h += 1
            duration_str = f"{h:02}:{m:02}:{s:02}"
            
            self.table.setItem(i, 2, QTableWidgetItem(duration_str))
            self.table.setItem(i, 3, QTableWidgetItem(str(entry[4])))
            self.table.setItem(i, 4, QTableWidgetItem(entry[5]))

            self.table.setRowHeight(i, 40)

            # Create action buttons for each row
            buttons_widget = QWidget()
            button_layout = QHBoxLayout(buttons_widget)
            button_layout.setContentsMargins(2, 2, 2, 2)
            button_layout.setSpacing(4)

            # Delete button
            delete_button = QPushButton()
            delete_button.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
            delete_button.setFixedSize(24, 24)
            delete_button.setToolTip("Elimina sessione")
            delete_button.clicked.connect(lambda _, e=entry: self.delete_entry(e[0]))
            button_layout.addWidget(delete_button)

            # Edit button
            edit_button = QPushButton()
            edit_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
            edit_button.setFixedSize(24, 24)
            edit_button.setToolTip("Modifica sessione")
            edit_button.clicked.connect(lambda _, e=entry: self.edit_entry(e[0]))
            button_layout.addWidget(edit_button)

            self.table.setCellWidget(i, 5, buttons_widget) 

    def delete_entry(self, entry_id):
        """Delegates entry deletion to the viewmodel."""
        if self.viewmodel is not None:
            self.viewmodel.delete_entry(entry_id)
            # Table will be refreshed automatically if entries_changed is connected
    
    def edit_entry(self, entry_id):
        """Emits signal to request editing of a specific entry."""
        self.edit_entry_requested.emit(entry_id)

    def refresh_entries(self):
        """Public method to manually trigger a data reload."""
        self.load_entries()
