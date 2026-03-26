from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, 
    QHBoxLayout, QFrame
)
from PySide6.QtCore import Qt, QPoint, Signal

class MiniTimerWindow(QWidget):
    """
    A compact, always-on-top floating timer window.
    """
    back_to_full_requested = Signal()
    toggle_timer_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Window flags: Frameless and Always on Top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.old_pos = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Main container with border and background
        self.container = QFrame()
        self.container.setObjectName("MiniContainer")
        self.container.setStyleSheet("""
            #MiniContainer {
                border: 2px solid;
                border-radius: 15px;
            }
            QLabel {
                color: white;
                border: none;
            }
        """)
        container_layout = QVBoxLayout(self.container)
        container_layout.setSpacing(5)

        # 1. Header with Close/Back button
        header_layout = QHBoxLayout()
        
        self.phase_label = QLabel("STUDIO")
        self.phase_label.setStyleSheet("font-size: 10px; font-weight: bold; color: #95a5a6;")
        
        self.back_btn = QPushButton("⤴")
        self.back_btn.setFixedSize(20, 20)
        self.back_btn.setToolTip("Back to full view")
        self.back_btn.setStyleSheet("""
            QPushButton {
                background: none;
                color: #bdc3c7;
                border: 1px solid #7f8c8d;
                border-radius: 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #34495e;
                color: white;
            }
        """)
        self.back_btn.clicked.connect(self.back_to_full_requested.emit)

        header_layout.addWidget(self.phase_label)
        header_layout.addStretch()
        header_layout.addWidget(self.back_btn)
        container_layout.addLayout(header_layout)

        # 2. Time Display
        self.time_label = QLabel("00:00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("font-size: 32px; font-weight: bold;")
        container_layout.addWidget(self.time_label)

        # 3. Control Button
        self.toggle_btn = QPushButton("AVVIA")
        self.toggle_btn.setFixedHeight(25)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_timer_requested.emit)
        container_layout.addWidget(self.toggle_btn)

        layout.addWidget(self.container)
        self.setFixedSize(210, 140)

    def update_time(self, time_str, phase_str, is_running, is_paused):
        self.time_label.setText(time_str)
        # Simplify phase string for mini mode
        if "STUDIO" in phase_str.upper():
            self.phase_label.setText("STUDIO")
        elif "PAUSA" in phase_str.upper():
            self.phase_label.setText("PAUSA")
        else:
            self.phase_label.setText("SESSIONE")

        if is_paused:
            self.time_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #f39c12;")
            self.toggle_btn.setText("RIPRENDI")
        else:
            self.time_label.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
            if is_running:
                self.toggle_btn.setText("PAUSA")
            else:
                self.toggle_btn.setText("AVVIA")

    def update_status(self, is_running, mode):
        if is_running:
            self.toggle_btn.setText("INTERROMPI" if mode == "Pomodoro" else "STOP E SALVA")
            self.toggle_btn.setStyleSheet(self.toggle_btn.styleSheet().replace("#3498db", "#e74c3c").replace("#2980b9", "#c0392b"))
        else:
            self.toggle_btn.setText("AVVIA")
            self.toggle_btn.setStyleSheet(self.toggle_btn.styleSheet().replace("#e74c3c", "#3498db").replace("#c0392b", "#2980b9"))

    # Dragging logic
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None
