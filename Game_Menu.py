#First Game Menu -> Game Selection, Options

from Github import Backlog
import os
import pygame
import pygame_menu

class Games():
    """

    """
    
    def __init__(self):
        self.Logger = Backlog()
        self.Games = ["TicTacToe", "Connect4"]
        self.window = 


    def game_menu(self):
        """

        """

        self.Menu =

        for game in self.Games:
            self.Menu.add.button()

        self.Menu.add.button()
        self.Menu.add.button()

        self.Menu.mainloop(self.window)

    def options_menu(self):
        """

        """

        self.Options =

        self.Options.add.slider()
        self.Options.add.slider()
        self.Options.add.slider()
        self.Options.add.button()
        self.Options.add.button()

        self.Options.add.button()

        self.Options.mainloop(self.window)

    def credit_menu(self):
        """

        """

        self.Credits =

        self.Credits.add.label()
        self.Credits.add.label()
        self.Credits.add.url()

        self.Credits.add.button()

        self.Credits.mainloop(self.window)

    def help_menu(self):
        """

        """

        self.Help =

        self.Help.add.label()
        self.Help.add.label()
        self.Help.add.label()
        self.Help.add.label()
        self.Help.add.label()
        self.Help.add.label()

        self.Help.add.button()

        self.Help.mainloop(self.window)

    def start_game(self):
        """

        """

        game = __import__(self.Games[])
        run = Run_Game(game, NN, self.Logger)
        run.start_menu()

games = Games()
games.game_menu()
    
