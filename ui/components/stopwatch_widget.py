# ui/components/stopwatch_widget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QComboBox
from PySide6.QtCore import QTimer, QTime, Qt, Signal

class StopwatchWidget(QWidget):
    # Emits (StartTime, EndTime)
    session_finished = Signal(QTime, QTime)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        
        self.start_time = None
        self.is_running = False
        self.elapsed_seconds = 0
        
        # Pomodoro specific state
        self.mode = "Stopwatch" # "Stopwatch" or "Pomodoro"
        self.pomodoro_phase = "Work" # "Work" or "Break"
        self.remaining_seconds = 25 * 60 # Default Pomodoro work time
        self.work_duration = 25 * 60
        self.break_duration = 5 * 60

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 0. Mode Selector
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Modalità:")
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Cronometro Standard", "Pomodoro (25/5)"])
        self.mode_selector.currentIndexChanged.connect(self.change_mode)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_selector)
        layout.addLayout(mode_layout)

        # 1. Phase Label (for Pomodoro)
        self.phase_label = QLabel("SESSIONE STANDARD")
        self.phase_label.setAlignment(Qt.AlignCenter)
        self.phase_label.setFixedHeight(20) # Fixed height
        self.phase_label.setStyleSheet("font-weight: bold; color: #7f8c8d;")
        layout.addWidget(self.phase_label)

        # 2. Time Display
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
        layout.addWidget(self.time_display)

        # 3. Control Buttons
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
        layout.addLayout(btn_layout)

    def change_mode(self, index):
        if self.is_running:
             self.reset_timer()
        
        if index == 0:
            self.mode = "Stopwatch"
            self.phase_label.setText("SESSIONE STANDARD")
            self.time_display.setText("00:00:00")
            self.phase_label.setStyleSheet("font-weight: bold; color: #7f8c8d;")
        else:
            self.mode = "Pomodoro"
            self.pomodoro_phase = "Work"
            self.remaining_seconds = self.work_duration
            self.update_display()
            self.phase_label.setText("POMODORO: STUDIO")
            self.phase_label.setStyleSheet("font-weight: bold; color: #e67e22;")

    def toggle_timer(self):
        if self.toggle_btn.isChecked():
            # --- START ---
            self.is_running = True
            self.start_time = QTime.currentTime()
            
            if self.mode == "Stopwatch":
                self.toggle_btn.setText("FERMA E SALVA")
                self.elapsed_seconds = 0
            else:
                self.toggle_btn.setText("INTERROMPI")
                # Reset to full duration if we just started
                if self.pomodoro_phase == "Work":
                    self.remaining_seconds = self.work_duration
                else:
                    self.remaining_seconds = self.break_duration
            
            self.timer.start(1000)
            self.mode_selector.setEnabled(False)
        else:
            # --- STOP ---
            self.stop_timer(manual=True)

    def stop_timer(self, manual=False):
        self.is_running = False
        self.timer.stop()
        self.mode_selector.setEnabled(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.setText("AVVIA SESSIONE")
        
        end_time = QTime.currentTime()
        
        # For Stopwatch, we always save.
        # For Pomodoro, we save if a Work session was interrupted or finished.
        if self.mode == "Stopwatch":
            if self.start_time:
                self.session_finished.emit(self.start_time, end_time)
        elif self.mode == "Pomodoro" and self.pomodoro_phase == "Work":
            if self.start_time:
                # If finished naturally, the duration is work_duration. 
                # If manual stop, it's the actual elapsed time.
                if not manual:
                    # Logic for natural end
                    actual_start = end_time.addSecs(-self.work_duration)
                    self.session_finished.emit(actual_start, end_time)
                else:
                    self.session_finished.emit(self.start_time, end_time)

    def reset_timer(self):
        self.is_running = False
        self.timer.stop()
        self.mode_selector.setEnabled(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.setText("AVVIA SESSIONE")
        self.start_time = None
        
        if self.mode == "Stopwatch":
            self.elapsed_seconds = 0
            self.time_display.setText("00:00:00")
        else:
            self.pomodoro_phase = "Work"
            self.remaining_seconds = self.work_duration
            self.update_display()
            self.phase_label.setText("POMODORO: STUDIO")

    def update_timer(self):
        if self.mode == "Stopwatch":
            self.elapsed_seconds += 1
            self.update_display()
        else:
            self.remaining_seconds -= 1
            if self.remaining_seconds <= 0:
                self.handle_phase_end()
            else:
                self.update_display()

    def handle_phase_end(self):
        if self.pomodoro_phase == "Work":
            # Studio finito -> Break
            self.stop_timer(manual=False) # Automatically saves the work session
            self.pomodoro_phase = "Break"
            self.remaining_seconds = self.break_duration
            self.phase_label.setText("POMODORO: PAUSA")
            self.phase_label.setStyleSheet("font-weight: bold; color: #27ae60;")
            self.update_display()
            # We don't auto-start the break, let user click start? Or auto-start?
            # Standard Pomodoro usually requires user to start the next phase.
        else:
            # Pausa finita -> Work
            self.stop_timer(manual=False)
            self.pomodoro_phase = "Work"
            self.remaining_seconds = self.work_duration
            self.phase_label.setText("POMODORO: STUDIO")
            self.phase_label.setStyleSheet("font-weight: bold; color: #e67e22;")
            self.update_display()

    def update_display(self):
        if self.mode == "Stopwatch":
            secs_to_show = self.elapsed_seconds
        else:
            secs_to_show = self.remaining_seconds
            
        hours = secs_to_show // 3600
        mins = (secs_to_show % 3600) // 60
        secs = secs_to_show % 60
        self.time_display.setText(f"{hours:02}:{mins:02}:{secs:02}")