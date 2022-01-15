from keras.engine.data_adapter import train_validation_split
from sklearn.metrics import accuracy_score
from tensorflow.keras.utils import to_categorical
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from keras.models import Sequential
from keras.layers import Dense, LSTM, Masking
from sklearn.metrics import r2_score
from sklearn.linear_model import BayesianRidge, LinearRegression

import tensorflow as tf
import numpy as np
import analyze 
import matplotlib.pyplot as plt

def MyAccuracy(predictions, realResults):
    acc = 0
    allResults = 0
    for index in range(len(predictions)):
        allResults = allResults + len(predictions[index])
        for innerIndex in range(len(predictions[index])):
            if(predictions[index][innerIndex] == realResults[index][innerIndex]):
                acc = acc + 1
    return acc/allResults

def NormalizeInputAsSequences(reps, amountOfReplays, theLongestReplayLength, numberOfFeatures):
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

    for repIndex in range(len(reps)):
        for dataPointIndex in range(min(len(reps[repIndex]), theLongestReplayLength)):
            xMatrix[repIndex,int(dataPointIndex),:] = reps[repIndex][dataPointIndex][:-1]

    return xMatrix, yMatrix

def PrepareInputForBayesian(replays, amountOfReplays, theLongestReplayLength, numberOfFeatures):
    maxValues = []

    for i in range(numberOfFeatures):
        maxValues.append(FindBiggestValue(replays,i))

    for rep in range(len(replays)):
        for dataPoint in replays[rep]:
            for i in range(numberOfFeatures):
                if(maxValues[i] == 0): 
                    continue
                dataPoint[i] = dataPoint[i]/maxValues[i]

    xMatrix = np.ones([amountOfReplays * theLongestReplayLength, numberOfFeatures])*-1
    yMatrix = np.zeros([amountOfReplays * theLongestReplayLength])
    
    for repIndex in range(len(replays)):
        for sequencePoint in range(min(len(replays[repIndex]), theLongestReplayLength)):
            yMatrix[repIndex*theLongestReplayLength + sequencePoint] = replays[repIndex][sequencePoint][-1]

    for repIndex in range(len(replays)):
        for sequencePoint in range(min(len(replays[repIndex]), theLongestReplayLength)):
            xMatrix[repIndex*theLongestReplayLength + sequencePoint] = replays[repIndex][sequencePoint][:-1]

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
    amountOfReplays = len(vectorizedReplayData)
    #theLongestReplayLength = FindLongestReplay(vectorizedReplayData)
    averageReplayLength = 145
    numberOfFeatures = 324

    xMatrix, yMatrix = NormalizeInputAsSequences(vectorizedReplayData, amountOfReplays, averageReplayLength, numberOfFeatures)

    
    if(existingModel is not None):
        model = existingModel
    else:
        model = Sequential()
        model.add(Masking(mask_value=-1.0, input_shape=(averageReplayLength,numberOfFeatures)))
        model.add(LSTM(1024, input_shape=(averageReplayLength,numberOfFeatures), return_sequences=True, dropout = 0.2))
        model.add(LSTM(512, input_shape=(averageReplayLength,1024), return_sequences = True))
        model.add(Dense(2, activation='softmax'))
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=["acc"])

    X_train, X_test, y_train, y_test = train_test_split(xMatrix, yMatrix, test_size=0.2, random_state=42)
    y_train = to_categorical(y_train)
    y_test = to_categorical(y_test)

    result = model.fit(X_train, y_train, batch_size=512, epochs=50, validation_split = 0.1)
    print("Model Loss")
    print(result.history['loss'])
    print("Validation Loss")
    print(result.history['val_loss'])

    predictions = model.predict(X_test)
    finalPredictions = predictions.argmax(axis=2)
    realResults = y_test.argmax(axis=2)
    
    print("Done Training | Accuarcy: " + str(MyAccuracy(finalPredictions, realResults)))
    return model

def TrainBayesianNetwork(vectorizedReplayData, existingModel):
    amountOfReplays = len(vectorizedReplayData)
    averageReplayLength = 145
    numberOfFeatures = 324
    xMatrix, yMatrix = PrepareInputForBayesian(vectorizedReplayData, amountOfReplays, averageReplayLength, numberOfFeatures)
    X_train, X_test, y_train, y_test = train_test_split(xMatrix, yMatrix, test_size=0.2, random_state=42)
    
    if(existingModel is None):
        model = BayesianRidge(compute_score=True)
    else:
        model = existingModel

    model.fit(X_train, y_train)
    prediction = model.predict(X_test)
    print(f"r2 Score Of Test Set : {r2_score(y_test, prediction)}")
    return model

def TrainLinearRegression(vectorizedReplayData, existingModel):
    amountOfReplays = len(vectorizedReplayData)
    averageReplayLength = 145
    numberOfFeatures = 324
    xMatrix, yMatrix = PrepareInputForBayesian(vectorizedReplayData, amountOfReplays, averageReplayLength, numberOfFeatures)
    X_train, X_test, y_train, y_test = train_test_split(xMatrix, yMatrix, test_size=0.2, random_state=42)
    
    if(existingModel is None):
        model = LinearRegression()
    else:
        model = existingModel

    model.fit(X_train, y_train)
    prediction = model.predict(X_test)
    print(f"r2 Score Of Test Set : {r2_score(y_test, prediction)}")
    return model


vectorizedReplayData = analyze.LoadVectorizedData(5000, 0)
LR = TrainLinearRegression(vectorizedReplayData, None)
BN = TrainBayesianNetwork(vectorizedReplayData, None)
LSTMmodel = TrainLSTM(vectorizedReplayData, None)

for i in range (1,6):
    vectorizedReplayData = analyze.LoadVectorizedData(5000, 5000*i)

    #print("Linear Regression " + str(i))
    #LR = TrainLinearRegression(vectorizedReplayData, LR)
    #print("Bayesian Network " + str(i))
    #BN = TrainBayesianNetwork(vectorizedReplayData, BN)
    #print("LSTM " + str(i))
    LSTMmodel = TrainLSTM(vectorizedReplayData, LSTMmodel)

#LR.save_weights("linearRegression30k.weights")
#BN.save_weights("bayesianNetwork30k.weights")
LSTMmodel.save_weights("lstm30k.weights")