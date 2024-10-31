# from typing import NameTuple
from collections import namedtuple, OrderedDict
from enum import Enum
import hashlib
import codecs
import pickle
import logging
import sys

logging.basicConfig(level=logging.INFO)

##################################
# Defining constants and classes #
##################################

# Server info
SERVER_PORT = 55555
SERVER_NAME = "130.203.16.40"

# Chunk size
CHUNK_SIZE = 128

# Request status
class ReqStatus(Enum):
    SUCCESS = 0
    FAILURE = 1

# Generates and returns hash using SHA1
def getHash(chunk):
    return hashlib.sha1(chunk).hexdigest() 

# Serializer for the bytes to be sent over the network
def serialize(obj): #Input object, return bytes
    return codecs.encode(pickle.dumps(obj), "base64")

# Deserializes the bytes sent over the network back into object 
def deserialize(serText): #Input bytes, return object
    return pickle.loads(codecs.decode(serText, "base64"))

# Class for request with request type and list of arguments
class Request():
    def __init__(self,reqType,args):
        self.RequestType = reqType
        self.Args = args

# Class for response with status and a body
class Response():
    def __init__(self,stat,body):
        self.Status = stat
        self.Body = body

