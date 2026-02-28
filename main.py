import sys
from PySide6.QtWidgets import QApplication

from database import Database
from repository import StudyRepository
from viewmodel import ViewModel
from ui.mainWindow import MainWindow

app = QApplication(sys.argv)

database = Database()
repository = StudyRepository(database)
viewmodel = ViewModel(repository)

window = MainWindow(viewmodel)
window.show()

sys.exit(app.exec())