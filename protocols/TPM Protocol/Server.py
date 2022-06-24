from urllib import response
import Device
import tensorflow as tf
import train_puf_model
from pypuf.io import random_inputs
import random
import helper


class Server:

    def __init__(self, name):
        self.name = name
        # Length of response

    def enroll(self, device: Device):
        train_puf_model.train_model(device.get_puf(), device.get_id())

    def load_tpm(self, id):
        self.model = tf.keras.models.load_model(
            f'TPM Protocol/database/{id}')

    def verify_part1(self, device_id, challenge_device, bits):
        self.bits = bits
        self.load_tpm(device_id)
        response_tpm = helper.predict_n_bit_response(
            self.model, challenge_device, self.bits)
        # generate challenge
        self.temp_challenge_sever = random_inputs(
            n=64, N=1, seed=random.randint(1, 1000))
        return response_tpm, self.temp_challenge_sever

    def verify_part2(self, response_device):
        response_server = helper.predict_n_bit_response(
            self.model, self.temp_challenge_sever, self.bits)
        fhd = helper.fhd(response_device, response_server)
        print("Server fhd = ", fhd)
        if fhd > 1:
            print("False device")
        else:
            print("Device authenticated")
