from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from ui.components.entry_widget import EntryWidgetBox
from ui.components.last_entries_widget import LastEntriesWidget
from ui.components.sub_grid import SubGrid


class EntryWidget(QWidget):
    def __init__(self, viewmodel):
        super().__init__()
        self.viewmodel = viewmodel
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Study Tracker")
        self.resize(400, 300)

        toplayout = QHBoxLayout()
        mainLayout = QHBoxLayout()

        # --- INTEGRAZIONE DEL WIDGET BOX ---
        # Creiamo un'istanza del widget e la salviamo in self per potervi accedere dopo
        self.study_entry_box = EntryWidgetBox("Dettagli Input", viewmodel=self.viewmodel)
        self.study_entry_box.setMinimumWidth(300)  # Imposta una larghezza minima per il widget
        self.study_entry_box.setMaximumWidth(400)  # Imposta una larghezza massima per il widget

        # Aggiungiamo il widget al layout della finestra principale
        toplayout.addWidget(self.study_entry_box)

        mainLayout.addLayout(toplayout)

        # --- INTEGRAZIONE DEL WIDGET DELLE ULTIME ENTRIES ---
        self.last_entries_widget = LastEntriesWidget(viewmodel=self.viewmodel)
        self.last_entries_widget.setMinimumHeight(200)  # Imposta un'altezza minima per il widget
        self.last_entries_widget.setMaximumHeight(300)  # Imposta un'altezza massima per il widget
        self.last_entries_widget.setMinimumWidth(900)  # Imposta una larghezza minima per il widget

        mainLayout.addWidget(self.last_entries_widget)

        self.setLayout(mainLayout)
    
    def save_entry(self, subject, date, start_time, end_time, notes):
        try:
            self.viewmodel.add_entry(subject, date, start_time, end_time, notes)
            self.last_entries_widget.refresh_entries()  # Aggiorna la visualizzazione delle ultime entries
        except ValueError as e:
            print(f"Error saving entry: {e}")