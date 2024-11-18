import sys
import os
from PyQt5.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHeaderView,
    QPushButton,
    QComboBox,
    QAction
)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt
import datetime
from api_handler import fetch_event_details, fetch_and_format_data

class SuppressQtWarnings:
    def __enter__(self):
        self._stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr.close()
        sys.stderr = self._stderr

class MainApp(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("Emploi du Temps - Visualisation")
        self.setGeometry(100, 100, 1300, 800)  # Fenêtre de base
        self.data = data
        self.current_week_start = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
        self.current_class = "INF1-b2"  # Classe par défaut
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

        # Adapter la taille des colonnes à la largeur de la fenêtre
        self.table.horizontalHeader().setStretchLastSection(True)
        for col in range(self.table.columnCount()):
            self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)  # Utiliser QHeaderView

        self.table.cellClicked.connect(self.on_cell_click)  # Connecter le clic
        self.populate_table(self.table)

        self.prev_week_button = QPushButton("Semaine Précédente", self)
        self.next_week_button = QPushButton("Semaine Suivante", self)
        self.class_selector = QComboBox(self)
        self.class_selector.addItems([
            "INF1-A1", "INF1-A2", "INF1-B1", 
            "INF1-B2", "INF1-C1", "INF1-C2", 
            "INF2-FA", "INF2-FI-A", "INF2-FI-B",

            "MMI1-A1", "MMI1-A2", "MMI1-B1", 
            "MMI1-B2", "MMI2-A1", "MMI2-A2", 
            "MMI2-B1", "MMI2-B2",

            "RT1-FI-A1", "RT1-FI-A2", 
            "RT1-FI-B1", "RT1-FI-B2",

            "GEII1-TDA1", "GEII1-TDA2", "GEII1-TDB1"
            ])  # Example classes

        self.current_week_button = QPushButton("Semaine Actuelle", self)  # New button
        self.prev_week_button.clicked.connect(self.load_previous_week)
        self.next_week_button.clicked.connect(self.load_next_week)
        self.current_week_button.clicked.connect(self.load_current_week)  # Connect new button
        self.class_selector.currentIndexChanged.connect(self.change_class)

        self.dark_mode_action = QAction("Mode Sombre", self)
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.triggered.connect(self.toggle_dark_mode)
        self.menuBar().addAction(self.dark_mode_action)

        layout.addWidget(self.prev_week_button)
        layout.addWidget(self.next_week_button)
        layout.addWidget(self.current_week_button)  # Add new button to layout
        layout.addWidget(self.class_selector)
        layout.addWidget(self.table)

    def resizeEvent(self, event):
        # Ce bloc gère le redimensionnement de la fenêtre
        self.adjust_table_size()
        super().resizeEvent(event)

    def adjust_table_size(self):
        """
        Ajuste la taille des colonnes en fonction de la taille de la fenêtre.
        """
        total_width = self.table.viewport().width()
        column_count = self.table.columnCount()

        # Ajuste la taille de chaque colonne de manière égale
        column_width = total_width // column_count
        for col in range(column_count):
            self.table.setColumnWidth(col, column_width)

    def populate_table(self, table):
        table.clearContents()
        table.setRowCount(44)
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(
            ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
        )
        table.setVerticalHeaderLabels(
            [f"{hour // 4}:{(hour % 4) * 15:02d}" for hour in range(32, 76)]
        )

        # Clear existing spans
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                table.setSpan(row, col, 1, 1)

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
                with SuppressQtWarnings():
                    if duration > 1:
                        table.setSpan(start_row, column, duration, 1)  # Merge cells pour couvrir toute la durée
                table.setItem(start_row, column, cell)  # Placement de la cellule dans la table

    def on_cell_click(self, row, column):
        """
        Gère le clic sur une cellule pour récupérer les détails de l'événement.
        """
        cell = self.table.item(row, column)
        if cell is None:
            return

        event_id = cell.data(
            Qt.UserRole
        )  # Récupérer l'ID de l'événement stocké dans la cellule
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

    def load_previous_week(self):
        self.current_week_start -= datetime.timedelta(days=7)
        self.load_data()

    def load_next_week(self):
        self.current_week_start += datetime.timedelta(days=7)
        self.load_data()

    def change_class(self):
        self.current_class = self.class_selector.currentText()
        self.load_data()

    def load_data(self):
        start_date = self.current_week_start.strftime("%Y-%m-%d")
        end_date = (self.current_week_start + datetime.timedelta(days=6)).strftime("%Y-%m-%d")
        self.data = fetch_and_format_data(start_date, end_date, self.current_class)
        self.populate_table(self.table)

    def load_current_week(self):
        self.current_week_start = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
        self.load_data()

    def toggle_dark_mode(self):
        if self.dark_mode_action.isChecked():
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2e2e2e;
                    color: #ffffff;
                }
                QTableWidget {
                    background-color: #3e3e3e;
                    color: #ffffff;
                    alternate-background-color: #4e4e4e;
                }
                QHeaderView::section {
                    background-color: #3e3e3e;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #3e3e3e;
                    color: #ffffff;
                }
                QComboBox {
                    background-color: #3e3e3e;
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet("")
