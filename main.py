import sys
from PyQt5.QtWidgets import QApplication
from api_handler import fetch_and_format_data
from table_widget import MainApp  # Importation de MainWindow au lieu de MainApp


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Récupération des données via l'API
    data = fetch_and_format_data()
    
    # Création et affichage de la fenêtre principale
    main_window = MainApp(data)
    main_window.show()
    
    # Boucle principale de l'application
    sys.exit(app.exec_())