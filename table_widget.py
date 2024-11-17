from PyQt5.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QMainWindow,
    QWidget,
    QVBoxLayout,
)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt
import datetime
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
        # Mapping des jours de la semaine avec leurs indices de colonne
        day_to_column = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
        }

        # Parcours des événements par date
        for date, events in self.data.items():
            # On extrait le jour de la semaine à partir de la date (par exemple "2024-11-14" => "Thursday")
            day_name = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%A")

            if day_name not in day_to_column:
                continue  # Si le jour n'est pas dans notre tableau (pas de classe ce jour-là)

            # Calcul de la colonne correspondante pour chaque jour
            column = day_to_column[day_name]

            # On boucle sur tous les événements de cette journée
            for event in events:
                # Récupération des informations de l'événement
                event_id = event["ID"]
                start_time_str = event["Début"].replace(" ", "")
                end_time_str = event["Fin"].replace(" ", "")
                # Convertir en objet datetime
                start_time = datetime.datetime.strptime(start_time_str, "%H:%M")
                end_time = datetime.datetime.strptime(end_time_str, "%H:%M")

                # Calcul de la ligne à partir de l'heure de début et de fin (ici 8h00 -> ligne 0)
                start_row = (start_time.hour - 8) * 4 + start_time.minute // 15
                end_row = (end_time.hour - 8) * 4 + end_time.minute // 15
                duration = end_row - start_row  # Durée en lignes

                # Description à afficher dans la cellule (on concatène plusieurs infos)
                description = f"{event['Début']} - {event['Fin']}\n{event['Module(s)']}\n{event['Professeur(s)']}"

                # Création de la cellule
                cell = QTableWidgetItem(description)
                cell.setBackground(QColor(event["Couleur"]))  # Couleur de l'événement
                cell.setData(
                    Qt.UserRole, event_id
                )  # On stocke l'ID de l'événement dans la cellule

                # Insertion de la cellule dans la bonne ligne et colonne, en tenant compte de la durée de l'événement
                table.setSpan(
                    start_row, column, duration, 1
                )  # Merge cells pour couvrir toute la durée
                table.setItem(
                    start_row, column, cell
                )  # Placement de la cellule dans la table

                # print(
                #     f"Inserting event {event_id} at row {start_row}, column {column}: {description}"
                # )

    def on_cell_click(self, row, column):
        """
        Gère le clic sur une cellule pour récupérer les détails de l'événement.
        """
        cell = self.table.item(row, column)
        if cell is None:
            return

        event_id = cell.data(
            Qt.UserRole
        )  # Récupérer l'ID de l'événement à partir de la cellule
        if not event_id:
            return  # Aucun ID, donc on ne fait rien

        try:
            details = fetch_event_details(event_id)
            if details:
                self.show_event_details(details)
            else:
                QMessageBox.warning(
                    self, "Erreur", "Aucun détail trouvé pour cet événement."
                )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {str(e)}")

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
