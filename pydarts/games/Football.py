# -*- coding: utf-8 -*-
# Game by ... @Poilou !
######
from include import CPlayer
from include import CGame
from include import CScores
import collections# To use OrderedDict to sort players from the last score they add
from copy import deepcopy# For backupTurn

GameLogo = 'Football.png' # Background image - relative to images folder - Must me names like the game itself
Headers = [ "1","2","3","Drib","","","Ball" ] # Columns headers - Must be a string
GameOpts = {'max_round':'100','master':'False','goals':'3'} # Dictionnay of options in STRING format. You can use any numeric or True or False but in string format.
nbdarts = 3 # How many darts per player and per round ? Yes ! this is a feature :)
GameRecords = {'Score Per Round':'DESC','Dribbles':'DESC'}

############
#Extend the basic player
############
class CPlayerExtended(CPlayer.CPlayer):
   def __init__(self,x,NbPlayers,Config,res):
      super(CPlayerExtended, self).__init__(x,NbPlayers,Config,res)
      # Read the CJoueur class parameters, and add here yours if needed
      self.ball = False # Does the player has got the ball ?
      self.dribbles = 0 # How many time the players get the ball
      # Init Player Records to zero
      for GR in GameRecords:
         self.Stats[GR]='0'

############
# Your Game's Class
############
class Game(CGame.CGame):
   def __init__(self,myDisplay,GameChoice,nbplayers,GameOpts,Config,Logs):
      super(Game, self).__init__(myDisplay, GameChoice, nbplayers, GameOpts, Config, Logs)
      # GameRecords is the dictionnary of stats (see above)
      self.GameRecords=GameRecords
      # Import game settings
      self.GameLogo = GameLogo
      self.Headers = Headers
      self.nbdarts=nbdarts # Total darts the player has to play
      #  Get the maxiumum round number
      self.maxround=self.GameOpts['max_round']

   ###############
   # Actions done before each dart throw - for example, check if the player is allowed to play
   def PreDartsChecks(self,Players,actualround,actualplayer,playerlaunch):
      return_code = 0
      # TxtRecap Can be used to create a per-player debug output
      self.TxtRecap+="###### Player {} ######\n".format(actualplayer)
      # You will probably save the turn to be used in case of backup turn (each first launch) :
      if playerlaunch==1 and actualround==1 and actualplayer==0:
         self.myDisplay.PlaySound('football_intro')
      elif playerlaunch==1:
         self.myDisplay.PlaySound('whistle')
         # Clean actualplayers' columns
         i=0
         for Col in Players[actualplayer].LSTColVal:
            Players[actualplayer].LSTColVal[i] = ['','txt']
            i+=1
      # Draw the balloon if a player has got the ball
      for P in Players:
         if P.ball:
            self.TxtRecap+="Player {} has got the ball !\n".format(P.PlayerName)
            P.LSTColVal[6] = ['balloon','image']
         P.LSTColVal[3]=[P.dribbles,'txt']
      # Backuping scores
      self.SaveTurn(Players)
      # Send debug output to log system. Use DEBUG or WARNING or ERROR or FATAL
      self.Logs.Log("DEBUG",self.TxtRecap)
      return return_code      

   ###############
   # Function run after each dart throw - for example, add points to player
   def PostDartsChecks(self,hit,Players,actualround,actualplayer,playerlaunch):
      return_code = 0
      if ((hit[1:] == 'B' and self.GameOpts['master'] == 'False') or (hit == 'DB' and self.GameOpts['master'] == 'True')) and Players[actualplayer].ball==False:
         # Remove balloon to other players
         for P in Players:
            P.ball = False
            P.LSTColVal[6]=['','txt']
         # Give the ballon to actual player (drible)
         self.TxtRecap+="Player {} get the ball !\n".format(Players[actualplayer].PlayerName)
         self.myDisplay.PlaySound('youllneverwalkalone')
         Players[actualplayer].ball = True
         Players[actualplayer].dribbles += 1
         Players[actualplayer].LSTColVal[6]=['balloon','image']
         Players[actualplayer].LSTColVal[3]=[Players[actualplayer].dribbles,'txt']
      # Else if the balloon holder score
      elif Players[actualplayer].ball and (hit[:1]== 'D' or hit[:1]== 'T'):
         self.myDisplay.PlaySound('goal')
         self.TxtRecap+="Player {} scored !".format(Players[actualplayer].PlayerName)
         Players[actualplayer].score+=1
      # Display hit history
      Players[actualplayer].LSTColVal[playerlaunch-1]=[hit,'txt']

      # You may want to count how many touches (Simple = 1 touch, Double = 2 touches, Triple = 3 touches)
      Players[actualplayer].IncrementHits(hit)

      # You may want to count darts played
      Players[actualplayer].dartsthrown += 1
      
      # It is recommanded to update stats every dart thrown
      self.RefreshStats(Players,actualround)

      # If the actual player wins
      if int(Players[actualplayer].score) == int(self.GameOpts['goals']):
         self.winner = actualplayer
         return_code = 3
      # Return code to main
      return return_code

   ###############
   # Method to frefresh Player Stats - Adapt to the stats you want. They represent mathematical formulas used to calculate stats. Refreshed after every launch
   def RefreshStats(self,Players,actualround):
      for P in Players:
         P.Stats['Score Per Round']=P.ScorePerRound(actualround)
         P.Stats['Dribbles']=P.dribbles

   ###############
   # Returns Random things, to send to clients in case of a network game
   def GetRandom(self,Players,actualround,actualplayer,playerlaunch):
      return None # Means that there is no random
   ###############
   # Set Random things, while received by master in case of a network game
   def SetRandom(self,Players,actualround,actualplayer,playerlaunch,data):
      pass
   #
   # Define the next game players order, depending of previous games' scores
   #
   def DefineNextGameOrder(self,Players):
      Sc = {}
      # Create a dict with player and his score
      for P in Players:
         Sc[P.PlayerName] = P.score
      # Order this dict depending of the score
      NewOrder=collections.OrderedDict(sorted(Sc.items(), key=lambda t: t[1]))# For DESC order, add "reverse=True" to the sorted() function
      FinalOrder=list(NewOrder.keys())
      # Return
      return FinalOrder
   #
   # Check for handicap and record appropriate marks for player
   #
   def CheckHandicap(self,Players):
      pass
"""
#
# Update stats.csv with marks, throws and mpr for each player
#
   def PlayerStats(self,Players,actualround):
      pass
"""
