import zmq
from xmlrpc.client import ServerProxy

def _getZMQSocket(host:str, port: int):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://{host}:{port}")
    socket.setsockopt(zmq.SUBSCRIBE, b'')
    return socket

def _getXmlRpc(host:str, port: int):
    return ServerProxy(f"http://{host}:{port}")