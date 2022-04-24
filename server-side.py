import socket 
import select 
import sys 
import rsa
from _thread import * 

# https://stackoverflow.com/questions/65597453/how-to-store-private-and-public-key-into-pem-file-generated-by-rsa-module-of-pyt

def clientthread(conn, addr):
    try:
        public_file = open("public.txt", "r")
        private_file = open("private.txt", "r")

        public_raw = public_file.read()
        private_raw = private_file.read()

        # we now have our keys 
        public_key = rsa.PublicKey.load_pkcs1(public_raw.encode('utf8'))
        private_key = rsa.PrivateKey.load_pkcs1(private_raw.encode('utf8'))

        public_file.close()
        private_file.close()

    except:

        print("Keys not found. Look at README and consider generating some!")
        exit()

    # TODO: send all messages stored in message history to this
    conn.send("Welcome to this Chatroom".encode())

    while True: 
        try: 
            message = conn.recv(2048)

            if message: 
                # prints message and addr of user who sent the message 
                # on server terminal 
                message_decrypted = rsa.decrypt(message, private_key).decode('utf8')
                print(f"<{addr[0]}> {message_decrypted}")
                
                # calls broadcast function to send message to all 
                message_to_send = f"<{addr[0]}> {message_decrypted}"
                broadcast(message_to_send, conn, public_key)
            else:
                # messed up connection 
                remove(conn)
        except: 
            continue
#TODO: make sure broadcast is working with encoding/decoding 
def broadcast(message, connection, public_key): 
    for clients in list_of_clients:
        if clients != connection:
            try: 
                clients.send(rsa.encrypt(message.encode(), public_key))
            except: 
                clients.close()
                remove(clients)

def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)
        
                  
if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

    if len(sys.argv) != 3:
        print("Provide Script, IP address, port number")

    else:
        IP_address = str(sys.argv[1])

        port = int(sys.argv[2])

        server.bind((IP_address, port))

        server.listen(100)

        list_of_clients = []

    while True:

        conn, addr = server.accept()
 

        list_of_clients.append(conn)
 
        # prints the address of the user that just connected
        print (addr[0] + " connected")
 
        # creates and individual thread for every user
        # that connects
        start_new_thread(clientthread,(conn,addr))    
 
    conn.close()
    server.close()