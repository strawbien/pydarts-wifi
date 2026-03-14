# -*- coding: utf-8 -*-
# Game by poilou
######
from include import CPlayer
from include import CGame
from include import CScores
from include import CStats
from include import CHandicap
import operator  # What For ?
import random  # For crazy
import collections  # To use OrderedDict to sort players from the last score they add
from copy import deepcopy  # For backupTurn

# VAR
GameLogo = 'Cricket.png'  # Background image - relative to images folder
LSTRandom = [20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7]
Headers = ['20', '19', '18', '17', '16', '15', 'B']
GameOpts = {'max_round': '20', 'optioncrazy': 'False', 'optioncutthroat': 'False', 'drinkscore': '200',
            'Teaming': 'False', 'optionteamscore': 'False', 'optionhandicap': 'False'}  # Options in string format
nbdarts = 3  # How many darts the player is allowed to throw
# Dictionnary of stats and dislay order (For exemple : Points Per Darts and Avg are displayed in descending order)
GameRecords = {'MPR': 'DESC', 'Hits per round': 'DESC', 'GiveOut': 'ASC'}


# Extend the basic player
class CPlayerExtended(CPlayer.CPlayer):
    def __init__(self, x, nbplayers, Config, res):
        super(CPlayerExtended, self).__init__(x, nbplayers, Config, res)
        self.PayDrink = False  # Flag used to know if player has reached the drink score
        self.DistribPoints = 0  # COunt how many points the player gave to the others (cut throat)
        # Init Player Records to zero
        for GR in GameRecords:
            self.Stats[GR] = '0'


class Game(CGame.CGame):
    def __init__(self, myDisplay, GameChoice, nbplayers, GameOpts, Config, Logs):
        super(Game, self).__init__(myDisplay, GameChoice, nbplayers, GameOpts, Config, Logs)
        self.Stats = CStats.CStats('Cricket', self.Logs)
        self.Handicap = CHandicap.CHandicap('Cricket', Config, Logs)
        self.GameRecords = GameRecords
        self.nbdarts = nbdarts  # Total darts the player has to play
        self.GameLogo = GameLogo
        self.Headers = Headers
        self.nbplayers=nbplayers
        #  Get the maxiumum round number
        self.maxround = self.GameOpts['max_round']
        # TEMP - place it somwhere else - prevent option to be activated in case of odd number of players
        if nbplayers >= 4 and nbplayers % 2 == 0 and GameOpts['Teaming'] == 'True':
            # Enable display of teaming
            self.myDisplay.Teaming = True
        elif GameOpts['Teaming'] == 'True':
            self.Logs.Log('ERROR', 'Teaming require at least 4 players and a multiple of 2 players. Disabling Teaming')
            self.GameOpts['Teaming'] = 'False'

    #
    def PostDartsChecks(self, hit, Players, actualround, actualplayer, playerlaunch):
        # Find teamMate (only for teaming)
        mate = self.Mate(actualplayer, len(Players))
        # Init
        PlayClosed = False  # Should we play the closed sound ?
        PlayOpen = False  # Should we play the open sound ?
        PlayHit = False  # Should we play the Double & triple sound ?
        PlayScored = False  # Should we play the Scored sound ?
        
        BlinkText = ""
        return_code = 0
        touchcount4total = False
        self.TxtRecap = "Player {} - Score before playing: {}\n".format(Players[actualplayer].ident,
                                                                        format(Players[actualplayer].ModifyScore(0)))
        # We put in a variable the affected column
        TouchedColumn = hit[1:]
        MultipleColumn = hit[0:1]
        Players[actualplayer].dartsthrown += 1
        # If this column is currently displayed - Valid hit
        if str(TouchedColumn) in self.Headers:
            # Look for the column corresponding to the value (return a string)
            IndexColTouched = self.Headers.index(str(TouchedColumn))
            if MultipleColumn == 'S':
                TouchToAdd = 1
            elif MultipleColumn == 'D':
                TouchToAdd = 2
            elif MultipleColumn == 'T':
                TouchToAdd = 3
            # To count how many over touched hits
            overtouched = 0
            # Displays the correspoding leds
            for x in range(0, TouchToAdd):
                # For each hit to add - If the player has less than 3 hits
                if Players[actualplayer].GetColVal(IndexColTouched) < 3:
                    # We add a touch to his score
                    Players[actualplayer].IncrementColTouch(IndexColTouched)
                    # If teaming, add touches to teammate
                    if self.GameOpts['Teaming'] == 'True' and self.GameOpts['optionteamscore'] == 'True':
                        self.TxtRecap += "Changing teammates marks!\n"
                        Players[mate].IncrementColTouch(IndexColTouched)
                    # Increment All Rounds hit count
                    Players[actualplayer].IncrementHits()
                    # Increment this round hit count
                    Players[actualplayer].roundhits += 1
                    # Define played sound regarding of situation
                    if Players[actualplayer].GetColVal(IndexColTouched) == 3:
                        if self.GetColumnState(actualplayer, Players, IndexColTouched) == 3:
                            PlayOpen = True
                            PlayHit = False
                        elif self.GetColumnState(actualplayer, Players, IndexColTouched) == 4:
                            PlayClosed = True
                            PlayHit = False
                    elif x == 0:
                        PlayHit = True
                # If he already has three hits, we calculate how many more hits the player has made
                elif Players[actualplayer].GetColVal(IndexColTouched) == 3:
                    # Increment overtouched for every touch over the 3 required ones
                    overtouched += 1

            # If there is a "surplus"
            if overtouched > 0:
                YourMateClosed = Players[mate].GetColVal(IndexColTouched)
                for LSTobj in Players:
                    y = LSTobj.GetColVal(IndexColTouched)  # Check if this players has closed
                    MateY = self.Mate(LSTobj.ident, len(Players))  # Identify this player's teammate
                    YourMateClosed = Players[MateY].GetColVal(IndexColTouched)  # Check if his mate has closed too
                    # We're looking for how much is a simple touch
                    valueofsimplehit = self.ScoreMap['S' + hit[1:]]
                    # Multiply the single touch by the number of times the player touched above 3
                    overtouchedpts = overtouched * int(valueofsimplehit)
                    # Given that we will also give the teammates (Cut-Throat), we divide the total points to be given by two if Teaming
                    if self.GameOpts['Teaming'] == 'True' and self.GameOpts['optioncutthroat'] == 'True':
                        overtouchedpts = overtouchedpts / 2
                    # If Cut Throat and the other team have not closed we add the points to others
                    if self.GameOpts['optioncutthroat'] == 'True' and (
                            (y < 3 and self.GameOpts['Teaming'] == 'False') or (
                            self.GameOpts['Teaming'] == 'True' and YourMateClosed >= 3 and (
                            y < 3 or YourMateClosed < 3))):
                        # Points are added to those who do not close
                        self.TxtRecap += "Player {} takes {} points in the nose ! (Cut-throat)\n".format(LSTobj.ident,
                                                                                                         overtouchedpts)
                        LSTobj.ModifyScore(overtouchedpts)
                        # Give half points to teammate too if teaming is enabled
                        if self.GameOpts['Teaming'] == 'True':
                            Players[MateY].ModifyScore(overtouchedpts)  # And give him half of point too
                            self.TxtRecap += "TeamMate {} takes {} points in the nose too ! (Cut-throat)\n".format(
                                MateY, overtouchedpts)
                        # Add points to player's Stats
                        Players[actualplayer].DistribPoints += overtouchedpts
                        # If players take points, the hits count for the player's total
                        touchcount4total = True
                        # Play Sound when you score
                        PlayScored=True
                    # If not Cut Throat we add the points to him only (+ possibly his teammate) if he is not closed for all
                    elif self.GameOpts['optioncutthroat'] == 'False' and LSTobj.ident == Players[
                        actualplayer].ident and (self.GameOpts['Teaming'] == 'False' or (
                            self.GameOpts['Teaming'] == 'True' and YourMateClosed >= 3)):
                        TotallyClosed = True
                        # Check if the gate is totally closed for normal mode
                        for LSTobj2 in Players:
                            z = LSTobj2.GetColVal(IndexColTouched)
                            # Identify people who require to be scored (only closed guys and teammates won't be scored)
                            if z < 3 and (self.GameOpts['Teaming'] == 'False' or (
                                    self.GameOpts['Teaming'] == 'True' and LSTobj2.ident != mate)):
                                TotallyClosed = False
                        # If you there is still someone who didn't closed, take score for you (and your teammate)
                        if TotallyClosed == False:
                            self.TxtRecap += "This player get {} extra score !\n".format(overtouchedpts)
                            LSTobj.ModifyScore(overtouchedpts)
                            # Give half points to your teammate too if teaming is enabled
                            if self.GameOpts['Teaming'] == 'True':
                                Players[mate].ModifyScore(overtouchedpts)  # And give him half of point too
                                self.TxtRecap += "TeamMate {} takes {} points !\n".format(MateY,
                                                                                          overtouchedpts)  # Was mate
                            touchcount4total = True
                    # For fun, if the player reached the required drink score (usually 500), tell him to pay a drink !
                    if LSTobj.PayDrink == False and LSTobj.score >= int(self.GameOpts['drinkscore']) and self.GameOpts[
                        'optioncutthroat'] == 'True':
                        LSTobj.PayDrink = True
                        self.myDisplay.PlaySound('diegoaimaboir')

            # Added buttons if the player had a surplus (common to Cut Throat and Normal Mode)
            if overtouched > 0 and touchcount4total == True:
                # We add his extra hits to his total since they counted (players took points)
                Players[actualplayer].IncrementHits(overtouched)
                # Increment this round hit count
                Players[actualplayer].roundhits += 1
                PlayHit = True  # Its a valid hit, play sound

            # Sound handling to avoid multiple sounds playing at a time
            if PlayScored:
                self.myDisplay.PlaySound('very_deep')
                self.Logs.Log("DEBUG", "Playing Scored Sound")
            elif PlayOpen:
                self.myDisplay.PlaySound('open')
                self.Logs.Log("DEBUG", "Playing Open Sound")
            elif PlayClosed:
                self.myDisplay.PlaySound('closed')
                self.Logs.Log("DEBUG", "Playing Closed Sound")
            elif PlayHit:
                self.myDisplay.Sound4Touch(hit)  # Its a valid hit, play sound
                self.Logs.Log("DEBUG", "Playing Simple Hit Sound")

        # Count darts played
        Players[actualplayer].dartsthrown += 1

        # It is recommanded to update stats evry dart thrown
        self.RefreshStats(Players, actualround)

        self.TxtRecap += "Hit: {} - Active Columns: {}\n".format(Players[actualplayer].GetTouchType(hit), self.Headers)
        self.TxtRecap += "Total number of hits for this player: {}\n".format(Players[actualplayer].GetTotalHit())
        self.TxtRecap += "Number of darts thrown from this player: {}\n".format(playerlaunch)
        self.TxtRecap += "Number of total darts thrown from this player: {}\n".format(Players[actualplayer].dartsthrown)

        # If it was last throw and no touch : play sound for "round missed"
        if playerlaunch == self.nbdarts and Players[actualplayer].roundhits == 0:
            self.myDisplay.PlaySound('chaussette')

        # Last throw of the last round
        if actualround >= int(self.maxround) and actualplayer == self.nbplayers - 1 and playerlaunch == self.nbdarts:
            self.TxtRecap += "/!\ Last Round Reached ({})\n".format(actualround)
            return_code = 2

        # Check if there is a winner
        winner = self.CheckWinner(Players)
        if winner != -1:
            self.TxtRecap += "/!\ Player {} wins !\n".format(winner)
            self.winner = winner
            return_code = 3

        # If there is blink text to display
        if BlinkText != "":
            self.myDisplay.InfoMessage([BlinkText], None, None, 'middle', 'big')

        # Display Recap text
        self.Logs.Log("DEBUG", self.TxtRecap)

        # And return code
        return return_code

    # Method to check if there is a winnner
    def CheckWinner(self, Players):
        bestscoreid = -1
        ClosedCols = True
        # Find the better score
        for ObjJoueur in Players:
            if (bestscoreid == -1 or ObjJoueur.score < Players[bestscoreid].score) and self.GameOpts[
                'optioncutthroat'] == 'True':
                bestscoreid = ObjJoueur.ident
            elif (bestscoreid == -1 or ObjJoueur.score > Players[bestscoreid].score) and self.GameOpts[
                'optioncutthroat'] == 'False':
                bestscoreid = ObjJoueur.ident
        # Check if the player who have the better score has closed all gates
        for LSTColVal in Players[bestscoreid].LSTColVal:
            if LSTColVal[0] != 3:
                ClosedCols = False
        # If the player who have the best score has closed all the gates
        if ClosedCols == True:
            return bestscoreid
        else:
            return -1

    """
    def RandomHeader(self,Players,force=False):
       for x in range(0,int(self.nbcol)):
          self.TxtRecap += "Working on column {}\n".format(x)
          # Check whether the Crazy doors are open or closed and assign new numbers to open and unclosed columns
          randomize = False
          # Only Random if bypass is not set
          if not force:
             for LSTobj in Players:
                y = LSTobj.GetColVal(x)
                # CASE 1 : column is CLOSED
                if y == 3:
                   randomize=False
                   self.TxtRecap += "This column {} is CLOSED by player {} !\n".format(x,LSTobj.PlayerName)
                   break
                # CASE 2 : If a player has one or two marks in column, then it is OPEN
                elif y in [1,2]:
                   randomize = True
                   self.TxtRecap += "This column {} is still OPEN (marked) for player {} ! Randomize !\n".format(x,LSTobj.PlayerName)
          else:
             randomize=True
          # If column is open, randomize number
          if randomize == True:
             self.TxtRecap+="Column {} will randomize.\n".format(x)
             randomisdone = False
             while randomisdone == False:
                RandomNumber = random.choice(LSTRandom)
                if (str(RandomNumber) in self.Headers)== False:
                   self.Headers[x] = str(RandomNumber)
                   randomisdone = True
          else:
             self.TxtRecap += "Column {} will not be randomized.\n".format(x)
    """

    #
    # New RandomHeader Method that use the GetColumnState internal method to check column. More reliable.
    #
    def RandomHeader(self, actualplayer, Players, force=False):
        for x in range(0, int(self.nbcol)):
            self.TxtRecap += "Working on column {}\n".format(x)
            # Init Randomize to false
            randomize = False
            # Check state of column (none, open or closed)
            State = self.GetColumnState(actualplayer, Players, x)
            self.TxtRecap + "State of column " + str(x) + " is " + str(State) + "\n"
            # If force random is not requested, get state of column
            if not force:
                # If state is True (Open), randomize
                if State == 2:
                    randomize = True
                # If state is Not opened, Closed by a player, or Closed by everyone, do not randomize
                elif State == 1 or State == 3 or State == 4:
                    randomize = False
            # If force random requested, randomize (first round for exemple)
            else:
                self.TxtRecap += "Forcing randomizing of column {}.\n".format(x)
                randomize = True
            # Randomizing column...
            if randomize == True:
                self.TxtRecap += "Column {} will randomize.\n".format(x)
                randomisdone = False
                while randomisdone == False:
                    RandomNumber = random.choice(LSTRandom)
                    if (str(RandomNumber) in self.Headers) == False:
                        self.Headers[x] = str(RandomNumber)
                        randomisdone = True
            else:
                self.TxtRecap += "Column {} will not be randomized.\n".format(x)

    #
    # Get state of column. It can be : 1=No hit, 2=Hit by a player or a team, 3=Closed by a player or a team, 4=Closed by everybody
    #
    def GetColumnState(self, actualplayer, Players, col):
        # Init
        State = 1
        nbclosed = 0
        # Loop on players
        for P in Players:
            # Get Mate if Teaming enabled
            if self.GameOpts['Teaming'] == 'True':
                mate = self.Mate(actualplayer, len(Players))
                # TEAMING CASE 1 - State can only go upper
                if P.GetColVal(col) in [1, 2] and State != 3:
                    self.TxtRecap += "[TEAMING] This column {} is OPEN for at least player {}!\n".format(col,
                                                                                                         P.PlayerName)
                    State = 2
                # NOTEAMING CASE 2
                elif P.GetColVal(col) == 3 and Players[mate].GetColVal(col) == 3:
                    State = 3
                    nbclosed += 1
                    self.TxtRecap += "[TEAMING] This column {} is CLOSED by both players {} and {} !\n".format(col,
                                                                                                               P.PlayerName,
                                                                                                               Players[
                                                                                                                   mate].PlayerName)
            elif self.GameOpts['Teaming'] == 'False':
                # NOTEAMING CASE 1
                if P.GetColVal(col) in [1, 2] and State != 3:
                    self.TxtRecap += "[NOTEAMING] This column {} is still OPEN (marked) by at least player {}!\n".format(
                        col, P.PlayerName)
                    State = 2
                # NOTEAMING CASE 2
                elif P.GetColVal(col) == 3:
                    State = 3
                    nbclosed += 1
                    self.TxtRecap += "[NOTEAMING] This column {} is CLOSED by at least player {} !\n".format(col,
                                                                                                             P.PlayerName)
        if nbclosed == len(Players):
            State = 4
            self.TxtRecap += "ALL PLAYERS (OR TEAM) has closed this column {} !\n".format(col)
        return State

    #
    # Action launched before each dart throw
    #
    def PreDartsChecks(self, Players, actualround, actualplayer, playerlaunch):
        self.TxtRecap = ""
        # If first round - set display as leds
        if playerlaunch == 1 and actualround == 1 and actualplayer == 0:
            self.myDisplay.PlaySound('cricket')
            for Player in Players:
                for Column, Value in enumerate(Player.LSTColVal):
                    Player.LSTColVal[Column] = [0, 'leds', 'grey2']
            if self.GameOpts['optionhandicap'] == 'True' and self.GameOpts['Teaming'] == 'True':
                self.CheckHandicap(Players)
        if playerlaunch == 1:
            # Reset number of hits in this round for this player
            Players[actualplayer].roundhits = 0
            # Heading definition according to these cases
            if self.GameOpts[
                'optioncrazy'] == 'True' and actualround == 1 and actualplayer == 0 and playerlaunch == 1 and self.RandomIsFromNet == False:
                self.RandomHeader(actualplayer, Players, True)
            # Definition of header - random if option crazy = 1
            elif self.GameOpts['optioncrazy'] == 'True' and self.RandomIsFromNet == False:
                self.RandomHeader(actualplayer, Players)
            self.TxtRecap += "Active columns : {}".format(self.Headers)
            self.Logs.Log("DEBUG", self.TxtRecap)
            self.SaveTurn(Players)

    #
    # If player Hit the Player button before having threw all his darts
    #
    def EarlyPlayerButton(self, Players, actualplayer, actualround):
        # Jump to next player by default
        return_code=1
        self.TxtRecap += "You hit Player button before throwing all your darts ! Did you hit the PNEU ?"
        self.TxtRecap += "Actualround {} Max Round {} actualplayer {} nbplayers {}".format(actualround, self.maxround,
                                                                                           actualplayer,
                                                                                           self.nbplayers - 1)
        # If no touch for this player at this round : play sound for "round missed"
        if Players[actualplayer].roundhits == 0:
            self.myDisplay.PlaySound('chaussette')

        # If last round reached
        if actualround == int(self.maxround) and actualplayer == self.nbplayers - 1:
            winner=self.CheckWinner(Players)
            if winner != -1:
               self.winner = winner
               self.TxtRecap += "/!\ Player {} wins !\n".format(winner)
               return 3
            return 2
        return return_code

    # Method to frefresh Player Stats - Adapt to the stats you want. They represent mathematical formulas used to calculate stats. Refreshed after every launch
    def RefreshStats(self, Players, actualround):
        for P in Players:
            P.Stats['MPR'] = P.ShowMPR()
            P.Stats['Hits per round'] = P.HitsPerRound(actualround)
            P.Stats['GiveOut'] = P.DistribPoints

    #
    # Returns and Random things, to send to clients in case of a network game
    #
    def GetRandom(self, Players, actualround, actualplayer, playerlaunch):
        if self.GameOpts['optioncrazy'] == 'True':
            return self.Headers
        else:
            return False

    #
    # Set Random things, while received by master in case of a network game
    #
    def SetRandom(self, Players, actualround, actualplayer, playerlaunch, data):
        if data != False:
            self.Headers = data
            self.RandomIsFromNet = True

    #
    # Define the next game players order, depending of previous games' scores
    #
    def DefineNextGameOrder(self, Players):
        Sc = {}
        # Create a dict with player and his score
        for P in Players:
            Sc[P.PlayerName] = P.score
        # Order this dict depending of the score
        if self.GameOpts['optioncutthroat'] == 'True':
            NewOrder = collections.OrderedDict(sorted(Sc.items(), key=lambda t: t[1],
                                                      reverse=True))  # For DESC order, add "reverse=True" to the sorted() function
        else:
            NewOrder = collections.OrderedDict(
                sorted(Sc.items(), key=lambda t: t[1]))  # For DESC order, add "reverse=True" to the sorted() function
        FinalOrder = list(NewOrder.keys())
        # Return
        return FinalOrder

    #
    # Find TeamMate in case of Teaming
    #
    def Mate(self, actualplayer, nbplayers):
        mate = -1
        if (self.GameOpts['Teaming'] == 'True'):
            if actualplayer < (nbplayers / 2):
                mate = actualplayer + nbplayers / 2
            else:
                mate = actualplayer - nbplayers / 2
        return mate

    #
    # Check for handicap and record appropriate marks for player
    #
    def CheckHandicap(self, Players):
        if len(Players) != 4:
            self.Logs.Log("WARNING", "Handicap is available in Cricket only for 4 players.")
            return False
        else:
            self.Logs.Log("DEBUG", "Looking for handicaps")
            LSThandimarks = []
            LSTmpr = []
            maxid = 0
            for player in Players:
                name = player.PlayerName
                if name.lower() not in self.Stats.PlayerStatDict:
                    LSTmpr.append(0.0)
                else:
                    LSTmpr.append(self.Stats.PlayerStatDict[name.lower()][2])
                # Load Handicaps from CHandicap
            LSThandimarks = self.Handicap.FindCricketHandicap(LSTmpr)
            maxid = self.Handicap.ReturnMaxid()
            # load handicaps into players
            for column in range(0, int(self.nbcol + 1)):
                for handmark in range(LSThandimarks[column] + 1):
                    self.Logs.Log("DEBUG", "Handicap : Column = {}, handmark = {}".format(column, handmark))
                    if maxid == 0:
                        if handmark == 0:
                            pass
                        else:
                            Players[1].IncrementColTouch(column)
                            Players[3].IncrementColTouch(column)
                    elif maxid == 1:
                        if handmark == 0:
                            pass
                    else:
                        Players[0].IncrementColTouch(column)
                        Players[2].IncrementColTouch(column)
