from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from keras.models import Sequential
from keras.layers import Dense, LSTM, Masking

import numpy as np
import analyze 
import matplotlib.pyplot as plt

reps = analyze.LoadReplays()

amountOfReplays = len(reps)
theLongestReplayLength = 0
numberOfFeatures =  len(reps[0]['0'].Vectorize())

for rep in reps:
    if(len(reps[rep])>theLongestReplayLength):
        theLongestReplayLength = len(reps[rep])

xMatrix = np.zeros([amountOfReplays, theLongestReplayLength, numberOfFeatures])
yMatrix = np.zeros([amountOfReplays, theLongestReplayLength])

for repIndex in range(len(reps)):
    for dataPointIndex in reps[repIndex]:
        xMatrix[repIndex,int(dataPointIndex),:] = reps[repIndex][dataPointIndex].Vectorize()
        yMatrix[repIndex,int(dataPointIndex)] = reps[repIndex][dataPointIndex].ReturnWinnerID() - 1

min_max_scaler = preprocessing.MinMaxScaler()
xMatrix = np.reshape(xMatrix, (amountOfReplays*theLongestReplayLength, numberOfFeatures))
X_train_minmax = min_max_scaler.fit_transform(xMatrix)
X_train_minmax = np.reshape(X_train_minmax, (amountOfReplays,theLongestReplayLength, numberOfFeatures))

X_train, X_test, y_train, y_test = train_test_split(X_train_minmax, yMatrix, test_size=0.33, random_state=42)

model = Sequential()
#model.add(Masking(mask_value = 0, input_shape=(theLongestReplayLength,numberOfFeatures)))
model.add(LSTM(256, input_shape=(theLongestReplayLength,numberOfFeatures), return_sequences=True))
model.add(LSTM(128, return_sequences = True))
model.add(Dense(1, activation='softmax'))
model.compile(loss='binary_crossentropy', optimizer='adam')

#filename = "model_weights_saved.hdf5"
#model.load_weights(filename)
#model.compile(loss='categorical_crossentropy', optimizer='adam')

result = model.fit(X_train, y_train, batch_size=256, epochs=100)
plt.figure()
plt.plot(result.history['loss'])

print("XD")

def NormalizeInput(replays):
    amountOfReplays = len(reps)
    theLongestReplayLength = 0
    numberOfFeatures =  len(reps[0]['0'].Vectorize())
    maxValues = []

    for i in range(numberOfFeatures):
        maxValues.append(FindBiggestValue(reps,i))

    for rep in reps:
        if(len(reps[rep])>theLongestReplayLength):
            theLongestReplayLength = len(reps[rep])

    

    xMatrix = np.zeros([amountOfReplays, theLongestReplayLength, numberOfFeatures])
    yMatrix = np.zeros([amountOfReplays, theLongestReplayLength])

    for repIndex in range(len(reps)):
        for dataPointIndex in reps[repIndex]:
            xMatrix[repIndex,int(dataPointIndex),:] = reps[repIndex][dataPointIndex].Vectorize()
            yMatrix[repIndex,int(dataPointIndex)] = reps[repIndex][dataPointIndex].ReturnWinnerID() - 1

def FindBiggestValue(Array, Index):
    max = 0
    for row in Array:
        if(row[str(Index)] > max):
            max = row[str(Index)]
    return max