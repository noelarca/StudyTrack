from PySide6.QtGui import QShortcut, QKeySequence

class HotkeyManager:
    """
    Utility class to manage application-wide keyboard shortcuts.
    """
    @staticmethod
    def setup_main_navigation(window):
        """Sets up shortcuts for switching between main tabs."""
        # Ctrl+1 to Ctrl+5 for navigation
        for i in range(5):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{i+1}"), window)
            # Use a default argument in lambda to capture the current 'i'
            shortcut.activated.connect(lambda index=i: window.tab_bar.setCurrentIndex(index))

    @staticmethod
    def setup_timer_shortcuts(widget, stopwatch):
        """Sets up shortcuts for timer control (Start/Stop/Pause)."""
        # S: Toggle Start/Stop
        start_shortcut = QShortcut(QKeySequence("S"), widget)
        start_shortcut.activated.connect(stopwatch.toggle_btn.click)

        # P: Toggle Pause/Resume
        pause_shortcut = QShortcut(QKeySequence("P"), widget)
        pause_shortcut.activated.connect(stopwatch.pause_btn.click)

        # R: Reset
        reset_shortcut = QShortcut(QKeySequence("R"), widget)
        reset_shortcut.activated.connect(stopwatch.reset_btn.click)

    @staticmethod
    def setup_form_shortcuts(widget, entry_box):
        """Sets up shortcuts for form interactions (Quality, Save)."""
        # Alt+1 to Alt+5 to set quality
        for i in range(1, 6):
            shortcut = QShortcut(QKeySequence(f"Alt+{i}"), widget)
            shortcut.activated.connect(lambda val=i: entry_box.selector.setValue(val))

        # Ctrl+S to trigger the save action
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), widget)
        save_shortcut.activated.connect(entry_box.button.click)
