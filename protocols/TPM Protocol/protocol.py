import Server
import Device
import helper
import tensorflow as tf
import pypuf.io

device = Device.Device("1", 123)
server = Server.Server("Master")

# server.enroll(device)
device.start_auth(server)
