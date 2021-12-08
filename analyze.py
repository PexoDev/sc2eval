from logging import error
from pathlib import Path
import json 

from zephyrus_sc2_parser.game import player
import Zephyrus.parser as zp

class Player:
    def __init__(self, name, race, matchInfo, matchInfoFrameIndex, timeline, timelineFrameIndex, id):
        self.name = name

        self.race = race
        self.apm = matchInfo["apm"][id]
        self.spm = matchInfo["spm"][id]
        self.sq = matchInfo["sq"][id]
        self.mmr = matchInfo["mmr"][id]

        self.avgMineralsColletionRate = matchInfo["avg_resource_collection_rate"]["minerals"][id]
        self.avgGasColletionRate = matchInfo["avg_resource_collection_rate"]["gas"][id]
        self.maxCollectionRate = matchInfo["max_collection_rate"][id]
        
        self.avgUnspentMinerals = matchInfo["avg_unspent_resources"]["minerals"][id]
        self.avgUnspentGas = matchInfo["avg_unspent_resources"]["gas"][id]

        self.mineralsLost = matchInfo["resources_lost"]["minerals"][id]
        self.gasLost = matchInfo["resources_lost"]["gas"][id]

        self.mineralsCollected = matchInfo["resources_collected"]["minerals"][id]
        self.gasCollected = matchInfo["resources_collected"]["gas"][id]

        self.workersProduced = matchInfo["workers_produced"][id]
        self.workersKilled = matchInfo["workers_killed"][id]
        self.workersLost = matchInfo["workers_lost"][id]

        self.supply = timeline[timelineFrameIndex][id]["supply"]
        self.maxSupply = timeline[timelineFrameIndex][id]["supply_cap"]
        self.supplyBlockTime = matchInfo["supply_block"][id]
        
        self.upgrades = timeline[timelineFrameIndex][id]["upgrade"]
        self.armyValueMinerals = timeline[timelineFrameIndex][id]["army_value"]["minerals"]
        self.armyValueGas = timeline[timelineFrameIndex][id]["army_value"]["gas"]

        if self.mmr is None or type(self.mmr) != int:
                self.mmr = 0

class ReplayData:
    def __init__(self,mmrDiff, apmDiff, sqDiff, supplyDiff, resourcesLostDiff):
        self.mmrDifference = mmrDiff
        self.apmDifference = apmDiff
        self.sqDifference = sqDiff
        self.supplyBlockDifference = supplyDiff
        self.resourcesLostDifference = resourcesLostDiff

class ReplayDataPoint:
    def __init__(self, player1Data, player2Data):
        self.player1Data = player1Data
        self.player2Data = player2Data

replaysFolder = "M:/Uni/sc2eval/Replays"

def ProcessReplay(replayPath):
    data = zp.parse_replay(replaysFolder+"/"+replayPath, local=True)

    players = data[0]
    timeline = data[1]
    matchInfo = data[3]
    matchMetaData = data[4]

    winnerID = matchMetaData["winner"]
    if winnerID == 1:
        loserID =  2 
    else:
        loserID = 1

    winnerData = players[winnerID]
    loserData = players[loserID]

    winner = Player(winnerData.name, winnerData.race, matchInfo, winnerID)
    loser = Player(loserData.name, loserData.race, matchInfo, loserID)

    #winningBuildOrder = winner.objects
    #losingBuildOrder = loser.objects

    winningMMRDiff = winner.mmr - loser.mmr
    winningAverageAPMDiff = winner.apm - loser.apm
    winningSQDiff = winner.sq - loser.sq
    winningSupplyBlockDiff = winner.supplyBlockTime - loser.supplyBlockTime
    winningResourcesLostDiff = (winner.gasLost + winner.mineralsLost) - (loser.mineralsLost + loser.gasLost)
       
    return ReplayData(winningMMRDiff, winningAverageAPMDiff, winningSQDiff, winningSupplyBlockDiff, winningResourcesLostDiff)

replays = ["1.SC2Replay","2.SC2Replay","3.SC2Replay","4.SC2Replay","5.SC2Replay","6.SC2Replay","10.SC2Replay","11.SC2Replay","12.SC2Replay"]
replaysData = []
for replay in replays:
    try:
        replaysData.append(ProcessReplay(replay))

    except Exception as e:
        print("Couldn't decode " + replay)

print(replaysData)