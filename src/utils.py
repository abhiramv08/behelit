# from typing import NameTuple
from collections import namedtuple, OrderedDict
from enum import Enum
import hashlib
import codecs
import pickle
import logging
import sys
import socket
import threading

logging.basicConfig(level=logging.INFO)

##################################
# Defining constants and classes #
##################################

# Server info
# SERVER_PORT = 55555
# SERVER_NAME = "130.203.16.40"
SERVERS = [("130.203.16.40", 55555), ("130.203.16.40", 55556), ("130.203.16.40", 55557)]

# Chunk size
CHUNK_SIZE = 128

# Request status
class ReqStatus(Enum):
    SUCCESS = 0
    FAILURE = 1

# Serializer for the bytes to be sent over the network
def serialize(obj): #Input object, return bytes
    return codecs.encode(pickle.dumps(obj), "base64")

# Deserializes the bytes sent over the network back into object 
def deserialize(serText): #Input bytes, return object
    return pickle.loads(codecs.decode(serText, "base64"))

class ReqType(Enum):
    READ = 0
    WRITE = 1
    WRITE_REPLICATE = 2

# Class for request with request type and list of arguments
class Request():
    def __init__(self,reqType,clock,args):
        self.RequestType = reqType
        self.Clock = clock
        self.Args = args

# Class for response with status and a body
class Response():
    def __init__(self,stat,body):
        self.Status = stat
        self.Body = body

#Send request to any server, port over socket
def sendReqSocket(self, request:Request, serverName:str, serverPort:int) -> Response:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.debug(f"Connecting to host: {serverName, serverPort}")
    client_socket.connect((serverName,serverPort))
    client_socket.sendall(serialize(request))
    client_socket.shutdown(socket.SHUT_WR)
    response = bytearray()
    while True:
        data = client_socket.recv(2048)
        if not data:
            break
        response.extend(data)
    response = deserialize(response)
    return response

# Target function that runs when a thread is spawned that handles the requests
# def socket_target(self, conn, responseFn):
#     serializedReq = bytearray()
#     while True: 
#         data = conn.recv(1024) 
#         if not data: 
#             break
#         serializedReq.extend(data)
#     serializedReq = bytes(serializedReq)
#     request = deserialize(serializedReq)
#     logging.debug(f"Received req")
#     reqResponse = responseFn(request)
#     serializedResp = serialize(reqResponse)
#     conn.send(serializedResp)
#     conn.shutdown(socket.SHUT_WR)

# # Sets up the upload handler of the peer and listens to any incoming requests.
# # responseFn : function to be called when you get a request
# def initListenerThread(self, myIp, myPort, responseFn):
#     self.listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     self.listener_socket.bind((myIp,myPort))
#     logging.info(f"Started peer, uploading on {(myIp,myPort)}")
#     self.listener_socket.listen(10) #Max 10 peers in the queue
#     while not self.stopUpload:
#         try:
#             client_socket, addr = self.listener_socket.accept()
#             logging.debug(f"Received req from client: {client_socket}, {addr}")
#             uLoadThreads = []
#             uLoadThreads.append(threading.Thread(target = self.socket_target, args = [client_socket, responseFn]))
#             uLoadThreads[-1].start()
#         except:
#             break
#     logging.debug("Stopped listener")


class DataStore:
    def __init__(self):
        self.data = dict()
    
    def put(self, key, value, clock):
        self.data[key] = (value, clock)
    
    def get(self, key):
        return self.data.get(key, None)

DATA_STORE = DataStore()

# Class for vector clock. Has functiosn to add client index, check if dependency is met, update timestamp
class VectorClock():
    def __init__(self):
        self.clk = dict()
    def AddClient(self,key):
        self.clk[key] = 0
    def DependencyCheck(self,key,msgTimestamp):
        if self.clk[key]+1 == msgTimestamp:
            return True
        return False
    def UpdateTimestamp(self,key,msgTimestamp):
        self.clk[key] = msgTimestamp if msgTimestamp>self.clk[key] else self.clk[key]+1 # need to verify
