from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from ui.components.entry_widget import EntryWidgetBox, EditEntryDialog
from ui.components.last_entries_widget import LastEntriesWidget
from ui.components.sub_grid import SubGrid
from ui.components.stopwatch_widget import StopwatchWidget


class EntryWidget(QWidget):
    def __init__(self, viewmodel):
        super().__init__()
        self.viewmodel = viewmodel
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Study Tracker")
        self.resize(400, 300)

        top_layout = QHBoxLayout()
        main_layout = QVBoxLayout()

        # --- INTEGRAZIONE DEL CRONOMETRO ---
        
        self.stopwatch = StopwatchWidget()
        top_layout.addWidget(self.stopwatch)
        self.stopwatch.session_finished.connect(self.handle_session_finished)

        # --- INTEGRAZIONE DEL WIDGET BOX ---
        # Creiamo un'istanza del widget e la salviamo in self per potervi accedere dopo
        self.study_entry_box = EntryWidgetBox("Dettagli Input", viewmodel=self.viewmodel)
        self.study_entry_box.setMinimumWidth(300)  # Imposta una larghezza minima per il widget
        self.study_entry_box.setMaximumWidth(400)  # Imposta una larghezza massima per il widget

        # Aggiungiamo il widget al layout della finestra principale
        top_layout.addWidget(self.study_entry_box)

        main_layout.addLayout(top_layout)

        # --- INTEGRAZIONE DEL WIDGET DELLE ULTIME ENTRIES ---
        self.last_entries_widget = LastEntriesWidget(viewmodel=self.viewmodel)
        self.last_entries_widget.setMinimumHeight(200)  # Imposta un'altezza minima per il widget
        self.last_entries_widget.setMaximumHeight(300)  # Imposta un'altezza massima per il widget
        self.last_entries_widget.setMinimumWidth(900)  # Imposta una larghezza minima per il widget

        self.last_entries_widget.edit_entry_requested.connect(self.handle_edit_entry)  # Connetti il segnale di richiesta di modifica

        main_layout.addWidget(self.last_entries_widget)

        self.setLayout(main_layout)
    
    def handle_session_finished(self, start_time, end_time):
        # Aggiorna i campi dell'EntryWidgetBox con i tempi del cronometro
        self.study_entry_box.time_edit_1.setTime(start_time)
        self.study_entry_box.time_edit_2.setTime(end_time)
        # Salva automaticamente la sessione
        self.study_entry_box.on_click()

    def save_entry(self, subject, date, start_time, end_time, notes):
        try:
            self.viewmodel.add_entry(subject, date, start_time, end_time, notes)
            self.last_entries_widget.refresh_entries()  # Aggiorna la visualizzazione delle ultime entries
        except ValueError as e:
            print(f"Error saving entry: {e}")

    def handle_edit_entry(self, entry_id):
        try:
            entry_data = self.viewmodel.get_entry_by_id(entry_id)
            if entry_data:
                # Apre una nuova finestra (Dialog) per la modifica
                dialog = EditEntryDialog(entry_data, self.viewmodel, self)
                dialog.exec()
            else:
                print(f"Entry with ID {entry_id} not found.") 
        except Exception as e:
            print(f"Error handling edit entry: {e}")