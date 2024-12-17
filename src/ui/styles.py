MAIN_WINDOW_STYLE = """
    QMainWindow {
        background-color: black;
    }
"""

CONSOLE_STYLE = """
    QTextEdit {
        background-color: black;
        color: #ffffff;
        font-family: 'Consolas';
        font-size: 14px;
        border: none;
        padding: 10px;
    }
    QTextEdit:vertical-scrollbar {
        width: 0px;
    }
    QScrollBar:vertical {
        border: none;
        background: black;
        width: 0px;
        margin: 0px;
    }
"""

INPUT_LINE_STYLE = """
    QLineEdit {
        background-color: black;
        color: #ffffff;
        font-family: 'Consolas';
        font-size: 14px;
        border: none;
        padding: 5px;
        margin: 0px 10px 10px 10px;
    }
"""

TOOLBAR_STYLE = """
    QWidget {
        background-color: rgba(30, 30, 30, 180);
        border: none;
    }
    QPushButton {
        background-color: rgba(60, 60, 60, 180);
        color: #ffffff;
        border: none;
        padding: 5px;
        margin: 2px;
        border-radius: 3px;
    }
    QPushButton:hover {
        background-color: rgba(80, 80, 80, 200);
    }
""" 