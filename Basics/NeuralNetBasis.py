#Basis fuer Neuronale Netze - als Warpper fuer Hauptfunktionen des Modells

from pickle import Pickler, Unpickler

class NeuralNet():
    def __init__(self, game, board):
        pass

    def train(self, states):
        pass

    def predict(self, board):
        pass

    def save_checkpoint(self, folder, filename):
        pass

    def load_checkpoint(self, folder, filename):
        pass

class GameModel():
    pass

class Trainer():

    def __init__(self, epNum, simNum, game, NN, simTime=None):
        pass

    def trainNN(self):
        pass

    def optimizeNN(self):
        pass
        
    def createExamples(self):
        pass

    def write(self):
        pass

    def writeExamples(self):
        pass
        
    def loadExamples(self):
        pass
