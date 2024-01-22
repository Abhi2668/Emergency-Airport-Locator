from sklearn import preprocessing
from sklearn import neighbors
from sklearn import metrics

import utils
from plane import Plane
import pandas as pd
import numpy as np

class AirportKNN:

    def __init__(self, airports: pd.DataFrame, test_set: pd.DataFrame, num_neighbors: int=2):

        self.airports = airports
        self.test_set = test_set

        self.knn = neighbors.KNeighborsClassifier(n_neighbors=num_neighbors)

        # Prepared Data Placeholders

        self.features_training = None
        self.features_test = None
        self.labels_training = None
        self.labels_test = None

        # Evaluation Items

        self.predicted = None

    def prepare_data(self, proto_min=False, tar_plane: Plane=None, normalize=False):

        if proto_min:
            min_runway = tar_plane.min_runway_length
            elev = tar_plane.elevation


            self.airports["elevation_ft"] = utils.elevation_inverter(self.airports, elev)
            self.airports["length_ft"] = utils.runway_inverter(self.airports, min_runway)

        self.features_training = self.airports.drop(["airport_ref", "ident", "type", "name"], axis=1)
        self.features_test = self.test_set.drop("airport_ref", axis=1)
        self.labels_training = self.airports["airport_ref"]
        self.labels_test = self.test_set["airport_ref"]

        # Normalize the training set to prevent overfitting to a specific feature

        if normalize:
            normalizer = preprocessing.StandardScaler()

            self.features_training = normalizer.fit_transform(self.features_training)
            self.features_test = normalizer.transform(self.features_test)

    def train(self):

        # Train a KNN iteration on the normalized testing data

        self.knn.fit(self.features_training, self.labels_training)

    def evaluate(self):

        self.predicted = self.knn.predict(self.features_test)
        accuracy = metrics.accuracy_score(self.labels_test, self.predicted)
        # print(accuracy)

    def fit(self):
        self.prepare_data()
        self.train()
        self.evaluate()

    def score(self):

        return self.knn.score(self.features_test, self.labels_test)

    def cross_validate(self, n_splits=5):
        self.features_training = np.array(self.features_training)
        self.labels_training = np.array(self.labels_training)

        indices = np.random.permutation(len(self.features_training))
        fold_size = len(self.features_training) // n_splits
        scores = []

        for fold in range(n_splits):
            test_i = indices[fold * fold_size: (fold + 1) * fold_size]
            train_i = np.concatenate([indices[:fold * fold_size], indices[(fold + 1) * fold_size:]])
            X_train, X_test = self.features_training[train_i], self.features_training[test_i]
            y_train, y_test = self.labels_training[train_i], self.labels_training[test_i]
            normalizer = preprocessing.StandardScaler()
            X_train_normalized = normalizer.fit_transform(X_train)
            X_test_normalized = normalizer.transform(X_test)
            self.knn.fit(X_train_normalized, y_train)
            predicted = self.knn.predict(X_test_normalized)

            scores.append(metrics.accuracy_score(y_test, predicted))

        print(np.mean(np.array(scores)))
        return np.mean(np.array(scores))