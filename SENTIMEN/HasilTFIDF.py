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
Form, Base = uic.loadUiType(os.path.join(current_dir, "UI/TFIDF_UI.ui"))

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

#CLASS HASIL TFIDF #########====================================================#################
class HasilTFIDF(QDialog, Base, Form ):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.setupUi(self)

        #FULL SCREEN
        #self.showMaximized() 

        self.dataTFIDF = {}
    
    def _inisialisasi(self):
        self.dataTFIDF = pd.read_excel("OUTPUT/TFIDF.xlsx")

        #Tampilkan Data
        self._tabelViewData()

    
    def _tabelViewData(self): 
        try:
            modelTFIDF = PandasModel(self.dataTFIDF)
            #Interactive, Fixed, Stretch, ResizeToContents, Custom
            self.tableViewTFIDF.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
            self.tableViewTFIDF.setModel(modelTFIDF)
            self.tableViewTFIDF.setWordWrap(True)
        except:
            return 1
    
    
############################## RUN ##############################################

def main():
    app=QApplication(sys.argv)
    window = HasilTFIDF()
    window._inisialisasi()
    window.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
    window.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
    window.exec_()

if __name__ == '__main__':
    try:
        main()
    except Exception as why:
        print(why)