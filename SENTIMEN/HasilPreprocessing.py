import os
import time
import datetime
import traceback, sys
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QFileDialog, QDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from functools import partial
import pandas as pd

import json

current_dir = os.path.dirname(os.path.abspath('__file__'))
Form, Base = uic.loadUiType(os.path.join(current_dir, "UI/Preprocessing_UI.ui"))

import images_rc

class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data
        
    def rowCount(self, parent=None):
        return len(self._data.values)
    
    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return QtCore.QVariant(str(
            self._data.iloc[index.row()][index.column()]))
        return QtCore.QVariant()

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

#CLASS MAIN UTAMA #########====================================================#################
class Hasil(QDialog, Base, Form ):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.setupUi(self)

        #FULL SCREEN
        #self.showMaximized() 

        self.hasil = {}
    
    def _inisialisasi(self, hasil):
        self.dataset = hasil

        #Tampilkan Data
        self._tabelViewData()
    
    def _tabelViewData(self): 
        try:
            #CASE FOLDING
            cf = pd.DataFrame({'komentar_casefolding':self.dataset['komentar_casefolding']})
            modelCase = PandasModel(cf)
            #Interactive, Fixed, Stretch, ResizeToContents, Custom
            self.tableViewCaseFolding.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            self.tableViewCaseFolding.setModel(modelCase)
            self.tableViewCaseFolding.setWordWrap(True)

            #TOKENIZING
            t = pd.DataFrame({'komentar_tokenizing':self.dataset['komentar_tokenizing']})
            modelToken= PandasModel(t)
            #Interactive, Fixed, Stretch, ResizeToContents, Custom
            self.tableViewTokenizing.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            self.tableViewTokenizing.setModel(modelToken)
            self.tableViewTokenizing.setWordWrap(True)

            #STOPWORD
            s = pd.DataFrame({'komentar_stopword':self.dataset['komentar_stopword']})
            modelStopword= PandasModel(s)
            #Interactive, Fixed, Stretch, ResizeToContents, Custom
            self.tableViewStopword.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            self.tableViewStopword.setModel(modelStopword)
            self.tableViewStopword.setWordWrap(True)

            #STEMMING
            stem = pd.DataFrame({'komentar_stemming':self.dataset['komentar_stemming']})
            modelStemming= PandasModel(stem)
            #Interactive, Fixed, Stretch, ResizeToContents, Custom
            self.tableViewStemming.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            self.tableViewStemming.setModel(modelStemming)
            self.tableViewStemming.setWordWrap(True)
        except:
            return 1
    
    
############################## RUN ##############################################

def main():
    app=QApplication(sys.argv)
    window = Hasil()
    window.show()
    app.exec_()

if __name__ == '__main__':
    try:
        main()
    except Exception as why:
        print(why)