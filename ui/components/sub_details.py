from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget
)
from PySide6.QtGui import QFont

class SubDetails(QWidget):
    def __init__(self, viewmodel=None):
        super().__init__()
        self.viewmodel = viewmodel

        self.layout = QVBoxLayout(self)
        self.details_list = QVBoxLayout()

        self.layout.addWidget(self.title)

    def load_details(self, subject):
        self.title = QLabel()
        self.title.setFont(QFont("Arial", 14, QFont.Bold))
        self.details_list.clear()  # Pulisce la lista prima di ricaricare
        details = self.viewmodel.get_subject_details(subject)
        self.title.setText(f"Dettagli per: {details.get('name', 'N/A')}")