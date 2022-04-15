import TrainModels 
import ReplaysParser 
import matplotlib.pyplot as plt

lstmWeightsPath = "M:/Uni/sc2eval/TrainedModels/lstm_290-match-length_30k.weights"

lstm = TrainModels.UseTrainedLSTMModel(lstmWeightsPath)
vectorizedReplayData = ReplaysParser.LoadVectorizedData(100, 31000)
normalizedData, expectedResults =  TrainModels.PrepareInputData(vectorizedReplayData, 100, 290, 324)

predictions = lstm.predict(normalizedData)
finalPredictions = predictions.argmax(axis=2)

accuracy = TrainModels.MyAccuracy(finalPredictions, expectedResults)

print(lstm)