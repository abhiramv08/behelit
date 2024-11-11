import threading
from utils import *

#TODO: each client will contact a primary server for reqs
#on put, primary will update its replica and send puts to other servers
#also order it (check if the user clock = timestamp-1)
#then increment the server clock (map: user to clock)
#on get, primary just returns latest data

class Server:
    def __init__(self, port):
        self.stopServer = False
        self.SERVER_IP = socket.gethostbyname(socket.gethostname())
        self.SERVER_PORT = port
        self.serverThread = threading.Thread(target = self.initServer, args = [])
        self.serverThread.start()

    # Stops the server by shutting down sockets and waiting for threads to wrap up.
    def stop(self):
        self.stopServer = True
        self.server_socket.shutdown(socket.SHUT_RDWR)
        self.serverThread.join()

    #############################
    # Handle incoming requests #
    ############################
    
    def readFromDS(self, key):
        return DATA_STORE.get(key, None)
    
    def writeToDS(self, key, value, clock):
        DATA_STORE.put(key, value, clock)
        return ReqStatus.SUCCESS

    # Helper function that maps the request type to the correct API. Returns the result of the operation
    def processRequest(self, request, client_addr):
        #Can be either: Read, Write or Write replicate request
        out = None
        logging.debug(f"Request: {request.RequestType}")
        if (request.RequestType == ReqType.READ):
            key = request.Args[0]
            out = self.readFromDS(key)
        elif (request.RequestType == ReqType.WRITE):
            key, 
        elif (request.RequestType == ReqType.WRITE_REPLICATE):
            pass
        return out

    # Target function that runs when a thread is spawned that handles the requests
    def socket_target(self, conn, addr):
        serializedReq = bytearray()
        while True: 
            data = conn.recv(1024) 
            if not data: 
                break
            serializedReq.extend(data)
        serializedReq = bytes(serializedReq)
        request = deserialize(serializedReq)
        logging.debug(f"Received req")
        reqResponse = self.processRequest(request, addr)
        serializedResp = serialize(reqResponse)
        conn.send(serializedResp)
        conn.shutdown(socket.SHUT_WR)

    # Initializes the server by binding on port and listens to requests.
    def initServer(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.SERVER_IP,self.SERVER_PORT))
        self.server_socket.listen(10) #Max 10 peers in the queue
        logging.info(f"Server started on {self.SERVER_IP}:{self.SERVER_PORT}")
        while not self.stopServer:
            try:
                client_socket, addr = self.server_socket.accept()
                logging.debug(f"Received req from client: {addr}")
                threading.Thread(target = self.socket_target, args = [client_socket, addr]).start()
            except:
                break
        logging.info("Server shutting down")
