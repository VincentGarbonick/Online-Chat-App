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

def insert_tester(text_area):
    while True:
        text_area.insert(INSERT,"fart lol\n")
        time.sleep(3)



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

send_button = Button(root, text="Send")
send_button.grid(row=1, column=0, sticky= E, padx=50)

#start_new_thread(insert_tester, (text_area,))
root.resizable(False, False) 
root.mainloop()