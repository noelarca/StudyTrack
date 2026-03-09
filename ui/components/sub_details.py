# ui/components/sub_details.py
"""
Widget for displaying detailed information about a specific subject, 
including statistics, associated tasks, and options to edit or delete the subject.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, 
    QListWidget, QHBoxLayout, QPushButton,
    QFrame, QGraphicsDropShadowEffect, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from ui.components.new_sub_window import NewSubjectWindow
from ui.components.subject_graph import SubjectGraphWidget, QualityPieChart

class StatCard(QFrame):
    """
    A custom styled card widget for displaying a single statistic.
    """
    def __init__(self, title, value, color_hex="#00bcd4"):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        # Custom CSS for the card with a left colored border
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(30, 40, 50, 0.6);
                border-radius: 12px;
                border-left: 5px solid {color_hex};
            }}
        """)
        self.setFixedHeight(110) # Locked height for all stat cards
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #b0bec5; font-size: 13px; font-weight: bold; background: transparent; border: none;")
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("color: white; font-size: 32px; font-weight: bold; background: transparent; border: none;")
        self.value_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

        # Subtle drop shadow for depth
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

    def set_value(self, value):
        self.value_label.setText(str(value))


class SubDetails(QWidget):
    """
    Displays subject-specific details and provides management actions.
    """
    def __init__(self, viewmodel=None):
        super().__init__()
        self.viewmodel = viewmodel
        self.current_subject = None

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area for long content (transparent background)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("QScrollArea { background: transparent; } QWidget#scroll_content { background: transparent; }")
        
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scroll_content")
        self.layout = QVBoxLayout(self.scroll_content)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(25)
        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll)

        # Header Section: Title, Info, and Buttons
        header_layout = QHBoxLayout()
        
        title_info_layout = QVBoxLayout()
        self.title = QLabel("Seleziona una materia")
        self.title.setStyleSheet("color: white; font-weight: bold; font-size: 36px;")
        
        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #90a4ae; font-size: 14px; font-style: italic;")
        
        title_info_layout.addWidget(self.title)
        title_info_layout.addWidget(self.info_label)
        
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignTop)
        
        self.edit_button = QPushButton("Modifica")
        self.edit_button.setCursor(Qt.PointingHandCursor)
        self.edit_button.setStyleSheet("""
            QPushButton {
                background-color: #00bcd4; color: black; border-radius: 8px; 
                padding: 10px 20px; font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background-color: #26c6da; }
        """)
        self.edit_button.clicked.connect(self.edit_subject)
        
        self.delete_button = QPushButton("Elimina")
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(244, 67, 54, 0.1); color: #f44336; border-radius: 8px; 
                border: 1px solid #f44336; padding: 10px 20px; font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background-color: rgba(244, 67, 54, 0.2); }
        """)
        self.delete_button.clicked.connect(self.delete_subject)
        
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        
        header_layout.addLayout(title_info_layout)
        header_layout.addStretch()
        header_layout.addLayout(button_layout)
        self.layout.addLayout(header_layout)

        # Stats Cards Layout
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.card_hours = StatCard("ORE TOTALI", "0.00", "#00bcd4") # Cyan
        self.card_quality = StatCard("QUALITÀ MEDIA", "0.0", "#8bc34a") # Green
        self.card_cfu = StatCard("CFU", "0", "#ff9800") # Orange
        
        stats_layout.addWidget(self.card_hours)
        stats_layout.addWidget(self.card_quality)
        stats_layout.addWidget(self.card_cfu)
        self.layout.addLayout(stats_layout)

        # Graphs Section
        graphs_layout = QHBoxLayout()
        graphs_layout.setSpacing(20)
        
        # Wrap graphs in styled frames to match cards
        self.hours_graph_container = QFrame()
        self.hours_graph_container.setStyleSheet("background-color: rgba(30, 40, 50, 0.4); border-radius: 12px;")
        hg_layout = QVBoxLayout(self.hours_graph_container)
        self.hours_graph = SubjectGraphWidget()
        # self.hours_graph.setLabelVisible(False)
        self.hours_graph_container.setFixedWidth(475)
        self.hours_graph_container.setFixedHeight(300)
        hg_layout.addWidget(self.hours_graph)
        
        self.quality_chart_container = QFrame()
        self.quality_chart_container.setStyleSheet("background-color: rgba(30, 40, 50, 0.4); border-radius: 12px;")
        qc_layout = QVBoxLayout(self.quality_chart_container)
        self.quality_chart = QualityPieChart()
        self.quality_chart_container.setFixedWidth(300)
        self.quality_chart_container.setFixedHeight(300)
        qc_layout.addWidget(self.quality_chart)
        
        graphs_layout.addWidget(self.hours_graph_container, 3)
        graphs_layout.addWidget(self.quality_chart_container, 2)
        self.layout.addLayout(graphs_layout)

        # Tasks Section
        tasks_header = QLabel("Task Associate")
        tasks_header.setStyleSheet("color: white; font-weight: bold; font-size: 20px; margin-top: 10px;")
        self.layout.addWidget(tasks_header)
        
        self.tasks_list = QListWidget()
        self.tasks_list.setMinimumHeight(200)
        self.tasks_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(30, 40, 50, 0.4);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                padding: 10px;
                outline: none;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                color: #eceff1;
                font-size: 15px;
                border-radius: 6px;
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
            QListWidget::item:selected {
                background-color: rgba(0, 188, 212, 0.15);
                color: #00bcd4;
                border: 1px solid rgba(0, 188, 212, 0.3);
            }
        """)
        self.layout.addWidget(self.tasks_list)
        
        self.layout.addStretch()

    def load_details(self, subject):
        if subject is None:
            return
        
        self.current_subject = subject
        
        if isinstance(subject, str):
            name = subject
        elif isinstance(subject, dict):
            name = subject.get("name")
        else:
            name = getattr(subject, "name", "Sconosciuto")

        self.title.setText(name)

        details = self.viewmodel.get_subject_details(name) if self.viewmodel else {}
        
        if details:
            total_hours = details.get("total_hours", 0) or 0
            avg_quality = details.get("avg_quality", 0) or 0
            cfu = details.get("credits", 0) or 0
            
            self.card_hours.set_value(f"{total_hours:.1f}")
            self.card_quality.set_value(f"{avg_quality:.1f}")
            self.card_cfu.set_value(str(cfu))
            
            semester = details.get("semester", "-")
            year = details.get("year", "-")
            notes = details.get("notes", "")
            info_text = f"Anno {year} • Semestre {semester}"
            if notes:
                info_text += f"\nNote: {notes}"
            self.info_label.setText(info_text)

        if self.viewmodel:
            stats_over_time = self.viewmodel.get_subject_stats_over_time(name, days=14)
            self.hours_graph.update_data(stats_over_time)
            
            quality_dist = self.viewmodel.get_subject_quality_distribution(name)
            self.quality_chart.update_data(quality_dist)

        self.tasks_list.clear()
        if self.viewmodel:
            tasks = self.viewmodel.get_tasks_by_subject(name)
            if not tasks:
                self.tasks_list.addItem("Nessun task in sospeso per questa materia. Ottimo lavoro!")
            else:
                for task in tasks:
                    status = "✅" if task[6] else "⏳"
                    self.tasks_list.addItem(f"{status}  {task[2]}")

    @property
    def subject(self):
        return self.current_subject

    @subject.setter
    def subject(self, value):
        if value != self.current_subject:
            self.load_details(value)

    def edit_subject(self):
        if self.current_subject is None:
            return
        self._edit_window = NewSubjectWindow(viewmodel=self.viewmodel, subject=self.current_subject)
        self._edit_window.show()
        self._edit_window.raise_()
        self._edit_window.activateWindow()

    def delete_subject(self):
        name = self.current_subject.get("name") if isinstance(self.current_subject, dict) else self.current_subject
        subject_id = self.viewmodel.get_subject_id_by_name(name)
        if subject_id:
            self.viewmodel.delete_subject(subject_id)
