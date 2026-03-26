# ui/components/stopwatch_widget.py
"""
Stopwatch and Pomodoro timer widgets for tracking study sessions.
Includes a custom animated switch and a full-featured timer widget.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, 
    QHBoxLayout, QComboBox, QSizePolicy, QAbstractButton,
    QSpinBox, QFrame
)
from PySide6.QtCore import (
    QTimer, QTime, Qt, Signal, Property, 
    QPoint, QPropertyAnimation, QSize
)
from PySide6.QtGui import QPainter, QColor

class Switch(QAbstractButton):
    """
    A custom animated toggle switch widget.
    
    Attributes:
        _offset (int): Current horizontal offset of the slider thumb.
        _anim (QPropertyAnimation): Animation for the thumb movement.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._offset = 2
        self._anim = QPropertyAnimation(self, b"offset", self)
        self._anim.setDuration(150)

    @Property(int)
    def offset(self):
        """Property for the thumb offset, used by animation."""
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value
        self.update()

    def sizeHint(self):
        """Returns the recommended size for the switch (Compact)."""
        return QSize(36, 18)

    def paintEvent(self, event):
        """Custom paint event to draw the switch track and thumb."""
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        
        # Colors from theme or defaults
        highlight = self.palette().highlight().color()
        track_color = highlight if self.isChecked() else QColor("#808080")
        thumb_color = QColor("white")
        
        # Draw track (rounded rectangle) - Height 18, radius 9
        p.setBrush(track_color)
        p.drawRoundedRect(0, 0, self.width(), self.height(), 9, 9)
        
        # Draw thumb (circle) - Size 14x14, centered vertically
        p.setBrush(thumb_color)
        p.drawEllipse(self._offset, 2, 14, 14)

    def nextCheckState(self):
        """Handles the state transition and starts the animation."""
        super().nextCheckState()
        self._anim.setStartValue(self._offset)
        # Offset end value: Width(36) - ThumbWidth(14) - Margin(2) = 20
        self._anim.setEndValue(20 if self.isChecked() else 2)
        self._anim.start()

class StopwatchWidget(QWidget):
    """
    A widget providing both Stopwatch and Pomodoro timer functionalities.
    
    Signals:
        session_finished (QTime, QTime): Emitted when a session ends, 
                                        containing start and end times.
    """
    # Emits (StartTime, EndTime)
    session_finished = Signal(QTime, QTime)
    mini_mode_requested = Signal()
    # Emits (time_string, phase_string, is_running, is_paused)
    time_changed = Signal(str, str, bool, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Core timer logic
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        
        self.start_time = None
        self.is_running = False
        self.is_paused = False
        self.elapsed_seconds = 0 # Seconds in the current block
        self.total_session_seconds = 0 # Total seconds across all blocks
        
        # Pomodoro specific state
        self.mode = "Stopwatch" # "Stopwatch" or "Pomodoro"
        self.pomodoro_phase = "Work" # "Work" or "Break"
        self.work_duration = 25 * 60
        self.break_duration = 5 * 60
        self.remaining_seconds = self.work_duration

        self.setup_ui()

    def setup_ui(self):
        """Initializes the user interface components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Add stretch at top to center the entire widget area vertically
        layout.addStretch()

        # 1. Integrated Timer Container (Switch & Time centered)
        self.timer_container = QFrame()
        self.timer_container.setFrameShape(QFrame.StyledPanel)
        self.timer_container.setFixedHeight(220) # Larger height for better visibility
        self.timer_container.setStyleSheet("""
            QFrame {
                border: 1px solid;
                border-radius: 20px;
                padding: 10px;
            }
        """)
        timer_layout = QVBoxLayout(self.timer_container)
        timer_layout.setContentsMargins(10, 10, 10, 15)
        timer_layout.setSpacing(0)

        # 1.1 Mode Switch Row (Top)
        mode_layout = QHBoxLayout()
        self.sw_label = QLabel("Stopwatch")
        self.sw_label.setStyleSheet("font-weight: bold; border: none; font-size: 11px;")
        
        self.mode_switch = Switch()
        self.mode_switch.toggled.connect(self.on_mode_toggled)
        
        self.pom_label = QLabel("Pomodoro")
        self.pom_label.setStyleSheet("color: gray; border: none; font-size: 11px;")

        self.mini_btn = QPushButton("🗗") # Icon-like symbol for mini mode
        self.mini_btn.setFixedSize(24, 24)
        self.mini_btn.setToolTip("Mini Mode")
        self.mini_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid gray;
                border-radius: 5px;
                font-size: 14px;
                color: gray;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                color: black;
            }
        """)
        self.mini_btn.clicked.connect(self.mini_mode_requested.emit)
        
        mode_layout.addStretch()
        mode_layout.addWidget(self.sw_label)
        mode_layout.addWidget(self.mode_switch)
        mode_layout.addWidget(self.pom_label)
        mode_layout.addStretch()
        mode_layout.addWidget(self.mini_btn)
        timer_layout.addLayout(mode_layout)

        timer_layout.addStretch()

        # 1.2 Phase Label
        self.phase_label = QLabel("SESSIONE STANDARD")
        self.phase_label.setAlignment(Qt.AlignCenter)
        self.phase_label.setStyleSheet("font-weight: bold; font-size: 13px; border: none; color: gray;")
        timer_layout.addWidget(self.phase_label)

        # 1.3 Time Display
        self.time_display = QLabel("00:00:00")
        self.time_display.setAlignment(Qt.AlignCenter)
        self.time_display.setStyleSheet("font-size: 72px; font-weight: bold; border: none; margin-top: -10px;")
        timer_layout.addWidget(self.time_display)

        timer_layout.addStretch()
        layout.addWidget(self.timer_container)

        # 2. Pomodoro Settings (Outside Timer, Underneath)
        self.pom_settings = QWidget()
        pom_settings_layout = QHBoxLayout(self.pom_settings)
        pom_settings_layout.setContentsMargins(0, 0, 0, 5)
        pom_settings_layout.setSpacing(10)
        
        work_lbl = QLabel("Studio:")
        work_lbl.setStyleSheet("font-size: 11px; color: gray;")
        self.work_input = QSpinBox()
        self.work_input.setRange(1, 120)
        self.work_input.setValue(25)
        self.work_input.setSuffix("m")
        self.work_input.setFixedWidth(60)
        self.work_input.setStyleSheet("font-size: 11px; height: 22px;")
        self.work_input.valueChanged.connect(self.update_pomodoro_durations)
        
        break_lbl = QLabel("Pausa:")
        break_lbl.setStyleSheet("font-size: 11px; color: gray;")
        self.break_input = QSpinBox()
        self.break_input.setRange(1, 30)
        self.break_input.setValue(5)
        self.break_input.setSuffix("m")
        self.break_input.setFixedWidth(60)
        self.break_input.setStyleSheet("font-size: 11px; height: 22px;")
        self.break_input.valueChanged.connect(self.update_pomodoro_durations)
        
        pom_settings_layout.addStretch()
        pom_settings_layout.addWidget(work_lbl)
        pom_settings_layout.addWidget(self.work_input)
        pom_settings_layout.addWidget(break_lbl)
        pom_settings_layout.addWidget(self.break_input)
        pom_settings_layout.addStretch()
        
        self.pom_settings.setVisible(False)
        layout.addWidget(self.pom_settings)

        # Space before buttons
        layout.addStretch()

        # 3. Control Buttons
        btn_layout = QHBoxLayout()
        
        self.toggle_btn = QPushButton("AVVIA SESSIONE")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setStyleSheet("QPushButton { font-weight: bold; padding: 10px; }")
        self.toggle_btn.clicked.connect(self.toggle_timer)

        self.pause_btn = QPushButton("PAUSA")
        self.pause_btn.setEnabled(False)
        self.pause_btn.setStyleSheet("QPushButton { font-weight: bold; padding: 10px; }")
        self.pause_btn.clicked.connect(self.toggle_pause)

        self.reset_btn = QPushButton("RESET")
        self.reset_btn.setStyleSheet("QPushButton { font-weight: bold; padding: 10px; }")
        self.reset_btn.clicked.connect(self.reset_timer)

        btn_layout.addWidget(self.toggle_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.reset_btn)
        layout.addLayout(btn_layout)

    def on_mode_toggled(self, is_pomodoro):
        """Switches between Stopwatch and Pomodoro modes."""
        if self.is_running or self.is_paused:
            self.reset_timer()
            
        if is_pomodoro:
            self.mode = "Pomodoro"
            self.pom_label.setStyleSheet("font-weight: bold;")
            self.sw_label.setStyleSheet("color: gray;")
            self.pom_settings.setVisible(True)
            self.update_pomodoro_durations()
        else:
            self.mode = "Stopwatch"
            self.sw_label.setStyleSheet("font-weight: bold;")
            self.pom_label.setStyleSheet("color: gray;")
            self.pom_settings.setVisible(False)
            self.reset_timer()

    def update_pomodoro_durations(self):
        """Updates durations from spinbox inputs and resets timer display if not running."""
        self.work_duration = self.work_input.value() * 60
        self.break_duration = self.break_input.value() * 60
        if not self.is_running and not self.is_paused:
            self.pomodoro_phase = "Work"
            self.remaining_seconds = self.work_duration
            self.phase_label.setText("POMODORO: STUDIO")
            self.update_display()

    def toggle_timer(self):
        """Starts or stops the timer based on current state."""
        if self.toggle_btn.isChecked():
            self.is_running = True
            self.is_paused = False
            self.start_time = QTime.currentTime()
            self.mode_switch.setEnabled(False)
            self.pom_settings.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.pause_btn.setText("PAUSA")
            
            if self.mode == "Stopwatch":
                self.toggle_btn.setText("FERMA E SALVA")
                # Don't reset total_session_seconds here, it might be a resume from reset? 
                # Actually, Start always resets if not paused.
                self.elapsed_seconds = 0
                self.total_session_seconds = 0
            else:
                self.toggle_btn.setText("INTERROMPI")
                self.remaining_seconds = self.work_duration if self.pomodoro_phase == "Work" else self.break_duration
            
            self.update_display()
            self.timer.start(1000)
        else:
            self.stop_timer(manual=True)

    def toggle_pause(self):
        """Toggles between paused and running states."""
        if not self.is_running and not self.is_paused:
            return

        if self.is_running:
            # PAUSING
            self.is_running = False
            self.is_paused = True
            self.timer.stop()
            self.pause_btn.setText("RIPRENDI")
            
            # Save the current block
            if self.start_time:
                end_time = QTime.currentTime()
                self.session_finished.emit(self.start_time, end_time)
                self.start_time = None
        else:
            # RESUMING
            self.is_running = True
            self.is_paused = False
            self.start_time = QTime.currentTime()
            self.pause_btn.setText("PAUSA")
            self.timer.start(1000)
        
        self.update_display()

    def stop_timer(self, manual=False):
        """
        Stops the timer and emits the session_finished signal for the last block.
        """
        was_running = self.is_running
        self.is_running = False
        self.is_paused = False
        self.timer.stop()
        self.mode_switch.setEnabled(True)
        self.pom_settings.setEnabled(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.setText("AVVIA SESSIONE")
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("PAUSA")
        
        self.update_display()
        
        if was_running and self.start_time:
            end_time = QTime.currentTime()
            if self.mode == "Stopwatch":
                self.session_finished.emit(self.start_time, end_time)
            elif self.mode == "Pomodoro" and self.pomodoro_phase == "Work":
                if not manual:
                    actual_start = end_time.addSecs(-self.work_duration)
                    self.session_finished.emit(actual_start, end_time)
                else:
                    self.session_finished.emit(self.start_time, end_time)
        
        self.start_time = None

    def reset_timer(self):
        """Resets the timer state and UI to initial values."""
        self.is_running = False
        self.is_paused = False
        self.timer.stop()
        self.mode_switch.setEnabled(True)
        self.pom_settings.setEnabled(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.setText("AVVIA SESSIONE")
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("PAUSA")
        self.start_time = None
        self.total_session_seconds = 0
        
        if self.mode == "Stopwatch":
            self.elapsed_seconds = 0
            self.phase_label.setText("SESSIONE STANDARD")
            self.update_display()
        else:
            self.update_pomodoro_durations()

    def update_timer(self):
        """Callback for the QTimer, updates time tracking based on mode."""
        if self.mode == "Stopwatch":
            self.elapsed_seconds += 1
            self.total_session_seconds += 1
            self.update_display()
        else:
            self.remaining_seconds -= 1
            if self.remaining_seconds <= 0:
                self.handle_phase_end()
            else:
                self.update_display()

    def handle_phase_end(self):
        """Handles transitions between Work and Break phases in Pomodoro mode."""
        if self.pomodoro_phase == "Work":
            self.stop_timer(manual=False)
            self.pomodoro_phase = "Break"
            self.remaining_seconds = self.break_duration
            self.phase_label.setText("POMODORO: PAUSA")
            self.update_display()
        else:
            self.stop_timer(manual=False)
            self.pomodoro_phase = "Work"
            self.remaining_seconds = self.work_duration
            self.phase_label.setText("POMODORO: STUDIO")
            self.update_display()

    def update_display(self):
        """Updates the time display label with formatted time."""
        if self.mode == "Stopwatch":
            secs_to_show = self.total_session_seconds
        else:
            secs_to_show = self.remaining_seconds

        hours = secs_to_show // 3600
        mins = (secs_to_show % 3600) // 60
        secs = secs_to_show % 60
        time_str = f"{hours:02}:{mins:02}:{secs:02}"
        
        if self.is_paused:
            self.time_display.setStyleSheet("font-size: 72px; font-weight: bold; border: none; margin-top: -10px; color: #f39c12;")
        else:
            self.time_display.setStyleSheet("font-size: 72px; font-weight: bold; border: none; margin-top: -10px;")

        self.time_display.setText(time_str)
        
        phase_text = self.phase_label.text()
        if self.is_paused:
            phase_text += " (IN PAUSA)"
            
        self.time_changed.emit(time_str, phase_text, self.is_running, self.is_paused)

