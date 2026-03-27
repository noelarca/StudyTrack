# StudyTrack
A simple but powerful study tracker, with some stat functionality

# Installation (For Users)

The easiest way to use StudyTrack is to download the standalone executable. No installation or prerequisites are required.

1. Go to the **Releases** page on GitHub (once you publish a release).
2. Download the `StudyTrack.exe` file.
3. Double-click the file to run the application.

---

# Development Setup (For Developers)

If you want to modify the code or build the application from source, follow these steps.

## Requirements
- Git
- Python 3.10+
- PySide6
- qt-material
- pyinstaller (for building)

### 1. Prerequisites
Ensure you have Git and Python installed:
- Git: Download from [git-scm.com](https://git-scm.com/downloads)
- Python: Download from [python.org](https://www.python.org/downloads/)

### 2. Clone the repository:
```bash
git clone https://github.com/noelarca/StudyTrack.git
cd StudyTrack
```

### 3. Set up a virtual environment (optional but recommended):
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 4. Install dependencies:
```powershell
pip install -r requirements.txt
```

### 5. Run the application:
```powershell
python main.py
```

## Building the Executable

To build the standalone `.exe` file yourself, run the following command in your terminal from the project root:

```powershell
python -m PyInstaller --noconsole --onefile --windowed --name "StudyTrack" StudyTrack.pyw
```

The compiled application will be located in the `dist/` directory.

---

## Third-Party Licenses

This project utilizes the following libraries:

- PySide6: Released under the GNU LGPL v3 license (https://www.gnu.org/licenses/lgpl-3.0.html).
- SQLite: Released into the Public Domain.
