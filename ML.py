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

def NormalizeInput(reps, amountOfReplays, theLongestReplayLength, numberOfFeatures):
    
    maxValues = []
    winnerIDs = []

    for rep in range(len(reps)):
        winnerIDs.append(reps[rep]['0'].ReturnWinnerID())
        for dataPoint in reps[rep]:
            reps[rep][dataPoint] = reps[rep][dataPoint].Vectorize()

    for i in range(numberOfFeatures):
        maxValues.append(FindBiggestValue(reps,i))

    for rep in range(len(reps)):
        for dataPoint in reps[rep]:
            for i in range(numberOfFeatures):
                if(maxValues[i] == 0): 
                    continue
                reps[rep][dataPoint][i] = reps[rep][dataPoint][i]/maxValues[i]
  

    xMatrix = np.ones([amountOfReplays, theLongestReplayLength, numberOfFeatures])*-1
    yMatrix = np.zeros([amountOfReplays,theLongestReplayLength])

    for repIndex in range(len(reps)):
        for dataPointIndex in reps[repIndex]:
            xMatrix[repIndex,int(dataPointIndex),:] = reps[repIndex][dataPointIndex]
            yMatrix[repIndex,int(dataPointIndex)] = winnerIDs[repIndex]

    return xMatrix, yMatrix

def FindBiggestValue(Array, Index):
    max = 0
    for replay in Array:
        for dataPoint in replay:
            if(replay[dataPoint][Index] > max):
                max = replay[dataPoint][Index]
    return max

def FindLongestReplay(reps):
    max = 0
    for rep in range(len(reps)):
        if(len(reps[rep])>max):
            max  = len(reps[rep])  
    return max

reps = analyze.LoadReplays()

amountOfReplays = len(reps)
theLongestReplayLength = FindLongestReplay(reps)
numberOfFeatures = len(reps[0]['0'].Vectorize())

xMatrix, yMatrix = NormalizeInput(reps, amountOfReplays, theLongestReplayLength, numberOfFeatures)
X_train, X_test, y_train, y_test = train_test_split(xMatrix, yMatrix, test_size=0.2, random_state=42)

y_train = to_categorical(y_train)
y_test = to_categorical(y_test)

model = Sequential()
model.add(Masking(mask_value=-1.0, input_shape=(theLongestReplayLength,numberOfFeatures)))
model.add(LSTM(512, input_shape=(theLongestReplayLength,numberOfFeatures), return_sequences=True, dropout = 0.2))
model.add(LSTM(256, input_shape=(theLongestReplayLength,512), return_sequences = True))
model.add(Dense(2, activation='softmax'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=["acc"])

#filename = "model_weights_saved.hdf5"
#model.load_weights(filename)

result = model.fit(X_train, y_train, batch_size=256, epochs=25, validation_split = 0.1)
plt.figure()
plt.plot(result.history['loss'])
plt.plot(result.history['val_loss'])

predictions = model.predict(X_test)
finalPredictions = predictions.argmax(axis=2)
realResults = y_test.argmax(axis=2)

#model.save_weights(filename)

print()
print(accuracy_score(realResults, finalPredictions))

print(" ")

