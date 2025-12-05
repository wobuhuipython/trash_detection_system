from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
from window.main_window import MainWindow
import sys

if __name__ == "__main__":
    try:
        QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    except Exception:
        pass

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())