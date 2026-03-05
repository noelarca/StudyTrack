from PySide6.QtWidgets import (QComboBox, QGroupBox, QFormLayout, QTimeEdit,
                               QDateEdit, QSpinBox, QTextEdit, QPushButton, QMessageBox, QHBoxLayout, QDialog, QVBoxLayout)
from PySide6.QtCore import QDate, QTime

class EntryWidgetBox(QGroupBox):
    def __init__(self, title="Nuovo Inserimento", parent=None, viewmodel=None):
        super().__init__(title, parent)
        self.viewmodel = viewmodel
        self.isEditing = False  # Flag per distinguere tra creazione e modifica
        self.editing_entry_id = None  # Per tenere traccia dell'ID dell'entry in fase di modifica
        
        self.setup_ui()

    def setup_ui(self):
        self.layoutWidget = QFormLayout()
        
        # Selettore della materia
        self.subject_selector = QComboBox()
        self.load_subjects()

        # aggiornamento automatico se il viewmodel emette subjects_changed
        if self.viewmodel is not None and hasattr(self.viewmodel, 'subjects_changed'):
            try:
                self.viewmodel.subjects_changed.connect(self.load_subjects)
            except Exception:
                pass
        
        # Due campi per le ore (con secondi)
        self.time_edit_1 = QTimeEdit()        
        self.time_edit_1.setDisplayFormat("HH:mm:ss")
        self.time_edit_1.setTime(QTime.currentTime())
        
        self.time_edit_2 = QTimeEdit()
        self.time_edit_2.setDisplayFormat("HH:mm:ss")
        self.time_edit_2.setTime(QTime.currentTime().addSecs(7200))
        
        # Campo per la data
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        
        # Selettore da 1 a 5
        self.selector = QSpinBox()
        self.selector.setRange(1, 5)
        self.selector.setValue(3)
        
        # Box per le note
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Inserisci qui le tue note...")
        self.notes_edit.setMaximumHeight(100)

        # Bottoni
        btn_layout = QHBoxLayout()
        self.button = QPushButton("Salva Sessione")
        self.button.clicked.connect(self.on_click)
        
        self.reset_btn = QPushButton("Svuota")
        self.reset_btn.clicked.connect(self.reset_form)
        
        btn_layout.addWidget(self.button)
        btn_layout.addWidget(self.reset_btn)

        # Aggiunta dei widget al layout
        self.layoutWidget.addRow("Materia:", self.subject_selector)
        self.layoutWidget.addRow("Ora Inizio:", self.time_edit_1)
        self.layoutWidget.addRow("Ora Fine:", self.time_edit_2)
        self.layoutWidget.addRow("Data:", self.date_edit)
        self.layoutWidget.addRow("Qualità (1-5):", self.selector)
        self.layoutWidget.addRow("Note:", self.notes_edit)
        self.layoutWidget.addRow(btn_layout)

        self.setLayout(self.layoutWidget)

    def load_subjects(self):
        self.subject_selector.clear()
        if not self.viewmodel:
            return
        subjects = self.viewmodel.get_subjects() or []
        if not subjects:
            self.subject_selector.addItem("-- Nessuna materia --")
            return

        for subj in subjects:
            if isinstance(subj, (tuple, list)) and len(subj) > 1:
                name = subj[1]
            else:
                name = str(subj)
            self.subject_selector.addItem(name)

    def load_entry_for_editing(self, entry_data):
        """Carica i dati di un'entry esistente per la modifica."""
        self.isEditing = True
        self.editing_entry_id = entry_data['id']
        self.setTitle(f"Modifica Inserimento (ID: {self.editing_entry_id})")
        
        # Imposta i valori nei widget
        index = self.subject_selector.findText(entry_data.get('subject_name', ""))
        if index < 0: # fallback
             subject_id = entry_data.get('subject_id')
        
        if index >= 0:
            self.subject_selector.setCurrentIndex(index)
        
        date_str = entry_data.get('date', "")
        if isinstance(date_str, str):
            self.date_edit.setDate(QDate.fromString(date_str, "yyyy-MM-dd"))
            
        start_time_str = entry_data.get('start_time', "")
        if isinstance(start_time_str, str):
            if " " in start_time_str:
                start_time_str = start_time_str.split(" ")[1]
            # Formato HH:mm:ss
            self.time_edit_1.setTime(QTime.fromString(start_time_str[:8], "HH:mm:ss"))

        end_time_str = entry_data.get('end_time', "")
        if isinstance(end_time_str, str):
            if " " in end_time_str:
                end_time_str = end_time_str.split(" ")[1]
            self.time_edit_2.setTime(QTime.fromString(end_time_str[:8], "HH:mm:ss"))

        self.selector.setValue(entry_data.get('quality', 3))
        self.notes_edit.setText(entry_data.get('notes', ""))
        self.button.setText("Aggiorna Sessione")

    def reset_form(self):
        """Resetta il form allo stato di nuovo inserimento."""
        self.isEditing = False
        self.editing_entry_id = None
        self.setTitle("Nuovo Inserimento")
        self.button.setText("Salva Sessione")
        self.date_edit.setDate(QDate.currentDate())
        self.time_edit_1.setTime(QTime.currentTime())
        self.time_edit_2.setTime(QTime.currentTime())
        self.selector.setValue(3)
        self.notes_edit.clear()

    def on_click(self):
        if not self.viewmodel:
            return

        subject = self.subject_selector.currentText()
        if subject == "-- Nessuna materia --":
            QMessageBox.warning(self, "Errore", "Seleziona una materia valida.")
            return

        try:
            if not self.isEditing:
                self.viewmodel.add_entry(
                    subject=subject,
                    date=self.date_edit.date().toString("yyyy-MM-dd"),
                    start_time=self.time_edit_1.time().toString("HH:mm:ss"),
                    end_time=self.time_edit_2.time().toString("HH:mm:ss"),
                    notes=self.notes_edit.toPlainText(),
                    quality=self.selector.value()
                )
                print("Sessione di studio salvata!")
            else:
                self.viewmodel.modify_entry(
                    entry_id=self.editing_entry_id,
                    subject=subject,
                    date=self.date_edit.date().toString("yyyy-MM-dd"),
                    start_time=self.time_edit_1.time().toString("HH:mm:ss"),
                    end_time=self.time_edit_2.time().toString("HH:mm:ss"),
                    notes=self.notes_edit.toPlainText(),
                    quality=self.selector.value()
                )
                print(f"Sessione di studio aggiornata!")
                self.reset_form()
                
        except Exception as e:
            QMessageBox.critical(self, "Errore di salvataggio", str(e))

class EditEntryDialog(QDialog):
    def __init__(self, entry_data, viewmodel, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modifica Sessione di Studio")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        self.entry_box = EntryWidgetBox("Modifica Dettagli", viewmodel=viewmodel)
        self.entry_box.load_entry_for_editing(entry_data)
        
        layout.addWidget(self.entry_box)
        
        # Chiudi se salvato con successo
        self.entry_box.button.clicked.connect(self.check_if_done)

    def check_if_done(self):
        if not self.entry_box.isEditing:
            self.accept()
