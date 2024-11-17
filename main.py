import sys
from PyQt5.QtWidgets import QApplication
from api_handler import fetch_and_format_data, getData
from table_widget import MainApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    data = fetch_and_format_data()
    main_app = MainApp(data)
    main_app.show()
    sys.exit(app.exec_())