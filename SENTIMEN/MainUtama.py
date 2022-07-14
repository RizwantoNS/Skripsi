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
import pandas as pd

import json

from functools import partial
import re
import math
from statistics import mean

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

# Python program to show time by process_time() 
from time import process_time

current_dir = os.path.dirname(os.path.abspath('__file__'))
Form, Base = uic.loadUiType(os.path.join(current_dir, "UI/MainUtama_UI.ui"))

import images_rc

from Preprocessing import Preprocessing
from TFIDF import TFIDF
from SVM import SVM
from HasilPreprocessing import Hasil
from HasilTFIDF import HasilTFIDF
from HasilSVM import HasilSVM

#CLASS SUB PROSES
class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.
    Supported signals are:
    - finished: No data
    - error:`tuple` (exctype, value, traceback.format_exc() )
    - result: `object` data returned from processing, anything
    - progress: `tuple` indicating progress metadata
    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(tuple)


class Worker(QRunnable):
    '''
    Worker thread
    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    '''
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done

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
class MainUtama(Base, Form):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.setupUi(self)

        #FULL SCREEN
        self.showMaximized() 
        
        #DEKLARASI
        self.counter = 0
        self.pilihFile = {}
        self.extension = {}
        self.dataset = {}
        self.hasilPreprocessing = {}
        self.hasilTFIDF = {}
        self.hasilSVM = {}
        self.modelSVM = {}
        
        self.threadpool = QThreadPool()
        
        self.btnPilihFile.clicked.connect(self._pilihFile)
        self.btnProses.clicked.connect(self._proses)
        self.btnHasilPreprocessing.clicked.connect(self._hasilPreprocessing)
        self.btnHasilTFIDF.clicked.connect(self._hasilTFIDF)
        self.btnHasilSVM.clicked.connect(self._hasilSVM)
        self._setButton()
        self.btnProses.setEnabled(False)
    
    def _setButton(self, ena=False):
        self.btnHasilPreprocessing.setEnabled(ena)
        self.btnHasilTFIDF.setEnabled(ena)
        self.btnHasilSVM.setEnabled(ena)
    
    def _pilihFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Excel (*.xlsx);;CSV (*.csv)", options=options)
        if fileName:
            self.txtPilihFile.setText("")
            self._setButton()
            self.btnProses.setEnabled(False)
            filename, file_extension = os.path.splitext(fileName)
            self.pilihFile  = fileName
            self.extension = file_extension
            
            # Pass the function to execute
            worker = Worker(self.execute_this_fn) # Any other args, kwargs are passed to the run function
            worker.signals.finished.connect(self.thread_complete)
            worker.signals.progress.connect(self.progress_fn)

            # Execute
            self.threadpool.start(worker)
        else:
            return 1
    
    #PROGRESS BERJALAN
    def progress_fn(self, progress):
        p, m = (progress)
        persen = math.floor(p)
        self.pB.setValue(persen)
        self.pB.setFormat("{} ({}%)".format(m, persen))
    
    def execute_this_fn(self, progress_callback):
        jmlProses = 3
        n = 0
        progress_callback.emit((n*100/jmlProses, 'Loading ...'))
        
        n += 1
        persen = n*100/jmlProses
        progress_callback.emit((persen, "Baca File"))
        if self.extension==".csv":
            self.dataset = pd.read_csv(self.pilihFile, sep=';')
        elif self.extension==".xlsx":
            self.dataset = pd.read_excel(self.pilihFile)
        
        n += 1
        persen = n*100/jmlProses
        self._tabelViewData()
        progress_callback.emit((persen, "Loading Data ..."))

        time.sleep(0)
        n += 1
        persen = n*100/jmlProses
        progress_callback.emit((persen, "Done!!!"))
    
    def thread_complete(self):
        self.btnProses.setEnabled(True)
        
    def recurring_timer(self):
        self.counter +=1
        jam = str(datetime.timedelta(seconds=self.counter))
    
    def _tabelViewData(self): 
        try:
            modelDataset = PandasModel(self.dataset)
            #Interactive, Fixed, Stretch, ResizeToContents, Custom
            self.tableViewData.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
            self.tableViewData.setModel(modelDataset)
            self.tabelViewData.setWordWrap(True)
        except:
            return 1
    
    #KLIK PROSES
    def _proses(self):
        # PROSES PREPROCESSING dan SVM
        worker = Worker(self._eksekusi)
        worker.signals.finished.connect(self._prosesComplete)
        worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.threadpool.start(worker)
        self._setButton()
    
    def _prosesComplete(self):
        self._setButton(True)
    
    def _eksekusi(self, progress_callback):
        jmlProses = 4
        n = 0
        progress_callback.emit((n*100/jmlProses, 'Loading Proses ...'))
        
        n += 1
        persen = n*100/jmlProses
        progress_callback.emit((persen, "Preprocessing ..."))
        self.hasilPreprocessing = self._preProcessing()

        n += 1
        persen = n*100/jmlProses
        progress_callback.emit((persen, "TFIDF ..."))
        self.hasilTFIDF = self._tfidf()
        
        n += 1
        persen = n*100/jmlProses
        progress_callback.emit((persen, "SVM ..."))
        self.hasilSVM = self._svm()

        n += 1
        persen = n*100/jmlProses
        progress_callback.emit((persen, "Done!!!"))

    def _preProcessing(self):
        self.proses = Preprocessing()
        
        hasil_proses = self.proses._inisialisasi(self.dataset)
        hasil_proses = hasil_proses.reset_index(drop=True)
        #SIMPAN EXCEL
        hasil_proses.to_excel("OUTPUT/Text_Preprocessing.xlsx", index=False)

        return hasil_proses
    
    def _tfidf(self):
        _prosesTFIDF = TFIDF()
        return _prosesTFIDF._inisialisasi(self.hasilPreprocessing)
    
    def _svm(self):
        _prosesSVM = SVM()
        self.modelSVM = _prosesSVM._inisialisasi()
    
    #LIHAT HASIL PREPROCESSING
    def _hasilPreprocessing(self):
        windowHP = Hasil()
        windowHP._inisialisasi(self.hasilPreprocessing)
        #windowHP.showFullScreen()
        windowHP.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        windowHP.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        windowHP.exec_()
    
    #LIHAT HASIL TFIDF
    def _hasilTFIDF(self):
        #windowHP = HasilTFIDF()
        #windowHP._inisialisasi()
        #windowHP.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        #windowHP.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        #windowHP.exec_()
        os.system("start EXCEL.EXE OUTPUT/TFIDF.xlsx")
    
    #LIHAT HASIL SVM
    def _hasilSVM(self):
        windowSVM = HasilSVM()
        windowSVM._inisialisasi(self.modelSVM['modelSVM'], self.modelSVM['y_test'], self.modelSVM['predicted'])
        windowSVM.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        windowSVM.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        windowSVM.exec_()
    
############################## RUN ##############################################

def main():
    app=QApplication(sys.argv)
    window = MainUtama()
    #window.showFullScreen()
    window.show()
    window.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
    window.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
    app.exec_()

if __name__ == '__main__':
    try:
        main()
    except Exception as why:
        print(why)