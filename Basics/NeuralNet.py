#Keras NNET

import os
import copy
import time
import shutil
import random
import numpy as np
import math
from pickle import Pickler, Unpickler
import sys
import itertools
import pygame

from Basics.NeuralNetBasis import NeuralNet, GameModel, Trainer
from Basics.MCTS import MCTS, MCTNode, MCTS_NN, MCTS_NN_Node

from keras.models import *
from keras.layers import *
from keras.optimizers import *


class NNWrapper(NeuralNet):

    def __init__(self, game, board):

        NNparams = {'TicTacToe': [0.3, 512, 0.001, 64, 10]}

        self.game = game.__class__
        self.board = board
        self.gamename = game.__class__.__name__
        self.args = NNparams[self.gamename]
        
        self.NN = GameNN(game, self.args[0], self.args[1], self.args[2], board)
        
        self.board_x, self.board_y = game.rows, game.cols
        self.action_size = len(game.all_possible_moves(board))
        

    def train(self, states):
        
        inputs, target_res, target_policy = list(zip(*states))

        inputs = np.asarray(inputs).astype(np.float32)
        target_res = np.asarray(target_res).astype(np.float32)
        
        target_policy = list(target_policy)
        max_len = len(max(target_policy, key=len))
        target_policy = [target_policy[i] + [0] * (max_len - len(target_policy[i])) for i in range(len(target_policy))]
        target_policy = np.asarray(target_policy).astype(np.float32)

        self.NN.model.fit(x = inputs, y = [target_policy, target_res], batch_size = self.args[3], epochs = self.args[4])
        self.save_checkpoint()

    def predict(self, board):

        board = board[np.newaxis, :, :]
        pi, v = self.NN.model.predict(board)

        return (pi[0], v[0])

    def save_checkpoint(self, folder=None, filename=None):

        if folder is None:
            folder = '{}/checkpoints/'.format(self.gamename)
        if filename is None:
            filename = 'checkpoint.pth.tar'.format(self.gamename)
        
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            print("Checkpoint Directory does not exist! Making directory {}".format(folder))
            os.mkdir(folder)
            
        else:
            print("Checkpoint Directory exists! ")
            
        self.NN.model.save_weights(filepath)


    def load_checkpoint(self, folder=None, filename=None):

        if folder is None:
            folder = '{}/checkpoints/'.format(self.gamename)
        if filename is None:
            filename = 'checkpoint.pth.tar'.format(self.gamename)
        
        filepath = os.path.join(folder, filename)
        #if not os.path.exists(filepath):
        #    raise Exception("No model in path '{}'".format(filepath))
        
        self.NN.model.load_weights(filepath)


class GameNN(GameModel):
    
    def __init__(self, game, dropout, channelnum, lr, board):

        # game params
        self.game = game.__class__
        self.board_x, self.board_y = game.cols, game.rows
        self.action_size = len(game.all_possible_moves(board))
        self.dropout = dropout
        self.channelnum = channelnum
        self.lr = lr

        # Neural Net
        self.input_boards = Input(shape=(self.board_x, self.board_y))                                                           # s: batch_size x board_x x board_y

        x_image = Reshape((self.board_x, self.board_y, 1))(self.input_boards)                                                   # batch_size  x board_x x board_y x 1
        h_conv1 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(self.channelnum, 3, padding='same')(x_image)))           # batch_size  x board_x x board_y x num_channels
        h_conv2 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(self.channelnum, 3, padding='same')(h_conv1)))           # batch_size  x board_x x board_y x num_channels
        h_conv3 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(self.channelnum, 3, padding='same')(h_conv2)))           # batch_size  x (board_x) x (board_y) x num_channels
        h_conv4 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(self.channelnum, 3, padding='valid')(h_conv3)))          # batch_size  x (board_x-2) x (board_y-2) x num_channels
        h_conv4_flat = Flatten()(h_conv4)       
        s_fc1 = Dropout(self.dropout)(Activation('relu')(BatchNormalization(axis=1)(Dense(1024)(h_conv4_flat))))                # batch_size x 1024
        s_fc2 = Dropout(self.dropout)(Activation('relu')(BatchNormalization(axis=1)(Dense(512)(s_fc1))))                        # batch_size x 1024
        self.pi = Dense(self.action_size, activation='softmax', name='pi')(s_fc2)                                               # batch_size x self.action_size
        self.v = Dense(1, activation='tanh', name='v')(s_fc2)                                                                   # batch_size x 1

        self.model = Model(inputs=self.input_boards, outputs=[self.pi, self.v])
        self.model.compile(loss=['categorical_crossentropy','mean_squared_error'], optimizer=Adam(self.lr))


class GameTraining(Trainer):

    def __init__(self, name, epNum, simNum, game, NN, simTime=None):
        self.epNum = epNum
        self.simNum = simNum
        self.simTime = simTime

        self.game = game
        self.gcls = game.__class__
        self.gamename = game.__class__.__name__
        self.name = name

        self.NN = NN
        self.PNN = self.NN.__class__(game, self.NN.board)

    def trainNN(self, name=None):
        
        examples = self.loadExamples(name)
        self.NN.train(examples)

    def testNN(self):

        result = [0, 0, 0]

        for i in range(10):
            player = self.getPlayer(i)
            currentgame = self.gcls(width=self.game.width, height=self.game.height, player=player)
            
            while currentgame.game_result()[0] is False:

                if currentgame.player == 0:
                    Nmcts = MCTS_NN(self.NN, 0, mode="play")

                    root = MCTS_NN_Node(currentgame, self.NN, currentgame.game_board, currentgame.game_state(currentgame.game_board, 0), 0)
                    action = Nmcts.search(root)
                    currentgame.pc_move(action)

                elif currentgame.player == 1:
                    
                    action = currentgame.random_player()
                    currentgame.pc_move(action)

            if currentgame.game_result()[0] == 1:
                result[0] += 1

            elif currentgame.game_result()[0] == -1:
                result[1] += 1

            else:
                result[2] += 1

        if result[0] > result[1]:
            print("Good NN!")
            self.NN.save_checkpoint()
            self.NN.save_checkpoint(folder="{}/models".format(self.gamename), filename="{}.pth.tar".format(self.name))

            if result[1] >= 4 and result[0] + result[2] < 6:
                return True

            else:
                return False

            
        else:
            print("Bad NN")
            return True

    def optimizeNN(self):

        result = [0, 0]
        self.NN.save_checkpoint(filename="{}-temp.pth.tar".format(self.name))
        self.PNN.load_checkpoint(filename="{}-temp.pth.tar".format(self.name))

        self.trainNN("game")
        trainTurn = []

        for i in range(self.epNum):
            player = self.getPlayer(i)
            currentgame = self.gcls(width=self.game.width, height=self.game.height, player=player)
            
            while currentgame.game_result()[0] is False:

                preboard = copy.deepcopy(currentgame.game_board)

                if currentgame.player == 0:
                    exp = round(random.uniform(0.0, 0.7), 2)
                    Nmcts = MCTS_NN(self.NN, 0, exp=exp)

                    root = MCTS_NN_Node(currentgame, self.NN, currentgame.game_board, currentgame.game_state(currentgame.game_board, 0), 0)
                    action = Nmcts.search(root)
                    currentgame.pc_move(action)
                    root.printStats()

                    trainTurn.append([preboard, 1, root.future_result, root.probs])

                elif currentgame.player == 1:
                    Pmcts = MCTS_NN(self.PNN, 1)

                    root = MCTS_NN_Node(currentgame, self.PNN, currentgame.game_board, currentgame.game_state(currentgame.game_board, 1), 1)
                    action = Pmcts.search(root)
                    currentgame.pc_move(action)
                    root.printStats()

                    trainTurn.append([preboard, 1, root.future_result, root.probs])

            if currentgame.game_result()[0] == 1:
                result[0] += 1

            elif currentgame.game_result()[0] == -1:
                result[1] += 1

        if result[0] > result[1]:
            trainGame = [(x[0], x[2], x[3]) for x in trainTurn]
            self.writeExamples(trainGame, "ogames")
            
            self.NN.save_checkpoint()
            self.NN.save_checkpoint(folder="{}/models".format(self.gamename), filename="{}.pth.tar".format(self.name))

        else:
            self.NN.load_checkpoint(filename="{}-temp.pth.tar".format(self.name))
            

    def solvedExamples(self):

        if not self.game.solved:
            print("Game not solved. Training Best as Hard.")
            self.name = "hard"
            self.createExamples()
            return

        trainTurn = []

        for i in range(50):
            player = self.getPlayer(i)
            currentgame = self.gcls(width=self.game.width, height=self.game.height, player=player)

            first, second, order = currentgame.solved_moves()
            turn = 1

            while currentgame.game_result()[0] is False:

                preboard = copy.deepcopy(currentgame.game_board)
                pplayer = copy.deepcopy(currentgame.player)
                moves = currentgame.all_possible_moves(currentgame.game_board)

                if turn in order[0]:

                    order[0].remove(turn)
                    move = first[random.randint(0, len(first)-1)]
                    first.remove(move)
                    currentgame.pc_move(move)
                    
                elif turn in order[1]:
                    
                    order[1].remove(turn)
                    move = currentgame.getMove(second, currentgame.game_board)
                    second.remove(move)
                    currentgame.pc_move(move)
                    
                probs = []
                for all_move in moves:
                    if all_move.pos_x == move.pos_x and all_move.pos_y == move.pos_y:
                        probs.append(1.0)
                    else:
                        probs.append(0)

                turn += 1
                trainTurn.append([preboard, pplayer, int((-1.0) ** pplayer), probs])

        trainGames = [(x[0], x[2], x[3]) for x in trainTurn]
        print(trainGames)
        self.writeExamples(trainGames, "best")


    def customExamples(self):

        trainTurn = []

        for i in range(10):
            player = self.getPlayer(i)
            currentgame = self.gcls(width=self.game.width, height=self.game.height, player=player)

            while currentgame.game_result()[0] is False:

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        
                        preboard = copy.deepcopy(currentgame.game_board)
                        pplayer = copy.deepcopy(currentgame.player)
                        moves = currentgame.all_possible_moves(currentgame.game_board)

                        move = currentgame.click()
                    
                        probs = []
                        for all_move in moves:
                            if all_move.pos_x == move.pos_x and all_move.pos_y == move.pos_y:
                                probs.append(1.0)
                            else:
                                probs.append(0)

                        trainTurn.append([preboard, pplayer, 0, probs])

                currentgame.render()

        trainGames = [(x[0], x[2], x[3]) for x in trainTurn]
        print(trainGames)
        self.writeExamples(trainGames, "cust")

    
    def createExamples(self):

        trainTurn = []    

        for i in range(self.epNum):
            player = self.getPlayer(i)
            currentgame = self.gcls(width=self.game.width, height=self.game.height, player=player)
            gameSimNum1, gameSimNum2 = self.setPlayers()

            player1 = MCTS(0, gameSimNum1)
            player2 = MCTS(1, gameSimNum2)
            
            while currentgame.game_result()[0] is False:

                preboard = copy.deepcopy(currentgame.game_board)

                if currentgame.player == 0:
                    
                    root1 = MCTNode(currentgame.game_state(currentgame.game_board, 0), currentgame.game_board, 0, currentgame)
                    best_node1 = player1.search(root1)
                    currentgame.pc_move(best_node1.action)
                    root1.printStats()
                    
                    trainTurn.append([preboard, 0, root1.future_result, root1.probs])

                elif currentgame.player == 1:
                    
                    root2 = MCTNode(currentgame.game_state(currentgame.game_board, 1), currentgame.game_board, 1, currentgame)
                    best_node2 = player2.search(root2)
                    currentgame.pc_move(best_node2.action)
                    root2.printStats()
                    
                    trainTurn.append([preboard, 1, root2.future_result, root2.probs])
                    
        trainGames = [(x[0], x[2], x[3]) for x in trainTurn]
        print(trainGames)
        self.writeExamples(trainGames)


    def writeExamples(self, trainData, name=None):

        folder = "./{}/examples/".format(self.gamename)
        if not os.path.exists(folder):
            os.makedirs(folder)

        if name is None:
            name = self.name
        
        filename = os.path.join(folder, name + ".examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(trainData)
        f.closed


        
    def loadExamples(self, name=None):

        if name is None:
            name = self.name

        if name == "best":
            trainGames = self.combineAllExamples()
            return trainGames

        if name == "game":
            trainGames = self.loadGameExamples()
            return trainGames

        examplesFile = "./" + self.gamename + "/examples/" + name + ".examples"

        if not os.path.isfile(examplesFile):
            print(f'File "{examplesFile}" with trainExamples not found!')
            r = input("Continue? [y|n]")
            if r != "y":
                sys.exit()

        else:
            print("File with trainExamples found. Loading it...")
            with open(examplesFile, "rb") as f:
                trainGames = Unpickler(f).load()

            f.closed
            print("Examples loaded")
            return trainGames


    def combineAllExamples(self):

        folder = "./{}/examples/".format(self.gamename)
        files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        
        trainGames = []
            
        for file in files:
            temp = []
            with open(file, "rb") as f:
                temp = Unpickler(f).load()
                    
            trainGames.append(temp)
            f.closed


        dataCopy = copy.deepcopy(trainGames)
        trainGames = []
        for diff in dataCopy:
            for turn in diff:
                trainGames.append((turn[0], turn[1], turn[2]))

        print(trainGames)            
        return trainGames


    def loadGameExamples(self):

        folder = "./{}/examples/".format(self.gamename)
        files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and "game" in f]

        trainGames = []
            
        for file in files:
            temp = []
            with open(file, "rb") as f:
                temp = Unpickler(f).load()
                    
            trainGames.append(temp)
            f.closed


        dataCopy = copy.deepcopy(trainGames)
        trainGames = []
        for diff in dataCopy:
            for turn in diff:
                trainGames.append((turn[0], turn[1], turn[2]))

        print(trainGames)            
        return trainGames
        




    def getPlayer(self, num):
        return num % 2

    def setPlayers(self):

        eloSets = {"hard": [1600, 2000, 3200, 4000, 6400],
                   "midd": [250, 500, 1000, 1600, 2000],
                   "easy": [10, 50, 100, 250, 500],
                   "deft": [10, 250, 500, 1000, 3200]}
        Eset = eloSets[self.name]
        
        return Eset[random.randint(0, len(Eset)-1)], Eset[random.randint(0, len(Eset)-1)]
                

    
