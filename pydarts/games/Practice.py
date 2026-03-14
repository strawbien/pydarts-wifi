# -*- coding: utf-8 -*-
# Game by ... Poilou !
########
from include import CPlayer
from include import CGame
from include import CScores
import collections# To use OrderedDict to sort players from the last score they add
from copy import deepcopy# For backupTurn
import random# To choose wich hit to play

GameLogo = 'Practice.png' # Background image - relative to images folder
Headers = [ "Try","-","-","-","-","-","-"] # Columns headers - Must be a string
GameOpts = {'max_round':'10','master':'False'} # Dictionnay of options in string format
GameRecords = {'Hits per round':'DESC', 'MPR':'DESC'} # Dictionnary of stats (For exemple, Avg is displayed in descending order)
nbdarts=3

############
#Extend the basic player
############
class CPlayerExtended(CPlayer.CPlayer):
   def __init__(self,x,NbPlayers,Config,res):
      super(CPlayerExtended, self).__init__(x,NbPlayers,Config,res)
      # Read the CJoueur class parameters, and add here yours if needed
      # Init all the Game stats
      for GR in GameRecords:
         self.Stats[GR]='0'

############
# Your Game's Class
############
class Game(CGame.CGame):
   def __init__(self,myDisplay,GameChoice,nbplayers,GameOpts,Config,Logs):
      super(Game, self).__init__(myDisplay, GameChoice, nbplayers, GameOpts, Config, Logs)
      # GameRecords is a descriptive dictionnary of stats to display at the end of a game
      self.GameRecords=GameRecords
      # Local data
      self.GameLogo = GameLogo
      self.Headers = Headers
      self.nbdarts=nbdarts # Total darts the player has to play
      #  Get the maxiumum round number
      self.maxround=self.GameOpts['max_round']
      

###############
# Actions done before each dart throw - for example, check if the player is allowed to play
   def PreDartsChecks(self,LSTPlayers,actualround,actualplayer,playerlaunch):
      return_code = 0
      # TxtRecap Can be used to create a per-player debug output
      if playerlaunch == 1 and actualplayer == 0 and actualround == 1:
         self.myDisplay.PlaySound('practice_intro')
      # You will probably save the turn to be used in case of backup turn (each first launch) :
      if playerlaunch==1 :
         self.SaveTurn(LSTPlayers)
         rand = random.randint(1,22)
         if rand==21 and self.GameOpts['master']=='True':
            rand='SB'
         elif rand==22 and self.GameOpts['master']=='True':
            rand='DB'
         elif (rand==21 or rand==22) and self.GameOpts['master']=='False':
            rand='B'
         elif self.GameOpts['master']=='False':
            rand='{}'.format(rand)
         elif self.GameOpts['master']=='True':
            randMultiple=random.randint(1,3)
            if randMultiple == 1:
               rand='S{}'.format(rand)
            elif randMultiple == 2:
               rand='D{}'.format(rand)
            elif randMultiple == 3:
               rand='T{}'.format(rand)
         if self.RandomIsFromNet == False:
            # Clean table of any previousinformation
            for Column,Value in enumerate(LSTPlayers[actualplayer].LSTColVal):
               LSTPlayers[actualplayer].LSTColVal[Column] = ('','txt')
            # Then Rand it
            LSTPlayers[actualplayer].LSTColVal[0] = (rand,'txt')
      
      self.Logs.Log("DEBUG",self.TxtRecap)
      return return_code      

###############
# Function run after each dart throw - for example, add points to player
   def PostDartsChecks(self,hit,LSTPlayers,actualround,actualplayer,playerlaunch):
      return_code = 0
      ####
      #Your main game code will be here
      ####

      # Apply the coefficient to simple double triple and bull (Master case)
      if self.GameOpts['master']=='True':
         if hit[:1] == 'S':
            hitcoeff = 1
         elif hit[:1] == 'D':
            hitcoeff = 3
         elif hit[:1] == 'T':
            hitcoeff = 6
         if hit == 'SB':
            hitcoeff = 5
         elif hit == 'DB':
            hitcoeff = 10

      # Apply the coefficient to simple double triple and bull (No Master case)
      if self.GameOpts['master']=='False':
         if hit[:1] == 'S':
            hitcoeff = 1
         elif hit[:1] == 'D':
            hitcoeff = 2
         elif hit[:1] == 'T':
            hitcoeff = 3
         if hit == 'SB':
            hitcoeff = 1
         elif hit == 'DB':
            hitcoeff = 2

      # GOOD HIT
      if (self.GameOpts['master']=='True' and hit == LSTPlayers[actualplayer].GetColVal(0)) or (self.GameOpts['master']=='False' and (hit[1:] == LSTPlayers[actualplayer].GetColVal(0))) :
         # Keep it for Stats
         LSTPlayers[actualplayer].IncrementHits(hit)
         # Play sound if touch is valid
         self.myDisplay.Sound4Touch(hit) # Play sound
         # Add value score (score equals hits in this game)
         LSTPlayers[actualplayer].score += 1 * hitcoeff
         # Display hits on screen
         LSTPlayers[actualplayer].LSTColVal[playerlaunch] = ("+{}".format(hitcoeff), 'txt')
      

      # Check for end of game (no more rounds to play)
      if playerlaunch == self.nbdarts and actualround == int(self.maxround) and actualplayer == len(LSTPlayers)-1:
         bestscoreid = -1
         bestscore = -1
         for Player in LSTPlayers:
            if Player.score > bestscore:
               bestscore = Player.score
               bestscoreid = Player.ident
         self.winner = bestscoreid
         return_code = 3

      # Record total dart thrown, total hits (S=1, D=2, T=3) and refresh players stats
      LSTPlayers[actualplayer].dartsthrown += 1
      self.RefreshStats(LSTPlayers,actualround)
      
      return return_code

   ###############
   # Method to frefresh Each Player Stats
   def RefreshStats(self,Players,actualround):
      for P in Players:
         P.Stats['Hits per round']=P.HitsPerRound(actualround)
         P.Stats['MPR']=P.ShowMPR()

   ###############
   # Returns Random things, to send to clients in case of a network game
   def GetRandom(self,LSTPlayers,actualround,actualplayer,playerlaunch):
      if playerlaunch == 1:
         return LSTPlayers[actualplayer].GetColVal(0)
      else:
         return None

   ###############
   # Set Random things, while received by master in case of a network game
   def SetRandom(self,LSTPlayers,actualround,actualplayer,playerlaunch,data):
      if data != None:
         LSTPlayers[actualplayer].LSTColVal[0] = (data, 'txt')
         self.Logs.Log("DEBUG","Setting random value for player {} to {}".format(actualplayer,data))
      self.RandomIsFromNet = True

   ###############
   # Define the next game players order, depending of previous games' scores
   def DefineNextGameOrder(self,LSTPlayers):
      Sc = {}
      # Create a dict with player and his score
      for P in LSTPlayers:
         Sc[P.PlayerName] = P.score
      # Order this dict depending of the score
      NewOrder=collections.OrderedDict(sorted(Sc.items(), key=lambda t: t[1]))# For DESC order, add "reverse=True" to the sorted() function
      FinalOrder=list(NewOrder.keys())
      # Return
      return FinalOrder

   ###############
   # Check for handicap and record appropriate marks for player
   def CheckHandicap(self,LSTPlayers):
      pass

