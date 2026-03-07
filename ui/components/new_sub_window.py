# ui/components/new_sub_window.py
"""
Window for creating a new subject or editing an existing one.
Handles input validation and interaction with the ViewModel for data persistence.
"""
from PySide6.QtWidgets import (
    QLabel, QLineEdit, QSpinBox, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QListWidget
)
from PySide6.QtCore import QDate, Signal

class NewSubjectWindow(QWidget):
    """
    A dialog-like window for subject entry and modification.
    
    Attributes:
        viewmodel (ViewModel): The business logic controller.
        subject (dict/str/None): Subject data if editing, else None.
        is_editing (bool): Whether the window is in edit mode.
    """
    def __init__(self, viewmodel=None, subject=None):
        super().__init__()
        self.viewmodel = viewmodel
        # subject may be either a name string (from sidebar/details) or a dict with fields
        self.subject = subject
        self.is_completed = False # Track if operation succeeded
        self.is_editing = subject is not None
        # store the numeric id for updates when available
        self._subject_id = None

        # if a name string was passed, try to resolve details via the viewmodel
        if isinstance(subject, str) and self.viewmodel is not None:
            try:
                details = self.viewmodel.get_subject_details(subject)
                # details will be empty dict if lookup failed
                if details:
                    self.subject = details
            except Exception:
                # fallback to keeping the name string only
                pass

        self.setup_ui()

    def setup_ui(self):
        """Initializes the UI layout and widgets."""
        self.layout = QVBoxLayout(self)

        self.title = QLabel("Aggiungi nuova materia:")

        self.nameSubject = QLabel("Nome:")
        self.nameInput = QLineEdit()

        self.semesterSubject = QLabel("Semestre:")
        self.semesterInput = QSpinBox()
        self.semesterInput.setRange(1, 2)  # Limit semester to 1 or 2

        self.yearSubject = QLabel("Anno:")
        self.yearInput = QSpinBox()
        self.yearInput.setRange(0, 5)  # Limit year to a reasonable range
        
        self.creditsSubject = QLabel("CFU:")
        self.creditsInput = QSpinBox()
        self.creditsInput.setRange(0, 60)  # Typical range of exam credits

        self.notesSubject = QLabel("Note:")
        self.notesInput = QLineEdit()

        self.saveButton = QPushButton("Salva")
        self.saveButton.clicked.connect(self.save_subject)

        # Pre-fill fields if editing
        if self.is_editing:
            self.title.setText("Modifica materia:")
            if isinstance(self.subject, dict):
                self._subject_id = self.subject.get("id")
                self.nameInput.setText(self.subject.get("name", ""))
                self.semesterInput.setValue(self.subject.get("semester", 1))
                self.yearInput.setValue(self.subject.get("year", 3))
                self.creditsInput.setValue(self.subject.get("credits", 0))
                self.notesInput.setText(self.subject.get("notes", ""))
            else:
                # only have a name; set it and leave the rest defaults
                self.nameInput.setText(str(self.subject))
                self.semesterInput.setValue(1)
                self.yearInput.setValue(3)
                self.creditsInput.setValue(0)
        else:
            # Default values for new subjects
            self.semesterInput.setValue(1)
            self.yearInput.setValue(3)
            self.creditsInput.setValue(0)

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.nameSubject)
        self.layout.addWidget(self.nameInput)
        self.layout.addWidget(self.semesterSubject)
        self.layout.addWidget(self.semesterInput)
        self.layout.addWidget(self.yearSubject)
        self.layout.addWidget(self.yearInput)
        self.layout.addWidget(self.creditsSubject)
        self.layout.addWidget(self.creditsInput)
        self.layout.addWidget(self.notesSubject)
        self.layout.addWidget(self.notesInput)
        self.layout.addWidget(self.saveButton)

        self.setWindowTitle("Gestione Materia")
        self.setMinimumSize(400, 300)

    def save_subject(self):
        """Gathers input data and calls the viewmodel to save or update the subject."""
        name = self.nameInput.text()
        semester = self.semesterInput.value()
        year = self.yearInput.value()
        credits = self.creditsInput.value()
        notes = self.notesInput.text()
        
        if not name.strip():
            # Basic validation: name is required
            return

        try:
            if self.viewmodel is not None:
                if self.is_editing:
                    # update requires an identifier; try using stored id first
                    subj_id = self._subject_id
                    if subj_id is None:
                        # fall back to looking up by original name
                        try:
                            details = self.viewmodel.get_subject_details(self.subject)
                            subj_id = details.get("id") if isinstance(details, dict) else None
                        except Exception:
                            subj_id = None
                    if subj_id is None:
                        raise ValueError("Cannot determine subject ID for update")
                    self.viewmodel.update_subject(subj_id, name, semester, year, credits, notes)
                else:
                    self.viewmodel.add_subject(name, semester, year, credits, notes)
            self.close()
        except Exception as e:
            # Error handling could be improved with a message box
            print(f"Error saving subject: {e}")
