# -*- coding: utf-8 -*-
# Game by ... you !
########
from include import CPlayer
from include import CGame

#

############
# Game Variables
############
GameOpts = {'max_round': '10'}
# Dictionary of stats and display order (For example : Points Per Darts and Avg are displayed in descending order)
GameRecords = {'Points Per Round': 'DESC', 'Points Per Dart': 'DESC'}
# How many darts per player and per round ? Yes ! this is a feature :)
nbdarts = 3  # Total darts the player has to play
# Background image - relative to images folder - Name it like the game itself
GameLogo = 'Sample_game.png'
# Columns headers - Better as a string
Headers = ["1", "2", "3", "4", "5", "6", "BULL"]

############
# Extend the basic player
############
class CPlayerExtended(CPlayer.CPlayer):
    def __init__(self, x, NbPlayers, Config, res):
        super(CPlayerExtended, self).__init__(x, NbPlayers, Config, res)
        # Extend the basic players property with your own here
        # Init Player Records to zero
        for GR in GameRecords:
            self.Stats[GR] = '0'


############
# Extend the common Game class
############
class Game(CGame.CGame):
    def __init__(self, myDisplay, GameChoice, nbplayers, GameOpts, Config, Logs):
        super(Game, self).__init__(myDisplay, GameChoice, nbplayers, GameOpts, Config, Logs)
        ##############
        # VAR
        ##############
        # Dictionary of options in STRING format.
        # You can use any numeric value or 'True' or 'False', but in string format.
        # Don't put more than 10 options per game or you will experience display issues
        self.GameOpts = GameOpts
        # Dictionary of stats and display order (For example : Points Per Darts and Avg are displayed in descending
        # order)
        self.GameRecords = GameRecords
        # How many darts per player and per round ? Yes ! this is a feature :)
        self.nbdarts = nbdarts  # Total darts the player has to play
        # Background image - relative to images folder - Name it like the game itself
        self.GameLogo = GameLogo
        # Columns headers - Better as a string
        self.Headers = Headers
        # self.ScoreMap.update({'SB':50})
        #  Get the maximum round number
        self.maxround = int(self.GameOpts['max_round'])

    ###############
    # Method to refresh Player Stats - Adapt to the stats you want.
    # They represent mathematical formulas used to calculate stats. Refreshed after every launch
    ###############
    def RefreshStats(self, Players, actualround):
        for P in Players:
            P.Stats['Points Per Round'] = P.AVG(actualround)
            P.Stats['Points Per Dart'] = P.ShowPPD()
