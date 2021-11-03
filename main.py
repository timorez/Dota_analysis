import sys
import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('interface.ui', self)
        self.Requests.clicked.connect(self.open_form)
        self.Clear.clicked.connect(self.clear)
        self.Analysis.clicked.connect(self.analysis)

    # Функция для сброса введенных данных
    def clear(self):
        self.Carry.setText('')
        self.Mid.setText('')
        self.Off.setText('')
        self.Four.setText('')
        self.Five.setText('')
        self.progressBar.setValue(0)
        self.Time.display(0)

    # Функция для анализа
    def analysis(self):
        carry = self.Carry.Text()
        mid = self.Mid.Text()
        off = self.Off.Text()
        four = self.Four.Text()
        five = self.Five.Text()
        names = [carry, mid, off, four, five]
        an = analysis(names)

    def open_form(self):
        self.form = SecondForm(self)
        self.form.show()


class SecondForm(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('second_interface.ui', self)


# Класс в котором производятся расчеты для анализа
class analysis:
    def __init__(self, names):
        self.names = names


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
