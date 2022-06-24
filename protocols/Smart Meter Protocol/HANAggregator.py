import SmartMeter
import tensorflow as tf
import train_puf_model
import numpy as np
import helper


class HANAggregator:

    def __init__(self, name):
        self.name = name
        # Length of response

    def enroll(self, sm: SmartMeter):
        train_puf_model.train_model(sm.get_puf(), sm.get_meter_id())

    def load_tpm(self, id):
        self.model = tf.keras.models.load_model(
            f'Smart Meter Protocol/database/{id}')

    def data_aggregation(self, input_messages):
        total_sum = 0
        for input_message in input_messages:
            bits = 32
            encrypted_message, challenge, meter_id = input_message.split("|")
            self.load_tpm(meter_id)

            challenge = challenge.replace('[', '')
            challenge = challenge.replace(']', '')
            challenge = np.fromstring(
                challenge, dtype=np.int8, sep=',').reshape(1, 64)

            response_tpm = np.array(helper.predict_n_bit_response(
                self.model, challenge, bits), dtype=np.int8)

            decrypted_message = helper.decrypt(
                response_tpm, encrypted_message.encode('utf-8')).decode('utf-8')
            reading, string_challenge, timestamp = decrypted_message.split("|")

            print(timestamp)
            print("Reading HA:", reading)
            total_sum += int(reading)
        print("Total Sum: ", total_sum)
