import sys
from PySide6.QtWidgets import QButtonGroup, QGridLayout, QWidget, QPushButton


class SubGrid(QWidget):
    def __init__(self, title: str = "Materie", viewmodel=None, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel

        self.layout = QGridLayout(self)

        # Creo un gruppo di pulsanti per le materie
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)  # Solo un pulsante può essere selezionato alla volta

        positions = [(i, j) for i in range(10) for j in range(2)]  # Posizioni per i pulsanti (2 colonne, 10 righe)

        # Estraggo le materie uniche dal database
        if self.viewmodel is None:
            print("SubGrid: viewmodel is None, cannot load subjects")
            self.subs = []
        else:
            try:
                self.subs = self.viewmodel.get_subjects()
            except Exception as e:
                print(f"Errore durante il caricamento delle materie: {e}")
                self.subs = []

        if self.subs is None:
            self.subs = []

        # populate buttons initially
        self._populate_buttons()

        # connect to subjects_changed to refresh grid when subjects update
        if self.viewmodel is not None and hasattr(self.viewmodel, 'subjects_changed'):
            try:
                self.viewmodel.subjects_changed.connect(self.refresh_grid)
            except Exception:
                pass


    def on_sub_clicked(self, sub):
        # normalize returned value to the subject name string
        if isinstance(sub, (tuple, list)) and len(sub) > 1:
            return sub[1]
        return str(sub)

    def _populate_buttons(self):
        # helper to add buttons to the grid
        # clear any previous placeholder
        # (we assume layout is empty at first call)
        if not self.subs:
            button = QPushButton("Nessuna materia disponibile")
            button.setEnabled(False)
            self.layout.addWidget(button)
            self.button_group.addButton(button)
            return

        for sub in self.subs:
            if isinstance(sub, (tuple, list)) and len(sub) > 1:
                name = sub[1]
            else:
                name = str(sub)
            button = QPushButton(name)
            button.clicked.connect(lambda checked, s=sub: self.on_sub_clicked(s))
            button.setCheckable(True)
            button.setMinimumHeight(20)
            button.setMaximumWidth(100)
            self.layout.addWidget(button)
            self.button_group.addButton(button)

    def refresh_grid(self):
        # remove all widgets from layout
        while self.layout.count():
            item = self.layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)

        # reload subjects and rebuild
        try:
            self.subs = self.viewmodel.get_subjects() or []
        except Exception:
            self.subs = []
        self._populate_buttons()
