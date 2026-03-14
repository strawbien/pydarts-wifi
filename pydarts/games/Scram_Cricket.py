# -*- coding: utf-8 -*-
# Game by Cory Baumgart
######
from include import CPlayer
from include import CGame
from include import CScores
import operator# For ?
import random# For crazy
import collections# To use OrderedDict to sort players from the last score they add
from copy import deepcopy# For backupTurn

#VAR
GameLogo = 'Cricket.png' # Background image - relative to images folder
LSTRandom = [ 20,19,18,17,16,15,14,13,12,11,10,9,8,7 ]
Headers=['20','19','18','17','16','15','B']
GameOpts = {'optioncrazy' :'False','optioncutthroat':'False','drinkscore':'200','Teaming':'False'} # Options in string format
nbdarts = 3 # How many darts the player is allowed to throw
switchturns = False #used to determine if players switched their turns
alreadyswitched = False #used to say the switch happened
GameRecords = {'MPR':'DESC','Score':'DESC'}

#Extend the basic player
class CPlayerExtended(CPlayer.CPlayer):
   def __init__(self,x,nbjoueurs,Config,res):
      super(CPlayerExtended, self).__init__(x,nbjoueurs,Config,res)
      self.PayDrink=False # Flag used to know if player has reached the drink score
      self.DistribPoints=0 # COunt how many points the player gave to the others (cut throat)
      # Init Player Records to zero
      for GR in GameRecords:
         self.Stats[GR]='0'

class Game(CGame.CGame):
   def __init__(self,myDisplay,GameChoice,nbplayers,GameOpts,Config,Logs):
      super(Game, self).__init__(myDisplay, GameChoice, nbplayers, GameOpts, Config, Logs)
      self.nbdarts=nbdarts # Total darts the player has to play
      self.GameLogo = GameLogo
      self.Headers = Headers
      # GameRecords is the dictionnary of stats (see above)
      self.GameRecords=GameRecords
      # TEMP - place it somwhere else - prevent option to be activated in case of odd number of players
      if (nbplayers>=4 and nbplayers % 2 == 0 and GameOpts['Teaming']=='True'):
         # Enable display of teaming
         self.myDisplay.Teaming=True
      elif GameOpts['Teaming']=='True':
         self.Logs.Log('ERROR','You asked for a team game but the number of players is not a multiple of 2 players and is not at least 4 people. Disabling Teaming')
         self.GameOpts['Teaming'] = 'False'
      # Fixed number of round
      self.maxround = 99
      self.SwitchTurns = switchturns
      self.AlreadySwitched = alreadyswitched

#
   def PostDartsChecks(self,key,Players,actualround,actualplayer,playerlaunch):
      # Find teamMate (only for teaming)
      mate=self.Mate(actualplayer,len(Players))
      #Init
      PlayClosed = False # Should we play the closed sound ?
      PlayHit = False # Should we play the Double & triple sound ?
      BlinkText =""
      return_code = 0
      touchcount4total = False
      self.TxtRecap="Player {} - Score before playing: {}\n".format(Players[actualplayer].ident,format(Players[actualplayer].ModifyScore(0)))
      #We put in a variable the affected column
      TouchedColumn=key[1:]
      MultipleColumn=key[0:1]
      #If this column is currently displayed - Valid key
      if str(TouchedColumn) in self.Headers:
         #Look for the column corresponding to the value (return a string)
         IndexColTouched=self.Headers.index(str(TouchedColumn))
         if MultipleColumn=='S':
            TouchToAdd=1
         elif MultipleColumn=='D':
            TouchToAdd=2
         elif MultipleColumn=='T':
            TouchToAdd=3
#
         overtouched = 0 # To count how many over touched hits
         ###Displays the correspoding leds
         for x in range(0,TouchToAdd):
            #For each key to add - If the player has less than 3 keys
            if Players[actualplayer].GetColVal(IndexColTouched) < 3:
               #We add a touch to his score
               Players[actualplayer].IncrementColTouch(IndexColTouched)
               #If teaming, add touches to teammate
               if self.GameOpts['Teaming'] == 'True':
                  self.TxtRecap += "Changing teammates marks!\n"
                  Players[mate].IncrementColTouch(IndexColTouched)
               # Increment All Rounds hit count
               Players[actualplayer].IncrementHits()
               # Increment this round hit count
               Players[actualplayer].roundhits += 1
               # Play Closed sound only if first time reaching 3 hit in the same Column :
               if Players[actualplayer].GetColVal(IndexColTouched) == 3:
                  PlayClosed = True
               elif x==0:
                  PlayHit = True
            #If he already has three keys, we calculate how many more keys the player has made
            elif Players[actualplayer].GetColVal(IndexColTouched) == 3:
               # Increment overtouched for every touch over the 3 required ones
               overtouched+=1
                     
         #If there is a surplus
         if overtouched > 0:
            YourMateClosed=Players[mate].GetColVal(IndexColTouched)
            for LSTobj in Players:
               y = LSTobj.GetColVal(IndexColTouched)# Check if this players has closed
               MateY = self.Mate(LSTobj.ident,len(Players)) # Identify this player's teammate
               YourMateClosed = Players[MateY].GetColVal(IndexColTouched)# Check if his mate has closed too
               #We're looking for how much is a simple touch
               valueofsimplehit=self.ScoreMap['S' + key[1:]]
               # Multiply the single touch by the number of times the player touched above 3
               overtouchedpts = overtouched * int(valueofsimplehit)
               # Given that we will also give the teammates (Cut-Throat), we divide the total points to be given by two if Teaming
               if self.GameOpts['Teaming']=='True' and self.GameOpts['optioncutthroat'] == 'True':
                  overtouchedpts = overtouchedpts / 2
               # If Cut Throat and the other team have not closed we add the points to others
               if self.GameOpts['optioncutthroat']=='True' and ((y < 3 and self.GameOpts['Teaming']=='False') or (self.GameOpts['Teaming']=='True' and YourMateClosed>=3 and (y<3 or YourMateClosed < 3))):
                  # Points are added to those who do not close
                  self.TxtRecap+="Player {} takes {} points in the nose ! (Cut-throat)\n".format(LSTobj.ident,overtouchedpts)
                  LSTobj.ModifyScore(overtouchedpts)
                  # Give half points to teammate too if teaming is enabled
                  if self.GameOpts['Teaming']=='True':
                     Players[MateY].ModifyScore(overtouchedpts)# And give him half of point too
                     self.TxtRecap+="TeamMate {} takes {} points in the nose too ! (Cut-throat)\n".format(MateY,overtouchedpts)
                  # Add points to player's Stats
                  Players[actualplayer].DistribPoints += overtouchedpts
                  # If players take points, the keys count for the player's total
                  touchcount4total=True
               #If not Cut Throat we add the points to him only (+ possibly his teammate) if he is not closed for all
               elif self.GameOpts['optioncutthroat'] == 'False' and LSTobj.ident==Players[actualplayer].ident and (self.GameOpts['Teaming']=='False' or (self.GameOpts['Teaming']=='True' and YourMateClosed>=3)):
                  TotallyClosed = True
                  #Check if the gate is totally closed for normal mode
                  for LSTobj2 in Players:
                     z = LSTobj2.GetColVal(IndexColTouched)
                     # Identify people who require to be scored (only closed guys and teammates won't be scored)
                     if z < 3 and (self.GameOpts['Teaming']=='False' or (self.GameOpts['Teaming']=='True' and LSTobj2.ident!=mate)):
                        TotallyClosed=False
                  # If you there is still someone who didn't closed, take score for you (and your teammate)
                  if TotallyClosed==False:
                     self.TxtRecap+="This player get {} extra score !\n".format(overtouchedpts)
                     LSTobj.ModifyScore(overtouchedpts)
                     # Give half points to your teammate too if teaming is enabled
                     if self.GameOpts['Teaming']=='True':
                        Players[mate].ModifyScore(overtouchedpts)# And give him half of point too
                        self.TxtRecap+="TeamMate {} takes {} points !\n".format(MateY,overtouchedpts) #Was mate
                     touchcount4total=True
               # For fun, if the player reached the required drink score (usually 500), tell him to pay a drink !
               if LSTobj.PayDrink == False and LSTobj.score >= int(self.GameOpts['drinkscore']) and self.GameOpts['optioncutthroat']=='True' :
                  LSTobj.PayDrink = True
                  self.myDisplay.PlaySound('diegoaimaboir')

         # Added buttons if the player had a surplus (common to Cut Throat and Normal Mode)
         if overtouched > 0 and touchcount4total == True:
            #We add his extra keys to his total since they counted (players took points)
            Players[actualplayer].IncrementHits(overtouched)
            # Increment this round hit count
            Players[actualplayer].roundhits += 1
            PlayHit = True # Its a valid hit, play sound

         # Sound handling to avoid multiple sounds playing at a time
         if  PlayClosed:# Play sound only once, even if multiple TouchToAdd, and only if another sound is not played at the moment
            self.myDisplay.PlaySound('closed')
         elif PlayHit: 
            self.myDisplay.Sound4Touch(key) # Its a valid hit, play sound

         self.TxtRecap += "Key: {} - Active Columns: {}\n".format(Players[actualplayer].GetTouchType(key), self.Headers)
         self.TxtRecap += "Total number of hits for this player: {}\n".format(Players[actualplayer].GetTotalHit())
         self.TxtRecap += "Number of darts thrown from this player: {}\n".format(playerlaunch)

      # You may want to count darts played
      Players[actualplayer].dartsthrown += 1
      
      # It is recommanded to update stats every dart thrown
      self.RefreshStats(Players,actualround)

      # If it was last throw and no touch : play sound for "round missed"
      if playerlaunch == self.nbdarts and Players[actualplayer].roundhits == 0:
         self.myDisplay.PlaySound('chaussette')
         
      # Last throw of the last round
      if actualround >= int(self.maxround) and actualplayer==self.nbplayers-1 and playerlaunch == self.nbdarts:
         self.TxtRecap += "/!\ Last Round Reached ({})\n".format(actualround)
         return_code = 2

      # Check if there is a winner
      if self.AlreadySwitched == True:
         winner = self.CheckWinner(Players)
         if winner != -1:
            self.TxtRecap += "/!\ Player {} wins !\n".format(winner)
            self.winner = winner
            return_code = 3

      # Check if its time to switch turns
      if self.AlreadySwitched != True:
         self.switchturns = self.SwitchPlayerTurns(Players)
         self.TxtRecap += 'Switch turns says: {}\n'.format(self.switchturns)
         if self.switchturns == True:
            BlinkText = 'Lets switch it up!'
            self.TxtRecap += 'Switching players\n'
            if actualplayer == 0 or actualplayer == 2:
               self.TxtRecap += 'Player 1 is current player\n'
               return_code = 1
            self.ClearPlayerMarks(Players,0)

      # If there is blink text to display
      if BlinkText != "":
         self.myDisplay.InfoMessage([BlinkText],None,None,'middle','big')

      # Print debug
      self.Logs.Log("DEBUG",self.TxtRecap)
      return return_code
#
   #Clear player 1 marks
   def ClearPlayerMarks(self,Players,player):
       for col in range(0,self.nbcol+1):
           Players[0].LSTColVal[col] = [0,'leds','grey2']
       if self.GameOpts['Teaming'] == 'True':
          for col in range(0,self.nbcol+1):
              Players[2].LSTColVal[col] = [0,'leds','grey2']
       self.SwitchTurns = False
       self.AlreadySwitched = True
#
   #check if we switch turns
   def SwitchPlayerTurns(self,Players):
      ClosedCols = True
      for LSTColVal in Players[1].LSTColVal:
        if LSTColVal[0] != 3:
           ClosedCols = False
      #Return true if all numbers are closed
      if ClosedCols == True:
         return True
      else:
         return False

   # Method to check if there is a winnner
   def CheckWinner(self,Players):
      bestscoreid = -1
      ClosedCols=True
      #Find the better score
      for ObjPlayer in Players:
         if (bestscoreid == -1 or ObjPlayer.score < Players[bestscoreid].score) and self.GameOpts['optioncutthroat']=='True':
            bestscoreid = ObjPlayer.ident
         elif (bestscoreid == -1 or ObjPlayer.score > Players[bestscoreid].score) and self.GameOpts['optioncutthroat']=='False':
            bestscoreid = ObjPlayer.ident
      #Check if the player who have the better score has closed all gates
      for LSTColVal in Players[bestscoreid].LSTColVal:
         if LSTColVal[0] != 3:
            ClosedCols = False
      # If the player who have the best score has closed all the gates
      if ClosedCols == True:
         return bestscoreid
      else:
         return -1
   #
   def RandomHeader(self,Players,bypass=False):
      for x in range(0,int(self.nbcol)):
         #Check whether the Crazy doors are open or closed and assign new numbers to open and unclosed columns
         unmarked = False
         marked = False
         if bypass == True:
            unmarked = True
         else:
            for LSTobj in Players:
               y = LSTobj.GetColVal(x)
               if y in [1,2,3]:
                  marked = True
                  self.TxtRecap += "This column {} is marked for player {}! Leave it alone!\n".format(x,LSTobj.PlayerName)
               else:
                  unmarked = True
                  self.TxtRecap += "Column {} is open for player {}!  Randomize.\n".format(x,LSTobj.PlayerName)
         #If column is open, randomize number
         if marked == False and unmarked == True:
            self.TxtRecap+="Opened column : {} Random !\n".format(x)
            randomisdone = False
            while randomisdone == False:
               RandomNumber = random.choice(LSTRandom)
               if (str(RandomNumber) in self.Headers)== False:
                  self.Headers[x] = str(RandomNumber)
                  randomisdone = True
         else:
            self.TxtRecap += "Closed column: {} Not changed!\n".format(x)
#
#Action launched before each dart throw
#
   def PreDartsChecks(self,Players,actualround,actualplayer,playerlaunch):
      return_code = 0
      self.TxtRecap = ""
      # If first round - set display as leds
      if playerlaunch == 1 and actualround == 1 and actualplayer == 0:
         self.myDisplay.PlaySound('cricket')
         for Player in Players:
            for Column,Value in enumerate(Player.LSTColVal):
               Player.LSTColVal[Column] = [0,'leds','grey2']
         for col in range(0,self.nbcol+1):
               Players[actualplayer].LSTColVal[col] = [3,'leds','grey2']
         if self.GameOpts['Teaming'] == 'True':
            mate=self.Mate(actualplayer,len(Players))
            for col in range(0,self.nbcol+1):
                Players[mate].LSTColVal[col] = [3,'leds','grey2']
      if playerlaunch == 1:
         # Reset number of hits in this round for this player 
         Players[actualplayer].roundhits = 0
         #Heading definition according to these cases
         if self.GameOpts['optioncrazy']=='True' and actualround==1 and actualplayer==0 and playerlaunch==1 and self.RandomIsFromNet == False:
            self.RandomHeader(Players,True)
         #Definition of header - random if option crazy = 1
         elif self.GameOpts['optioncrazy']=='True' and self.RandomIsFromNet == False:
            self.RandomHeader(Players)
         self.TxtRecap+="Active columns : {}".format(self.Headers)
         self.Logs.Log("DEBUG",self.TxtRecap)
         self.SaveTurn(Players)

      return return_code
#
# If player Hit the Player button before having threw all his darts
#
   def EarlyPlayerButton(self,Players,actualplayer,actualround):
      # Next player by default
      return_code=1
      self.TxtRecap+="You hit Player button before throwing all your darts ! Did you hit the PNEU ?"
      self.TxtRecap+="Actualround {} Max Round {} actualplayer {} nbplayers {}".format(actualround,self.maxround,actualplayer,self.nbplayers - 1)
      # If no touch for this player at this round : play sound for "round missed"
      if Players[actualplayer].roundhits == 0:
         self.myDisplay.PlaySound('chaussette')
      if actualround == int(self.maxround) and actualplayer == self.nbplayers - 1:
         # If its a EarlyPlayerButton just at the last round - return GameOver
         return 2
      return return_code

   ###############
   # Method to frefresh Player Stats - Adapt to the stats you want. They represent mathematical formulas used to calculate stats. Refreshed after every launch
   def RefreshStats(self,Players,actualround):
      for P in Players:
         P.Stats['MPR']=P.ShowMPR()
         P.Stats['Score']=P.score

#
# Returns and Random things, to send to clients in case of a network game
#
   def GetRandom(self,Players,actualround,actualplayer,playerlaunch):
      if GameOpts['optioncrazy']=='True':
         return self.Headers
      else:
         return False
#
# Set Random things, while received by master in case of a network game
#
   def SetRandom(self,Players,actualround,actualplayer,playerlaunch,data):
      if data != False:
         self.Headers = data
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
      if self.GameOpts['optioncutthroat']=='True':
         NewOrder=collections.OrderedDict(sorted(Sc.items(), key=lambda t: t[1], reverse=True))# For DESC order, add "reverse=True" to the sorted() function
      else:
         NewOrder=collections.OrderedDict(sorted(Sc.items(), key=lambda t: t[1]))# For DESC order, add "reverse=True" to the sorted() function
      FinalOrder=list(NewOrder.keys())
      # Return
      return FinalOrder

#
# Find TeamMate in case of Teaming
#
   def Mate(self,actualplayer,nbplayers):
      mate=-1
      if (self.GameOpts['Teaming'] == 'True'):
         if actualplayer<(nbplayers / 2):
            mate=actualplayer + nbplayers / 2
         else:
            mate=actualplayer - nbplayers / 2
      return mate
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
