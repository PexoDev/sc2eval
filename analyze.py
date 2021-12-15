import os
import jsonpickle
import Zephyrus.parser as zp

from zephyrus_sc2_parser.game import player
from player import Player
from replayDataPoint import ReplayDataPoint

ReplaysFolder = "M:/Uni/sc2eval/Replays"
SerializedDataFolder = "M:/Uni/sc2eval/SerializedData"

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
    filename = replayName+".data"
    with open(SerializedDataFolder + "/" + filename, "w") as file:
        serializedData = jsonpickle.encode(replayData)
        file.write(serializedData)
    print("Saved replay data to file "+filename)

def AnalyzeReplays():
    i = 0
    for filename in os.listdir(ReplaysFolder):
        if("Alpha" in filename): continue

        try:
            SerializeData(ProcessReplay(ReplaysFolder+"/"+filename), filename)
        except Exception as e:
            print("Couldn't decode " + filename)
            print(e)
            continue

        i += 1
        if i > 10: 
            return

def LoadReplays():
    replayData = {}
    i = 0

    for filename in os.listdir(SerializedDataFolder):
        with open(SerializedDataFolder + "/" + filename, "r") as file:
            replayData[i] = jsonpickle.decode(file.read())
            i += 1
            
    return replayData

#AnalyzeReplays()
replays = LoadReplays()
replays[0]['0'].Vectorize()
#print(replays)