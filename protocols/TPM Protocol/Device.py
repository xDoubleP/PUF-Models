from pypuf.simulation import XORArbiterPUF
from pypuf.io import random_inputs
import random
import Server
import numpy as np
import helper


class Device:
    def __init__(self, id, seed):
        self.puf = XORArbiterPUF(n=64, k=2, seed=seed)
        self.id = id

    def get_id(self):
        return self.id

    def get_puf(self):
        return self.puf

    def challenge_puf(self, challenge):
        return self.puf.eval(challenge)

    def start_auth(self, server):
        # generate Challenge
        challenge = random_inputs(n=64, N=1, seed=random.randint(1, 1000))
        bits = 16
        server_response, server_challenge = server.verify_part1(
            self.get_id(), challenge, bits)
        # Needed because response is only 1 bit
        response = helper.generate_n_bit_response(
            self.puf, challenge, bits)

        fhd = helper.fhd(server_response, response)
        print("fhd = ", fhd)
        if fhd > 1:
            print("False server")
        else:
            print("Server authenticated")
            device_response = helper.generate_n_bit_response(
                self.puf, server_challenge, bits)
            server.verify_part2(device_response)
            return True
