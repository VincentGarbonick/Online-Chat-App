import socket
import select
import sys
import rsa
import threading
from _thread import *
from tkinter import *
from tkinter.scrolledtext import ScrolledText
import time

WIN_WIDTH = 40
WIN_HEIGHT = 10
TEXT_BOX_HEIGHT = 1.5

def return_kitty():
    return(r"""
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

def insert_tester(text_area):
    while True:
        text_area.insert(INSERT,"fart lol\n")
        time.sleep(3)


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

def send_message(text_area, public_key, server, input_box):
    # get all text from the input box 
    text = input_box.get("1.0", "end-1c")
    text_area.insert(INSERT,f"Me:{text}\n")
    message_encrypted = rsa.encrypt(text.encode(), public_key)
    server.send(message_encrypted)
    
    input_box.delete('1.0', END)

if __name__ == "__main__":
    try:
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
        
        #start_new_thread(listener, (server, public_key, private_key))

        # Creating tkinter main window
        root = Tk()
        root.title("Kitty Chat")
        #root.geometry("600x400")

        root.columnconfigure(0, weight=3)
        root.columnconfigure(1, weight=1)

        text_area = ScrolledText(root, wrap = WORD, font = ("Times New Roman", 15))
        text_area.grid(row=0, column=0, columnspan=1, sticky=N, padx=(10,0))


        input_box = Text(root, height=TEXT_BOX_HEIGHT)
        input_box.grid(row= 1, column = 0, sticky = W, padx=(10,0), pady=(10,10))

        send_button = Button(root, text="Send", height=1, 
        width=10, command= lambda: send_message(text_area, public_key, server, input_box))

        send_button.grid(row=1, column=0, sticky= E, padx=30)

        #start_new_thread(insert_tester, (text_area,))
        root.resizable(False, False)
        text_area.insert(INSERT, "Welcome to Kitty Chat!\n")
        text_area.insert(INSERT, "Enter your username and press \"send\" to begin!\n")
        root.mainloop()
        # Get user name
        
        #print("\nEnter username: " , end='')
        #print("Enter username: ")
        #username = sys.stdin.readline()
        #server.send(rsa.encrypt(username.encode(), public_key))
        '''
        while True: 

            sys.stdout.write(f"{username.strip()}: ")
            sys.stdout.flush()

            message_encrypted = rsa.encrypt(sys.stdin.readline().encode(), public_key)
            server.send(message_encrypted)
        '''
    except(KeyboardInterrupt, SystemExit): 
        print("\nClient Exiting...")
        #close the socket
        message_encrypted = rsa.encrypt("Disconnected".encode(), public_key)
        server.send(message_encrypted)
        server.close()

    except Exception as e:
        print(e)
        exit()
        