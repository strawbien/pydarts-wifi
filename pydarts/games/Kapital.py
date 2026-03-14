# -*- coding: utf-8 -*-
#game by diego aimabouer
#######
from include import CPlayer
from include import CGame
from include import CScores
import time
import operator#?
import collections# To use OrderedDict to sort players from the last score they add
from copy import deepcopy# For backupTurn
#
#
GameLogo = 'Kapital.png' # Background image
Headers = [ '! ','D1','D2','D3',' ',' ',' ' ] # Columns headers - Must be a string
GameOpts = {} # Dictionnay of options in string format
nbdarts = 3
GameRecords = {'Score':'DESC'}

#1=green
#2=red
#3=grey
#4=white

LSTCouleur = { 'SB': 1,'DB': 2,
            'S20': 3, 'D20': 2, 'T20': 2,
            'S19': 4,'D19': 1,'T19': 1,
            'S18': 3,'D18': 2,'T18': 2,
            'S17': 4,'D17': 1,'T17': 1,
            'S16': 4,'D16': 1,'T16': 1,
            'S15': 4,'D15': 1,'T15': 1,
            'S14': 3,'D14': 2,'T14': 2,
            'S13': 3,'D13': 2,'T13': 2,
            'S12': 3,'D12': 2,'T12': 2,
            'S11': 4,'D11': 1,'T11': 1,
            'S10': 3,'D10': 2,'T10': 2,
            'S9': 4,'D9': 1,'T9': 1,
            'S8': 3,'D8': 2,'T8': 2,
            'S7': 3,'D7': 2,'T7': 2,
            'S6': 4,'D6': 1,'T6': 1,
            'S5': 4,'D5': 1,'T5': 1,
            'S4': 4,'D4': 1,'T4': 1,
            'S3': 3,'D3': 2,'T3': 2,
            'S2': 3,'D2': 2,'T2': 2,
            'S1': 4,'D1': 1,'T1': 1
            }

LSTSuite = {   'SB': 25,'DB': 25,
            'S20': 20, 'D20': 20, 'T20': 20,
            'S19': 19,'D19': 19,'T19': 19,
            'S18': 18,'D18': 18,'T18': 18,
            'S17': 17,'D17': 17,'T17': 17,
            'S16': 16,'D16': 16,'T16': 16,
            'S15': 15,'D15': 15,'T15': 15,
            'S14': 14,'D14': 14,'T14': 14,
            'S13': 13,'D13': 13,'T13': 13,
            'S12': 12,'D12': 12,'T12': 12,
            'S11': 11,'D11': 11,'T11': 11,
            'S10': 10,'D10': 10,'T10': 10,
            'S9': 9,'D9': 9,'T9': 9,
            'S8': 8,'D8': 8,'T8': 8,
            'S7': 7,'D7': 7,'T7': 7,
            'S6': 6,'D6': 6,'T6': 6,
            'S5': 5,'D5': 5,'T5': 5,
            'S4': 4,'D4': 4,'T4': 4,
            'S3': 3,'D3': 3,'T3': 3,
            'S2': 2,'D2': 2,'T2': 2,
            'S1': 1,'D1': 1,'T1': 1
            }


LSTCam = ['20','1','18','4','13','6','10','15','2','17','3','19','7','16','8','11','14','9','12','5']

#Extend the basic player
class CPlayerExtended(CPlayer.CPlayer):
   def __init__(self,x,nbjoueurs,Config,res):
      super(CPlayerExtended, self).__init__(x,nbjoueurs,Config,res)
      # Init Player Records to zero
      for GR in GameRecords:
        self.Stats[GR]='0'

# Class of the real game
class Game(CGame.CGame):
   def __init__(self,myDisplay,GameChoice,nbplayers,GameOpts,Config,Logs):
      super(Game, self).__init__(myDisplay, GameChoice, nbplayers, GameOpts, Config, Logs)
      self.GameLogo = GameLogo
      self.Headers = Headers
      self.nbdarts=nbdarts # Total darts the player has to play
      self.maxround=15 # Must be defined, even if it is not an option for the game like here
      self.GameRecords=GameRecords

# Actions done before each dart throw - for example, check if the player is allowed to play
   def PreDartsChecks(self,Players,actualround,actualplayer,playerlaunch):
      if playerlaunch == 1:
         Players[actualplayer].ContratDone = False
         self.JackPot = 0
      return_code = 0 
      self.TxtRecap += ""
      # Init
      if playerlaunch == 1 :
         Players[actualplayer].ContratDone = False # First Dart, reset contract to NOT DONE.
         self.SaveTurn(Players)         
         Players[actualplayer].scoredanscontrat=0
         # Clear table for current player
         for i in range(1,4):
            Players[actualplayer].LSTColVal[i] = ('','txt','grey')
         if actualround==13:
            self.LSTcotecote = []

      #music introduction 
      if playerlaunch == 1 and actualplayer == 0 and actualround == 1:
         time.sleep(1)
         self.myDisplay.PlaySound('kapitalintro')
         #time.sleep(7)
      
      #myDisplay du contrat
      if playerlaunch == 1 and actualround == 1 :
         for ObjJoueur in Players:
            ObjJoueur.LSTColVal[0] = (str('K'),'txt','white')
      if playerlaunch == 1 and actualround == 2 :
         for ObjJoueur in Players:
            ObjJoueur.LSTColVal[0] = (str('20'),'txt','white')
      if playerlaunch == 1 and actualround == 3 :
         for ObjJoueur in Players:
            ObjJoueur.LSTColVal[0] = (str('Trpl'),'txt','white')
      if playerlaunch == 1 and actualround == 4 :
         for ObjJoueur in Players:
            ObjJoueur.LSTColVal[0] = (str('19'),'txt','white')
      if playerlaunch == 1 and actualround == 5 :
         for ObjJoueur in Players:
            ObjJoueur.LSTColVal[0] = (str('Dble'),'txt','white')
      if playerlaunch == 1 and actualround == 6 :
         for ObjJoueur in Players:
            ObjJoueur.LSTColVal[0] = (str('18'),'txt','white')
      if playerlaunch == 1 and actualround == 7 :
         for ObjJoueur in Players:
            ObjJoueur.LSTColVal[0] = (str('Kolr'),'txt','white')
      if playerlaunch == 1 and actualround == 8 :
         for ObjJoueur in Players:
            ObjJoueur.LSTColVal[0] = (str('17'),'txt','white')
      if playerlaunch == 1 and actualround == 9 :
         for ObjJoueur in Players:
            ObjJoueur.LSTColVal[0] = (str('57'),'txt','white')
      if playerlaunch == 1 and actualround == 10 :
         for ObjJoueur in Players:
            ObjJoueur.LSTColVal[0] = (str('16'),'txt','white')
      if playerlaunch == 1 and actualround == 11:
         for ObjJoueur in Players:
            ObjJoueur.LSTColVal[0] = (str('Suite'),'txt','white')
      if playerlaunch == 1 and actualround == 12:
         for ObjJoueur in Players:
            ObjJoueur.LSTColVal[0] = (str('15'),'txt','white')
      if playerlaunch == 1 and actualround == 13 :
         for ObjJoueur in Players:
            ObjJoueur.LSTColVal[0] = (str('Kkot'),'txt','white')
      if playerlaunch == 1 and actualround == 14 :
         for ObjJoueur in Players:
            ObjJoueur.LSTColVal[0] = (str('14'),'txt','white')
      if playerlaunch == 1 and actualround == 15 :
         for ObjJoueur in Players:
            ObjJoueur.LSTColVal[0] = (str('B'),'txt','white')

      return return_code
        

##########################################################################################################################################
# le jeu  ################################################################################################################################
##########################################################################################################################################

   def PostDartsChecks(self,key,Players,actualround,actualplayer,playerlaunch):
      return_code = 0
      self.TxtRecap = ""
      #if playerlaunch == 1:
      #   Players[actualplayer].ContratDone = False
      #   self.JackPot = 0
      TouchedCamembert=key[1:]
      MultipleCamembert=key[0:1]
      Couleur=LSTCouleur[key]
      ValeurCamembert=LSTSuite[key]         

      if MultipleCamembert=='S':
         MultipleTouch=1
      elif MultipleCamembert=='D':
         MultipleTouch=2
      elif MultipleCamembert=='T':
         MultipleTouch=3

      #affiche la touche du joueur dans une case
      if Couleur == 1 : LedColor = 'green'
      elif Couleur == 2 : LedColor = 'red'
      elif Couleur == 3 : LedColor = 'grey'
      elif Couleur == 4 : LedColor = 'white'
      
      Players[actualplayer].LSTColVal[playerlaunch] = (str(key),'txt',LedColor)
      
###############################################################################################################################################
###### KAPITAL # 1 ###########################################################################################################################
      if actualround == 1 :
         Players[actualplayer].ModifyScore(self.ScoreMap.get(key))
         #self.myDisplay.DisplayScore(Players[actualplayer],Players[actualplayer].posy,Players[actualplayer].score)
         Players[actualplayer].ContratDone = True
###############################################################################################################################################
###### le 20 # 2 ##############################################################################################################################
      if actualround == 2 :    
         # si le joueur reusssit un 20 : 
         if playerlaunch == 1 : #Init
            self.JackPot = 0
         if str(TouchedCamembert) == '20' :  
            self.myDisplay.PlaySound('kapitalcontratok')
            self.JackPot += 1
            self.TxtRecap += "Bien joué Calhagan ! {} touches !\n".format(self.JackPot)
            if self.JackPot == 3 :
               time.sleep(1)
               self.myDisplay.PlaySound('kapital3goodhits')

            # on modifie le score dans son contrat
            Players[actualplayer].scoredanscontrat =  Players[actualplayer].scoredanscontrat + self.ScoreMap.get(key) # ??
            #a chaque touche reussie on augmente son score
            Players[actualplayer].ModifyScore(self.ScoreMap.get(key))         
            Players[actualplayer].ContratDone = True
         
###############################################################################################################################################
###### le TRIPLE # 3 ##########################################################################################################################
      if actualround == 3 :
         #si la touche est un triple
         if playerlaunch == 1 :
               self.JackPot = 0
         if MultipleTouch == 3 :
            self.myDisplay.PlaySound('kapitalcontratok')
            self.JackPot += 1
            if self.JackPot == 3 :
               time.sleep(1)
               self.myDisplay.PlaySound('kapital3goodhits')
            Players[actualplayer].ContratDone = True
            # on modifie le score dans son contrat
            Players[actualplayer].scoredanscontrat =  Players[actualplayer].scoredanscontrat + self.ScoreMap.get(key)
            #a chaque touche reussit on augmente son score
            Players[actualplayer].ModifyScore(self.ScoreMap.get(key))         

###############################################################################################################################################
###### le 19 # 4 ##############################################################################################################################
      if actualround == 4 :    
         # si le joueur reusssit un 19 : 
         if playerlaunch == 1 :
               self.JackPot = 0
         if str(TouchedCamembert) == '19' :
            Players[actualplayer].ContratDone = True
            self.myDisplay.PlaySound('kapitalcontratok')
            self.JackPot += 1
            if self.JackPot == 3 :
               time.sleep(1)
               self.myDisplay.PlaySound('kapital3goodhits')
            
            # on modifie le score dans son contrat
            Players[actualplayer].scoredanscontrat =  Players[actualplayer].scoredanscontrat + self.ScoreMap.get(key)
            #a chaque touche reussit on augmente son score
            Players[actualplayer].ModifyScore(self.ScoreMap.get(key))         

###############################################################################################################################################
###### le DOUBLE # 5 ##########################################################################################################################
      if actualround == 5 :
         if playerlaunch == 1 :
            self.JackPot = 0
      #si la touche est un double
         if MultipleTouch == 2 :
            Players[actualplayer].ContratDone = True
            self.myDisplay.PlaySound('kapitalcontratok')
            self.JackPot += 1
            if self.JackPot == 3 :
               time.sleep(1)
               self.myDisplay.PlaySound('kapital3goodhits')
            
            # on modifie le score dans son contrat
            Players[actualplayer].scoredanscontrat =  Players[actualplayer].scoredanscontrat + self.ScoreMap.get(key)
            #a chaque touche reussit on augmente son score
            Players[actualplayer].ModifyScore(self.ScoreMap.get(key))         
            #si le joueuer ne reussit pas de triple le score dans son contrat est 0
            #si apres sa 3eme flechette le score dans son contrat est 0, il divise par 2 son total

###############################################################################################################################################
###### le 18 # 6 ##############################################################################################################################
      
      if actualround == 6 :    
         if playerlaunch == 1 :
            self.JackPot = 0
# si le joueur reusssit un 18 :      
         if str(TouchedCamembert) == '18' :
            Players[actualplayer].ContratDone = True
            self.myDisplay.PlaySound('kapitalcontratok')
            self.JackPot += 1
            if self.JackPot == 3:
               time.sleep(1)
               self.myDisplay.PlaySound('kapital3goodhits')
            # on modifie le score dans son contrat
            Players[actualplayer].scoredanscontrat =  Players[actualplayer].scoredanscontrat + self.ScoreMap.get(key)
            #a chaque touche reussit on augmente son score
            Players[actualplayer].ModifyScore(self.ScoreMap.get(key))         
 
###############################################################################################################################################
###### la COULEUR # 7 #########################################################################################################################
      if actualround == 7 :
         # on modifie le score dans son contrat
         Players[actualplayer].scoredanscontrat =  Players[actualplayer].scoredanscontrat + self.ScoreMap.get(key)
         if playerlaunch == 1 :
            self.LSTcouleurdanscontrat = []
         # creation de la liste du joueur :
         self.LSTcouleurdanscontrat.append(LSTCouleur[key])
         # 2nd dart
         if len(self.LSTcouleurdanscontrat) == 2:
            if self.LSTcouleurdanscontrat[0] != self.LSTcouleurdanscontrat[1]:
               self.myDisplay.PlaySound('kapitalpressure')
       # 3rd dart
         if len(self.LSTcouleurdanscontrat) == 3:
            if self.LSTcouleurdanscontrat[0] != self.LSTcouleurdanscontrat[1] and self.LSTcouleurdanscontrat[0] != 0 and self.LSTcouleurdanscontrat[0] != self.LSTcouleurdanscontrat[2] and self.LSTcouleurdanscontrat[2] != self.LSTcouleurdanscontrat[1]:
               self.TxtRecap += "Hehe ! Good Job !\n"
               Players[actualplayer].ContratDone = True
               self.myDisplay.PlaySound('kapitalhardcontrat')
               time.sleep(2)
               self.myDisplay.PlaySound('kapitalhardcontrat')            
               # on modifie le score 
               Players[actualplayer].score =  Players[actualplayer].score + Players[actualplayer].scoredanscontrat          

###############################################################################################################################################
###### le 17 # 8 ##############################################################################################################################
      if actualround == 8 :    
         if playerlaunch == 1 :
            self.JackPot = 0
         # si le joueur reusssit un 17 :      
         if str(TouchedCamembert) == '17' : 
            Players[actualplayer].ContratDone = True
            self.myDisplay.PlaySound('kapitalcontratok')
            self.JackPot += 1
            if self.JackPot == 3 :
               time.sleep(1)
               self.myDisplay.PlaySound('kapital3goodhits')
            
            # on modifie le score dans son contrat
            Players[actualplayer].scoredanscontrat =  Players[actualplayer].scoredanscontrat + self.ScoreMap.get(key)
            #a chaque touche reussit on augmente son score
            Players[actualplayer].ModifyScore(self.ScoreMap.get(key))         
        
###############################################################################################################################################
###### le 57 # 9 ##############################################################################################################################
      if actualround == 9 :    
         Players[actualplayer].scoredanscontrat =  Players[actualplayer].scoredanscontrat + self.ScoreMap.get(key)
         if Players[actualplayer].scoredanscontrat == 57 :
            Players[actualplayer].ContratDone = True
            self.myDisplay.PlaySound('kapitalhardcontrat')
            time.sleep(2)
            self.myDisplay.PlaySound('kapitalhardcontrat')
            #on ajoute 57 a son score et on l'affiche
            Players[actualplayer].score = Players[actualplayer].score + 57        
            #Players[actualplayer].scoredanscontrat = 99 # ??
            return_code = 1 # Contract is done, next please!
            
####################################################################################################################################################
####### le 16  # 10 ############################################################################################################################
      if actualround == 10 :    
         if playerlaunch == 1 :
            self.JackPot = 0
# si le joueur reusssit un 16 :      
         if str(TouchedCamembert) == '16' : 
            Players[actualplayer].ContratDone = True
            self.myDisplay.PlaySound('kapitalcontratok')
            self.JackPot += 1
            if self.JackPot == 3 :
               time.sleep(1)
               self.myDisplay.PlaySound('kapital3goodhits')
            
            # on modifie le score dans son contrat
            Players[actualplayer].scoredanscontrat =  Players[actualplayer].scoredanscontrat + self.ScoreMap.get(key)
            #a chaque touche reussit on augmente son score
            Players[actualplayer].ModifyScore(self.ScoreMap.get(key))         
         
###############################################################################################################################################
###### la SUITE # 11 ##########################################################################################################################
      if actualround == 11 :
         # on modifie le score dans son contrat
         Players[actualplayer].scoredanscontrat =  Players[actualplayer].scoredanscontrat + self.ScoreMap.get(key)
         if playerlaunch == 1 :
            self.LSTSuitedanscontrat = []
         # creation de la liste du joueur :
         self.LSTSuitedanscontrat.append(ValeurCamembert)
         self.LSTSuitedanscontrat.sort()
##########si le joueur a fait 2 camemberts en suite : pressure!###############################
         if len(self.LSTSuitedanscontrat) == 2:
          if self.LSTSuitedanscontrat[0] + 1 == self.LSTSuitedanscontrat[1] or self.LSTSuitedanscontrat[0] + 2 == self.LSTSuitedanscontrat[1] or 25 in self.LSTSuitedanscontrat:
            self.myDisplay.PlaySound('kapitalpressure')

######### 3 camembert de suite ##################################
         if len(self.LSTSuitedanscontrat) == 3:
            if (self.LSTSuitedanscontrat[0] + 1 == self.LSTSuitedanscontrat[1] and self.LSTSuitedanscontrat[1] + 1 == self.LSTSuitedanscontrat[2] and 25 not in self.LSTSuitedanscontrat) or (self.LSTSuitedanscontrat[0] + 1 == self.LSTSuitedanscontrat[1] and self.LSTSuitedanscontrat[2] == 25) or (self.LSTSuitedanscontrat[0] + 2 == self.LSTSuitedanscontrat[1] and self.LSTSuitedanscontrat[2] == 25) or (self.LSTSuitedanscontrat[2] == 25 and self.LSTSuitedanscontrat[1] == 25):
               Players[actualplayer].ContratDone = True
               self.myDisplay.PlaySound('kapitalhardcontrat')
               time.sleep(2)
               self.myDisplay.PlaySound('kapitalhardcontrat')
               self.TxtRecap += "Suite done !\n"
               # on modifie le score 
               Players[actualplayer].score =  Players[actualplayer].score + Players[actualplayer].scoredanscontrat 
               #a chaque touche reussit on augmente son score        
               #self.myDisplay.DisplayScore(Players[actualplayer],Players[actualplayer].posy,Players[actualplayer].score)          
            else:
               self.TxtRecap += "Looser !\n"
###############################################################################################################################################
###### le 15  # 12 ############################################################################################################################
      if actualround == 12 :    
         if playerlaunch == 1 :
            self.JackPot = 0
# si le joueur reusssit un 15 :      
         if str(TouchedCamembert) == '15' : 
            Players[actualplayer].ContratDone = True
            self.myDisplay.PlaySound('kapitalcontratok')
            self.JackPot += 1 
            if self.JackPot == 3:
               time.sleep(1)
               self.myDisplay.PlaySound('kapital3goodhits')

            # on modifie le score dans son contrat
            Players[actualplayer].scoredanscontrat =  Players[actualplayer].scoredanscontrat + self.ScoreMap.get(key)
            #a chaque touche reussit on augmente son score
            Players[actualplayer].ModifyScore(self.ScoreMap.get(key))         

###############################################################################################################################################
###### le cote cote #13#######################################################################################################################
      if actualround == 13 :
         if playerlaunch == 1:
            self.LSTcotecote = []

         # on modifie le score dans son contrat
         Players[actualplayer].scoredanscontrat =  Players[actualplayer].scoredanscontrat + self.ScoreMap.get(key)
         self.TxtRecap += "Votre cote-cote vous rapporte actuellement {} points\n".format(Players[actualplayer].scoredanscontrat)
         # creation de la liste du joueur :
         if TouchedCamembert != 'B':
            temp = LSTCam.index(TouchedCamembert)  
            self.LSTcotecote.append(temp)
         else:
            self.LSTcotecote.append(25)

         self.TxtRecap += "Votre cote-cote en est ici : {}\n".format(self.LSTcotecote)

         self.LSTcotecote.sort()

         ###########si le cotecote est réussi
         #if self.LSTcotecote == self.LSTcotecote1 or self.LSTcotecote == self.LSTcotecote2 or self.LSTcotecote == self.LSTcotecote3 or self.LSTcotecote == self.LSTcotecote4 or self.LSTcotecote == self.LSTcotecote5 or self.LSTcotecote == self.LSTcotecote6 or self.LSTcotecote == self.LSTcotecote7 or self.LSTcotecote == self.LSTcotecote8 or self.LSTcotecote == self.LSTcotecote9 or self.LSTcotecote == self.LSTcotecote10 or self.LSTcotecote == self.LSTcotecote11 or self.LSTcotecote == self.LSTcotecote12 or self.LSTcotecote == self.LSTcotecote13 or self.LSTcotecote == self.LSTcotecote14 or self.LSTcotecote == self.LSTcotecote15 or self.LSTcotecote == self.LSTcotecote16 or self.LSTcotecote == self.LSTcotecote17 or self.LSTcotecote == self.LSTcotecote18 or self.LSTcotecote == self.LSTcotecote19 or self.LSTcotecote == self.LSTcotecote20 or self.LSTcotecote == self.LSTcotecote21 or self.LSTcotecote == self.LSTcotecote22 or self.LSTcotecote == self.LSTcotecote23 or self.LSTcotecote == self.LSTcotecote24 or self.LSTcotecote == self.LSTcotecote25 or self.LSTcotecote == self.LSTcotecote26 or self.LSTcotecote == self.LSTcotecote27 or self.LSTcotecote == self.LSTcotecote28 or self.LSTcotecote == self.LSTcotecote29 or self.LSTcotecote == self.LSTcotecote30 or self.LSTcotecote == self.LSTcotecote31 or self.LSTcotecote == self.LSTcotecote32 or self.LSTcotecote == self.LSTcotecote33 or self.LSTcotecote == self.LSTcotecote34 or self.LSTcotecote == self.LSTcotecote35 or self.LSTcotecote == self.LSTcotecote36 or self.LSTcotecote == self.LSTcotecote37 or self.LSTcotecote == self.LSTcotecote38 or self.LSTcotecote == self.LSTcotecote39 or self.LSTcotecote == self.LSTcotecote40 or self.LSTcotecote == self.LSTcotecote41 or self.LSTcotecote == self.LSTcotecote42 or self.LSTcotecote == self.LSTcotecote43 or self.LSTcotecote == self.LSTcotecote44 or self.LSTcotecote == self.LSTcotecote45 or self.LSTcotecote == self.LSTcotecote46 or self.LSTcotecote == self.LSTcotecote47 or self.LSTcotecote == self.LSTcotecote48 or self.LSTcotecote == self.LSTcotecote49 or self.LSTcotecote == self.LSTcotecote50 or self.LSTcotecote == self.LSTcotecote51 or self.LSTcotecote == self.LSTcotecote52 or self.LSTcotecote == self.LSTcotecote53 or self.LSTcotecote == self.LSTcotecote54 or self.LSTcotecote == self.LSTcotecote55 or self.LSTcotecote == self.LSTcotecote56 or self.LSTcotecote == self.LSTcotecote57 or self.LSTcotecote == self.LSTcotecote58 or self.LSTcotecote == self.LSTcotecote59 or self.LSTcotecote == self.LSTcotecote60 or self.LSTcotecote == self.LSTcotecote61 or self.LSTcotecote == self.LSTcotecote62 or self.LSTcotecote == self.LSTcotecote63 or self.LSTcotecote == self.LSTcotecote64 or self.LSTcotecote == self.LSTcotecote65 or self.LSTcotecote == self.LSTcotecote66 or self.LSTcotecote == self.LSTcotecote67 or self.LSTcotecote == self.LSTcotecote68 or self.LSTcotecote == self.LSTcotecote69 or self.LSTcotecote == self.LSTcotecote70 or self.LSTcotecote == self.LSTcotecote71 or self.LSTcotecote == self.LSTcotecote72 or self.LSTcotecote == self.LSTcotecote73 or self.LSTcotecote == self.LSTcotecote74 or self.LSTcotecote == self.LSTcotecote75 or self.LSTcotecote == self.LSTcotecote76 or self.LSTcotecote == self.LSTcotecote77 or self.LSTcotecote == self.LSTcotecote78 or self.LSTcotecote == self.LSTcotecote79 or self.LSTcotecote == self.LSTcotecote80 or self.LSTcotecote == self.LSTcotecote81 :
         if len(self.LSTcotecote) == 3:
            if self.CheckKotKot(self.LSTcotecote):
               Players[actualplayer].ContratDone = True
               self.myDisplay.PlaySound('kapitalhardcontrat')
               time.sleep(2)
               self.myDisplay.PlaySound('kapitalhardcontrat')
               self.TxtRecap += "Kotkot réussi !!! Good Job mate !\n"
               # on modifie le score 
               Players[actualplayer].score =  Players[actualplayer].score + Players[actualplayer].scoredanscontrat 
            else :
               self.TxtRecap += "Looser.\n"

###############################################################################################################################################
###### le 14  # 14 ############################################################################################################################
      if actualround == 14 :    
         if playerlaunch == 1 :
            self.JackPot = 0
# si le joueur reusssit un 14 :      
         if str(TouchedCamembert) == '14' : 
            Players[actualplayer].ContratDone = True
            self.myDisplay.PlaySound('kapitalcontratok')
            self.JackPot +=1
            if self.JackPot == 3 :
               time.sleep(1)
               self.myDisplay.PlaySound('kapital3goodhits')
            
            # on modifie le score dans son contrat
            Players[actualplayer].scoredanscontrat =  Players[actualplayer].scoredanscontrat + self.ScoreMap.get(key)
            #a chaque touche reussit on augmente son score
            Players[actualplayer].ModifyScore(self.ScoreMap.get(key))         

###############################################################################################################################################
###### le  centre # 15 ########################################################################################################################
      if actualround == 15 :    
         if playerlaunch == 1 :
            self.JackPot = 0
# si le joueur reusssit une bulle :      
         if str(TouchedCamembert) == 'B' :
            self.JackPot+=1
            Players[actualplayer].ContratDone = True
            self.myDisplay.PlaySound('kapitalhardcontrat')
            time.sleep(2)
            self.myDisplay.PlaySound('kapitalhardcontrat')
            if self.JackPot == 3:
               time.sleep(1)
               self.myDisplay.PlaySound('kapital3goodhits')
            
            # on modifie le score dans son contrat
            Players[actualplayer].scoredanscontrat =  Players[actualplayer].scoredanscontrat + self.ScoreMap.get(key)
            #a chaque touche reussit on augmente son score
            Players[actualplayer].ModifyScore(self.ScoreMap.get(key))         

###############################################################################################################################################
############################################################################################################################################
      # If contrat not Done : division
      if playerlaunch == 3 and Players[actualplayer].ContratDone == False:
         self.myDisplay.PlaySound('kapitaldivision')
         Players[actualplayer].score = Players[actualplayer].score / 2

      # You may want to count how many touches (Simple = 1 touch, Double = 2 touches, Triple = 3 touches)
      Players[actualplayer].IncrementHits(key)

      # You may want to count darts played
      Players[actualplayer].dartsthrown += 1
      
      # It is recommanded to update stats every dart thrown
      self.RefreshStats(Players,actualround)

      #Check actual winnner if last round reached
      if actualround == 15 :
         self.winner = self.CheckWinner(Players)
         if self.winner != -1:
            self.TxtRecap+="Current winner is Player {}\n".format(self.winner)
         # Last round
         if actualplayer==self.nbplayers-1 and playerlaunch == int(self.nbdarts):
            self.TxtRecap += "\n/!\ Last round reached ({})\n".format(actualround)
            if self.winner != -1:
               return_code = 3
               BlinkText = "Winner : P.{} !".format(self.winner)
            else:
               return_code = 2

      # Adding Jackpot to debug
      self.TxtRecap += "\n Le Jackpot en est à {}".format(self.JackPot)
      
      # Display Recapitulation Text
      self.Logs.Log("DEBUG",self.TxtRecap)
      return return_code     
      
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
         self.TxtRecap+="/!\ There is a score deuce ! Two people have {}\n. No winner!\n".format(bestscore)
         bestplayer = -1
      return bestplayer

   #################
   # Function launched when the player put player button before having launched all his darts
   def EarlyPlayerButton(self,Players,actualplayer,actualround):
      # Jump to next player by default
      return_code=1
      self.TxtRecap = "Pneu (or early player buttton) function\n"
      # If contract not done
      if Players[actualplayer].ContratDone == False:
         # Play division sound
         self.myDisplay.PlaySound('kapitaldivision')
         # Divide score
         Players[actualplayer].score = Players[actualplayer].score / 2
      # Check actual winnner if last round reached
      if actualround == 15 :
         self.winner = self.CheckWinner(Players)
         if self.winner != -1:
            self.TxtRecap+="Current winner is Player {}\n".format(self.winner)
         # Last round
         if actualplayer==self.nbplayers-1:
            self.TxtRecap += "\n/!\ Last round reached ({})\n".format(actualround)
            if self.winner != -1:
               return_code = 3
               BlinkText = "Winner : P.{} !".format(self.winner)
            else:
               return_code=2
      self.Logs.Log('DEBUG',self.TxtRecap)
      return return_code

   ###############
   # Method to frefresh Player Stats - Adapt to the stats you want. They represent mathematical formulas used to calculate stats. Refreshed after every launch
   def RefreshStats(self,Players,actualround):
      for P in Players:
         P.Stats['Score']=P.score

   #
   # Check if KotKot is True or not (index goes from 0 to 19 (round the clock) and 25 for bull
   #      
   def CheckKotKot(self,ind):
      # No bulleye
      if 25 not in self.LSTcotecote and ((self.LSTcotecote[2]-self.LSTcotecote[1] == 1 and self.LSTcotecote[1]-self.LSTcotecote[0] == 1) or (self.LSTcotecote[0]==0 and self.LSTcotecote[2]==19 and (self.LSTcotecote[1] == 1 or self.LSTcotecote[1] == 18))): # If indexes are contiguous and no center
         return True
      # Two bullseye
      elif self.LSTcotecote[2] == 25 and self.LSTcotecote[1] == 25:
         return True
      # One bullseye and substract ok
      elif self.LSTcotecote[2] == 25 and ((self.LSTcotecote[1]-self.LSTcotecote[0] == 1) or (self.LSTcotecote[1]-self.LSTcotecote[0] == 2)):
         return True
      # One bullseye and substract nok
      elif self.LSTcotecote[2] == 25 and ((self.LSTcotecote[1] == 18 and self.LSTcotecote[0]==0) or (self.LSTcotecote[1]==19 and self.LSTcotecote[0]==0) or (self.LSTcotecote[1] == 19 and self.LSTcotecote[0]==1)):
         return True
      else:
         return False

   #
   # Returns and Random things, to send to clients in case of a network game
   #
   def GetRandom(self,Players,actualround,actualplayer,playerlaunch):
      return None # Means that there is no random
   
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
