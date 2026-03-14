# -*- coding: utf-8 -*-
# Game by Cory Baumgart!
######
from include import CPlayer
from include import CGame
from include import CScores
import collections# To use OrderedDict to sort players from the last score they add
from copy import deepcopy# For backupTurn

GameLogo = 'Bermuda_Triangle.png' # Background image - relative to images folder
Headers = [ "12","-","-","-","-","-","-" ] # Columns headers - Must be a string
GameOpts = {'Double_bull':'False'} # Dictionnay of options - will be used at the initial screen
nbdarts = 3 # How many darts the player is allowed to throw
GameRecords = {'Points Per Round':'DESC','Points Per Dart':'DESC'}

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
      # GameRecords is the dictionnary of stats (see above)
      self.GameRecords=GameRecords
      self.GameLogo = GameLogo
      self.Headers = Headers
      self.nbdarts=nbdarts # Total darts the player has to play
      # Number of round is ruled
      self.maxround = 13
      if self.GameOpts['Double_bull'] == 'False':
         self.ScoreMap.update({'DB':25})
         # One more round if double bull enabled
         self.maxround = 12


###############
# Actions done before each dart throw - for example, check if the player is allowed to play
   def PreDartsChecks(self,Players,actualround,actualplayer,playerlaunch):
      return_code = 0
      
      # Set score at startup
      if actualround == 1 and playerlaunch == 1 and actualplayer == 0:
         self.myDisplay.PlaySound('ho_one_intro')

      # Each new player
      if playerlaunch==1:
         Players[actualplayer].pointsinround = 0
         self.SaveTurn(Players)
         Players[actualplayer].PrePlayScore = Players[actualplayer].score # Backup current score

         # Reset display Table
         Players[actualplayer].LSTColVal = []
         # Clean all next boxes
         for i in range(0,7):
            Players[actualplayer].LSTColVal.append(['','int'])
      
      # Display headers depending of round
      if actualround == 1:
         self.Headers[0] = str('12')
      elif actualround == 2:
         self.Headers[0] = str('13')
      elif actualround == 3:
         self.Headers[0] = str('14')
      elif actualround == 4:
         self.Headers[0] = str('DBL')
      elif actualround == 5:
         self.Headers[0] = str('15')
      elif actualround == 6:
         self.Headers[0] = str('16')
      elif actualround == 7:
         self.Headers[0] = str('17')
      elif actualround == 8:
         self.Headers[0] = str('TPL')
      elif actualround == 9:
         self.Headers[0] = str('18')
      elif actualround == 10:
         self.Headers[0] = str('19')
      elif actualround == 11:
         self.Headers[0] = str('20')
      elif actualround == 12:
         self.Headers[0] = str('SB')
      elif actualround == 13 and self.GameOpts['Double_bull']=='True':
         self.Headers[0] = str('DB')
      # Print debug output
      self.Logs.Log("DEBUG",self.TxtRecap)
      return return_code      

###############
# Function run after each dart throw - for example, add points to player
   def PostDartsChecks(self,hit,Players,actualround,actualplayer,playerlaunch):
      self.TxtRecap = ""
      return_code = 0
      addscore = 0
      # Define a var for adding score
      if (hit[1:] == '12') and actualround == 1:
         addscore = Players[actualplayer].pointsinround + self.ScoreMap[hit]
      elif (hit[1:] == '13') and actualround == 2:
         addscore = Players[actualplayer].pointsinround + self.ScoreMap[hit]
      elif (hit[1:] == '14') and actualround == 3:
         addscore = Players[actualplayer].pointsinround + self.ScoreMap[hit]
      elif hit[:1] == 'D' and actualround == 4:
         addscore = Players[actualplayer].pointsinround + self.ScoreMap[hit]
      elif (hit[1:] == '15') and actualround ==5:
         addscore = Players[actualplayer].pointsinround + self.ScoreMap[hit]
      elif (hit[1:] == '16') and actualround ==6:
         addscore = Players[actualplayer].pointsinround + self.ScoreMap[hit]
      elif (hit[1:] == '17') and actualround ==7:
         addscore = Players[actualplayer].pointsinround + self.ScoreMap[hit]
      elif hit[:1] == 'T' and actualround ==8:
         addscore = Players[actualplayer].pointsinround + self.ScoreMap[hit]
      elif (hit[1:] == '18') and actualround ==9:
         addscore = Players[actualplayer].pointsinround + self.ScoreMap[hit]
      elif (hit[1:] == '19') and actualround ==10:
         addscore = Players[actualplayer].pointsinround + self.ScoreMap[hit]
      elif (hit[1:] == '20') and actualround ==11:
         addscore = Players[actualplayer].pointsinround + self.ScoreMap[hit]
      elif (hit == 'SB' or hit == 'DB') and actualround ==12:
         addscore = Players[actualplayer].pointsinround + self.ScoreMap[hit]
      elif hit == 'DB' and actualround ==13 and self.GameOpts['Double_bull']=='True':
         addscore = Players[actualplayer].pointsinround + self.ScoreMap[hit]
      
      # Classic case (between start and end)
      if addscore > 0:
         self.myDisplay.Sound4Touch(hit) # Touched !
         Players[actualplayer].score += addscore # add score
         Players[actualplayer].pointsinround += self.ScoreMap[hit] # Keep total for this round
         # You may want to keep the "Total Points" (Global amount of grabbed points, follow the player all game long)
         Players[actualplayer].TotalPoints+=self.ScoreMap.get(hit)
      # No dart marked
      elif Players[actualplayer].pointsinround == 0 and playerlaunch == 3:
         self.TxtRecap += "Dividing score by half!\n"
         # Divide score by half
         return_code = 1 # Next player
         Players[actualplayer].score -= Players[actualplayer].score/2
         self.myDisplay.PlaySound('whatamess')
      
      # Check last round
      if actualround >= int(self.maxround) and actualplayer==self.nbplayers-1 and playerlaunch == int(self.nbdarts):
         self.TxtRecap += "/!\ Last round reached ({})\n".format(actualround)
         return_code = 2
         winner = self.CheckWinner(Players)
         if winner != -1:
            self.TxtRecap += "/!\ Player {} wins !\n".format(winner)
            self.winner = winner
            return_code = 3

      # You may want to count how many touches (Simple = 1 touch, Double = 2 touches, Triple = 3 touches)
      Players[actualplayer].IncrementHits(hit)

      # You may want to count darts played
      Players[actualplayer].dartsthrown += 1
      
      # It is recommanded to update stats every dart thrown
      self.RefreshStats(Players,actualround)

      # Store what he played in the table
      Players[actualplayer].LSTColVal[0] = (addscore, 'int')

      # Print debug
      self.Logs.Log("DEBUG",self.TxtRecap)

      # Next please !
      return return_code

   ##############
   # Method to check if there is a winnner
   def CheckWinner(self,Players):
      bestscoreid = -1
      # Find the better score
      for Player in Players:
         if (bestscoreid == -1 or Player.score > Players[bestscoreid].score):
            bestscoreid = Player.ident
            print("player "+str(bestscoreid)+" is current winner")
      #print(bestscoreid)
      return bestscoreid

   ###############
   # Function launched if the player hit the player button before having thrown all his darts (Pneu)
   def EarlyPlayerButton(self,Players,actualplayer,actualround):
      self.TxtRecap+="EarlyPlayer function. Actual player marked {}\n".format(Players[actualplayer].pointsinround)
      # Jump to next player by default
      return_code=1
      
      # Eventually divide by 2
      if Players[actualplayer].pointsinround == 0:
         self.TxtRecap += "Dividing score by half! And early !\n"
         # Divide score by half
         Players[actualplayer].score -= Players[actualplayer].score/2
         self.myDisplay.PlaySound('whatamess')
      
      # Last round - check winner or return Game over
      if actualround == int(self.maxround) and actualplayer == self.nbplayers - 1:
         # Game over
         return_code=2
         winner=self.CheckWinner(Players)
         if winner != -1:
            self.winner = winner
            self.TxtRecap += "/!\ Player {} wins !\n".format(winner)
            # Victory
            return_code=3

      return return_code

   ###############
   # Method to frefresh Player Stats - Adapt to the stats you want. They represent mathematical formulas used to calculate stats. Refreshed after every launch
   def RefreshStats(self,Players,actualround):
      for P in Players:
         P.Stats['Points Per Round']=P.ShowPPR()
         P.Stats['Points Per Dart']=P.ShowPPD()

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

   #################
   # Check for handicap and record appropriate marks for player
   def CheckHandicap(self,Players):
      pass
