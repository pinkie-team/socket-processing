#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import os,csv,time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

processingHost = "127.0.0.1" #Processingで立ち上げたサーバのIPアドレス
processingPort = 10001       #Processingで設定したポート番号

basePath = os.path.dirname(os.path.abspath(__file__))
logDir = os.path.normpath(os.path.join(basePath,'../flask-app/log'))
sensor1FileName = "1.csv"
sensor2FileName = "2.csv"

isSensor1Detect = False
isSensor2Detect = False
positionY = '0'

UPPERPOSITION = '100'
LOWERPOSITION = '700'

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
    global positionY,isSensor1Detect,isSensor2Detect

    if(data[1] == '1'):
        positionY = UPPERPOSITION
        isSensor1Detect = True
        print("bib sensor 1 is detected")
    elif(data[1] == '2'):
        positionY = LOWERPOSITION
        isSensor2Detect = True
        print("bib sensor 2 is detected")

def main():
    global isSensor1Detect,isSensor2Detect

    socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketClient.connect((processingHost, processingPort))

    eventHandler = EventHandler()
    observer = Observer()
    observer.schedule(eventHandler, logDir)
    observer.start()

    '''
    while True:
        if(isSensor1Detect and isSensor2Detect):
            socketClient.send("300".encode('utf-8'))
            isSensor1Detect = False
            isSensor2Detect = False
        elif(isSensor1Detect or isSensor2Detect):
            socketClient.send(positionY.encode('utf-8'))
            isSensor1Detect = False
            isSensor2Detect = False
        time.sleep(0.1)
    '''
    try:
        file1 = open(logDir + "/" + sensor1FileName, 'w')
        if len(open(logDir + "/" + sensor1FileName).readlines()) != 0:
            print("im alive")
            file1.write('')
        file1.close()

        file2 = open(logDir + "/" + sensor1FileName, 'w')
        if len(open(logDir + "/" + sensor1FileName).readlines()) != 0:
            file2.write('')
        file2.close()

        while True:
            if(isSensor1Detect and isSensor2Detect):
                socketClient.send("400".encode('utf-8'))
                print("1 and 2 sensor is detected")
                isSensor1Detect = False
                isSensor2Detect = False
            elif(isSensor1Detect or isSensor2Detect):
                socketClient.send(positionY.encode('utf-8'))
                isSensor1Detect = False
                isSensor2Detect = False
            time.sleep(0.5)
    except (Exception, KeyboardInterrupt):
        observer.stop()
    observer.join()

if __name__ == '__main__':
    main()
