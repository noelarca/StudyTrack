from PySide6.QtCharts import (
    QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis,
    QPieSeries, QPieSlice
)
from PySide6.QtCore import Qt, QDateTime, QDate
from PySide6.QtGui import QPainter, QColor, QPen, QFont

class SubjectGraphWidget(QChartView):
    """
    A widget that displays a line chart of study hours over time for a subject.
    Adapts to dark theme.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setStyleSheet("background: transparent;")
        
        self.chart = QChart()
        # Set a built-in dark theme that matches qt-material's dark blue
        self.chart.setTheme(QChart.ChartThemeDark)
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.legend().hide()
        self.chart.setBackgroundVisible(False) # Make it transparent to show underlying UI
        
        self.setChart(self.chart)
        
        self.series = QLineSeries()
        # Customizing the line color to a nice cyan/blue
        pen = QPen(QColor("#00bcd4"))
        pen.setWidth(3)
        self.series.setPen(pen)
        self.chart.addSeries(self.series)
        
        # Axis X (Time)
        self.axis_x = QDateTimeAxis()
        self.axis_x.setFormat("dd/MM")
        self.axis_x.setTitleText("Data")
        self.axis_x.setLabelsColor(QColor("white"))
        self.axis_x.setTitleBrush(QColor("white"))
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.series.attachAxis(self.axis_x)
        
        # Axis Y (Hours)
        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("Ore")
        self.axis_y.setLabelFormat("%.1f")
        self.axis_y.setLabelsColor(QColor("white"))
        self.axis_y.setTitleBrush(QColor("white"))
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_y)

    def update_data(self, stats_data):
        self.series.clear()
        
        if not stats_data:
            self.chart.setTitle("Nessun dato di studio negli ultimi 14 giorni")
            return
            
        self.chart.setTitle("Ore di studio (Ultimi 14 giorni)")
        
        min_date = None
        max_date = None
        max_hours = 1.0
        
        for date_str, hours in stats_data:
            qdate = QDate.fromString(date_str, "yyyy-MM-dd")
            qdatetime = QDateTime(qdate, Qt.LocalTime)
            msecs = qdatetime.toMSecsSinceEpoch()
            
            self.series.append(msecs, hours)
            
            if min_date is None or qdatetime < min_date:
                min_date = qdatetime
            if max_date is None or qdatetime > max_date:
                max_date = qdatetime
            if hours > max_hours:
                max_hours = hours
                
        if min_date and max_date:
            if min_date == max_date:
                min_date = min_date.addDays(-1)
                max_date = max_date.addDays(1)
            
            self.axis_x.setRange(min_date, max_date)
            self.axis_y.setRange(0, max_hours * 1.2)
        
        self.axis_x.setTickCount(min(len(stats_data), 7))

class QualityPieChart(QChartView):
    """
    A widget that displays a pie chart of study session quality distribution.
    Adapts to dark theme.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setStyleSheet("background: transparent;")
        
        self.chart = QChart()
        self.chart.setTheme(QChart.ChartThemeDark)
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setBackgroundVisible(False)
        self.chart.legend().setAlignment(Qt.AlignRight)
        self.chart.legend().setLabelColor(QColor("white"))
        self.setChart(self.chart)
        
        self.series = QPieSeries()
        self.chart.addSeries(self.series)

    def update_data(self, distribution):
        self.series.clear()
        
        if not distribution:
            self.chart.setTitle("Nessun dato sulla qualità")
            return
            
        self.chart.setTitle("Qualità delle sessioni")
        
        # Quality labels and more vibrant colors for dark theme
        labels = {1: "Scarsa", 2: "Sufficiente", 3: "Buona", 4: "Ottima", 5: "Eccellente"}
        colors = {
            1: QColor("#ff5252"), # Vibrant Red
            2: QColor("#ffab40"), # Vibrant Orange
            3: QColor("#ffff8d"), # Vibrant Yellow
            4: QColor("#b2ff59"), # Vibrant Light Green
            5: QColor("#69f0ae")  # Vibrant Green
        }
        
        for quality in sorted(distribution.keys()):
            count = distribution[quality]
            label = labels.get(quality, f"Livello {quality}")
            slice = self.series.append(f"{label}", count)
            slice.setBrush(colors.get(quality, QColor("gray")))
            slice.setLabelVisible(True)
            slice.setLabelColor(QColor("white"))
            
        if self.series.slices():
            largest = max(self.series.slices(), key=lambda s: s.value())
            largest.setExploded(True)
