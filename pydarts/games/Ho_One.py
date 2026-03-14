# -*- coding: utf-8 -*-
# Game by ... poilou !
######
from include import CPlayer
from include import CGame
from include import CScores
from include import CStats
from include import CHandicap
import collections# To use OrderedDict to sort players from the last score they add
from copy import deepcopy# For backupTurn

GameLogo = 'Ho_One.png' # Background image - relative to images folder
Headers = [ "D1","D2","D3","","Rnd","PPD","PPR" ] # Columns headers - Must be a string
GameOpts = {'startingat':'301','max_round':'20','double_in':'False','double_out':'False','master_in':'False','master_out':'False','league':'False','split_bull':'True'} # Dictionnay of options - will be used at the initial screen
GameRecords = {'Points Per Round':'DESC','Points Per Dart':'DESC'} # Dictionnary of stats and dislay order (For exemple, Avg is displayed in descending order)
nbdarts = 3 # How many darts the player is allowed to throw

############
# Extend the basic player's class
############
class CPlayerExtended(CPlayer.CPlayer):
    def __init__(self,x,NbPlayers,Config,res):
        super(CPlayerExtended, self).__init__(x,NbPlayers,Config,res)
        self.PrePlayScore = None
        self.Frozen = False
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
        # Config are the are the options contained in your config file
        self.GameLogo = GameLogo
        self.Headers = Headers
        self.nbdarts=nbdarts # Tohttps://www.dsih.fr/tal darts the player has to play
        # Load handicap and stat classes
        self.Handicap = CHandicap.CHandicap('Ho_One',Config,self.Logs)
        self.Stats = CStats.CStats('Ho_One',self.Logs)
        #  Get the maxiumum round number
        self.maxround=self.GameOpts['max_round']
        if nbplayers != 4 and GameOpts['league']=='True':
            self.Logs.Log("ERROR","League option can only be used with 4 players! Disabling league play!")
            self.GameOpts['league'] = 'False'
        elif GameOpts['league']=='True':
            self.myDisplay.Teaming = True
        # Decide on BullEye value
        if GameOpts['split_bull']=='False':
            self.ScoreMap.update({'SB': 50})

    ###########################################################################################
    # Actions done before each dart throw - for example, check if the player is allowed to play
    def PreDartsChecks(self,LSTPlayers,actualround,actualplayer,playerlaunch):
        return_code = 0
        teammatescore = 0
        otherteamscore = 0
        self.Frozen = False
        # Set score at startup
        if actualround == 1 and playerlaunch == 1 and actualplayer == 0:
            try:
                LST = self.CheckHandicap(LSTPlayers)
            except Exception as e:
                self.Logs.Log("ERROR","Handicap failed : {}".format(e))
            for Player in LSTPlayers:
                # Init score
                if self.GameOpts['league'] == 'False':
                    Player.score = int(self.GameOpts['startingat'])
                elif self.GameOpts['league'] == 'True':
                    Player.score = int(LST[Player.ident])
                # Init Avg
                Player.Avg = 0
            self.myDisplay.PlaySound('ho_one_intro')

        # Each new player
        if playerlaunch==1:
            LSTPlayers[actualplayer].pointsinround = 0
            self.SaveTurn(LSTPlayers)
            LSTPlayers[actualplayer].PrePlayScore = LSTPlayers[actualplayer].score # Backup current score

            #Reset display Table
            LSTPlayers[actualplayer].LSTColVal = []
            # Clean all next boxes
            for i in range(0,7):
                LSTPlayers[actualplayer].LSTColVal.append(['','int'])
        # Display Avg
        if actualround == 1 and playerlaunch == 1:
            LSTPlayers[actualplayer].LSTColVal[5] = (0.0,'int')
            LSTPlayers[actualplayer].LSTColVal[6] = (0.0,'int')
        else:
            LSTPlayers[actualplayer].LSTColVal[5] = (LSTPlayers[actualplayer].ShowPPD(),'int')
            LSTPlayers[actualplayer].LSTColVal[6] = (LSTPlayers[actualplayer].ShowPPR(),'int')
        # Clean next boxes
        for i in range(playerlaunch-1,self.nbdarts):
            LSTPlayers[actualplayer].LSTColVal[i]=('','int')

        # Get Playing Suggestions
        PossibleLaunch = self.SearchPossibleLaunch(LSTPlayers[actualplayer].score,playerlaunch)

        # Display if there is a suggestion to display
        if len(PossibleLaunch)>=1:LSTPlayers[actualplayer].LSTColVal[playerlaunch-1] = (PossibleLaunch[0],'int','green')
        if len(PossibleLaunch)>=2:LSTPlayers[actualplayer].LSTColVal[playerlaunch] = (PossibleLaunch[1],'int','green')
        if len(PossibleLaunch)>=3:LSTPlayers[actualplayer].LSTColVal[playerlaunch+1] = (PossibleLaunch[2],'int','green')
        
        #Get scores for teammate and opposite team and see if freeze rule is in effect
        if self.GameOpts['league'] == 'True':
             teammate = self.Mate(actualplayer,len(LSTPlayers))
             teammatescore = LSTPlayers[teammate].score
             if actualplayer == 0 or actualplayer == 2:
                  otherteamscore += LSTPlayers[1].score
                  otherteamscore += LSTPlayers[3].score
             else:
                  otherteamscore += LSTPlayers[0].score
                  otherteamscore += LSTPlayers[2].score
             #if teammatescore is not lower than otherteamscore, freeze rule is active
             if teammatescore >= otherteamscore:
                  self.Logs.Log("DEBUG",'FROZEN!!!')
                  self.Frozen = True
                  LSTPlayers[actualplayer].LSTColVal[3] = ('FRZ','str','red')
             else:
                  self.Frozen = False
                  LSTPlayers[actualplayer].LSTColVal[3] = ('','str','red')

        # Print debug output
        self.Logs.Log("DEBUG",self.TxtRecap)
        return return_code        

    ###############
    # Function run after each dart throw - for example, add points to player
    def PostDartsChecks(self,hit,LSTPlayers,actualround,actualplayer,playerlaunch):
        return_code = 0
        # Define a var for substracted score
        subscore = LSTPlayers[actualplayer].score - self.ScoreMap[hit]
        #################################
        # Starting Ho One
        if LSTPlayers[actualplayer].score == int(self.GameOpts['startingat']):
            # All good opening cases
            if     (  
                    (self.GameOpts['double_in']=='True' and hit[:1] == 'D') or
                    (self.GameOpts['master_in']=='True' and (hit[:1] == 'D' or hit[:1] == 'T' or hit[1:] == 'B')) or
                    (self.GameOpts['double_in']=='False' and self.GameOpts['master_in']=='False')
                    ):
                self.myDisplay.Sound4Touch(hit) # Good start !
                LSTPlayers[actualplayer].score = subscore # Substract
                LSTPlayers[actualplayer].pointsinround += self.ScoreMap[hit] # Keep total for this round
                LSTPlayers[actualplayer].TotalPoints += self.ScoreMap[hit] #for ppd,ppr
        # Ending Ho One
        elif subscore == 0:
            if self.Frozen == True:
                text = "You were frozen and reached zero!  You lose!"
                self.myDisplay.InfoMessage(["You were frozen and reached zero!  You lose!"], 3000,'red','middle','huge')
                self.myDisplay.PlaySound('whatamess')
                return_code = 3
                if actualplayer == 0 or actualplayer == 2:
                     self.winner = actualplayer + 1
                else:
                     self.winner = actualplayer - 1
            # All closing cases
            elif     (  
                    (self.GameOpts['double_out']=='True' and hit[:1] == 'D') or
                    (self.GameOpts['master_out']=='True' and (hit[:1] == 'D' or hit[:1] == 'T' or hit[1:] == 'B')) or
                    (self.GameOpts['double_out']=='False' and self.GameOpts['master_out']=='False')
                    ):
                self.myDisplay.Sound4Touch(hit)
                return_code = 3
                self.winner = actualplayer
                LSTPlayers[actualplayer].score = 0
                LSTPlayers[actualplayer].TotalPoints += self.ScoreMap[hit] #for ppd,ppr
            # else it is a fail
            else:
                return_code = 1 # Next player
                LSTPlayers[actualplayer].score = LSTPlayers[actualplayer].PrePlayScore
                LSTPlayers[actualplayer].TotalPoints -= LSTPlayers[actualplayer].pointsinround #take hit back from total score
                self.myDisplay.PlaySound('whatamess')
        # Case for score = 1 and *_out option enabled
        elif subscore == 1 and (self.GameOpts['double_out']=='True' or self.GameOpts['master_out']=='True'):
            return_code = 1 # Next player
            LSTPlayers[actualplayer].score = LSTPlayers[actualplayer].PrePlayScore
            LSTPlayers[actualplayer].TotalPoints -= LSTPlayers[actualplayer].pointsinround #for ppd,ppr
            self.myDisplay.PlaySound('whatamess')
        # Classic case (between start and end)
        elif subscore > 0:
            self.myDisplay.Sound4Touch(hit) # Touched !
            LSTPlayers[actualplayer].score = subscore # Substract
            LSTPlayers[actualplayer].pointsinround += self.ScoreMap[hit] # Keep total for this round
            LSTPlayers[actualplayer].TotalPoints += self.ScoreMap[hit] #for ppd,ppr
        # Any other case it is a fail
        else:
            return_code = 1 # Next player
            LSTPlayers[actualplayer].score = LSTPlayers[actualplayer].PrePlayScore
            LSTPlayers[actualplayer].TotalPoints -= LSTPlayers[actualplayer].pointsinround #for ppd,ppr
            self.myDisplay.PlaySound('whatamess')


        # Check last round
        if actualround >= int(self.maxround) and actualplayer==self.nbplayers-1 and playerlaunch == int(self.nbdarts):
            self.TxtRecap += "/!\ Last round reached ({})\n".format(actualround)
            return_code = 2

        # Store what he played in the table
        LSTPlayers[actualplayer].LSTColVal[playerlaunch-1] = (self.ScoreMap[hit],'int')
        # Store total for the round in column 6 (start from 0)
        LSTPlayers[actualplayer].LSTColVal[4] = (LSTPlayers[actualplayer].pointsinround,'int')
        # Calculate average and display in column 7
        #LSTPlayers[actualplayer].Avg = int((int(self.GameOpts['startingat']) - LSTPlayers[actualplayer].score) / LSTPlayers[actualplayer].dartsthrown)
        LSTPlayers[actualplayer].LSTColVal[5] = (LSTPlayers[actualplayer].ShowPPD(),'int')
        LSTPlayers[actualplayer].LSTColVal[6] = (LSTPlayers[actualplayer].ShowPPR(),'int')

        # Record total dart thrown, total hits (S=1, D=2, T=3) and refresh players stats
        LSTPlayers[actualplayer].dartsthrown += 1
        LSTPlayers[actualplayer].IncrementHits(hit)
        self.RefreshStats(LSTPlayers,actualround)
        
        # Next please !
        return return_code

    ############################################
    # Used to help drunken player
    def SearchPossibleLaunch(self,Score,playerlaunch):
        #/!\return value must be iterable and must have at least 3 values
        return_value = []
        # 1 dart possibility
        for Hit,DicKey in self.ScoreMap.items():
            if (  (Score==DicKey and self.GameOpts['double_out']=='False' and self.GameOpts['master_out']=='False')  
                    or (Score==DicKey and Hit[:1]=='D' and self.GameOpts['double_out']=='True') 
                    or (Score==DicKey and (Hit[:1]=='D' or Hit[:1]=='T') and self.GameOpts['master_out']=='True')
                ):
                return_value = [Hit]
                return return_value
                break
        # 2 darts possibilities - Player must have at least two darts left 
        if playerlaunch == 2 or playerlaunch == 1:
            for Hit,DicKey in self.ScoreMap.items():
                if (  (Score>DicKey and self.GameOpts['double_out']=='False' and self.GameOpts['master_out']=='False')  
                    or (Score>DicKey and Hit[:1]=='D' and self.GameOpts['double_out']=='True') 
                    or (Score>DicKey and (Hit[:1]=='D' or Hit[:1]=='T') and self.GameOpts['master_out']=='True')
                    ):
                    firstrest = Score-DicKey
                    for Hit2,DicKey2 in self.ScoreMap.items():
                        if firstrest==DicKey2:
                            return_value = [ Hit2, Hit ]
                            return return_value
        # 3 darts possibilities - Player must have at least 3 darts left
        if playerlaunch == 1:
            for Hit,DicKey in self.ScoreMap.items():
                if (  (Score>DicKey and self.GameOpts['double_out']=='False' and self.GameOpts['master_out']=='False')  
                    or (Score>DicKey and Hit[:1]=='D' and self.GameOpts['double_out']=='True') 
                    or (Score>DicKey and (Hit[:1]=='D' or Hit[:1]=='T') and self.GameOpts['master_out']=='True')
                    ):
                    firstrest = Score-DicKey
                    for Hit3,DicKey3 in self.ScoreMap.items():
                        if firstrest > DicKey3:
                            secondrest = firstrest - DicKey3
                            for Hit4,DicKey4 in self.ScoreMap.items():
                                if secondrest==DicKey4:
                                    return_value = [ Hit3, Hit4, Hit ]
                                    return return_value
        return return_value

    ###############
    # Method to frefresh Each Player Stats - Specific to every game
    def RefreshStats(self,Players,actualround):
        for P in Players:
            P.Stats['Points Per Round']=P.ShowPPR()
            P.Stats['Points Per Dart']=P.ShowPPD()

    ###############
    # Returns Random things, to send to clients in case of a network game
    def GetRandom(self,LSTPlayers,actualround,actualplayer,playerlaunch):
        return None # Means that there is no random

    ###############
    # Set Random things, while received by master in case of a network game
    def SetRandom(self,LSTPlayers,actualround,actualplayer,playerlaunch,data):
        pass

    ###############
    # Define the next game players order, depending of previous games' score
    def DefineNextGameOrder(self,LSTPlayers):
        Sc = {}
        # Create a dict with player and his score
        for P in LSTPlayers:
            Sc[P.PlayerName] = P.score
        # Order this dict depending of the score
        NewOrder=collections.OrderedDict(sorted(Sc.items(), key=lambda t: t[1], reverse=True))# For DESC order, add "reverse=True" to the sorted() function
        FinalOrder=list(NewOrder.keys())
        # Return
        return FinalOrder
            
    #Find your teammate        
    def Mate(self,actualplayer,nbplayers):
         mate=-1
         if actualplayer<(nbplayers / 2):
             mate=actualplayer + nbplayers / 2
         else:
             mate=actualplayer - nbplayers / 2
         return int(mate)
#
# Check for handicap and record appropriate marks for player
#
    def CheckHandicap(self,LSTPlayers):
         self.Logs.Log("DEBUG","Checking for handicaps!")
         LSTPPD = []
         LSTPoints = []
         playerstartscore = 0
         for player in LSTPlayers:
             name = player.PlayerName
             if name.lower() not in self.Stats.PlayerStatDict:
                 LSTPPD.append(0)
             else:
                 LSTPPD.append(int(float(self.Stats.PlayerStatDict[name.lower()][6])))
         LSTPoints = self.Handicap.hoonehandicap(LSTPPD,self.GameOpts['startingat'],LSTPlayers)
         return LSTPoints

"""
#
# Update stats.csv with points, throws, ppd, ppr for each player
#
    def PlayerStats(self,LSTPlayers,actualround):
         for objplayer in LSTPlayers:
              name = objplayer.PlayerName
              if name.lower() not in self.Stats.PlayerStatDict: #if there is no player in the stats csv file
                    self.Logs.Log("DEBUG","Cannot find {} in the stats file!  I will add them.".format(name.title()))
                    self.Stats.PlayerStatDict[name.lower()] = ["0","0","0.0",str(objplayer.TotalPoints),str(objplayer.dartsthrown),str(objplayer.ShowPPD()),str(objplayer.ShowPPR())]
              else:
                    self.Logs.Log("DEBUG","Updating {}'s stats!".format(name.title()))
                    self.Stats.Increase01Points(name.lower(),objplayer.TotalPoints)
                    self.Stats.Increase01Throws(name.lower(),objplayer.dartsthrown)
                    self.Stats.PPR(name.lower())
                    self.Stats.PPD(name.lower())
         self.Stats.WritetoCSV()
"""
