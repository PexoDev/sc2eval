from zephyrus_sc2_parser.game import player
from player import Player
from replayDataPoint import ReplayDataPoint

import os
import json
import Zephyrus.parser as zp
import numpy as np
import sklearn as skl
import shutil

ReplaysFolder = "M:/Uni/sc2eval/Replays/RawReplays"
CorruptedReplaysFolder = "M:/Uni/sc2eval/CorruptedReplays"
TooShortReplaysFolder = "M:/Uni/sc2eval/TooShortReplays"
SerializedDataFolder = "M:/Uni/sc2eval/SerializedData"

CorruptedReplays = []
TooShortReplays = []

def ProcessReplay(replayPath):
    data = zp.parse_replay(replayPath, local=True)

    players = data[0]
    timeline = data[1]
    matchInfo = data[3]
    matchMetaData = data[4]

    winnerID = int(matchMetaData["winner"])

    dataPoints = {}
    i = 0
    while (i < len(timeline)):
        p1 = Player(players[1].name, players[1].race, matchInfo, i, timeline, i, 1)
        p2 = Player(players[2].name, players[2].race, matchInfo, i, timeline, i, 2)
        dataPoints[i] = ReplayDataPoint(p1,p2, int(winnerID-1))
        i += 1

    return dataPoints

def SerializeData(replayData, replayName):
        filename = replayName+".jsonData"
        with open(SerializedDataFolder + "/" + filename, "w") as file:
            serializedData = json.dumps(replayData)
            file.write(serializedData)
        print("Saved replay data to file "+filename)
    

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
    
    print(CorruptedReplays)
    print(TooShortReplays)

    for index in range(len(CorruptedReplays)):
        shutil.move(ReplaysFolder+"/"+CorruptedReplays[index],CorruptedReplaysFolder+"/"+CorruptedReplays[index])
    for index in range(len(TooShortReplays)):
        shutil.move(ReplaysFolder+"/"+TooShortReplays[index],TooShortReplaysFolder+"/"+TooShortReplays[index])

def LoadVectorizedData(count, startIndex):
    i = 0
    vectorizedData = []
    allReplays = os.listdir(SerializedDataFolder)
    for fileIndex in range(startIndex, min(startIndex+count,len(allReplays))):
        filename = allReplays[fileIndex]
        if(not filename.__contains__("_vectorized.jsonData")): continue
        with open(SerializedDataFolder + "/" + filename, "r") as file:
            rep =  json.loads(file.read())
            if(len(rep) >= 33):
                vectorizedData.append(rep)
        i += 1
        if(i%10 == 0):
            print("Loaded "+str(i)+"/"+str(len(allReplays)),end='\r')
        if(i >= count):
            return vectorizedData
    return vectorizedData

def VectorizeAndSaveReplay(replayData, replayName):
    vectorized = []
    i = 0
    while (i < len(replayData)):
        vectorized.append(replayData[i].Vectorize())
        i += 1
    SerializeData(vectorized, replayName+"_vectorized")