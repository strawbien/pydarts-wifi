# -*- coding: utf-8 -*-
# Game by LB
#######
from include import CPlayer
from include import CGame
from include import CScores
import collections# To use OrderedDict to sort players from the last score they add
from copy import deepcopy# For backupTurn
#
GameLogo = 'Shanghai.png' # Background image - relative to images folder
Headers = [ "HIT","MAX","-","-","-","-","-" ] # Columns headers - Must be a string
GameOpts = {'max_round':'7'} # Dictionnay of options
nbdarts = 3
GameRecords = {'Score':'DESC','Reached Score':'DESC', 'Hits':'DESC'}

#Extend the basic player
class CPlayerExtended(CPlayer.CPlayer):
   def __init__(self,x,nbjoueurs,Config,res):
      super(CPlayerExtended, self).__init__(x,nbjoueurs,Config,res)
      #The score the player has to hit
      self.ActualHit = 1
      # Init Player Records to zero
      for GR in GameRecords:
         self.Stats[GR]='0'
# Class of the real game
class Game(CGame.CGame):
   def __init__(self,myDisplay,GameChoice,nbplayers,GameOpts,Config,Logs):
      super(Game, self).__init__(myDisplay, GameChoice, nbplayers, GameOpts, Config, Logs)
      self.GameLogo = GameLogo
      self.Headers = Headers
      self.GameRecords=GameRecords
      self.nbdarts=nbdarts # Total darts the player has to play
      #  Get the maxiumum round number
      self.maxround=self.GameOpts['max_round']

   def SaveTurn(self,Players):
      #Create Backup Properies Array
      try:
         self.PreviousBackUpPlayer = deepcopy(self.BackUpPlayer)
      except:
         self.TxtRecap+="No previous turn to backup. You cannot use BackUpTurn since you threw no darts"
      self.BackUpPlayer = deepcopy(Players)
      self.TxtRecap+="Score Backup."


   def PostDartsChecks(self,hit,Players,actualround,actualplayer,playerlaunch):
      return_code = 0
      BlinkText = ""
      if str(hit[1:]) == str(Players[actualplayer].ActualHit):
         self.myDisplay.Sound4Touch(hit) # Play hit sound
         self.TxtRecap+="Player {}, your score was {}\n".format(actualplayer,Players[actualplayer].score)
         #debug-print self.ScoreMap.get(hit)
         Players[actualplayer].IncrementHits(hit)
         Players[actualplayer].score += self.ScoreMap.get(hit)
         if hit[1:] == '20':
            Players[actualplayer].ActualHit = 'B'
         elif hit[1:] == 'B':
            BlinkText = "Game Over !"
            self.TxtRecap += "/!\ Victory of player {} !\n".format(Players[actualplayer].ident)
            self.winner = Players[actualplayer].ident
            return_code = 3
         else:
            Players[actualplayer].ActualHit = Players[actualplayer].ActualHit + 1
         self.TxtRecap+="Player {} hit a {}\n".format(actualplayer,Players[actualplayer].GetTouchType(hit))
         self.TxtRecap+="Player {}, your score is now {}\n".format(actualplayer,Players[actualplayer].score)
         if return_code < 2:
            self.TxtRecap+="Player {}, you have now to hit {}\n".format(actualplayer,Players[actualplayer].ActualHit)
      # Check actual winnner
      self.winner = self.CheckWinner(Players)
      if self.winner != -1:
         self.TxtRecap+="Current winner is Player {}".format(self.winner)
      # Last round
      if actualround >= int(self.maxround) and actualplayer==self.nbplayers-1 and playerlaunch == int(self.nbdarts):
         self.TxtRecap += "\n/!\ Last round reached ({})\n".format(actualround)
         if self.winner != -1:
            return_code = 3
         else:
            return_code = 2

      # Update Score, darts count and Max score possible
      maxscore = self.CheckMaxPossibleScore(playerlaunch+1,actualround,Players[actualplayer].ActualHit,Players[actualplayer].score)
      Players[actualplayer].LSTColVal[0] = (Players[actualplayer].ActualHit,'int')
      Players[actualplayer].LSTColVal[1] = (maxscore,'int','green')

      # You may want to count darts played
      Players[actualplayer].dartsthrown += 1
      
      # It is recommanded to update stats every dart thrown
      self.RefreshStats(Players,actualround)

      # If there is text to display with blink
      if BlinkText != "":
         self.myDisplay.InfoMessage([BlinkText],None,None,'middle','big')

      # Display Hit
      # self.myDisplay.InfoMessage([str(hit)],1000,None,'middle','huge')
      
      # Print debug infos
      self.Logs.Log("DEBUG",self.TxtRecap)
      # return code
      return return_code
   ####
   # Before each throw - update screen, display score, etc...
   ####
   def PreDartsChecks(self,Players,actualround,actualplayer,playerlaunch):
      # First round, first player
      self.TxtRecap = "#########################\n"
      if playerlaunch==1 and actualround==1 and actualplayer==0:
         self.myDisplay.PlaySound('shanghai_intro')
      if playerlaunch == 1:
         self.SaveTurn(Players)

         # Update Score
         for LSTPlayer in Players:
            #self.myDisplay.DisplayLedsTxt(LSTPlayer.posy,str(LSTPlayer.ActualHit),0)
            LSTPlayer.LSTColVal[0] = (LSTPlayer.ActualHit,'int')
            #self.myDisplay.DisplayScore(LSTPlayer.ident,LSTPlayer.posy,str(LSTPlayer.score))
      maxscore = self.CheckMaxPossibleScore(playerlaunch,actualround,Players[actualplayer].ActualHit,Players[actualplayer].score)
      #self.myDisplay.DisplayLedsTxt(Players[actualplayer].posy,str(maxscore),1)
      Players[actualplayer].LSTColVal[1] = (maxscore,'int','green')

   # Method to check WHO is the winnner
   def CheckWinner(self,Players):
      deuce = False
      bestscore = -1
      bestplayer = -1
      for LSTObj in Players:
         if LSTObj.score > bestscore:
            bestscore = LSTObj.score
            deuce = False #necessary to reset deuce if there is a deuce with a higher score !
            bestplayer = LSTObj.ident
         elif LSTObj.score == bestscore:
            deuce = True
            bestplayer = -1
      if deuce:
         self.TxtRecap+="/!\ There is a score deuce ! Two people have {}\n".format(bestscore)
         higherhit = -1
         higherplayer = -1
         bestplayer = -1
         for LSTObj in Players:
            if LSTObj.score==bestscore:
               if LSTObj.ActualHit > higherhit:
                  bestplayer = LSTObj.ident
                  higherhit = LSTObj.ActualHit
               elif LSTObj.ActualHit == higherhit:
                  self.TxtRecap+="/!\ There is also a hit deuce ! Two people have {}\n".format(higherhit)
                  higherhit = LSTObj.ActualHit
                  bestplayer = -1
      return bestplayer

   def CheckMaxPossibleScore(self,playerlaunch,actualround,actualhit,actualscore):
      # Search MAX possible score for this player
      maxscore = actualscore
      dartsleft = 25-actualround*3-playerlaunch
      # Bull special case
      if actualhit == 'B':
         actualhit = 21
      for i in range(0,dartsleft):
         if actualhit+i == 21:
            maxscore += 50
         else:
            maxscore += (actualhit+i)*3
      return maxscore

#
# Pushed Player Early
#
   def EarlyPlayerButton(self,Players,actualplayer,actualround):
      return_code=1
      if actualround == int(self.maxround) and actualplayer == self.nbplayers - 1:
         self.winner = self.CheckWinner(Players)
         if self.winner != -1:
            self.TxtRecap+="Current winner is Player {}".format(self.winner)
            return 3
         else:
            return 2
      return return_code

   ###############
   # Method to frefresh Player Stats - Adapt to the stats you want. They represent mathematical formulas used to calculate stats. Refreshed after every launch
   def RefreshStats(self,Players,actualround):
      for P in Players:
         P.Stats['Score']=P.score
         P.Stats['Reached Score']=P.ActualHit
         P.Stats['Hits']=P.GetTotalHit()

#
# Returns and Random things, to send to clients in case of a network game
#
   def GetRandom(self,Players,actualround,actualplayer,playerlaunch):
      return None
#
# Set Random things, while received by master in case of a network game
#
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
