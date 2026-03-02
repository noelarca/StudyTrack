from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget
)

class SubDetails(QWidget):
    def __init__(self, viewmodel=None):
        super().__init__()
        self.viewmodel = viewmodel

        self.layout = QVBoxLayout(self)

        self.title = QLabel("Dettagli materia:")
        self.details_list = QListWidget()

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.details_list)

    def load_details(self, subject):
        self.details_list.clear()  # Pulisce la lista prima di ricaricare
        details = self.viewmodel.get_subject_details(subject)
        if details:
            for key, value in details.items():
                label = "CFU" if key == "credits" else key.capitalize()
                self.details_list.addItem(f"{label}: {value}")