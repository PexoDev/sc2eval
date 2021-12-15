from buildingType import BuildingType
from unitType import UnitType
from upgradeType import UpgradeType


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
        resultVector.append(int(self.avgMineralsColletionRate))
        resultVector.append(int(self.avgGasColletionRate))
        resultVector.append(int(self.maxCollectionRate))
        resultVector.append(int(self.avgUnspentMinerals))
        resultVector.append(int(self.avgUnspentGas))
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