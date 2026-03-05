# ui/components/stopwatch_widget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import QTimer, QTime, Qt, Signal

class StopwatchWidget(QWidget):
    # Definiamo un segnale che emette due oggetti QTime (Inizio, Fine)
    session_finished = Signal(QTime, QTime)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        
        self.start_time = None
        self.is_running = False
        self.elapsed_seconds = 0

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 1. Label del Tempo (Grande e visibile)
        self.time_display = QLabel("00:00:00")
        self.time_display.setAlignment(Qt.AlignCenter)
        self.time_display.setStyleSheet("""
            font-size: 48px; 
            font-weight: bold; 
            color: #2c3e50;
            background-color: #ecf0f1;
            border-radius: 10px;
            padding: 10px;
        """)

        # 2. Pulsanti di controllo
        btn_layout = QHBoxLayout()
        
        self.toggle_btn = QPushButton("AVVIA SESSIONE")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white; font-weight: bold; padding: 10px; }
            QPushButton:checked { background-color: #c0392b; }
        """)
        self.toggle_btn.clicked.connect(self.toggle_timer)

        self.reset_btn = QPushButton("RESET")
        self.reset_btn.setStyleSheet("""
            QPushButton { background-color: #7f8c8d; color: white; font-weight: bold; padding: 10px; }
            QPushButton:hover { background-color: #95a5a6; }
        """)
        self.reset_btn.clicked.connect(self.reset_timer)

        btn_layout.addWidget(self.toggle_btn)
        btn_layout.addWidget(self.reset_btn)

        layout.addWidget(self.time_display)
        layout.addLayout(btn_layout)

    def toggle_timer(self):
        if self.toggle_btn.isChecked():
            # --- START ---
            self.is_running = True
            self.start_time = QTime.currentTime() # Registra l'ora esatta di inizio
            self.toggle_btn.setText("FERMA E SALVA")
            self.elapsed_seconds = 0
            self.time_display.setText("00:00:00")
            self.timer.start(1000) # Scatta ogni 1 secondo
        else:
            # --- STOP ---
            self.is_running = False
            self.timer.stop()
            end_time = QTime.currentTime()
            self.toggle_btn.setText("AVVIA SESSIONE")
            
            # Emetti il segnale con i dati per il form principale
            if self.start_time:
                self.session_finished.emit(self.start_time, end_time)

    def reset_timer(self):
        self.is_running = False
        self.timer.stop()
        self.elapsed_seconds = 0
        self.time_display.setText("00:00:00")
        self.start_time = None
        self.toggle_btn.setChecked(False)
        self.toggle_btn.setText("AVVIA SESSIONE")

    def update_display(self):
        self.elapsed_seconds += 1
        # Formattazione manuale HH:MM:SS
        hours = self.elapsed_seconds // 3600
        mins = (self.elapsed_seconds % 3600) // 60
        secs = self.elapsed_seconds % 60
        self.time_display.setText(f"{hours:02}:{mins:02}:{secs:02}")