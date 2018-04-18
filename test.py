# -*- coding: utf-8 -*-

"""
PyQt5 tutorial 

This example shows a QCalendarWidget widget.

author: py40.com
last edited: 2017年3月
"""
import sys
from PyQt5.QtWidgets import (QWidget, QCalendarWidget,
                             QLabel, QApplication)
from PyQt5.QtCore import QDate


class Example(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        cal = QCalendarWidget(self)
        cal.setGridVisible(True)
        cal.move(20, 20)
        cal.clicked[QDate].connect(self.showDate)

        self.lbl = QLabel(self)
        date = cal.selectedDate()
        self.lbl.setText(date.toString())
        self.lbl.move(130, 260)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Calendar')
        self.show()

    def showDate(self, date):
        self.lbl.setText(date.toString())

import pickle
if __name__ == '__main__':
    dic = {
    "1.jpg": [[123, 254], [163, 248], [203, 229], [227, 204], [242, 181], [196, 201], [223, 167], [240, 147], [254, 129], \
    [174, 192], [205, 156], [224, 135], [237, 115], [155, 189], [179, 157], [196, 134], [211, 117], [138, 188], \
    [153, 161], [164, 145], [176, 131]],
    "3.jpg": [[163, 254], [163, 248], [203, 229], [227, 204], [242, 181], [196, 201], [223, 167], [240, 147], [254, 129], \
    [174, 192], [205, 156], [224, 135], [237, 115], [155, 189], [179, 157], [196, 134], [211, 117], [138, 188], \
    [153, 161], [164, 145], [176, 131]]

    }
    pickle.dump(dic, open("./OriPos","w"))
    # app = QApplication(sys.argv)
    # ex = Example()
    # sys.exit(app.exec_())