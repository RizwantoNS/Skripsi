import os
import traceback, sys
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QFileDialog, QDialog, QMessageBox
import re
import pandas as pd
import itertools
# import StemmerFactory class
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory, StopWordRemover, ArrayDictionary
from nltk.tokenize import word_tokenize 
import nltk
import swifter

#CLASS Preprocessing
class Preprocessing():
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        #self.dataset = pd.read_excel("DATA.xlsx")
        self.dataset = pd.DataFrame()
        self.hasil = pd.DataFrame()
    
    def _inisialisasi(self, dataset):
        self.dataset = dataset
        self.hasil['sentimen'] = self.dataset['sentimen']
        self.hasil['komentar'] = self.dataset['komentar']

        #JALANKAN PROSES
        self._proses()

        #OUTPUT
        return self.hasil
    
    def isfloat(self, num):
        try:
            float(num)
            return True
        except ValueError:
            return False
    
    def _cleaning(self):
        #hapus seluruh kata yang mengandung angka, contoh: perempuan2
        self.hasil['cleaning'] = self.hasil['komentar'].str.replace('\d+', '')
        
        #hapus seluruh karakter yang tidak termasuk alphabet
        self.hasil['cleaning'] = self.hasil['cleaning'].str.replace('[^a-zA-Z]', ' ')

        #hapus double space
        self.hasil['cleaning'] = self.hasil['cleaning'].str.replace(' +', ' ')
        
        #hapus NaN
        self.hasil= self.hasil.dropna()

        # menghilangkan kata dengan huruf ganda, contoh: perempuannnnn
        f = lambda x: ''.join(ch for ch, _ in itertools.groupby(x))
        self.hasil['cleaning'] = self.hasil['cleaning'].swifter.apply(f)

    #1. Case folding
    def _case_folding(self):
        self.hasil['komentar_casefolding'] = self.hasil['cleaning'].str.lower()
    
    #2. Tokenizing
    def _tokenizing(self):
        self.hasil['komentar_tokenizing'] = self.hasil['komentar_casefolding'].str.split()
    
    #3. Filtering (Stopword Removal)
    def _stopword(self):
        stop_factory = StopWordRemoverFactory().get_stop_words() #load defaul stopword
        
        data_stopword = pd.read_excel("STOPWORD.xlsx")
        more_stopword = data_stopword['kata'].values.tolist()
        #more_stopword = ['bulan'] #menambahkan stopword
        data = stop_factory + more_stopword #menggabungkan stopword

        self.hasil['komentar_stopword'] = self.hasil['komentar_tokenizing'].swifter.apply(lambda x: ([word for word in x if word not in (data)]))

    #4. Stemming
    # apply stemmed term to dataframe
    def _stemming(self):
        factory = StemmerFactory()
        stemmer = factory.create_stemmer()
        self.hasil['komentar_stemming'] = self.hasil['komentar_stopword'].swifter.apply(lambda x: ([stemmer.stem(word) for word in x]))

        #Untuk Proses TFIDF
        self.hasil['proses_tfidf'] = self.hasil['komentar_stemming'].swifter.apply(lambda x: ' '.join(map(str, x)))

    def _proses(self):
        self._cleaning()
        self._case_folding()
        self._tokenizing()
        self._stopword()
        self._stemming()

############################## RUN ##############################################

def main():
    app=QApplication(sys.argv)
    window = Preprocessing()
    dataset = pd.read_excel("DATA.xlsx")
    window._inisialisasi(dataset)
    #window.show()
    app.exec_()

if __name__ == '__main__':
    try:
        main()
    except Exception as why:
        print(why)
