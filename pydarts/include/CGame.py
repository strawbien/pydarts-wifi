from copy import deepcopy  # For backupTurn
import collections

# This class is used for common methods and var shared by games - All games have a inherited version of this class
class CGame:
    def __init__(self, myDisplay, GameChoice, nbplayers, GameOpts, Config, Logs):
        self.Logs = Logs
        self.GameOpts = GameOpts
        self.GameChoice = GameChoice
        self.nbplayers = nbplayers
        self.Config = Config
        self.myDisplay = myDisplay
        self.TxtRecap = ""
        self.nbcol = int(self.Config.GetValue('SectionGlobals', 'nbcol'))
        self.RandomIsFromNet = False
        # Init and Override default scores if relevant
        self.ScoreMap = deepcopy(self.Config.DefaultScoreMap)

    def PreDartsChecks(self, players, actualround, actualplayer, playerlaunch):
        self.TxtRecap = ""
        return_code = 0
        # TxtRecap Can be used to create a per-player debug output
        self.TxtRecap += "###### Player {}: {} ######\n".format(actualplayer + 1, players[actualplayer].PlayerName)
        # You will probably save the turn to be used in case of backup turn (every first dart) :
        if playerlaunch == 1:
            self.SaveTurn(players)
        #####
        # Write your code here.
        #####
        # Return codes are :
        #  1 - Jump to next player immediatly
        #  2 - Game is over
        #  3 - There is a winner (self.winner must hold winner id)
        #  4 - The player is not allowed to play (jump to next player)
        # Send debug output to log system. Use DEBUG or WARNING or ERROR or FATAL
        self.Logs.Log("DEBUG", self.TxtRecap)
        return return_code

        ###############

    # Function run after each dart throw
    # for example, add points to player
    # Check return codes.
    def PostDartsChecks(self, hit, players, actualround, actualplayer, playerlaunch):
        # Return codes are : 1 : Next player 2 : Game Over 3 : Winner id is self.winner
        return_code = 0
        ####
        # Main game code will be here
        ####

        # You may want to keep current score (which is displayed in the last column)
        players[actualplayer].ModifyScore(self.ScoreMap.get(hit))

        # You may want to keep the "Total Points" (Global amount of grabbed points, follow the player all game long)
        players[actualplayer].TotalPoints += self.ScoreMap.get(hit)

        # You may want to display score on screen
        players[actualplayer].LSTColVal[playerlaunch - 1] = [self.ScoreMap.get(hit), 'txt']

        # You may want to count how many touches (Simple = 1 touch, Double = 2 touches, Triple = 3 touches)
        players[actualplayer].IncrementHits(hit)

        # You may want to count darts played
        players[actualplayer].dartsthrown += 1
        
        # You may want to play sound if the hit is valid
        self.myDisplay.Sound4Touch(hit)

        # It is recommended to update stats every dart thrown
        self.RefreshStats(players, actualround)

        # Return codes are :
        #  1 - Jump to next player immediately
        #  2 - Game is over
        #  3 - There is a winner (self.winner must hold winner id)
        #  4 - The player is not allowed to play (jump to next player)
        # Return code to main loop
        return return_code

    ###############
    # Common Game Stats Handling - Construct stats stable and return it to be displayed
    def GameStats(self, Players, actualround, Scores=False):
        # New Score method (Sqlite DB)
        if Scores:
            data = {}
            for GS in self.GameRecords:
                for P in Players:
                    # Keep game name
                    data['gamename'] = self.GameChoice
                    # Construct options data
                    data['gameoptions'] = ""
                    for opts in self.GameOpts:
                        data['gameoptions'] += str(opts) + "=" + str(self.GameOpts[opts]) + "|"
                    # Game stats must be initated at top of this file
                    data['scorename'] = GS
                    # This stat is calculated like this
                    data['score'] = str(P.Stats[GS])
                    # Playername is obviously consigned
                    data['playername'] = P.PlayerName
                    # Add data to Sqlite DB
                    try:
                        Scores.AddScore(data)
                    except:
                        self.Logs.Log("ERROR", "Error inserting data into local database")
                        return False
        return True

    #################################################
    # Backup player properties to use with BackupTurn
    def SaveTurn(self, Players):
        # Create Backup Properies Array
        try:
            self.PreviousBackUpPlayer = deepcopy(self.BackUpPlayer)
        except:
            self.Logs.Log("DEBUG", "Probably first player of first round. Nothing to backup.")
            self.PreviousBackUpPlayer = deepcopy(Players)
        self.BackUpPlayer = deepcopy(Players)
        self.Logs.Log("DEBUG", "Backuped score in case of BackUpTurn request.")

    ##################################################
    # Run when player push PLAYERBUTTON before last dart
    def EarlyPlayerButton(self, Players, actualplayer, actualround):
        return_code=1
        Players[actualplayer].dartsthrown += 1
        self.Logs.Log("DEBUG", "You pushed player button and default action will occur.")
        if actualround == int(self.maxround) and actualplayer == self.nbplayers - 1:
            self.Logs.Log("DEBUG", "At last round, default action is to return game over. if it's not what you expect, raise a bug please.")
            # If its a EarlyPlayerButton just at the last round - return GameOver
            return 2
        return return_code

    #################
    # MISSED BUTTON
    def MissButtonPressed(self,Players,actualplayer,actualround,playerlaunch):
        return_code=0
        self.Logs.Log("DEBUG","You missed the dart (or pressed the missbutton) and default action will occur.")
        # Return same code than EarlyPlayerButton and perform the same actions
        if playerlaunch==int(self.nbdarts):
            self.Logs.Log("DEBUG","Running the EarlyPlayerButton method because it is last dart.")
            return_code = self.EarlyPlayerButton(Players,actualplayer,actualround)
            self.Logs.Log("DEBUG","Which return {}".format(return_code))
        # Or just increment dart thrown
        else:
            Players[actualplayer].dartsthrown += 1
        # And return value
        return return_code

    ###############
    # Returns Random things, to send to clients in case of a network game
    # If there is no random values in your game, leave it like this
    def GetRandom(self, Players, actualround, actualplayer, playerlaunch):
        return None  # Means that there is no random

    ###############
    # Set Random things, while received by master in case of a network game
    # If there is no random values in your game, leave it like this
    def SetRandom(self, Players, actualround, actualplayer, playerlaunch, data):
        pass

    ###############
    # Define the next game players order, depending of previous games' scores
    # This function reorder players for the next match, based for exemple on final scores of previous game
    def DefineNextGameOrder(self, Players):
        Sc = {}
        # Create a dict with player and his score
        for P in Players:
            Sc[P.PlayerName] = P.score
        # Order this dict depending of the score
        NewOrder = collections.OrderedDict(
            sorted(Sc.items(), key=lambda t: t[1]))  # For DESC order, add "reverse=True" to the sorted() function
        FinalOrder = list(NewOrder.keys())
        # Return
        return FinalOrder

    ###############
    # Check for handicap and record appropriate marks for player
    #
    def CheckHandicap(self, players):
        pass
