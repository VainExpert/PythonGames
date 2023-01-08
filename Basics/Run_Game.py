#

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from Basics.Backlog import Backlog

from Basics.MCTS import *
from Basics.NeuralNet import NNWrapper, GameNN, GameTraining
from Games.TicTacToe import TicTacToe

import pygame
import pygame_menu



#---------------------------------------------------Run Game Class---------------------------------------------------
class Run_Games():
    """
    Player Selections:
    NN+MCTS: Strengths (easy, midd, hard, cust, best, deft) -> from MSCTS import MCTS_NN, MCTS_NN_Node -> best = MCTS_NN.search(); move = best.move
    Pure MCTS: Elo (1-7[s], 100, 500, 900, 1111, 2222, 3333) -> from MCTS import MCTS, MCTNode -> best = MCTS.search(); move = best.move

    AlphaBeta-MinMax: to implement
    Solo NN: to implement
    Q-Learner: to implement
    DeepLearner: to implement

    Random Player: random Move from avaible moves -> from Game import random_player -> move = Game.random_player()
    Human: -> from Game import click -> move = Game.click()
    Random Choice for Player out of Selection

    Select Idea:
    1. Select Type:
    NN+MCTS or Pure MCTS or Random or Human or Random Choice (or not implemented)
    2. Select Strength if NN+MCTS or Pure MCTS (or not implemented):
    Show Strength Options; Play-Button; Train-Button (if available) 
    """
    
    def __init__(self, game, NN, log):

        self.player1 = Player("Mensch", 2, 1)
        self.player2 = Player("Mensch", 2, 2)

        self.Draw = 0
        self.turns = 1
        self.avgturns = 0
        self.totalturns = []
        
        self.games = 0
        self.prev = 0

        self.gcls = game
        self.game = game()
        self.gamename = self.game.__class__.__name__
        self.game.init_grid()

        self.NN = NN(self.game, self.game.game_board)
        self.trainData = {1: [10, 50, "easy"], 2: [20, 100, "midd"], 3: [50, 1000, "hard"], 4: [0, 0, "cust"], 5: [50, 1000, "best"], 6: [25, 500, "deft"]}
        self.trainStrength = [10, 50, "easy"]
        self.trainType = 5
        self.trainStrengths = [('Best', 5), ('Custom', 4), ('Schwer', 3), ('Mittel', 2), ('Einfach', 1)]

        self.volume = 0.5
        self.button_sound = pygame.mixer.Sound("C:/Users/Tom/Documents/Coding/Code/GitHub/PythonGames/Games/Menu_Button.mp3")
        self.button_sound.set_volume(self.volume)
        self.played = pygame.mixer.Sound("C:/Users/Tom/Documents/Coding/Code/GitHub/PythonGames/Games/Move_Played.mp3")
        self.played.set_volume(self.volume)

        self.theme = pygame_menu.themes.THEME_BLUE
        self.Logger = log
        self.Logger.log("info", "Game init complete.")



#-------------------------------------------------------MENÜS-------------------------------------------------------
#-----------------------------------------------------Hauptmenü-----------------------------------------------------
    def start_menu(self):
        """
        Hauptmenü mit Zugriff auf Options-Menü und Spielmenü

        :button: Zur Spielerauswahl
        :button: Zum Optionsmenü
        :button save: sichert das Programm-Protokoll
        :button quit: beendet das Programm
        """

        pygame.mixer.Sound.play(self.button_sound)

        self.menu = pygame_menu.Menu("Willkommen bei {}!".format(self.gamename), height=self.game.height, width=self.game.width, theme=self.theme)

        self.menu.add.button("Spielen", self.select_player_menu)
        self.menu.add.button("Optionen", self.option_menu)
        
        self.save = self.menu.add.button('Ende', self.exit)
        self.save.show()
        self.quit = self.menu.add.button('Ende', pygame_menu.events.EXIT)
        self.quit.hide()

        self.check_resize()

        self.menu.mainloop(self.game.window)

#----------------------------------------------Options Menü----------------------------------------------
    def option_menu(self):
        """
        Options-Menü mit Zugriff auf das Bot-Training und die Programm-Credits

        :slider: Verändert Lautstärke der Sounds/Musik
        :slider: Verändert Fenstergröße
        :button: Training der Bots
        :button: Credit-Seite
        :button: Zurück zum Hauptmenü
        """

        pygame.mixer.Sound.play(self.button_sound)

        self.Logger.log("info", "Options Menu open.")
        self.OptionMenu = pygame_menu.Menu("Optionen", height=self.game.height, width=self.game.width, theme=self.theme)

        self.OptionMenu.add.range_slider(title="Musik:", default=self.volume, range_values=(0,1), increment=0.1, onchange=self.change_volume)
        self.OptionMenu.add.range_slider(title="Fenstergröße:", default=1, range_values=(0,2), increment=0.15, onchange=self.change_size)
        self.OptionMenu.add.selector("Window Theme:", [("Blau", pygame_menu.themes.THEME_BLUE),
                                                             ("Grau", pygame_menu.themes.THEME_DEFAULT),
                                                             ("Dunkel", pygame_menu.themes.THEME_DARK),
                                                             ("Grün", pygame_menu.themes.THEME_GREEN),
                                                             ("Orange", pygame_menu.themes.THEME_ORANGE),
                                                             ("Hell", pygame_menu.themes.THEME_SOLARIZED)], onchange=self.change_theme)
        self.OptionMenu.add.button("Bot-Training", self.gym_menu)
        self.OptionMenu.add.button("About", self.about_page)
        self.OptionMenu.add.button("Zurück", self.start_menu)

        self.check_resize()

        self.OptionMenu.mainloop(self.game.window)

#---------------------------------------Credits Menü---------------------------------------
    def about_page(self):
        """
        Credits mit Infos zum Programm

        :label: Author
        :label: Version/Release
        :url:
        :button:
        :button:
        
        TODO:
        Infos zu der Lizenz
        """

        pygame.mixer.Sound.play(self.button_sound)
        self.Logger.log("info", "About Menu open.")
        
        self.AboutMenu = pygame_menu.Menu("About", height=self.game.height, width=self.game.width, theme=self.theme)

        self.AboutMenu.add.label("Author: Tom \"VainExpert\" Maier")
        self.AboutMenu.add.label("Version 2.0, Release 2021")
        self.AboutMenu.add.url("https://github.com/VainExpert")
        self.AboutMenu.add.label(" ")        
        self.AboutMenu.add.label("Zum Beenden der Applikation Doppelklick\nauf den Ende-Button im Hauptmenü")

        self.AboutMenu.add.button("Bot-Beschreibungen", self.bot_menu)
        self.AboutMenu.add.button("Zurück", self.option_menu)

        self.check_resize()

        self.AboutMenu.mainloop(self.game.window)

    def bot_menu(self):
        """

        """

        pygame.mixer.Sound.play(self.button_sound)
        self.Logger.log("info", "Bot Description open.")
        
        self.BotMenu = pygame_menu.Menu("Bots", height=self.game.height, width=self.game.width, theme=self.theme)

        self.aife1 = self.BotMenu.add.label("A.I.F.E. - AI For Everything")
        self.aife2 = self.BotMenu.add.label("Basiert auf dem Prinzip von AlphaZero\nVerwendet Neuronale Netze und\nmit Monte Carlo Tree Search\num den besten Zug zu finden.")

        self.adam1 = self.BotMenu.add.label("\nA.D.A.M. - All Dumb Actions Made")
        self.adam2 = self.BotMenu.add.label("Nutzt reine Monte Carlo Tree Search\num den besten Zug zu finden")
        
        self.randy1 = self.BotMenu.add.label("\nRandom")
        self.randy2 = self.BotMenu.add.label("Spielt einen zufälligen möglichen Spielzug")

        self.BotMenu.add.button("Zurück", self.about_page)
            
        self.BotMenu.mainloop(self.game.window)


#--------------------------------------Bot Training Auswahl Menü--------------------------------------
    def gym_menu(self):
        """

        """

        pygame.mixer.Sound.play(self.button_sound)
        self.Logger.log("info", "Bot Gym open.")

        self.Gym = pygame_menu.Menu("Trainingshalle", height=self.game.height, width=self.game.width, theme=pygame_menu.themes.THEME_BLUE)

        self.Gym.add.label("Bot Training")
        self.Gym.add.selector("Bot Type: ", [("A.I.F.E", 5)], onchange=self.change_train_type)
        self.Gym.add.selector("Strength: ", self.trainStrengths, onchange=self.change_train_strength)
        
        self.Gym.add.button("Train", self.trainBot)
        self.Gym.add.button("Zurück", self.option_menu)

        self.check_resize()

        self.Gym.mainloop(self.game.window)

#-----------------------------------------Bot Training Menü-----------------------------------------
    def trainBot(self):
        """
        TODO:
        train as backend
        """

        pygame.mixer.Sound.play(self.button_sound)
        self.Logger.log("info", "Bot Training open.")

        self.Training = pygame_menu.Menu("Training", height=self.game.height, width=self.game.width, theme=self.theme)

        self.Training.add.label("A.I.F.E. der Schwierigkeit {}".format(self.trainStrength[2]))
        self.bar = self.Training.add.progress_bar(" ", width=self.game.width - 50, default=0)
        self.Training.add.button("Starte Training", self.train)
        
        if self.prev == 0:
            self.back = self.Training.add.button("Zurück", self.gym_menu)
            self.back.hide()

        else:
            self.back = self.Training.add.button("Zurück", self.next_menu)
            self.back.hide()
                
        self.check_resize()

        self.Training.mainloop(self.game.window)
            
#----------------------------------------------Spieler Auswahl Menü----------------------------------------------
    def select_player_menu(self):
        """


        """

        pygame.mixer.Sound.play(self.button_sound)
        self.Logger.log("info", "Player Selection open.")

        self.SelectMenu = pygame_menu.Menu(columns=3, rows=3, title="Spieler Auswahl", height=self.game.width, width=self.game.width, theme=self.theme)

        self.SelectMenu.add.label("Spieler 1:")
        self.p1img = self.SelectMenu.add.image("C:/Users/Tom/Documents/Coding/Code/GitHub/PythonGames/Games/Mensch.png")
        self.SelectMenu.add.selector(" ", [('Mensch' , 2, None),
                                           ('A.I.F.E.', 5, [('Einfach', 1), ('Mittel', 2), ('Schwer', 3), ('Custom', 4), ('Best', 5)]),
                                           ('A.D.A.M.', 4, [("Einfach", 1), ("Mittel", 4), ('Schwer', 7),
                                                           ("Einfach", 100), ("Mittel", 500), ('Schwer', 1000),
                                                           ("Einfach", 1500), ("Mittel", 2000), ('Schwer', 3000)]),
                                           ('Random', 3, None),
                                           ('Zufallsauswahl', 1, None)],
                                     onchange=self.set_player1)

        self.SelectMenu.add.label(" ")
        self.SelectMenu.add.button('Weiter', self.next_menu)
        self.SelectMenu.add.button('Zurück', self.start_menu)

        self.SelectMenu.add.label("Spieler 2:")
        self.p2img = self.SelectMenu.add.image("C:/Users/Tom/Documents/Coding/Code/GitHub/PythonGames/Games/Mensch.png")
        self.SelectMenu.add.selector(" ", [('Mensch' , 2, None),
                                           ('A.I.F.E.', 5, [('Einfach', 1), ('Mittel', 2), ('Schwer', 3), ('Custom', 4), ('Best', 5)]),
                                           ('A.D.A.M.', 4, [("Einfach", 1), ("Mittel", 4), ('Schwer', 7),
                                                           ("Einfach", 100), ("Mittel", 500), ('Schwer', 1000),
                                                           ("Einfach", 1500), ("Mittel", 2000), ('Schwer', 3000)]),
                                           ('Random', 3, None),
                                           ('Zufallsauswahl', 1, None)],
                                     onchange=self.set_player2)

        self.check_resize()

        self.SelectMenu.mainloop(self.game.window)            


#-----------------------------------------------Spieler Prüfung Menü-----------------------------------------------
    def next_menu(self):
        """

        
        """

        pygame.mixer.Sound.play(self.button_sound)
        self.Logger.log("info", "Player Check open.")

        self.set_random()


        if self.player1.type >= 5 or self.player2.type >= 5:
               self.prev = 1
               self.NextMenu = pygame_menu.Menu(columns=3, rows=5, title="Spieler prüfen", height=self.game.height, width=self.game.width, theme=self.theme)
        
        else:
            
            if self.player1.type == 4 or self.player2.type == 4:
               self.NextMenu = pygame_menu.Menu(columns=3, rows=4, title="Spieler prüfen", height=self.game.height, width=self.game.width, theme=self.theme)

            else:
               self.NextMenu = pygame_menu.Menu(columns=3, rows=3, title="Spieler prüfen", height=self.game.height, width=self.game.width, theme=self.theme)
        
        self.NextMenu.add.label("Spieler 1:")
        self.NextMenu.add.image(self.player1.img)
        self.NextMenu.add.label(self.player1.name)
        
        if self.player1.type >= 4:
           self.NextMenu.add.selector("Stärke: ", self.player1.strengths, onchange=self.set_strength1)
           
        if self.player1.type >= 5:
           self.NextMenu.add.button('Train', self.trainBot)

        if self.player2.type >= 5 and self.player1.type == 4:
            elf.NextMenu.add.label(" ")

        if self.player2.type >= 5 and self.player1.type < 4:
            self.NextMenu.add.label(" ")
            self.NextMenu.add.label(" ")

        if self.player2.type == 4 and self.player1.type < 4:
            self.NextMenu.add.label(" ")
        
        self.NextMenu.add.label(" ")
        self.NextMenu.add.button('Start', self.play)
        self.NextMenu.add.button('Zurück', self.select_player_menu)
        
        if self.player1.type == 4 or self.player2.type == 4 or self.player1.type >= 5 or self.player2.type >= 5:
           self.NextMenu.add.label(" ")

        if self.player1.type >= 5 or self.player2.type >= 5:
           self.NextMenu.add.label(" ")
        
        self.NextMenu.add.label("Spieler 2:")
        self.NextMenu.add.image(self.player2.img)
        self.NextMenu.add.label(self.player2.name)

        if self.player2.type >= 4:
           self.NextMenu.add.selector("Stärke: ", self.player2.strengths, onchange=self.set_strength1)
        
        if self.player2.type >= 5:
           self.NextMenu.add.button('Train', self.trainBot)

        self.check_resize()

        self.NextMenu.mainloop(self.game.window)


#-------------------------------------------------------Play-------------------------------------------------------
    def play(self):
        """


        """

        pygame.mixer.Sound.play(self.button_sound)
        self.Logger.log("info", "{} Start Game:".format(self.gamename))

        game = self.gcls(width=self.game.width, height=self.game.height)
        game.title_message("{}   -   Start Game".format(self.gamename))
        
        Sampler = GameTraining("game-{}".format(self.games), 0, 0, game, self.NN)
        self.games += 1
        trainGame = []
        trainTurn = []

        run = True
        check1 = False
        check2 = False

        while run:

            game.render()
            
            if game.player == 0:

                if not check1:
                    self.Logger.log("info", "{}: {} Turn".format(self.turns, game.player_sym))
                    game.title_message("{}   -   {}: {}-{} Turn".format(self.gamename, self.turns, self.player1.name, game.player_sym))
                    check1 = True
                    self.turns += 1

                preboard = copy.deepcopy(game.game_board)
                pplayer = copy.deepcopy(game.player)
                moves = game.all_possible_moves(game.game_board)

                if self.player1.type == 2:
                    for event in pygame.event.get():
                        
                        if event.type == pygame.QUIT:
                            self.Logger.save()
                            pygame.quit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                self.Logger.save()
                                pygame.quit()   

                        if event.type == pygame.MOUSEBUTTONDOWN:

                            move = game.click()

                            if move is None:
                                continue

                            probs = []
                            for all_move in moves:
                                if all_move.pos_x == move.pos_x and all_move.pos_y == move.pos_y:
                                    probs.append(1.0)
                                else:
                                    probs.append(0)

                            self.Logger.log("info", self.get_stats(preboard, pplayer, probs))
                            trainTurn.append([preboard, pplayer, (-1.0) ** pplayer, moves, probs])
                            pygame.mixer.Sound.play(self.played)

                            check2 = False

                        if event.type == pygame.VIDEORESIZE:
                            self.game.width = event.w
                            self.game.height = event.h
                            self.game.window = pygame.display.set_mode((event.w, event.h),
                                              pygame.RESIZABLE)

                elif self.player1.type == 3:

                    move = game.random_player()
                    game.pc_move(move)

                    probs = []
                    for all_move in moves:
                        if all_move.pos_x == move.pos_x and all_move.pos_y == move.pos_y:
                            probs.append(1.0)
                        else:
                            probs.append(0)

                    self.Logger.log("info", self.get_stats(preboard, pplayer, moves, probs))
                    trainTurn.append([preboard, pplayer, (-1.0) ** pplayer, probs])
                    pygame.mixer.Sound.play(self.played)

                    check2 = False

                elif self.player1.type == 4:

                    root = MCTNode(game.game_state(game.game_board, 0), game.game_board, 0, game)
                    best = self.player1.bot.search(root)
                    game.pc_move(best.action)
                    self.Logger.log("info", root.printStats())

                    trainTurn.append([preboard, 0, root.future_result, root.probs])
                    pygame.mixer.Sound.play(self.played)

                    check2 = False
                    
                elif self.player1.type == 5:
                    
                    root = MCTS_NN_Node(game, self.NN, game.game_board, game.game_state(game.game_board, 0), 0)
                    action = self.player1.bot.search(root)
                    game.pc_move(action)
                    self.Logger.log("info", root.printStats())

                    trainTurn.append([preboard, 0, root.future_result, root.probs])
                    pygame.mixer.Sound.play(self.played)
                    
                    check2 = False

            game.render()

            result = game.game_result()
            if result[0] is not False:
                res = []
                
                if result[0] == 0.5:
                    self.Logger.log("info", "Unentschieden")
                    game.title_message("{}   -   Unentschieden".format(self.gamename))

                    res.append("Unentschieden")
                    self.Draw += 1
                    
                elif result[0] == 1:
                    self.Logger.log("info", "Spieler 1 - {} - {} hat gewonnen".format(self.player1.name, result[1]))
                    game.title_message("{}   -   Spieler 1 - {} - {} hat gewonnen".format(self.gamename, self.player1.name, result[1]))

                    res.append("{}: ".format(result[1]) + self.player1.win_screen())
                    self.player1.wins += 1
                    
                elif result[0] == -1:
                    self.Logger.log("info", "Spieler 2 - {} - {} hat gewonnen".format(self.player2.name, result[1]))
                    game.title_message("{}   -  Spieler 2 - {} - {} hat gewonnen".format(self.gamename, self.player2.name, result[1]))

                    res.append("{}: ".format(result[1]) + self.player2.win_screen())
                    self.player2.wins += 1

                self.totalturns.append(self.turns-1)
                self.turns = 1

                trainGame = [(x[0], x[2], x[3]) for x in trainTurn]
                Sampler.writeExamples(trainGame)

                self.continue_menu(res)

            if game.player == 1:

                if not check2:
                    self.Logger.log("info", "{}: {} Turn".format(self.turns, game.player_sym))
                    game.title_message("{}   -   {}: {}-{} Turn".format(self.gamename, self.turns, self.player2.name, game.player_sym))
                    check2 = True
                    self.turns += 1

                preboard = copy.deepcopy(game.game_board)
                pplayer = copy.deepcopy(game.player)
                moves = game.all_possible_moves(game.game_board)

                if self.player2.type == 2:
                    for event in pygame.event.get():
                        
                        if event.type == pygame.QUIT:
                            self.Logger.save()
                            pygame.quit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                self.Logger.save()
                                pygame.quit()                        

                        if event.type == pygame.MOUSEBUTTONDOWN:
                    
                            move = game.click()

                            if move is None:
                                continue

                            probs = []
                            for all_move in moves:
                                if all_move.pos_x == move.pos_x and all_move.pos_y == move.pos_y:
                                    probs.append(1.0)
                                else:
                                    probs.append(0)

                            self.Logger.log("info", self.get_stats(preboard, pplayer, moves, probs))
                            trainTurn.append([preboard, pplayer, (-1.0) ** pplayer, probs])
                            pygame.mixer.Sound.play(self.played)

                            check1 = False

                        if event.type == pygame.VIDEORESIZE:
                            self.game.width = event.w
                            self.game.height = event.h
                            self.game.window = pygame.display.set_mode((event.w, event.h),
                                              pygame.RESIZABLE)


                elif self.player2.type == 3:

                    move = game.random_player()
                    game.pc_move(move)

                    probs = []
                    for all_move in moves:
                        if all_move.pos_x == move.pos_x and all_move.pos_y == move.pos_y:
                            probs.append(1.0)
                        else:
                            probs.append(0)

                    self.Logger.log("info", self.get_stats(preboard, pplayer, moves, probs))
                    trainTurn.append([preboard, pplayer, (-1.0) ** pplayer, probs])
                    pygame.mixer.Sound.play(self.played)

                    check1 = False

                elif self.player2.type == 4:

                    root = MCTNode(game.game_state(game.game_board, 1), game.game_board, 1, game)
                    best = self.player2.bot.search(root)
                    game.pc_move(best.action)
                    self.Logger.log("info", root.printStats())

                    trainTurn.append([preboard, 1, root.future_result, root.probs])
                    pygame.mixer.Sound.play(self.played)

                    check1 = False

                elif self.player2.type == 5:
                    
                    root = MCTS_NN_Node(game, self.NN, game.game_board, game.game_state(game.game_board, 1), 1)
                    action = self.player2.bot.search(root)
                    game.pc_move(action)
                    self.Logger.log("info", root.printStats())

                    trainTurn.append([preboard, 1, root.future_result, root.probs])
                    pygame.mixer.Sound.play(self.played)

                    check1 = False

            game.render()

            result = game.game_result()
            if result[0] is not False:
                res = []
                
                if result[0] == 0.5:
                    self.Logger.log("info", "Unentschieden")
                    game.title_message("{}   -   Unentschieden".format(self.gamename))

                    res.append("Unentschieden")
                    self.Draw += 1
                    
                elif result[0] == 1:
                    self.Logger.log("info", "Spieler 1 - {} - {} hat gewonnen".format(self.player1.name, result[1]))
                    game.title_message("{}   -   Spieler 1 - {} - {} hat gewonnen".format(self.gamename, self.player1.name, result[1]))

                    res.append("{}: ".format(result[1]) + self.player1.win_screen())
                    self.player1.wins += 1
                    
                elif result[0] == -1:
                    self.Logger.log("info", "Spieler 2 - {} - {} hat gewonnen".format(self.player2.name, result[1]))
                    game.title_message("{}   -  Spieler 2 - {} - {} hat gewonnen".format(self.gamename, self.player2.name, result[1]))

                    res.append("{}: ".format(result[1]) + self.player2.win_screen())
                    self.player2.wins += 1

                self.totalturns.append(self.turns-1)
                self.turns = 1

                trainGame = [(x[0], x[2], x[3]) for x in trainTurn]
                Sampler.writeExamples(trainGame)

                self.continue_menu(res)


#--------------------------------------------After Play--------------------------------------------
#---------------------------Erneut Menü---------------------------
    def continue_menu(self, result):
        """
        
        """
        
        self.Logger.log("info", "Game Ende Menu open.")
        self.conMenu = pygame_menu.Menu("Weiterspielen?", height=self.game.height, width=self.game.width, theme=self.theme)

        for line in result:
            self.conMenu.add.label("{}".format(line))
        
        self.conMenu.add.button("Nochmal", self.play)
        self.conMenu.add.button("Fertig", self.result_menu)

        self.check_resize()

        self.conMenu.mainloop(self.game.window)

#---------------------------Ergebnis Menü--------------------------
    def result_menu(self):
        """


        """

        pygame.mixer.Sound.play(self.button_sound)
        self.Logger.log("info", "Result Menu open.")

        self.results()
        self.resMenu = pygame_menu.Menu("Resultate", height=self.game.height, width=self.game.width, theme=self.theme)

        self.resMenu.add.label(self.player1.format_wins())
        self.resMenu.add.label(self.player2.format_wins())

        self.resMenu.add.label("Unentschieden: {}".format(self.Draw))
        self.resMenu.add.label("Durchschnittliche Züge: {}".format(self.average()))

        self.resMenu.add.button("Zum Hauptmenü", self.reset_vals)

        self.check_resize()

        self.resMenu.mainloop(self.game.window)


#------------------------------------------------UTILITIES---------------------------------------
#-----------------------Button Functions-----------------------
    def exit(self):
        """


        """

        pygame.mixer.Sound.play(self.button_sound)

        self.Logger.save()
        self.save.hide()
        self.quit.show()

    def train(self):
        """

        """

        self.Logger.log("info", "Bot Training started.")
        self.Training.render()

        eps, sims, strengthName = self.trainStrength
        Trainer = GameTraining(strengthName, eps, sims, self.game, self.NN)
        self.Logger.subtitle("Train {} Bot".format(strengthName))

        self.Training.render()

        self.Logger.log("info", "Creating examples.")
        self.bar.set_title("Creating examples")

        self.bar.render()
        self.Training.render()

        if strengthName == "cust":
            self.bar.set_value(15)
            self.bar.render()
            self.Training.render()
            
            Trainer.customExamples()

        elif strengthName == "best":
            self.bar.set_value(20)
            self.bar.render()
            self.Training.render()
            
            Trainer.solvedExamples()

        else:
            self.bar.set_value(8)
            self.bar.render()
            self.Training.render()
            
            Trainer.createExamples()

        self.bar.set_value(35)
        self.bar.render()
        self.Training.render()

        self.Logger.log("info", "Training Model with created examples.")
        self.bar.set_title("Training Model")

        self.bar.render()
        self.Training.render()
        
        Trainer.trainNN()
        self.NN.save_checkpoint(folder="{}/models".format(self.gamename), filename="{}.pth.tar".format(strengthName))

        self.bar.set_value(65)
        self.bar.render()
        self.Training.render()

        self.Logger.log("info", "Testing Model.")
        self.bar.set_title("Testing Model")

        self.bar.render()
        self.Training.render()
        
        optimize = Trainer.testNN()

        if not optimize:
            self.bar.set_value(100)
            self.bar.render()
            self.back.show()
            self.Training.render()

        else:
            self.bar.set_value(75)
            self.bar.render()
            self.Training.render()

            while optimize:
                self.Logger.log("info", "Optimizing Model.")
                self.bar.set_title("Optimizing Model")

                self.bar.render()
                self.Training.render()
                
                Trainer.optimizeNN()

                self.Logger.log("info", "Testing Model.")
                self.bar.set_title("Testing Model")

                self.bar.render()
                self.Training.render()
                
                optimize = Trainer.testNN()

            self.bar.set_value(100)
            self.bar.render()
            self.back.show()
            self.Training.render()

        self.Logger.log("info", "Trainnig done.")
        self.bar.render()
        self.Training.render()


#--------------------------------------------Selector Functions--------------------------------------------
    def change_train_type(self, selected_value, number, **kwargs):
        """

        """

        pygame.mixer.Sound.play(self.button_sound)

        self.trainStrengths = [('Best', 5), ('Custom', 4), ('Schwer', 3), ('Mittel', 2), ('Einfach', 1)]
        self.trainType = 5

    def change_train_strength(self, selected_value, number, **kwargs):
        """

        """

        pygame.mixer.Sound.play(self.button_sound)
        self.Logger.log("info", "Train Strength changed from {} to {}.".format(self.trainStrength, self.trainData[number]))
        
        self.trainStrength = self.trainData[number]


#--------------------------------------------Slider Functions--------------------------------------------
    def change_volume(self, range_value, **kwargs):
        """

        """

        self.Logger.log("info", "Volume changed from {} to {}.".format(self.volume, range_value))

        self.volume = range_value
        self.played.set_volume(range_value)
        self.button_sound.set_volume(range_value)

    def change_size(self, range_value, **kwargs):
        """

        """
        self.Logger.log("info", "Width changed from {} to {}.".format(self.game.width, int(self.game.width * range_value)))
        self.Logger.log("info", "Height changed from {} to {}.".format(self.game.height,  int(self.game.height * range_value)))

        self.game.width = int(self.game.width * range_value)
        self.game.height = int(self.game.height * range_value)

        self.game.window = pygame.display.set_mode((self.game.width, self.game.height),
                                              pygame.RESIZABLE)
        self.NN = self.NN.__class__(self.game, self.game.game_board)

    def change_theme(self, color, changed_value, **kwargs):
        """

        """
        
        self.Logger.log("info", "Theme changed from {} to {}.".format(self.theme, changed_value))
        self.theme = changed_value

        self.OptionMenu = pygame_menu.Menu("Optionen", height=self.game.height, width=self.game.width, theme=self.theme)
        self.OptionMenu.draw(self.game.window)
        self.OptionMenu.render()
        
    def check_resize(self):
        """

        """
        for event in pygame.event.get():   

            if event.type == pygame.QUIT:
                self.Logger.save()
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.Logger.save()
                    pygame.quit()   

            if event.type == pygame.VIDEORESIZE:
                    self.game.width = event.w
                    self.game.height = event.h
                    self.game.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.NN = self.NN.__class__(self.game, self.game.game_board)


#--------------------------------------------Player Detail Setters--------------------------------------------
    def set_player1(self, selected_value, number, settings, **kwargs):
        """
        
        """

        pygame.mixer.Sound.play(self.button_sound)
        
        if number == 1:
            players = ["Mensch", "Random", "A.D.A.M.", "A.I.F.E."]
            name = random.choice(players)
            status = players.index(name) + 2
            
            if status == 4:
                settings = [("Einfach", 1), ("Mittel", 4), ('Schwer', 7),
                            ("Einfach", 100), ("Mittel", 500), ('Schwer', 1000),
                            ("Einfach", 1500), ("Mittel", 2000), ('Schwer', 3000)]

            if status == 5:
                settings = [('Einfach', 1), ('Mittel', 2), ('Schwer', 3), ('Custom', 4), ('Best', 5)]

            status = str(status) + str(1)

        else:
            name = selected_value[0][0]
            status = number

        NN = None
        elo = [None, None, None]
        if number == 5:
            elo = self.trainData[settings[0][1]]
            self.NN.load_checkpoint("{}/models".format(self.gamename), "{}.pth.tar".format(elo[2]))
            NN = self.NN

        self.Logger.log("info", "Player 1 changed from {} to {}.".format(self.player1.name, name))
        self.player1 = Player(name, status, 1, NN, elo[2], settings)

        if number == 1:
            self.player1.img = "C:/Users/Tom/Documents/Coding/Code/GitHub/PythonGames/Games/zufall.png"

        self.p1img.set_image(pygame_menu.baseimage.BaseImage(self.player1.img))    

    def set_player2(self, selected_value, number, settings, **kwargs):
        """

        """

        pygame.mixer.Sound.play(self.button_sound)
        
        if number == 1:
            
            players = ["Mensch", "Random", "A.D.A.M.", "A.I.F.E."]
            name = random.choice(players)
            status = players.index(name) + 2

            if status == 4:
                settings = [("Einfach", 1), ("Mittel", 4), ('Schwer', 7),
                            ("Einfach", 100), ("Mittel", 500), ('Schwer', 1000),
                            ("Einfach", 1500), ("Mittel", 2000), ('Schwer', 3000)]

            if status == 5:
                settings = [('Einfach', 1), ('Mittel', 2), ('Schwer', 3), ('Custom', 4), ('Best', 5)]

            status = str(status) + str(1)

        else:
            name = selected_value[0][0]
            status = number

        NN = None
        elo = [None, None, None]
        if number == 5:
            elo = self.trainData[settings[0][1]]
            self.NN.load_checkpoint("{}/models".format(self.gamename), "{}.pth.tar".format(elo[2]))
            NN = self.NN

        self.Logger.log("info", "Player 2 changed from {} to {}.".format(self.player2.name, name))
        self.player2 = Player(name, status, 2, NN, elo[2], settings)

        if number == 1:
            self.player2.img = "C:/Users/Tom/Documents/Coding/Code/GitHub/PythonGames/Games/zufall.png"

        self.p2img.set_image(pygame_menu.baseimage.BaseImage(self.player2.img))


    def set_strength1(self, selected_value, strength, **kwargs):
        """

        """

        pygame.mixer.Sound.play(self.button_sound)

        if self.player1.type == 4:
            self.Logger.log("info", "Player 1 Strength set to {}.".format(strength))
            if strength < 8:
                self.player1.set_bot(simTime=strength)

            else:
                self.player1.set_bot(simNum=strength)

        else:
            elo = self.trainData[strength]
            self.trainStrength = elo
            self.Logger.log("info", "Player 1 Strength set to {}.".format(elo[2]))
            self.NN.load_checkpoint("{}/models".format(self.gamename), "{}.pth.tar".format(elo[2]))
            self.player1.set_bot(NN=self.NN, elo=elo[2])

    def set_strength2(self, selected_value, strength, **kwargs):
        """
        
        """

        pygame.mixer.Sound.play(self.button_sound)
        
        if self.player2.type == 4:
            self.Logger.log("info", "Player 2 Strength set to {}.".format(strength))
            if strength < 8:
                self.player2.set_bot(simTime=strength)

            else:
                self.player2.set_bot(simNum=strength)

        else:
            elo = self.trainData[strength]
            self.trainStrength = elo
            self.Logger.log("info", "Player 2 Strength set to {}.".format(elo[2]))
            self.NN.load_checkpoint("{}/models".format(self.gamename), "{}.pth.tar".format(elo[2]))
            self.player2.set_bot(NN=self.NN, elo=elo[2])

    def set_random(self):
        """

        """

        if type(self.player1.type) is str:
            self.player1.type = int(self.player1.type[0])
            self.player1.img = "C:/Users/Tom/Documents/Coding/Code/GitHub/PythonGames/Games/{}.png".format(self.player1.name)
            self.Logger.log("info", "Player 1 from Random to {}.".format(self.player1.name))

        if type(self.player2.type) is str:
            self.player2.type = int(self.player2.type[0])
            self.player2.img = "C:/Users/Tom/Documents/Coding/Code/GitHub/PythonGames/Games/{}.png".format(self.player2.name)
            self.Logger.log("info", "Player 2 from Random to {}.".format(self.player2.name))


#-----------------------------Result Analyse/Output-----------------------------
    def get_stats(self, board, player, moves, probs):
        """

        """

        output = ""
        output += "Player " + str(player) + "\n"

        result = [0.5, (-1) ** player]
        res = random.choice(result)
        output += "Future Result:" + str(res) + "\n"

        for row in board:
            output += str(row) + "\n"

        for i in range(len(moves)):
            output += "Probability:" + str(prob[i]) + "Move:" + str(moves[i].pos) + "\n"
    
        return output    



    def results(self):
        """

        """
        
        self.Logger.log("info", "Results: ")
        
        self.Logger.log("info", self.player1.format_wins())
        self.Logger.log("info", self.player2.format_wins())
            
        self.Logger.log("info", "Draws: {}".format(self.Draw))
        self.Logger.log("info", "Average Turns: {}".format(self.average()))

    def reset_vals(self):
        """

        """

        pygame.mixer.Sound.play(self.button_sound)
        self.Logger.log("info", "Game Values reset.")

        self.player1 = Player("Mensch", 2, 1)
        self.player2 = Player("Mensch", 2, 2)
        self.prev = 0

        self.Draw = 0
        self.turns = 1
        self.avgturns = 0
        self.totalturns = []

        self.start_menu()

    def average(self):
        """

        """
        
        return round((sum(self.totalturns) / len(self.totalturns)), 2)



#----------------------------------------------------Player Class----------------------------------------------------
class Player():
    """

    """

    def __init__(self, name, status, num, NN=None, elo=None, strengths=None):
        self.name = name
        self.type = status
        self.num = num
        self.wins = 0
        self.strengths = strengths
        self.img = "C:/Users/Tom/Documents/Coding/Code/GitHub/PythonGames/Games/{}.png".format(name)

        if self.type == 4:
            self.strength = 1
            self.bot = MCTS(self.num-1, sim_time=self.strength)

        if self.type == 5:
            self.strength = elo
            self.bot = MCTS_NN(NN, self.num-1, mode="play")

    def set_bot(self, NN=None, elo=None, simNum=None, simTime=None):
        """

        """
        
        if simNum is not None or simTime is not None:
            if simNum is not None:
                self.strength = simNum
            else:
                self.strength = simTime
            
            self.bot = MCTS(self.num-1, simNum, simTime)

        if NN is not None:
            self.strength = elo
            self.bot = MCTS_NN(NN, self.num-1, mode="play")

    def win_screen(self):
        """

        """

        if self.name == "Mensch":
            return "Spieler {} hat gewonnen!".format(self.num)

        elif self.strengths is None:
            return "Spieler {} - {} hat gewonnen!".format(self.num, self.name)

        else:
            return "Spieler {} - {}-{} hat gewonnen!".format(self.num, self.name, self.strength, self.wins)
        

    def format_wins(self):
        """

        """

        if self.name == "Mensch":
            return "Spieler {} Siege: {}".format(self.num, self.wins)

        elif self.strengths is None:
            return "Spieler {} - {} Siege: {}".format(self.num, self.name, self.wins)

        else:
            return "Spieler {} - {}-{} Siege: {}".format(self.num, self.name, self.strength, self.wins)



#"Main"
log = Backlog("TicTacToe")
run = Run_Games(TicTacToe, NNWrapper, log)
run.start_menu()
