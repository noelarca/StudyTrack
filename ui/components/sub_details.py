from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, 
    QListWidget, QHBoxLayout, QPushButton
)
from ui.components.new_sub_window import NewSubjectWindow

class SubDetails(QWidget):
    def __init__(self, viewmodel=None):
        super().__init__()
        self.viewmodel = viewmodel
        self.current_subject = None  # Store the currently displayed subject for editing purposes

        self.layout = QVBoxLayout(self)

        option_buttons_layout = QHBoxLayout()

        self.edit_button = QPushButton("Modifica")
        self.edit_button.clicked.connect(self.edit_subject)
        self.delete_button = QPushButton("Elimina")
        self.delete_button.clicked.connect(self.delete_subject) 
        # self.delete_button.clicked.connect(self.delete_subject)  # Placeholder for delete functionality
        option_buttons_layout.addWidget(self.edit_button)
        option_buttons_layout.addWidget(self.delete_button)
        
        self.layout.addLayout(option_buttons_layout)
        

        self.title = QLabel("Dettagli materia:")
        self.details_list = QListWidget()

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.details_list)

    def load_details(self, subject):
        # Accept either an explicit subject or use current_subject
        if subject is None:
            subject = getattr(self, "current_subject", None)
        else:
            self.current_subject = subject

        self.details_list.clear()

        # Determine a name to show in the title
        if isinstance(subject, str):
            name = subject
        elif isinstance(subject, dict):
            name = subject.get("name") or subject.get("title") or str(subject)
        else:
            name = getattr(subject, "name", None) or getattr(subject, "title", None) or str(subject)

        self.title.setText(f"{name}")
        self.title.setStyleSheet("font-weight: bold; font-size: 20px;")

        details = self.viewmodel.get_subject_details(subject) if self.viewmodel else {}
        if details:
            for key, value in details.items():
                label = "CFU" if key == "credits" else key.capitalize()
                self.details_list.addItem(f"{label}: {value}")

    @property
    def subject(self):
        return getattr(self, "current_subject", None)

    @subject.setter
    def subject(self, value):
        if value != getattr(self, "current_subject", None):
            self.current_subject = value
            self.load_details(value)
            if self.viewmodel and hasattr(self.viewmodel, "select_subject"):
                try:
                    self.viewmodel.select_subject(value)
                except Exception:
                    pass

    def edit_subject(self):
        # keep a reference so the window doesn't get garbage collected immediately
        print("Edit subject:", self.current_subject)
        # if there is no subject selected, nothing to edit
        if self.current_subject is None:
            return

        # create/edit window and store it on the instance
        self._edit_window = NewSubjectWindow(viewmodel=self.viewmodel, subject=self.current_subject)
        self._edit_window.show()
        # ensure the window is brought to front
        try:
            self._edit_window.raise_()
            self._edit_window.activateWindow()
        except Exception:
            pass

    def delete_subject(self):
        self.subject_id = self.viewmodel.get_subID_by_name(self.current_subject.get("name")) if self.current_subject else None
        if self.subject_id is None:
            return
        else:
            print("Attempting to delete subject with ID:", self.subject_id)
            self.viewmodel.delete_subject(self.subject_id)