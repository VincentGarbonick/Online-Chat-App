import socket
import select
import sys
import rsa
import threading
from _thread import *

def print_kitty():
    print(r"""
                                     ,
              ,-.       _,---._ __  / \
             /  )    .-'       `./ /   \
            (  (   ,'            `/    /|
             \  `-"             \'\   / |
              `.              ,  \ \ /  |
               /`.          ,'-`----Y   |
              (            ;        |   '
              |  ,-.    ,-'         |  /
              |  | (   | Kitty Chat | /
              )  |  \  `.___________|/
              `--'   `--'
              """)
def listener(server, public_key, private_key):
    try:
        while True:
            # maintains a list of possible input streams
            #sockets_list = [sys.stdin, server]
            sockets_list = [server]

            # select.select is for monitoring sockets, open files, and pipes until they can be R/W 
            # https://bip.weizmann.ac.il/course/python/PyMOTW/PyMOTW/docs/select/index.html
            read_sockets, write_socket, error_socket = select.select(sockets_list,[],[])

            # constantly checking between the server for broadcasted messages, 
            # or sending a message of its own 
            for socks in read_sockets:
                if socks == server:
                    message = socks.recv(2048)
                    try:
                        message_decrypted = rsa.decrypt(message, private_key).decode('utf8')
                        print(message_decrypted)
                    # for some reason, when the program first runs, the server sends some kind of unencrypted string,
                    # so the program whines and fails to decrypt the first time
                    except:
                        continue 
    except Exception as e:
        print(e)
        server.close()
        exit()



if __name__ == "__main__":
    try:
        # IPV4 and TCP 
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if len(sys.argv) != 3:
            print("[WARNING] Incorrect usage of program.")
            print("Correct usage: ")
            print("python3 server-side.py HOST_IP HOST_PORT")
            exit()
        host_IP = str(sys.argv[1])
        port = int(sys.argv[2])
        server.connect((host_IP, port))


        # open our private and public keys 
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
        
        start_new_thread(listener, (server, public_key, private_key))
        print_kitty()
        # Get user name
        print("\nEnter username: " , end='')
        #print("Enter username: ")
        username = sys.stdin.readline()
        server.send(rsa.encrypt(username.encode(), public_key))

        while True: 
            #TODO: format this [redacted] to look like <username/ID> _____ and have your 
            # message there so it looks like a chatroom

            # due to python being infuriating, you have to write print like this or else 
            # it won't print in loop
            # https://stackoverflow.com/questions/25368786/python-print-does-not-work-in-loop
            sys.stdout.write(f"{username.strip()}: ")
            sys.stdout.flush()

            message_encrypted = rsa.encrypt(sys.stdin.readline().encode(), public_key)
            server.send(message_encrypted)

    except(KeyboardInterrupt, SystemExit): 
        print("\nClient Exiting...")
        #close the socket
        message_encrypted = rsa.encrypt("Disconnected".encode(), public_key)
        server.send(message_encrypted)
        server.close()

    except Exception as e:
        print(e)
        exit()
        