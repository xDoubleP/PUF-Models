import base64
import numpy as np
from cryptography.fernet import Fernet


def encrypt(key, message):
    key = base64.urlsafe_b64encode(key)
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)
    return encrypted_message


def decrypt(key, encrypted_message):
    key = base64.urlsafe_b64encode(key)
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)
    return decrypted_message


# Shifts challenge bit 1 to the right continuously to generate multiple bits
# Can only be shifted X number of times before challenges are repeated
# Where X is the length of the challenge.


def generate_n_bit_response(puf, challenge, n):
    key = []
    for i in range(n):
        response = puf.eval(challenge)
        key.append(response[0])
        challenge = np.roll(challenge, 1)
    return key


def predict_n_bit_response(model, challenge, n):
    key = []
    for i in range(n):
        #     temp = []
        #     for x in range(10):
        #         response = model.predict(get_parity_vectors(challenge))
        #         prediction = 1 if response[0] <= 0.5 else -1
        #         temp.append(prediction)
        #     key.append(max(set(temp), key=temp.count))
        response = model.predict(get_parity_vectors(challenge))
        prediction = 1 if response[0] <= 0.5 else -1
        key.append(prediction)
        challenge = np.roll(challenge, 1)
    return key


def fhd(vector1, vector2):
    # convert -1s to 0s
    vector1 = np.array(list(map(lambda x: 1 if x == 1 else 0, vector1)))
    vector2 = np.array(list(map(lambda x: 1 if x == 1 else 0, vector2)))
    print(vector1, vector2)
    return (vector1 != vector2).sum()/vector1.size

# https://github.com/Praneshss/PUF_Tutorial


def get_parity_vectors(C):
    n = C.shape[1]
    m = C.shape[0]
    C[C == 0] = -1
    parityVec = np.zeros((m, n+1))
    parityVec[:, 0:1] = np.ones((m, 1))
    for i in range(2, n+2):
        parityVec[:, i -
                  1: i] = np.prod(C[:, 0: i-1], axis=1).reshape((m, 1))
    return parityVec
