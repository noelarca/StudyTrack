from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QCalendarWidget, QSplitter
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QTextCharFormat, QColor, QBrush
from ui.components.day_details_widget import DayDetailsWidget

class CalendarUI(QWidget):
    def __init__(self, viewmodel):
        super().__init__()
        self.viewmodel = viewmodel
        
        # Colors for intensity levels
        self.intensity_colors = [
            QColor("#9be9a8"), # < 2 hours
            QColor("#40c463"), # < 4 hours
            QColor("#30a14e"), # < 6 hours
            QColor("#216e39")  # > 6 hours
        ]
        
        self.setup_ui()
        
        if self.viewmodel:
            self.viewmodel.entries_changed.connect(self.refresh_calendar)

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        
        # Splitter for resizability
        splitter = QSplitter(Qt.Horizontal)
        
        # --- Left Side: The Calendar ---
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self.on_date_selected)
        
        # --- Right Side: Details for selected day ---
        self.details_widget = DayDetailsWidget(self.viewmodel)
        
        splitter.addWidget(self.calendar)
        splitter.addWidget(self.details_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        self.refresh_calendar()
        self.on_date_selected() # Initial load for today

    def get_format_for_hours(self, hours):
        fmt = QTextCharFormat()
        fmt.setFontWeight(700) # Bold
        
        if hours == 0:
            return fmt # Default
            
        color = self.intensity_colors[0]
        if hours >= 6:
            color = self.intensity_colors[3]
        elif hours >= 4:
            color = self.intensity_colors[2]
        elif hours >= 2:
            color = self.intensity_colors[1]
            
        fmt.setBackground(QBrush(color))
        # White text for dark backgrounds
        if hours >= 4:
            fmt.setForeground(QBrush(Qt.white))
        else:
            fmt.setForeground(QBrush(Qt.black))
            
        return fmt

    def refresh_calendar(self):
        if not self.viewmodel: return
        stats = self.viewmodel.get_daily_stats(days=365)
        for date_str, hours in stats:
            qdate = QDate.fromString(date_str, "yyyy-MM-dd")
            self.calendar.setDateTextFormat(qdate, self.get_format_for_hours(hours))

    def on_date_selected(self):
        selected_date = self.calendar.selectedDate()
        self.details_widget.update_details(selected_date)
