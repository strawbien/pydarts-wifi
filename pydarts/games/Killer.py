# -*- coding: utf-8 -*-
# Game by @Diego !
######
from include import CPlayer
from include import CGame
from include import CScores
import operator
import random
import collections# To use OrderedDict to sort players from the last score they add
from copy import deepcopy# For backupTurn
import time

GameLogo = 'Killer.png' # Background image
Headers = [ "Hom","Hit","Kil","-","-","-","-" ] # Columns headers - Must be a string
GameOpts = {'max_round':'100'} # Dictionnay of options - Text format only
nbdarts = 3 # How many darts per player and per round
GameRecords = {'Score':'DESC','Points Per Round':'DESC'}

#Extend the basic player
class CPlayerExtended(CPlayer.CPlayer):
   def __init__(self,x,nbjoueurs,Config,res):
      super(CPlayerExtended, self).__init__(x,nbjoueurs,Config,res)
      self.Camembert = 21
      self.killer = False
      self.NbColVal = 1
      self.alive = True
      # Init Player Records to zero
      for GR in GameRecords:
         self.Stats[GR]='0'

# Class of the real game
class Game(CGame.CGame):
   def __init__(self,myDisplay,GameChoice,nbplayers,GameOpts,Config,Logs):
      super(Game, self).__init__(myDisplay, GameChoice, nbplayers, GameOpts, Config, Logs)
      self.GameLogo = GameLogo
      self.Headers = Headers
      self.nbdarts = nbdarts
      self.nbplayers=nbplayers
      # GameRecords is the dictionnary of stats (see above)
      self.GameRecords=GameRecords
      #  Get the maxiumum round number
      self.maxround=self.GameOpts['max_round']

   ############################################################################################
   ###  le jeu  ###############################################################################
   ############################################################################################

   def PostDartsChecks(self,hit,Players,actualround,actualplayer,playerlaunch):
      self.TxtRecap = ""
      return_code = 0
      #On met dans une variable la colone touchée
      TouchedCamembert=hit[1:]
      MultipleCamembert=hit[0:1]
      

      ###### Qd la touche est sur un camembert d'un autre joueur##################################################################################
      x=-1
      for ObjJoueur in Players: #boucle autant de fois que le nb de joueurs
         x=x+1
         #qd la touche est sur un camembert d'un joueur mort et que le toucheur est killer
         if str(TouchedCamembert) == str(Players[x].Camembert) and str(TouchedCamembert) != str(Players[actualplayer].Camembert) and Players[x].alive  == False and Players[actualplayer].killer == True :     
            self.myDisplay.Sound4Touch(hit) #If its a valid hit, play sound
            if MultipleCamembert=='S':
               TouchToAdd=1
            elif MultipleCamembert=='D':
               TouchToAdd=2
            elif MultipleCamembert=='T':
               TouchToAdd=3   
              
            self.TxtRecap += "We take {} points back to player {}\n".format(TouchToAdd,actualplayer)
            Players[actualplayer].NbColVal = Players[actualplayer].NbColVal - TouchToAdd
 
            for ObjJoueur in Players:
               ObjJoueur.LSTColVal[1] = (ObjJoueur.NbColVal,'int')


         # Qd la touche est sur un camembert d'un joueur mort et que le toucheur n'est pas killer
         if str(TouchedCamembert) == str(Players[x].Camembert) and str(TouchedCamembert) != str(Players[actualplayer].Camembert) and Players[x].alive  == False and Players[actualplayer].killer == False :     
            self.myDisplay.PlaySound('whatamess')#If its a valid hit, play sound
            if MultipleCamembert=='S':
               TouchToAdd=1
            elif MultipleCamembert=='D':
               TouchToAdd=2
            elif MultipleCamembert=='T':
               TouchToAdd=3   
              
            self.TxtRecap += "We take {} points back to player {}\n".format(TouchToAdd,actualplayer)
            Players[actualplayer].NbColVal = Players[actualplayer].NbColVal - TouchToAdd
 
            for ObjJoueur in Players:
               ObjJoueur.LSTColVal[1] = (ObjJoueur.NbColVal,'int')
         
         # Qd la touche est sur un camembert d'un autre joueur et que le joueur n'est pas killer
         if str(TouchedCamembert) == str(Players[x].Camembert) and str(TouchedCamembert) != str(Players[actualplayer].Camembert) and Players[actualplayer].killer == False and Players[x].alive  == True  :
            self.myDisplay.PlaySound('whatamess')#If its a valid hit, play sound
            if MultipleCamembert=='S':
               TouchToAdd=1
            elif MultipleCamembert=='D':
               TouchToAdd=2
            elif MultipleCamembert=='T':
               TouchToAdd=3            
                        
            self.TxtRecap += "We take {} points back to player {}\n".format(TouchToAdd,actualplayer)
            Players[actualplayer].NbColVal = Players[actualplayer].NbColVal - TouchToAdd 
            for ObjJoueur in Players:
               ObjJoueur.LSTColVal[1] = (ObjJoueur.NbColVal,'int')
            
            # Le toucheur peut se tuer
            if Players[actualplayer].NbColVal < 0:
               Players[actualplayer].alive  = False
               self.TxtRecap += "Player {} is dead\n".format(actualplayer)
               self.myDisplay.PlaySound('harmonica')#If its a killing hit, play harmonica

         # Qd la touche est sur un camembert d'un joueur vivant et que le toucheur est killer
         elif str(TouchedCamembert) == str(Players[x].Camembert) and str(TouchedCamembert) != str(Players[actualplayer].Camembert) and Players[actualplayer].killer == True and Players[x].alive  == True :
            self.myDisplay.PlaySound('gunshotsimple')#If its a valid hit, play sound

            if MultipleCamembert=='S':
               TouchToAdd=1
            elif MultipleCamembert=='D':
               TouchToAdd=2
            elif MultipleCamembert=='T':
               TouchToAdd=3

            Players[actualplayer].IncrementHits(hit)
            Players[actualplayer].ModifyScore(Players[actualplayer].GetTouchUnit(hit))
            
            self.TxtRecap += "We take {} points back to player {}\n".format(TouchToAdd,x)
            Players[x].NbColVal = Players[x].NbColVal - TouchToAdd 
            
            for ObjJoueur in Players:
               ObjJoueur.LSTColVal[1] = (ObjJoueur.NbColVal,'int')
            # Le toucheur peut dékillerer un joueur
            if Players[x].NbColVal < 5 and Players[x].NbColVal > 0:
               Players[x].killer = False
               self.TxtRecap += "Player  {} is not Killer anymore...\n".format(x)
            # Le toucheur peut tuer un joueur
            if Players[x].NbColVal < 0 and Players[x].alive  == True:
               Players[x].alive  = False
               self.TxtRecap += "Player {} is dead\n".format(x)
               self.myDisplay.PlaySound('harmonica')#If its a killing hit, play harmonica

             

      #######qd la touche est sur le camembert du joueur##########################################################################################
      if str(TouchedCamembert) == str(Players[actualplayer].Camembert) :
         self.myDisplay.Sound4Touch(hit)#If its a valid hit, play sound
         if MultipleCamembert=='S':
            TouchToAdd=1
         elif MultipleCamembert=='D':
            TouchToAdd=2
         elif MultipleCamembert=='T':
            TouchToAdd=3  

         # On ajoute les touches si le joueur a moins de 5 touches
         if Players[actualplayer].NbColVal < 5 and Players[actualplayer].killer == False :
            Players[actualplayer].NbColVal = Players[actualplayer].NbColVal + TouchToAdd
            self.TxtRecap += "Score of player {} is {}\n".format(actualplayer,Players[actualplayer].NbColVal)

            Players[actualplayer].IncrementHits(hit)
            Players[actualplayer].ModifyScore(Players[actualplayer].GetTouchUnit(hit))

         for ObjJoueur in Players:
            ObjJoueur.LSTColVal[1] = (ObjJoueur.NbColVal,'int')
         
         # On enleve les touches si le joueur s'auto touche en tant que killer           
         if str(TouchedCamembert) == str(Players[actualplayer].Camembert) and Players[actualplayer].killer == True:
            Players[actualplayer].NbColVal = Players[actualplayer].NbColVal - TouchToAdd 
            self.TxtRecap += "We take {} points back to player {}\n".format(TouchToAdd,actualplayer)

            for ObjJoueur in Players:
               ObjJoueur.LSTColVal[1] = (ObjJoueur.NbColVal,'int')

            # Le toucheur peut se dékilleriser
            if Players[actualplayer].NbColVal < 5:
               Players[actualplayer].killer = False
               self.TxtRecap += "Player  {} is not Killer anymore...\n".format(actualplayer)
               self.myDisplay.PlaySound('whatamess')

         # Pour chaque touche a ajouter - Si le joueur a 5 touches ou plus
         if Players[actualplayer].NbColVal == 5 or Players[actualplayer].NbColVal > 5:
            Players[actualplayer].killer = True
            self.TxtRecap += "Player {} is killer!!!\n".format(actualplayer)
            self.myDisplay.PlaySound('yiha')

      ######on écrit le status des joueurs : mort ou killer#######################################################################################
      x=-1
      for ObjJoueur in Players:
         x=x+1
         if Players[x].NbColVal < 0 :
            ObjJoueur.LSTColVal[2] = ('killer_skull1','image')
            Players[x].alive = False
         if Players[x].NbColVal > -1 :
            ObjJoueur.LSTColVal[2] = ('','txt')
            Players[x].alive = True
         if Players[x].killer == True:
            ObjJoueur.LSTColVal[2] = ('killer_santiag1','image')
         if Players[x].killer == False and Players[x].alive == True:
            ObjJoueur.LSTColVal[2] = ('','txt')
         if Players[x].NbColVal > 0 and Players[x].NbColVal < 5:
            Players[x].killer = False
            ObjJoueur.LSTColVal[2] = ('','txt')

      # Check if there is a winner (only on last dart thrown, except if winner is current player)
      self.winner = self.CheckWinner(Players,self.nbplayers)
      if self.winner != -1 and (playerlaunch==self.nbdarts or actualplayer==self.winner): # If the function checkwinner returns the id of a winner
         #time.sleep(7)
         self.myDisplay.PlaySound('harmonica')
         time.sleep(1)
         return_code = 3 # Tell the main loop there is a winner

      # Check last round
      if actualround >= int(self.maxround) and actualplayer==self.nbplayers-1 and (playerlaunch == int(self.nbdarts) or return_code == 1):
         self.TxtRecap += "/!\ Last round reached ({})\n".format(actualround)
         return_code = 2

      # Refresh stats - in any case, TotalPoints equals to "score"
      Players[actualplayer].TotalPoints = Players[actualplayer].score
      self.RefreshStats(Players,actualround)

      # Display Recap Text
      self.Logs.Log("DEBUG",self.TxtRecap)
      #Return code to tell the main program if there is a special thing (winnner - game over - etc)
      return return_code

   # Executed before every dart throw
   def PreDartsChecks(self,Players,actualround,actualplayer,playerlaunch):
      return_code = 0
     # First launch - Display Go msg and save backupturn
      if playerlaunch == 1:
         #backup score each round
         self.SaveTurn(Players)
      #on affiche les cases au 1er tour
      if playerlaunch == 1 and actualplayer == 0 and actualround == 1:
         if self.RandomIsFromNet == False:
            self.DefinitCamembert(Players,self.nbplayers)
         self.myDisplay.PlaySound('killerintro')
         #time.sleep(7)         
         for ObjJoueur in Players:
            ObjJoueur.LSTColVal[0] = (ObjJoueur.Camembert,'txt','red')
            ObjJoueur.LSTColVal[1] = (ObjJoueur.NbColVal,'txt')
      # If player is dead - he can't play
      if Players[actualplayer].alive == False and playerlaunch == 1:
         return_code = 4
      return return_code

   # Randomize goal for players
   def DefinitCamembert(self, Players, nbplayers):
      TabCam = []
      y = 0
      for x in range(0,nbplayers):
         
         while y in TabCam or y < 1:
            y = random.randint(1,20)
         TabCam.append(y)
      TabCam=sorted(TabCam)
      for x in range(0,nbplayers):
         Players[x].Camembert = TabCam[x]
         self.TxtRecap += "Goal for player {} is {}\n".format(x,Players[x].Camembert)

   ############################
   # Check if there is a winner
   def CheckWinner(self, Players,nbplayers):
      nbkiller = 0
      nbdead = 0
      actualwinner= -1

      for ObjJoueur in Players:
         if ObjJoueur.killer :
            actualwinner=ObjJoueur.ident
            nbkiller+=1            
         if ObjJoueur.alive == False:
            nbdead += 1
      if nbdead == self.nbplayers - 1 :
         self.TxtRecap += "Player {} wins !\n".format(actualwinner)
         return actualwinner
            
      else:
         self.TxtRecap+="Still no winner ...\n"
         return -1

   ###############
   # Method to frefresh Player Stats - Adapt to the stats you want. They represent mathematical formulas used to calculate stats. Refreshed after every launch
   def RefreshStats(self,Players,actualround):
      for P in Players:
         P.Stats['Score']=P.score
         P.Stats['Points Per Round']=P.AVG(actualround)

   #
   # Returns and Random things, to send to clients in case of a network game
   #
   def GetRandom(self,LSTPlayers,actualround,actualplayer,playerlaunch):
      if actualround == 1 and actualplayer == 0 and playerlaunch == 1:
         myrand=[]
         for Player in LSTPlayers:
            myrand.append(Player.Camembert)
      else:
         myrand = None # Means that there is no random
      return myrand
   #
   # Set Random things, while received by master in case of a network game
   #
   def SetRandom(self,LSTPlayers,actualround,actualplayer,playerlaunch,data):
      if actualround == 1 and actualplayer == 0 and playerlaunch == 1 and data!=None:
         for Player in LSTPlayers:
            Player.Camembert = data[Player.ident]
      self.RandomIsFromNet = True

   #
   # Define the next game players order, depending of previous games' scores
   #
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
   #
   # Check for handicap and record appropriate marks for player
   #
   def CheckHandicap(self,LSTPlayers):
      pass
