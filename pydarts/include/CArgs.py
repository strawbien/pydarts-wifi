# To use exit...
import sys,getopt,struct
# To get config

try:
   from netifaces import AF_INET, AF_INET6
   import netifaces as ni
except:
   pass

class CArgs:
   def __init__(self):
      # Init
      self.NetServer=None
      self.NetPort=None
      self.GameName=None
      self.NetAlias=None
      #
      # Usage Message
      #
      self.Usage = '--- Pydarts Help Page ---\n'
      self.Usage += '\n[ Main options ]\n'
      self.Usage += '--help | -h\t\tprint this help page\n'
      self.Usage += '--version | -V\t\tprint pyDarts version\n'
      self.Usage += '--soundvolume=\t\tset sound volume (%)\n'
      self.Usage += '--debuglevel=\t\tverbosity level (1-4) 1:Debug 2:Warnings 3:Errors 4:Fatal errors\n'
      self.Usage += '--solo=\t\t\ttime between players (s) (0 means you need to push PLAYER)\n'
      self.Usage += '--fullscreen\t\tenable fullscreen (bypass resx and resy)\n'
      self.Usage += '--resx=\t\t\tX resolution (pixels)\n'
      self.Usage += '--resy=\t\t\tY resolution (pixels)\n'
      self.Usage += '--config=\t\tuse an alternate config file (relative to your $HOME/.pydarts config folder)\n'
      self.Usage += '--scoreonlogo\t\tdisplay score on logo instead of displaying it on the middle of the screen\n'
      self.Usage += '--onscreenbuttons\t\tdisplay clickable buttons at the bottom of the screen\n'
      self.Usage += '\n[ Network options ]\n'
      self.Usage += '--netgamename=\t\tpreset network game name\n'
      self.Usage += '--servername=\t\tpreset network game server or ip address\n'
      self.Usage += '--serveralias=\t\tpreset network server alias (usefull to send to master server a public IP / behind NAT)\n'
      self.Usage += '--serverport=\t\tlisten or join server on that port. (Default 5005).\n'
      self.Usage += '--masterport=\t\tlisten or join master server on that port (default 5006)\n'
      self.Usage += '\n[ Servers options ]\n'
      self.Usage += '--listen=\t\tlistening interface (server & master server only). Default is eth0.\n'
      self.Usage += '--serverport=\t\tlisten or join server on that port. (Default 5005).\n'
      self.Usage += '--masterport=\t\tlisten or join master server on that port (default 5006)\n'
      self.Usage += '--notifications=\tEnable (1) or disable (0) Master Server notifications (default 0)\n'
      self.Usage += '--clear-db\tClear all games history when launching the Master Server (default 0)\n'
      self.Usage += '\n[ Advanced options ]\n'
      self.Usage += '--locale=\t\tSelect pydarts interface language (en_GB, fr_FR, es_ES, de_DE... more languages soon !)\n'
      self.Usage += '--bypass-stats\t\tbypass stats updates\n'
      self.Usage += '--noserial\t\tbypass serial connexion test\n'
      self.Usage += '--serialport=\t\tspecify serial port to use\n'
      self.Usage += '--serialspeed=\t\tspecify serial speed\n'
      self.Usage += '--mastertest\t\tcreate fake games in MasterServer (test purpose)\n'
      self.Usage += '--masterclosegame\t\tclose all open games on this Master Server (cleaning purpose)\n'
      self.Usage += '--animationduration=\tduration for every round animation (ms default:5)\n'
      self.Usage += '--forcecalibration\tforce board calibration even if config file already exists\n'
      self.Usage += '--clear-local-db\tClear all locally stored hi-score and game history (default 0)\n'
      self.Usage += '--speech=\tSelect between "espeak" or "pyttsx3" as text-to-speech engine (default is cross-platform pyttsx3)\n'
      self.Usage += '--games=\tEnable all games (all) or only supported and official games (official). Default to "official".\n'
      self.Usage += '\n[ Direct-Play Mode ]\n'
      self.Usage += 'Note : direct play allow you to launch a game without using menus - please refer to the wiki\n'
      self.Usage += '--gametype=\t\tpreset game type : only "local" is supported for now. No default.\n'
      self.Usage += '--selectedgame=\t\tpreset game selection (case sensitive). No default.\n'
      self.Usage += '--localplayers=\t\tpreset players name, comma separated, lower case. No Default.\n'
      self.Usage += '\t\t\texemple : --localplayers=foo,bar\n'


      # LIST HERE Option available for CLI
      self.shortopts='VhN:S:P:o:a:'
      self.longopts=[      'serveralias=',
                           'localplayers=',
                           'selectedgame=',
                           'gametype=',
                           'masterserver=',
                           'masterport=',
                           'serverport=',
                           'servername=',
                           'netgamename=',
                           'locale=',
                           'debuglevel=',
                           'soundvolume=',
                           'solo=',
                           'colorset=',
                           'resx=',
                           'resy=',
                           'listen=',
                           'config=',
                           'blinktime=',
                           'releasedartstime=',
                           'nbcol=',
                           'speech=',
                           'espeakpath=',
                           'serialspeed=',
                           'serialport=',
                           'animationduration=',
                           'notifications=',
                           'games=',
                           'noserial',
                           'help',
                           'version',
                           'bypass-stats',
                           'fullscreen',
                           'mastertest',
                           'masterclosegames',
                           'scoreonlogo',
                           'onscreenbuttons',
                           'forcecalibration',
                           'clear-db',
                           'server2',
                           'clear-local-db',
                           'enable-support',
                     ]
      #
      #debug - print sys.argv
      try:
         self.opts,self.args = getopt.getopt(sys.argv[1:],self.shortopts,self.longopts) # Option waiting for a value are followed by a :
      except getopt.GetoptError as err: # Print a clean message in case of unrecognized option
         print(str(err)) # will print something like "option -a not recognized"
         sys.exit(1)
      # Display help page if requested
      if self.GetParamValue2('help') or self.GetParamValue2('h'):
         print(self.Usage)
         sys.exit(0)

#
# To filter game type
#

   def GetGameType(self,gametype):
      if str(gametype) in ('local'):#For now, only local is allowed by command line
         return gametype
      else:
         return False
#
# To give Logs objects after creation
#

   def SetLogs(self,Logs):
      self.Logs=Logs

#
# Return true if an arguement is present
#
   def GetArgument(self,arg):
      #print self.args
      if arg in self.args:
         return True
#
# Return the value of a parameter, true if the parameter has no value, false otherwise
#
   def GetParamValue(self,parameter):
      return_code = False
      for opt,arg in self.opts:
         if opt == parameter:
            if arg=='':
               return_code = True
            else:
               return_code = arg
      return return_code

#
# New way to get couple param/value
#
   def GetParamValue2(self,p):
      simple="-{}".format(p)
      double="--{}".format(p)
      for opt,arg in self.opts:
         if simple==opt or double==opt:
            if arg=='':
               return True
            else:
               return arg
      return False

#
# Give Network Status
#
   def NetRequested(self):
      if self.GetParamValue2('netgamename') != False or self.GetParamValue2('localplayers') != False:
         return True
      else:
         return False

#
# Give name of requested net game
#
   def NetGameName(self):
      if self.GetParamValue2('netgamename') != False:
         self.GameName=self.GetParamValue2('netgamename')
      else:
         return False
      #print(self.GameName)
      return self.GameName
         
#
# Return Network Server
#
   def GetNetServer(self):
      self.NetServer=self.GetParamValue2('servername')
      return self.NetServer
      
#
# Return Network Server
#
   def GetNetAlias(self):
      if self.GetParamValue2('serveralias'):
         self.NetAlias=self.GetParamValue2('serveralias')
      elif self.GetParamValue2('servername'):
         self.NetAlias=self.GetParamValue2('servername')
      else:
         return False
      return self.NetAlias

#
# Return Network Server port
#
   def GetNetPort(self):
      self.NetPort=self.GetParamValue2('serverport')
      return self.NetPort


#######################
# SERVERS METHODS
#######################

#
# Get ip address from either interface name or ipaddress (search if an ip match on system)
#
   def get_ip_address(self,ifname):
      # Interfaces lookup
      ifaces = ni.interfaces()
      # Print result
      self.Logs.Log("DEBUG","Found thoses interfaces : {}".format(ifaces))
      # Try to find ipaddress from interface name
      try:
         self.Logs.Log("DEBUG","Searching address matching interface name : {}".format(ifname))
         ipaddress = ni.ifaddresses(ifname)[AF_INET][0]['addr']
         # return the ip associated if lookup if a success
         return ipaddress
      # If it fails
      except Exception as e:
         # Print warning
         self.Logs.Log("WARNING","Ip lookup from interface name ({}) failed. Trying from IP.".format(ifname))
         # In case of IP adress given as interface
         for iface in ifaces:
            # Iter all ifaces
            try:
               # Get IP from iface
               ipaddress=ni.ifaddresses(iface)[AF_INET][0]['addr']
            # if it fails print error
            except:
               ipaddress=None
            # Compare ip address to arg given, if it match, so the argument was an ip address
            if ipaddress==ifname:
               # Return IP given so it can use it to listen
               return ipaddress
      # If everything failed, return None
      return None
