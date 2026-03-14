class CPlayer:
    def __init__(self, ident, nbjoueurs, Config, res):
        #self.colheight = min(int((res['y']/1.8)/nbjoueurs),100) # MUST be the same than in CScreen.SetLineHeight
        #self.bottomspace = res['y'] / 40
        self.Config=Config
        self.nbcol = int(Config.GetValue('SectionGlobals','nbcol'))
        #self.posy = int(res['y']-nbjoueurs*self.colheight + ident*self.colheight - self.bottomspace)
        self.ident = ident
        # Init value of each column for this player
        self.LSTColVal = []
        for x in range(0,self.nbcol+1):
            self.LSTColVal.append(('','txt',None))
        # Init Player name
        self.PlayerName = "Player{}".format(self.ident+1)
        # Stats table
        self.Stats={}

        ############################
        #### Player Properties (Please use them)
        ############################
        # Score is the value displayed in the last column. "Current"
        self.score = 0
        # TotalPoints is the total count of point accumulated by the player, even if it is not equal to score
        self.TotalPoints = 0
        # Count how many valid hits the player reached for the whoel game
        self.hits = 0
        # Count how many valid hits the player reached in this round
        self.roundhits = 0
        # Count the points accumulated in current round
        self.pointsinround = 0
        # Count total of dart thrown. In some games it could differents from max_round*3.
        self.dartsthrown = 0
    #
    def InitPlayerColor(self,color):
        self.couleur= color
    #
    def GetPositiony(self):
        return self.posy
    #
    def GetCouleur(self):
        return self.couleur
    #
    def GetColVal(self,Col):
        if self.LSTColVal[Col][1] == 'int':
            return int(self.LSTColVal[Col][0])
        else:
            return self.LSTColVal[Col][0]
    #
    def IncrementColTouch(self,Col):
        if self.LSTColVal[Col][1] == 'int' or self.LSTColVal[Col][1] == 'leds':
            thetype = self.LSTColVal[Col][1]
            nb = self.LSTColVal[Col][0] + 1
            color = self.LSTColVal[Col][2]
            self.LSTColVal[Col] = (nb,thetype,color)
        else:
            return False

    # If a touch given, Increment with correponding value, else, add touch value
    def IncrementHits(self,Hit=1):
        if str(Hit)[:1] == 'S':
            self.hits+=1
        elif str(Hit)[:1] == 'D':
            self.hits+=2
        elif str(Hit)[:1] == 'T':
            self.hits+=3
        else:
            self.hits+=Hit

    # Increment and Decrement A column
    def IncrementCol(self,Nb,Col):
        if self.LSTColVal[Col][1] == 'int':
            color = self.LSTColVal[Col][2]
            oldnb = self.LSTColVal[Col][0]
            self.LSTColVal[Col] = (oldnb + Nb, 'int',color) 
        else: 
            return False

    # Remove nb unit from a column
    def DecrementCol(self,Nb,Col):
        if self.LSTColVal[Col][1] == 'int':
            color = self.LSTColVal[Col][2]
            oldnb = self.LSTColVal[Col][0]
            self.LSTColVal[Col] = (oldnb - Nb, 'int',color) 
        else:
            return False

    # Find if a touch is a Simple, Double, Triple
    def GetTouchType(self,Touch):
        if Touch[:1] == 'S':
            value = "Simple "
        elif Touch[:1] == 'D':
            value = "Double "
        elif Touch[:1] == 'T':
            value = "Triple "
        if Touch[1:] == "B":
            value += "Bull"
        else:
            value += Touch[1:]
        return value

    # Return touch unit ( 1 for simple, 2 for double, and 3 for triple)
    def GetTouchUnit(self,Touch):
        if Touch[:1] == 'S':
            return 1
        elif Touch[:1] == 'D':
            return 2
        elif Touch[:1] == 'T':
            return 3

    # Return Total Hit
    def GetTotalHit(self):
        return self.hits

    # Add point to players' score
    def ModifyScore(self,qty):
        self.score+=qty
        return self.score

    # Set score to given
    def SetScore(self,Score):
        self.score=Score
        return self.score

    def GetScore(self):
        return int(self.score)

    # Returns the id of the previous player
    def GetPreviousPlayerId(self,totalnbplayers):
        if self.ident>0:
            return self.ident-1
        else:
            return totalnbplayers-1

    #########
    # Stats based on number of Dart Thrown * 3
    #########
    
    # Return MPR ((hits/darts thrown)*3) (sems to be official calculation method)
    def ShowMPR(self):
        try:
            mpr = round((float(self.hits)/float(self.dartsthrown))*3,2)
        except:
            mpr = 0.00
        return mpr

    # Return Points Per Dart
    def ShowPPD(self):
        try:
            ppd = round(float(self.TotalPoints)/float(self.dartsthrown),2)
        except:
            ppd = 0.00
        return ppd

    # Return Points Per Round
    def ShowPPR(self):
        try:
            ppr = round((float(self.TotalPoints)/self.dartsthrown)*3,2)
        except:
            ppr = 0.00
        return ppr

    #########
    # AVG based on actualround
    #########

    # Return Average points per round
    def AVG(self,actualround):
        return round((float(self.TotalPoints)/actualround),2)

    # Return score divided per number of rounds
    def ScorePerRound(self,actualround):
        return round(float(self.score) / float(actualround),2)

    # Return a basic score per round
    def HitsPerRound(self,actualround):
        return round(float(self.hits) / float(actualround),2)


