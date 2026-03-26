from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from ui.components.entry.entry_widget import EntryWidgetBox
from ui.dialogs.edit_entry_dialog import EditEntryDialog
from ui.components.entry.last_entries_widget import LastEntriesWidget
from ui.components.subject.sub_grid import SubGrid
from ui.components.entry.stopwatch_widget import StopwatchWidget
from ui.components.entry.mini_timer import MiniTimerWindow

class EntryWidget(QWidget):
    """
    UI for logging new study sessions.
    Features:
    - Stopwatch to track study duration in real-time.
    - Input form for manual session logging.
    - List of recent study entries with editing capabilities.
    """
    def __init__(self, viewmodel):
        """
        Initializes the entry logging interface.
        
        Args:
            viewmodel (ViewModel): The viewmodel for data interaction.
        """
        super().__init__()
        self.viewmodel = viewmodel
        self.mini_timer = None
        self.setup_ui()

    def setup_ui(self):
        """Sets up the layout and initializes components."""
        self.setWindowTitle("Study Tracker")
        self.resize(400, 300)

        # Main layout structure
        top_layout = QHBoxLayout()
        main_layout = QVBoxLayout()

        # --- STOPWATCH COMPONENT ---
        # Integrated stopwatch to track session duration automatically.
        self.stopwatch = StopwatchWidget()
        top_layout.addWidget(self.stopwatch)
        self.stopwatch.session_finished.connect(self.handle_session_finished)
        
        # Mini Mode Setup
        self.stopwatch.mini_mode_requested.connect(self.enter_mini_mode)
        self.stopwatch.time_changed.connect(self.update_mini_timer)

        # --- INPUT FORM BOX ---
        # Form for subject selection, time input, and notes.
        self.study_entry_box = EntryWidgetBox("Dettagli Input", viewmodel=self.viewmodel)
        self.study_entry_box.setMinimumWidth(300)
        self.study_entry_box.setMaximumWidth(400)
        top_layout.addWidget(self.study_entry_box)

        main_layout.addLayout(top_layout)

        # --- RECENT ENTRIES LIST ---
        # Displays the last few study sessions and allows editing/deleting.
        self.last_entries_widget = LastEntriesWidget(viewmodel=self.viewmodel)
        self.last_entries_widget.setMinimumHeight(200)
        self.last_entries_widget.setMaximumHeight(300)
        self.last_entries_widget.setMinimumWidth(900)

        # Signal connection for editing entries
        self.last_entries_widget.edit_entry_requested.connect(self.handle_edit_entry)

        main_layout.addWidget(self.last_entries_widget)

        self.setLayout(main_layout)
    
    def handle_session_finished(self, start_time, end_time):
        """
        Callback when the stopwatch finishes.
        Auto-fills the input form with the tracked times and attempts to save.
        
        Args:
            start_time (QTime): Tracked session start.
            end_time (QTime): Tracked session end.
        """
        self.study_entry_box.time_edit_1.setTime(start_time)
        self.study_entry_box.time_edit_2.setTime(end_time)
        # Automatically trigger the save action
        self.study_entry_box.on_click()

    def save_entry(self, subject, date, start_time, end_time, notes):
        """
        Directly saves an entry via the viewmodel.
        
        Args:
            subject (str): Subject name.
            date (str): Session date.
            start_time (str): Start time.
            end_time (str): End time.
            notes (str): Notes.
        """
        try:
            self.viewmodel.add_entry(subject, date, start_time, end_time, notes)
            # Refresh the list of entries to show the new one
            self.last_entries_widget.refresh_entries()
        except ValueError as e:
            # Handle validation errors (e.g., via print or a future message box)
            print(f"Error saving entry: {e}")

    def handle_edit_entry(self, entry_id):
        """
        Opens a dialog to edit an existing session entry.
        
        Args:
            entry_id (int): ID of the entry to edit.
        """
        try:
            entry_data = self.viewmodel.get_entry_by_id(entry_id)
            if entry_data:
                # Launch the modal edit dialog
                dialog = EditEntryDialog(entry_data, self.viewmodel, self)
                dialog.exec()
            else:
                print(f"Entry with ID {entry_id} not found.") 
        except Exception as e:
            print(f"Error handling edit entry: {e}")

    def enter_mini_mode(self):
        """Transitions the UI to a floating mini-timer."""
        if not self.mini_timer:
            self.mini_timer = MiniTimerWindow()
            self.mini_timer.back_to_full_requested.connect(self.exit_mini_mode)
            self.mini_timer.toggle_timer_requested.connect(self.stopwatch.toggle_btn.click)

        # Sync initial state
        self.mini_timer.update_status(self.stopwatch.is_running, self.stopwatch.mode)
        self.mini_timer.update_time(self.stopwatch.time_display.text(), self.stopwatch.phase_label.text())
        
        # Hide main window and show mini timer
        self.window().hide()
        self.mini_timer.show()

    def exit_mini_mode(self):
        """Returns to the full application view in a normal (non-fullscreen) state."""
        if self.mini_timer:
            self.mini_timer.hide()
        
        main_window = self.window()
        main_window.showNormal()  # Restore from minimized/maximized/fullscreen
        main_window.resize(1100, 700) # Reset to minimum size
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()

    def update_mini_timer(self, time_str, phase_str):
        """Updates the mini timer display if it's active."""
        if self.mini_timer and self.mini_timer.isVisible():
            self.mini_timer.update_time(time_str, phase_str)
            self.mini_timer.update_status(self.stopwatch.is_running, self.stopwatch.mode)
