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

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np

import math

from sklearn import metrics
import seaborn as sns

current_dir = os.path.dirname(os.path.abspath('__file__'))
Form, Base = uic.loadUiType(os.path.join(current_dir, "UI/SVM_UI.ui"))

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

#CLASS HASIL SVM #########====================================================#################
class HasilSVM(QDialog, Base, Form ):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.setupUi(self)

        #FULL SCREEN
        #self.showMaximized() 

        # a figure instance to plot on
        self.figure, self.ax = plt.subplots()
        # this is the Canvas Widget that
        # displays the 'figure'it takes the
        # 'figure' instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        # creating a Vertical Box layout
        layout = QtWidgets.QVBoxLayout()

        # adding canvas to the layout
        layout.addWidget(self.canvas)

        # setting layout to the Grafik
        self.widgetSVM.setLayout(layout)

        self.modelSVM = {}
        self.y_test = {}
        self.predicted = {}
    
    def _inisialisasi(self, modelSVM, y, predicted):
        self.modelSVM = modelSVM
        self.y_test = y
        self.predicted = predicted
        #Tampilkan Grafik
        self._viewGrafik()

    def _viewGrafik(self):
        classes = np.unique(self.y_test)

        ## Plot confusion matrix
        cm = metrics.confusion_matrix(self.y_test, self.predicted)
        sns.heatmap(cm, annot=True, fmt='d', ax=self.ax, cmap=plt.cm.Blues, 
                    cbar=False)
        self.ax.set(xlabel="Pred", ylabel="True", xticklabels=classes, 
            yticklabels=classes, title="Confusion matrix")
        plt.yticks(rotation=0)

        #AKURASI
        accuracy = metrics.accuracy_score(self.y_test.values, self.predicted)
        self.txtAkurasi.setText(str("{0:.1%}".format(accuracy)))

        ## Accuracy, Precision, Recall
        apr = metrics.classification_report(self.y_test, self.predicted, output_dict=True)
        df = pd.DataFrame(apr).transpose()

        modelAPR = PandasModel(df)
        #Interactive, Fixed, Stretch, ResizeToContents, Custom
        self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.tableView.setModel(modelAPR)
        self.tableView.setWordWrap(True)
    """
    def _viewGrafik2(self):
        from sklearn.svm import SVC
        from sklearn import svm

        data_tfidf = pd.read_excel("OUTPUT/TFIDF.xlsx")
        num_training = math.ceil(len(data_tfidf.index)*0.9)

        sentimen = data_tfidf["sentimen"]
        komentar = data_tfidf["proses_tfidf"]
  
        data_tfidf.drop('sentimen', axis=1, inplace=True)
        data_tfidf.drop('proses_tfidf', axis=1, inplace=True)
        
        X_train = data_tfidf[:num_training]
        X_test = data_tfidf[num_training:]
        y_train = sentimen[:num_training]
        y_test = sentimen[num_training:]

        komentar_train = komentar[:num_training]
        komentar_test = komentar[num_training:]

        classes = np.unique(y_test)

        h = .02  # step size in the mesh
        # we create an instance of SVM and fit out data. We do not scale our
        # data since we want to plot the support vectors
        C = 10  # SVM regularization parameter
        
        # train classifier
        modelSVM = svm.SVC(kernel='rbf', gamma=2, C=C, probability=True).fit(X_train, y_train)

        #Prediksi
        predicted = modelSVM.predict(X_test)

        ## Plot confusion matrix
        cm = metrics.confusion_matrix(y_test, predicted)
        sns.heatmap(cm, annot=True, fmt='d', ax=self.ax, cmap=plt.cm.Blues, 
                    cbar=False)
        self.ax.set(xlabel="Pred", ylabel="True", xticklabels=classes, 
            yticklabels=classes, title="Confusion matrix")
        plt.yticks(rotation=0)

        
        #AKURASI
        accuracy = metrics.accuracy_score(y_test.values, predicted)
        self.txtAkurasi.setText(str("{0:.1%}".format(accuracy)))

        ## Accuracy, Precision, Recall
        apr = metrics.classification_report(y_test, predicted, output_dict=True)
        df = pd.DataFrame(apr).transpose()  

        modelAPR = PandasModel(df)
        #Interactive, Fixed, Stretch, ResizeToContents, Custom
        self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.tableView.setModel(modelAPR)
        self.tableView.setWordWrap(True)
    """

############################## RUN ##############################################

def main():
    app=QApplication(sys.argv)
    window = HasilSVM()
    window._inisialisasi()
    window.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
    window.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
    window.exec_()

if __name__ == '__main__':
    try:
        main()
    except Exception as why:
        print(why)