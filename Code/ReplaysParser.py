from math import ceil
import os
import json
import shutil
import threading
import zephyrus_sc2_parser.parser as zp

from replayDataPoint import ReplayDataPoint
from zephyrus_sc2_parser.game import player
from player import Player

ReplaysFolder = "Replays/RawReplays"
CorruptedReplaysFolder = "Replays/CorruptedReplays"
TooShortReplaysFolder = "Replays/TooShortReplays"
SerializedDataFolder = "SerializedReplays"

CorruptedReplays = []
TooShortReplays = []

def ProcessReplay(replayPath):
    data = zp.parse_replay(replayPath, local=True, network=False)

    players = data[0]
    timeline = data[1]
    matchInfo = data[3]
    matchMetaData = data[4]

    winnerID = int(matchMetaData["winner"])

    dataPoints = {}
    i = 0
    while (i < len(timeline)):
        p1 = Player(players[1].name, players[1].race, matchInfo, timeline, i, 1)
        p2 = Player(players[2].name, players[2].race, matchInfo, timeline, i, 2)
        dataPoints[i] = ReplayDataPoint(p1,p2, int(winnerID-1))
        i += 1

    return dataPoints

def AnalyzeReplays(startIndex, count):
    ReplaysScaned = os.listdir(SerializedDataFolder)
    CorruptedReplays = []
    TooShortReplays = []
    for index in range(len(ReplaysScaned)):
        ReplaysScaned[index] = ReplaysScaned[index].removesuffix("_vectorized.jsonData")
    allFiles = [item for item in os.listdir(ReplaysFolder) if item not in ReplaysScaned]
    for fileIndex in range(startIndex, min(startIndex + count, len(allFiles))):
        filename = allFiles[fileIndex]
        try:
            processedReplay = ProcessReplay(ReplaysFolder+"/"+filename)
            if(len(processedReplay) < 33):
                print("Moving " + filename + " to too short replays folder")
                TooShortReplays.append(filename)
            else:
                VectorizeAndSaveReplay(processedReplay, filename)
        except Exception as e:
            print("Couldn't decode " + filename + " | Moving it to corrupted folder")
            CorruptedReplays.append(filename)
            print(e)
            continue

    for index in range(len(CorruptedReplays)):
        shutil.move(ReplaysFolder+"/"+CorruptedReplays[index],CorruptedReplaysFolder+"/"+CorruptedReplays[index])
    for index in range(len(TooShortReplays)):
        shutil.move(ReplaysFolder+"/"+TooShortReplays[index],TooShortReplaysFolder+"/"+TooShortReplays[index])

def LoadVectorizedData(count, startIndex, path = None):
    if(path is None):
        path = SerializedDataFolder

    i = 0
    vectorizedData = []
    allReplays = os.listdir(path)

    allReplays = sorted(allReplays, key =  lambda x: os.stat(path+"/"+x).st_size)
    
    for fileIndex in range(startIndex, min(startIndex+count,len(allReplays))):
        filename = allReplays[fileIndex]
        if(not filename.__contains__("_vectorized.jsonData")): continue
        with open(path + "/" + filename, "r") as file:
            rep =  json.loads(file.read())
            if(len(rep) >= 33):
                vectorizedData.append(rep)
        i += 1
        if(i%10 == 0):
            print("Loaded "+str(i)+"/"+str(len(allReplays)),end='\r')
        if(i >= count):
            return vectorizedData
    return vectorizedData

def LoadVectorizedReplay(path):
    with open(path, "r") as file:
        rep =  json.loads(file.read())
        return rep

# Extracts 42 basic features 
def ExtractBasicDataOnly(vectorizedData):
    basicData = []

    for replayIndex in range(len(vectorizedData)):
        basicReplay = []
        for dataPointIndex in range(len(vectorizedData[replayIndex])):
            basicDataPoint = []
            basicDataPoint.extend(vectorizedData[replayIndex][dataPointIndex][0:21]) #player1 data
            basicDataPoint.extend(vectorizedData[replayIndex][dataPointIndex][161:182]) #player2 data
            basicDataPoint.append(vectorizedData[replayIndex][dataPointIndex][-1]) #winnerID
            basicReplay.append(basicDataPoint)
        basicData.append(basicReplay)

    return basicData

# Extracts 142 features: basic + army
def ExtractBasicAndArmyData(vectorizedData):
    basicData = []

    for replayIndex in range(len(vectorizedData)):
        basicReplay = []
        for dataPointIndex in range(len(vectorizedData[replayIndex])):
            basicDataPoint = []
            basicDataPoint.extend(vectorizedData[replayIndex][dataPointIndex][0:71]) #player1 data
            basicDataPoint.extend(vectorizedData[replayIndex][dataPointIndex][161:232]) #player2 data
            basicDataPoint.append(vectorizedData[replayIndex][dataPointIndex][-1]) #winnerID
            basicReplay.append(basicDataPoint)
        basicData.append(basicReplay)

    return basicData

def VectorizeAndSaveReplay(replayData, replayName):
    vectorized = []
    i = 0
    while (i < len(replayData)):
        vectorized.append(replayData[i].Vectorize())
        i += 1
    SaveSerializedDataToFile(vectorized, replayName+"_vectorized")

def SaveSerializedDataToFile(replayData, replayName):
    filename = replayName+".jsonData"
    with open(SerializedDataFolder + "/" + filename, "w") as file:
        serializedData = json.dumps(replayData)
        file.write(serializedData)


def ProcessReplays(threadsCount = 8):
    allReplays = len(os.listdir(ReplaysFolder))
    r = ceil(allReplays/(threadsCount*100))
    for i in range(r):
        threads = []
        for threadIndex in range(threadsCount):
            thread = threading.Thread(target=AnalyzeReplays, args=(threadIndex*100, 100))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

        print("Processed "+str(i*threadsCount*100)+"/"+str(allReplays))