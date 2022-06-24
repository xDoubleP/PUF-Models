import pypuf
import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow import random
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow import keras
import pypuf.simulation
import pypuf.io
import parity_vector
from matplotlib import pyplot as plt
import time
start_time = time.time()


random.set_seed(1337)  # reproducibility

df1 = pd.read_csv('APUF_XOR_Challenge_Parity_64_500000.csv', header=None)
df2 = pd.read_csv('4_lspuf.csv', header=None)

# split into input (X) and output (Y) variables
X = df1.iloc[:100000, :65]
y = df2.iloc[:100000, :]

print(y.shape, X.shape)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=0)

model = Sequential()

# less nodes and layer lead to better generalization
model.add(Dense(30, input_dim=X.shape[1], activation='relu'))

model.add(Dense(30, activation='relu'))
model.add(Dense(30, activation='relu'))
model.add(Dense(30, activation='relu'))

model.add(Dense(1, activation='sigmoid'))

model.summary()

model.compile(loss='binary_crossentropy',
              optimizer='adam', metrics='accuracy')

results = model.fit(X_train, y_train, epochs=200, batch_size=1000,
                    validation_data=(X_test, y_test))


scores = model.evaluate(X_test, y_test)
print("Evaluate Accuracy: ", scores[1])
print("--- %s seconds ---" % (time.time() - start_time))

# Plot graphs
loss = results.history["loss"]
val_loss = results.history["val_loss"]
epochs = range(1, len(loss) + 1)
plt.plot(epochs, loss, "y", label="Training Loss", color="red")
plt.plot(epochs, val_loss, "y", label="Validation Loss")
plt.title("Training and Validation Loss")
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.legend()
plt.show()

acc = results.history["accuracy"]
val_acc = results.history["val_accuracy"]
plt.plot(epochs, acc, "y", label="Training accuracy", color="red")
plt.plot(epochs, val_acc, "y", label="Validation accuracy")
plt.title("Training and Validation accuracy")
plt.xlabel("Epochs")
plt.ylabel("accuracy")
plt.legend()
plt.show()
