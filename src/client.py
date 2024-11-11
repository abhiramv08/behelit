from utils import *

#TODO: client maintains its own local clock
#client increments clock before each put request

class Client:

    def __init(self, port, server_id):
        self.CLIENT_IP = socket.gethostbyname(socket.gethostname())
        self.CLIENT_PORT = port
        self.SERVER_IP, self.SERVER_PORT = SERVERS[server_id]
        self.clock = 0

    def stop(self):
        logging.debug("Stopping client")

    ###########################
    # Calls to server API that client needs to make
    ###########################
    def read(self, key):
        read_req = Request(ReqType.READ, self.clock, (key))
        response = sendReqSocket(read_req, self.SERVER_IP, self.SERVER_PORT)
        logging.debug(f"Read response: status - {response.Status}, body - {response.Body}")
        return response.Body

    def write(self, key, value):
        self.clock+=1
        write_req = Request(ReqType.WRITE, self.clock, (key, value))
        response = sendReqSocket(write_req, self.SERVER_IP, self.SERVER_PORT)
        logging.debug(f"Write response: status - {response.Status}, body - {response.Body}")
        return response.Status
