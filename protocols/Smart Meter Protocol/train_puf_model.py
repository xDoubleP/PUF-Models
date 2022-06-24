
import pypuf
from sklearn.model_selection import train_test_split
from tensorflow import random
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
import pypuf.simulation
import pypuf.io
import helper
import numpy as np

import tensorflow as tf
from matplotlib import pyplot as plt


def train_model(puf, puf_id):
    print("VERSION ------ ", tf.__version__)
    print("PUFID:", puf_id)
    challenges = pypuf.io.random_inputs(n=64, N=40000, seed=123)
    responses = puf.eval(challenges)

    X = helper.get_parity_vectors(challenges)
    # X = challenges
    y = (1 - responses) // 2  # convert -1s to 0s
    # y = responses

    print(y.shape, X.shape)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=0)

    model = Sequential()

    # less nodes and layer lead to better generalization
    model.add(Dense(8, input_dim=X.shape[1], activation='relu'))
    model.add(Dense(4, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))

    model.summary()

    model.compile(loss='binary_crossentropy',
                  optimizer='adam', metrics='accuracy')

    results = model.fit(X_train, y_train, epochs=200, batch_size=1000,
                        validation_data=(X_test, y_test))

    scores = model.evaluate(X_test, y_test)
    model.save(f'Smart Meter Protocol/database/{puf_id}')
    print("Evaluate Accuracy: ", scores[1])
