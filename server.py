import socket
import threading
import os
import random
import audio_metadata as am
from time import sleep

class musicStream:

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = "localhost"
        self.port = 1337
        self.active_threads = []
        self.music = os.listdir("/home/monster/music")
        self.flag = True
        self.size = 1024

    def start(self):
        try:
            self.socket.bind((self.host, self.port))
            print("Stream started waiting for requests.")
        except (socket.error, OSError) as error:
            print(error)
            self.socket.close()
            return False
        
        while True:
            try:
                data, addr = self.socket.recvfrom(self.size)
                print(f"Song request from {addr[0]} on port {addr[1]}")
            except socket.error as error:
                print(error)
                self.socket.close()
                return False
            if b"GET SONG" in data:
                thread = threading.Thread(target=self.handler, args=(data, addr,))
                thread.start()
                self.active_threads.append(thread)
            else:
                pass
    
    def handler(self, data, addr):
        print(f"Inbound request from {addr[0]} on UDP port {addr[1]}")
        song = random.choice(self.music)
        m = am.load(f"/home/monster/music/{song}")
        title = f'TITLE({m["tags"]["artist"][0]} - {m["tags"]["title"][0]})'
        try:
            self.socket.sendto(title.encode(), (addr[0], addr[1]))
        except (socket.error, socket.timeout, OSError) as error:
            print(error)
            return False
        with open(f"/home/monster/music/{song}", "rb") as f:
            while True:
                data = f.read(20000)
                if not data:
                    print("Done with stream")
                    try:
                        self.socket.sendto(data, (addr[0], addr[1]))
                        self.socket.sendto(b"DONE", (addr[0], addr[1]))
                    except (socket.error, socket.timeout) as error:
                        return False
                    break
                try:
                    self.socket.sendto(data, (addr[0], addr[1]))
                except (socket.error, socket.timeout) as error:
                    print(error)
                    self.socket.close()
                    return error
        f.close()
        return True


if __name__ == "__main__":
    mystream = musicStream()
    mystream.start()
