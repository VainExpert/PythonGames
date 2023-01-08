#Basic Game Skeleton

import pygame
import math
import random
import numpy as np


class GameUtils():
    
    #TODO:
    #     Dirs for gamespecific files (Pics, Icons, NN-Models, Example-Games)
    #     Logging (Log Class with .txt-Files as Logs, deleted when Program restarted)
    #	  Another Type of Search -> MinMax -> Bot-Options in Game_Menu
    #Refactor: PEP8-Standards, Code weniger redundant (imports einschraenken, often used functions, ...)

    def __init__(self, WIDTH, HEIGHT, ROWS, COLS):

        self.width = WIDTH
        self.height = HEIGHT

        pygame.init()

        self.window = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.font_size = int(self.width // 10)
        self.FONT = pygame.font.SysFont('courier', self.font_size)

        self.rows = ROWS
        self.cols = COLS

        self.dist_to_cen = self.width // self.rows // 2

        self.game_board = None
        self.coord_set = {}
        self.imgs = []

        self.Colors = {'WHITE':(255, 255, 255), 'BLACK':(0, 0, 0), 'GRAY': (200, 200, 200),
                       'RED': (255, 0, 0), 'BLUE': (0, 0, 255)}
        

    def draw_grid(self):

        gap_size = self.width // self.rows

        for i in range(self.rows):
            x = i * gap_size

            pygame.draw.line(self.window, self.Colors['GRAY'], (x, 0), (x, self.width), 5)
            pygame.draw.line(self.window, self.Colors['GRAY'], (0, x), (self.width, x), 5)


    def init_grid(self):

        self.game_board = np.zeros((self.cols, self.rows))

        coords = {}
        idx = 0
        for i in range(self.rows):
            for j in range(self.cols):
                x = self.transform_coords(j)
                y = self.transform_coords(i)

                coords.update({str(idx): [x, y]})
                idx += 1

        self.coord_set.update(coords)

    def transform_coords(self, idx):
        return self.dist_to_cen * (2 * idx + 1)
                      
    def display_message(self, content):

        pygame.time.delay(500)
        self.window.fill(self.Colors['WHITE'])
        text = self.FONT.render(content, 1, self.Colors['BLACK'])
        self.window.blit(text, ((self.width - text.get_width()) // 2, (self.width - text.get_height()) // 2))
        pygame.display.update()
        pygame.time.delay(3000)

    def change_icon(self, icon):

        pygame.display.set_icon(icon)

    def title_message(self, message):

        pygame.display.set_caption(message)

    def random_player(self):

        possible_moves = self.all_possible_moves(self.game_board)
        return random.choice(possible_moves)

    @classmethod
    def get_player_num(cls, player):
        pass

    def rand_start(self):
        pass

    def change_player(self):
        pass

    def simulate_move(self, move, board, player, rootplayer):
        pass

    def pc_move(self, move):
        pass

    @classmethod
    def all_possible_moves(cls, board):
        pass

    def render(self):
        pass

    def click(self):
        pass

    def game_state(self, board, rootplayer):
        pass

    def game_result(self):
        pass



class GameMove():
    pass
