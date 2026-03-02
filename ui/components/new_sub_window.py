from PySide6.QtWidgets import (
    QLabel, QLineEdit, QSpinBox, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QListWidget
)
from PySide6.QtCore import QDate, Signal

class NewSubjectWindow(QWidget):
    def __init__(self, viewmodel=None, subject=None):
        super().__init__()
        self.viewmodel = viewmodel
        # subject may be either a name string (from sidebar/details) or a dict with fields
        self.subject = subject
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

        self.layout = QVBoxLayout(self)

        self.title = QLabel("Aggiungi nuova materia:")

        self.nameSubject = QLabel("Nome:")
        self.nameInput = QLineEdit()

        self.semesterSubject = QLabel("Semestre:")
        self.semesterInput = QSpinBox()
        self.semesterInput.setRange(1, 2)  # Limita il semestre a 1 o 2

        self.yearSubject = QLabel("Anno:")
        self.yearInput = QSpinBox()
        self.yearInput.setRange(0,5)  # Limita l'anno a un intervallo ragionevole
        
        self.creditsSubject = QLabel("CFU:")
        self.creditsInput = QSpinBox()
        self.creditsInput.setRange(0, 60)  # range of exam credits

        self.notesSubject = QLabel("Note:")
        self.notesInput = QLineEdit()

        self.saveButton = QPushButton("Salva")
        self.saveButton.clicked.connect(self.save_subject)

        if self.is_editing:
            # if subject is a dict we can pull fields, otherwise we only have name
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
            self.semesterInput.setValue(1)  # Imposta il semestre di default a 1
            self.yearInput.setValue(3)  # Imposta l'anno di default a quello corrente
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

        self.setWindowTitle("Aggiungi Materia")
        self.setMinimumSize(400, 100)  # Imposta una dimensione minima per la finestra

    def save_subject(self):
        name = self.nameInput.text()
        semester = self.semesterInput.value()
        year = self.yearInput.value()
        credits = self.creditsInput.value()
        notes = self.notesInput.text()
        try:
            # delegate to viewmodel (which will emit subjects_changed)
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
                        # if we still don't have an id, raise so user knows
                        raise ValueError("Cannot determine subject ID for update")
                    self.viewmodel.update_subject(subj_id, name, semester, year, credits, notes)
                else:
                    self.viewmodel.add_subject(name, semester, year, credits, notes)
            self.close()
        except Exception as e:
            print(f"Error saving subject: {e}")