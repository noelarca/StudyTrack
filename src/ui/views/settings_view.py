from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QFrame
)
from PySide6.QtCore import Qt
from qt_material import apply_stylesheet, list_themes

class SettingsUI(QWidget):
    """
    Settings page for the application.
    Allows users to change themes and other application-wide settings.
    """
    def __init__(self, viewmodel):
        super().__init__()
        self.viewmodel = viewmodel
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        # Title
        self.title = QLabel("Impostazioni")
        self.title.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
        self.layout.addWidget(self.title)

        # Theme Section
        self.theme_frame = QFrame()
        self.theme_frame.setStyleSheet("background-color: rgba(255, 255, 255, 0.05); border-radius: 10px; padding: 20px;")
        theme_layout = QVBoxLayout(self.theme_frame)

        self.theme_label = QLabel("Tema dell'applicazione")
        self.theme_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00bcd4;")
        theme_layout.addWidget(self.theme_label)

        self.theme_desc = QLabel("Scegli un tema per personalizzare l'aspetto di StudyTrack.")
        self.theme_desc.setStyleSheet("color: #b0bec5; margin-bottom: 10px;")
        theme_layout.addWidget(self.theme_desc)

        self.theme_selector = QComboBox()
        themes = list_themes()
        self.theme_selector.addItems(themes)
        
        current_theme = self.viewmodel.get_setting("theme")
        index = self.theme_selector.findText(current_theme)
        if index >= 0:
            self.theme_selector.setCurrentIndex(index)

        self.theme_selector.currentTextChanged.connect(self.change_theme)
        theme_layout.addWidget(self.theme_selector)

        self.layout.addWidget(self.theme_frame)
        self.layout.addStretch()

    def change_theme(self, theme_name):
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            apply_stylesheet(app, theme=theme_name)
            self.viewmodel.set_setting("theme", theme_name)
