import socket
from io import BytesIO
from PIL import Image, ImageTk
import time, threading, tkinter as tk

con2 = "", 16247


def recvall(conn, length):
    buf = b""
    while len(buf) < length:
        data = conn.recv(length - len(buf))
        if not data:
            return data
        buf += data
    return buf

def displayFpsFunc():
    while True:
        print("\r\t\tFPS = " + str(round(1/lag, 3)), end=" \t\t")
        time.sleep(0.1) # 40 ms
displayFpsThread = threading.Thread(target=displayFpsFunc)
displayFpsThread.setDaemon(True)
lag = float('inf')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind(con2)
    sock.listen()
    print(f"Server started @ {con2[0]}:{con2[1]}")
    sock, addr = sock.accept()
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    print("Client connected IP:", addr)

    size = int.from_bytes(sock.recv(2), "big"), int.from_bytes(sock.recv(2), "big")

    root = tk.Tk()
    root.geometry(f'{size[0]}x{size[1]}')
    root.resizable(False, False)
    lbl = tk.Label(root, bd=0)
    lbl.pack()

    watching = True
    displayFpsThread.start()

    def update():
        global lag
        global phImg
        t1 = 0
        while watching:
            lag = time.time() - t1
            t1 = time.time()

            sock.sendall(b"\xff")
            leng = int.from_bytes(sock.recv(3), byteorder="big")
            bs = recvall(sock, leng)
            bs = BytesIO(bs)
            img = Image.open(bs)
            phImg = ImageTk.PhotoImage(img)
            lbl.configure(image = phImg)
            root.after(0, update)
    root.after(0, update)
    print('Starting mainloop.')
    root.mainloop()
