import socket 
import select 
import sys 
import rsa
from _thread import * 
import threading

# https://stackoverflow.com/questions/65597453/how-to-store-private-and-public-key-into-pem-file-generated-by-rsa-module-of-pyt


#def heartbeat_listener()

def create_client(conn, addr):
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

    while threading.main_thread().isAlive(): 
        try: 
            message = conn.recv(2048)

            if message: 
                # prints message and addr of user who sent the message 
                # on server terminal 
                message_decrypted = rsa.decrypt(message, private_key).decode('utf8')
                print(f"<{addr[0]}> {message_decrypted}")
                
                # calls message_all_clients function to send message to all 
                message_to_send = f"<{addr[0]}> {message_decrypted}"
                message_all_clients(message_to_send, conn, public_key)
            else:
                # messed up connection 
                remove(conn)
        except: 
            continue
        '''
        # constantly try pinging client with info to see if it's "alive" or not 
        try:
            keepalive_message_encrypted = rsa.encrypt("wliqqquekhrlkjnsmnaqqq".encode(), public_key)
            conn.send(keepalive_message_encrypted)
        except: 
            print("whoopsie woo!@@@@@")
        '''
    print("exiting")

#TODO: debug this on your other computer, for some reason the RSA module isn't installing correctly :/
def message_all_clients(message, connection, public_key): 
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
        print("[WARNING] Incorrect usage of program.")
        print("Correct usage: ")
        print("python3 server-side.py HOST_IP HOST_PORT")
        exit()

    else:
        
        list_of_clients = []
        host_IP = str(sys.argv[1])
        port = int(sys.argv[2])
        server.bind((host_IP, port))
        server.listen(100)

    try:    
        while True:
            conn, addr = server.accept()
    
            list_of_clients.append(conn)
    
            # connect message
            print (addr[0] + " connected")
    
            # create client for each connected user
            start_new_thread(create_client,(conn,addr))    

    except(KeyboardInterrupt, SystemExit):
        print("bye")
        #conn.close()
        server.close()