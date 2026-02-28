import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QTabWidget, QLabel
)

app = QApplication(sys.argv)

window = QWidget()
layout = QVBoxLayout(window)

tabs = QTabWidget()

# First tab
tab1 = QWidget()
tab1_layout = QVBoxLayout(tab1)
tab1_layout.addWidget(QLabel("Content of Tab 1"))

# Second tab
tab2 = QWidget()
tab2_layout = QVBoxLayout(tab2)
tab2_layout.addWidget(QLabel("Content of Tab 2"))

# Add tabs
tabs.addTab(tab1, "Tab 1")
tabs.addTab(tab2, "Tab 2")

layout.addWidget(tabs)

window.show()
sys.exit(app.exec())