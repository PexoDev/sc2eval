import time
import numpy as np
import ReplaysParser 
import tensorflow as tf

from keras import optimizers
from keras.models import Sequential
from keras.layers import Dense, LSTM, Masking
from tensorflow.keras import losses
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split

modelNumberOfFeatures = 322 #142 for basic+army data

def PrepareInputData(reps, amountOfReplays, theLongestReplayLength, numberOfFeatures):
    winnerIDs = []

    for rep in range(len(reps)):
        winnerIDs.append(reps[rep][0][-1])

    xMatrix = np.ones([amountOfReplays, theLongestReplayLength, numberOfFeatures])*-1
    yMatrix = np.ones([amountOfReplays,theLongestReplayLength])*-1

    for repIndex in range(len(reps)):
        for dataPointIndex in range(len(yMatrix[repIndex])):
            yMatrix[repIndex,int(dataPointIndex)] = winnerIDs[repIndex]

        for dataPointIndex in range(min(len(reps[repIndex]), theLongestReplayLength)):
            for dataValueIndex in range (len(xMatrix[repIndex,int(dataPointIndex)])):
                if(xMatrix[repIndex,int(dataPointIndex),int(dataValueIndex)] < 0):
                    xMatrix[repIndex,int(dataPointIndex),int(dataValueIndex)] = 0

            xMatrix[repIndex,int(dataPointIndex),:] = reps[repIndex][dataPointIndex][:-1]

    return xMatrix, yMatrix

def FindLongestReplay(reps):
    max = 0
    for rep in range(len(reps)):
        if(len(reps[rep])>max):
            max  = len(reps[rep])  
    return max

def TrainLSTM(vectorizedReplayData, existingModel):
    theLongestReplayLength = FindLongestReplay(vectorizedReplayData)
    amountOfReplays = len(vectorizedReplayData)
    xMatrix, yMatrix = PrepareInputData(vectorizedReplayData, amountOfReplays, theLongestReplayLength, modelNumberOfFeatures)
    
    if(existingModel is not None):
        model = existingModel
    else:
        model = InitializeLSTMModel()

    X_train, X_test, y_train, y_test = train_test_split(xMatrix, yMatrix, test_size=0.2, random_state=42)
    y_train = to_categorical(y_train)
    y_test = to_categorical(y_test)

    es = EarlyStopping(monitor='val_loss', mode='min', patience=5, min_delta=0.001, verbose=1, restore_best_weights = True)

    result = model.fit(X_train, y_train, batch_size=128, epochs=100, validation_data=[X_test, y_test], callbacks=[es])
    print("Model Loss")
    print(result.history['loss'])
    print("Validation Loss")
    print(result.history['val_loss'])

    return model

def IterateTraining(batchSize, maxReplaysToUse, modelNamePrefix):
    startTime = time.time()
    vectorizedReplayData = ReplaysParser.LoadVectorizedData(batchSize, 0)
    #vectorizedReplayData = ReplaysParser.ExtractBasicAndArmyData(vectorizedReplayData)

    LSTMmodel = TrainLSTM(vectorizedReplayData, None)

    for i in range (1, int(maxReplaysToUse/batchSize)-1 ):
        vectorizedReplayData = ReplaysParser.LoadVectorizedData(batchSize, batchSize*i)
        #vectorizedReplayData = ReplaysParser.ExtractBasicAndArmyData(vectorizedReplayData)

        try:
            LSTMmodel = TrainLSTM(vectorizedReplayData, LSTMmodel)
        except Exception as e:
            print(e)

        print("BATCH [" + str(i) + "/"+str(int(maxReplaysToUse/batchSize)-1)+"]")

    LSTMmodel.save_weights(modelNamePrefix+str(maxReplaysToUse)+".weights")
    print("Training time: " + str(time.time() - startTime))

def InitializeLSTMModel():
    model = Sequential()
    model.add(Masking(mask_value=-1.0, input_shape=(None, modelNumberOfFeatures)))
    model.add(LSTM(1024, return_sequences = True, dropout = 0.2))
    model.add(LSTM(512, return_sequences = True, dropout = 0.2))
    model.add(LSTM(256, return_sequences = True, dropout = 0.2))
    model.add(Dense(2, activation='softmax'))
    model.compile(loss="binary_crossentropy", optimizer='adam', metrics=["accuracy"])
    return model

def UseTrainedLSTMModel(weightsPath):
    model = InitializeLSTMModel()
    model.load_weights(weightsPath)
    return model

#IterateTraining(128, 30000, "lstm_all-features_batch128-128_layers1024-512-256_")