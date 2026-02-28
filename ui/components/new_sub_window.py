from PySide6.QtWidgets import (
    QLabel, QLineEdit, QSpinBox, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QListWidget
)
from PySide6.QtCore import QDate, Signal

class NewSubjectWindow(QWidget):
    def __init__(self, viewmodel=None):
        super().__init__()
        self.viewmodel = viewmodel


        self.layout = QVBoxLayout(self)

        self.title = QLabel("Aggiungi nuova materia:")

        self.nameSubject = QLabel("Nome:")
        self.nameInput = QLineEdit()

        self.semesterSubject = QLabel("Semestre:")
        self.semesterInput = QSpinBox()
        self.semesterInput.setRange(1, 2)  # Limita il semestre a 1 o 2
        self.semesterInput.setValue(1)  # Imposta il semestre di default a 1

        self.yearSubject = QLabel("Anno:")
        self.yearInput = QSpinBox()
        self.yearInput.setRange(2000, 2100)  # Limita l'anno a un intervallo ragionevole
        self.yearInput.setValue(QDate.currentDate().year())  # Imposta l'anno di default a quello corrente

        self.creditsSubject = QLabel("CFU:")
        self.creditsInput = QSpinBox()
        self.creditsInput.setRange(0, 60)  # range of exam credits
        self.creditsInput.setValue(0)

        self.notesSubject = QLabel("Note:")
        self.notesInput = QLineEdit()

        self.saveButton = QPushButton("Salva")
        self.saveButton.clicked.connect(self.save_subject)

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
            # delega al viewmodel (che emetterà il segnale subjects_changed)
            if self.viewmodel is not None:
                self.viewmodel.add_subject(name, semester, year, credits, notes)
            self.close()
        except Exception as e:
                print(f"Error saving subject: {e}")