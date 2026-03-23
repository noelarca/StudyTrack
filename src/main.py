import sys
import os
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from core.database import Database
from core.repository import StudyRepository
from core.viewmodel import ViewModel
from ui.main_window import MainWindow

"""
StudyTracker - Main Entry Point
This script initializes the application, sets up the data layers (Database, Repository, ViewModel),
applies the visual theme, and launches the main window.
"""

def main():
    # Create the Qt Application
    app = QApplication(sys.argv)

    # Initialize data layers
    # Ensure the database is stored in the user's AppData folder
    appdata_path = os.path.join(os.environ['APPDATA'], 'StudyTrack')
    if not os.path.exists(appdata_path):
        os.makedirs(appdata_path)
    
    db_path = os.path.join(appdata_path, 'study_tracker.db')

    # Database handles SQLite connections and schema
    database = Database(db_path)
    # Repository provides an abstraction over the database
    repository = StudyRepository(database)
    # ViewModel handles business logic and UI state/signals
    viewmodel = ViewModel(repository)

    # Apply theme from settings
    theme = viewmodel.get_setting("theme")
    apply_stylesheet(app, theme=theme)

    # Create and show the Main Window, passing the viewmodel for data interaction
    window = MainWindow(viewmodel)
    window.setMinimumSize(1100, 700)  # Set a minimum size to maintain usability
    window.show()

    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
