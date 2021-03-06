from ipaddress import ip_address
import socket 
import select 
import sys 
import rsa
from _thread import *
import threading
import time 
import logging 

# https://stackoverflow.com/questions/65597453/how-to-store-private-and-public-key-into-pem-file-generated-by-rsa-module-of-pyt

# global variables for the list of clients and addresses
list_of_clients = []
list_of_addresses = []

# Sends a pulse to the client servers to make sure they are alive. Currently unimlemented. 
def heartbeat_listener():    
    # instantiate a dummy socket object to test heartbeats with
    s = socket.socket()
    while threading.main_thread().isAlive(): 
        
        for addr in list_of_addresses:
            try:
                #print("Connecting to : " + str(addr))
                #test = socket.create_connection(('173.89.275.99', 33116),1)
                test = socket.create_connection(addr,1)

            except Exception as e:
                #print(e)
                continue

        time.sleep(1)

# Creates a client serverside when a use connects
# Inputs: Connection and address, keys, and logging object 
def create_client(conn, addr, public_key, private_key, log):

    # wait on username authorization 
    username = rsa.decrypt(conn.recv(2048), private_key).decode('utf8').strip() # remove newline at end 
    # addr is formatted like IP, port, and we only care about IP. Cut it out. Also cut out leading parenthesis.
    ip_address = (str(addr).split(",")[0])[1:]

    print(f"{username} connecting from {ip_address}")
    log.info(f"{username} connecting from {ip_address}")
    message_all_clients(f"{username} connected", conn, public_key)

    while threading.main_thread().isAlive(): 
        try: 
            # blocks until it gets at least one byte or the socket is closed
            message = conn.recv(2048)

            if message: 
                # prints message and addr of user who sent the message 
                # on server terminal 
                message_decrypted = rsa.decrypt(message, private_key).decode('utf8')

                print(f"{username}: {message_decrypted}".strip())
                log.info(f"{username}: {message_decrypted}".strip())

                # calls message_all_clients function to send message to all 
                message_to_send = f"{username}: {message_decrypted}"
                message_all_clients(message_to_send, conn, public_key)

        except: 
            if conn in list_of_clients:
                log.info(f"Removing {conn}")
                list_of_clients.remove(conn)

# Messages all the clients in the names list. 
def message_all_clients(message, connection, public_key): 
    for client in list_of_clients:
        if client != connection:
            try: 
                client.send(rsa.encrypt(message.encode(), public_key))
            except: 
                client.close()
                if connection in list_of_clients:
                    log.info(f"Removing {connection}")
                    list_of_clients.remove(connection)
                  
if __name__ == "__main__":
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    
    # set up logging 
    log = logging.getLogger("mylog")
    log.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")
    filehandler = logging.FileHandler("server_log.txt", "a")
    filehandler.setLevel(logging.INFO)
    filehandler.setFormatter(formatter)
    log.addHandler(filehandler)
    

    if len(sys.argv) != 3:
        print("[WARNING] Incorrect usage of program.")
        print("Correct usage: ")
        print("python3 server-side.py HOST_IP HOST_PORT")
        exit()

    else:
        
        log.info("Starting server...")
        host_IP = str(sys.argv[1])
        port = int(sys.argv[2])
        server.bind((host_IP, port))
        server.listen(100)

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

        except Exception as e:
            print(e)
            log.warn(e)
            exit()
        
        #start_new_thread(heartbeat_listener,())
        
    try:    
        while True:
            # conn is a socket object that can send and recieve data 
            # addr is the address bound to the socket on the other end of the connection 
            conn, addr = server.accept()
            list_of_clients.append(conn)
            list_of_addresses.append(addr)
    
            # create client for each connected user
            start_new_thread(create_client,(conn, addr, public_key, private_key, log))   

    except(KeyboardInterrupt, SystemExit):
        print("\nServer closed...")
        log.info("Server closed.")
        message = "Server shutting down..."
        for client in list_of_clients:
            try: 
                client.send(rsa.encrypt(message.encode(), public_key))
            except: 
                continue 
        server.close()

    except Exception as e:
        log.warn(e)
        server.close()