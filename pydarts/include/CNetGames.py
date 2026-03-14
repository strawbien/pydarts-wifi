#!/usr/bin/env python

class CNetGames():
   def __init__(self,GameName):
      self.GameName = GameName
      self.MembersId = []
      
      # Store the choosed game
      self.ChoosedGame = None
      
      # Store the Game Options Dict
      self.ChoosedOptions = {} # Deprecated
      self.Opts= {}
      self.nbdarts = None # Total darts each player is allowed to throw in this game

      # RandomValues will be a key/value array with a unique combination of Round/Player/Launch as key
      self.RandomValues={} # New list of max x round
      
      # HitValues will be a key/value array with a unique combination of Round/Player/Launch as key
      self.HitValues={} #
      
      # Store all the players names
      self.PlayersNames = []
      
      # Server has all informations and is ready to give them to clients
      #self.GameReady = False
         
      # All players are totally ready - game can begin
      #self.PlayersReady = 0
      #self.PlayersReadySent = False

      # Players properties
      self.Player = []
      
      # Is game ready to launch
      self.Launch = False
      # Is game aborted by Master Player
      self.Aborted = False
