import json
import os

class SettingsManager:
    """
    Manages application settings and their persistence in a JSON file.
    """
    def __init__(self, settings_path=None):
        if settings_path is None:
            appdata_path = os.path.join(os.environ['APPDATA'], 'StudyTrack')
            if not os.path.exists(appdata_path):
                os.makedirs(appdata_path)
            settings_path = os.path.join(appdata_path, 'settings.json')
        
        self.settings_path = settings_path
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r') as f:
                    return json.load(f)
            except Exception:
                return self.get_defaults()
        return self.get_defaults()

    def get_defaults(self):
        return {
            "theme": "dark_blue.xml"
        }

    def save_settings(self):
        try:
            with open(self.settings_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get_setting(self, key):
        return self.settings.get(key, self.get_defaults().get(key))

    def set_setting(self, key, value):
        self.settings[key] = value
        self.save_settings()
