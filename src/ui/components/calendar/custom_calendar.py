from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QPushButton, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QColor, QPalette, QFont

class DayCell(QFrame):
    """
    Individual cell representing a single day in the calendar.
    """
    clicked = Signal(QDate)

    def __init__(self, date, is_current_month=True, parent=None):
        super().__init__(parent)
        self.date = date
        self.is_current_month = is_current_month
        self.selected = False
        self.priority = 0
        self.intensity_color = None
        
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(45, 45) # Fixed size for consistency
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(2, 4, 2, 4)
        self.layout.setSpacing(2)
        
        self.label = QLabel(str(self.date.day()))
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)
        
        # Dots container
        self.dots_layout = QHBoxLayout()
        self.dots_layout.setSpacing(2)
        self.dots_layout.setAlignment(Qt.AlignCenter)
        self.layout.addLayout(self.dots_layout)
        
        self.update_style()

    def set_priority(self, count):
        """Sets 0-4 dots representing task priority/count."""
        self.priority = max(0, min(4, count))
        
        # Clear existing dots
        for i in reversed(range(self.dots_layout.count())):
            self.dots_layout.itemAt(i).widget().setParent(None)
            
        # Add new dots
        for _ in range(self.priority):
            dot = QFrame()
            dot.setFixedSize(4, 4)
            # Use white dots if background is dark, otherwise orange
            dot_color = "#ffffff" if self.intensity_color and self.intensity_color.lightness() < 150 else "#ff9800"
            dot.setStyleSheet(f"background-color: {dot_color}; border-radius: 2px;")
            self.dots_layout.addWidget(dot)

    def set_intensity(self, color):
        """Sets the background color for the heatmap effect."""
        self.intensity_color = color
        self.update_style()
        # Refresh dots to ensure visibility
        self.set_priority(self.priority)

    def update_style(self):
        bg_color = "#ffffff"
        text_color = "#333333"
        font_weight = "normal"
        border_color = "#e0e0e0"
        
        if not self.is_current_month:
            text_color = "#bdbdbd"
            bg_color = "#fafafa"
            
        if self.intensity_color:
            bg_color = self.intensity_color.name()
            # Adjust text color for readability
            if self.intensity_color.lightness() < 150:
                text_color = "#ffffff"
            else:
                text_color = "#1b5e20" # Dark green text for light green bg
            font_weight = "bold"

        if self.date == QDate.currentDate():
            border_color = "#1976d2"
            if not self.intensity_color:
                bg_color = "#e3f2fd"
                text_color = "#1976d2"
            font_weight = "bold"
            
        if self.selected:
            bg_color = "#1976d2"
            text_color = "#ffffff"
            border_color = "#1565c0"
            
        style = f"""
            DayCell {{
                border: 1px solid {border_color};
                border-radius: 4px;
                background-color: {bg_color};
            }}
            DayCell:hover {{
                background-color: {bg_color if self.selected else "#f5f5f5"};
                border: 2px solid #1976d2;
            }}
            QLabel {{
                color: {text_color};
                font-weight: {font_weight};
                background: transparent;
            }}
        """
        self.setStyleSheet(style)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.date)

    def set_selected(self, selected):
        self.selected = selected
        self.update_style()
        # Refresh dots to ensure visibility
        self.set_priority(self.priority)


class CustomCalendar(QWidget):
    """
    A fully custom calendar widget built from scratch with heatmap support.
    """
    dateSelected = Signal(QDate)
    calendarRendered = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_date = QDate.currentDate()
        self.selected_date = QDate.currentDate()
        self.day_cells = [] 
        
        # Intensity colors (GitHub style)
        self.intensity_colors = [
            QColor("#9be9a8"), # Low (< 2h)
            QColor("#40c463"), # Med-Low (< 4h)
            QColor("#30a14e"), # Med-High (< 6h)
            QColor("#216e39")  # High (> 6h)
        ]
        
        self.setup_ui()
        self.render_calendar()

    def get_intensity_color(self, hours):
        if hours <= 0: return None
        if hours < 2: return self.intensity_colors[0]
        if hours < 4: return self.intensity_colors[1]
        if hours < 6: return self.intensity_colors[2]
        return self.intensity_colors[3]

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # Header: Month Year and Navigation
        header_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("<")
        self.prev_btn.setFixedWidth(30)
        self.prev_btn.clicked.connect(self.prev_month)
        
        self.month_label = QLabel()
        self.month_label.setAlignment(Qt.AlignCenter)
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        self.month_label.setFont(header_font)
        
        self.next_btn = QPushButton(">")
        self.next_btn.setFixedWidth(30)
        self.next_btn.clicked.connect(self.next_month)
        
        header_layout.addWidget(self.prev_btn)
        header_layout.addStretch()
        header_layout.addWidget(self.month_label)
        header_layout.addStretch()
        header_layout.addWidget(self.next_btn)
        
        self.main_layout.addLayout(header_layout)

        # Days of week header
        days_layout = QGridLayout()
        days_layout.setSpacing(5)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            lbl = QLabel(day)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-weight: bold; color: #666;")
            days_layout.addWidget(lbl, 0, i)
        
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(5)
        
        self.main_layout.addLayout(days_layout)
        self.main_layout.addLayout(self.grid_layout)
        self.main_layout.addStretch()

    def render_calendar(self):
        # Clear existing cells
        for i in reversed(range(self.grid_layout.count())): 
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.day_cells.clear()

        # Set month label
        self.month_label.setText(self.current_date.toString("MMMM yyyy"))

        # Calculate range
        first_day = QDate(self.current_date.year(), self.current_date.month(), 1)
        # Adjust for Monday start (Qt: Mon=1, Sun=7)
        day_of_week = first_day.dayOfWeek()
        start_date = first_day.addDays(-(day_of_week - 1))

        # Fill 6 weeks (to be safe and consistent)
        for row in range(6):
            for col in range(7):
                date = start_date.addDays(row * 7 + col)
                is_current_month = date.month() == self.current_date.month()
                
                cell = DayCell(date, is_current_month)
                if date == self.selected_date:
                    cell.set_selected(True)
                
                cell.clicked.connect(self.on_day_clicked)
                self.grid_layout.addWidget(cell, row, col)
                self.day_cells.append(cell)
        
        self.calendarRendered.emit()

    def on_day_clicked(self, date):
        self.selected_date = date
        for cell in self.day_cells:
            cell.set_selected(cell.date == date)
        self.dateSelected.emit(date)

    def prev_month(self):
        self.current_date = self.current_date.addMonths(-1)
        self.render_calendar()

    def next_month(self):
        self.current_date = self.current_date.addMonths(1)
        self.render_calendar()
