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

class MyDialog:
    def __init__(self, parent):
        top = self.top = Toplevel(parent)
        top.geometry("300x100")
        self.myLabel = Label(top, text='Enter your username below')
        self.myLabel.pack()
        
        self.myEntryBox = Entry(top)
        self.myEntryBox.pack()

        self.mySubmitButton = Button(top, text='Submit', command=self.send)
        self.mySubmitButton.pack()

    def send(self):
        global username
        username = self.myEntryBox.get()
        self.top.destroy()

def spawnDialog(root, public_key):
    inputDialog = MyDialog(root)
    root.wait_window(inputDialog.top)
    #print('Username: ', username)
    message_encrypted = rsa.encrypt(username.encode(), public_key)
    server.send(message_encrypted)

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


def listener(server, text_area, private_key):
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
                        text_area.configure(state='normal')

                        text_area.insert(INSERT,f"{message_decrypted}\n")
                        text_area.configure(state='disabled')
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
    text_area.configure(state='normal')
    text = input_box.get("1.0", "end-1c")
    text = str(text).strip()
    text_area.insert(INSERT,f"{username}: {text}\n")
    message_encrypted = rsa.encrypt(text.encode(), public_key)
    server.send(message_encrypted)
    
    input_box.delete('1.0', END)
    text_area.configure(state='disabled')

def close_protocol(server, root):
    print("\nClient Exiting...")
    #close the socket
    message_encrypted = rsa.encrypt("Disconnected".encode(), public_key)
    server.send(message_encrypted)
    server.close()
    root.destroy()


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
        

        # Creating tkinter main window
        root = Tk()
        root.title("Kitty Chat")
        root.geometry("800x620")
        #root.geometry("1000x1000")

        root.columnconfigure(0, weight=3)
        root.columnconfigure(1, weight=1)

        text_area = ScrolledText(root, wrap = WORD, font = ("Times New Roman", 15))
        text_area.grid(row=0, column=0, columnspan=2, sticky=NW, padx=(10,0))


        input_box = Text(root, height=TEXT_BOX_HEIGHT)
        input_box.grid(row= 1, column = 0, sticky = W, padx=(10,0), pady=(10,10))

        send_button = Button(root, text="Send", height=1, 
        width=10, command= lambda: send_message(text_area, public_key, server, input_box))

        send_button.grid(row=1, column=1, sticky= E, padx=30)

        #start_new_thread(insert_tester, (text_area,))
        root.resizable(False, False)
        text_area.insert(INSERT, "Welcome to Kitty Chat!\n")
        text_area.insert(INSERT, "Enter your username and press \"send\" to begin!\n")
        text_area.configure(state='disabled')
        start_new_thread(listener, (server, text_area, private_key))

        # when we press enter, it's the same as clicking send 
        root.bind('<Return>', lambda event=None: send_button.invoke())

        # if we press "exit," it is the same as cancelling this program from terminal
        root.protocol("WM_DELETE_WINDOW", lambda: close_protocol(server, root))
        
        #disable our input box and button until the user puts a username in 
        input_box.configure(state='disabled')
        send_button.configure(state='disabled')
        spawnDialog(root, public_key)
        input_box.configure(state='normal')
        send_button.configure(state='normal')

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
        