from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QSplitter
)
from PySide6.QtCore import Qt, QDate
from ui.components.calendar.day_details_widget import DayDetailsWidget
from ui.components.calendar.custom_calendar import CustomCalendar

class CalendarUI(QWidget):
    """
    UI component for visualizing study sessions and tasks on a custom heatmap calendar.
    Features:
    - Heat-map style intensity indicators based on study hours.
    - Priority dots for tasks due on specific dates.
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
        
        self.setup_ui()
        
        # Auto-refresh calendar when new entries or tasks are modified
        if self.viewmodel:
            self.viewmodel.entries_changed.connect(self.refresh_calendar, Qt.QueuedConnection)
            self.viewmodel.tasks_changed.connect(self.refresh_calendar, Qt.QueuedConnection)

    def setup_ui(self):
        """Sets up the layout, custom calendar, and details panel."""
        main_layout = QHBoxLayout(self)
        
        # Splitter allows resizing between the calendar and details view
        splitter = QSplitter(Qt.Horizontal)
        
        # --- LEFT SIDE: THE CUSTOM CALENDAR ---
        self.calendar = CustomCalendar()
        self.calendar.dateSelected.connect(self.on_date_selected)
        self.calendar.calendarRendered.connect(self.refresh_calendar)
        
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
        self.on_date_selected(QDate.currentDate()) # Show details for today by default

    def refresh_calendar(self):
        """
        Fetches daily stats and tasks from the viewmodel and updates the custom 
        calendar's visual formatting (heatmap and priority dots).
        """
        if not self.viewmodel: return
        
        # Update heatmap
        stats = self.viewmodel.get_daily_stats(days=365)
        stats_dict = {date_str: hours for date_str, hours in stats}
        
        # Update tasks/priority (Mocking priority logic based on task count for now)
        # In a real scenario, you'd fetch tasks due on each date
        tasks = self.viewmodel.get_all_tasks()
        task_counts = {}
        for task in tasks:
            # task is a tuple: (id, subject_name, title, description, due_date, priority, is_completed)
            due_date = task[4]
            if due_date:
                task_counts[due_date] = task_counts.get(due_date, 0) + 1

        print(f"DEBUG: refresh_calendar - day_cells count: {len(self.calendar.day_cells)}")
        for cell in self.calendar.day_cells:
            try:
                date_str = cell.date.toString("yyyy-MM-dd")
                
                # Set heatmap intensity
                hours = stats_dict.get(date_str, 0)
                cell.set_intensity(self.calendar.get_intensity_color(hours))
                
                # Set priority dots based on task count
                priority = task_counts.get(date_str, 0)
                cell.set_priority(priority)
            except Exception as e:
                print(f"DEBUG: Error updating cell: {e}")

    def on_date_selected(self, selected_date):
        """
        Callback triggered when a user selects a date on the custom calendar.
        Updates the details panel with info for that date.
        """
        self.details_widget.update_details(selected_date)
