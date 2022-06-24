import base64
import hashlib
import time
from tkinter.ttk import Separator
from pypuf.simulation import XORArbiterPUF
from pypuf.io import random_inputs
import random
import numpy as np
import helper
import hmac
from fuzzy_extractor import FuzzyExtractor


class SmartMeter:

    # Initialise Boths PUFs, its device id and the internal local challenge
    def __init__(self, id, seed1, seed2):
        self.puf1 = XORArbiterPUF(n=64, k=2, seed=seed1)
        self.puf2 = XORArbiterPUF(n=64, k=2, seed=seed2)
        self.meter_id = id
        # in reality this would get the reading
        self.reading = random.randint(1, 1000)
        self.counter = 0

    def get_meter_id(self):
        return self.meter_id

    def get_puf1(self):
        return self.puf1

    def get_puf2(self):
        return self.puf2

    def challenge_puf1(self, challenge):
        return self.puf1.eval(challenge)

    def challenge_puf2(self, challenge):
        return self.puf2.eval(challenge)

    def get_reading(self):
        return self.reading

    def get_encrypted_data(self):
        # generate Challenge
        self.counter += 1
        challenge = random_inputs(n=64, N=1, seed=self.counter)
        bits = 32

        # Needed because response is only 1 bit
        response = np.array(helper.generate_n_bit_response(
            self.puf1, challenge, bits))

        # Fuzzy Extractor
        extractor = FuzzyExtractor(32, 4)
        key, helper_data_encrypt = extractor.generate(response)
        key_as_bits = helper.key_to_bits(key)

        reading = str(self.get_reading())
        timestamp = time.ctime()
        string_challenge = np.array2string(challenge, separator=',')
        data = [reading, string_challenge, timestamp]
        message = "||".join(data)

        # Encryption
        encrypted_message = helper.encrypt(key_as_bits, message)
        encrypted_message = encrypted_message.decode('utf-8')

        print(f"Reading SM {self.get_meter_id()}: {reading}")
        print("Secret Key: ", base64.urlsafe_b64encode(key))

        mac_response = np.array(helper.generate_n_bit_response(
            self.puf2, challenge, bits))

        # Mac Key
        mac_key, helper_data_mac = extractor.generate(mac_response)
        mac_key_as_bits = np.array2string(
            helper.key_to_bits(mac_key), separator=',')

        mac_message = encrypted_message + string_challenge + \
            str(self.get_meter_id()) + mac_key_as_bits

        hmac1 = hmac.new(key=mac_key_as_bits.encode(),
                         msg=mac_message.encode(), digestmod=hashlib.sha256)

        # Mac Tag
        hash = hmac1.digest()

        return(encrypted_message, str(self.get_meter_id()), str(hash, "ISO-8859-1"), helper_data_encrypt, helper_data_mac)
