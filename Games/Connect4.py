#Connect 4

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pygame
import math
import random
import copy
from Basics.BasicGame import GameUtils, GameMove



class TicTacToe(GameUtils):
    
    def __init__(self, width=1540, height=1320, cols=7, rows=6, player=None):
        super().__init__(width, height, cols, rows)

        self.IMG_SIZE = int((self.width/self.rows)-(self.width/10))
        self.solved = True
        self.rescaled = False

        if player is None:
            self.player = None
            self.player_sym = None
            self.player_img = None

            self.rand_start()


        else:
            self.player = player

            if self.player == 0:
                self.player_sym = 'Y'
                self.player_num = -1
                self.player_img = pygame.transform.scale(pygame.image.load("C:/Users/Tom/Documents/Coding/Code/GitHub/PythonGames/Games/X_SYM.png"), (self.IMG_SIZE, self.IMG_SIZE))

            else:
                self.player_sym = 'R'
                self.player_num = 1
                self.player_img = pygame.transform.scale(pygame.image.load("C:/Users/Tom/Documents/Coding/Code/GitHub/PythonGames/Games/O_SYM.png"), (self.IMG_SIZE, self.IMG_SIZE))

        self.init_grid()

    @classmethod
    def get_player_num(cls, player):
        if player == 0:
            return -1
        else:
            return 1

    def rand_start(self):
        
        player = random.randint(0,1)
        
        if player == 0:
            self.player = 0
            self.player_sym = 'Y'
            self.player_num = -1
            self.player_img = pygame.transform.scale(pygame.image.load("C:/Users/Tom/Documents/Coding/Code/GitHub/PythonGames/Games/X_SYM.png"), (self.IMG_SIZE, self.IMG_SIZE))
            
        else:
            self.player = 1
            self.player_sym = 'R'
            self.player_num = 1
            self.player_img = pygame.transform.scale(pygame.image.load("C:/Users/Tom/Documents/Coding/Code/GitHub/PythonGames/Games/O_SYM.png"), (self.IMG_SIZE, self.IMG_SIZE))

        

    def change_player(self):
        if self.player == 1:
            self.player = 0
            self.player_sym = 'Y'
            self.player_num = -1
            self.player_img = pygame.transform.scale(pygame.image.load("C:/Users/Tom/Documents/Coding/Code/GitHub/PythonGames/Games/X_SYM.png"), (self.IMG_SIZE, self.IMG_SIZE))
            
        else:
            self.player = 1
            self.player_sym = 'R'
            self.player_num = 1
            self.player_img = pygame.transform.scale(pygame.image.load("C:/Users/Tom/Documents/Coding/Code/GitHub/PythonGames/Games/O_SYM.png"), (self.IMG_SIZE, self.IMG_SIZE))



    def click(self):

        self.rescale_img()
        m_x, m_y = pygame.mouse.get_pos()

        for i in range(self.cols):
            for j in range(self.rows):
                if self.game_board[i][j] == 0:
                    
                    x = self.transform_coords(j)
                    y = self.transform_coords(i)

                    dis = math.sqrt((x - m_x) ** 2 + (y - m_y) ** 2)

                    if dis < self.width // self.rows // 2:
                        self.imgs.append((x, y, self.player_img))
                        self.game_board[i][j] = self.player_num

                        self.change_player()

                        return Connect4Move(i, j)

            
    def game_result(self):
        
        if self.game_state(self.game_board, 0) == 1:
            return 1, "Y"

        elif self.game_state(self.game_board, 0) == -1:
            return -1, "R"

        elif self.game_state(self.game_board, 0) == 0.5:
            return 0.5, ""

        else:
            return False, ""


    def game_state(self, board, rootplayer):
        
        state = []

        for i in range(self.rows):
            for j in range(self.cols):
                
                if board[i][j] == 0:
                    state.append(0)
                    
                elif board[i][j] != 0:
                    state.append(board[i][j])

                if len(state) == 3:
                    if (state[0] == state[1] == state[2]) and 0 not in state:

                        if (rootplayer == 0 and state[0] == -1) or (rootplayer == 1 and state[0] == 1):
                            return 1

                        else:
                            return -1

                    else:
                        state = []

        for i in range(self.rows):
            for j in range(self.cols):
                
                if board[j][i] == 0:
                    state.append(0)
                    
                elif board[j][i] != 0:
                    state.append(board[j][i])

                if len(state) == 3:
                    if (state[0] == state[1] == state[2]) and 0 not in state:

                        if (rootplayer == 0 and state[0] == -1) or (rootplayer == 1 and state[0] == 1):
                            return 1

                        else:
                            return -1

                    else:
                        state = []

        if board[1][1] != 0:
            
            if board[0][0] == board[1][1] == board[2][2]:
                if (rootplayer == 0 and board[1][1] == -1) or (rootplayer == 1 and board[1][1] == 1):
                    return 1

                else:
                    return -1

            if board[0][2] == board[1][1] == board[2][0]:
                if (rootplayer == 0 and board[1][1] == -1) or (rootplayer == 1 and board[1][1] == 1):
                    return 1

                else:
                    return -1

        for i in range(len(board)):
            if 0 in board[i]:
                return 0

        return 0.5


    def simulate_move(self, move, board, player, rootplayer):

        temp_board = copy.deepcopy(board)

        j, i = move.pos_x, move.pos_y
        x = self.transform_coords(j)
        y = self.transform_coords(i)
        
        temp_board[i][j] = self.get_player_num(player)
        score = self.game_state(temp_board, rootplayer)

        if player == 0:
            temp_player = 1
        else:
            temp_player = 0

        return score, temp_board, temp_player

    def pc_move(self, move):

        self.rescale_img()
        
        j, i = move.pos_x, move.pos_y
        x = self.transform_coords(j)
        y = self.transform_coords(i)
        
        self.imgs.append((x, y, self.player_img))      
        self.game_board[i][j] = self.player_num

        self.change_player()

    def is_valid_col(self, col):
        return self.game_board[5][col] == 0

    def next_open_row(self, board, col):
        
        for r in range(self.rows):
            if self.game_board[r][col] == 0:
                return r

    @classmethod
    def all_possible_moves(cls, board):

        possible_moves = []
        idx = 0
        for col in range(self.cols):
            if self.is_vaild_col(col):
                row = self.next_open_row(board, col)
                possible_moves.append(Connect4Move(row, col, idx))
                idx += 1

        return possible_moves

##    def solved_moves(self):
##
##        corners = [[0, 0], [0, 2], [2, 0], [2, 2]]
##        reactions = [[1, 1], [1, 0], [2, 1], [1, 2], [0, 1]]
##        turn_order = {0: [1, 2, 3, 5], 1: [4, 6, 7]}
##
##        first_turns = []
##        for corner in corners:
##            first_turns.append(Connect4Move(corner[0], corner[1]))
##
##        defences = []
##        for react in reactions:
##            defences.append(Connect4Move(react[0], react[1]))
## 
##        return first_turns, defences, turn_order

##    def getMove(self, moves, board):
##
##        if board[0][0] != 0 and board[0][2] != 0 and board[0][0] == board[0][2]:
##            search = self.searchMove(moves, 0, 1)
##            if search is not None:
##                return search
##
##        if board[0][0] != 0 and board[2][0] != 0 and board[0][0] == board[2][0]:
##            search = self.searchMove(moves, 1, 0)
##            if search is not None:
##                return search
##
##        if board[0][0] != 0 and board[2][2] != 0 and board[0][0] == board[2][2]:
##            search = self.searchMove(moves, 1, 1)
##            if search is not None:
##                return search
##
##        if board[0][2] != 0 and board[2][2] != 0 and board[0][2] == board[2][2]:
##            search = self.searchMove(moves, 1, 2)
##            if search is not None:
##                return search
##
##        if board[0][2] != 0 and board[2][0] != 0 and board[0][2] == board[2][0]:
##            search = self.searchMove(moves, 1, 1)
##            if search is not None:
##                return search                
##
##        if board[2][0] != 0 and board[2][2] != 0 and board[2][0] == board[2][2]:
##            search = self.searchMove(moves, 2, 1)
##            if search is not None:
##                return search
##            
##    def searchMove(self, moves, x, y):
##
##        for move in moves:
##            if move.pos_x == y and move.pos_y == x:
##                return move
##
##        return None

    def rescale_img(self):
        if self.width != 1540 and not self.rescaled:
            if self.player == 0:
                self.player_img = pygame.transform.scale(pygame.image.load("C:/Users/Tom/Documents/Coding/Code/GitHub/PythonGames/Games/X_SYM.png"), (self.IMG_SIZE, self.IMG_SIZE))

            else:
                self.player_img = pygame.transform.scale(pygame.image.load("C:/Users/Tom/Documents/Coding/Code/GitHub/PythonGames/Games/O_SYM.png"), (self.IMG_SIZE, self.IMG_SIZE))

            self.rescaled = True

    def render(self):
        
        self.window.fill(self.Colors['WHITE'])
        self.draw_grid()

        for img in self.imgs:
            x, y, IMG = img
            self.window.blit(IMG, (x - IMG.get_width() // 2, y - IMG.get_height() // 2))

        pygame.display.update()


##    def pos_scores(self):
##
##        if self.board_empty():
##            return {[(1, 1)]: 5,
##                    [(0, 0), (0, 2), (2, 0), (2, 2)]: 10,
##                    [(0, 1), (1, 0), (1, 2), (2, 1)]: 2
##                    }
##
##        else:
##            return {[(1, 1)]: 10,
##                    [(0, 0), (0, 2), (2, 0), (2, 2)]: 5,
##                    [(0, 1), (1, 0), (1, 2), (2, 1)]: 2
##                    }

    def board_empty(self):

        for row in self.game_board:
            for col in row:
                if col != 0:
                    return False

        return True

class Connect4Move(GameMove):

    def __init__(self, i, j, id_nr=None):

        self.pos_x = j
        self.pos_y = i
        self.id = id_nr

    def pos(self):
        return (self.pos_y, self.pos_x)

                
    
