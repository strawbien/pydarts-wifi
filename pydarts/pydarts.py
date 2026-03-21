#!/usr/bin/env python
# -*- coding: utf-8 -*-

################
# Import pyDarts internal classes and load essentials
################

try:
    from include import CConfig
    from include import CArgs
    from include import CPatchs
    from include import CLogs

    # Starts logger system, it will filter on a config basis
    Logs = CLogs.CLogs()
    # To manage cli opts
    Args = CArgs.CArgs()
    # This one handle Config File - Serial is used to try to detect serial port
    Config = CConfig.CConfig(Args, Logs)
    # Check local config file existance and create if necessary
    Config.CheckConfigFile()
    # Read config file for main configuration and store it in object data storage
    Config.ReadConfigFile("SectionGlobals")
    # Read hidden default values
    Config.ReadConfigFile("SectionAdvanced")
    # Read Config file for keys combination : Arduino send a key=>it correspond to a hit
    ConfigKeys = Config.ReadConfigFile("SectionKeys")
    # Update Logs system with loglevel set in config
    Logs.SetConfig(Config)
except Exception as e:
    print(
        "[FATAL] Unable to load internal first level dependancies or to create basic instances. Your download seems corrupted. Please download pydarts again.")
    print("[FATAL] Error was {}".format(e))
    exit(1)

#################
# Welcome
#################
print("################ Welcome to pyDarts ##########################")
print("#      A Free, Open-Source and Open-Hardware Darts Game      #")
print("#             Please check the website to know more          #")
print("#               {}               #".format(CConfig.officialwebsite))
print("#                     or check the Wiki                      #")
print("#         {}         #".format(CConfig.wiki))
print("#            or use --help for available options             #")
print("##############################################################")

#########
# External classes and system dependancies checks
#########
missing_dep = []
# To use exit
try:
    import sys
except:
    missing_dep.append('sys')
# To use time.sleep
try:
    import time
except:
    missing_dep.append('time')
# To browse folders...
try:
    import os, os.path
except:
    missing_dep.append('os')
# Pygame is the main dependancy
try:
    # To disable support prompt for pyGame, comment two last lines of /usr/lib/python3/dist-packages/pygame/__init__.py
    import pygame
    from pygame.locals import *
except:
    missing_dep.append('pygame')
# Pyserial is capital :) !
try:
    import serial
except:
    missing_dep.append('serial')
# Json used for communications with Web Services
try:
    import json
except:
    missing_dep.append('json')
# Python array deep copy (backup turn)
try:
    from copy import deepcopy
except:
    missing_dep.append('copy')
# Threading for keyboard
try:
    from threading import Thread
except:
    missing_dep.append('threading')
# To do various random
try:
    import random
except:
    missing_dep.append('random')
# To speech cross-platform
try:
    import pyttsx3
except:
    missing_dep.append('pyttsx3')
# To detect netword port
try:
    from netifaces import AF_INET, AF_INET6
    import netifaces as ni
except:
    missing_dep.append('netifaces')

if len(missing_dep) > 0:
    print("[FATAL] Unable to load following dependancies :")
    for dep in missing_dep:
        print("[FATAL] Missing : {}".format(dep))
    print("[FATAL] Unable to run pyDarts without them. Please refer to the wiki : {}".format(CConfig.wiki))
    sys.exit(1)

########################
# Create various instances of second layer internal classes
########################
from include import CInput
from include import CPlayer
from include import CScreen
from include import CLocale
from include import CExternal
from include import CClient
from include import CScores

# Create locale instance
Lang = CLocale.GTLocale(Logs, Config)
# Manage display
myDisplay = CScreen.CScreen(Config, Logs, Lang)
# Manage mouse events
Inputs = CInput.CInput(Logs, Config, myDisplay)
myDisplay.SetInputs(Inputs)  # Give input object to screen object
# Object used to apply patches
# Patch = CPatchs.CScoresPatches(Logs)
# Patch.Patch_08_01_Score_format() # New score format starting from v0.8
# Client of Master Server
NetMasterClient = CClient.MasterClient(Logs)
# pyDartsCH External API - can be removes from future versions. No news from creator :(
pydartsCh = CExternal.pydartsCh(Logs, Config)
# v1.2 SQlite score storage
Scores = CScores.CScores2(Config, Logs)

##############
# INIT
##############

# Give translations to object Inputs
Inputs.Lang = Lang

# Beautiful intro screen
myDisplay.NiceShot(Lang.lang('Welcome') + "!")

# Sound volume
soundvolume = int(Config.GetValue('SectionGlobals', 'soundvolume'))
if soundvolume:
    myDisplay.SoundVolume = soundvolume

# Sys requirements check
if sys.version[:3] not in Config.supported_python_versions:
    Logs.Log("WARNING",
             "Your version of python {} is not known as pydarts compatible. Please execute pydarts with one of this version of python : {}.".format(
                 sys.version[:3], Config.supported_python_versions))

# Verbosity
debuglevel = int(Config.GetValue('SectionGlobals', 'debuglevel'))
if debuglevel >= 1 and debuglevel <= 4:
    Logs.UpdateFacility(debuglevel)

# Run Checks for PydartsCH Api
pydartsCh.__main__()

####################
# Calibration Wizard
####################
if not Config.configfileexists or Config.GetValue('SectionAdvanced', 'forcecalibration'):
    Logs.Log("DEBUG", "Launching serial input wizard")
    Config.FindSerialPort()  # At this step, multiple serial port can be found
    # If there is multiple available devices
    if Config.detectedserialport and (
            len(Config.detectedserialport) > 1 or Config.GetValue('SectionAdvanced', 'forcecalibration')):
        selectedport = myDisplay.SelectPort(
            Config.detectedserialport)  # At this step, we display a menu to force the user to choose a port (Config.detectedserialport is a list)
        Config.detectedserialport = selectedport  # We pass the selected port to the config object (selectedport is not a list anymore)
        Logs.Log("DEBUG", "You chose port {}.".format(Config.detectedserialport))
    elif Config.detectedserialport and len(Config.detectedserialport) == 1:
        Config.detectedserialport = Config.detectedserialport[0]
        Logs.Log("DEBUG", "Using detected serial port {}".format(Config.detectedserialport))
    else:
        Logs.Log("WARNING",
                 "No suitable serial port detected. Config file will be created anyway but please setup manually first and launch pyDarts again.")
    # We connect with the unique selected port
    if not Inputs.WifiMode:
        Inputs.Serial_Connect()
    # Display first use wizard
    NewConfigKeys = myDisplay.GetConfig()
    # Write config file
    Config.WriteConfigFile(NewConfigKeys)
    # Read it
    ConfigKeys = Config.ReadConfigFile("SectionKeys")  # Refresh new keys
    # Pass config to input object
    Inputs.ConfigKeys = ConfigKeys
# Or we connect the port found in config file
else:
    if Inputs.WifiMode:
        Inputs.Wifi_Connect()
    else:
        Inputs.Serial_Connect()

#####################
# Init some vars
#####################
MatchQty = 0  # Count number of matches
solo = int(Config.GetValue('SectionGlobals', 'solo'))
bypass_stats = str(Config.GetValue('SectionAdvanced', 'bypass-stats'))
Logs.Log("DEBUG", "Solo option is set to : {} s".format(solo))
StatsScreen = False  # Return value of Stats Screen (start again a new game with same parameters)
GT = None  # Game type
directplay = None  # Direct play functionnlity (play without having to use menus)
netgamename = Config.GetValue('SectionAdvanced', 'netgamename', False)  # Game Name
servername = Config.GetValue('SectionAdvanced', 'servername', False)  # Server ip or name
serveralias = Config.GetValue('SectionAdvanced', 'serveralias', False)  # Server alias
serverport = Config.GetValue('SectionAdvanced', 'serverport')  # Server port
GT = Args.GetGameType(Config.GetValue('SectionAdvanced', 'gametype', False))  # Game type (local,netmaster,netmanual)
localplayers = Config.GetValue('SectionAdvanced', 'localplayers', False)  # Local players
selectedgame = Config.GetValue('SectionAdvanced', 'selectedgame', False)  # Selected game
LoPl = myDisplay.InitLoPl(localplayers)

######################
######## SOFTWARE LOOP
######################

while True:
    # Init (or reset) network status
    NetStatus = None  # Master or slave

    #############################
    # NEW MENUS SEQUENCE
    #############################

    ######
    # START AGAIN (possibility to start a new game straight away without using menus again)
    ######
    if StatsScreen == 'startagain':
        if GT == 'local':
            menu = True
            # Try to order players depending of game
            try:
                LoPl = objGame.DefineNextGameOrder(Players)
                AllPl = LoPl
                NuPl = len(LoPl)
            except Exception as e:
                Logs.Log("ERROR", "Unable order player from previous results. Error was {}".format(e))
        elif (GT == 'netmaster' or GT == 'netmanual'):
            NuPl = len(LoPl)
            menu = 'connect'

    ######
    # DIRECT PLAY MODE (possibility to launch a game without passing thru menus). Only available if it hasen't be disabled by any process
    ######
    elif GT == 'local' and localplayers and selectedgame and not directplay == False:
        try:
            Game = selectedgame
            menu = True
            AllPl = LoPl
            NuPl = len(LoPl)
            ChoosedGame = __import__("games.{}".format(Game), fromlist=["games"])
            # Merge config file options and default game options
            GameOpts_Default = ChoosedGame.GameOpts
            GameOpts_Config = Config.ReadConfigFile(selectedgame)  # Take config file Game options if they exists
            if not GameOpts_Config: GameOpts_Config = {}  # Default to empty dict
            GameOpts = GameOpts_Default.copy()
            GameOpts.update(GameOpts_Config)
            myDisplay.GameOpts = GameOpts
            myDisplay.selectedgame = Game
            # Enable Direct Play mode
            directplay = True
        except Exception as e:
            Logs.Log("ERROR", "Unable launch Direct Play mode. Error was {}".format(e))
            menu = 'gametype'
    else:
        menu = 'gametype'

    #######################
    # Menus loop
    #######################

    while menu != True:
        ########
        # MAIN MENU - GAME TYPE (LOCAL, NETWORK, NETWORK MANUAL)
        ########
        if menu == 'gametype':
            GT = myDisplay.GameType()
            menu = 'players'

        ########
        # PLAYERS NAMES
        ########
        if menu == 'players':
            # Display menu anyway
            LoPl = myDisplay.PlayersNamesMenu3(LoPl)  # LoPl = Local Players
            NuPl = len(LoPl)  # NuPl = Number of players

            if LoPl == 'escape':
                menu = 'gametype'
                LoPl = myDisplay.InitLoPl(localplayers)
            elif GT == 'netmaster' and LoPl != 'escape':
                menu = 'serverlist'
            elif GT == 'netmanual' and LoPl != 'escape':
                menu = 'netoptions'
            elif GT == 'local' and LoPl != 'escape':
                menu = 'gamelist'

        ########
        # NETWORK USING MASTER SERVER
        ########
        if GT == 'netmaster' and menu == 'serverlist':  # Connexion to master server if requested
            NetSettings = myDisplay.ServerList(NetMasterClient, NuPl)
            if NetSettings == 'escape':
                menu = 'players'
            else:
                menu = 'connect'
                netgamename = NetSettings['GAMENAME']
                servername = NetSettings['SERVERIP']
                serverport = NetSettings['SERVERPORT']
                serveralias = servername

        ########
        # MANUAL NETWORK CONFIG
        ########
        if GT == 'netmanual' and menu == 'netoptions':  # Display menu to manually setup or check network settings
            menu = 'connect'
            NetSettings = myDisplay.NetOptions()
            if NetSettings == 'escape':
                menu = 'players'
            else:
                netgamename = NetSettings['GAMENAME']
                servername = NetSettings['SERVERIP']
                serverport = NetSettings['SERVERPORT']
                serveralias = NetSettings['SERVERALIAS']

        ########
        # NET CONNECTION
        ########
        # If network, connect to server
        if (GT == 'netmaster' or GT == 'netmanual') and menu == 'connect':
            Logs.Log("DEBUG", "Net game requested.")
            NetClient = CClient.CClient(Logs, Config)
            solo = 0  # If network, force the SOLO MODE OFF from config (players must push PLAYERBUTTON every rounds - mandatory for network
            try:
                myDisplay.DisplayBackground()
                myDisplay.InfoMessage([Lang.lang('game-client-connecting')])
                NetClient.connect_host(servername, int(serverport))
                menu = 'net1'
            except Exception as e:
                Logs.Log("ERROR",
                         "Unable to reach server : {} on port : {}. Error is {}".format(servername, serverport, e))
                myDisplay.DisplayBackground()
                myDisplay.InfoMessage([Lang.lang('game-client-no-connection')], 3000)
                menu = 'gametype'
        # Check client/server version compatibility
        if (GT == 'netmaster' or GT == 'netmanual') and menu == 'net1':
            serverversion = NetClient.GetServerVersion(netgamename)
            myDisplay.VersionCheck(serverversion)
            menu = 'net2'
        # Then join
        if (GT == 'netmaster' or GT == 'netmanual') and menu == 'net2':
            NetStatus = NetClient.join2(netgamename)
            # If you are master go to the game selector
            if NetStatus == 'YOUAREMASTER' and StatsScreen != 'startagain':
                menu = 'gamelist'
            # If you are master and asked to start again, so... go to starting page
            elif NetStatus == 'YOUAREMASTER' and StatsScreen == 'startagain':
                menu = 'net3'
            # If you are slave go to the menu which wait for game info
            elif NetStatus == 'YOUARESLAVE':
                menu = 'net3'

        ########
        # GAME SELECTION
        ########
        if (NetStatus == 'YOUAREMASTER' or GT == 'local') and menu == 'gamelist':
            # Display game choice and option only for game creators (local and netmanual)
            Games = myDisplay.GetGameList()
            Game = myDisplay.GameList(Games)
            if Game == 'escape' and NetStatus is not None:
                NetClient.LeaveGame(netgamename, LoPl, NetStatus)
                NetClient.close_host()
                menu = 'players'
                NetStatus = None  # reset Network status if you leave network game
            elif Game == 'escape' and NetStatus is None:
                menu = 'players'
            elif Game == 'MiniGolf':
                myDisplay.PlaySound('goodchoice')
                menu = 'minigolf'
            else:
                myDisplay.PlaySound('goodchoice')
                ChoosedGame = __import__("games.{}".format(Game), fromlist=["games"])
                menu = 'gameoptions'

        ########
        # GAME OPTIONS
        ########
        if (NetStatus == 'YOUAREMASTER' or GT == 'local') and menu == 'gameoptions':
            # Display game choice and option only for game creators (local and netmanual)
            GameOpts_Default = ChoosedGame.GameOpts
            GameOpts_Config = Config.ReadConfigFile(Game)  # Take config file Game options if they exists
            if not GameOpts_Config: GameOpts_Config = {}  # Default to empty dict
            GameOpts = GameOpts_Default.copy()
            GameOpts.update(GameOpts_Config)
            #print(GameOpts)
            # MENU 3
            GameOpts = myDisplay.OptionsMenu2(GameOpts, Game)
            if GameOpts == 'escape' and NetStatus is not None:
                NetClient.LeaveGame(netgamename, LoPl, NetStatus)
                NetClient.close_host()
                menu = 'gametype'
                NetStatus = None  # reset Network status if you leave network game
            elif GameOpts == 'escape' and NetStatus is None:
                menu = 'gamelist'
            elif NetStatus is None:
                menu = True
            elif NetStatus is not None:
                menu = 'net3'

        #######################################
        # MasterPlayer send game info to server
        #######################################
        if NetStatus == 'YOUAREMASTER' and menu == 'net3':
            # Send Game info (gamename and selected options - can be merged)
            NetClient.sendGame(Game)
            NetClient.sendOpts2(GameOpts, ChoosedGame.nbdarts)  # 2
            menu = 'starting'
            try:  # Check if it is the right place
                Logs.Log("DEBUG", "Sending game info to master server {} on port {}".format(
                    Config.GetValue('SectionGlobals', 'masterserver'), Config.GetValue('SectionGlobals', 'masterport')))
                NetMasterClient.connect_master(Config.GetValue('SectionGlobals', 'masterserver'),
                                               int(Config.GetValue('SectionGlobals', 'masterport')))
                NetMasterClient.SendGameInfo(servername, serveralias, serverport, netgamename, Game, LoPl[0], NuPl)
                NetMasterClient.close_cx()
            except Exception as e:
                Logs.Log("WARNING", "Unable to reach Master Server {} on port {}. Error was : {}".format(
                    Config.GetValue('SectionGlobals', 'masterserver'), Config.GetValue('SectionGlobals', 'masterport'),
                         e))

        ########################################
        # Notice Master server that we joined and add local players to game on master server
        ########################################
        if NetStatus == 'YOUARESLAVE' and menu == 'net3':
            try:
                NetMasterClient.connect_master(Config.GetValue('SectionGlobals', 'masterserver'),
                                               int(Config.GetValue('SectionGlobals', 'masterport')))
                NetMasterClient.JoinaGame(netgamename, len(LoPl))
                NetMasterClient.close_cx()
                menu = 'starting'
            except:
                Logs.Log("WARNING", "Unable to add local players to Master Server")

        ############################
        # Network game menu - Starting - If network enabled, AllPl (All Players names) list is updated via network
        ############################
        if NetStatus is not None and menu == 'starting':
            # Wait for the choosed game from server
            if NetStatus == 'YOUARESLAVE':
                Game = NetClient.getGame()
            # Display starting page with a few game info
            AllPl = myDisplay.Starting(NetClient, NetStatus, LoPl, netgamename, Game)
            menu = True  # Means that goes on...
            if AllPl == [] or AllPl == -1:  # Empty network Player List or -1 signal
                NetClient.LeaveGame(netgamename, LoPl, NetStatus)
                NetClient.close_host()
                # For Slave Players, display the message and wait for Enter to be pressed
                if not AllPl:
                    myDisplay.InfoMessage([Lang.lang('master-player-has-left')], 0, None, 'middle')
                    NetMasterClient.connect_master(Config.GetValue('SectionGlobals', 'masterserver'),
                                                   int(Config.GetValue('SectionGlobals', 'masterport')))
                    NetMasterClient.CancelGame(netgamename)
                    NetMasterClient.close_cx()
                    Inputs.ListenInputs(['arrows'], ['escape', 'enter'])
                elif AllPl == -1:  # Notice Master server that someone is leaving
                    NetMasterClient.connect_master(Config.GetValue('SectionGlobals', 'masterserver'),
                                                   int(Config.GetValue('SectionGlobals', 'masterport')))
                    NetMasterClient.LeaveaGame(netgamename, len(LoPl))
                    NetMasterClient.close_cx()
                menu = 'gametype'
                NetStatus = None  # reset Network status if you leave network game
            else:
                menu = 'net4'
        # If network disabled - local games
        else:
            AllPl = LoPl  #  In local games, all players are local players
            NuPl = len(AllPl)  # Refresh count of number of players again

        ####################################################
        # Display message while it download info from server
        ####################################################
        if NetStatus == 'YOUARESLAVE' and menu == 'net4':
            NuPl = len(AllPl)  # Refresh count of number of players again
            myDisplay.InfoMessage([Lang.lang('getting-info-from-server')], None, None, 'middle')
            ChoosedGame = __import__("games.{}".format(Game), fromlist=["games"])
            GameOpts = NetClient.getOpts2()
            myDisplay.GameOpts = GameOpts
            myDisplay.selectedgame = Game
            Logs.Log("DEBUG","Starting a network game of {} (with options {} with {} players : {}".format(Game, GameOpts, NuPl,AllPl))
            menu = True

        ##########################
        # Players are ready - game will be launch so we can delete game from master server
        ##########################
        if NetStatus == "YOUAREMASTER" and menu == 'net4':
            NuPl = len(AllPl)  # Refresh count of number of players again
            menu = True
            try:
                NetMasterClient.connect_master(Config.GetValue('SectionGlobals', 'masterserver'),
                                               int(Config.GetValue('SectionGlobals', 'masterport')))
                NetMasterClient.LaunchGame(netgamename)
                NetMasterClient.close_cx()
            except Exception as e:
                Logs.Log("WARNING", "Unable to reach Master Server {} on port {} in order to remove game".format(
                    Config.GetValue('SectionGlobals', 'masterserver'), Config.GetValue('SectionGlobals', 'masterport')))

        ########
        # MINIGOLF — custom 60fps game loop with V2 layout
        ########
        if GT == 'local' and menu == 'minigolf':
            import pygame
            from games.MiniGolf import MiniGolfGame

            # Build player objects (lightweight wrappers around names + colors)
            class _MGPlayer:
                def __init__(self, ident, name, color):
                    self.ident      = ident
                    self.PlayerName = name
                    self.score      = 0
                    self.couleur    = color
                    self.LSTColVal  = [('', 'txt', None)] * 3
                def GetScore(self):  return int(self.score)
                def GetColor(self):  return self.couleur

            mg_colors = list(myDisplay.ColorSet.values())
            mg_players = [_MGPlayer(i, LoPl[i], mg_colors[i % len(mg_colors)])
                          for i in range(len(LoPl))]

            mg_game = MiniGolfGame(mg_players)
            myDisplay.DefineConstantsV2(nbplayers=len(mg_players))

            clock = pygame.time.Clock()
            running = True
            while running:
                try:
                    dt = min(clock.tick(60) / 1000.0, 1.0 / 30.0)  # cap to avoid first-frame jumps

                    # --- Poll input (non-blocking) ---
                    hit = Inputs.PollInput()
                    if hit == 'GAMEBUTTON':
                        running = False
                    elif hit and hit not in ('PLAYERBUTTON', 'BACKUPBUTTON') \
                             and not mg_game.is_animating:
                        result = mg_game.process_segment(hit)
                        Logs.Log("DEBUG", "MiniGolf hit {} → {}".format(hit, result.get('event')))

                    # --- Sync score panel data ---
                    for p in mg_players:
                        p.score = sum(mg_game.scores[p.ident])
                        n = mg_game.shots[p.ident]
                        for i in range(3):
                            p.LSTColVal[i] = (
                                'coup {}'.format(i+1) if i < n else '', 'txt', None)

                    # --- Render ---
                    myDisplay.screen.fill((20, 20, 20))
                    myDisplay.DrawScoresPanel(mg_players, mg_game.active_player_ident)
                    myDisplay.DrawRoundPanel(mg_players,  mg_game.active_player_ident)
                    colorset = myDisplay.ColorSet
                    myDisplay.DrawGameArea(
                        render_callback=lambda r: mg_game.render(
                            myDisplay.screen, r, colorset, dt))
                    pygame.display.flip()
                except Exception as _mg_err:
                    import traceback
                    print("=== MiniGolf EXCEPTION ===")
                    traceback.print_exc()
                    running = False

            menu = 'gametype'

    ######## END OF MENU LOOP ##########

    # Pydats.ch module
    # If enabled, send game info to pydarts.ch
    if pydartsCh.enabled:
        try:
            pydartsCh.SaveGame(Game, GameOpts)
        except Exception as e:
            Logs.Log("WARNING", "Unable send game to pydarts.ch remote database. Error was {}".format(e))

    # Now create players objects
    Players = []
    for x in range(0, NuPl):
        # Get Player color
        pcolor = list(myDisplay.ColorSet.values())[x]
        # Create Player object
        Players.append(ChoosedGame.CPlayerExtended(x, NuPl, Config, myDisplay.res))
        Players[x].InitPlayerColor(pcolor)
        Players[x].PlayerName = AllPl[x]

    ################
    # MATCH Loop
    ################

    # Match loop ends if MatchDone is true
    MatchDone = False
    # Round init
    actualround = 1
    # Player Launch Init
    playerlaunch = 1
    # Actual Player Init
    actualplayer = 0
    # Create Game objects and init var
    objGame = ChoosedGame.Game(myDisplay, Game, NuPl, GameOpts, Config, Logs)
    # Dart Stroke Init
    DartStroke = -1
    # Increment the number of Match done
    MatchQty += 1
    # Backup of the Hit for a usage in following round
    Prev_DartStroke = None
    # Used to store Cheats
    magickey = ""
    # Run Handicap
    try:
        Handicap = objGame.CheckHandicap(Players)
    except Exception as e:
        Logs.Log("ERROR","Handicap failed : {}".format(e))

    # Store game properties in local DB
    data = {'gameoptions': ""}
    for opts in GameOpts:
        data['gameoptions'] += str(opts) + "=" + str(GameOpts[opts]) + "|"
    data['gamename'] = Game
    data['nbplayers'] = NuPl
    game_id = Scores.AddGame(data)
    Logs.Log("DEBUG", "Local game id is : {}".format(game_id))

    # Main loop (every input runs a loop - a dart, a button or a click)
    while not MatchDone:

        ##############
        # Step 1 : The player plays
        ##############
        PreDartsChecks = -1
        PostDarts = -1
        EarlyPlayerButton = -1
        MissedDart = -1

        # Display debug every round
        Logs.Log("DEBUG", "###### NEW ROUND #########")
        Logs.Log("DEBUG",
                 "Game Round {}. Round of player {}. Dart {}.".format(actualround, Players[actualplayer].PlayerName,
                                                                      playerlaunch))

        # Pre Play Checks
        if NetStatus == 'YOUARESLAVE':
            try:
                randomval = NetClient.getRandom(actualround, actualplayer, playerlaunch)
                objGame.SetRandom(Players, actualround, actualplayer, playerlaunch, randomval)
            except Exception as e:
                Logs.Log("ERROR", "Problem getting and setting random value from master client : {}".format(e))

        ##############
        # PreDartsChecks - Is a game method that prepare game before each dart
        ##############
        PreDartsChecks = objGame.PreDartsChecks(Players, actualround, actualplayer, playerlaunch)
        ##############

        #
        if NetStatus == 'YOUAREMASTER':
            try:
                randomval = objGame.GetRandom(Players, actualround, actualplayer, playerlaunch)
                NetClient.sendRandom(randomval, actualround, actualplayer, playerlaunch)
            except Exception as e:
                Logs.Log("ERROR", "Problem sending random value to slave clients : {}".format(e))

        # If the player is allowed to play
        if PreDartsChecks != 4 and playerlaunch <= objGame.nbdarts:

            # Every first dart
            if playerlaunch == 1 and len(magickey) == 0:
                myDisplay.InfoMessage([Lang.lang('get-ready')], 2000, None, 'middle', 'big')
                myDisplay.InfoMessage([str(Players[actualplayer].PlayerName) + " : Go ! "], solo, None, 'middle', 'big')
                Inputs.Serial_Flush()  # Flush Serial input values (prevent user to hit while prog sleeps)
                myDisplay.SoundStartRound(
                    str(Players[actualplayer].PlayerName))  # Play sound for first dart (playername otherwise default)

            # Display board
            ClickZones = myDisplay.RefreshGameScreen(Players, actualround, objGame.maxround, objGame.nbdarts - playerlaunch + 1,
                                        objGame.nbdarts, objGame.GameLogo, objGame.Headers, actualplayer)

            # The player plays !
            if NetStatus is None or Players[actualplayer].PlayerName in LoPl:
                # If its a local game or our turn to play in a net game : We read inputs.

                while True:
                    # Backup this DartStroke for next round
                    Prev_DartStroke = DartStroke
                    
                    # If there is cheating in progress
                    if len(magickey) > 0:
                        ktype = ['num','alpha']
                        myDisplay.InfoMessage([str(magickey)], 0, None, 'middle', 'big')
                    else:
                        ktype = []

                    ##### INPUT #######
                    DartStroke = Inputs.ListenInputs(ktype,
                                                     ['PLAYERBUTTON', 'GAMEBUTTON', 'BACKUPBUTTON', 'EXTRABUTTON',
                                                      'TOGGLEFULLSCREEN', 'resize', 'JOKER', 'CHEAT', 'double-click', 'MISSDART',
                                                      'VOLUME-UP', 'VOLUME-DOWN', 'enter','single-click'], [],
                                                     'game')
                    ##### INPUT #######

                    # Check Mouse input first
                    Clicked=myDisplay.IsClicked(ClickZones, DartStroke)
                    if Clicked:
                        DartStroke=Clicked
                    
                    # If at this stage DartStroke is still a tuple, we loop again (clicked on screen) 
                    if isinstance(DartStroke,tuple):
                        Logs.Log("DEBUG", "Stop clicking nowhere !")
                        continue

                    if DartStroke == 'BACKUPBUTTON' and actualplayer==0 and actualround==1 and playerlaunch==1:
                        Logs.Log("WARNING", "Backup Turn is disabled on first round of first player ! Naughty you !")
                        continue

                    # Toggle full-screen
                    if DartStroke == 'TOGGLEFULLSCREEN':
                        myDisplay.CreateScreen(True)
                        ClickZones=myDisplay.RefreshGameScreen(Players, actualround, objGame.maxround,
                                                    objGame.nbdarts - playerlaunch + 1, objGame.nbdarts,
                                                    objGame.GameLogo, objGame.Headers, actualplayer)

                    # Resize screen
                    elif DartStroke == 'resize':
                        myDisplay.CreateScreen(False, Inputs.newresolution)
                        ClickZones=myDisplay.RefreshGameScreen(Players, actualround, objGame.maxround,
                                                    objGame.nbdarts - playerlaunch + 1, objGame.nbdarts,
                                                    objGame.GameLogo, objGame.Headers, actualplayer)

                    # Adjust volume
                    elif DartStroke == 'VOLUME-UP' or DartStroke == 'VOLUME-DOWN':
                        myDisplay.AdjustVolume(DartStroke)

                    # If you hit on keyboard a value, like T20, it is stored in a variable "magickey".
                    # This is great for debugging pyDarts. Or cheating !
                    elif DartStroke in [ 'CHEAT' ]:
                        magickey='MAGIC!'
                    elif magickey=='MAGIC!' and DartStroke in ['S', 'D', 'T', 's', 'd', 't', 'R', 'r']:
                        magickey = str(DartStroke)
                    # Try to override backup button when trying to press a bullseye
                    elif magickey and magickey != 'MAGIC!' and DartStroke == 'BACKUPBUTTON':
                        magickey += 'B'
                    elif magickey and magickey != 'MAGIC!' and DartStroke in ['b','B'] or isinstance(DartStroke, int):
                        magickey += str(DartStroke)
                    # All other situations, break current "While true" (and continue)
                    else:
                        break

                # If magickey is set and you hit enter - it's validated - similar to JOKER but without random
                if DartStroke == 'enter' and len(magickey) > 0:
                    # If you hit R21, it jump directly to round 21, for instance
                    if magickey[:1] in ['r','R']:
                        actualround=int(magickey[1:])
                        Logs.Log("DEBUG", "Jumping to round : {}".format(actualround))
                        magickey = ''
                        continue
                    # Otherwise we keep what you pressed as a valid hit (cheating)
                    DartStroke = magickey.upper()
                    Logs.Log("DEBUG", "Not fair to cheat nasty boy ! Get this : {}".format(DartStroke))
                    magickey = ''

                # Rewrite by a random hit (when pressing 'r' Joker key)
                if DartStroke == 'JOKER':
                    # Transfer ConfigKeys to new list
                    RandList = list(ConfigKeys)
                    # remove buttons from list to prevent missing dart, going back a turn,
                    # skipping a turn or closing game (pop with None arg remove only if exists)
                    if 'playerbutton' in RandList:RandList.remove('playerbutton')
                    if 'gamebutton' in RandList:RandList.remove('gamebutton')
                    if 'backupbutton' in RandList:RandList.remove('backupbutton')
                    if 'extrabutton' in RandList:RandList.remove('extrabutton')
                    # Try to choose random value from ConfigKeys
                    try:
                        DartStroke = random.choice(list(RandList)).upper()
                        Logs.Log("DEBUG", "Looking up for a random hit... Lucky guy ! {}".format(DartStroke))
                    except Exception as e:
                        DartStroke='S20'
                        Logs.Log("WARNING", "Unable to get a random hit. Your board is probably not calibrated ! I give you a {}.".format(DartStroke))
                        Logs.Log("DEBUG", "Looking up for a random hit... Lucky guy ! {}".format(DartStroke))

                # What did we play ?
                Logs.Log("DEBUG", "Input restrained is : {}".format(DartStroke))

                # Send DartStroke to server if player has played
                if NetStatus is not None:
                    NetClient.play(actualround, actualplayer, playerlaunch, DartStroke)

            else:
                # Else its a net game and it's our turn to wait from network !
                Logs.Log("DEBUG","Waiting for remote player (Player {} and Round {})...".format(actualplayer, actualround))
                DartStroke = NetClient.WaitSomeonePlay(actualround, actualplayer, playerlaunch)
                if DartStroke=='FINALPLAYERBUTTON':DartStroke='PLAYERBUTTON'
                
            # INFO : From here the DartStroke should be something included in config file keys, or it loop again.

            # Print error and loop again if key has not been found in config file
            if  not Inputs.SerialBypass and str(DartStroke).upper() not in ConfigKeys and str(DartStroke).lower() not in ConfigKeys:
                Logs.Log("ERROR","Key \"{}\" must exists in your local config file and it has not been found. We recommand you to calibrate your board again.".format(DartStroke))
                Logs.Log("DEBUG", "Jumping back to start of the loop.")
                continue

            # Post Darts Checks
            if (
                   (Inputs.SerialBypass or str(DartStroke).upper() in ConfigKeys or str(DartStroke).lower() in ConfigKeys) 
                   and str(DartStroke) not in ( 'PLAYERBUTTON' , 'BACKUPBUTTON' , 'GAMEBUTTON' , 'EXTRABUTTON', 'MISSDART')
               ):
                #
                # POST DART CHECKS
                #
                # Return codes are :
                #  1 - Jump to next player immediately
                #  2 - Game is over
                #  3 - There is a winner (self.winner must hold winner id)
                #  4 - The player is not allowed to play (jump to next player)
                Logs.Log("DEBUG","Key {} has been found in your config file (or serial bypass). Running PostDartChecks".format(DartStroke))
                try:
                    PostDarts = objGame.PostDartsChecks(DartStroke, Players, actualround, actualplayer, playerlaunch)
                except Exception as e:
                    Logs.Log("ERROR","Error in game PostDartsChecks (we will consider that you missed your dart) : {}".format(e))
                    PostDarts=-1
                    MissedDart=0
                    DartStroke="MISSDART"
                # Display score in differents ways depending on options
                if int(Config.GetValue('SectionGlobals', 'scoreonlogo')) == 1:
                    ClickZones=myDisplay.RefreshGameScreen(Players, actualround, objGame.maxround,
                                                objGame.nbdarts - playerlaunch + 1, objGame.nbdarts, objGame.GameLogo,
                                                objGame.Headers, actualplayer, str(DartStroke), 1000)
                else:
                    myDisplay.InfoMessage([str(DartStroke)], 1000, None, 'middle', 'huge')

            #if ((actualround == 1 and actualplayer > 0) or actualround > 1) and playerlaunch == 1 and len(magickey) == 0 and Prev_DartStroke not in ['BACKUPTURN', 'TOGGLEFULLSCREEN']:
            
            """
            # EARLY PLAYERBUTTON PRESSED
            if DartStroke == 'PLAYERBUTTON' and playerlaunch <= objGame.nbdarts:
                myDisplay.PlaySound('next_player')
                Logs.Log("DEBUG", "You pushed Playerbutton early... Hum !")
                try:
                    EarlyPlayerButton = objGame.EarlyPlayerButton(Players, actualplayer, actualround)
                except Exception as e:
                    Logs.Log("ERROR", "EARLYPLAYERBUTTON is not handled properly by this game. Error was {}".format(e))
            """
            
            # MISSDART BUTTON PRESSED
            if DartStroke == 'MISSDART' and playerlaunch <= objGame.nbdarts:
                Logs.Log("DEBUG", "Missed that dart!")
                myDisplay.InfoMessage([Lang.lang('Missed !')], 1000, None, 'middle', 'big')
                try:
                    MissedDart = objGame.MissButtonPressed(Players, actualplayer, actualround, playerlaunch)
                except Exception as e:
                    Logs.Log("ERROR", "MISSDART is not handled properly by this game. Error was {}".format(e))

            # DISPLAY RELEASE DARTS IF SOLO ENABLED
            if (
                solo
                and (playerlaunch == objGame.nbdarts or (DartStroke == 'PLAYERBUTTON' and playerlaunch < objGame.nbdarts)) 
                and DartStroke!='GAMEBUTTON'
                and DartStroke!='BACKUPBUTTON'
                ):
                myDisplay.InfoMessage([Lang.lang('release-darts')],int(Config.GetValue('SectionGlobals', 'releasedartstime')), None, 'middle', 'big')

            # EARLY PLAYERBUTTON PRESSED
            if DartStroke == 'PLAYERBUTTON' and playerlaunch <= objGame.nbdarts:
                Logs.Log("DEBUG", "You pushed Playerbutton early... Hum !")
                try:
                    EarlyPlayerButton = objGame.EarlyPlayerButton(Players, actualplayer, actualround)
                except Exception as e:
                    Logs.Log("ERROR", "EARLYPLAYERBUTTON is not handled properly by this game. Error was {}".format(e))
                    EarlyPlayerButton=1


            """
            Need a bit of clarification
            """
            # WAIT For Player Button... (MISSDART AND PLAYERBUTTON are voluntarily absent of this list)
            if (
                  (NetStatus is None or Players[actualplayer].PlayerName in LoPl) 
                  and not solo
                  #and DartStroke not in ( 'PLAYERBUTTON' , 'BACKUPBUTTON' , 'GAMEBUTTON' , 'EXTRABUTTON')
                  and DartStroke not in ( 'BACKUPBUTTON' , 'GAMEBUTTON' , 'EXTRABUTTON')
                  and (playerlaunch == objGame.nbdarts or PostDarts == 1 or EarlyPlayerButton==1) 
                  and PostDarts != 2 
                  and PostDarts != 3
               ) :
                ClickZones=myDisplay.RefreshGameScreen(Players, actualround, objGame.maxround, 0, objGame.nbdarts,objGame.GameLogo, objGame.Headers, actualplayer)
                myDisplay.DisplayPressPlayer(Lang.lang('release-darts-and-press-player'))
                # Game context, wait for PLAYERBUTTON only...
                while DartStroke!='PLAYERBUTTON':
                    Logs.Log("DEBUG", "Waiting for player to push PLAYERBUTTON...")
                    DartStroke=Inputs.ListenInputs(['num', 'alpha', 'fx', 'arrows'], ['PLAYERBUTTON','single-click'], [],'game')
                    Clicked=myDisplay.IsClicked(ClickZones,DartStroke)
                    if Clicked:DartStroke=Clicked
                if NetStatus is not None:
                    NetClient.play(actualround, actualplayer, playerlaunch, 'FINALPLAYERBUTTON')

            # OR Wait that the REMOTE player has pushed PLAYERBUTTON (Net game only) (MISSDART AND PLAYERBUTTON are voluntarily absent of this list)
            elif (
                     NetStatus is not None
                     and Players[actualplayer].PlayerName not in LoPl 
                     and not solo
                     #and DartStroke not in ( 'PLAYERBUTTON' , 'BACKUPBUTTON' , 'GAMEBUTTON' , 'EXTRABUTTON', 'MISSDART')
                     and DartStroke not in ( 'BACKUPBUTTON' , 'GAMEBUTTON' , 'EXTRABUTTON' )
                     and (playerlaunch == objGame.nbdarts or PostDarts == 1 or EarlyPlayerButton==1) 
                     and PostDarts != 2 
                     and PostDarts != 3
                  ):
                myDisplay.RefreshGameScreen(Players, actualround, objGame.maxround, 0, objGame.nbdarts,objGame.GameLogo, objGame.Headers, actualplayer)
                myDisplay.DisplayPressPlayer(Lang.lang('press-player-remote'), 'blue')
                # Else its a net game and it's our turn to wait from network !
                Logs.Log("DEBUG", "Waiting for remote player to push the FINALPLAYERBUTTON...")
                # Wait to receive PLAYERBUTTON
                NetClient.WaitSomeonePlay(actualround, actualplayer, playerlaunch,'FINALPLAYERBUTTON')
                # If received, rewrite to PLAYERBUTTON for client
                DartStroke='PLAYERBUTTON'

        # If not allowed to play (PreDartsChecks = 4)
        else:
            # Force BACKUPBUTTON again (double BACKUPTURN) if someone pressed BackupButton and that the previous player is not allowed to play neither
            if Prev_DartStroke == 'BACKUPBUTTON':
                DartStroke = Prev_DartStroke
            # Else, the regular case, go to next player
            else:
                DartStroke = 'PLAYERBUTTON'
        #
        # Step 2 : All the differents possibilities
        #

        # BackUpTurn case - only if a dart as already been played
        if DartStroke == 'BACKUPBUTTON' and (actualplayer>0 or actualround>1 or playerlaunch>1):
            # Go back to correct stage
            if playerlaunch == 1:
                Logs.Log("DEBUG", "Ho Hooooo... Backup Turn !")
                RestoreSession = objGame.PreviousBackUpPlayer
                # If it is first player of first round (prevent jumping to round zero)
                if actualround==0 and actualplayer == 0:
                    actualround = 1
                    actualplayer = 1
                # If it the first player, jump to previous round and last player
                elif actualplayer == 0:
                    actualround = actualround - 1
                    actualplayer = NuPl - 1
                # All other cases are "normal"
                else:
                    actualplayer = actualplayer - 1
            # Restore score of players
            else:
                RestoreSession = objGame.BackUpPlayer
            # Display
            myDisplay.InfoMessage([Lang.lang('Backup Turn !')], 1000, None, 'middle', 'huge')

            # Restore Players' data
            try:
                myDisplay.PlaySound('backup')
                Players = deepcopy(RestoreSession)
                playerlaunch = 0
                Logs.Log("DEBUG", "Backup Turn ! Restoring previous scores.")
            except Exception as e:
                Logs.Log("ERROR", "Backup Turn is not available in this game. : {}".format(e))


        Logs.Log("DEBUG", "At this stage, PostDarts returns {}, EarlyPlayerButton is {}, and MissedDart is {}".format(PostDarts,EarlyPlayerButton,MissedDart))
        Logs.Log("DEBUG", "Memo: 0: nothing special, 1: jump to next player,  2: game over, 3: victory, 4: current player not allowed to play")
        
        # Victory
        if PostDarts == 3 or EarlyPlayerButton == 3 or MissedDart == 3:
            txtwinner = "Winner : {}".format(Players[objGame.winner].PlayerName)
            # Play sound for winner (Playername otherwise default)
            myDisplay.SoundEndGame(Players[objGame.winner].PlayerName)
            myDisplay.InfoMessage([txtwinner], 3000, None, 'middle', 'big')
            # Terminate match
            MatchDone = True
            # If enabled, send game info to pydarts.ch
            if pydartsCh.enabled:
                try:
                    pydartsCh.SaveWinner(Players[objGame.winner].PlayerName, str(actualround), GameOpts)
                except Exception as e:
                    Logs.Log("ERROR", "Unable send winner to pydarts.ch remote database. Error was {}".format(e))

        # Game Over
        if PostDarts == 2 or EarlyPlayerButton == 2 or MissedDart == 2:
            myDisplay.InfoMessage([Lang.lang('last-round-reached')], 3000, None, 'middle')
            myDisplay.PlaySound('grant_me_a_last_game')
            MatchDone = True

        # GAMEBUTTON Pressed
        if DartStroke == 'GAMEBUTTON':
            Logs.Log("DEBUG", "Who has pushed the Game Button ?")
            myDisplay.InfoMessage([Lang.lang('Game interrupted')], 3000, None, 'middle')
            #myDisplay.PlaySound('grant_me_a_last_game')
            MatchDone = True

        # Send to external stats tool pydarts.ch
        if pydartsCh.enabled:
            try:
                DartStroke_Value = objGame.ScoreMap[DartStroke]
                pydartsCh.SaveDart(str(Players[actualplayer].PlayerName),
                                   str(actualround),
                                   str(Players[actualplayer].score),
                                   str(DartStroke_Value),
                                   str(DartStroke),
                                   str(playerlaunch)
                                   )
            except Exception as e:
                Logs.Log("WARNING",
                         "Unable send your hit : '{}' to pydarts.ch remote database. Error was {}".format(DartStroke,e))

        # Next hit, please !
        playerlaunch += 1

        ##### PREPARE NEXT ROUND (in Next loop)
        # Next Player ?
        if not MatchDone and (playerlaunch > objGame.nbdarts or PostDarts == 1 or PostDarts == 4 or DartStroke == 'PLAYERBUTTON'):
            myDisplay.PlaySound('next_player')
            actualplayer += 1
            playerlaunch = 1

        # Next Round ? - Only jump to next round if there is no victory, no match end (give more accurate stats)
        if not MatchDone and actualplayer >= NuPl:
            actualplayer = 0
            actualround += 1


    ###############
    # MATCH IS OVER
    ###############

    # Quit if it was a network game
    Logs.Log("DEBUG", "This game is over")
    if NetStatus is not None:
        NetClient.close_host()

    # Grab stats from the game and write them in local DB
    if bypass_stats == 'True':
        Logs.Log("DEBUG", "You requested to bypass stats update and screen. OK !")
        StatsScreen = 'escape'
    else:
        try:
            Stats = objGame.GameStats(Players, actualround, Scores)
        except Exception as e:
            Logs.Log("ERROR", "Problem building stats with objGame.GameStats method : {}".format(e))

        #  2020 new score table display
        try:
            for scorename in objGame.GameRecords:
                # Get Stats for this game only
                StatsData = Scores.GetScoreTable(scorename, objGame.GameRecords[scorename], True)
                # Display stats for this game
                StatsScreen = myDisplay.DisplayRecords(StatsData, scorename, Scores.gamename, Scores.gameoptions, True)
                # Get Stats for this type of game (with same options)
                StatsData = Scores.GetScoreTable(scorename, objGame.GameRecords[scorename])
                # Display stats for this kind of game
                StatsScreen = myDisplay.DisplayRecords(StatsData, scorename, Scores.gamename, Scores.gameoptions)
        except Exception as e:
            StatsScreen = 'escape'
            Logs.Log("ERROR", "Problem displaying Stats table with screen.DisplayRecords method : {}".format(e))

    # Exiting if it was directplay mode and that the user pressed escape
    if StatsScreen == 'escape' and directplay:
        Logs.Log("DEBUG", "Exiting game because of \"directplay\" mode enabled. Bye !")
        sys.exit(0)
