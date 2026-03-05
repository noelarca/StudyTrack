from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, 
    QListWidget, QHBoxLayout, QPushButton
)
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from PySide6.QtCore import Qt, QDateTime, QPointF
from PySide6.QtGui import QPainter
from ui.components.new_sub_window import NewSubjectWindow

class SubjectChart(QChartView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.legend().hide()
        self.setChart(self.chart)
        
        self.series = QLineSeries()
        self.chart.addSeries(self.series)
        
        self.axis_x = QDateTimeAxis()
        self.axis_x.setFormat("dd/MM")
        self.axis_x.setTitleText("Data")
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.series.attachAxis(self.axis_x)
        
        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("Ore")
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_y)

    def update_data(self, data):
        self.series.clear()
        if not data:
            return
            
        min_date = None
        max_date = None
        max_hours = 0
        
        for date_str, hours in data:
            dt = QDateTime.fromString(date_str, "yyyy-MM-dd")
            self.series.append(dt.toMSecsSinceEpoch(), hours)
            
            if min_date is None or dt < min_date:
                min_date = dt
            if max_date is None or dt > max_date:
                max_date = dt
            if hours > max_hours:
                max_hours = hours
                
        if min_date and max_date:
            self.axis_x.setRange(min_date, max_date)
            # Aggiungiamo un po' di padding alla Y
            self.axis_y.setRange(0, max_hours * 1.2 if max_hours > 0 else 1)

class SubDetails(QWidget):
    def __init__(self, viewmodel=None):
        super().__init__()
        self.viewmodel = viewmodel
        self.current_subject = None  # Store the currently displayed subject for editing purposes

        self.layout = QVBoxLayout(self)

        option_buttons_layout = QHBoxLayout()

        self.edit_button = QPushButton("Modifica")
        self.edit_button.clicked.connect(self.edit_subject)
        self.delete_button = QPushButton("Elimina")
        self.delete_button.clicked.connect(self.delete_subject) 
        option_buttons_layout.addWidget(self.edit_button)
        option_buttons_layout.addWidget(self.delete_button)
        
        self.layout.addLayout(option_buttons_layout)
        
        self.title = QLabel("Dettagli materia:")
        self.title.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.layout.addWidget(self.title)

        # Container per i dettagli testuali
        self.details_list = QListWidget()
        self.details_list.setMaximumHeight(150)
        self.layout.addWidget(self.details_list)

        # Aggiunta del grafico
        self.chart_label = QLabel("Andamento studio (ultimi 7 giorni):")
        self.chart_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.layout.addWidget(self.chart_label)
        
        self.chart_view = SubjectChart()
        self.layout.addWidget(self.chart_view)

    def load_details(self, subject):
        # Accept either an explicit subject or use current_subject
        if subject is None:
            subject = getattr(self, "current_subject", None)
        else:
            self.current_subject = subject

        self.details_list.clear()

        # Determine a name to show in the title
        if isinstance(subject, str):
            name = subject
        elif isinstance(subject, dict):
            name = subject.get("name") or subject.get("title") or str(subject)
        else:
            name = getattr(subject, "name", None) or getattr(subject, "title", None) or str(subject)

        self.title.setText(f"{name}")

        details = self.viewmodel.get_subject_details(name) if self.viewmodel else {}
        if details:
            for key, value in details.items():
                if key in ["id", "name"]: continue
                label = "CFU" if key == "credits" else key.capitalize()
                if key == "total_hours": label = "Ore Totali"
                if key == "avg_quality": label = "Qualità Media"
                
                # Format floats
                if isinstance(value, float):
                    value = f"{value:.2f}"
                
                self.details_list.addItem(f"{label}: {value}")

        # Carica i dati per il grafico
        if self.viewmodel:
            stats = self.viewmodel.get_subject_stats_over_time(name, days=7)
            self.chart_view.update_data(stats)

    @property
    def subject(self):
        return getattr(self, "current_subject", None)

    @subject.setter
    def subject(self, value):
        if value != getattr(self, "current_subject", None):
            self.current_subject = value
            self.load_details(value)
            if self.viewmodel and hasattr(self.viewmodel, "select_subject"):
                try:
                    # Se value è un dict, passa il nome
                    name = value.get("name") if isinstance(value, dict) else value
                    self.viewmodel.select_subject(name)
                except Exception:
                    pass

    def edit_subject(self):
        # keep a reference so the window doesn't get garbage collected immediately
        print("Edit subject:", self.current_subject)
        # if there is no subject selected, nothing to edit
        if self.current_subject is None:
            return

        # create/edit window and store it on the instance
        self._edit_window = NewSubjectWindow(viewmodel=self.viewmodel, subject=self.current_subject)
        self._edit_window.show()
        # ensure the window is brought to front
        try:
            self._edit_window.raise_()
            self._edit_window.activateWindow()
        except Exception:
            pass

    def delete_subject(self):
        name = self.current_subject.get("name") if isinstance(self.current_subject, dict) else self.current_subject
        self.subject_id = self.viewmodel.get_subID_by_name(name) if name else None
        if self.subject_id is None:
            return
        else:
            print("Attempting to delete subject with ID:", self.subject_id)
            self.viewmodel.delete_subject(self.subject_id)
