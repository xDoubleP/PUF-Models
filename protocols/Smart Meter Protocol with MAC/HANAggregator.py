import base64
import hashlib
import SmartMeter
import tensorflow as tf
import train_puf_model
import numpy as np
import helper
from pypuf.io import random_inputs
import hmac
from fuzzy_extractor import FuzzyExtractor


class HANAggregator:

    # Initialise intial counter
    def __init__(self, name):
        self.name = name
        self.counter = 0


# Train PUFs in the enrollement phase


    def enroll(self, sm: SmartMeter):
        train_puf_model.train_model(sm.get_puf1(), f"1:{sm.get_meter_id()}")
        train_puf_model.train_model(sm.get_puf2(), f"2:{sm.get_meter_id()}")

# Load TPMS in the data aggregation phase
    def load_tpm(self, id):
        self.model1 = tf.keras.models.load_model(
            f'database/1:{id}')
        self.model2 = tf.keras.models.load_model(
            f'database/2:{id}')

    def data_aggregation(self, input_messages):
        # Generate challenge
        total_sum = 0
        self.counter += 1
        challenge = random_inputs(n=64, N=1, seed=self.counter)
        extractor = FuzzyExtractor(32, 4)
        for input_message in input_messages:
            bits = 32
            # decompose message and load TPMs
            encrypted_message, meter_id, hash, helper_data_encrypt, helper_data_mac = input_message
            self.load_tpm(meter_id)

            # Reproduce mac key
            response_tpm = np.array(helper.predict_n_bit_response(
                self.model1, challenge, bits), dtype=np.int8)

            mac_response = np.array(helper.predict_n_bit_response(
                self.model2, challenge, bits), dtype=np.int8)

            mac_key = extractor.reproduce(mac_response, helper_data_mac)
            mac_key_as_bits = np.array2string(
                helper.key_to_bits(mac_key), separator=',')
            mac_message = encrypted_message + \
                np.array2string(challenge, separator=',') + meter_id + \
                mac_key_as_bits

           # Reproduce mac tag
            hmac1 = hmac.new(key=mac_key_as_bits.encode(),
                             msg=mac_message.encode(), digestmod=hashlib.sha256)

            check_hash = hmac1.digest()

            # check mac tag
            if (hash == str(check_hash, "ISO-8859-1")):
                print("HASH CHECK PASSED")

           # Reproduce encryption key and decrypt
                key = extractor.reproduce(response_tpm, helper_data_encrypt)
                key_as_bits = helper.key_to_bits(key)
                print("Secret Key using TPM only: ",
                      base64.urlsafe_b64encode(response_tpm))
                print("Secret Key Reproduced using helper data: ", base64.urlsafe_b64encode(key))
                decrypted_message = helper.decrypt(
                    key_as_bits, encrypted_message.encode('utf-8')).decode('utf-8')
                reading, string_challenge, timestamp = decrypted_message.split(
                    "||")
                print(timestamp)
                print("Reading HA:", reading)
                # summing meter reading
                total_sum += int(reading)
            else:
                print("HASH CHECK FAILED")
        print("Total Sum: ", total_sum)
