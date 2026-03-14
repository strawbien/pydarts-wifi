# -*- coding: utf-8 -*-
# Game by LB, idea by Manouk 
########
from include import CPlayer
from include import CGame
from include import CScores
import random
import collections# To use OrderedDict to sort players from the last score they add
from copy import deepcopy# For backupTurn

GameLogo = 'Kinito.png' # Background image - relative to images folder
Headers = [ "Min","Total","K'to","","","","" ] # Columns headers - Must be a string
GameOpts = {'max_round':'10','winscore':'210','kinito':'21','master':'False'} # Dictionnay of options - will be used at the initial screen
nbdarts = 3
# Dictionnary of stats and dislay order (For exemple : Points Per Darts and Avg are displayed in descending order)
GameRecords = {'Points Per Round':'DESC'}

############
#Extend the basic player
############
class CPlayerExtended(CPlayer.CPlayer):
   def __init__(self,x,NbPlayers,Config,res):
      super(CPlayerExtended, self).__init__(x,NbPlayers,Config,res)
      self.minscore = None
      # Read the CJoueur class parameters, and add here yours if needed
      self.kinito = False
      # Total points
      self.TotalPoints = 0
      # Score to hit when Kinito occur
      self.KinitoScore = ""
      self.Headers = Headers
      self.GameLogo =GameLogo
      self.nbdarts=nbdarts # Total darts the player has to play
      # Init Player Records to zero
      for GR in GameRecords:
         self.Stats[GR]='0'

############
# Your Game's Class
############
class Game(CGame.CGame):
   def __init__(self,myDisplay,GameChoice,nbplayers,GameOpts,Config,Logs):
      super(Game, self).__init__(myDisplay, GameChoice, nbplayers, GameOpts, Config, Logs)
      # Nb players
      self.nbplayers=nbplayers
      # GameRecords is the dictionnary of stats (see above)
      self.GameRecords=GameRecords
      # Set config string to integer
      self.nbdarts=3
      self.Headers = Headers
      self.GameLogo = GameLogo
      #  Get the maxiumum round number
      self.maxround=self.GameOpts['max_round']

###############
# Actions done before each dart throw - for example, check if the player is allowed to play
   def PreDartsChecks(self,Players,actualround,actualplayer,playerlaunch):
      return_code = 0
      self.TxtRecap=""
      #music introduction 
      if playerlaunch == 1 and actualplayer == 0 and actualround == 1:
         self.myDisplay.PlaySound('kinitintro')
         for Player in Players:
            Player.LSTColVal[0] = (0,'int','green')
      # Init first player score to do (first player of first round random)
      if actualround == 1 and actualplayer == 0 and playerlaunch == 1 and self.RandomIsFromNet==False:
         Players[actualplayer].minscore = random.randint(1,20)
      if Players[actualplayer].minscore == None:
         Players[actualplayer].minscore = 0
      self.TxtRecap+="You had to reach at least score {}\n".format(Players[actualplayer].minscore)
      # Reset Per round total and kinito status
      Players[actualplayer].LSTColVal[0]=(Players[actualplayer].minscore,'int')
      if playerlaunch == 1:
         # Backup Turn save
         self.SaveTurn(Players)
         Players[actualplayer].LSTColVal[1]=(0,'int',None)
         # Update Screen for new challenger
         for Player in Players:
            Player.kinito = False
            Player.KinitoScore=""
            Player.LSTColVal[2] = ('','int','green')
      # Put KinitoScore in table
      for Player in Players:
         Player.LSTColVal[2] = (Player.KinitoScore,'int','red')

      # Check winner
      WinnerValue=self.CheckWinner(Players,actualplayer,playerlaunch)
      if WinnerValue != -1:
         return_code=WinnerValue
      self.Logs.Log("DEBUG",self.TxtRecap)
      return return_code

###############
# Function run after each dart throw - for example, add points to player
   def PostDartsChecks(self,hit,Players,actualround,actualplayer,playerlaunch):
      self.TxtRecap=""
      return_code = 0
      # Who is next player ?
      if actualplayer==self.nbplayers-1:
         nextplayer=0
      else:
         nextplayer = actualplayer+1
      # Basic Score check
      if self.ScoreMap[hit] >= Players[actualplayer].minscore and (playerlaunch==self.nbdarts or hit != "T7") and not Players[actualplayer].kinito :
         self.TxtRecap+="Good. You reached {} score\n".format(self.ScoreMap[hit])
         Players[actualplayer].minscore = self.ScoreMap[hit]
         Players[actualplayer].IncrementCol(self.ScoreMap[hit],1)
         Players[actualplayer].score+=self.ScoreMap[hit]
         Players[actualplayer].TotalPoints+=self.ScoreMap[hit]
         self.myDisplay.Sound4Touch(hit) # Play sound
      # bad bluff (score is under the min score)
      if self.ScoreMap[hit] < Players[actualplayer].minscore and (hit != "T7" or playerlaunch==self.nbdarts) and not Players[actualplayer].kinito:
         self.TxtRecap+="What a mess. You reached {} score\n".format(self.ScoreMap[hit])
         Players[actualplayer].score -= Players[actualplayer].GetColVal(1)
         Players[actualplayer].TotalPoints -= Players[actualplayer].GetColVal(1)
         return_code = 1 # next player
         self.myDisplay.PlaySound('whatamess')
      # Kinito Open
      if self.ScoreMap[hit] == int(self.GameOpts['kinito']) and int(playerlaunch)<int(self.nbdarts):
         Players[actualplayer].score+=self.ScoreMap[hit]
         Players[actualplayer].TotalPoints+=self.ScoreMap[hit]
         self.TxtRecap+="Kinito ! You reached special score ! ({})\n".format(self.ScoreMap[hit])
         self.myDisplay.PlaySound('kinito')
         #self.myDisplay.DisplayBlinkCentered("Kinito !")
         self.myDisplay.InfoMessage(["Kinito !"],1000,None,'middle','big')
         Players[actualplayer].kinito = True
         Players[actualplayer].KinitoScore = 'K\'to'
         if self.RandomIsFromNet == False:
            self.KinitoScore(Players)
      # If Kinito played
      if Players[actualplayer].kinito:
         for Player in Players:
            if self.ScoreMap[hit] == Player.KinitoScore and Player.ident != actualplayer:
               Players[actualplayer].score+=self.ScoreMap[hit]
               Players[actualplayer].TotalPoints+=self.ScoreMap[hit]
               Player.score = int(Player.score / 2)
               self.TxtRecap+="You hit the Kinito score of player {} !\n".format(Player.ident)
               self.myDisplay.PlaySound('kinito')
      
      # Put score / 2 to min score to next player
      if len(Players) > 1:
         self.TxtRecap+="Hit : {}".format(hit)
         Players[nextplayer].minscore = int(self.ScoreMap[hit] / 2)
      else:
         Players[actualplayer].minscore = self.ScoreMap[hit]
      # Player get over Winscore with master option
      if Players[actualplayer].score > int(self.GameOpts['winscore']) and self.GameOpts['master']=='True':
         Players[actualplayer].score=2 * int(self.GameOpts['winscore'])-Players[actualplayer].score
         Players[actualplayer].TotalPoints+=self.ScoreMap[hit]
         self.myDisplay.PlaySound('toohigh') # Too High , man !
         #self.myDisplay.DisplayBlinkCentered("Damn, you get too high !")
         self.myDisplay.InfoMessage(["Too high !"],1000,None,'middle','big')
         return_code = 1
      # Populate screen table
      Players[actualplayer].LSTColVal[0] = (Players[actualplayer].minscore,'int')
      for Player in Players:
         Player.LSTColVal[2] = (Player.KinitoScore,'int','red')

      # You may want to count how many touches (Simple = 1 touch, Double = 2 touches, Triple = 3 touches)
      Players[actualplayer].IncrementHits(hit)

      # You may want to count darts played
      Players[actualplayer].dartsthrown += 1
      
      # It is recommanded to update stats every dart thrown
      self.RefreshStats(Players,actualround)

      # Check last round
      if actualround >= int(self.maxround) and actualplayer==self.nbplayers-1 and (playerlaunch == self.nbdarts or return_code == 1):
         self.TxtRecap += "/!\ Last round reached ({})\n".format(actualround)
         return_code = 2
      # Check winner
      WinnerValue=self.CheckWinner(Players,actualplayer,playerlaunch)
      if WinnerValue != -1:
         return_code=WinnerValue
      # Display Hit
      # self.myDisplay.InfoMessage([str(hit)],1000,None,'middle','huge')
      # Print debug
      self.Logs.Log("DEBUG",self.TxtRecap)
      # Return code
      return return_code
################
# Function to check winner
   def CheckWinner(self,Players,actualplayer,playerlaunch):
      # Check winner if no master option
      if Players[actualplayer].score >= int(self.GameOpts['winscore']) and self.GameOpts['master']=='False':
         self.winner = Players[actualplayer].ident 
         return_code = 3 # There is a winner
      # Check winner if master option
      elif Players[actualplayer].score == int(self.GameOpts['winscore']) and self.GameOpts['master']=='True':
         self.winner = Players[actualplayer].ident 
         return_code = 3 # There is a winner
      else:
         return_code=-1
      return return_code
###############
# Function used to backup turn - you don't needs to modify it (for the moment) 
   def SaveTurn(self,Players):
      #Create Backup Properies Array
      try:
         self.PreviousBackUpPlayer = deepcopy(self.BackUpPlayer)
      except:
         self.TxtRecap+="No previous turn to backup.\n"
      self.BackUpPlayer = deepcopy(Players)
      self.TxtRecap+="Score Backup.\n"
      
#################
# Function to attribute a kinito score to everyone 
   def KinitoScore(self,Players):
      for Player in Players:
         if not Player.kinito:
            done=False
            while not done:
               kinitoscore = random.choice(list(self.ScoreMap.values()))
               # If NOT master, player's kinito score is less than General Kinito score
               if kinitoscore < int(self.GameOpts['kinito']):# and self.GameOpts['master']==False:
                  Player.KinitoScore=kinitoscore
                  done = True

   #################
   # Fonction pneu
   def EarlyPlayerButton(self,Players,actualplayer,actualround):
      return_code=1
      # If master option and early player button pushed, return to original score and refresh screen
      if self.GameOpts['master']=='True':
         Players[actualplayer].score -= Players[actualplayer].LSTColVal[1][0]
      if actualround == int(self.maxround) and actualplayer == self.nbplayers - 1:
         # If its a EarlyPlayerButton just at the last round - return GameOver code
         return 2
      return return_code

   ###############
   # Method to frefresh Player Stats - Adapt to the stats you want. They represent mathematical formulas used to calculate stats. Refreshed after every launch
   def RefreshStats(self,Players,actualround):
      for P in Players:
         P.Stats['Points Per Round']=P.AVG(actualround)

   #
   # Returns and Random things, to send to clients in case of a network game
   #
   def GetRandom(self,Players,actualround,actualplayer,playerlaunch):
      # Send initial random score value
      ret = {'PLAYERKINITO':None,'KINITOSCORE':None,'MINSCORE':None}
      if actualround == 1 and actualplayer == 0 and playerlaunch == 1:
         ret['MINSCORE']=Players[0].minscore
      # Check if Kinito is open and if true, send random values to other players
      KinitoOpen = False
      for Player in Players:
         if Player.kinito:
            KinitoOpen=True
      if KinitoOpen:
         KScores = []
         for P in Players:
            KScores.append(P.KinitoScore)
         ret={'PLAYERKINITO':Player.ident,'KINITOSCORES':KScores}
      return ret
      
      
      
# Set Random things, while received by master in case of a network game
#
   def SetRandom(self,Players,actualround,actualplayer,playerlaunch,data):
      KinitoOpen=False
      for Player in Players:
         if Player.kinito:
            KinitoOpen=True
            self.Logs.Log("DEBUG","KINITO is open ! We wait for random score via network :)")
      if KinitoOpen and 'KINITOSCORES' in data:
         KScores = data['KINITOSCORES']
         for P in Players:
            if P.kinito==False:
               P.KinitoScore = int(KScores[P.ident])
            else:
               P.KinitoScore = 'K\'to'
      if actualround == 1 and actualplayer == 0 and playerlaunch == 1:
         Players[0].minscore = int(data['MINSCORE'])
      self.RandomIsFromNet = True

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
