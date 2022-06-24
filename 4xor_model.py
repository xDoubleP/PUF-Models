import pypuf
from sklearn.model_selection import train_test_split
from tensorflow import random
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import pypuf.simulation
import pypuf.io
import parity_vector
from matplotlib import pyplot as plt
import time
start_time = time.time()

random.set_seed(1337)  # reproducibility
puf = pypuf.simulation.XORArbiterPUF(n=64, k=4, seed=1)
challenges = pypuf.io.random_inputs(n=64, N=80000, seed=123)
responses = puf.eval(challenges)

X = parity_vector.get_parity_vectors(challenges)
# X = challenges
y = (1 - responses) // 2  # convert -1s to 0s
# y = responses

print(y.shape, X.shape)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=0)

model = Sequential()

# less nodes and layer lead to better generalization
model.add(Dense(12, input_dim=X.shape[1], activation='relu'))
model.add(Dense(10, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

model.summary()

model.compile(loss='binary_crossentropy',
              optimizer='adam', metrics='accuracy')

results = model.fit(X_train, y_train, epochs=500, batch_size=1000,
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
