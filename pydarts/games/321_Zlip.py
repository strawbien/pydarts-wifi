# -*- coding: utf-8 -*-
# Game by poilou
#######
from include import CPlayer
from include import CGame

# VAR
WinTotal = 321  # Le chiffre a atteindre
GameLogo = '321_Zlip.png'  # Background image - relative to images folder
Headers = ["D1", "D2", "D3", "", "", "", ""]
GameOpts = {'max_round': '10', 'advanced': 'True', 'master': 'False'}  # Options in string format
nbdarts = 3  # How many darts the player is allowed to throw
GameRecords = {'Zlips': 'DESC', 'Zlipped': 'ASC', 'Points Per Round': 'DESC'}

# Extend the basic player
class CPlayerExtended(CPlayer.CPlayer):
    def __init__(self, x, nbjoueurs, Config, res):
        super(CPlayerExtended, self).__init__(x, nbjoueurs, Config, res)
        self.havezapped = 0
        self.x = x
        self.nbzapped = 0
        # Init Player Records to zero
        for GR in GameRecords:
            self.Stats[GR] = '0'

    def Zap(self, Display_Zlip=False):
        self.havezapped += 1
        if Display_Zlip:
            self.LSTColVal[6] = ['321Zap_zlip', 'image']

    def GetZap(self):
        return self.havezapped

    def SetZapped(self):
        self.nbzapped += 1

    def GetZapped(self):
        return self.nbzapped


class Game(CGame.CGame):
    def __init__(self, myDisplay, GameChoice, nbplayers, GameOpts, Config, Logs):
        super(Game, self).__init__(myDisplay, GameChoice, nbplayers, GameOpts, Config, Logs)
        self.nbdarts = nbdarts  # Total darts the player has to play
        self.GameRecords = GameRecords
        self.GameLogo = GameLogo
        self.Headers = Headers
        self.ScoreMap.update({'SB': 50})
        #  Get the maxiumum round number
        self.maxround = self.GameOpts['max_round']

    #
    # Post Darts Launch Checks
    #
    def PostDartsChecks(self, key, Players, actualround, actualplayer, playerlaunch):
        # Init
        BlinkText = ""  # Default blink text
        return_code = 0  # default return code
        self.TxtRecap = "Score before playing {0}\n".format(Players[actualplayer].ModifyScore(0))

        # Whatever you played, we keep it in the display table
        Players[actualplayer].LSTColVal[playerlaunch - 1] = (self.ScoreMap.get(key), 'txt')
        self.TxtRecap = "Player has played {}\n".format(self.ScoreMap.get(key))

        # Case : the player goes over 321
        if (Players[actualplayer].ModifyScore(0) + self.ScoreMap.get(key)) > WinTotal:
            self.TxtRecap += "/!\ Going over {}, too much !\n".format(WinTotal)
            NewScore = WinTotal - Players[actualplayer].ModifyScore(0)
            NewScore = self.ScoreMap.get(key) - NewScore
            NewScore = WinTotal - NewScore
            Players[actualplayer].SetScore(NewScore)
            BlinkText = "Damn, you get too high !"
            self.myDisplay.PlaySound('toohigh')  # Too High , man !
            playerlaunch = self.nbdarts
            return_code = 1

        # The player reach exactly 321 points
        elif (Players[actualplayer].ModifyScore(0) + self.ScoreMap.get(key)) == WinTotal:
            Players[actualplayer].IncrementHits(key)
            # The player did not zlip anyone and "master" is enabled. master has got a priority on advanced
            if (Players[actualplayer].GetZap() == 0 and self.GameOpts['master'] == 'True'):
                BlinkText = "Ho Dear ! You have to Zlip first !"
                self.myDisplay.PlaySound('whatamess')  # If its a valid hit, play sound
                Players[actualplayer].SetScore(0)
                self.TxtRecap += "/!\ Game in master mode - You never zlipped, so back to Zero !\n"
                playerlaunch = self.nbdarts
                return_code = 1
            # The player did not zlip anyone and "advanced" is enabled
            elif (Players[actualplayer].GetZap() == 0 and self.GameOpts['advanced'] == 'True'):
                BlinkText = "Gosh ! You picked up a free Zlip !"
                self.myDisplay.PlaySound('zapdamn')  # If its a valid hit, play sound
                Players[actualplayer].SetScore(0)
                self.TxtRecap += "/!\ Game in advanced mode - You did not Zlip, so you won a Zlip !\n"
                playerlaunch = self.nbdarts
                Players[actualplayer].Zap(True)
                return_code = 1
            # The player Zapped at least once or none of the advanced nor master is true - Victoire
            elif Players[actualplayer].GetZap() > 0 or (self.GameOpts['master'] == 'False' and self.GameOpts['advanced'] == 'False'):
                self.myDisplay.PlaySound('zapdamn')  # Sound of victory
                BlinkText = "{} won with {} zap !".format(Players[actualplayer].PlayerName,
                                                          Players[actualplayer].GetZap())
                self.TxtRecap += "/!\ Player {} wins !\n".format(Players[actualplayer].ident)
                self.winner = Players[actualplayer].ident
                Players[actualplayer].ModifyScore(self.ScoreMap.get(key))
                Players[actualplayer].IncrementHits(key)
                return_code = 3

        # Standard Case - score is incremented
        else:
            self.myDisplay.Sound4Touch(key)  # Play sound for double, triple and center
            Players[actualplayer].TotalPoints += self.ScoreMap.get(key)
            Players[actualplayer].IncrementHits(key)
            Players[actualplayer].ModifyScore(self.ScoreMap.get(key))

        # Case : if the player Zlip another player
        for LSTobj in Players:
            if LSTobj.score == Players[actualplayer].score and LSTobj.ident != Players[actualplayer].ident and Players[
                actualplayer].score > 0:
                self.TxtRecap += "The player {} has been zlipped !\n".format(LSTobj.ident)
                LSTobj.SetScore(0)
                BlinkText = "Zapped!"
                if self.GameOpts['master'] == 'True' or self.GameOpts['advanced'] == 'True':
                    Players[actualplayer].Zap(True)
                else:
                    Players[actualplayer].Zap()
                LSTobj.SetZapped()
                self.myDisplay.PlaySound('zapdamn')

        # If there is text to display blinking
        if BlinkText != "":
            self.myDisplay.InfoMessage([BlinkText], None, None, 'middle', 'big')

        # You may want to count darts played
        Players[actualplayer].dartsthrown += 1
        # Players[actualplayer].TotalPoints = Players[actualplayer].score

        # It is recommanded to update stats evry dart thrown
        self.RefreshStats(Players, actualround)

        #### Display and return code only behond this point

        # Round log
        self.TxtRecap += "Score after playing {0}\n".format(Players[actualplayer].ModifyScore(0))
        self.TxtRecap += "Player  {} - dart {} - Zlips : {} - Zlipped : {}\n {}".format(actualplayer, playerlaunch,
                                                                                        Players[
                                                                                            actualplayer].havezapped,
                                                                                        Players[actualplayer].nbzapped,
                                                                                        self.TxtRecap)
        self.TxtRecap += "Touche {} : {} ({})\n".format(key, Players[actualplayer].GetTouchType(key), key)
        self.TxtRecap += "Fleches lancees : {}\n".format(str(playerlaunch))
        self.TxtRecap += "Total des touches : {}\n".format(Players[actualplayer].GetTotalHit())

        # If its the last launch of last round
        if actualround >= int(self.maxround) and actualplayer == self.nbplayers - 1 and playerlaunch == self.nbdarts:
            self.TxtRecap += "/!\ Last round reached ({})\n".format(actualround)
            return_code = 2

        # Print debug
        self.Logs.Log("DEBUG", self.TxtRecap)
        return return_code

    #####
    # Method called before each dart launch
    #####
    def PreDartsChecks(self, Players, actualround, actualplayer, playerlaunch):
        return_code = 0
        # Keep playerlaunch in current object
        self.playerlaunch = playerlaunch

        if playerlaunch == 1 and actualround == 1 and actualplayer == 0:
            self.myDisplay.PlaySound('321Zlip_intro')

        # First launch - Display Go msg and save backupturn
        if playerlaunch == 1:
            # Backup round's score
            self.SaveTurn(Players)

        # Clean table for current player (only next launch)
        for i in range(playerlaunch, 4):
            Players[actualplayer].LSTColVal[i - 1] = ('', 'txt')

        # For all other players
        for LSTobj in Players:
            if playerlaunch == 1 or LSTobj.ident != actualplayer:
                # clean table for all players
                LSTobj.LSTColVal[0] = ['', 'txt']
                LSTobj.LSTColVal[1] = ['', 'txt']
                LSTobj.LSTColVal[2] = ['', 'txt']
            # Si c est un joueur qui a plus de points on affiche le nombre de points pour le zapper
            if LSTobj.score > Players[actualplayer].score and LSTobj.ident != actualplayer:
                DiffScore = LSTobj.score - Players[actualplayer].score
                # Possibilities = self.SearchPossibleLaunch(DiffScore)
                ZapList = self.SearchZap(DiffScore)
                if len(ZapList) >= 1: LSTobj.LSTColVal[0] = (ZapList[0], 'int', 'green')
                if len(ZapList) >= 2: LSTobj.LSTColVal[1] = (ZapList[1], 'int', 'green')
                if len(ZapList) >= 3: LSTobj.LSTColVal[2] = (ZapList[2], 'int', 'green')
            # Sinon on cherche un possible zap en arriere
            elif LSTobj.ident != actualplayer:
                ScoreUp = WinTotal - Players[actualplayer].score
                ScoreDown = WinTotal - LSTobj.score
                ZapList = self.SearchZap(ScoreUp, ScoreDown)
                if len(ZapList) >= 1: LSTobj.LSTColVal[0] = (ZapList[0], 'int', 'purple')
                if len(ZapList) >= 2: LSTobj.LSTColVal[1] = (ZapList[1], 'int', 'purple')
                if len(ZapList) >= 3: LSTobj.LSTColVal[2] = (ZapList[2], 'int', 'purple')
            # Pour nous on affiche le nombre de points vers la victoire (si ZAP OK et Option master ou advanced)
            if Players[actualplayer].GetZap() > 0 or (
                    self.GameOpts['master'] == 'False' and self.GameOpts['advanced'] == 'False'):
                DiffScore = WinTotal - Players[actualplayer].score
                # Possibilities = self.SearchZap(DiffScore)
                ZapList = self.SearchZap(DiffScore)
                if len(ZapList) >= 1: Players[actualplayer].LSTColVal[playerlaunch - 1] = (ZapList[0], 'int', 'red')
                if len(ZapList) >= 2: Players[actualplayer].LSTColVal[playerlaunch] = (ZapList[1], 'int', 'red')
                if len(ZapList) >= 3: Players[actualplayer].LSTColVal[playerlaunch + 1] = (ZapList[2], 'int', 'red')

    #
    # Search any possible ZAP (Normal and back zap)
    #
    def SearchZap(self, ScoreUp, ScoreDown=0):
        # /!\return value must be iterable and must have at least 3 values
        # print LSTChiffres
        return_value = []
        total = ScoreUp + ScoreDown
        # 1 dart possibility
        for Hit, DicKey in self.ScoreMap.items():
            if total == DicKey:
                return_value = [Hit]
                return return_value
                break
        # 2 darts possibilities - Player must have at least two darts left
        if self.playerlaunch == 2 or self.playerlaunch == 1:
            for Hit, DicKey in self.ScoreMap.items():
                if total > DicKey and DicKey < ScoreUp:
                    firstrest = total - DicKey
                    for Hit2, DicKey2 in self.ScoreMap.items():
                        if firstrest == DicKey2:
                            return_value = [Hit, Hit2]
                            return return_value
        # 3 darts possibilities - Player must have at least 3 darts left
        if self.playerlaunch == 1:
            for Hit, DicKey in self.ScoreMap.items():
                if total > DicKey and DicKey < ScoreUp:
                    firstrest = total - DicKey
                    for Hit3, DicKey3 in self.ScoreMap.items():
                        if firstrest > DicKey3 and DicKey + DicKey3 < ScoreUp:
                            secondrest = firstrest - DicKey3
                            for Hit4, DicKey4 in self.ScoreMap.items():
                                if secondrest == DicKey4:
                                    return_value = [Hit, Hit3, Hit4]
                                    return return_value
        return return_value


    ###############
    # Method to frefresh Player Stats - Adapt to the stats you want.
    # They represent mathematical formulas used to calculate stats. Refreshed after every launch
    def RefreshStats(self, Players, actualround):
        for P in Players:
            P.Stats['Zlips'] = P.havezapped
            P.Stats['Zlipped'] = P.nbzapped
            P.Stats['Points Per Round'] = P.AVG(actualround)
