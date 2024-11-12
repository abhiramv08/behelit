import threading
import time
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
        self.OTHER_SERVERS = []
        for s_ip, s_port in SERVERS:
            if s_port != self.SERVER_PORT:
                self.OTHER_SERVERS.append((s_ip, s_port))
        self.serverThread = threading.Thread(target = self.initServer, args = [])
        self.serverThread.start()
        self.dataStore = DataStore()
        

    # Stops the server by shutting down sockets and waiting for threads to wrap up.
    def stop(self):
        self.stopServer = True
        self.server_socket.shutdown(socket.SHUT_RDWR)
        self.serverThread.join()

    #############################
    # Handle incoming requests #
    ############################
    
    def readFromDS(self, key):
        return self.dataStore.get(key, None)
    
    def checkAndWrite(self, key, value, clock, id):
        while True:
            prevClock = self.dataStore.get(key)[1]
            if prevClock.DependencyCheck(clock, id):
                break
            else:
                time.sleep(5)
        self.dataStore.put(key, value, clock)

    def writeToDS(self, key, value, clock, id):
        self.checkAndWrite(key, value, clock, id)
        #send replicate requests to all the other servers 
        for s_ip, s_port in self.OTHER_SERVERS:
            replicate_req = Request(ReqType.WRITE_REPLICATE, clock, (key, value, id))
            response = sendReqSocket(replicate_req, s_ip, s_port)
            logging.debug(f"Replicate response: status - {response.Status},  clock - {response.Clock}, body - {response.Body}")
        return Response(ReqStatus.SUCCESS, None, None)
    
    def replicateWrite(self, key, value, clock, id):
        #dependency check and then write
        self.checkAndWrite(key, value, clock, id)
        return Response(ReqStatus.SUCCESS, None, None)

    # Helper function that maps the request type to the correct API. Returns the result of the operation
    def processRequest(self, request, client_addr):
        #Can be either: Read, Write or Write replicate request
        out = None
        client_port = int(client_addr[1])
        logging.debug(f"Request: {request.RequestType}")
        if (request.RequestType == ReqType.READ):
            key = request.Args[0]
            out = self.readFromDS(key)
        elif (request.RequestType == ReqType.WRITE):
            key = request.Args[0]
            value = request.Args[1]
            client_clock = request.Clock
            out = self.writeToDS(key, value, client_clock, client_port)
        elif (request.RequestType == ReqType.WRITE_REPLICATE):
            key = request.Args[0]
            value = request.Args[1]
            client_clock = request.Clock
            out = self.replicateWrite(key, value, client_clock, client_port)
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
