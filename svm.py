import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

class AirportSVM:

    def __init__(self, airports: pd.DataFrame, test_set: pd.DataFrame):

        self.airports = airports
        self.test_set = test_set

        # Initialize SVM model
        self.svm = SVC(kernel='rbf', C=1.0)

        # Prepared Data Placeholders
        self.features_training = self.airports.drop(["airport_ref", "ident", "type", "name"], axis=1)
        self.features_test = self.test_set.drop("airport_ref", axis=1)
        self.labels_training = self.airports["airport_ref"]
        self.labels_test = self.test_set["airport_ref"]

        # Evaluation Items
        self.predicted = None

    def prepare_data(self):
        # Normalize the data
        normalizer = preprocessing.StandardScaler()
        self.features_training = normalizer.fit_transform(self.features_training)
        self.features_test = normalizer.transform(self.features_test)

    def train(self):
        # Train the SVM model
        self.svm.fit(self.features_training, self.labels_training)

    def evaluate(self):
        # Evaluate the model
        self.predicted = self.svm.predict(self.features_test)
        accuracy = accuracy_score(self.labels_test, self.predicted)
        print("Accuracy:", accuracy)

    def fit(self):
        # Full workflow
        self.prepare_data()
        print("Data Prepared")
        self.train()
        print("Training Done")
        self.evaluate()

