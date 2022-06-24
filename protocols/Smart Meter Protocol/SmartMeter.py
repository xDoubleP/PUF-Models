import time
from pypuf.simulation import XORArbiterPUF
from pypuf.io import random_inputs
import random
import numpy as np
import helper


class SmartMeter:
    def __init__(self, id, seed):
        self.puf = XORArbiterPUF(n=64, k=2, seed=seed)
        self.meter_id = id
        # in reality this would get the reading
        self.reading = random.randint(1, 1000)

    def get_meter_id(self):
        return self.meter_id

    def get_puf(self):
        return self.puf

    def challenge_puf(self, challenge):
        return self.puf.eval(challenge)

    def get_reading(self):
        return self.reading

    def get_encrypted_data(self):
        # generate Challenge
        challenge = random_inputs(n=64, N=1, seed=random.randint(1, 1000))
        bits = 32

        # Needed because response is only 1 bit
        response = np.array(helper.generate_n_bit_response(
            self.puf, challenge, bits))

        reading = str(self.get_reading())
        timestamp = time.ctime()
        string_challenge = np.array2string(challenge, separator=',')
        data = [reading, string_challenge, timestamp]

        message = "|".join(data)
        encrypted_message = helper.encrypt(response, message)
        encrypted_message = encrypted_message.decode('utf-8')

        print(f"Reading SM {self.get_meter_id()}: {reading}")

        return(encrypted_message + "|" +
               string_challenge + "|" + str(self.get_meter_id()))
