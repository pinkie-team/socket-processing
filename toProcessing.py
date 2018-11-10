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

motion1FileName = "motion_1.csv"
motion2FileName = "motion_2.csv"
motion3FileName = "motion_3.csv"
sound1FileName = "sound_1.csv"
sound2FileName = "sound_2.csv"
sound3FileName = "sound_3.csv"

isMotion1Detect = False
isMotion2Detect = False
isMotion3Detect = False
isSound1Detect = False
isSound2Detect = False
isSound3Detect = False

#TODO 座標にxも追加したい ex)(0,300)
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
                    analyzeSensorData(getSensorType(event.src_path),row)
            with open(event.src_path, 'w') as f:
                f.write('')
        return

    def on_deleted(self, event):
        print('%s has been deleted.' % event.src_path)
        return

def getext(filename):
    return os.path.splitext(filename)[-1].lower()

def getSensorType(filename):
    basename = os.path.basename(filename)
    return basename.split('_')[0]

def analyzeSensorData(sensorType,data):
    global positionY,isMotion1Detect,isMotion2Detect,isMotion3Detect
    global isSound1Detect,isSound2Detect,isSound3Detect

    #TODO ファイル名で更に場合分け
    if(sensorType == 'motion'):
        if(data[1] == '1'):
            positionY = UPPERPOSITION
            isMotion1Detect = True
            print('motion sensor 1 is detected')
        elif(data[1] == '2'):
            positionY = LOWERPOSITION
            isMotion2Detect = True
            print('motion sensor 2 is detected')
        elif(data[1] == '3'):
            positionY = LOWERPOSITION
            isMotion3Detect = True
            print('motion sensor 3 is detected')
    if(sensorType == 'sound'):
        if(data[1] == '1'):
            positionY = UPPERPOSITION
            isSound1Detect = True
            print('sound sensor 1 is detected')
        elif(data[1] == '2'):
            positionY = LOWERPOSITION
            isSound2Detect = True
            print('sound sensor 2 is detected')
        elif(data[1] == '3'):
            positionY = LOWERPOSITION
            isSound3Detect = True
            print('sound sensor 3 is detected')

def resetSensorFlag():
    global isMotion1Detect,isMotion2Detect,isMotion3Detect
    global isSound1Detect,isSound2Detect,isSound3Detect
    isMotion1Detect = False
    isMotion2Detect = False
    isMotion3Detect = False
    isSound1Detect = False
    isSound2Detect = False
    isSound3Detect = False

def main():
    global isMotion1Detect,isMotion2Detect,isMotion3Detect
    global isSound1Detect,isSound2Detect,isSound3Detect

    socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketClient.connect((processingHost, processingPort))

    eventHandler = EventHandler()
    observer = Observer()
    observer.schedule(eventHandler, logDir)
    observer.start()

    #TODO 音声ログの場合も追記
    try:
        motion1File = open(logDir + '/' + motion1FileName, 'w')
        if len(open(logDir + '/' + motion1FileName).readlines()) != 0:
            motion1File.write('')
        motion1File.close()

        motion2File = open(logDir + '/' + motion2FileName, 'w')
        if len(open(logDir + '/' + motion2FileName).readlines()) != 0:
            motion2File.write('')
        motion2File.close()

        motion3File = open(logDir + '/' + motion3FileName, 'w')
        if len(open(logDir + '/' + motion3FileName).readlines()) != 0:
            motion3File.write('')
        motion3File.close()

        sound1File = open(logDir + '/' + sound1FileName, 'w')
        if len(open(logDir + '/' + sound1FileName).readlines()) != 0:
            sound1File.write('')
        sound1File.close()

        sound2File = open(logDir + '/' + sound2FileName, 'w')
        if len(open(logDir + '/' + sound2FileName).readlines()) != 0:
            sound2File.write('')
        sound2File.close()

        sound3File = open(logDir + '/' + sound3FileName, 'w')
        if len(open(logDir + '/' + sound3FileName).readlines()) != 0:
            sound3File.write('')
        sound3File.close()

        while True:
            if(isMotion1Detect and isMotion2Detect):
                socketClient.send('400'.encode('utf-8'))
            elif(isMotion1Detect or isMotion2Detect):
                socketClient.send(positionY.encode('utf-8'))
            elif(isSound1Detect and isSound2Detect):
                socketClient.send('400'.encode('utf-8'))
            elif(isSound1Detect or isSound2Detect):
                socketClient.send(positionY.encode('utf-8'))
            resetSensorFlag()
            time.sleep(0.5)
    except (Exception, KeyboardInterrupt):
        observer.stop()
    observer.join()

if __name__ == '__main__':
    main()
