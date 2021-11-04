import sys
import sqlite3
import csv
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('interface.ui', self)
        self.Requests.clicked.connect(self.open_form)
        self.Clear.clicked.connect(self.clear)
        self.Analysis.clicked.connect(self.analysis)
        self.error_label.hide()
        self.time_label.hide()
        self.con = sqlite3.connect('dota2_heroes.sqlite')
        self.cur = self.con.cursor()
        truenames = list(self.cur.execute("""SELECT name FROM heroes"""))
        self.truenames1 = []
        for _ in truenames:
            self.truenames1.append(_[0])

    # Функция для сброса введенных данных
    def clear(self):
        self.Carry.setText('')
        self.Mid.setText('')
        self.Off.setText('')
        self.Four.setText('')
        self.Five.setText('')
        self.progressBar.setValue(0)
        self.Time.display(0)
        self.error_label.hide()
        self.time_label.hide()

    # Функция для анализа
    def analysis(self):
        self.error_label.hide()
        self.time_label.hide()
        carry = self.Carry.text()
        mid = self.Mid.text()
        off = self.Off.text()
        four = self.Four.text()
        five = self.Five.text()
        names = [carry, mid, off, four, five]
        an = analysis(names)
        if an.name_check(names):
            self.error_label.setText(an.name_check(names))
            self.error_label.show()
        else:
            self.progressBar.setValue(an.main_analysis(names))
            self.Time.display(an.time(names)[0])
            if an.time(names)[1]:
                self.time_label.setText('В пике есть персонажи со слишком большой '
                                        'разницей во времени набора пика силы')

    def open_form(self):
        self.form = SecondForm(self)
        self.form.show()


class SecondForm(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('second_interface.ui', self)


# Класс в котором производятся расчеты для анализа
class analysis(MainWindow):
    def __init__(self, names):
        super(analysis, self).__init__()
        self.names = names

    def name_check(self, names):
        for i in names:
            if i not in self.truenames1:
                return 'Ошибка: неверное имя персонажа - {}'.format(i)
            elif names.count(i) > 1:
                return 'Ошибка: в команде не может быть двух одинаковых персонажей({})'.format(i)
            else:
                return False

    def main_analysis(self, names):
        with open('ideal_parameters.csv', encoding='utf-8') as csvfile:
            reader = list(csv.reader(csvfile, delimiter=';'))
        ideal_parameters = list(int(i[1]) for i in reader)
        inp_parameters = [0, 0, 0, 0, 0]
        cnt = 1
        res = 0
        for n in names:
            inp_parameters[0] += list(self.cur.execute("""SELECT farm FROM heroes
                                                WHERE name = ?""", (n,)))[0][0]
            inp_parameters[1] += list(self.cur.execute("""SELECT meta FROM heroes
                                                WHERE name = ?""", (n,)))[0][0]
            inp_parameters[2] += list(self.cur.execute("""SELECT front FROM heroes
                                                WHERE name = ?""", (n,)))[0][0]
            inp_parameters[3] += list(self.cur.execute("""SELECT lane FROM heroes
                                                WHERE name = ?""", (n,)))[0][0]
            inp_parameters[4] += list(self.cur.execute("""SELECT active_sup FROM heroes
                                                WHERE name = ?""", (n,)))[0][0]
        if inp_parameters[0] - ideal_parameters[0] <= 0:
            res += 20
        else:
            res += ((inp_parameters[0] - ideal_parameters[0]) / ideal_parameters[0]) * 20
        for i in inp_parameters[1:]:
            if i >= ideal_parameters[cnt]:
                res += 20
            else:
                res += (i / ideal_parameters[cnt]) * 20
            cnt += 1
        return int(res)

    def time(self, names):
        times = []
        for _ in names[:3]:
            times.append(list(self.cur.execute("""SELECT time FROM heroes
                                                            WHERE name = ?""", (_,)))[0][0])
        n = 0
        if max(times) - min(times) > 10:
            n = 1
        return [int(sum(times) / len(times)), n]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
