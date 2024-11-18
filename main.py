import sys
import datetime
from PyQt5.QtWidgets import QApplication
from api_handler import fetch_and_format_data
from table_widget import MainApp  # Importation de MainWindow au lieu de MainApp


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Initial start and end dates
    start_date = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
    end_date = start_date + datetime.timedelta(days=6)
    class_name = "INF1-b2"

    # Récupération des données via l'API
    data = fetch_and_format_data(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), class_name)

    # Création et affichage de la fenêtre principale
    main_window = MainApp(data)
    main_window.show()

    # Boucle principale de l'application
    sys.exit(app.exec_())
