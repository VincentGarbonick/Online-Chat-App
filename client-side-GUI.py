import socket
import select
import sys
import rsa
import threading
from _thread import *
from tkinter import *
from tkinter.scrolledtext import ScrolledText
import time

def insert_tester(text_area):
    while True:
        text_area.insert(INSERT,"fart lol\n")
        time.sleep(3)



# Creating tkinter main window
win = Tk()
win.title("ScrolledText Widget")
  
# Title Label
'''
Label(win, 
          text = "ScrolledText Widget Example",
          font = ("Times New Roman", 15), 
          background = 'green', 
          foreground = "white").grid(column = 0,
                                     row = 0)
'''
# Creating scrolled text 
# area widget
text_area = ScrolledText(win, 
                        wrap = WORD, 
                        width = 40, 
                        height = 10, 
                        font = ("Times New Roman", 15))
  
text_area.grid(column = 0, pady = 10, padx = 10)
text_area.insert(INSERT,
"""\
This is a scrolledtext widget to make tkinter text read only.
Hi
Geeks !!!
Geeks !!!
Geeks !!! 
Geeks !!!
Geeks !!!
Geeks !!!
Geeks !!!
""")
#start_new_thread(insert_tester, (text_area,))

win.mainloop()