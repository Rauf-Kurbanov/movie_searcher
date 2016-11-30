from PyQt4 import QtCore, QtGui


class AdvComboBox(QtGui.QComboBox):
    def __init__(self, parent=None):
        super(AdvComboBox, self).__init__(parent)

        self.setEditable(True)
        self.setInsertPolicy(QtGui.QComboBox.NoInsert)
        self.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)

        # add a filter model to filter matching items
        self.pFilterModel = QtGui.QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())

        # add a completer, which uses the filter model
        self.completer = QtGui.QCompleter(self.pFilterModel, self)
        # always show all (filtered) completions
        self.completer.setCompletionMode(QtGui.QCompleter.UnfilteredPopupCompletion)

        self.setCompleter(self.completer)

        self.lineEdit().textEdited[str].connect(self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.on_completer_activated)

    # on selection of an item from the completer, select the corresponding item from combobox
    def on_completer_activated(self, text):
        if text:
            index = self.findText(str(text))
            self.setCurrentIndex(index)
