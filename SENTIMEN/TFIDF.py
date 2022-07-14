import sys
from PyQt5.QtWidgets import QApplication
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import swifter
import math

#CLASS TFIDF
class TFIDF():
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        self.data_preprocessing = pd.DataFrame()
        self.hasil = pd.DataFrame()
    
    def _inisialisasi(self, data_preprocessing):
        data_preprocessing = data_preprocessing.reset_index(drop=True)

        self.data_preprocessing = data_preprocessing

        #JALANKAN PROSES
        self._proses()

        #OUTPUT
        return self.hasil
    
    def _proses(self):
        # banyaknya term yang akan digunakan, 
        # di pilih berdasarkan top max_features 
        # yang diurutkan berdasarkan term frequency seluruh corpus
        max_features = 1000

        tf_idf = TfidfVectorizer(max_features=max_features, binary=True)
        self.hasil = tf_idf.fit_transform(self.data_preprocessing["proses_tfidf"]).toarray()

        #SIMPAN EXCEL
        df1 = pd.DataFrame(self.hasil, columns=tf_idf.get_feature_names())
        res = pd.concat([self.data_preprocessing['sentimen'], self.data_preprocessing['proses_tfidf'], df1], axis=1)
        pd.DataFrame(res).to_excel("OUTPUT/TFIDF.xlsx", sheet_name = "TFIDF", index=False)


############################## RUN ##############################################

def main():
    app=QApplication(sys.argv)
    window = TFIDF()
    data_preprocessing = pd.read_excel("OUTPUT/Text_Preprocessing.xlsx")
    window._inisialisasi(data_preprocessing)
    exit()

if __name__ == '__main__':
    try:
        main()
    except Exception as why:
        print(why)