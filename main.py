import sys
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from database import Database
from repository import StudyRepository
from viewmodel import ViewModel
from ui.mainWindow import MainWindow

"""
StudyTracker - Main Entry Point
This script initializes the application, sets up the data layers (Database, Repository, ViewModel),
applies the visual theme, and launches the main window.
"""

def main():
    # Create the Qt Application
    app = QApplication(sys.argv)

    # Apply qt-material theme for a modern dark look
    apply_stylesheet(app, theme='dark_blue.xml')

    # Initialize data layers
    # Database handles SQLite connections and schema
    database = Database()
    # Repository provides an abstraction over the database
    repository = StudyRepository(database)
    # ViewModel handles business logic and UI state/signals
    viewmodel = ViewModel(repository)

    # Create and show the Main Window, passing the viewmodel for data interaction
    window = MainWindow(viewmodel)
    window.setMinimumSize(1100, 700)  # Set a minimum size to maintain usability
    window.show()

    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
