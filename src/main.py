import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import FakeConsole

def main():
    app = QApplication(sys.argv)
    ex = FakeConsole()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 