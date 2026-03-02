import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainter

app = QApplication(sys.argv)

series = QLineSeries()
series.append(0, 6)
series.append(2, 4)
series.append(3, 8)
series.append(7, 4)
series.append(10, 5)

chart = QChart()
chart.addSeries(series)
chart.createDefaultAxes()
chart.setTitle("Simple Line Chart")

chart_view = QChartView(chart)
chart_view.setRenderHint(QPainter.Antialiasing)

window = QMainWindow()
window.setCentralWidget(chart_view)
window.resize(600, 400)
window.show()

sys.exit(app.exec())