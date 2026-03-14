#!/usr/bin/env python
#-*- coding: utf-8 -*-
# Import dependancies
try:
   import requests
   import json
   dependancies=True
except Exception as e: # Report error
   print(e)
   dependancies=False

#
# External api pydarts.ch
#
class pydartsCh:
   def __init__(self,Logs,Config):
      # Take required objects
      self.Logs=Logs
      self.Config=Config
      self.apikey = self.Config.GetValue('SectionAdvanced','pydartsch_apikey')
      self.url_game="http://pydarts.ch/api/Games"
      self.url_darts = "http://pydarts.ch/api/Results"
      self.url_winner = "http://pydarts.ch/api/Winner"
      # Flag used to determine if this tool is enabled or not
      self.enabled=True
      # Remote id of the current game. It s gathered when you run SaveGame and then sent with all darts
      self.remoteid=False#
      self.timeout=2
#
#
#
   def __main__(self):
      # Check api key
      if not self.apikey:
         self.Logs.Log("DEBUG","Pydarts.ch stats tool disabled cause no apikey is set.")
         self.enabled=False
      # Check dependancies
      if not dependancies:
         self.Logs.Log("DEBUG","Unable to load dependancy 'requests' or 'json' for Pydarts.ch. External has been disabled")
         self.enabled=False
      return self.enabled

#
#
#
   def SaveGame(self,gamename,GameOpts):  
      data = {}
      data['apiKey'] = str(self.apikey)
      data['gameName'] = str(gamename)
      data['options'] = str(GameOpts)
      self.Logs.Log("DEBUG","Sending game creation to Pydarts.ch : {}".format(data))
      r = requests.post(self.url_game, json=data, timeout=self.timeout)
      d=json.loads(str(r.text.decode('UTF-8')))
      self.remoteid = d['id']
      self.Logs.Log("DEBUG","Pydarts.ch remote game id is {}".format(self.remoteid))

#
#
#
   def SaveDart(self,playername,actualround,score,value,hit,playerlaunch):
      if not self.remoteid:
         self.Logs.Log("ERROR","Pydarts.ch remote game id is not defined. Unable to send darts data without it.")
         return False
      data = {}
      data['gameId'] =  self.remoteid
      data['apiKey'] = str(self.apikey)
      data['playerName'] = str(playername)
      data['round'] = actualround
      #data['preScore'] = prescore
      data['score'] = score
      data['Points'] = value
      data['Hit'] = hit
      data['Dart'] = playerlaunch
      #json_data = json.dumps(data)
      self.Logs.Log("DEBUG","Sending Dart score to Pydarts.ch remote webservice : {}".format(data))
      r = requests.post(self.url_darts, json=data, timeout=self.timeout)
      self.Logs.Log("DEBUG","Received from Pydarts.ch remote webservice : {}".format(r.text))
#
#
#
   def SaveWinner(self,winnername,actualround,GameOpts): 
      data = {}
      data['GameId'] = self.remoteid
      data['Winner'] = str(winnername)
      data['Round'] = actualround
      self.Logs.Log("DEBUG","Sending winner to Pydarts.ch : {}".format(data))
      r = requests.post(self.url_winner, json=data, timeout=self.timeout)
      d=json.loads(str(r.text.decode('UTF-8')))
