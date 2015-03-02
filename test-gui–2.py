#!/usr/bin/env python3

import socket
import threading
import tkinter
import time
from tkinter import ttk
from queue import Queue

INPUT_PORT = 38802
OUTPUT_PORT = 38801
SIZE = 1024

class Client(threading.Thread):

    def __init__(self, queue):
        super().__init__()
        self.daemon = True
        self.queue = queue

    def run(self):
        while True:
            msg = self.queue.get()
            server = socket.socket()
            host = socket.gethostname()
            server.connect((host, OUTPUT_PORT))
            server.send(bytes(msg, "utf-8"))
            server.close()

class Server(threading.Thread):

    def __init__(self, client, addr, queue):
        super().__init__()
        self.client = client
        self.addr = addr
        self.queue = queue
        self.daemon = True

    def run(self):
        while True:
            msg = self.client.recv(SIZE)
            if not msg:
                break
            self.queue.put(msg.decode("utf-8"))
        self.client.close()

class HandleRequest(threading.Thread):

    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        self.daemon = True
        self.server = socket.socket()
        self.host = socket.gethostname()

    def run(self):
        self.server.bind((self.host, INPUT_PORT))
        self.server.listen(5)
        while True:
            client, addr = self.server.accept()
            server_thread = Server(client, addr, self.queue)
            server_thread.start()
            

class MainWindow(tkinter.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.parent.title("První GUI aplikace")
        self.parent.rowconfigure(0, weight=700)
        self.parent.rowconfigure(1, weight=200)
        self.parent.rowconfigure(2, weight=100)
        self.parent.columnconfigure(0, weight=800)
        self.parent.columnconfigure(1, weight=100)
        self.parent.columnconfigure(2, weight=100)
        self.create_widgets()
        self.in_queue = Queue()
        self.out_queue = Queue()
        self.client_thread = Client(self.out_queue)
        self.client_thread.start()
        self.server_thread = HandleRequest(self.in_queue)
        self.server_thread.start()
        self.check_message()

    def create_widgets(self):
        self.scroll_bar_y = ttk.Scrollbar(orient = tkinter.VERTICAL)
        self.scroll_bar_x = ttk.Scrollbar(orient = tkinter.HORIZONTAL)
        self.notepad = tkinter.Text(undo = True,
                                    state = "disabled",
                                    wrap = tkinter.NONE,
                                    yscrollcommand = self.scroll_bar_y.set,
                                    xscrollcommand = self.scroll_bar_x.set,
                                    )
        self.entry = tkinter.Entry(text="")
        self.button = ttk.Button(text="Odeslat")
        
        self.button["command"] = self.send_message
        self.scroll_bar_y["command"] = self.notepad.yview
        self.scroll_bar_x["command"] = self.notepad.xview

        self.notepad.grid(row=0, column=0, columnspan=2, sticky=tkinter.NSEW, padx=2, pady=2)
        self.scroll_bar_y.grid(row=0, column=2, sticky=tkinter.NS)
        self.scroll_bar_x.grid(row=1, column=0, columnspan=2, sticky=tkinter.EW)
        self.entry.grid(row=2, column=0, sticky=tkinter.NSEW, padx=2)
        self.button.grid(row=2, column=1, columnspan=2, sticky=tkinter.NSEW)

    def check_message(self):
        if not self.in_queue.empty():
            text = self.in_queue.get()
            self.notepad.configure(state="normal")
            self.notepad.insert(tkinter.END, "<<< "+text+"\n")
            self.notepad.configure(state="disabled")
        self.parent.after(100, self.check_message)

    def send_message(self):
        text = self.entry.get()
        if text:
            self.out_queue.put(text)
            self.notepad.configure(state="normal")
            self.notepad.insert(tkinter.END, ">>> "+text+"\n")
            self.notepad.configure(state="disabled")
        

root = tkinter.Tk()
app = MainWindow(root)
app.mainloop()
