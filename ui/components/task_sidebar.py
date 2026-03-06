from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget
from PySide6.QtCore import Signal

class TaskSidebar(QWidget):
    subject_selected = Signal(str)

    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 5, 0)
        
        sidebar_label = QLabel("Filtra Materie:")
        sidebar_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(sidebar_label)
        
        self.subject_list = QListWidget()
        self.subject_list.setFixedWidth(180)
        self.subject_list.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.subject_list)

    def on_item_clicked(self, item):
        self.subject_selected.emit(item.text())

    def refresh_subjects(self, current_filter):
        self.subject_list.clear()
        self.subject_list.addItem("Tutte")
        
        subjects = self.viewmodel.get_subjects() if self.viewmodel else []
        for s in subjects:
            name = s[1] if isinstance(s, (tuple, list)) else str(s)
            self.subject_list.addItem(name)
            
        found = False
        for i in range(self.subject_list.count()):
            if self.subject_list.item(i).text() == current_filter:
                self.subject_list.setCurrentRow(i)
                found = True
                break
        if not found:
            self.subject_list.setCurrentRow(0)
            return "Tutte"
        return current_filter

    def current_subject(self):
        item = self.subject_list.currentItem()
        return item.text() if item else "Tutte"

    def count(self):
        return self.subject_list.count()

    def item_text(self, index):
        return self.subject_list.item(index).text()
