import sys
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import *

qtCreatorFile = "mainwindow.ui"  # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)



class MyApp(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.confirm_n.clicked.connect(self.inputN)

        


    def inputN(self):
        n =  self.n.value()

        YOlayout =QVBoxLayout(self.Y0Area)

        for i in range(n):
            inputY0 = QDoubleSpinBox(self.Y0Area)
            YOlayout.addWidget(inputY0)
        self.Y0Area.setLayout(YOlayout)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
