import sys
import sqlite3
import csv
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem


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
        an = analysis()
        if type(an.main_analysis(names)) == int:
            self.progressBar.setValue(an.main_analysis(names))
            self.Time.display(an.time(names)[0])
            if an.time(names)[1] == 1:
                self.time_label.setText('В выборе есть персонажи\n'
                                        'co слишком разным временем\n'
                                        'набора пика силы')
                self.time_label.show()
        else:
            self.error_label.setText(an.main_analysis(names))
            self.error_label.show()
        self.sf = SecondForm
        self.sf.insertion(self, names, an.main_analysis(names))

    def open_form(self):
        self.form = SecondForm()
        self.form.show()


class SecondForm(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('second_interface.ui', self)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(5)
        lst = ['pos1', 'pos2', 'pos3', 'pos4', 'pos5', 'res']
        self.con = sqlite3.connect('dota2_heroes.sqlite')
        self.cur = self.con.cursor()
        self.tableWidget.setHorizontalHeaderLabels(lst)
        for row in range(5):
            for col in range(6):
                item = str(list(self.cur.execute("""SELECT * FROM recentrequests"""))[row][col])
                self.tableWidget.setItem(row, col, QTableWidgetItem(item))

    def insertion(self, names, res):
        for i in [5, 4, 3, 2, 1]:
            if i > 1:
                ite = list(list(self.cur.execute("""SELECT * FROM recentrequests
                                                    WHERE id = ?""", (i - 1,)))[0])
            self.cur.execute("""UPDATE recentrequests
                                SET (pos1, pos2, pos3, pos4, pos5, res) = (?, ?, ?, ?, ?, ?)
                                WHERE id = ?""", (ite[0], ite[1], ite[2], ite[3], ite[4], ite[5], i))
        self.cur.execute("""UPDATE recentrequests
                            SET (pos1, pos2, pos3, pos4, pos5, res) = (?, ?, ?, ?, ?, ?)
                            WHERE id = 1""", (names[0], names[1], names[2], names[3], names[4], res))
        self.con.commit()


# Класс в котором производятся расчеты для анализа
class analysis(MainWindow):
    def __init__(self):
        super(analysis, self).__init__()

    def main_analysis(self, names):
        flag = 0
        for i in names:
            if i not in self.truenames1:
                return 'Ошибка: неверное имя персонажа - {}'.format(i)
            elif names.count(i) > 1:
                return 'Ошибка: в команде не может быть двух одинаковых персонажей({})'.format(i)
            else:
                flag += 1
        if flag == 5:
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
        if max(times) - min(times) >= 10:
            n = 1
        return [int(sum(times) / len(times)), n]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
