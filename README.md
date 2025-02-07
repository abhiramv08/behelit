# Behelit
Behelit: A causal key-value database

This system implements Causal Consistency when messages need to be replicated across multiple servers and there is a causal relation between the messages. Each message has a dependency associated with it depending on the causal order of messages and represented by vector clocks present on the clients and the server.

This is implemented by a key value store structure, where each client interacts with a particular key and can either perform a read or a write operation. Each client has its own primary server and performs the operation on it directly. It is the primary’s job to replicate the operations onto other existing servers. Another client may read/write on key and expects causal consistency.

## Protocol
A client increments its vector clock by 1 whenever it generates a message write on the server. It sends the updated value and its own vector clock to its server. Once the server makes sure that this write has its dependencies resolved, it can update the key/value store. And then replicate this message to other servers. Server checks for dependency by the following algorithm:
1) Check if this write from the client has timestamp just 1 apart from the index in its own vector clock
2) Every other client’s write requests occurring before this write have already been implemented (every other index in the message vector clock is same as its own).
This ensures that messages are delivered in a causal order. If the conditions aren’t met, the
server’s thread waits until some other thread receives this message.

## Program Structure
The program is divided into client, server and util files. Common functionalities like socket programming code, vector clock handling, dependency checking are done in the util file. Client exposes write() and read() APIs. Server handles the incoming network request and writes/reads its own data base and may replicate the message. The server supports multithreading, so it doesn’t block a client. Bytes over the socket are deserialized to requests and responses. 

## Run Steps
For the demo, we just change directory to test, and run the python file, test.py  
cd ./test  
python test.py
