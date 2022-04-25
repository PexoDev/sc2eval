import time
import numpy as np
import ReplaysParser 
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense, LSTM, Masking
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras import losses

averageReplayLength = 145
modelNumberOfFeatures = 322

def MyAccuracy(predictions, realResults):
    acc = 0
    allResults = 0
    for index in range(len(predictions)):
        allResults = allResults + len(predictions[index])
        for innerIndex in range(len(predictions[index])):
            if(predictions[index][innerIndex] == realResults[index][innerIndex]):
                acc = acc + 1
    return acc/allResults

def PrepareInputData(reps, amountOfReplays, theLongestReplayLength, numberOfFeatures):
    winnerIDs = []

    for rep in range(len(reps)):
        winnerIDs.append(reps[rep][0][-1])

    xMatrix = np.ones([amountOfReplays, theLongestReplayLength, numberOfFeatures])*-1
    yMatrix = np.zeros([amountOfReplays,theLongestReplayLength])

    for repIndex in range(len(reps)):
        for dataPointIndex in range(len(yMatrix[repIndex])):
            yMatrix[repIndex,int(dataPointIndex)] = winnerIDs[repIndex]

        for dataPointIndex in range(min(len(reps[repIndex]), theLongestReplayLength)):
            for dataValueIndex in range (len(xMatrix[repIndex,int(dataPointIndex)])):
                if(xMatrix[repIndex,int(dataPointIndex),int(dataValueIndex)] < 0):
                    xMatrix[repIndex,int(dataPointIndex),int(dataValueIndex)] = 0

            xMatrix[repIndex,int(dataPointIndex),:] = reps[repIndex][dataPointIndex][:-1]

    return xMatrix, yMatrix

def PrepareAndNormalizeInputData(reps, amountOfReplays, theLongestReplayLength, numberOfFeatures):
    maxValues = []
    winnerIDs = []

    for rep in range(len(reps)):
        winnerIDs.append(reps[rep][0][-1])

    for i in range(numberOfFeatures):
         maxValues.append(FindBiggestValue(reps,i))

    for rep in range(len(reps)):
         for dataPoint in reps[rep]:
             for i in range(numberOfFeatures):
                 if(maxValues[i] == 0): 
                     continue
                 dataPoint[i] = dataPoint[i]/maxValues[i]

    xMatrix = np.ones([amountOfReplays, theLongestReplayLength, numberOfFeatures])*-1
    yMatrix = np.zeros([amountOfReplays,theLongestReplayLength])

    for repIndex in range(len(reps)):
        for dataPointIndex in range(len(yMatrix[repIndex])):
            yMatrix[repIndex,int(dataPointIndex)] = winnerIDs[repIndex]

        for dataPointIndex in range(min(len(reps[repIndex]), theLongestReplayLength)):
            for dataValueIndex in range (len(xMatrix[repIndex,int(dataPointIndex)])):
                if(xMatrix[repIndex,int(dataPointIndex),int(dataValueIndex)] < 0):
                    xMatrix[repIndex,int(dataPointIndex),int(dataValueIndex)] = 0

            xMatrix[repIndex,int(dataPointIndex),:] = reps[repIndex][dataPointIndex][:-1]

    return xMatrix, yMatrix


def FindBiggestValue(Array, Index):
    max = 0
    for replay in Array:
        for dataPoint in replay:
            if(dataPoint[Index] > max):
                max = dataPoint[Index]
    return max

def FindLongestReplay(reps):
    max = 0
    for rep in range(len(reps)):
        if(len(reps[rep])>max):
            max  = len(reps[rep])  
    return max
    
def FindAverageReplayLength(reps):
    sum = 0
    for rep in range(len(reps)):
        sum = sum + len(reps[rep])
    return sum/len(reps)

def TrainLSTM(vectorizedReplayData, existingModel):
    theLongestReplayLength = min(FindLongestReplay(vectorizedReplayData), 500)
    amountOfReplays = len(vectorizedReplayData)
    xMatrix, yMatrix = PrepareInputData(vectorizedReplayData, amountOfReplays, theLongestReplayLength, modelNumberOfFeatures)
    
    if(existingModel is not None):
        model = existingModel
    else:
        model = InitializeLSTMModel()

    X_train, X_test, y_train, y_test = train_test_split(xMatrix, yMatrix, test_size=0.2, random_state=42)
    y_train = to_categorical(y_train)
    y_test = to_categorical(y_test)

    es = EarlyStopping(monitor='val_loss', mode='min', patience=10, min_delta=0.001, verbose=1, restore_best_weights = True)

    result = model.fit(X_train, y_train, batch_size=32, epochs=100, validation_split = 0.1, callbacks=[es])
    print("Model Loss")
    print(result.history['loss'])
    print("Validation Loss")
    print(result.history['val_loss'])

    predictions = model.predict(X_test)
    finalPredictions = predictions.argmax(axis=2)
    realResults = y_test.argmax(axis=2)
    
    print("Done Training | Accuarcy: " + str(MyAccuracy(finalPredictions, realResults)))
    return (model, MyAccuracy(finalPredictions, realResults))

def IterateTraining(batchSize, maxReplaysToUse, modelNamePrefix):
    startTime = time.time()
    vectorizedReplayData = ReplaysParser.LoadVectorizedData(batchSize, 0)
    #vectorizedReplayData = ReplaysParser.ExtractBasicAndArmyData(vectorizedReplayData)

    (LSTMmodel, acc) = TrainLSTM(vectorizedReplayData, None)
    Accuracies = [acc]

    for i in range (1, int(maxReplaysToUse/batchSize)-1 ):
        vectorizedReplayData = ReplaysParser.LoadVectorizedData(batchSize, batchSize*i)
        #vectorizedReplayData = ReplaysParser.ExtractBasicAndArmyData(vectorizedReplayData)
        try:
            (LSTMmodel, acc) = TrainLSTM(vectorizedReplayData, LSTMmodel)
        except Exception as e:
            print(e)

        Accuracies.append(acc)

    LSTMmodel.save_weights(modelNamePrefix+str(maxReplaysToUse)+".weights")
    print(Accuracies)
    print("Training time: " + str(time.time() - startTime))

def UseTrainedLSTMModel(weightsPath):
    model = InitializeLSTMModel()
    model.load_weights(weightsPath)
    return model

def InitializeLSTMModel():
    # lossMethod = losses.BinaryCrossentropy(
    #         from_logits=False,
    #         label_smoothing=0.0,
    #         axis=-1,
    #         reduction="auto",
    #         name="binary_crossentropy",
    #         )

    model = Sequential()
    model.add(Masking(mask_value=-1.0, input_shape=(None, modelNumberOfFeatures)))
    model.add(LSTM(1024, input_shape=(None,  modelNumberOfFeatures), return_sequences = True, dropout = 0.2))
    model.add(LSTM(512, input_shape=(None, 1024), return_sequences = True))
    model.add(Dense(2, activation='softmax'))
    model.compile(loss="binary_crossentropy", optimizer='adam', metrics=["accuracy"])
    return model

#IterateTraining(512,15000, "lstm_various-match-length_not-normalized_all-features_")