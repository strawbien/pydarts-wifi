import sqlite3
import os
import sys
# Patch for ConfigParser
if sys.version[:1]=='2':
   import ConfigParser as configparser
elif sys.version[:1]=='3': 
   import configparser
import time
#

class CScores2:
   def __init__(self,Config,Logs):
      self.Config=Config
      self.Logs=Logs
      self.userpath=os.path.expanduser('~')
      self.pathdir='{}/.pydarts'.format(self.userpath)
      self.db='{}/scores.db'.format(self.pathdir)
      self.DBChecks()
#
   def connect(self):
      """ 
      Create a database connection to the SQLite database
         specified by the db_file
         :param db_file: database file
         :return: Connection object or None
      """
      try:
         self.cx = sqlite3.connect(self.db)
      except Exception as e:
         self.Logs.Log("ERROR","{}".format(e))
      return None
#
   def DBChecks(self):
      if not os.path.exists(self.pathdir):
         os.makedirs(self.pathdir)
      # Connect to db
      self.connect()
      # Purge if requested
      if self.Config.GetValue('SectionAdvanced','clear-local-db'):
         self.Logs.Log("WARNING","Squeezing any existing table in {}".format(self.db))
         sql='DROP table scores'
         cur = self.cx.cursor()
         cur.execute(sql)
         sql='DROP table games'
         cur = self.cx.cursor()
         cur.execute(sql)
        # Create structure if needed
      sql="""
            CREATE TABLE IF NOT EXISTS scores 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
            game_id INTEGER,
            scorename TEXT,
            score FLOAT,
            playername TEXT)
            """;
      cur = self.cx.cursor()
      cur.execute(sql)
      self.cx.commit()


      sql="""
         CREATE TABLE IF NOT EXISTS games
         (  id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATETIME,
            gamename TEXT,
            gameoptions TEXT,
            nbplayers INT
         )
         """
      cur = self.cx.cursor()
      cur.execute(sql)
      self.cx.commit()

      if self.cx:
         self.cx.close()
#
   def AddGame(self,data):
      self.gamename=data['gamename']
      self.gameoptions=data['gameoptions']
      self.nbplayers=data['nbplayers']
      self.connect()
      # Replaced CURRENT_TIMESTAMP by datetime('now','localtime'),
      sql="""
            INSERT INTO games (
            date,
            gamename,
            gameoptions,
            nbplayers)
            VALUES (
            datetime('now','localtime'),
            '""" + str(data['gamename']) + """',
            '""" + str(data['gameoptions']) + """',
            """ + str(data['nbplayers']) + """
            )
            """;
      #print(sql)
      # Get cursor
      cur = self.cx.cursor()
      # Exsecute query
      cur.execute(sql)
      # Get last inserted id
      game_id=cur.lastrowid
      # Commit changes
      self.cx.commit()
      # Close cx if its still open
      if self.cx:
         self.cx.close()
      self.game_id=game_id
      return game_id

#
   def AddScore(self,data):
      self.connect()
      sql="""
            INSERT INTO scores (
            game_id,
            scorename,
            score,
            playername)
            VALUES (
            '""" + str(self.game_id) + """',
            '""" + str(data['scorename']) + """',
            '""" + str(data['score']) + """',
            '""" + str(data['playername']) + """'
            )
            """;
      # Get cursor
      cur = self.cx.cursor()
      # Exsecute query
      cur.execute(sql)
      # Commit changes
      self.cx.commit()
      # Close cx if its still open
      if self.cx:
         self.cx.close()
#
   def GetScoreTable(self,scorename,orderby,current=False):
      self.connect()
      #
      if current:
         sql_this_game_only="""AND games.id='""" + str(self.game_id) + """'"""
      else:
         sql_this_game_only=""
      #
      sql="""
            SELECT 
               CASE games.id
                  WHEN """ + str(self.game_id) + """ THEN 1
                  ELSE 0
               END hiscore,
               date,
               playername,
               score
            FROM scores
            LEFT JOIN games on scores.game_id=games.id
            WHERE
            gameoptions='""" + str(self.gameoptions) + """'
            AND
            gamename='""" + str(self.gamename) + """'
            AND
            scorename='""" + str(scorename) + """'
            """ + sql_this_game_only + """
            ORDER BY score """ + str(orderby) + """
            LIMIT 12
            """;
      # Get cursor
      cur = self.cx.cursor()
      # Exsecute query
      cur.execute(sql)
      # Get rows
      rows = cur.fetchall()
      return rows

# OLD CLASS managing text-style hi score
class CScores:
   def __init__(self,GameName,Logs):
      self.Logs=Logs
      self.userpath=os.path.expanduser('~')
      self.pathdir='{}/.pydarts'.format(self.userpath)
      self.pathfile='{}/scores.txt'.format(self.pathdir)
      self.ScoreFile = configparser.ConfigParser()
      #
      self.GameName = GameName
      self.CheckScoreFile()
      self.CheckSection()
      #
      self.hi_score_nb = 3 # Number of hiscore to keep in the score file for each hiscore
#
   def CheckScoreFile(self):
      """ Check Score File existence. Create it if necessary """
      if not os.path.isfile(self.pathfile):
         self.Logs.Log("DEBUG","Scores file {} don't exists. Creating...".format(self.pathfile))
         if not os.path.exists(self.pathdir):
            os.makedirs(self.pathdir)
         file = open(self.pathfile, 'w')
         file.close()
#
   def CheckSection(self,Section=None):
      """ Create game section if not exists """
      if Section == None : Section = self.GameName
      if Section != None:
         self.ScoreFile.read(self.pathfile)
         if not self.ScoreFile.has_section(Section):
            self.Logs.Log("DEBUG","Creating section [{}] in score file".format(Section))
            file = open(self.pathfile, 'a')
            file.write('[{}]\n'.format(Section))
            file.close()
#
   def GetValue(self,ScoreName,valuetype=None):
      """ Get Option value """
      self.ScoreFile.read(self.pathfile)
      if self.ScoreFile.has_option(self.GameName,ScoreName):
         if valuetype=='int':
            return self.ScoreFile.getint(self.GameName, ScoreName)
         elif valuetype=='float':
            return self.ScoreFile.getfloat(self.GameName, ScoreName)
         elif valuetype=='boolean':
            return self.ScoreFile.getboolean(self.GameName, ScoreName)
         else:
            return self.ScoreFile.get(self.GameName, ScoreName)
#
   def CheckHiScorePosition(self,ScoreName,TypeValue,Value,ScoreType='HI'): # HI or LOW (type of Hiscore or Lowscore)
      position = None
      for i in range(1,self.hi_score_nb+1):
         # Retrieve value depending of the type
         if self.ScoreFile.has_option(self.GameName,ScoreName + '_' + str(i)):
            try:
               if TypeValue=='int': FileValue=self.ScoreFile.getint(self.GameName, ScoreName + '_' + str(i))
               elif TypeValue=='float': FileValue=self.ScoreFile.getfloat(self.GameName, ScoreName + '_' + str(i))
            except Exception as e:
               self.Logs.Log("WARNING","Problem with your score file for value {}. You will be set to first place.".format(ScoreName + '_' + str(i)))
         else: return 1 # If the score number 1 doesnt exist in the file you are sure to be on the first place of the podium
         # Compare it on ScoreType criteria
         if ((ScoreType=='HI' and Value > FileValue) or (ScoreType == 'LOW' and Value < FileValue)):
            position = i
            #debug-print "Your position has been found in the HiScores file: " + str(position)
            return position
#
   def GetPlayerName4Value(self,ScoreName):
      self.ScoreFile.read(self.pathfile)
      try:
         return self.ScoreFile.get(self.GameName, "{}_who".format(ScoreName))
      except:
         self.Logs.Log("DEBUG","No player name for Hi Score value {}_who, creating with empty score".format(ScoreName))
         self.UpdateValue(ScoreName,'0',"DefaultPlayer")
#
   def UpdateValue(self,ScoreName,Value,PlayerName):
      """ Update/Create Value Option """
      self.ScoreFile.read(self.pathfile)
      if self.ScoreFile.has_option(self.GameName,ScoreName):
         self.Logs.Log("DEBUG","Resetting value {}. Now it is {}/{}".format(ScoreName,Value,PlayerName))
         self.ScoreFile.set(self.GameName,ScoreName,Value)
         self.ScoreFile.set(self.GameName,"{}_who".format(ScoreName),PlayerName)
         with open(self.pathfile, 'w') as configfile:
            self.ScoreFile.write(configfile)
      else:
         self.Logs.Log("DEBUG","The score {} doesn\'t exists in the Score file. Creating...".format(ScoreName))
         ActualOptions=self.ReadGameScores()
         # Remove Section
         self.ScoreFile.remove_section(self.GameName)
         with open(self.pathfile, 'w') as configfile:
            self.ScoreFile.write(configfile)
         # Create Section
         self.CheckSection()
         # Append old options
         file = open(self.pathfile, 'a')
         for ActualScore,ActualValue in list(ActualOptions.items()):
            file.write("{} = {}\n".format(ActualScore,ActualValue))
         # Append new one to the end of the file
         file.write("{} = {}\n".format(ScoreName, Value))
         file.write("{}_who = {}\n".format(ScoreName,PlayerName))
         file.close()
#
   def InsertHiScore(self, ScoreName, Place, Value, PlayerName):
      """ Insert a Hi score in a existing list"""
      """ Downgrade all other score to make a hole for inserting the score and then insert it at requested place """
      self.DowngradeScore(ScoreName, Place)
      self.UpdateValue(ScoreName + '_' + str(Place), Value, PlayerName)
#
   def DowngradeScore(self, ScoreName, Place):
      """ Shift the scores from up to down starting from the penultimate place, to the place given (future place for a new hi score) """
      startingplace = self.hi_score_nb - 1
      for i in range(startingplace,Place-1,-1):
         PreviousPlace = i + 1
         ScoreValue = self.GetValue(ScoreName + '_' + str(i))
         ScoreWho = self.GetValue(ScoreName + '_' + str(i) + '_who')
         self.UpdateValue(ScoreName + '_' + str(PreviousPlace), ScoreValue, ScoreWho)
#
   def ReadGameScores(self,GameName=None):
      if GameName == None:
         GameName = self.GameName
      """ Read all game scores and return them in a Dict """
      self.ScoreFile.read(self.pathfile)
      options = self.ScoreFile.options(GameName)
      DictOptions={}
      for option in options:
         try:
            DictOptions[option] = self.ScoreFile.get(GameName, option)
         except:
            self.Logs.Log("DEBUG","HiScore issue with value : {}!".format(option))
            DictOptions[option] = None
      return DictOptions
