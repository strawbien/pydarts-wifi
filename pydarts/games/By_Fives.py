# -*- coding: utf-8 -*-
# Game by ... poilou !
######
from include import CPlayer
from include import CGame
from include import CScores
import collections# To use OrderedDict to sort players from the last score they add
from copy import deepcopy# For backupTurn

GameLogo = 'By_Fives.png' # Background image - relative to images folder
Headers = [ "Rnd","","","","","","" ] # Columns headers - Must be a string
GameOpts = {'winscore':'5'} # Dictionnay of options - will be used at the initial screen
nbdarts = 3 # How many darts the player is allowed to throw
# Dictionnary of stats and dislay order (For exemple : Points Per Darts and Avg are displayed in descending order)
GameRecords = {'Score':'DESC'}

############
# Extend the basic player's class
############
class CPlayerExtended(CPlayer.CPlayer):
   def __init__(self,x,NbPlayers,Config,res):
      super(CPlayerExtended, self).__init__(x,NbPlayers,Config,res)
      self.PrePlayScore = None
      # Init Player Records to zero
      for GR in GameRecords:
         self.Stats[GR]='0'

############
# Your Game's Class
############
class Game(CGame.CGame):
   def __init__(self,myDisplay,GameChoice,nbplayers,GameOpts,Config,Logs):
      super(Game, self).__init__(myDisplay, GameChoice, nbplayers, GameOpts, Config, Logs)
      self.GameLogo = GameLogo
      self.Headers = Headers
      self.maxround=99 # Set total rounds
      self.nbdarts=nbdarts # Total darts the player has to play
      # GameRecords is the dictionnary of stats (see above)
      self.GameRecords=GameRecords

   ###############
   # Actions done before each dart throw - for example, check if the player is allowed to play
   def PreDartsChecks(self,Players,actualround,actualplayer,playerlaunch):
      return_code = 0

      # Set score at startup
      if actualround == 1 and playerlaunch == 1 and actualplayer == 0:
         for Player in Players:
            # Init score
            Player.score = 0
         self.myDisplay.PlaySound('ho_one_intro')

      # Each new player
      if playerlaunch==1:
         Players[actualplayer].pointsinround = 0
         self.SaveTurn(Players)
         Players[actualplayer].PrePlayScore = Players[actualplayer].score # Backup current score

         #Reset display Table
         Players[actualplayer].LSTColVal = []
         # Clean all next boxes
         for i in range(0,7):
            Players[actualplayer].LSTColVal.append(['','int'])
      
      # Print debug output
      self.Logs.Log("DEBUG",self.TxtRecap)
      return return_code      

   ###############
   # Function run after each dart throw - for example, add points to player
   def PostDartsChecks(self,hit,Players,actualround,actualplayer,playerlaunch):
      return_code = 0
      
      self.myDisplay.Sound4Touch(hit) # Touched !
      Players[actualplayer].pointsinround += self.ScoreMap[hit]

      if playerlaunch == 3:
         checkpoints = self.Modby5(Players[actualplayer].pointsinround)
         if checkpoints == True:
            Players[actualplayer].score += 1
         if Players[actualplayer].score == int(self.GameOpts['winscore']):
            #return_code = 3
            self.TxtRecap="Game should be over\n"

      # Change table displayed
      Players[actualplayer].LSTColVal[0] = (Players[actualplayer].pointsinround,'int')

      # You may want to count how many touches (Simple = 1 touch, Double = 2 touches, Triple = 3 touches)
      Players[actualplayer].IncrementHits(hit)

      # You may want to count darts played
      Players[actualplayer].dartsthrown += 1
      
      # It is recommanded to update stats every dart thrown
      self.RefreshStats(Players,actualround)

      # Check last round
      if actualround >= int(self.maxround) and actualplayer==self.nbplayers-1 and playerlaunch == int(self.nbdarts):
         self.TxtRecap += "/!\ Last round reached ({})\n".format(actualround)
         return_code = 2

      #Check if there is a winner
      winner = self.CheckWinner(Players)
      self.TxtRecap="Check winner module was run.  Winner reports {}\n".format(winner)
      if winner != -1:
         self.TxtRecap += "/!\ Player {} wins !\n".format(winner)
         self.winner = winner
         return_code = 3
         
      return return_code

   ###############
   # Module to divide score by 5 and return modulus
   def Modby5(self,score):
      remainder = 0
      remainder = score % 5
      if remainder == 0:
         return True
      else:
         return False
   ###############
   # Method to check if there is a winnner
   def CheckWinner(self,Players):
      winnerid = -1
      #Find the better score
      for Player in Players:
         if Player.score == int(self.GameOpts['winscore']):
            winnerid = Player.ident
      return winnerid

   ###############
   # Method to frefresh Player Stats - Adapt to the stats you want. They represent mathematical formulas used to calculate stats. Refreshed after every launch
   def RefreshStats(self,Players,actualround):
      for P in Players:
         P.Stats['Score']=P.score

   ###############
   # Returns Random things, to send to clients in case of a network game
   def GetRandom(self,Players,actualround,actualplayer,playerlaunch):
      return None # Means that there is no random

   ###############
   # Set Random things, while received by master in case of a network game
   def SetRandom(self,Players,actualround,actualplayer,playerlaunch,data):
      pass

   ###############
   # Define the next game players order, depending of previous games' score
   def DefineNextGameOrder(self,Players):
      Sc = {}
      # Create a dict with player and his score
      for P in Players:
         Sc[P.PlayerName] = P.score
      # Order this dict depending of the score
      NewOrder=collections.OrderedDict(sorted(Sc.items(), key=lambda t: t[1], reverse=True))# For DESC order, add "reverse=True" to the sorted() function
      FinalOrder=list(NewOrder.keys())
      # Return
      return FinalOrder

   ######################
   # Check for handicap and record appropriate marks for player
   def CheckHandicap(self,Players):
      pass

