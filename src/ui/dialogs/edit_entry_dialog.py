from PySide6.QtWidgets import QDialog, QVBoxLayout
from ui.components.entry.entry_widget import EntryWidgetBox

class EditEntryDialog(QDialog):
    """
    A dialog wrapper for EntryWidgetBox used when editing entries from lists or calendars.
    """
    def __init__(self, entry_data, viewmodel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.setWindowTitle("Modifica Sessione di Studio")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        self.entry_box = EntryWidgetBox("Modifica Dettagli", viewmodel=self.viewmodel)
        self.entry_box.load_entry_for_editing(entry_data)
        
        layout.addWidget(self.entry_box)
        
        # Close the dialog if the user successfully saves (which resets the box state)
        self.entry_box.button.clicked.connect(self.check_if_done)

    def check_if_done(self):
        """Closes the dialog only if the operation was successful (reset triggered)."""
        if not self.entry_box.is_editing:
            self.accept()
