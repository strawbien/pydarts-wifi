import os
import sys
import csv
# Patch for ConfigParser
if sys.version[:1]=='2':
    import ConfigParser as configparser
elif sys.version[:1]=='3': 
    import configparser
import time
#
class CStats:
    def __init__(self,GameName,Logs):
        self.Logs=Logs
        self.userpath=os.path.expanduser('~')
        self.pathdir='{}/.pydarts'.format(self.userpath)
        self.pathfile='{}/playerstats.csv'.format(self.pathdir)
        self.StatsFile = configparser.ConfigParser()
        self.PlayerStatDict = {}
        #
        self.GameName = GameName
        self.CheckStatsFile()
        self.WritetoDict()

# Playerstats.csv columns: 0:CricketMarks,1:CricketThrows,2:CricketMPR,3:01Throws,4:01Points,5:01PPR,6:01PPD
    def CheckStatsFile(self):
        """ Check Stat File existence. Create it if necessary """
        if not os.path.isfile(self.pathfile):
            self.Logs.Log("WARNING","Stats file {} doesn't exists. Creating...".format(self.pathfile))
        if not os.path.exists(self.pathdir):
            os.makedirs(self.pathdir)
        self.WritetoCSV()
        
#
    def WritetoDict(self):
        with open(self.pathfile,'r') as infile:
            reader = csv.reader(infile)
            for row in reader:
                key = row[0]
                if key in self.PlayerStatDict:
                    self.Logs.Log("WARNING","This name is duplicated in the file!  Skipping!")
                pass
                self.PlayerStatDict[key] = row[1:]
#
    def WritetoCSV(self):
        with open(self.pathfile,'w') as f:
            for k,v in self.PlayerStatDict.items():
                f.write(str.join(',', [k]+[str(i) for i in v])+'\n')
#
    def MPR(self,player):
        marks = float(self.PlayerStatDict[player][0])
        throws = float(self.PlayerStatDict[player][1])
        totl = float((marks/throws)*3)
        self.Logs.Log("DEBUG","Marks:{}, Throws:{} , MPR:{}".format(marks,throws,totl))
        self.PlayerStatDict[player][2] = str(round(totl,6))
#
    def IncreaseCricketMarks(self,player,increase):
        marks = int(self.PlayerStatDict[player][0])
        marks += increase
        self.PlayerStatDict[player][0] = str(marks)
#
    def IncreaseCricketThrows(self,player,increase):
        throws = int(self.PlayerStatDict[player][1])
        throws += increase
        self.PlayerStatDict[player][1] = str(throws)
#
    def PPD(self,player):
        throws = int(self.PlayerStatDict[player][3])
        totalscore = int(self.PlayerStatDict[player][4])
        try:
            totl = float(totalscore/throws)
        except:
            totl = 0
        self.PlayerStatDict[player][6] = str(round(totl,2))
#
    def PPR(self,player):
        throws = int(self.PlayerStatDict[player][3])
        totalscore = int(self.PlayerStatDict[player][4])
        try:
            totl = float((totalscore/throws)*3)
        except:
            totl = 0
        self.PlayerStatDict[player][5] = str(round(totl,2))
#
    def Increase01Points(self,player,totalscore):
        points = int(self.PlayerStatDict[player][4])
        points += totalscore
        self.PlayerStatDict[player][4] = str(points)
#
    def Increase01Throws(self,player,increase):
        throws = int(self.PlayerStatDict[player][3])
        throws += increase
        self.PlayerStatDict[player][3] = str(throws)
