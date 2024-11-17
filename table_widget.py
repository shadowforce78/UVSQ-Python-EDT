import datetime
from PyQt5.QtWidgets import (
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)
from PyQt5.QtGui import QColor
from api_handler import fetch_event_details


class MainApp(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("Emploi du Temps - Visualisation")
        self.setGeometry(100, 100, 1300, 800)
        self.data = data
        self.initUI()

    def initUI(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.table = QTableWidget(self)
        self.table.setRowCount(44)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
        )
        self.table.setVerticalHeaderLabels(
            [f"{hour // 4}:{(hour % 4) * 15:02d}" for hour in range(32, 76)]
        )
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(20)
        self.table.horizontalHeader().setDefaultSectionSize(250)

        self.table.cellClicked.connect(self.on_cell_click)  # Connecter le clic
        self.populate_table(self.table)

        layout.addWidget(self.table)

    def populate_table(self, table):
        # Mapper les jours de la semaine à leurs colonnes
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

                # Calcul des lignes correspondantes
                start_row = (start_time.hour - 8) * 4 + start_time.minute // 15
                end_row = (end_time.hour - 8) * 4 + end_time.minute // 15
                duration = end_row - start_row

                # Affichage de la description informative
                description = (
                    f"{event['Début']} - {event['Fin']}\n"
                    f"{event['Module(s)']}\n"
                    f"{event['Professeur(s)']}"
                )

                # Création d'un item pour la cellule
                cell = QTableWidgetItem(description)

                # Stocker l'ID de l'événement dans les données internes
                cell.setData(0, event["ID"])

                # Appliquer la couleur de fond
                cell.setBackground(QColor(event["Couleur"]))

                # Étendre l'événement sur plusieurs lignes si nécessaire
                table.setSpan(start_row, column, duration, 1)
                table.setItem(start_row, column, cell)

    def on_cell_click(self, row, column):
        """
        Gère le clic sur une cellule.
        """
        cell = self.table.item(row, column)
        if cell is None:
            return

        event_id = cell.data(0)  # Récupérer l'ID stocké
        if event_id:
            details = fetch_event_details(event_id)
            if details:
                self.show_event_details(details)

    def show_event_details(self, details):
        """
        Affiche une boîte de dialogue avec les détails de l'événement.
        """
        elements = details.get("elements", [])
        message = "\n\n".join(
            f"{element['label']}: {element['content']}"
            for element in elements
            if element["content"]
        )

        QMessageBox.information(self, "Détails du cours", message)
