#! /usr/bin/env python
import sys
from PyQt4 import QtCore, QtGui, uic
from functools import partial

designerQTFile = "layoutGUI.ui"

def getWidgetsWithPrefix(layout, name = ""):
    return   [b for i in range(layout.count())
                for b in [layout.itemAt(i).widget()]
                if name in b.objectName()]

class MovieSuggester(QtGui.QWidget):
    def __init__(self):
        super(MovieSuggester, self).__init__()
        # Loads the xml and adds the fields to out object
        uic.loadUi(designerQTFile, self)

        self.sliderVals = self.getSliderValues()

        self.resetButton.clicked.connect(self.resetSliders)
        self.goButton.clicked.connect(self.runGo)
        # Connecting buttons of the movies to the function
        for b in getWidgetsWithPrefix(self.goLayout, "nameButton"):
            b.clicked.connect(self.itemClicked)





        self.show()

    def runGo(self):
        '''Does the Go thing (forms the new output on the left)'''
        pass

    def itemClicked(self):
        '''Whenever we click on a movie we load the description,
           pic from IMDB and set the tags for the movie'''
        button = self.sender()
        button.setText("Clicked")

    def getSliderValues(self):
        sliderVals = [x.value() for x in getWidgetsWithPrefix(self.tagValuesLayout)]
        return sliderVals

    def resetSliders(self):
        sliders = getWidgetsWithPrefix(self.tagValuesLayout)
        for (s, v) in zip(sliders, self.sliderVals):
            s.setValue(v)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)

    window = MovieSuggester()
    sys.exit(app.exec_())