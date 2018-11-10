#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import os,csv,time
import math
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import traceback

DEMO = True

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

isMotionDetect = False
isSoundDetect = False

'''
window_width = 1440
window_height = 900
x1, x2, x3 = 100.0, window_width / 2.0, window_width - 100.0
y1, y2, y3 = window_height - 100, 100.0, window_height - 100.0
'''

window_width = 1824
window_height = 984
x1, x2, x3 = 516.8, 1064.0, 1611.2
y1, y2, y3 = 278.8, 574.0, 869.2

r1, r2, r3 = 1.0, 1.0, 1.0
MOTION_ALPHA = 1.0
SOUND_ALPHA = 1.0

#TODO 座標にxも追加したい ex)(0,300)
positionY = '0'
position = ['0','0']
UPPERPOSITION = '100'
LOWERPOSITION = '700'

motionSensorVal = ['0','0','0']
soundSensorVal = ['0','0','0']

class EventHandler(FileSystemEventHandler):
    def on_created(self, event):
        print('%s has been created.' % event.src_path)
        return

    def on_modified(self, event):
        if getext(event.src_path) in ('.csv'):
            with open(event.src_path, "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    readSensorData(getSensorType(event.src_path),row)
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

def readSensorData(sensorType,data):
    global positionY,isMotion1Detect,isMotion2Detect,isMotion3Detect
    global isSound1Detect,isSound2Detect,isSound3Detect
    global motionSensorVal,soundSensorVal

    #TODO ファイル名で更に場合分け
    if(sensorType == 'motion'):
        if(data[1] == '1'):
            positionY = UPPERPOSITION
            isMotion1Detect = True
            motionSensorVal[0] = data[2]
            print('motion sensor 1 is detected')
        elif(data[1] == '2'):
            positionY = LOWERPOSITION
            isMotion2Detect = True
            motionSensorVal[1] = data[2]
            print('motion sensor 2 is detected')
        elif(data[1] == '3'):
            positionY = LOWERPOSITION
            isMotion3Detect = True
            motionSensorVal[2] = data[2]
            print('motion sensor 3 is detected')
    if(sensorType == 'sound'):
        if(data[1] == '1'):
            positionY = UPPERPOSITION
            isSound1Detect = True
            soundSensorVal[0] = data[2]
            print('sound sensor 1 is detected')
        elif(data[1] == '2'):
            positionY = LOWERPOSITION
            isSound2Detect = True
            soundSensorVal[1] = data[2]
            print('sound sensor 2 is detected')
        elif(data[1] == '3'):
            positionY = LOWERPOSITION
            isSound3Detect = True
            soundSensorVal[2] = data[2]
            print('sound sensor 3 is detected')

def calc_kouten():
    global r1,r2,r3
    global x1,x2,x3,y1,y2,y3
    global window_width, window_height

    try:
        l = math.sqrt(pow(x2-x1, 2) + pow(y2-y1, 2))
        theta1 = math.atan2(y2-y1, x2-x1)
        theta2 = math.acos((pow(l, 2) + pow(r1, 2) - pow(r2, 2)) / (2 * l * r1))
    except ValueError:
        return {'x1': 0.0, 'y1': 0.0, 'x2': 0.0, 'y2': 0.0}

    xi1 = x1 + r1 * math.cos(theta1 + theta2)
    yi1 = y1 + r1 * math.sin(theta1 + theta2)
    xi2 = x1 + r1 * math.cos(theta1 - theta2)
    yi2 = y1 + r1 * math.sin(theta1 - theta2)

    return {'x1': xi1, 'y1': yi1, 'x2': xi2, 'y2': yi2}


def is_collision():
    global position
    kouten = calc_kouten()
    dx1 = abs(kouten['x1'] - x3)
    dx2 = abs(kouten['x2'] - x3)

    dy1 = abs(kouten['y1'] - y3)
    dy2 = abs(kouten['y2'] - x3)

    if math.sqrt(pow(dx1, 2)+pow(dy1, 2)) <= r3:
        position[0] = kouten['x1']
        position[1] = kouten['y1']
        print('************************')
        print('1: {} {}'.format(kouten['x1'], kouten['y1']))
        print('************************')
        return True
    if math.sqrt(pow(dx2, 2)+pow(dy2, 2)) <= r3:
        position[0] = kouten['x2']
        position[1] = kouten['y2']
        print('************************')
        print('2: {} {}'.format(kouten['x2'], kouten['y2']))
        print('************************')
        return True

    return False

def resetSensorFlag():
    global isMotion1Detect,isMotion2Detect,isMotion3Detect
    global isSound1Detect,isSound2Detect,isSound3Detect
    global motionSensorVal,soundSensorVal
    global r1,r2,r3

    isMotion1Detect = False
    isMotion2Detect = False
    isMotion3Detect = False
    isSound1Detect = False
    isSound2Detect = False
    isSound3Detect = False
    motionSensorVal = ['0','0','0']
    soundSensorVal = ['0','0','0']
    r1,r2,r3 = 1.0, 1.0, 1.0

def main():
    global isMotion1Detect,isMotion2Detect,isMotion3Detect
    global isSound1Detect,isSound2Detect,isSound3Detect
    global position
    global r1,r2,r3
    global motionSensorVal

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
            if(isMotion1Detect and isMotion2Detect and isMotion3Detect):
                if DEMO:
                    socketClient.send('{},{}'.format(window_width/2.0,window_height/2.0).encode('utf-8'))
                else:
                    while not is_collision():
                        r1 += float(motionSensorVal[0])*MOTION_ALPHA
                        r2 += float(motionSensorVal[1])*MOTION_ALPHA
                        r3 += float(motionSensorVal[2])*MOTION_ALPHA
                    #if is_collision():
                    print(position)
                    resetSensorFlag()
                    socketClient.send('{},{}'.format(position[0],position[1]).encode('utf-8'))

            elif(isMotion1Detect and isMotion2Detect):
                socketClient.send('200,200'.encode('utf-8'))
                resetSensorFlag()
            elif(isMotion1Detect and isMotion3Detect):
                socketClient.send('700,1000'.encode('utf-8'))
                resetSensorFlag()
            elif(isMotion2Detect and isMotion3Detect):
                socketClient.send('1000,200'.encode('utf-8'))
                resetSensorFlag()
            elif(isMotion1Detect):
                socketClient.send('{},{}'.format(x1,y1).encode('utf-8'))
                resetSensorFlag()
            elif(isMotion2Detect):
                socketClient.send('{},{}'.format(x2,y2).encode('utf-8'))
                resetSensorFlag()
            elif(isMotion3Detect):
                socketClient.send('{},{}'.format(x3,y3).encode('utf-8'))
                resetSensorFlag()


            if(isSound1Detect and isSound2Detect and isSound3Detect):
                if DEMO:
                    socketClient.send('{},{}'.format(window_width/2.0,window_height/2.0).encode('utf-8'))
                else:
                    '''
                    r1 += 1.0
                    r2 += 1.0
                    r3 += 1.0
                    '''
                    while not is_collision():
                        r1 += float(motionSensorVal[0])*MOTION_ALPHA
                        r2 += float(motionSensorVal[1])*MOTION_ALPHA
                        r3 += float(motionSensorVal[2])*MOTION_ALPHA
                    #if is_collision():
                    print(position)
                    resetSensorFlag()
                    socketClient.send('{},{}'.format(window_width/2.0,window_height/2.0).encode('utf-8'))
                    #socketClient.send('400'.encode('utf-8'))

            elif(isSound1Detect and isSound2Detect):
                socketClient.send('200,200'.encode('utf-8'))
                resetSensorFlag()
            elif(isSound1Detect and isSound3Detect):
                socketClient.send('700,1000'.encode('utf-8'))
                resetSensorFlag()
            elif(isSound2Detect and isSound3Detect):
                socketClient.send('1000,200'.encode('utf-8'))
                resetSensorFlag()
            elif(isSound1Detect):
                socketClient.send('{},{}'.format(x1,y1).encode('utf-8'))
                resetSensorFlag()
            elif(isSound2Detect):
                socketClient.send('{},{}'.format(x2,y2).encode('utf-8'))
                resetSensorFlag()
            elif(isSound3Detect):
                socketClient.send('{},{}'.format(x3,y3).encode('utf-8'))
                resetSensorFlag()

            time.sleep(5)
    except (Exception, KeyboardInterrupt):
        traceback.print_exc()
        observer.stop()
    observer.join()

if __name__ == '__main__':
    main()
