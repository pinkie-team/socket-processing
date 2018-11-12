#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import os,csv,time
import math
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import traceback

DEMO = False

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
'''
x1, x2, x3 = 516.8, 1064.0, 1611.2
y1, y2, y3 = 278.8, 574.0, 869.2
'''

window_width = 1824
window_height = 984
margin_w = window_width * 0.3;
margin_h = window_height * 0.3;

'''
x1, x2, x3 = 364.8, 912.0, 1459.2
y1, y2, y3 = 196.8, 492.0, 787.2
'''
x1, y1 = window_width / 2 - margin_w, window_height / 2 + margin_h
x2, y2 = window_width / 2, window_height / 2 - margin_h
x3, y3 = window_width / 2 + margin_w, window_height / 2 + margin_h
AREA_UPLEFT = [window_width/2-margin_w, window_height/2-margin_h]
AREA_UPRIGHT = [window_width/2+margin_w, window_height/2-margin_h]
AREA_DOWNCENTER = [window_width/2, window_height/2+margin_h]


r1, r2, r3 = 1.0, 1.0, 1.0
MOTION_ALPHA = 0.1
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

    results = {
        'x12a': 0.0, 'y12a': 0.0, 'x12b': 0.0, 'y12b': 0.0,
        'x13a': 0.0, 'y13a': 0.0, 'x13b': 0.0, 'y13b': 0.0,
        'x23a': 0.0, 'y23a': 0.0, 'x23b': 0.0, 'y23b': 0.0
    }

    try:
        l12 = math.sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2))
        theta12a = math.atan2(y2 - y1, x2 - x1)
        theta12b = math.acos((pow(l12, 2) + pow(r1, 2) - pow(r2, 2)) / (2 * l12 * r1))

        # 円1,2の交点
        x12a = x1 + r1 * math.cos(theta12a + theta12b)
        y12a = y1 + r1 * math.sin(theta12a + theta12b)
        x12b = x1 + r1 * math.cos(theta12a - theta12b)
        y12b = y1 + r1 * math.sin(theta12a - theta12b)

        results['x12a'] = x12a
        results['y12a'] = y12a
        results['x12b'] = x12b
        results['y12b'] = y12b
    except ValueError:
        pass

    try:
        l23 = math.sqrt(pow(x3 - x2, 2) + pow(y3 - y2, 2))
        theta23a = math.atan2(y3 - y2, x3 - x2)
        theta23b = math.acos((pow(l23, 2) + pow(r2, 2) - pow(r3, 2)) / (2 * l23 * r2))

        # 円2,3の交点
        x23a = x2 + r2 * math.cos(theta23a + theta23b)
        y23a = y2 + r2 * math.sin(theta23a + theta23b)
        x23b = x2 + r2 * math.cos(theta23a - theta23b)
        y23b = y2 + r2 * math.sin(theta23a - theta23b)

        results['x23a'] = x23a
        results['y23a'] = y23a
        results['x23b'] = x23b
        results['y23b'] = y23b
    except ValueError:
        pass

    try:
        l13 = math.sqrt(pow(x3 - x1, 2) + pow(y3 - y1, 2))
        theta13a = math.atan2(y3 - y1, x3 - x1)
        theta13b = math.acos((pow(l13, 2) + pow(r1, 2) - pow(r3, 2)) / (2 * l13 * r1))

        # 円1,3の交点
        x13a = x1 + r1 * math.cos(theta13a + theta13b)
        y13a = y1 + r1 * math.sin(theta13a + theta13b)
        x13b = x1 + r1 * math.cos(theta13a - theta13b)
        y13b = y1 + r1 * math.sin(theta13a - theta13b)

        results['x13a'] = x13a
        results['y13a'] = y13a
        results['x13b'] = x13b
        results['y13b'] = y13b
    except ValueError:
        pass

    return results


def is_collision():
    global position
    kouten = calc_kouten()

    dx12a = abs(kouten['x12a'] - x3)
    dy12a = abs(kouten['y12a'] - y3)
    dx12b = abs(kouten['x12b'] - x3)
    dy12b = abs(kouten['y12b'] - y3)

    dx13a = abs(kouten['x13a'] - x2)
    dy13a = abs(kouten['y13a'] - y2)
    dx13b = abs(kouten['x13b'] - x2)
    dy13b = abs(kouten['y13b'] - y2)

    dx23a = abs(kouten['x23a'] - x1)
    dy23a = abs(kouten['y23a'] - y1)
    dx23b = abs(kouten['x23b'] - x1)
    dy23b = abs(kouten['y23b'] - y1)

    # 円1,2の交点aが円3の半径内にあるかどうか
    if math.sqrt(pow(dx12a, 2) + pow(dy12a, 2)) <= r3 and kouten['x12a'] != 0 and kouten['y12a'] != 0:
        position[0] = kouten['x12a']
        position[1] = kouten['y12a']
        print('************************')
        print('1,2 A: {} {}'.format(kouten['x12a'], kouten['y12a']))
        print('************************')
        return True

    # 円1,2の交点bが円3の半径内にあるかどうか
    if math.sqrt(pow(dx12b, 2) + pow(dy12b, 2)) <= r3 and kouten['x12b'] != 0 and kouten['y12b'] != 0:
        position[0] = kouten['x12b']
        position[1] = kouten['y12b']
        print('************************')
        print('1,2 B: {} {}'.format(kouten['x12b'], kouten['y12b']))
        print('************************')
        return True

    # 円1,3の交点aが円2の半径内にあるかどうか
    if math.sqrt(pow(dx13a, 2) + pow(dy13a, 2)) <= r2 and kouten['x13a'] != 0 and kouten['y13a'] != 0:
        position[0] = kouten['x13a']
        position[1] = kouten['y13a']
        print('************************')
        print('1,3 A: {} {}'.format(kouten['x13a'], kouten['y13a']))
        print('************************')
        return True

    # 円1,3の交点bが円2の半径内にあるかどうか
    if math.sqrt(pow(dx13b, 2) + pow(dy13b, 2)) <= r2 and kouten['x13b'] != 0 and kouten['y13b'] != 0:
        position[0] = kouten['x13b']
        position[1] = kouten['y13b']
        print('************************')
        print('1,3 B: {} {}'.format(kouten['x13b'], kouten['y13b']))
        print('************************')
        return True

    # 円2,3の交点aが円1の半径内にあるかどうか
    if math.sqrt(pow(dx23a, 2) + pow(dy23a, 2)) <= r1 and kouten['x23a'] != 0 and kouten['y23a'] != 0:
        position[0] = kouten['x23a']
        position[1] = kouten['y23a']
        print('************************')
        print('2,3 A: {} {}'.format(kouten['x23a'], kouten['y23a']))
        print('************************')
        return True

    # 円2,3の交点bが円1の半径内にあるかどうか
    if math.sqrt(pow(dx23b, 2) + pow(dy23b, 2)) <= r1 and kouten['x23b'] != 0 and kouten['y23b'] != 0:
        position[0] = kouten['x23b']
        position[1] = kouten['y23b']
        print('************************')
        print('2,3 B: {} {}'.format(kouten['x23b'], kouten['y23b']))
        print('************************')
        return True

    return False

def get_remove_interger_zero_count(decimal_values):
    """
    与えられた数値の整数部に0があるパターンを除去するには何倍すれば良いかを求める
    :param decimal_values:  センサー値
    :type   list
    :return:    何倍すれば全ての数値から0.111といった整数部が0のパターンを除去できるか
    :rtype: int
    """
    count = 0

    for decimal_value in decimal_values:
        tmp_count = 0
        integer = math.modf(decimal_value)[1]

        while integer == 0:
            decimal_value *= 10
            integer = math.modf(decimal_value)[1]
            tmp_count += 1

        if count < tmp_count:
            count = tmp_count

    return count

def resetSensorFlag():
    global isMotion1Detect,isMotion2Detect,isMotion3Detect
    global isSound1Detect,isSound2Detect,isSound3Detect
    global motionSensorVal,soundSensorVal
    global r1,r2,r3
    global position

    print(position)

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
    global motionSensorVal,soundSensorVal

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
                        r1 += MOTION_ALPHA / float(motionSensorVal[0])
                        r2 += MOTION_ALPHA / float(motionSensorVal[1])
                        r3 += MOTION_ALPHA / float(motionSensorVal[2])
                    #if is_collision():
                    print(position)
                    socketClient.send('{},{}'.format(position[0],position[1]).encode('utf-8'))
                    resetSensorFlag()

            elif(isMotion1Detect and isMotion2Detect):
                position = AREA_UPLEFT
                socketClient.send('{},{}'.format(position[0],position[1]).encode('utf-8'))
                resetSensorFlag()
            elif(isMotion1Detect and isMotion3Detect):
                position = AREA_DOWNCENTER
                socketClient.send('{},{}'.format(position[0],position[1]).encode('utf-8'))
                resetSensorFlag()
            elif(isMotion2Detect and isMotion3Detect):
                position = AREA_UPRIGHT
                socketClient.send('{},{}'.format(position[0],position[1]).encode('utf-8'))
                resetSensorFlag()
            elif(isMotion1Detect):
                position[0] = x1
                position[1] = y1
                socketClient.send('{},{}'.format(position[0],position[1]).encode('utf-8'))
                resetSensorFlag()
            elif(isMotion2Detect):
                position[0] = x2
                position[1] = y2
                socketClient.send('{},{}'.format(position[0],position[1]).encode('utf-8'))
                resetSensorFlag()
            elif(isMotion3Detect):
                position[0] = x3
                position[1] = y3
                socketClient.send('{},{}'.format(position[0],position[1]).encode('utf-8'))
                resetSensorFlag()


            if(isSound1Detect and isSound2Detect and isSound3Detect):
                if DEMO:
                    socketClient.send('{},{}'.format(window_width/2.0,window_height/2.0).encode('utf-8'))
                else:
                    max_count = get_remove_interger_zero_count([abs(float(soundSensorVal[0])), abs(float(soundSensorVal[1])), abs(float(soundSensorVal[2]))])
                    value1, value2, value3 = abs(float(soundSensorVal[0]))*pow(10, max_count), abs(float(soundSensorVal[1]))*pow(10, max_count), abs(float(soundSensorVal[2]))*pow(10, max_count)
                    print(value1)
                    min_value = min(value1, value2, value3)
                    loop_count = 0

                    while not is_collision():
                        loop_count += 1

                        if loop_count >= 300000:
                            print('**********************')
                            print('many loop')
                            print('**********************')
                            position[0] = window_width/2.0
                            position[1] = window_height/2.0
                            break

                        '''
                        r1 += float(soundSensorVal[0]) * SOUND_ALPHA
                        r2 += float(soundSensorVal[1]) * SOUND_ALPHA
                        r3 += float(soundSensorVal[2]) * SOUND_ALPHA
                        '''
                        r1 += value1 / min_value
                        r2 += value2 / min_value
                        r3 += value3 / min_value

                    print(position)
                    print(loop_count)
                    socketClient.send('{},{}'.format(position[0],position[1]).encode('utf-8'))
                    resetSensorFlag()

            elif(isSound1Detect and isSound2Detect):
                position = AREA_UPLEFT
                socketClient.send('{},{}'.format(position[0],position[1]).encode('utf-8'))
                resetSensorFlag()
            elif(isSound1Detect and isSound3Detect):
                position = AREA_DOWNCENTER
                socketClient.send('{},{}'.format(position[0],position[1]).encode('utf-8'))
                resetSensorFlag()
            elif(isSound2Detect and isSound3Detect):
                position = AREA_UPRIGHT
                socketClient.send('{},{}'.format(position[0],position[1]).encode('utf-8'))
                resetSensorFlag()
            elif(isSound1Detect):
                position[0] = x1
                position[1] = y1
                socketClient.send('{},{}'.format(position[0],position[1]).encode('utf-8'))
                resetSensorFlag()
            elif(isSound2Detect):
                position[0] = x2
                position[1] = y2
                socketClient.send('{},{}'.format(position[0],position[1]).encode('utf-8'))
                resetSensorFlag()
            elif(isSound3Detect):
                position[0] = x3
                position[1] = y3
                socketClient.send('{},{}'.format(position[0],position[1]).encode('utf-8'))
                resetSensorFlag()

            time.sleep(20)
    except (Exception, KeyboardInterrupt):
        traceback.print_exc()
        observer.stop()
    observer.join()

if __name__ == '__main__':
    main()
