#! /usr/bin/env python
import sys
from PyQt4 import QtCore, QtGui, uic
from suggester.suggester import Suggester
from internet.movies import imdb_descr_and_poster_from_title

designerQTFile = "gui/layoutGUI.ui"


def getWidgetsWithPrefix(layout, name=""):
    return [b for i in range(layout.count())
            for b in [layout.itemAt(i).widget()]
            if name in b.objectName()]


class MovieSuggester(QtGui.QWidget):
    def __init__(self, suggester):
        super(MovieSuggester, self).__init__()
        # Loads the xml and adds the fields to out object
        uic.loadUi(designerQTFile, self)

        self.sliderVals = self.getSliderValues()

        self.resetButton.clicked.connect(self.resetSliders)
        self.goButton.clicked.connect(self.runGo)
        # Connecting buttons of the movies to the function
        for b in getWidgetsWithPrefix(self.goLayout, "nameButton"):
            b.clicked.connect(self.itemClicked)

        self.suggester = suggester

        self.rec6 = self.suggester.getInitialRecs()
        self.selected_movie = self.rec6[0]
        self.populateButtons(self.rec6)
        self.setTags(self.suggester.getTopTags(self.selected_movie))
        self.populateMovieDescr()

        self.show()

    def runGo(self):
        """Does the Go thing (forms the new output on the left)"""
        self.rec6 = self.suggester.getNextRecs(self.selected_movie, self.getTags())
        self.populateButtons(self.rec6)

    def populateMovieDescr(self):
        # Stupid naming in the dataset
        descr, pic = imdb_descr_and_poster_from_title(
            self.selected_movie.rsplit('(', 1)[0]
                               .rsplit(',', 1)[0])
        self.movieSummary.setText(descr)

        image = QtGui.QImage()
        image.loadFromData(pic)
        self.moviePicture.setPixmap(QtGui.QPixmap(image))

    def itemClicked(self):
        """Whenever we click on a movie we load the description,
           pic from IMDB and set the tags for the movie"""
        button = self.sender()
        self.selected_movie = button.text()
        self.setTags(self.suggester.getTopTags(self.selected_movie))
        self.populateMovieDescr()

    def getSliderValues(self):
        sliderVals = [x.value() for x in getWidgetsWithPrefix(self.tagValuesLayout)]
        return sliderVals

    def populateButtons(self, buttonNames):
        """Gets button names and sets them"""
        for (b, n) in zip(getWidgetsWithPrefix(self.goLayout, "nameButton"), buttonNames):
            b.setText(n)

    def resetSliders(self):
        sliders = getWidgetsWithPrefix(self.tagValuesLayout)
        for (s, v) in zip(sliders, self.sliderVals):
            s.setValue(v)

    def getTags(self):
        """Returns a pair of lists - tagNames and tagVals"""
        tagVals = self.getSliderValues()
        tags = getWidgetsWithPrefix(self.tagNamesLayout)
        ret = []
        for s in tags:
            ret.append(s.text())
        return ret, tagVals

    def setTags(self, tags):
        tag_names, self.sliderVals = tags
        self.resetSliders()
        self._setTagNames(tag_names)

    def _setTagNames(self, tag_names):
        tags = getWidgetsWithPrefix(self.tagNamesLayout)
        for (s, v) in zip(tags, tag_names):
            s.setText(v)

def main():
    app = QtGui.QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)

    suggester = Suggester()

    window = MovieSuggester(suggester)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
