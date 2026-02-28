from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget,
    QLabel
)
from ui.components.new_sub_window import NewSubjectWindow

class SubSidebar(QWidget):
    # signal emitted when a subject is selected (passes subject name)
    subject_selected = Signal(str)

    def __init__(self, viewmodel=None):
        super().__init__()
        self.viewmodel = viewmodel

        self.layout = QVBoxLayout(self)

        self.title = QLabel("Materie:")

        self.subject_list = QListWidget()
        self.load_subjects()
        self.subject_list.itemClicked.connect(lambda item: self.on_subject_clicked(item))
        # auto-refresh when subjects change
        if self.viewmodel is not None and hasattr(self.viewmodel, 'subjects_changed'):
            try:
                self.viewmodel.subjects_changed.connect(self.load_subjects)
            except Exception:
                pass
        
        self.add_button = QPushButton("Aggiungi materia")
        self.add_button.clicked.connect(self.addsubject)

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.subject_list)
        self.layout.addWidget(self.add_button)

    def load_subjects(self):
        self.subject_list.clear()  # Pulisce la lista prima di ricaricare
        subjects = self.viewmodel.get_subjects()
        if subjects is not None:
            # convert returned subjects into strings for display
            if isinstance(subjects, str):
                subjects = [subjects]
            else:
                subjects = [
                    s[1] if isinstance(s, (tuple, list)) and len(s) > 1 else str(s)
                    for s in subjects
                ]
            self.subject_list.addItems(subjects)

    def addsubject(self):
        # temporary implementation: adds a placeholder subject with default values
        try:
            self.SubWindow = NewSubjectWindow(viewmodel=self.viewmodel)
            self.SubWindow.show()  # Mostra la finestra di aggiunta materia
            # ricaricamento avverrà tramite segnale `subjects_changed` emesso dal ViewModel
        except Exception as e:
            print(f"Error adding subject: {e}")

    def on_subject_clicked(self, item):
        subject = item.text()
        self.viewmodel.select_subject(subject)  # Seleziona la materia nel viewmodel
        # notify listeners about the selection
        self.subject_selected.emit(subject)