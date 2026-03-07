# ui/components/sub_details.py
"""
Widget for displaying detailed information about a specific subject, 
including statistics, associated tasks, and options to edit or delete the subject.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, 
    QListWidget, QHBoxLayout, QPushButton,
    QFrame, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt
from ui.components.new_sub_window import NewSubjectWindow
from ui.components.subject_graph import SubjectGraphWidget, QualityPieChart

class SubDetails(QWidget):
    """
    Displays subject-specific details and provides management actions.
    
    Attributes:
        viewmodel (ViewModel): The business logic controller.
        current_subject (dict/str): Currently selected subject data.
    """
    def __init__(self, viewmodel=None):
        super().__init__()
        self.viewmodel = viewmodel
        self.current_subject = None

        self.main_layout = QVBoxLayout(self)
        
        # Scroll area for long content
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.layout = QVBoxLayout(self.scroll_content)
        self.layout.setSpacing(15)
        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll)

        # Toolbar layout: Title and management buttons
        toolbar = QHBoxLayout()
        self.title = QLabel("Seleziona una materia")
        self.title.setStyleSheet("font-weight: bold; font-size: 22px;")
        
        self.edit_button = QPushButton("Modifica")
        self.edit_button.clicked.connect(self.edit_subject)
        
        self.delete_button = QPushButton("Elimina")
        self.delete_button.clicked.connect(self.delete_subject)
        
        toolbar.addWidget(self.title)
        toolbar.addStretch()
        toolbar.addWidget(self.edit_button)
        toolbar.addWidget(self.delete_button)
        self.layout.addLayout(toolbar)

        # Stats Cards Layout: Displays aggregate metrics for the subject
        stats_container = QFrame()
        stats_container.setFrameShape(QFrame.StyledPanel)
        stats_container.setStyleSheet("border-radius: 10px; background-color: rgba(0,0,0,5);")
        stats_layout = QGridLayout(stats_container)
        
        self.total_hours_label = QLabel("0.00")
        self.total_hours_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.avg_quality_label = QLabel("0.0")
        self.avg_quality_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.cfu_label = QLabel("0")
        self.cfu_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        stats_layout.addWidget(QLabel("Ore Totali"), 0, 0, Qt.AlignCenter)
        stats_layout.addWidget(self.total_hours_label, 1, 0, Qt.AlignCenter)
        
        stats_layout.addWidget(QLabel("Qualità Media"), 0, 1, Qt.AlignCenter)
        stats_layout.addWidget(self.avg_quality_label, 1, 1, Qt.AlignCenter)
        
        stats_layout.addWidget(QLabel("CFU"), 0, 2, Qt.AlignCenter)
        stats_layout.addWidget(self.cfu_label, 1, 2, Qt.AlignCenter)
        
        self.layout.addWidget(stats_container)

        # Info section
        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("font-style: italic; color: gray;")
        self.layout.addWidget(self.info_label)

        # Graphs Section
        graphs_layout = QHBoxLayout()
        self.hours_graph = SubjectGraphWidget()
        self.hours_graph.setMinimumHeight(300)
        self.quality_chart = QualityPieChart()
        self.quality_chart.setMinimumHeight(300)
        
        graphs_layout.addWidget(self.hours_graph, 3)
        graphs_layout.addWidget(self.quality_chart, 2)
        self.layout.addLayout(graphs_layout)

        # Tasks Section: Lists tasks linked to this subject
        tasks_header = QLabel("Task Associate")
        tasks_header.setStyleSheet("font-weight: bold; font-size: 16px; margin-top: 10px;")
        self.layout.addWidget(tasks_header)
        
        self.tasks_list = QListWidget()
        self.tasks_list.setMinimumHeight(150)
        self.layout.addWidget(self.tasks_list)
        
        self.layout.addStretch()

    def load_details(self, subject):
        """
        Loads and displays details for the given subject.
        
        Args:
            subject (dict/str): Subject object or name to load.
        """
        if subject is None:
            return
        
        self.current_subject = subject
        
        # Normalize name extraction
        if isinstance(subject, str):
            name = subject
        elif isinstance(subject, dict):
            name = subject.get("name")
        else:
            name = getattr(subject, "name", "Sconosciuto")

        self.title.setText(name)

        # Fetch subject details from viewmodel
        details = self.viewmodel.get_subject_details(name) if self.viewmodel else {}
        
        if details:
            # Update Stats displays
            total_hours = details.get("total_hours", 0) or 0
            avg_quality = details.get("avg_quality", 0) or 0
            cfu = details.get("credits", 0) or 0
            
            self.total_hours_label.setText(f"{total_hours:.1f}")
            self.avg_quality_label.setText(f"{avg_quality:.1f}")
            self.cfu_label.setText(str(cfu))
            
            # Update Info metadata text
            semester = details.get("semester", "-")
            year = details.get("year", "-")
            notes = details.get("notes", "")
            info_text = f"Anno {year}, Semestre {semester}"
            if notes:
                info_text += f"\nNote: {notes}"
            self.info_label.setText(info_text)

        # Update Graphs
        if self.viewmodel:
            stats_over_time = self.viewmodel.get_subject_stats_over_time(name, days=14)
            self.hours_graph.update_data(stats_over_time)
            
            quality_dist = self.viewmodel.get_subject_quality_distribution(name)
            self.quality_chart.update_data(quality_dist)

        # Update associated tasks list
        self.tasks_list.clear()
        if self.viewmodel:
            tasks = self.viewmodel.get_tasks_by_subject(name)
            if not tasks:
                self.tasks_list.addItem("Nessun task per questa materia")
            else:
                for task in tasks:
                    # task format: (id, subject_id, title, desc, due, priority, completed)
                    status = "[✓]" if task[6] else "[ ]"
                    self.tasks_list.addItem(f"{status} {task[2]}")

    @property
    def subject(self):
        """The currently loaded subject."""
        return self.current_subject

    @subject.setter
    def subject(self, value):
        """Sets the current subject and triggers UI update."""
        if value != self.current_subject:
            self.load_details(value)

    def edit_subject(self):
        """Opens the edit window for the current subject."""
        if self.current_subject is None:
            return
        self._edit_window = NewSubjectWindow(viewmodel=self.viewmodel, subject=self.current_subject)
        self._edit_window.show()
        self._edit_window.raise_()
        self._edit_window.activateWindow()

    def delete_subject(self):
        """Deletes the current subject after confirming ID."""
        name = self.current_subject.get("name") if isinstance(self.current_subject, dict) else self.current_subject
        subject_id = self.viewmodel.get_subject_id_by_name(name)
        if subject_id:
            # Note: viewmodel.delete_subject should handle UI refreshment via signals
            self.viewmodel.delete_subject(subject_id)
