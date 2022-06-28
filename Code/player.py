from buildingType import BuildingType
from unitType import UnitType
from upgradeType import UpgradeType


class Player:
    def __init__(self, name, race, matchInfo, timeline, timelineFrameIndex, id):
        self.name = name

        self.race = race
        self.mmr = matchInfo["mmr"][id] < 0 if 0 else matchInfo["mmr"][id]
        self.apm = matchInfo["apm"][id] < 0 if 0 else matchInfo["apm"][id]
        self.sq = matchInfo["sq"][id] < 0 if 0 else matchInfo["sq"][id]

        self.spm = timeline[timelineFrameIndex][id]["spm"] < 0 if 0 else matchInfo["spm"][id]

        self.mineralsColletionRate = timeline[timelineFrameIndex][id]["resource_collection_rate"]["minerals"]
        self.gasColletionRate = timeline[timelineFrameIndex][id]["resource_collection_rate"]["gas"]
        self.unspentMinerals = timeline[timelineFrameIndex][id]["unspent_resources"]["minerals"]
        self.unspentGas = timeline[timelineFrameIndex][id]["unspent_resources"]["gas"]
        self.mineralsLost = timeline[timelineFrameIndex][id]["resources_lost"]["minerals"]
        self.gasLost = timeline[timelineFrameIndex][id]["resources_lost"]["gas"]
        self.mineralsCollected = timeline[timelineFrameIndex][id]["resources_collected"]["minerals"]
        self.gasCollected = timeline[timelineFrameIndex][id]["resources_collected"]["gas"]
        self.workersProduced = timeline[timelineFrameIndex][id]["workers_produced"]
        self.workersKilled = timeline[timelineFrameIndex][id]["workers_killed"]
        self.workersLost = timeline[timelineFrameIndex][id]["workers_lost"]

        self.supply = timeline[timelineFrameIndex][id]["supply"]
        self.maxSupply = timeline[timelineFrameIndex][id]["supply_cap"]
        self.supplyBlockTime = matchInfo["supply_block"][id]
        
        self.armyValueMinerals = timeline[timelineFrameIndex][id]["army_value"]["minerals"]
        self.armyValueGas = timeline[timelineFrameIndex][id]["army_value"]["gas"]

        self.armyComposition = {}
        self.buildings = {}
        self.upgrades = {}

        for type in UnitType:
            self.armyComposition[type.name] = 0
            if(type.name in timeline[timelineFrameIndex][id]['unit']):
                self.armyComposition[type.name] = timeline[timelineFrameIndex][id]['unit'][type.name]['live']
        
        for type in BuildingType:
            self.buildings[type.name] = 0
            if(type.name in timeline[timelineFrameIndex][id]['building']):
                self.buildings[type.name] = timeline[timelineFrameIndex][id]['building'][type.name]['live']

        for type in UpgradeType:
            if (type.name in timeline[timelineFrameIndex][id]["upgrade"]): 
                self.upgrades[type.name] = 1
            else:
                self.upgrades[type.name] = 0

        if self.mmr is None or not isinstance(self.mmr,int):
                self.mmr = 0


    def Vectorize(self):
        resultVector = []

        if(self.race == "Terran"):
            resultVector.append(int(0))
        elif(self.race == "Protoss"):
            resultVector.append(int(1))
        else:
            resultVector.append(int(2))

        resultVector.append(int(self.apm))
        resultVector.append(int(self.spm))
        resultVector.append(int(self.sq))
        resultVector.append(int(self.mmr))
        resultVector.append(int(self.mineralsColletionRate))
        resultVector.append(int(self.gasColletionRate))
        resultVector.append(int(self.unspentMinerals))
        resultVector.append(int(self.unspentGas))
        resultVector.append(int(self.mineralsLost))
        resultVector.append(int(self.gasLost))
        resultVector.append(int(self.mineralsCollected))
        resultVector.append(int(self.gasCollected))
        resultVector.append(int(self.workersProduced))
        resultVector.append(int(self.workersKilled))
        resultVector.append(int(self.workersLost))
        resultVector.append(int(self.supply))
        resultVector.append(int(self.maxSupply))
        resultVector.append(int(self.supplyBlockTime))
        resultVector.append(int(self.armyValueMinerals))
        resultVector.append(int(self.armyValueGas))

        for key in self.armyComposition:
            resultVector.append(int(self.armyComposition[key]))
        for key in self.buildings:
            resultVector.append(int(self.buildings[key]))
        for key in self.upgrades:
            resultVector.append(int(self.upgrades[key]))

        return resultVector