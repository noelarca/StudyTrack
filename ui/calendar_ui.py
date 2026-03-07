from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QCalendarWidget, QSplitter
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QTextCharFormat, QColor, QBrush
from ui.components.day_details_widget import DayDetailsWidget

class CalendarUI(QWidget):
    """
    UI component for visualizing study sessions on a calendar.
    Features:
    - Heat-map style intensity indicators (background colors) based on study hours.
    - Day-by-day details panel showing sessions for the selected date.
    """
    def __init__(self, viewmodel):
        """
        Initializes the calendar interface.
        
        Args:
            viewmodel (ViewModel): The viewmodel for data interaction.
        """
        super().__init__()
        self.viewmodel = viewmodel
        
        # Colors for intensity levels (inspired by GitHub contributions)
        self.intensity_colors = [
            QColor("#9be9a8"), # Low intensity (< 2 hours)
            QColor("#40c463"), # Medium-Low intensity (< 4 hours)
            QColor("#30a14e"), # Medium-High intensity (< 6 hours)
            QColor("#216e39")  # High intensity (> 6 hours)
        ]
        
        self.setup_ui()
        
        # Auto-refresh calendar when new entries are added/modified
        if self.viewmodel:
            self.viewmodel.entries_changed.connect(self.refresh_calendar)

    def setup_ui(self):
        """Sets up the layout, calendar, and details panel."""
        main_layout = QHBoxLayout(self)
        
        # Splitter allows resizing between the calendar and details view
        splitter = QSplitter(Qt.Horizontal)
        
        # --- LEFT SIDE: THE CALENDAR ---
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self.on_date_selected)
        
        # --- RIGHT SIDE: DETAILS PANEL ---
        # Displays session info for the date selected on the calendar.
        self.details_widget = DayDetailsWidget(self.viewmodel)
        
        splitter.addWidget(self.calendar)
        splitter.addWidget(self.details_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # Initial load of data
        self.refresh_calendar()
        self.on_date_selected() # Show details for today by default

    def get_format_for_hours(self, hours):
        """
        Determines the visual format (color, bold) for a specific day based on study hours.
        
        Args:
            hours (float): Total study hours for the day.
            
        Returns:
            QTextCharFormat: The formatting to apply to the calendar cell.
        """
        fmt = QTextCharFormat()
        fmt.setFontWeight(700) # Make study days bold
        
        if hours == 0:
            return fmt # Return default format for days with no study
            
        # Determine color based on intensity
        color = self.intensity_colors[0]
        if hours >= 6:
            color = self.intensity_colors[3]
        elif hours >= 4:
            color = self.intensity_colors[2]
        elif hours >= 2:
            color = self.intensity_colors[1]
            
        fmt.setBackground(QBrush(color))
        
        # Adjust text color for readability against dark backgrounds
        if hours >= 4:
            fmt.setForeground(QBrush(Qt.white))
        else:
            fmt.setForeground(QBrush(Qt.black))
            
        return fmt

    def refresh_calendar(self):
        """
        Fetches daily stats from the viewmodel and updates the calendar's 
        visual formatting for all study days.
        """
        if not self.viewmodel: return
        stats = self.viewmodel.get_daily_stats(days=365)
        for date_str, hours in stats:
            qdate = QDate.fromString(date_str, "yyyy-MM-dd")
            self.calendar.setDateTextFormat(qdate, self.get_format_for_hours(hours))

    def on_date_selected(self):
        """
        Callback triggered when a user selects a date on the calendar.
        Updates the details panel with info for that date.
        """
        selected_date = self.calendar.selectedDate()
        self.details_widget.update_details(selected_date)
