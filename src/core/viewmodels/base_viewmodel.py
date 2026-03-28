from PySide6.QtCore import QObject, Signal
from utils.settings import SettingsManager

class BaseViewModel(QObject):
    """
    Base class for all ViewModels, providing shared functionality like settings management.
    """
    settings_changed = Signal()

    def __init__(self, repository):
        super().__init__()
        self.repository = repository
        self.settings_manager = SettingsManager()

    def get_setting(self, key):
        return self.settings_manager.get_setting(key)

    def set_setting(self, key, value):
        self.settings_manager.set_setting(key, value)
        self.settings_changed.emit()
