from PySide6.QtWidgets import (QComboBox, QGroupBox, QFormLayout, QTimeEdit,
                               QDateEdit, QSpinBox, QTextEdit, QPushButton)
from PySide6.QtCore import QDate, QTime

class EntryWidgetBox(QGroupBox):
    def __init__(self, title="Nuovo Inserimento", parent=None, viewmodel=None):
        super().__init__(title, parent)
        self.viewmodel = viewmodel
        
        # Utilizziamo un FormLayout per un allineamento pulito Etichetta/Campo
        layoutWidget = QFormLayout()
        
        # Selettore della materia
        self.subject_selector = QComboBox()
        self.load_subjects()
        # aggiornamento automatico se il viewmodel emette subjects_changed
        if self.viewmodel is not None and hasattr(self.viewmodel, 'subjects_changed'):
            try:
                self.viewmodel.subjects_changed.connect(self.load_subjects)
            except Exception:
                pass
        
        # Due campi per le ore (es. Inizio e Fine)
        self.time_edit_1 = QTimeEdit()
        self.time_edit_1.setTime(QTime.currentTime()) # Imposta l'ora attuale di default
        
        self.time_edit_2 = QTimeEdit()
        self.time_edit_2.setTime(QTime.currentTime().addSecs(7200)) # +2 ore di default
        
        # Campo per la data
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True) # Mostra un calendario a tendina
        
        # Selettore da 1 a 5
        self.selector = QSpinBox()
        self.selector.setRange(1, 5)
        self.selector.setValue(3)
        
        # Box per le note (testo multiriga)
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Inserisci qui le tue note...")
        self.notes_edit.setMaximumHeight(100) # Limita l'altezza per non occupare troppo spazio

        # Aggiunta di un pulsante per salvare o inviare i dati
        self.button = QPushButton("Salva Sessione")
        self.button.clicked.connect(self.on_click)

        # Aggiunta dei widget al layout con le rispettive etichette
        layoutWidget.addRow("Materia:", self.subject_selector)
        layoutWidget.addRow("Ora Inizio:", self.time_edit_1)
        layoutWidget.addRow("Ora Fine:", self.time_edit_2)
        layoutWidget.addRow("Data:", self.date_edit)
        layoutWidget.addRow("Qualità (1-5):", self.selector)
        layoutWidget.addRow("Note:", self.notes_edit)
        layoutWidget.addRow(self.button) # Aggiungiamo il pulsante alla fine del form

        self.setLayout(layoutWidget)

    def load_subjects(self):
        # carica le materie dal viewmodel e aggiorna il combobox
        self.subject_selector.clear()
        if not self.viewmodel:
            return
        subjects = self.viewmodel.get_subjects() or []
        if isinstance(subjects, str):
            subjects = [subjects]
        if not subjects:
            self.subject_selector.addItem("-- Nessuna materia --")
            return

        for subj in subjects:
            # supporta tuple/list (id, name) e stringhe
            if isinstance(subj, (tuple, list)) and len(subj) > 1:
                name = subj[1]
            else:
                name = str(subj)
            self.subject_selector.addItem(name)

    def on_click(self):
        # Chiamiamo il metodo del viewmodel per salvare l'entry
        if self.viewmodel:
            self.viewmodel.add_entry(
                subject=self.subject_selector.currentText(),
                date=self.date_edit.date().toString("yyyy-MM-dd"),
                start_time=self.time_edit_1.time().toString("HH:mm"),
                end_time=self.time_edit_2.time().toString("HH:mm"),
                notes=self.notes_edit.toPlainText(),
                quality=self.selector.value()
            )

        print("Sessione di studio salvata!")
        print("Ora Inizio:", self.time_edit_1.time().toString())
        print("Ora Fine:", self.time_edit_2.time().toString())
        print("Data:", self.date_edit.date().toString())
        print("Qualità:", self.selector.value())
        print("Note:", self.notes_edit.toPlainText())

