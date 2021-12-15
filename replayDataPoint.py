class ReplayDataPoint:
    def __init__(self, player1Data, player2Data, winnerID):
        self.player1Data = player1Data
        self.player2Data = player2Data
        self.winnerID = winnerID

    def Vectorize(self):
        resultVector = self.player1Data.Vectorize() + self.player2Data.Vectorize()
        resultVector.append(self.winnerID)
        return resultVector