import datetime
from PyQt5.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from PyQt5.QtGui import QColor


class MainApp(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("Emploi du Temps - Visualisation")
        self.setGeometry(100, 100, 1300, 800)
        self.data = data
        self.initUI()

    def initUI(self):
        # Widget principal
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Layout principal
        layout = QVBoxLayout(central_widget)

        # Tableau pour l'emploi du temps
        table = QTableWidget(self)
        table.setRowCount(44)  # 44 lignes : 8h -> 19h
        table.setColumnCount(5)  # Lundi à Vendredi
        table.setHorizontalHeaderLabels(["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"])
        table.setVerticalHeaderLabels(
            [f"{hour // 4}:{(hour % 4) * 15:02d}" for hour in range(32, 76)]
        )
        table.setEditTriggers(QTableWidget.NoEditTriggers)  # Empêche l'édition
        table.setAlternatingRowColors(True)

        # Ajuster la taille des cellules
        table.verticalHeader().setDefaultSectionSize(20)  # Hauteur des lignes
        table.horizontalHeader().setDefaultSectionSize(250)  # Largeur des colonnes

        # Remplir le tableau
        self.populate_table(table)

        layout.addWidget(table)

    def populate_table(self, table):
        day_to_column = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
        }

        for day, events in self.data.items():
            day_name = datetime.datetime.strptime(day, "%Y-%m-%d").strftime("%A")
            if day_name not in day_to_column:
                continue

            column = day_to_column[day_name]

            for event in events:
                start_time = datetime.datetime.strptime(event["Début"], "%H:%M")
                end_time = datetime.datetime.strptime(event["Fin"], "%H:%M")

                start_row = (start_time.hour - 8) * 4 + start_time.minute // 15
                end_row = (end_time.hour - 8) * 4 + end_time.minute // 15
                duration = end_row - start_row

                description = f"{event['Début']} - {event['Fin']}\n{event['Module(s)']}\n{event['Professeur(s)']}"
                cell = QTableWidgetItem(description)
                cell.setBackground(QColor(event["Couleur"]))
                table.setSpan(start_row, column, duration, 1)
                table.setItem(start_row, column, cell)
