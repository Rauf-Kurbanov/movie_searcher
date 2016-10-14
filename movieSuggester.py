#! /usr/bin/env python

import sys
from PyQt4 import QtCore, QtGui, uic

designerQTFile = "layoutGUI.ui"

class MovieSuggester(QtGui.QWidget):
    def __init__(self):
        super(MovieSuggester, self).__init__()
        uic.loadUi(designerQTFile, self)
        self.show()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MovieSuggester()
    sys.exit(app.exec_())
