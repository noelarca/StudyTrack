# ui/components/entry_widget.py
"""
Widgets for manual entry and modification of study sessions.
Includes a form-based group box and a dialog wrapper for editing existing entries.
"""
from PySide6.QtWidgets import (QComboBox, QGroupBox, QFormLayout, QTimeEdit,
                               QDateEdit, QSpinBox, QTextEdit, QPushButton, QMessageBox, QHBoxLayout, QVBoxLayout)
from PySide6.QtCore import QDate, QTime, Qt

class EntryWidgetBox(QGroupBox):
    """
    A form for entering or editing study session details.
    
    Attributes:
        viewmodel (ViewModel): The business logic controller.
        is_editing (bool): True if currently editing an existing entry.
        editing_entry_id (int): ID of the entry being edited.
    """
    def __init__(self, title="Nuovo Inserimento", parent=None, viewmodel=None):
        super().__init__(title, parent)
        self.viewmodel = viewmodel
        self.is_editing = False
        self.editing_entry_id = None
        
        self.setup_ui()

    def setup_ui(self):
        """Initializes the form layout and widgets."""
        self.layout = QFormLayout()
        
        # Subject selection
        self.subject_selector = QComboBox()
        self.load_subjects()

        # Connect to viewmodel signals for dynamic subject list updates
        if self.viewmodel is not None and hasattr(self.viewmodel, 'subjects_changed'):
            try:
                self.viewmodel.subjects_changed.connect(self.load_subjects, Qt.QueuedConnection)
            except Exception:
                pass
        
        # Session time range
        self.time_edit_1 = QTimeEdit()        
        self.time_edit_1.setDisplayFormat("HH:mm:ss")
        self.time_edit_1.setTime(QTime.currentTime())
        
        self.time_edit_2 = QTimeEdit()
        self.time_edit_2.setDisplayFormat("HH:mm:ss")
        self.time_edit_2.setTime(QTime.currentTime().addSecs(7200)) # Default 2 hour duration
        
        # Session date
        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        
        # Subjective quality rating
        self.selector = QSpinBox()
        self.selector.setRange(1, 5)
        self.selector.setValue(3)
        
        # Session notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Inserisci qui le tue note...")
        self.notes_edit.setMaximumHeight(100)

        # Control buttons
        btn_layout = QHBoxLayout()
        self.button = QPushButton("Salva Sessione")
        self.button.clicked.connect(self.on_click)
        
        self.reset_btn = QPushButton("Svuota")
        self.reset_btn.clicked.connect(self.reset_form)
        
        btn_layout.addWidget(self.button)
        btn_layout.addWidget(self.reset_btn)

        # Add rows to the form layout
        self.layout.addRow("Materia:", self.subject_selector)
        self.layout.addRow("Ora Inizio:", self.time_edit_1)
        self.layout.addRow("Ora Fine:", self.time_edit_2)
        self.layout.addRow("Data:", self.date_edit)
        self.layout.addRow("Qualità (1-5):", self.selector)
        self.layout.addRow("Note:", self.notes_edit)
        self.layout.addRow(btn_layout)

        self.setLayout(self.layout)

    def load_subjects(self):
        """Reloads the subject list from the viewmodel."""
        self.subject_selector.clear()
        if not self.viewmodel:
            return
        subjects = self.viewmodel.get_subjects() or []
        if not subjects:
            self.subject_selector.addItem("-- Nessuna materia --")
            return

        for subj in subjects:
            # Handle tuple/list format (id, name, ...)
            name = subj[1] if isinstance(subj, (tuple, list)) and len(subj) > 1 else str(subj)
            self.subject_selector.addItem(name)

    def load_entry_for_editing(self, entry_data):
        """
        Populates the form with data from an existing entry.
        
        Args:
            entry_data (dict): Dictionary containing entry details.
        """
        self.is_editing = True
        self.editing_entry_id = entry_data['id']
        self.setTitle(f"Modifica Inserimento (ID: {self.editing_entry_id})")
        
        # Set subject
        index = self.subject_selector.findText(entry_data.get('subject_name', ""))
        if index >= 0:
            self.subject_selector.setCurrentIndex(index)
        
        # Set date
        date_str = entry_data.get('date', "")
        if isinstance(date_str, str):
            self.date_edit.setDate(QDate.fromString(date_str, "yyyy-MM-dd"))
            
        # Set start and end times (parsing from string format)
        start_time_str = entry_data.get('start_time', "")
        if isinstance(start_time_str, str):
            if " " in start_time_str: start_time_str = start_time_str.split(" ")[1]
            self.time_edit_1.setTime(QTime.fromString(start_time_str[:8], "HH:mm:ss"))

        end_time_str = entry_data.get('end_time', "")
        if isinstance(end_time_str, str):
            if " " in end_time_str: end_time_str = end_time_str.split(" ")[1]
            self.time_edit_2.setTime(QTime.fromString(end_time_str[:8], "HH:mm:ss"))

        self.selector.setValue(entry_data.get('quality', 3))
        self.notes_edit.setText(entry_data.get('notes', ""))
        self.button.setText("Aggiorna Sessione")

    def reset_form(self):
        """Resets the form to default 'new entry' state."""
        self.is_editing = False
        self.editing_entry_id = None
        self.setTitle("Nuovo Inserimento")
        self.button.setText("Salva Sessione")
        self.date_edit.setDate(QDate.currentDate())
        self.time_edit_1.setTime(QTime.currentTime())
        self.time_edit_2.setTime(QTime.currentTime())
        self.selector.setValue(3)
        self.notes_edit.clear()

    def on_click(self):
        """Handles the save/update button click."""
        if not self.viewmodel:
            return

        subject = self.subject_selector.currentText()
        if subject == "-- Nessuna materia --":
            QMessageBox.warning(self, "Errore", "Seleziona una materia valida.")
            return

        try:
            if not self.is_editing:
                self.viewmodel.add_entry(
                    subject=subject,
                    date=self.date_edit.date().toString("yyyy-MM-dd"),
                    start_time=self.time_edit_1.time().toString("HH:mm:ss"),
                    end_time=self.time_edit_2.time().toString("HH:mm:ss"),
                    notes=self.notes_edit.toPlainText(),
                    quality=self.selector.value()
                )
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
                self.reset_form()
                
        except Exception as e:
            QMessageBox.critical(self, "Errore di salvataggio", str(e))
