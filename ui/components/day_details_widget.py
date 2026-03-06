from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt

class DayDetailsWidget(QWidget):
    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.date_label = QLabel("Seleziona un giorno")
        self.date_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.date_label)
        
        self.entries_list = QListWidget()
        layout.addWidget(self.entries_list)

    def update_details(self, selected_date):
        date_str = selected_date.toString("yyyy-MM-dd")
        self.date_label.setText(f"Sessioni del {selected_date.toString('dd/MM/yyyy')}")
        
        self.entries_list.clear()
        if not self.viewmodel: return
        
        entries = self.viewmodel.get_entries_by_date(date_str)
        if not entries:
            self.entries_list.addItem("Nessuna sessione registrata per questo giorno.")
            return
            
        for e in entries:
            start = e['start_time'].split(" ")[1] if " " in e['start_time'] else e['start_time']
            end = e['end_time'].split(" ")[1] if " " in e['end_time'] else e['end_time']
            
            item_text = f"[{e['subject_name']}] {start} - {end}\nQualità: {e['quality']}/5"
            if e['notes']:
                item_text += f"\nNote: {e['notes']}"
                
            item = QListWidgetItem(item_text)
            self.entries_list.addItem(item)
