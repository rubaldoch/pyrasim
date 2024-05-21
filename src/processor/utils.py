from xmlrpc.client import ServerProxy
import numpy as np
import zmq
import os

def toDbv(num):
    return 20 * np.log10(np.abs(num))

def getSocket(port=8082):
    """
    Create ZMQ context and subscrite to it

    Returns
        zmq.socket
    """
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://127.0.0.1:{port}") # connect, not bind, the PUB will bind, only 1 can bind
    socket.setsockopt(zmq.SUBSCRIBE, b'') # subscribe to topic of all (needed or else it won't work)
    return socket

def getXmlrpc(port=8080):
    """
    Create a XML RPC server proxy
    """
    return ServerProxy(f"http://127.0.0.1:{port}")

def psd(fft_size, data):
    """Return the power spectral density of `samples`"""
    window = np.hamming(fft_size)
    result = np.multiply(window, data)
    result = np.fft.fft(result, fft_size)
    result = np.square(np.abs(result))
    result = np.nan_to_num(10.0 * np.log10(result))
    return result

def createDir(filename):
    if not os.path.isdir(filename):
        os.makedirs(filename)