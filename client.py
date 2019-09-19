import socket
import io
import threading
import re
import os
import platform
from pydub import AudioSegment
from time import sleep
if "Windows" in platform.platform():
    hostos = "Windows"
    from pydub.playback import play
elif "Linux" in platform.platform():
    hostos = "Linux"
    from pydub.playback import _play_with_simpleaudio as play

class myClient:

    def __init__(self):
        self.host = "192.168.0.7"
        self.port = 1337
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(15)
        self.chunk = 50000
        self.flag = True
        self.stream = []
        self.title = []
        self.p = None
        self.lastsong = []

    def onTimeout(self):
        print("Communication with server timed out sleeping for 30 seconds..")
        sleep(30)
        if hostos == "Windows":
            os.system("cls")
        else:
            os.system("clear")
        self.get_stream()

    def waiting(self):
        while True:
            if len(self.title) == 0:
                sleep(1)
            else:
                if hostos == "Windows":
                    os.system("cls")
                else:
                    os.system("clear")
                break
        while True:
            if len(self.title) == 0:
                sleep(1)
            if len(self.title) != 0  and self.title[0] not in self.lastsong:
                self.lastsong.append(self.title[0])
            if len(self.title) != 0 and len(self.lastsong[0]) > len(self.title[0]):
                var = len(self.lastsong[0]) - len(self.title[0])
                self.lastsong.pop(0)
            else:
                var = 0
            if len(self.title) != 0:
                animation = [f" {self.title[0]} |" + " "*var, f" {self.title[0]} /" + " "*var, f" {self.title[0]} -" + " "*var, f" {self.title[0]} \\" + " "*var]
                for x in animation:
                    print(x, end="\r", flush=True)
                    sleep(.2)
        return False

    def connect(self):
        thread = threading.Thread(target=self.get_stream)
        thread.start()
        wthread = threading.Thread(target=self.waiting)
        wthread.start()
        print(" Tuning into radio.. Please wait..", end="\r", flush=True)
        while True:
            if len(self.stream) == 0:
                sleep(1)
            else:
                self.p = play(self.stream[0])
                if hostos == "Linux":
                    self.p.wait_done()
                self.stream.remove(self.stream[0])
                self.title.pop(0)

    def get_stream(self):
        while True:
            buffer = b""
            if len(self.stream) < 3:
                try:
                    self.socket.sendto(b"GET SONG", (self.host, self.port))
                except OSError as error:
                    print(error)
                    self.onTimeout()
                while True:
                    try:
                        data, addr = self.socket.recvfrom(self.chunk)
                    except (socket.timeout, OSError) as error:
                        while len(self.stream) != 0:
                            sleep(1)
                        self.onTimeout()
                    if b"TITLE" in data:
                        match = re.search(b"TITLE\((.*)\)", data)
                        data.strip(b"TITLE(" + match.group(1) + b")")
                    if b"DONE" in data:
                        data.strip(b"DONE")
                        buffer += data
                        break
                    buffer += data
                stream = AudioSegment.from_file(io.BytesIO(buffer), format="mp3")
                self.stream.append(stream)
                self.title.append(match.group(1).decode())
                del buffer
            else:
                sleep(1)
        return False

if __name__ == "__main__":
    client = myClient()
    client.connect()