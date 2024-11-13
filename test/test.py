import time
import sys
import os
import shutil
sys.path.append('../src/')
from client import Client
from server import Server
from utils import *

def cleanup():
    try:
        os.path.exists("./test_1_1") and shutil.rmtree("./test_1_1")
        os.path.exists("./test_1_2") and shutil.rmtree("./test_1_2")
        os.path.exists("./test_2_1") and shutil.rmtree("./test_2_1")
        os.path.exists("./test_2_2") and shutil.rmtree("./test_2_2")
        os.path.exists("./test_3_1") and shutil.rmtree("./test_3_1")
        os.path.exists("./test_3_2") and shutil.rmtree("./test_3_2")
        os.path.exists("./test_3_3") and shutil.rmtree("./test_3_3")
    except:
        pass

def test1():
    logging.info("---------------------------------------------------------------------------------------------------------")
    logging.info("--- Standard test: 2 clients with write/read --- ")
    logging.info("---------------------------------------------------------------------------------------------------------")
    server0 = Server(55555)
    server1 = Server(55556)
    server2 = Server(55557)
    client1 =  Client(100, 0)
    client2 =  Client(101, 1)
    client1.write("A", "A0")
    print(f"Client 1: A - {client1.read('A')}")
    print(f"Client 2: A - {client2.read('A')}")
    client2.write("A", "A1")
    print(f"Client 1: A - {client1.read('A')}")
    print(f"Client 2: A - {client2.read('A')}")
    server1.stop()
    server2.stop()
    server0.stop()


def test2():
    logging.info("-------------------------------------------")
    logging.info("--- Causal dependency test: 3 clients  --- ")
    logging.info("-------------------------------------------")
    server0 = Server(55555)
    server1 = Server(55556)
    server2 = Server(55557, True)
    Alice =  Client(100, 0)
    Bob =  Client(101, 1)
    Charlie = Client(102, 2)
    Alice.write("M", "I've lost my wedding ring")
    # print(f"Alice: M - {Alice.read('M')}")
    # print(f"Bob : M - {Bob.read('M')}")
    # print(f" Charlie: M - {Charlie.read('M')}")
    Alice.write("M", "Whew, found it upstairs!")
    print(f"Alice: M - {Alice.read('M')}")
    print(f"Bob : M - {Bob.read('M')}")
    print(f"Charlie: M - {Charlie.read('M')}")
    Bob.write("M", "Glad to hear that")
    print(f"Alice: M - {Alice.read('M')}")
    print(f"Bob : M - {Bob.read('M')}")
    print(f"Charlie: M - {Charlie.read('M')}")
    time.sleep(40)
    print(f"Alice: M - {Alice.read('M')}")
    print(f"Bob : M - {Bob.read('M')}")
    print(f"Charlie: M - {Charlie.read('M')}")
    server1.stop()
    server2.stop()
    server0.stop()

# cleanup()
test1()
test2()
# test3()
