# -*- coding: utf-8 -*-
import os
import sys
#from . import CLogs
import serial # To detect serial port
import glob# used in FindSerialPort method
# Import library depending of python version
if sys.version[:1]=='2':
   import ConfigParser as configparser
elif sys.version[:1]=='3':
   import configparser
# pyDarts running Version
pyDartsVersion="1.2.0-rc1"
# pyDarts official running wiki
wiki="https://obilhaut.freeboxos.fr/pydarts-wiki"
# Official website
officialwebsite="http://pydarts.sourceforge.net"

#
# Default values and default config file structure
#
ConfigList = {}
#
ConfigList['SectionGlobals'] = {       'connection_type':'serial',
                                       'wifi_port':8000,
                                       'serialport':None,
                                       'serialspeed':9600,
                                       'blinktime':3000,
                                       'solo':2000,
                                       'releasedartstime':1800,
                                       'resx':1000,
                                       'resy':700,
                                       'fullscreen':0,
                                       'nbcol':6,
                                       'soundvolume':100,
                                       'colorset':'clear',
                                       'espeakpath':'/usr/bin/espeak',
                                       'debuglevel':2,
                                       'masterserver':'obilhaut.freeboxos.fr',
                                       'masterport':5006,
                                       'locale':False,
                                       'scoreonlogo':0,
                                       'onscreenbuttons':False
                                       }
#
ConfigList['SectionAdvanced'] = {      'noserial':False,
                                       'bypass-stats':False,
                                       'localplayers':False,
                                       'selectedgame':False,
                                       'gametype':False,
                                       'netgamename':False,
                                       'serverport':5005,
                                       'servername':'obilhaut.freeboxos.fr',
                                       'serveralias':False,
                                       'listen':'eth0',
                                       'clientpolltime':5,
                                       'masterclientpolltime':32,
                                       'animationduration':5,
                                       'bypass-stats':False,
                                       'clear-local-db':False,
                                       'forcecalibration':False,
                                       'pydartsch_apikey':False,
                                       'speech':'pyttsx3',
                                       'enable-support':False,
                                       'games':'official'
                                 }
#
ConfigList['SectionKeys'] = {
                                        's20':'',
                                        'd20':'',
                                        't20':'',
                                        's19':'',
                                        'd19':'',
                                        't19':'',
                                        's18':'',
                                        'd18':'',
                                        't18':'',
                                        's17':'',
                                        'd17':'',
                                        't17':'',
                                        's16':'',
                                        'd16':'',
                                        't16':'',
                                        's15':'',
                                        'd15':'',
                                        't15':'',
                                        's14':'',
                                        'd14':'',
                                        't14':'',
                                        's13':'',
                                        'd13':'',
                                        't13':'',
                                        's12':'',
                                        'd12':'',
                                        't12':'',
                                        's11':'',
                                        'd11':'',
                                        't11':'',
                                        's10':'',
                                        'd10':'',
                                        't10':'',
                                        's9':'',
                                        'd9':'',
                                        't9':'',
                                        's8':'',
                                        'd8':'',
                                        't8':'',
                                        's7':'',
                                        'd7':'',
                                        't7':'',
                                        's6':'',
                                        'd6':'',
                                        't6':'',
                                        's5':'',
                                        'd5':'',
                                        't5':'',
                                        's4':'',
                                        'd4':'',
                                        't4':'',
                                        's3':'',
                                        'd3':'',
                                        't3':'',
                                        's2':'',
                                        'd2':'',
                                        't2':'',
                                        's1':'',
                                        'd1':'',
                                        't1':'',
                                        'sb':'',
                                        'db':'',
                                        'playerbutton':'',
                                        'gamebutton':'',
                                        'backupbutton':'',
                                        'missdart':''
                                       }
#
ConfigList['Server'] = {
                                    'mastertest':False,
                                    'masterclosegames':False,
                                    'notifications':False,
                                    'notifications-smtp-server':None,
                                    'notifications-sender':None,
                                    'notifications-reply':None,
                                    'notifications-username':None,
                                    'notifications-passsword':None,
                                    'clear-db':False,
                                    'server2':False
}

#
# Start of Config Class
#
class CConfig:
   def __init__(self,Args,Logs):
      # Define paths
      self.userpath=os.path.expanduser('~')
      self.pathdir='{}/.pydarts'.format(self.userpath)
      self.pathfile='{}/pydarts.cfg'.format(self.pathdir)
      # Args
      self.Args=Args
      # Local logs object
      self.Logs=Logs
      # Copy into object the value of default config
      self.ConfigList = ConfigList
      # Copy in Local variable the value of the config file
      self.ConfigFile = {}
      # If we force usage of an alternate config file via parameter --config
      config=self.Args.GetParamValue2('config')
      self.detectedserialport = False
      if config:
         self.Logs.Log("DEBUG","Using alternative config file {}".format(self.Args.GetParamValue2('config')))
         self.pathfile="{}/{}".format(self.pathdir,self.Args.GetParamValue2('config'))
      # Default score map (can be overrided in games)
      self.DefaultScoreMap = {'SB': 25,'DB': 50,
            'S20': 20, 'D20': 40, 'T20': 60,
            'S19': 19,'D19': 38,'T19': 57,
            'S18': 18,'D18': 36,'T18': 54,
            'S17': 17,'D17': 34,'T17': 51,
            'S16': 16,'D16': 32,'T16': 48,
            'S15': 15,'D15': 30,'T15': 45,
            'S14': 14,'D14': 28,'T14': 42,
            'S13': 13,'D13': 26,'T13': 39,
            'S12': 12,'D12': 24,'T12': 36,
            'S11': 11,'D11': 22,'T11': 33,
            'S10': 10,'D10': 20,'T10': 30,
            'S9': 9,'D9': 18,'T9': 27,
            'S8': 8,'D8': 16,'T8': 24,
            'S7': 7,'D7': 14,'T7': 21,
            'S6': 6,'D6': 12,'T6': 18,
            'S5': 5,'D5': 10,'T5': 15,
            'S4': 4,'D4': 8,'T4': 12,
            'S3': 3,'D3': 6,'T3': 9,
            'S2': 2,'D2': 4,'T2': 6,
            'S1': 1,'D1': 2,'T1': 3
            }
      # pyDarts running Version
      self.pyDartsVersion=pyDartsVersion
      # pyDarts running wiki
      self.wiki=wiki
      # Official website
      self.officialwebsite=officialwebsite
      # Supported games (games availables in compiled version)
      self.officialgames=['321_Zlip','Cricket','Football','Ho_One','Kapital','Kinito','Practice','Sample_game','Shanghai','Killer']
      self.allgames=self.officialgames + ['Bermuda_Triangle','By_Fives','Scram_Cricket']
      # List of compatibles versions of python
      self.supported_python_versions=('3.2','3.3','3.4','3.5','3.6','3.7','3.8','3.9')
      # Order of your dart board parts 
      self.OrderedDartKeys = ['S20','S1','S18','S4','S13','S6','S10','S15','S2','S17','S3','S19','S7','S16','S8','S11','S14','S9','S12','S5','D20','D1','D18','D4','D13','D6','D10','D15','D2','D17','D3','D19','D7','D16','D8','D11','D14','D9','D12','D5','T20','T1','T18','T4','T13','T6','T10','T15','T2','T17','T3','T19','T7','T16','T8','T11','T14','T9','T12','T5','SB','DB','PLAYERBUTTON','GAMEBUTTON','BACKUPBUTTON','EXTRABUTTON','MISSDART']
      # Print version if requested
      self.PrintVersion()




   #
   # Print Version if requested
   #
   def PrintVersion(self):
      if self.Args.GetParamValue2('version') or self.Args.GetParamValue2('V'):
         print(pyDartsVersion)
         sys.exit(0)

   #
   # Try to detect available port
   #
   def FindSerialPort(self):
      """
      Lists serial port names
         :returns:
            A list of the serial ports available on the system
      """
      self.Logs.Log("DEBUG","Your operating system has been detected as :"+sys.platform)
      if sys.platform.startswith('win'):
         ports = ["COM{}".format(i + 1) for i in range(256)]
      elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
         # this excludes your current terminal "/dev/tty"
         ports = glob.glob('/dev/tty[A-Za-z0-9]*')
      elif sys.platform.startswith('darwin'):
         ports = glob.glob('/dev/tty.*')
      else:
         self.Logs.Log("WARNING","Unsupported operating system... Unable to detect serial port format.")
      #
      result = []
      for port in ports:
         try:
            s = serial.Serial(port,'9600')
            s.close()
            result.append(port)
         except Exception as e:
            self.Logs.Log("DEBUG","Connection unsuccessful on port {}".format(port))
      # Add eventually the command line suggestion of the config file value
      try:
         if self.GetValue('SectionGlobals','serialport'):
            result.append(self.GetValue('SectionGlobals','serialport'))
      except:
         pass
      # Remove duplicates
      result=list(set(result))
      if len(result)>1:
         self.Logs.Log("DEBUG", "We finally found multiple port suitable for pydarts : {}.".format(result))
         ret=result
      elif len(result)==1:
         self.Logs.Log("DEBUG", "Great ! We found only one suitable serial port : {}. We will use it in your freshly created config file !".format(result))
         ret=result
      else:
         self.Logs.Log("WARNING","Sorry dude... We found no suitable serial port... Please double check and/or adapt your config file.".format(result))
         ret=False
      self.detectedserialport=ret

#
# Check if the config file exists and if not, create it
#
   def CheckConfigFile(self):
      self.configfileexists = True
      # Create config folder in profile if necessary
      if not os.path.isfile(self.pathfile):
         self.Logs.Log("WARNING","Creating folder {}".format(self.pathdir))
         if not os.path.exists(self.pathdir):
            os.makedirs(self.pathdir)
         self.configfileexists = False
      else:
         self.Logs.Log("DEBUG","Config file {} exists. We use it so...".format(self.pathfile))

#
# Create and fill config file
#
   def WriteConfigFile(self,NewKeys):
      self.defaultconfig= ( "[SectionGlobals]\n"
                            "### Serial configuration - GNU/Linux exemple : /dev/ttyACM0 - Windows example : COM3) - Default 9600 bauds\n"
                            "serialport:{}\n".format(self.detectedserialport))
      self.defaultconfig+=(
                            "#serialspeed:9600\n\n"
                            "### Blink time of main information (ms) (good is 3000)\n"
                            "#blinktime:3000\n"
                            "### Wait between player in ms - (Solo Option - put to 0 disable it - default 2000)\n"
                            "#solo:2000\n"
                            "### Time to release darts safely after a hit on player button (good is 1000-3000)\n"
                            "#releasedartstime:1800\n"
                            "### Screen resolution - if fullscreen is set to 1, resolution is bypassed\n"
                            "#resx:1000\n"
                            "#resy:700\n"
                            "#fullscreen:0\n"
                            "### How many columns in tab without BULL's eye. Will be moved to a game setting, a day.\n"
                            "#nbcol:6\n"
                            "### Default sound volume (percent)\n"
                            "#soundvolume:100\n"
                            "### Color set (clear|dark|grayscale|make_your_own)\n"
                            "#colorset:clear\n"
                            "### Espeak path (to use voice synthesis - example on linux : /usr/bin/espeak)\n"
                            "#espeakpath:/usr/bin/espeak\n"
                            "### Debug level : 1=Debug|2=Warnings|3=Errors|4=Fatal Errors (Default 2)\n"
                            "#debuglevel:2\n"
                            "### Master Server : the server which can host Game List\n"
                            "#masterserver:obilhaut.freeboxos.fr\n"
                            "#masterport:5006\n"
                            "### Localization (en_GB, fr_FR, de_DE, es_ES, ...)\n"
                            "#locale:en_GB\n"
                            "### Score display on logo instead of normal display (0/1)\n"
                            "#scoreonlogo:0\n"
                            "### Display clickable buttons at the bottom of the screen\n"
                            "#onscreenbuttons:0\n"
                            "\n"
                            "### SectionKeys store mandatory configuration linked to your arduino configuration. Check wiki online in any doubt.\n")

      self.defaultconfig+=("[SectionKeys]\n")
      for key in self.OrderedDartKeys:
         try:
            self.defaultconfig+=("{}:{}\n".format(key.upper(),NewKeys[key]))
         except:
            pass
      self.defaultconfig+=(
                            "\n"
                            "[SectionAdvanced]\n"
                            "### You can test pydarts without any dart board connected, using this option : \n"
                            "#noserial:0\n"
                            "### If you do not want the stats to be updated, please use this option : \n"
                            "#bypass-stats:0\n"
                            "### Frequency in second for the client to poll the server for players names\n"
                            "#clientpolltime:5\n"
                            "### Stats format ('old','csv', or coming soon : 'sqlite'\n"
                            "#stats-format:old\n"
                            "### Clear score DB (for Sqlite fomat)\n"
                            "#clear-local-db:0\n"
                            "### Select speech engine (espeak or pyttsx3). Defaut is cross-platform pyttsx3\n"
                            "#speech:pyttsx3\n"
                            "### Enable non official games (\"all\" or \"official\") : \n"
                            "#games:official\n"
                            ""
                             )
      self.defaultconfig+=(
                            "\n"
                            "[Server]\n"
                            "### Clear Server (Game Server or Master Server) Database at startup : \n"
                            "#clear-db:0\n"
                            "### Enable or not notifications (Master Server) : \n"
                            "#notifications:0\n"
                            "### SMTP server that will send notifications (Master Server): \n"
                            "#notifications-smtp-server:smtp.yourISP.com\n"
                            "### The email address used as the sender address (Master Server) : \n"
                            "#notifications-sender:you@yourisp.com\n"
                            "### The email address used as the reply-to address (Master Server) : \n"
                            "#notifications-reply:another@email.com\n"
                            "### Username used to authenticate on smtp server (Master Server) : \n"
                            "#notifications-username:your-username\n"
                            "### Password used to authenticate on smtp server (Master Server) : \n"
                            "#notifications-password:your-password\n"
                            "### Use the Master server in Test mode (0 or 1) - (Create fake games) : \n"
                            "#mastertest:0\n"
                            "### Close all open games in MasterServer (0 or 1) : \n"
                            "#masterclosegames:0\n"
                            ""
                             )
      try:
         self.Logs.Log("DEBUG","Writing config file : "+self.pathfile)
      except:
         pass
      try:
         file = open(self.pathfile, 'w')
         file.write(self.defaultconfig)
         file.close()
      except:
         self.Logs.Log("FATAL","Unable to write config file " + self.pathfile + ". Please check permissions. Exiting.")
         exit(1)
#
# Read a section of the config file
#
   def ReadConfigFile(self,Section):
      Config = configparser.ConfigParser()
      # If somedays you like to preserve case in options, just uncomment the following
      #Config.optionxform=str
      self.Logs.Log("DEBUG","Working on section {} of your config file.".format(Section))
      try:
         Config.read(self.pathfile)
      except:
         self.Logs.Log("FATAL","Your config file {} contain errors. Correct them or rename this file (it will be regenerated).".format(self.pathfile))
         exit (1)
      try:
         options = Config.options(Section) # Try to loads options from config file
      except Exception as e:
         if Section in self.ConfigList:#Warn only if the requested section is part of the config
            self.Logs.Log("WARNING","Your config file does not contain a section named {}.".format(Section))
         else:
            self.Logs.Log("DEBUG","Don't forget that you may create section named {} to customize pyDarts".format(Section))
         self.ConfigFile[Section]={} # Create empty config values even if the section does not exists
         return False
      DictOptions={}
      for option in options:
         try:
            DictOptions[option] = Config.get(Section, option)
         except Exception as e:
            self.Logs.Log("ERROR","Configuration issue with this option : {}".format(option))
            self.Logs.Log("DEBUG","Error was : {}".format(e))
            DictOptions[option] = None

      # Store in local object
      self.ConfigFile[Section]=DictOptions

      # Return options
      return DictOptions

#
#  Return value for an option (first search CLI args, then config file, then search default value) 
#  Break if option is required, return false otherwise
#

   def GetValue(self,Section,v,req=True):
      if v==None or Section==None:
         return False
      else:
         if self.Args.GetParamValue2(v):
            #self.Logs.Log("DEBUG","Using cli config value for {}={}".format(v,self.Args.GetParamValue2(v)))
            return self.Args.GetParamValue2(v)
         elif v in self.ConfigFile[Section]:
            #self.Logs.Log("DEBUG","Using config file value for {}:{}".format(v,self.ConfigFile[Section][v]))
            return self.ConfigFile[Section][v]
         elif v in self.ConfigList[Section]:
            #self.Logs.Log("WARNING","Using default config value for {}:{}".format(v,self.ConfigList[Section][v]))
            return self.ConfigList[Section][v]
         elif req:
            self.Logs.Log("FATAL","Error getting required config value {}. No command line, no config found, no default. Abort".format(v))
            sys.exit(1)
         else:
            return False
#
# Specific config (comma separated values)
#
   def GetPlayersNames(self):
      PlayersNames = self.GetValue('SectionAdvanced','localplayers')
      if PlayersNames:
         return PlayersNames.split(',')
      else:
         return False
