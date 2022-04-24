import socket 
import select 
import sys 
from _thread import * 

def clientthread(conn, addr):
    # TODO: send all messages stored in message history to this
    conn.send("Welcome to this Chatroom".encode())

    while True: 
        try: 
            message = conn.recv(2048)

            if message: 
                # prints message and addr of user who sent the message 
                # on server terminal 
                print("<" + addr[0] + ">" + message)

                # calls broadcast function to send message to all 
                message_to_send = print(f"<{addr[0]}> {message}")
                broadcast(message_to_send, conn)
            else:
                # messed up connection 
                remove(conn)
        except: 
            continue

def broadcast(message, connection): 
    for clients in list_of_clients:
        if clients != connection:
            try: 
                clients.send(message)
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