#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import os,csv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

processingHost = "127.0.0.1" #Processingで立ち上げたサーバのIPアドレス
processingPort = 10001       #Processingで設定したポート番号

basePath = os.path.dirname(os.path.abspath(__file__))
logDir = os.path.normpath(os.path.join(basePath,'../flask-app/log'))

isSensorDetect = False
positionY = '0'

UPPERPOSITION = '100'
LOWERPOSITION = '500'

class EventHandler(FileSystemEventHandler):
    def on_created(self, event):
        print('%s has been created.' % event.src_path)
        return

    def on_modified(self, event):
        if getext(event.src_path) in ('.csv'):
            with open(event.src_path, "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    analyzeSensorData(row)
            with open(event.src_path, "w") as f:
                f.write('')
        return

    def on_deleted(self, event):
        print('%s has been deleted.' % event.src_path)
        return

def getext(filename):
    return os.path.splitext(filename)[-1].lower()

def analyzeSensorData(data):
    global positionY,isSensorDetect

    isSensorDetect = True
    if(data[1] == '1'):
        positionY = UPPERPOSITION
        print("bib sensor 1 is detected")
    elif(data[1] == '2'):
        positionY = LOWERPOSITION
        print("bib sensor 2 is detected")


def main():
    global isSensorDetect

    socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketClient.connect((processingHost, processingPort))

    eventHandler = EventHandler()
    observer = Observer()
    observer.schedule(eventHandler, logDir)
    observer.start()

    try:
        while True:
            if(isSensorDetect):
                socketClient.send(positionY.encode('utf-8'))
                isSensorDetect = False
    except (Exception, KeyboardInterrupt):
        observer.stop()
    observer.join()

if __name__ == '__main__':
    main()
