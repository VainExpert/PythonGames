#Monte Carlo Tree Search

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import math
import random
import copy
import time
import numpy as np
np.seterr(all="ignore")

class MCTS():

    def __init__(self, player, sim_numb=None, sim_time=None):
        self.player = player
        self.sim_numb = sim_numb
        self.sim_time = sim_time


    def search(self, root):

        if self.sim_numb is None:
            assert(self.sim_time is not None)
            end_time = time.time() + self.sim_time

            while time.time() < end_time:
                node = self.select_node_policy(root)
                reward = node.rollout(self.player)
                node.backpropagate(reward)

        else:
            
            for _ in range(self.sim_numb):
                node = self.select_node_policy(root)
                reward = node.rollout(self.player)
                node.backpropagate(reward)

        return root.best_child(param=0)


    def select_node_policy(self, root):

        current_node = root
        while not current_node.is_terminal():

            if not current_node.is_expanded():
                return current_node.expand(self.player)

            else:
                current_node = current_node.best_child()

        return current_node


class MCTNode():

    def __init__(self, score, board, player, game, action=None, parent=None):

        self.score = score
        self.board = board
        self.current = player
        self.parent = parent
        self.action = action
        self.game = game
        self.gcls = game.__class__

        self.results = {'-1': 0, '1': 0, '0': 0, '0.5': 0}
        self.visits = 0

        self.all_actions = None
        self.untried_actions = None
        self.tried_actions= []
        self.children = []

        self.probs = self.move_probs()
        self.future_result = 0.5

    def move_probs(self):

        self.probs = [(child.set_value() / child.visits) + 0 * math.sqrt((math.log(self.visits))/child.visits)
                   for child in self.children]
            

    def future(self):

        keys = ['-1', '1', '0.5']
        res = self.results[keys[0]]
        key = -1
        for k in keys:
            if self.results[k] > res:
                res = self.results[k]
                key = float(k)

        self.future_result = key
        

    def pprint(self):
        
        output = ""
        for row in self.board:
            output += str(row) + "\n"
        return output

    def printStats(self):

        output = ""
        output += "Player:" + str(self.current) + "\n"
        output += self.pprint()
        self.future()
        output += "Calc Result:" + str(self.future_result) + " Current:" + str(self.score) + "\n"
        self.move_probs()
        for i in range(len(self.tried_actions)):
            output += "Probability:" + str(self.probs[i]) + "Move:" + str(self.tried_actions[i].pos) + "\n"
        return output


    def set_value(self):
        wins = self.results['1']
        draws = self.results['0.5']
        loses = self.results['-1']
        noneturns = self.results['0']

        if loses == 0 and noneturns == 0:
            return wins + draws

        elif loses == 0:
            return (wins + draws) / noneturns

        elif noneturns == 0:
            return (wins + draws) / loses

        else:
            return (wins + draws) / (loses + noneturns)
    

    def is_expanded(self):
        return len(self.get_actions()) == 0

    def is_terminal(self):
        return self.score != 0


    def best_child(self, param=1.4):
        
        weights = [(child.set_value() / child.visits) + param * math.sqrt((math.log(self.visits))/child.visits)
                   for child in self.children]

        return self.children[np.argmax(weights)]

    def backpropagate(self, score):
        
        self.visits += 1
        self.results[str(score)] += 1
        
        if self.parent:
            self.parent.backpropagate(score)

    def get_actions(self):

        if self.untried_actions is None:
            self.untried_actions = self.game.all_possible_moves(self.board)
            self.all_actions = self.untried_actions
        
        return self.untried_actions

    def rollout(self, ownplayer):

        current_node = self
        lookahead = 0
        while not current_node.is_terminal() and lookahead != 24:

            sim_game = self.gcls(width=self.game.width, height=self.game.height, player=current_node.current)
            possible_moves = current_node.get_actions()
            action = possible_moves[random.randint(0, len(possible_moves)-1)]
            next_score, next_board, next_player = sim_game.simulate_move(action, current_node.board, current_node.current, ownplayer)
            new_node = MCTNode(next_score, next_board, next_player, sim_game, action, parent=current_node)
            current_node = new_node
            lookahead += 1

        return current_node.score

    def expand(self, ownplayer):

        action = self.get_actions().pop()
        self.tried_actions.append(action)
        sim_game = self.gcls(width=self.game.width, height=self.game.height, player=ownplayer)

        next_score, next_board, next_player = sim_game.simulate_move(action, self.board, self.current, ownplayer)
        child_node = MCTNode(next_score, next_board, next_player, sim_game, action, parent=self)

        self.children.append(child_node)
        return child_node




class MCTS_NN():

    def __init__(self, NN, player, mode="train", exp=1.0):
        self.NN = NN
        self.exploration = exp
        self.player = player
        modi = {"train": [1600, None], "play": [None, 7], "very fast": [None, 1], "fast": [None, 2]}
        self.simNum = modi[mode][0]
        self.simTime = modi[mode][1]

    def search(self, root):

        if self.simNum is None:
            assert(self.simTime is not None)
            end_time = time.time() + self.simTime

            while time.time() < end_time:
                node = self.select_node(root)
            
                while node.result == 0:
                    node = node.expand(self.player)

                node.backpropagate(node.score)

            root.update()        
            return root.best_action(self.exploration)

        else:
            
            for _ in range(self.simNum):
                node = self.select_node(root)
            
                while node.result == 0:
                    node = node.expand(self.player)

                node.backpropagate(node.score)

            root.update()        
            return root.best_action(self.exploration)
    
            

    def select_node(self, node):

        current = node

        while current.result == 0:
            if len(current.unexpanded_moves) != 0:
                return current.expand(self.player)

            else:
                if len(current.children) == 1:
                    return current.children[0]
                
                current = current.best_child(self.exploration)

        return current


class MCTS_NN_Node():

    def __init__(self, game, NN, board, score, player, parent=None, action=None):

        self.board = board
        self.score = score
        self.result = score
        self.current = player
        self.action = action
    
        self.possible_moves = game.all_possible_moves(board)
        self.unexpanded_moves = copy.deepcopy(self.possible_moves)
        self.expanded_moves = []

        self.NN = NN
        self.probs = []
        self.future_result = 0.5
        self.updated = False
        self.visits = 0

        self.game = game
        self.gcls = game.__class__
        self.children = []
        self.parent = parent

    def pprint(self):
        
        output = ""
        for row in self.board:
            output += str(row) + "\n"
        return output


    def printStats(self):

        output = ""
        output += "Player:" + str(self.current) + "\n"
        output += self.pprint()
        output += "Calc Result:" + str(self.future_result) + " Current:" + str(self.score) + "\n"
        for i in range(len(self.expanded_moves)):
            output += "Probability:" + str(self.probs[i]) + "Move:" + str(self.expanded_moves[i].pos) + "\n"
        return output

    
    def update(self):

        if not self.updated:
            results = self.NN.predict(self.board)

            self.probs = results[0].tolist()
            self.score += results[1][0]
            self.future_result = results[1][0]
            
            self.updated = True

    def expand(self, ownplayer):

        action = self.unexpanded_moves.pop()
        self.expanded_moves.append(action)
        sim_game = self.gcls(width=self.game.width, height=self.game.height, player=ownplayer)

        next_score, next_board, next_player = sim_game.simulate_move(action, self.board, self.current, ownplayer)
        child_node = MCTS_NN_Node(sim_game, self.NN, next_board, next_score, next_player, parent=self, action=action)
        self.children.append(child_node)

        return child_node

    def backpropagate(self, res):

        self.update()
        self.score += res
        self.visits += 1
        
        if self.parent:
            self.parent.backpropagate(res)

    def best_child(self, exp):

        ucbs = self.ucbs(exp)
        return self.children[np.argmax(ucbs)]

    def best_action(self, exp):
        return self.best_child(exp).action

    def ucbs(self, exp):

        child_visits = 0
        for child in self.children:
            child_visits += child.visits
        
        return [child.score + exp * self.probs[count] * (math.sqrt(child_visits) / (self.visits)) for count, child in enumerate(self.children)]
        
