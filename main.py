import sys
import json
import datetime
import requests
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtGui import QColor


# --- Configuration API ---
endPointUrl = "https://edt.iut-velizy.uvsq.fr/Home/GetCalendarData"

headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
}

start = "2024-11-11"
end = "2024-11-16"
resType = 103
calView = "agendaWeek"
federationIds = ["INF1-B"]
colourScheme = 3

body = {
    "start": start,
    "end": end,
    "resType": resType,
    "calView": calView,
    "federationIds": federationIds,
    "colourScheme": colourScheme,
}


def format_events(events):
    formatted_data = {}

    for event in events:
        # Conversion des dates au format lisible
        start_time = datetime.datetime.fromisoformat(event["start"])
        end_time = datetime.datetime.fromisoformat(event["end"])

        # Extraction des infos principales
        event_info = {
            "Début": start_time.strftime("%H:%M"),
            "Fin": end_time.strftime("%H:%M"),
            "Description": event["description"].replace("<br />", "\n")
            .replace("&39;", "'")
            .strip(),
            "Professeur(s)": event["description"].split("<br />")[0],  # Prof principal
            "Module(s)": ", ".join(event["modules"]) if event["modules"] else "Non spécifié",
            "Type": event["eventCategory"],
            "Site": ", ".join(event["sites"]) if event["sites"] else "Non spécifié",
            "Couleur": event["backgroundColor"],
        }

        # Classement par jour
        date_str = start_time.strftime("%Y-%m-%d")
        if date_str not in formatted_data:
            formatted_data[date_str] = []

        formatted_data[date_str].append(event_info)

    return formatted_data


def fetch_and_format_data():
    # Récupération des données depuis l'API
    response = requests.post(endPointUrl, headers=headers, data=body)
    formatedResponse = json.loads(response.text)
    formatted_data = format_events(formatedResponse)
    return formatted_data


# --- Application PyQt ---
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Emploi du Temps - Visualisation")
        self.setGeometry(100, 100, 1200, 800)

        # Récupération des données
        self.data = fetch_and_format_data()

        # Initialisation du tableau
        self.initUI()

    def initUI(self):
        # Widget principal
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Layout principal
        layout = QVBoxLayout(central_widget)

        # Tableau pour l'emploi du temps
        table = QTableWidget(self)

        # 4 colonnes par heure x 12 heures = 48 lignes (8h -> 20h)
        table.setRowCount(48)
        table.setColumnCount(7)  # Lundi à Dimanche
        table.setHorizontalHeaderLabels(["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"])
        table.setVerticalHeaderLabels(
            [f"{hour // 4}:{(hour % 4) * 15:02d}" for hour in range(32, 80)]  # 8h à 20h (15 min)
        )
        table.setEditTriggers(QTableWidget.NoEditTriggers)  # Empêche l'édition
        table.setAlternatingRowColors(True)

        # Remplir le tableau
        self.populate_table(table)

        layout.addWidget(table)

    def populate_table(self, table):
        # Mapper les jours de la semaine à leurs colonnes
        day_to_column = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 5,
            "Sunday": 6,
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

                # Ajouter l'événement dans les cases correspondantes
                description = f"{event['Début']} - {event['Fin']}\n{event['Module(s)']}\n{event['Professeur(s)']}"
                cell = QTableWidgetItem(description)

                # Appliquer la couleur
                cell.setBackground(QColor(event["Couleur"]))
                table.setSpan(start_row, column, duration, 1)  # Étendre sur plusieurs lignes
                table.setItem(start_row, column, cell)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())
