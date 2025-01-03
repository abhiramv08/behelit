from utils import *

#TODO: client maintains its own local clock
#client increments clock before each put request

class Client:
    def __init__(self, id, server_id):
        self.CLIENT_IP = socket.gethostbyname(socket.gethostname())
        self.CLIENT_ID = id
        self.SERVER_IP, self.SERVER_PORT = SERVERS[server_id]
        self.clock = VectorClock()
        self.clock.AddClient(self.CLIENT_ID)

    def stop(self):
        logging.debug("Stopping client")

    ###########################
    # Calls to server API that client needs to make
    ###########################
    def read(self, key):
        read_req = Request(ReqType.READ, self.clock, (key))
        response = sendReqSocket(read_req, self.SERVER_IP, self.SERVER_PORT)
        logging.debug(f"Read response: status - {response.Status},  clock - {response.Clock}, body - {response.Body}")
        if response.Clock:
            self.clock.UpdateClock(response.Clock)
        logging.debug(f"New clock after read - {self.clock}")
        return response.Body

    def write(self, key, value):
        self.clock.IncrementClock(self.CLIENT_ID)
        write_req = Request(ReqType.WRITE, self.clock, (self.CLIENT_ID, key, value))
        response = sendReqSocket(write_req, self.SERVER_IP, self.SERVER_PORT)
        logging.debug(f"Write response: status - {response.Status},  clock - {response.Clock}, body - {response.Body}")
        #dont update clock in this case
        return response.Status
