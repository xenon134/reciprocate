print('Initialising ... ')
import socket
from io import BytesIO
from PIL import Image
import pygame, time, threading

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
    mt = threading.main_thread()
    while mt.is_alive():
        print("\r\t\tFPS =", round(1/lag, 3), end=" \t\t")
        #pygame.display.set_caption('FPS: ' + str(round(1/lag, 3)))
        time.sleep(0.1) # 200 ms
lag = float('inf')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind(con2)
    sock.listen()
    print("Server started @ " + str(con2[0]) + ":" + str(con2[1]))
    sock, addr = sock.accept()
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    print("Client connected IP:", addr)

    size = int.from_bytes(sock.recv(2), "big"), int.from_bytes(sock.recv(2), "big")
    pygame.init()
    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
    clock = pygame.time.Clock()
    watching = True
    t1 = 0
    threading.Thread(target=displayFpsFunc).start()

    while watching:
        lag = time.time() - t1
        t1 = time.time()
        newSize = None

        for event in pygame.event.get():
            #print(event)
            if event.type == pygame.QUIT:
                watching = False
                break
            elif event.type == pygame.WINDOWRESIZED:
                newSize = event.x, event.y

        if newSize:
            sock.sendall(b'\xff')
            for i in newSize:
                sock.sendall(i.to_bytes(2, "big"))
            print(f'\rResized to {newSize[0]}x{newSize[1]}   \t\t')
        else:
            sock.sendall(b'\x00')
        leng = recvall(sock, 3)
        if leng != b'\xff\xff\xff': # screen same as before
            leng = int.from_bytes(leng, byteorder="big")
            bs = recvall(sock, leng)
            bs = BytesIO(bs)
            img = Image.open(bs, formats=['jpeg'])
            img = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
            screen.blit(img, (0, 0))
            pygame.display.flip()
        
        clock.tick(60)
