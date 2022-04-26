import socket
import select
import sys
import rsa

# TODO: consider rewriting client to something like this for...reasons 
# https://python.plainenglish.io/build-a-chatroom-app-with-python-458fc435025a

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

try: 
    while True:
    
        # maintains a list of possible input streams
        sockets_list = [sys.stdin, server]
        
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
                
            else:
                #TODO: format this [redacted] to look like <username/ID> _____ and have your 
                # message there so it looks like a chatroom
                message_encrypted = rsa.encrypt(sys.stdin.readline().encode(), public_key)
                server.send(message_encrypted)

except(KeyboardInterrupt, SystemExit): 
    print("\nClient Exiting...")
    #close the socket
    message_encrypted = rsa.encrypt("Disconnected".encode(), public_key)
    server.send(message_encrypted)
    server.close()
