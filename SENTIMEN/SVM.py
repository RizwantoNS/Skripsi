import sys
from PyQt5.QtWidgets import QApplication
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import swifter
import math
#SVM
from sklearn.svm import SVC
from sklearn.metrics import roc_auc_score
from sklearn.metrics import accuracy_score

from TFIDF import TFIDF

#CLASS SVM
class SVM():
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        self.data_tfidf = pd.DataFrame()
        self.SVM = {}
        self.y_test = {}
        self.predicted = {}
    
    def _inisialisasi(self):
        self.data_tfidf = pd.read_excel("OUTPUT/TFIDF.xlsx")
        #JALANKAN PROSES
        self._proses()

        #OUTPUT
        return {'modelSVM':self.SVM, 'y_test':self.y_test, 'predicted':self.predicted}
    
    def _proses(self):

        #bagi 70% Training 30% Testing
        num_training = math.ceil(len(self.data_tfidf.index)*0.7)

        sentimen = self.data_tfidf["sentimen"]
        komentar = self.data_tfidf["proses_tfidf"]
  
        self.data_tfidf.drop('sentimen', axis=1, inplace=True)
        self.data_tfidf.drop('proses_tfidf', axis=1, inplace=True)
        
        X_train = self.data_tfidf[:num_training]
        X_test = self.data_tfidf[num_training:]
        y_train = sentimen[:num_training]
        y_test = sentimen[num_training:]

        komentar_train = komentar[:num_training]
        komentar_test = komentar[num_training:]
        
        # we create an instance of SVM and fit out data. We do not scale our
        # data since we want to plot the support vectors
        C = 10.0  # SVM regularization parameter
        # train classifier
        self.SVM = SVC(kernel='rbf', gamma=1,   degree=3, C=C, probability=True)
        self.SVM.fit(X_train, y_train)

        #Prediksi
        predicted = self.SVM.predict(X_test)    

        self.y_test = y_test
        self.predicted = predicted
        
        '''review_postif = "saya suka main game ini seru sekali"
        review_negatif = "game nya bagus tapi setelah update banyak bug "
       
        self.predicted(self._proses(review_negatif))
        '''
        #SIMPAN EXCEL
        
        data_training = pd.concat([y_train, komentar_train, X_train], axis=1)
        data_training.rename(columns = {'proses_tfidf':'komentar'}, inplace = True)
        data_training.to_excel("OUTPUT/data_training.xlsx", index=False)

        data_testing= pd.concat([y_test, komentar_test, X_test], axis=1)
        data_testing.rename(columns = {'proses_tfidf':'komentar'}, inplace = True)
        data_testing.to_excel("OUTPUT/data_testing.xlsx", index=False)

        #predict and evaluate predictions
        #predictions = clf.predict_proba(X_test)
        #print('ROC-AUC yields ' + str(roc_auc_score(y_test, predictions[:,1])))
        
        

############################## RUN ##############################################

def main():
    app=QApplication(sys.argv)
    window = SVM()
    data_tfidf = pd.read_excel("OUTPUT/TFIDF.xlsx")
    output = window._inisialisasi(data_tfidf)
    print(output)
    app.exec_()

if __name__ == '__main__':
    try:
        main()
    except Exception as why:
        print(why)
