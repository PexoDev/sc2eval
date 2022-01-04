import jsonpickle
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

def NormalizeInput(reps, amountOfReplays, theLongestReplayLength, numberOfFeatures):
    
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
        for dataPointIndex in range(20, min(len(reps[repIndex]), theLongestReplayLength)):
            xMatrix[repIndex,int(dataPointIndex),:] = reps[repIndex][dataPointIndex][:-1]
            yMatrix[repIndex,int(dataPointIndex)] = winnerIDs[repIndex]

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

reps = analyze.LoadVectorizedData(1, 0)

amountOfReplays = len(reps)
# theLongestReplayLength = FindLongestReplay(reps)
averageReplayLength = 145
# numberOfFeatures = len(reps[0][0])-1
numberOfFeatures = 324

xMatrix, yMatrix = NormalizeInput(reps, amountOfReplays, averageReplayLength, numberOfFeatures)

model = Sequential()
model.add(Masking(mask_value=-1.0, input_shape=(averageReplayLength,numberOfFeatures)))
model.add(LSTM(1024, input_shape=(averageReplayLength,numberOfFeatures), return_sequences=True, dropout = 0.2))
model.add(LSTM(512, input_shape=(averageReplayLength,1024), return_sequences = True))
model.add(Dense(2, activation='softmax'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=["acc"])

filename = "model_weights.hdf5"
model.load_weights(filename)

#X_train, X_test, y_train, y_test = train_test_split(xMatrix, yMatrix, test_size=1, random_state=42)
#y_train = to_categorical(y_train)
#y_test = to_categorical(y_test)

y_test = to_categorical(yMatrix)

# result = model.fit(X_train, y_train, batch_size=128, epochs=100, validation_split = 0.1)
# plt.figure()
# plt.plot(result.history['loss'])
# plt.plot(result.history['val_loss'])

predictions = model.predict(xMatrix)
finalPredictions = predictions.argmax(axis=2)
realResults = y_test.argmax(axis=2)

# model.save_weights(filename)

print()
print(accuracy_score(realResults, finalPredictions))
print(MyAccuracy(finalPredictions, realResults))

print(" ")