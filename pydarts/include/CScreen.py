# -*- coding: utf-8 -*-
import os, os.path
from include.ColorSets import *
import pygame
from pygame.locals import *
import sys
from . import CScores
# Randomize player names / and create a random game name / ...
import random
# Run external commands (shell)
import subprocess
# Import pexpect (used for support)
import pexpect
# Make hard calculation
import math
# To get current username
import getpass
# Cross-platform text speech
import pyttsx3
# To seep a bit while dwagent run (support tool)
import time

class CScreen(pygame.Surface):
    #
    # Init
    #
    def __init__(self, Config, Logs, Lang):
        # Init
        self.netgamename = None
        self.servername = None
        self.serveralias = None
        self.serverport = None
        # Store config in local value
        self.Logs = Logs
        self.Lang = Lang  # Import language values
        self.lineheight = None  # Depends of player number - calculated later
        self.Config = Config
        # Image cache (speed up pygame image load process
        self.imagecache = {}
        # For drawing a dart board
        self.LSTOrder = {20: 1, 1: 2, 18: 3, 4: 4, 13: 5, 6: 6, 10: 7, 15: 8, 2: 9, 17: 10, 3: 11, 19: 12, 7: 13,
                         16: 14, 8: 15, 11: 16, 14: 17, 9: 18, 12: 19, 5: 20}
        # Set default Sound Volume (percent)
        try:
            self.SoundVolume = int(self.Config.GetValue('SectionGlobals', 'soundvolume'))
        except:
            self.SoundVolume = 50
        # Initialize pygame
        pygame.init()
        # Initialize pygame mixer
        pygame.mixer.init()
        # Create resolution prameters
        if int(self.Config.GetValue('SectionGlobals', 'fullscreen')) != 1:
            self.fullscreen = False
        else:
            self.fullscreen = True
        # CreateScreen Init or toggle screen
        self.CreateScreen()
        # Choose color set
        self.InitColorSet()
        # Define constants - first without the required nb of players
        self.DefineConstants()
        # Define a boolean value to know if teaming is active (default is inactive)
        self.Teaming = False
        # Init Clickable zone
        self.ClickZones={}
        # Define text-to-speech
        try:
            self.tts=pyttsx3.init()
        except:
            self.Logs.Log("WARNING", "Unable to load cross-plateform text-to-speech pyttsx3 lib.")

    #
    # Give Inputs object to Screen object
    #
    def SetInputs(self, Inputs):
        self.Inputs = Inputs

    #
    # Init player's names
    #
    def InitLoPl(self, localplayers=False):
        LoPl = []
        if localplayers:
            LoPl = localplayers.split(",")
        else:
            try:
                LoPl.append(getpass.getuser())
            except:
                LoPl.append('{}{}'.format(self.Lang.lang('Player'), nbplayers + 1))
        return LoPl

    #
    # Create screen and optionnaly toggle Fullscreen/windowed
    #
    def CreateScreen(self, Toggle=False, newresolution=False):
        # Toggle if requested
        if self.fullscreen and Toggle:
            self.fullscreen = False
        elif Toggle and not self.fullscreen:
            self.fullscreen = True
        # If toggle screen or resize
        if Toggle:
            # Grab information before quitting actual screen
            self.screen = pygame.display.get_surface()  # Get a reference to the currently set display surface
            tmp = self.screen.convert()  # change the pixel format of an image ? Can't remember why I do that ;)
            caption = pygame.display.get_caption()  # Get current caption
            cursor = pygame.mouse.get_cursor()  # Get the image for the system mouse cursor
            bits = self.screen.get_bitsize()  # Get the bit depth of the Surface pixel format
            # Bye bye old screen !
            pygame.display.quit()

        if not pygame.display or Toggle:
            # Welcome new screen !
            pygame.display.init()
        # Define resolution
        self.InitResolution(newresolution)
        # Define screen constants (depends on resolution)
        self.DefineConstants()
        # Tell pygame it is fullscreen if it is
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Set fullscreen with actual resolution
        else:
            self.screen = pygame.display.set_mode((self.res['x'], self.res['y']),
                                                  pygame.RESIZABLE)  # Start windowed with settings
        # If Toggling, blit the new screen
        if Toggle:
            self.screen.blit(tmp, (0, 0))

        # Get caption back
        pygame.display.set_caption('pyDarts v.{}'.format(self.Config.pyDartsVersion))
        # Set pyDarts icon images
        imagefile = self.GetPathOfFile('images', 'icon_white.png')
        if imagefile != False:
            iconimage = pygame.image.load(imagefile)
            pygame.display.set_icon(iconimage)
        else:
            self.Logs.Log("WARNING", "Unable to load icon image.")
        pygame.key.set_mods(0)  # HACK: work-a-round for a SDL bug??
        if Toggle:
            pygame.mouse.set_cursor(*cursor)  # Duoas 16-04-2007

    #
    # Init the choosen ColorSet
    #
    def InitColorSet(self):
        self.FallbackColorSet = 'clear'  # In case of failure to load reuested color set
        self.ChoosenColorSet = self.Config.GetValue('SectionGlobals', 'colorset')
        try:
            self.ColorSet = ColorSet[self.ChoosenColorSet]
        except:
            self.Logs.Log("WARNING", "The colorset \"{}\" does not exists ! Falling back to default ({}) ".format(
                self.Config.GetValue('SectionGlobals', 'colorset'), self.FallbackColorSet))
            self.ColorSet = ColorSet[self.FallbackColorSet]

    #
    # Get best parametered display resolution or best resolution if fullscreen
    #
    def InitResolution(self, newresolution=False):
        """Init a dictionnary named "res" which contains x and y display resolutions"""
        # Used resolution
        self.res = {}
        # Minimal resolution
        self.resmin = {}
        self.resmin['x'] = 200
        self.resmin['y'] = 100
        if newresolution:
            self.res['x'] = int(newresolution[0])
            self.res['y'] = int(newresolution[1])
            self.Logs.Log("DEBUG", "Using display mode : {}x{}".format(self.res['x'], self.res['y']))
        elif self.fullscreen == False:
            self.res['x'] = int(self.Config.GetValue('SectionGlobals', 'resx'))
            self.res['y'] = int(self.Config.GetValue('SectionGlobals', 'resy'))
            self.Logs.Log("DEBUG", "Using display mode : {}x{}".format(self.res['x'], self.res['y']))
        else:
            infoObject = pygame.display.Info()
            self.res['x'] = infoObject.current_w
            self.res['y'] = infoObject.current_h
            self.Logs.Log("DEBUG",
                          "Ho yeah, going fullscreen : {}x{}".format(infoObject.current_w, infoObject.current_h))
        # Exit if resolution smaller than minimal size
        if self.res['x'] < self.resmin['x'] or self.res['y'] < self.resmin['y']:
            self.Logs.Log("WARNING",
                          "Cannot reduce resolution to something smaller than {}x{}, sorry.".format(self.resmin['x'],
                                                                                                    self.resmin['y']))
            self.res['x'] = self.resmin['x']
            self.res['y'] = self.resmin['y']

    ####################### METHODS FOR V1+ DISPLAY ####################

    #
    # Display a rect with transparency, with optionnal border
    #
    def BlitRect(self, X, Y, SX, SY, Color, Border=False, BorderColor=False, Alpha=None):
        if not Color:  # If color is not set, put alpha to 100%
            Color = self.ColorSet['black']  # Arbitrary
            Alpha = 0
        if Alpha == None: Alpha = self.alpha
        if not BorderColor: BorderColor = self.ColorSet['grey']
        s = pygame.Surface((SX, SY))  # the size of your rect
        s.set_alpha(Alpha)  # alpha level
        s.fill(Color)  # this fills the entire surface
        self.screen.blit(s, (X, Y))  # (0,0) are the top-left coordinates
        if Border:
            pygame.draw.rect(self.screen, BorderColor, (X, Y, SX, SY), Border)

    #
    # Return best text size to scale text in a given box size (usefull for responsive design)
    #
    def ScaleTxt(self, txt, boxX, boxY, startingtextsize=None, dafont=None, divider=1, step=0.1):
        if dafont == None: dafont = self.defaultfontpath
        if startingtextsize == None: startingtextsize = boxY
        while True:
            TxtSize = int(startingtextsize / divider)
            font = pygame.font.Font(dafont, TxtSize)
            fontsize = font.size(str(txt))
            # print("PROUT : {} - {} and text size is {} and text is {}".format(boxX,boxY,TxtSize,txt))
            if TxtSize <= 0:
                self.Logs.Log("ERROR","Unable to find suitable text size for a box of size {}x{} and for text {}".format(boxX,boxY,txt))
                return False
            if fontsize[0] < boxX and fontsize[1] < boxY:
                spaceX = int((boxX - fontsize[0]) / 2)
                spaceY = int((boxY - fontsize[1]) / 2)
                # Returns Best text size, horizontal space needed to center text, vertical space to center text
                return [TxtSize, spaceX, spaceY]
            else:
                divider += step

    #
    # All menus use the same header
    #
    def MenuHeader(self, txt, subtxt=None):
        Y = int(self.res['y'] / 30)
        X = 0
        SX = self.res['x']
        SYtxt = int(self.res['y'] / 15)
        if subtxt:
            SYsubtxt = int(self.res['y'] / 25)
        TStxt = int(SYtxt / 2)
        if subtxt:
            TSsubtxt = int(SYsubtxt / 2)
        ScaledTStxt = self.ScaleTxt(txt, self.res['x'] - self.space * 2, SYtxt)
        TStxt = ScaledTStxt[0]
        if subtxt:
            ScaledTSsubtxt = self.ScaleTxt(subtxt, self.res['x'] - self.space * 2, SYsubtxt)
            TSsubtxt = ScaledTSsubtxt[0]
            font = pygame.font.Font(self.defaultfontpath, TSsubtxt)
        fontbig = pygame.font.Font(self.defaultfontpath, TStxt)
        self.BlitRect(X, Y, SX, SYtxt, self.ColorSet['black'])
        if subtxt:
            self.BlitRect(X, Y + SYtxt + self.space * 2, SX, SYsubtxt, self.ColorSet['black'])
            subtext = font.render(subtxt, True, self.ColorSet['white'])
            self.screen.blit(subtext, [X + self.space * 2, Y + SYtxt + ScaledTSsubtxt[
                2] + self.space * 2])  # +int(TStxt*2.5)+int(TSsubtxt/2)
        text = fontbig.render(txt, True, self.ColorSet['white'])
        self.screen.blit(text, [X + self.space * 2, Y + ScaledTStxt[2]])  # +int(TStxt/2.5)

    #
    # Main UI messaging method - can display multiple phrases, mutiple sizes, multiple places
    #
    def InfoMessage(self, txts, wait=None, Color=None, Y=None, BS=None, Enter=False):
        if BS == 'small':
            BS = self.res['y'] / 40
        if BS == None or BS == 'normal':
            BS = self.res['y'] / 20
        if BS == 'big':
            BS = self.res['y'] / 7
        if BS == 'huge':
            BS = self.res['y'] / 4
        if wait == None:
            wait = 3000
        if Color == None:
            Color = self.ColorSet['white']

        # Constants
        SX = self.res['x']
        RectX = 0
        # For each sentence in list
        for txt in txts:
            # Display background
            self.DisplayBackground()
            # Calculate Y
            if Y == None or Y == 'bottom':
                Y = self.res['y'] / 3 * 2
            if Y == 'fullbottom':
                Y = self.res['y'] - (BS / 2)
            if Y == 'top':
                Y = self.res['y'] / 3
            if Y == 'middle':
                Y = self.res['y'] / 2
            # Calculate rect size and place
            RectY = int(Y - (BS / 2))
            # Display Rect
            self.BlitRect(RectX, RectY, SX, BS, self.ColorSet['black'])
            # Determine text size
            ScaledTS = self.ScaleTxt(txt, SX, BS)
            TS = ScaledTS[0]
            # Create font
            font = pygame.font.Font(self.defaultfontpath, int(TS))
            Tx = RectX + ScaledTS[1]
            Ty = RectY + ScaledTS[2]
            # Render text
            txt = font.render(txt, True, self.ColorSet['white'])
            # Blit content
            self.screen.blit(txt, [Tx, Ty])
            # Update screen
            self.UpdateScreen()
            # Optionnaly wait a few sec between each message
            if wait != None:
                pygame.time.wait(wait)  # Wait X millisecond

    #
    # Define if the click is inside the given zone
    #
    def IsClicked(self, Zones=False, click=False):
        # Eventually get Zones for current object if not provided
        if not Zones: Zones=self.ClickZones
        # Exit if we did not receive a click (maybe another input) or if Zones is not set
        if type(click) is not tuple or not Zones:
            return False
        # Try to expand all zones and compare them to click
        #print(Zones)
        try:
            for key in Zones.keys():
                # Avoid getting an exception for integers
                if type(Zones[key]) is not tuple:
                    continue
                # Compare
                if click[0] >= Zones[key][0] and click[0] <= Zones[key][0] + Zones[key][2] and click[1] >= Zones[key][1] and click[1] <= Zones[key][1] + Zones[key][3]:
                    self.Logs.Log("DEBUG","Clicked on {}".format(key))
                    return key
        except Exception as e:
            self.Logs.Log("WARNING","Issue in CScreen.IsClicked method.")
            self.Logs.Log("DEBUG","Issue is {}".format(e))
            return False

    ####################### MENUS ########################

    #
    # Special menu - getting board config
    #
    def GetConfig(self):
        NewKeys = {}
        self.DisplayBackground()  # display basic screen
        i = 0
        total = 66
        self.Inputs.Serial_Flush()
        j = 0
        while True:
            key = self.Config.OrderedDartKeys[j]
            i = 0
            txt = self.Lang.lang('press-on') + " " + str(key)
            self.InfoMessage([txt], 0, None, 'fullbottom', 'big')
            for key2 in self.Config.OrderedDartKeys:
                # Get type
                Type = key2[:1]
                # Define colors
                if i % 2 == 0 and (Type == 'D' or Type == 'T'):
                    partcolor = self.ColorSet['green']
                elif Type == 'D' or Type == 'T':
                    partcolor = self.ColorSet['red']
                else:
                    partcolor = None
                if key2 == key: partcolor = self.ColorSet['yellow']
                # Draw the right thing
                if key2[1:] != 'B' and len(key2) <= 3:
                    Score = int(key2[1:])
                elif key2[1:] == 'B':
                    Score = 'B'
                if Type == 'S' and Score != 'B':
                    self.Drawsimple(self.LSTOrder[Score], partcolor)
                elif Type == 'D' and Score != 'B':
                    self.Drawdouble(self.LSTOrder[Score], partcolor)
                elif Type == 'T' and Score != 'B':
                    self.Drawtriple(self.LSTOrder[Score], partcolor)
                elif Type == 'S' and Score == 'B':
                    self.Drawbull(True, False, partcolor)
                elif Type == 'D' and Score == 'B':
                    self.Drawbull(False, True, partcolor)
                if key2 != 'D5':  # On T20 we switch color order
                    i += 1
                if key2 == key or len(key2) > 3: break  # If key2 is not yet configurer or if it is buttons
            subtxt = self.Lang.lang('press-on-parts') + " - " + self.Lang.lang('left') + " : " + str(total - i)
            self.MenuHeader(self.Lang.lang('board-calibration'), subtxt)
            self.UpdateScreen()
            K = self.Inputs.ListenInputs([], ['escape', 'enter', 'space', 'TOGGLEFULLSCREEN'], [], 'wizard')
            self.Inputs.Serial_Flush()
            if K == 'enter':
                return NewKeys
            elif K == 'space':
                NewKeys[key] = ''
            elif K == 'escape':
                if j > 0:
                    j -= 2
                else:
                    sys.exit(0)
            else:
                NewKeys[key] = K
            i += 1
            j += 1
            # All keys calibrated
            if j == total:
                return NewKeys

    #
    # Display Players engaged in a network game menu
    #
    def Starting(self, NetClient, NetStatus, LoPl, netgamename, Game):
        # Debug
        prev_tick=0
        self.DisplayBackground()  # display basic screen
        # Init empty values
        Rdy = {'REQUEST': None, 'PLAYERSNAMES': None}
        AllPl = []
        # We refresh user list every 5 seconds until the message LAUNCH comes from server
        nexttick = int(pygame.time.get_ticks() / 1000)
        # This loop will ends when the game will be launched
        ClickZones = {}
        while True:
            # Get actual tick from pygame
            tick = int(pygame.time.get_ticks() / 1000)
            # Debug
            if tick!=prev_tick:self.Logs.Log('DEBUG',"Tick:"+str(tick)+" and next refresh (nexttick) when :"+str(nexttick))
            # Listen for keyboard
            K = self.Inputs.KbdAndMouse(['fx', 'arrows'], ['tab', 'enter', 'escape', 'single-click'])

            # Analyse mouse
            Clicked=self.IsClicked(ClickZones, K)
            if Clicked:
                K=Clicked
            # Analyse key
            # If the Master pressed enter
            if (K == 'enter' or K == 'return') and NetStatus == 'YOUAREMASTER':
                self.InfoMessage([self.Lang.lang('Ready to kick ass ?')], 0, None, 'middle', 'big')
                # He is ok to launch the game. Tell it to server
                d = {'REQUEST': 'LAUNCH','GAMENAME': NetClient.gamename}
                NetClient.send(d)  # Send message
            # If the Master player pressed tab
            elif K == 'tab' and NetStatus == 'YOUAREMASTER':
                self.PlaySound('shakeitbaby')
                # Request the server to shuffle player names
                d = {'REQUEST': 'SHUFFLE', 'GAMENAME': NetClient.gamename}
                NetClient.send(d)  # Send message
                # Display refreshing from server
                self.InfoMessage([self.Lang.lang('net-client-randomizing')])
            elif K == 'escape' and NetStatus == 'YOUARESLAVE':
                return -1  # Return -1 means yourself, as a slave client left the game
            elif K == 'escape' and NetStatus == 'YOUAREMASTER':
                return []  # Return -1 means yourself, as a slave client left the game
            SY = int(self.res['y'] / 40)
            Y = int(self.res['y'] / 7)

            # If something goes wrong with tick, beat back nexttick for 5 seconds. For instance, if server take more than 5 seconds to reply.
            if tick > nexttick:
                nexttick=tick+5
            # Refreshing players list                
            elif nexttick == tick:
                self.InfoMessage([self.Lang.lang('net-client-refresh-players')], 0)  # Display refreshing from server
                Rdy = NetClient.SendLocalPlayers(LoPl)  # Send name of local players, and wait for game to be launched
                self.DisplayBackground()  # display basic screen
                nexttick += int(self.Config.GetValue('SectionAdvanced', 'clientpolltime'))
                # Refresh player list if provided by server
                if 'PLAYERSNAMES' in Rdy:
                    AllPl = Rdy['PLAYERSNAMES']
                # Display page title
                if NetStatus == 'YOUAREMASTER':
                    txt = self.Lang.lang('players-ready-masterplayer')
                else:
                    txt = self.Lang.lang('players-ready-slaveplayer')
                txt2 = self.Lang.lang('Game type') + " : " + Game + " - " + self.Lang.lang('Game name') + " : " + netgamename
                self.MenuHeader(txt, txt2)
                Y += SY * 2  # and add a space
                SY = SY * 2
                # Following for loop is for displaying players' names purpose
                X = 0
                SX = self.res['x']
                for P in AllPl:
                    self.BlitRect(X, Y, SX, SY, self.ColorSet['black'], True)
                    # Print text
                    Scaled = self.ScaleTxt(P, SX, SY)
                    font = pygame.font.Font(self.defaultfontpath, Scaled[0])
                    txt = font.render(P, True, self.ColorSet['white'])
                    self.screen.blit(txt, [X + Scaled[1], Y + Scaled[2]])
                    Y += SY
                # Display buttons
                ClickZones['escape'] = self.PreviousMenu()
                if NetStatus == 'YOUAREMASTER': ClickZones['return'] = self.PressEnter(self.Lang.lang("OK"))
                self.UpdateScreen()
                # If we received the order to LAUNCH or to ABORT game
                if Rdy['REQUEST'] == 'LAUNCH' or Rdy['REQUEST'] == 'ABORT':
                    # Return Player list to main game
                    return AllPl
            prev_tick=tick
    #
    # Player Names menu
    #
    def PlayersNamesMenu3(self, AllPl):
        # Init
        edit = {}
        Players = AllPl
        alpha = 'a'
        previous_K = None
        sel = 0
        # This loop breaks when the player press enter
        while True:
            S = int(self.res['y'] / 18)
            # AllBoxesBorders
            BB = 2
            # Fx box
            X = int(self.res['x'] / 15)
            Y = int(self.res['y'] / 9)
            # Fx Text
            TX = int(X + (self.space * 2))
            TY = int(Y)
            # Players name Box
            NX = X + S
            NY = Y
            NS = int(self.res['x'] - X * 2 - S * 3)
            # Player name Text
            TX2 = int(X + S)
            TY2 = int(TY + self.space * 2)
            # Init enabled F keys
            fkeys = []
            # Draw background
            self.DisplayBackground()
            # Draw Text
            self.MenuHeader(self.Lang.lang('players-names'), self.Lang.lang('players-names-subtitle'))
            # Draw each line a player name
            i = 0
            ClickZones = {}
            for Player in Players:
                Y += S
                TY += S
                TY2 += S
                NY += S

                # Define Colors regarding of state (editing or selecting or none)
                if str(i) in edit:
                    bgcolor = self.ColorSet['grey']
                    bordercolor = self.ColorSet['blue']
                elif sel == i:
                    bgcolor = self.ColorSet['green']
                    bordercolor = self.ColorSet['green']
                else:
                    bgcolor = self.ColorSet['blue']
                    bordercolor = self.ColorSet['black']

                # Construct available F keys list
                fkeys.append('f{}'.format(i + 1))

                # First Column : Fx
                pygame.draw.rect(self.screen, bgcolor, (X, Y, S, S), 0)
                pygame.draw.rect(self.screen, self.ColorSet['black'], (X, Y, S, S), BB)

                # Display Fx
                font = pygame.font.Font(self.defaultfontpath, int(S / 1.8))
                textF = font.render("F{}".format(i + 1), True, self.ColorSet['black'])
                self.screen.blit(textF, [TX, TY2])

                # Display player name
                if str(i) in edit:
                    txtPlayerName = "{}_".format(edit[str(i)][:12])
                    Players[i] = edit[str(i)][:12]
                else:
                    txtPlayerName = Players[i]

                pygame.draw.rect(self.screen, bordercolor, (NX, NY, NS, S), BB)  # Square around players' name's border
                self.BlitRect(NX, NY, NS, S, self.ColorSet['black'])  # Square around players' name
                ScaledTS = self.ScaleTxt(txtPlayerName, NS - self.space * 2, S)
                TS = ScaledTS[0]
                font = pygame.font.Font(self.defaultfontpath, TS)
                textEachPlayer = font.render(txtPlayerName, True, self.ColorSet['white'])
                self.screen.blit(textEachPlayer, [TX2 + self.space, TY2 + ScaledTS[2]])
                # Save clickable zone for this player id
                ClickZones['playername|'+str(i)] = (X, Y, NS + S, S)
                # Draw - sign
                # if i>1:
                font = pygame.font.Font(self.defaultfontpath, int(S / 1.8))
                MinusX = X + NS + S
                MinusTX = TX + NS + S
                pygame.draw.rect(self.screen, self.ColorSet['red'], (MinusX, Y, S, S), 0)
                pygame.draw.rect(self.screen, self.ColorSet['black'], (MinusX, Y, S, S), BB)
                textF = font.render("-", True, self.ColorSet['white'])
                self.screen.blit(textF, [MinusTX, TY])
                ClickZones['remove|'+str(i)] = (MinusX, Y, S, S)
                # +
                if len(Players) < 12:
                    font = pygame.font.Font(self.defaultfontpath, int(S / 1.8))
                    PlusX = X + NS + S * 2
                    PlusTX = TX + NS + S * 2
                    pygame.draw.rect(self.screen, self.ColorSet['green'], (PlusX, Y, S, S), 0)
                    pygame.draw.rect(self.screen, self.ColorSet['black'], (PlusX, Y, S, S), BB)
                    textF = font.render("+", True, self.ColorSet['white'])
                    self.screen.blit(textF, [PlusTX, TY])
                    ClickZones['add-after|'+str(i)] = (PlusX, Y, S, S)
                # Increment player id counter
                i += 1
            # Add buttons to first players table
            ClickZones['escape'] = self.PreviousMenu()
            ClickZones['return'] = self.PressEnter(self.Lang.lang("OK"))
            # Refresh screen
            self.UpdateScreen()
            # Read input
            if len(edit) == 0:
                K = self.Inputs.ListenInputs(['alpha', 'num', 'fx', 'math', 'arrows'],
                                             ['PLAYERBUTTON', 'BACKUPBUTTON', 'GAMEBUTTON', 'EXTRABUTTON',
                                              'escape', 'enter', 'backspace', 'tab', 'TOGGLEFULLSCREEN',
                                              'space','single-click'])
            else:
                K = self.Inputs.ListenInputs(['alpha', 'num', 'fx', 'math', 'arrows'],
                                             ['PLAYERBUTTON', 'BACKUPBUTTON', 'GAMEBUTTON','EXTRABUTTON',
                                              'enter', 'backspace','single-click'], context='editing')

            # Compare all Players names zone to clicked zone
            Clicked = self.IsClicked(ClickZones, K)
            if Clicked:
                if "|" in Clicked:
                    splitted = Clicked.split("|")
                    clic=splitted[0]
                    i=int(splitted[1])
                    if clic=='remove' and len(Players) > 1:
                        Players.pop(i)
                    elif clic=="add-after" and len(Players) < 12:
                        Players.insert(i + 1, 'Player' + str(i + 2))
                    elif clic=='playername' and len(edit) == 0:
                        K = "f" + str(i + 1)
                    elif clic=='playername' and len(edit) > 0:
                        K = "enter"
                else:
                    K=Clicked
            # Key analysis
            if K == 'escape':  # Previous menu
                return 'escape'
            # Toggle Fullscreen
            elif (K == 'TOGGLEFULLSCREEN') and len(edit) == 0:
                self.CreateScreen(True)
            # Next Screen !
            elif (K == 'return' or K == 'enter' or K == 'GAMEBUTTON') and len(edit) == 0:
                self.DefineConstants(len(Players))
                return Players
            # Valid and save PlayerName edition
            elif (K == 'return' or K == 'enter' or K == 'GAMEBUTTON') and len(edit) > 0:
                edit = {}
            # Add char to playername string
            elif (K == 'up' or K=='EXTRABUTTON') and len(edit) > 0:
                for curr in edit:
                    if len(edit[curr]) < 12:
                        edit[curr] = "{}a".format(edit[curr])
                        alpha = 'a'
            # Delete a char and/or remove player
            elif (K == 'backspace' or K == 'BACKUPBUTTON' or K == 'left') and len(edit) > 0:
                # Find current player that is in editing mode
                for k in edit:
                    # If there is at least one char, delete it
                    if len(edit[k])>0:
                        edit[k] = edit[k][:-1]
                    # Else remove the player (thanks Zvetix)
                    else:
                        del Players[int(k)]
                        nbplayers = len(Players)
                        edit={}
            # Randomize players
            elif K == 'tab' and len(edit) == 0:  # Randomize Player names
                self.PlaySound('shakeitbaby')
                random.shuffle(Players)
            # Add a player at the end
            elif (K == '+' or K == 'EXTRABUTTON') and len(Players) < 12:
                nbplayers = len(Players)
                Players.append('{}{}'.format(self.Lang.lang('Player'), nbplayers + 1))
            # Remove last player of the list
            elif K == '-' and len(Players) > 1:
                Players.pop()
                nbplayers = len(Players)
            # Enable Edit mode
            elif (K == 'BACKUPBUTTON' and len(edit) == 0):  # With Buttons
                edit = {}
                ident = sel
                edit[str(ident)] = ''
            elif (K == 'right' and len(edit) == 0):  # With Arrows
                edit = {}
                ident = sel
                edit[str(ident)] = ''
            elif K in fkeys:  # With F keys
                edit = {}
                ident = int(K[1:]) - 1
                sel = ident
                edit[str(ident)] = ''
            # Select next player
            elif (K == 'PLAYERBUTTON' or K == 'down' or K=='space') and len(edit) == 0:
                if sel == len(Players) - 1:
                    sel = 0
                else:
                    sel += 1
            # Select previous player
            elif (K == 'up') and len(edit) == 0:
                if sel == 0:
                    sel = len(Players) - 1
                else:
                    sel -= 1
            # Next character - round the alphabet (Playername edition context)
            elif (K == 'PLAYERBUTTON' or K == 'right') and len(
                    edit) > 0:
                if alpha == 'z' or alpha == 'Z':  #  Eventually reset to start of alhabet
                    K = 'a'
                else:  # Or increment char
                    K = chr(ord(alpha) + 1)
                alpha = K  #  Keep it in mind
                for curr in edit:
                    if len(edit[curr]) < 12:
                        edit[curr] = "{}{}".format(edit[curr][:-1], K)
            # Append char to current edition
            elif len(edit) > 0:
                for curr in edit:
                    if len(edit[curr]) < 12:
                        edit[curr] = "{}{}".format(edit[curr], K)
            self.Logs.Log('DEBUG', 'You hit ' + str(K) + ' and previous key was ' + str(previous_K) + '.')
            previous_K = K

    #
    # Choose Game Type : Local - Network
    #
    def GameType(self):
        selected = 1
        while True:
            # MaxSelected depends on conditionnal amount of menus
            if (str(self.Config.GetValue('SectionAdvanced', 'enable-support')) in ('True','1')):
                MaxSel=5 
            else: 
                MaxSel=4

            # Round the selected clock ;)
            if selected > MaxSel:
                selected = 1
            if selected == 0:
                selected = MaxSel

            # Init border width
            BB = 2
            ClickZones = {}

            # Base display
            Y = int(self.res['y'] / 4)
            X = int(self.res['x'] / 15)
            S = int(self.res['y'] / 15)
            line_space = int(S * 1.5)
            space = int(S * 1.5)

            # Game type name box
            NX = X + S
            NY = Y
            NS = int(self.res['x'] - X - NX)

            # Draw bg
            self.DisplayBackground()

            # Titles
            self.MenuHeader(self.Lang.lang('game-type'))

            # First Menu
            # Fonts & text creation
            txt1 = "F1"
            ScaledTS1 = self.ScaleTxt(txt1, S - self.space * 2, S)
            TS1 = ScaledTS1[0]  # Get only first value
            font1 = pygame.font.Font(self.defaultfontpath, TS1)
            txt2 = self.Lang.lang('game-type-local')
            ScaledTS2 = self.ScaleTxt(txt2, NS - self.space * 2, S)
            TS2 = ScaledTS2[0]
            font2 = pygame.font.Font(self.defaultfontpath, TS2)
            # Conditionnal border color
            if selected == 1:
                selectedborder = self.ColorSet['green']
                selectedbg = self.ColorSet['green']
            else:
                selectedborder = self.ColorSet['black']
                selectedbg = self.ColorSet['blue']
            #
            TX = int(X + self.space)
            TY = int(Y + self.space)
            TX2 = int(X + S + self.space)
            TY2 = int(Y + self.space)
            # Fx and menu
            self.BlitRect(X, Y, S, S, selectedbg)
            self.BlitRect(NX, NY, NS, S, self.ColorSet['black'])
            # Borders of each above box
            pygame.draw.rect(self.screen, self.ColorSet['black'], (X, Y, S, S), BB)
            pygame.draw.rect(self.screen, selectedborder, (NX, NY, NS, S), BB)
            # Save Clickable zone
            ClickZones['f1'] = (NX, NY, NS, S)
            #
            textF = font1.render(txt1, True, self.ColorSet['black'])
            self.screen.blit(textF, [TX, TY + ScaledTS1[2]])
            txt2 = font2.render(txt2, True, self.ColorSet['white'])
            self.screen.blit(txt2, [TX2, TY2 + ScaledTS2[2]])

            # Second Menu
            # Conditionnal border color
            if selected == 2:
                selectedborder = self.ColorSet['green']
                selectedbg = self.ColorSet['green']
            else:
                selectedborder = self.ColorSet['black']
                selectedbg = self.ColorSet['blue']
            # Fonts & text creation
            Y += line_space
            NY += line_space
            TY += line_space
            TY2 += line_space
            txt1 = "F2"
            ScaledTS1 = self.ScaleTxt(txt1, S - self.space * 2, S)
            TS1 = ScaledTS1[0]
            font1 = pygame.font.Font(self.defaultfontpath, TS1)
            txt2 = self.Lang.lang('game-type-master')
            ScaledTS2 = self.ScaleTxt(txt2, NS - self.space * 2, S)
            TS2 = ScaledTS2[0]
            font2 = pygame.font.Font(self.defaultfontpath, TS2)
            # Fx box and menu name
            self.BlitRect(X, Y, S, S, selectedbg)
            self.BlitRect(NX, NY, NS, S, self.ColorSet['black'])
            # borders of each above box
            pygame.draw.rect(self.screen, self.ColorSet['black'], (X, Y, S, S), BB)
            pygame.draw.rect(self.screen, selectedborder, (NX, NY, NS, S), BB)
            # Save Clickable zone
            ClickZones['f2'] = (NX, NY, NS, S)
            # text
            textF = font1.render(txt1, True, self.ColorSet['black'])
            self.screen.blit(textF, [TX, TY + ScaledTS1[2]])
            txt2 = font2.render(txt2, True, self.ColorSet['white'])
            self.screen.blit(txt2, [TX2, TY2 + ScaledTS2[2]])

            # Third Menu
            # Conditionnal border color
            if selected == 3:
                selectedborder = self.ColorSet['green']
                selectedbg = self.ColorSet['green']
            else:
                selectedborder = self.ColorSet['black']
                selectedbg = self.ColorSet['blue']
            # Fonts & text creation
            Y += line_space
            NY += line_space
            TY += line_space
            TY2 += line_space
            txt1 = "F3"
            ScaledTS1 = self.ScaleTxt(txt1, S - self.space * 2, S)
            TS1 = ScaledTS1[0]
            font1 = pygame.font.Font(self.defaultfontpath, TS1)
            txt2 = self.Lang.lang('game-type-manual')
            ScaledTS2 = self.ScaleTxt(txt2, NS - self.space * 2, S)
            TS2 = ScaledTS2[0]
            font2 = pygame.font.Font(self.defaultfontpath, TS2)
            # boxes
            self.BlitRect(X, Y, S, S, selectedbg)
            self.BlitRect(NX, NY, NS, S, self.ColorSet['black'])
            # border of above boxes
            pygame.draw.rect(self.screen, self.ColorSet['black'], (X, Y, S, S), BB)
            pygame.draw.rect(self.screen, selectedborder, (NX, NY, NS, S), BB)
            # Save Clickable zone
            ClickZones['f3'] = (NX, NY, NS, S)
            # text
            textF = font1.render(txt1, True, self.ColorSet['black'])
            self.screen.blit(textF, [TX, TY + ScaledTS1[2]])
            txt2 = font2.render(txt2, True, self.ColorSet['white'])
            self.screen.blit(txt2, [TX2, TY2 + ScaledTS2[2]])

            # Fourth Menu - Exit
            # Conditionnal border color
            if selected == 4:
                selectedborder = self.ColorSet['green']
                selectedbg = self.ColorSet['green']
            else:
                selectedborder = self.ColorSet['black']
                selectedbg = self.ColorSet['blue']
            # Fonts & text creation
            Y += line_space
            NY += line_space
            TY += line_space
            TY2 += line_space
            txt1 = "Esc"
            ScaledTS1 = self.ScaleTxt(txt1, S - self.space * 2, S)
            TS1 = ScaledTS1[0]
            font1 = pygame.font.Font(self.defaultfontpath, TS1)
            txt2 = self.Lang.lang('exit')
            ScaledTS2 = self.ScaleTxt(txt2, NS - self.space * 2, S)
            TS2 = ScaledTS2[0]
            font2 = pygame.font.Font(self.defaultfontpath, TS2)
            # boxes
            self.BlitRect(X, Y, S, S, selectedbg)
            self.BlitRect(NX, NY, NS, S, self.ColorSet['black'])
            # border
            pygame.draw.rect(self.screen, self.ColorSet['black'], (X, Y, S, S), BB)
            pygame.draw.rect(self.screen, selectedborder, (NX, NY, NS, S), BB)
            # Save Clickable zone
            ClickZones['escape'] = (NX, NY, NS, S)
            # text
            textF = font1.render(txt1, True, self.ColorSet['black'])
            self.screen.blit(textF, [TX, TY + ScaledTS1[2]])
            txt2 = font2.render(txt2, True, self.ColorSet['white'])
            self.screen.blit(txt2, [TX2, TY2 + ScaledTS2[2]])


            # Fifth conditionnal support tool on main screen
            if (str(self.Config.GetValue('SectionAdvanced', 'enable-support')) in ('True','1')):
                # Conditionnal border color
                if selected == 5:
                    selectedborder = self.ColorSet['green']
                    selectedbg = self.ColorSet['green']
                else:
                    selectedborder = self.ColorSet['black']
                    selectedbg = self.ColorSet['blue']
                # Fonts & text creation
                Y += line_space
                NY += line_space
                TY += line_space
                TY2 += line_space
                txt1 = 'f4'
                ScaledTS1 = self.ScaleTxt(txt1, S - self.space * 2, S)
                TS1 = ScaledTS1[0]
                font1 = pygame.font.Font(self.defaultfontpath, TS1)
                txt2 = self.Lang.lang('Alpha - Launch support tool')
                ScaledTS2 = self.ScaleTxt(txt2, NS - self.space * 2, S)
                TS2 = ScaledTS2[0]
                font2 = pygame.font.Font(self.defaultfontpath, TS2)
                # boxes
                self.BlitRect(X, Y, S, S, selectedbg)
                self.BlitRect(NX, NY, NS, S, self.ColorSet['black'])
                # border
                pygame.draw.rect(self.screen, self.ColorSet['black'], (X, Y, S, S), BB)
                pygame.draw.rect(self.screen, selectedborder, (NX, NY, NS, S), BB)
                # Save Clickable zone
                ClickZones['f4'] = (NX, NY, NS, S)
                # text
                textF = font1.render(txt1, True, self.ColorSet['black'])
                self.screen.blit(textF, [TX, TY + ScaledTS1[2]])
                txt2 = font2.render(txt2, True, self.ColorSet['white'])
                self.screen.blit(txt2, [TX2, TY2 + ScaledTS2[2]])

            ################
            # Update screen
            self.UpdateScreen()
            K = self.Inputs.ListenInputs(['arrows', 'fx', 'alpha', 'math'],
                                         ['escape', 'PLAYERBUTTON', 'BACKUPBUTTON', 'TOGGLEFULLSCREEN', 'GAMEBUTTON',
                                          'single-click', 'double-click', 'resize', 'VOLUME-UP', 'VOLUME-DOWN',
                                          'enter', 'space'])
            # Click cases
            Clicked=self.IsClicked(ClickZones, K)
            if Clicked:
                K = Clicked

            # Keyboard cases
            if K == 'GAMEBUTTON' or K == 'enter':  # First position please, because eventually construct f1, f2 or f3
                K = 'f' + str(selected)
            if K == 'PLAYERBUTTON' or K == 'down' or K=='space':
                selected += 1
            if K == 'up':
                selected -= 1
            if K == 'f1':
                return 'local'
            if K == 'f2':
                return 'netmaster'
            if K == 'f3':
                return 'netmanual'
            if K == 'f4':
                self.Support()
            if K == 'resize':  # Resize screen
                self.CreateScreen(False, self.Inputs.newresolution)
            if K == 'TOGGLEFULLSCREEN':  # Toggle fullscreen
                self.CreateScreen(True, False)
            if K == '+' or K == '-':  # Sound volume
                self.AdjustVolume(K)
            if K == 'escape': #  or K=='BACKUPBUTTON'
                sys.exit(0)

    #
    # Menu to setup Network options
    #
    def NetOptions(self):
        # Max length for fields
        maxlength = {}
        maxlength['netgamename'] = 20
        maxlength['servername'] = 60
        maxlength['serveralias'] = 60
        maxlength['serverport'] = 10
        # Create a random game name ending by this number
        randgamename = random.randint(10000, 99999)
        if self.netgamename == None:
            self.netgamename = str(self.Config.GetValue('SectionAdvanced', 'netgamename')).lower()
            if self.netgamename == 'false': self.netgamename = 'game{}'.format(randgamename)
        if self.servername == None:
            self.servername = str(self.Config.GetValue('SectionAdvanced', 'servername'))
            if self.servername == 'False': self.servername = ''
        if self.serveralias == None:
            self.serveralias = str(self.Config.GetValue('SectionAdvanced', 'serveralias'))
            if self.serveralias == 'False': self.serveralias = ''
        if self.serverport == None:
            self.serverport = str(self.Config.GetValue('SectionAdvanced', 'serverport'))
            if self.serverport == 'False': self.serverport = ''
        edit = {}
        while True:
            ClickZones = {}
            # Constants
            BB = 2  # Border
            Y = int(self.res['y'] / 4)
            X = int(self.res['x'] / 15)
            S = int(self.res['y'] / 22)  # Basic size unit
            space = int(S * 3)
            NX = X + S
            NY = Y
            BoxX = self.res['x'] - 2 * X - 2 * S  # Size of the option box
            # Background display
            self.DisplayBackground()

            # Display Title
            self.MenuHeader(self.Lang.lang('net-options'))

            # First Option : Game name
            if 'netgamename' in edit:
                boxcolor = self.ColorSet['red']  # Change color of Fx box if editing in progress
            else:
                boxcolor = self.ColorSet['blue']  # Else standard color
            self.BlitRect(X, Y - S, BoxX, S, self.ColorSet['white'])  # Item title box
            self.BlitRect(X, Y, S, S, boxcolor, BB, self.ColorSet['black'])  # Fx Box
            self.BlitRect(NX, NY, BoxX, S, self.ColorSet['black'], BB, self.ColorSet['white'])  # Value box
            ClickZones['f1'] = (X, Y, BoxX + S + BoxX, S)

            ScaledFSFx = self.ScaleTxt("F1", S, S)
            font = pygame.font.Font(self.defaultfontpath, ScaledFSFx[0])
            textF = font.render("F1", True, self.ColorSet['black'])

            ScaledFS = self.ScaleTxt(self.Lang.lang('net-options-netgamename'), BoxX, S)
            font = pygame.font.Font(self.defaultfontpath, ScaledFS[0])
            textE = font.render(self.Lang.lang('net-options-netgamename'), True, self.ColorSet['black'])

            self.screen.blit(textF, [X + ScaledFSFx[1], Y + ScaledFSFx[2]])
            self.screen.blit(textE, [X + self.space, Y - S - BB + ScaledFS[2]])

            if 'netgamename' in edit:
                self.netgamename = edit['netgamename']
                txt = "{}_".format(self.netgamename.lower())
            else:
                txt = self.netgamename.lower()
            ScaledT = self.ScaleTxt(txt, BoxX, S)
            font = pygame.font.Font(self.defaultfontpath, ScaledT[0])
            txt = font.render(txt, True, self.ColorSet['white'])
            self.screen.blit(txt, [X + S + self.space * 2, Y + ScaledT[2] + self.space])

            # Second Option : Server name
            if 'servername' in edit:
                boxcolor = self.ColorSet['red']
            else:
                boxcolor = self.ColorSet['blue']
            self.BlitRect(X, Y - S + space, BoxX, S, self.ColorSet['white'])  # Item title box
            self.BlitRect(X, Y + space, S, S, boxcolor, BB, self.ColorSet['black'])  # Fx Box
            self.BlitRect(NX, NY + space, BoxX, S, self.ColorSet['black'], BB, self.ColorSet['white'])  # Value box
            ClickZones['f2'] = (X, Y + space, BoxX + S + BoxX, S)

            ScaledFSFx = self.ScaleTxt("F2", S, S)
            font = pygame.font.Font(self.defaultfontpath, ScaledFSFx[0])
            textF = font.render("F2", True, self.ColorSet['black'])

            ScaledFS = self.ScaleTxt(self.Lang.lang('net-options-servername'), BoxX, S)
            font = pygame.font.Font(self.defaultfontpath, ScaledFS[0])
            textE = font.render(self.Lang.lang('net-options-servername'), True, self.ColorSet['black'])

            self.screen.blit(textF, [X + ScaledFSFx[1], Y + ScaledFSFx[2] + space])
            self.screen.blit(textE, [X + self.space, Y - S - BB + ScaledFS[2] + space])

            if 'servername' in edit:
                self.servername = edit['servername']
                txt = "{}_".format(self.servername)
            else:
                txt = self.servername

            ScaledT = self.ScaleTxt(txt, BoxX, S)
            font = pygame.font.Font(self.defaultfontpath, ScaledT[0])
            txt = font.render(txt, True, self.ColorSet['white'])
            self.screen.blit(txt, [X + S + self.space * 2, Y + ScaledT[2] + self.space + space])

            # Third Option : Server Alias
            if 'serveralias' in edit:
                boxcolor = self.ColorSet['red']
            else:
                boxcolor = self.ColorSet['blue']
            self.BlitRect(X, Y - S + space * 2, BoxX, S, self.ColorSet['white'])  # Item title box
            self.BlitRect(X, Y + space * 2, S, S, boxcolor, BB, self.ColorSet['black'])  # Fx Box
            self.BlitRect(NX, NY + space * 2, BoxX, S, self.ColorSet['black'], BB, self.ColorSet['white'])  # Value box
            ClickZones['f3'] = (X, Y + space * 2, BoxX + S + BoxX, S)

            ScaledFSFx = self.ScaleTxt("F3", S, S)
            font = pygame.font.Font(self.defaultfontpath, ScaledFSFx[0])
            textF = font.render("F3", True, self.ColorSet['black'])

            ScaledFS = self.ScaleTxt(self.Lang.lang('net-options-serveralias'), BoxX, S)
            font = pygame.font.Font(self.defaultfontpath, ScaledFS[0])
            textE = font.render(self.Lang.lang('net-options-serveralias'), True, self.ColorSet['black'])

            self.screen.blit(textF, [X + ScaledFSFx[1], Y + ScaledFSFx[2] + space * 2])
            self.screen.blit(textE, [X + self.space, Y - S - BB + ScaledFS[2] + space * 2])

            if 'serveralias' in edit:
                self.serveralias = edit['serveralias']
                txt = "{}_".format(self.serveralias)
            else:
                txt = self.serveralias
            ScaledT = self.ScaleTxt(txt, BoxX, S)
            font = pygame.font.Font(self.defaultfontpath, ScaledT[0])
            txt = font.render(txt, True, self.ColorSet['white'])
            self.screen.blit(txt, [X + S + self.space * 2, Y + ScaledT[2] + self.space + space * 2])

            # Fourth Option : Server port
            if 'serverport' in edit:
                boxcolor = self.ColorSet['red']
            else:
                boxcolor = self.ColorSet['blue']
            self.BlitRect(X, Y - S + space * 3, BoxX, S, self.ColorSet['white'])  # Item title box
            self.BlitRect(X, Y + space * 3, S, S, boxcolor, BB, self.ColorSet['black'])  # Fx Box
            self.BlitRect(NX, NY + space * 3, BoxX, S, self.ColorSet['black'], BB, self.ColorSet['white'])  # Value box
            ClickZones['f4'] = (X, Y + space * 3, BoxX + S + BoxX, S)

            ScaledFSFx = self.ScaleTxt("F4", S, S)
            font = pygame.font.Font(self.defaultfontpath, ScaledFSFx[0])
            textF = font.render("F4", True, self.ColorSet['black'])

            ScaledFS = self.ScaleTxt(self.Lang.lang('net-options-serverport'), BoxX, S)
            font = pygame.font.Font(self.defaultfontpath, ScaledFS[0])
            textE = font.render(self.Lang.lang('net-options-serverport'), True, self.ColorSet['black'])

            self.screen.blit(textF, [X + ScaledFSFx[1], Y + ScaledFSFx[2] + space * 3])
            self.screen.blit(textE, [X + self.space, Y - S - BB + ScaledFS[2] + space * 3])

            if 'serverport' in edit:
                self.serverport = edit['serverport']
                txt = "{}_".format(self.serverport)
            else:
                txt = self.serverport

            ScaledT = self.ScaleTxt(txt, BoxX, S)
            font = pygame.font.Font(self.defaultfontpath, ScaledT[0])
            txt = font.render(txt, True, self.ColorSet['white'])
            self.screen.blit(txt, [X + S + self.space * 2, Y + ScaledT[2] + self.space + space * 3])

            # Menu navigation
            ClickZones['escape'] = self.PreviousMenu()
            ClickZones['enter'] = self.PressEnter(self.Lang.lang('Next'))
            self.UpdateScreen()

            ### Listen
            if edit and len(edit) > 0:
                K = self.Inputs.ListenInputs(['fx', 'alpha', 'num', 'math', 'arrows'],
                                             ['enter', 'backspace', 'single-click'], context='editing')
            else:
                K = self.Inputs.ListenInputs(['fx', 'alpha', 'num', 'math', 'arrows'],
                                             ['backspace', 'enter', 'escape', 'TOGGLEFULLSCREEN', 'single-click'])
            ### Analysys
            # Mouse
            #print("Click Zones : {}".format(ClickZones))
            Clicked=self.IsClicked(ClickZones,K)
            if Clicked:
                K=Clicked
            """
            try:
                if self.IsClicked(ClickZones['enter'], K):
                    K = 'enter'
                elif self.IsClicked(ClickZones['escape'], K):
                    K = 'escape'
                elif self.IsClicked(ClickZones['f1'], K):
                    if len(edit) > 0:
                        K = 'enter'
                    else:
                        K = 'f1'
                elif self.IsClicked(ClickZones['f2'], K):
                    if len(edit) > 0:
                        K = 'enter'
                    else:
                        K = 'f2'
                elif self.IsClicked(ClickZones['f3'], K):
                    if len(edit) > 0:
                        K = 'enter'
                    else:
                        K = 'f3'
                elif self.IsClicked(ClickZones['f4'], K):
                    if len(edit) > 0:
                        K = 'enter'
                    else:
                        K = 'f4'
            except Exception as e:
                print("Error {}".format(e))
            """
            if K == 'f1' and len(edit)==0:
                edit = {}
                edit['netgamename'] = ''
            elif (K == 'TOGGLEFULLSCREEN') and len(edit) == 0:  # Toggle fullscreen
                self.CreateScreen(True)
            elif K == 'f2' and len(edit)==0:
                edit = {}
                edit['servername'] = ''
            elif K == 'f3' and len(edit)==0:
                edit = {}
                edit['serveralias'] = ''
            elif K == 'f4' and len(edit)==0:
                edit = {}
                edit['serverport'] = ''
            elif (K == 'enter' or K == 'return') and len(edit) == 0:
                NetOptions = {}
                NetOptions['GAMENAME'] = self.netgamename
                NetOptions['SERVERIP'] = self.servername
                NetOptions['SERVERALIAS'] = self.serveralias
                NetOptions['SERVERPORT'] = self.serverport
                return NetOptions
            elif K in ('f1','f2','f3','f4') and len(edit) > 0:
                edit = {}
            elif (K == 'enter' or K == 'return') and len(edit) > 0:
                edit = {}
            elif K == 'backspace' and len(edit) > 0:
                for e in edit:
                    edit[e] = edit[e][:-1]
            elif len(edit) > 0 and len(str(K)) == 1:  # If the user hit a standard char
                for e in edit:  # Update value in the temp storage disct (MUST be only one value)
                    if len(edit[e]) < maxlength[e]:  # Disallow typing more that the maxlength number of chars
                        edit[e] = "{}{}".format(edit[e], K)
            elif K == 'escape':
                return K

    #
    # Display Arrows to show the player that he can navigate in the menu
    #
    def PressEnter(self, txt, X=None, Y=None, SX=None, SY=None, Update=False, imagename='key_enter.png'):
        BS = int(self.res['y'] / 15)
        if SX == None: SX = int(self.res['x'] / 7)
        if SY == None: SY = int(self.res['y'] / 15)
        if X == None: X = int(self.res['x'] - int(self.res['x'] / 15) - SX)
        if Y == None: Y = int(self.res['y'] - self.res['y'] / 10)  # Same as PreviousMenu
        ImgSX = int(SY / 2.5)
        # ImgSY = ImgSX

        # Do not display text if screen is small
        # if self.screen_proportions < self.prop_limit:
        # txt=False
        # ImgSX = int(SY*0.8)
        # ImgSY = ImgSX

        # Container
        BB = 2
        self.BlitRect(X, Y, SX, SY, self.ColorSet['black'])
        imagefile = self.GetPathOfFile('images', imagename)
        # Print text
        if self.screen_proportions >= self.prop_limit:
            Scaled = self.ScaleTxt(txt, SX - ImgSX - self.space * 2, SY)
            font = pygame.font.Font(self.defaultfontpath, Scaled[0])
            text = font.render(txt, True, self.ColorSet['white'])
            self.screen.blit(text, [X + Scaled[1] + ImgSX + self.space * 2, Y + Scaled[2]])
            self.DisplayImage(imagefile, X + self.space, Y + self.space, ImgSX, SY - self.space * 2, False, False, True)
        else:
            # Print
            self.DisplayImage(imagefile, X + self.space, Y + self.space, SX - self.space * 2, SY - self.space * 2,False, True, True)
        return (X, Y, SX, SY)

    # Previous
    def PreviousMenu(self, X=None, Y=None, S=None, Update=False):
        if X == None: X = int(self.res['x'] / 15)
        if Y == None: Y = int(self.res['y'] - self.res['y'] / 10)
        if S == None: S = int(self.res['y'] / 15)
        BB = 2
        TX = int(X + S / 6)
        TY = int(Y + S / 6)
        TS = int(S / 2)
        font = pygame.font.Font(self.defaultfontpath, TS)
        pygame.draw.rect(self.screen, self.ColorSet['black'], (X, Y, S, S), BB)
        self.BlitRect(X, Y, S, S, self.ColorSet['black'])
        text = font.render("Esc", True, self.ColorSet['white'])
        self.screen.blit(text, [TX, TY])
        if Update: self.UpdateScreen()
        return (X, Y, S, S)

    # Left
    def LeftArrow(self, X=None, Y=None, S=None, Update=False):
        if Y == None: Y = int(self.res['y'] - self.res['y'] / 10)
        if X == None: X = int(self.res['x'] / 15)
        if S == None: S = int(self.res['y'] / 15)
        BB = 2
        TX = int(X + S / 3)
        TY = int(Y + S / 6)
        TS = int(S / 2)
        font = pygame.font.Font(self.defaultfontpath, TS)
        pygame.draw.rect(self.screen, self.ColorSet['black'], (X, Y, S, S), BB)
        self.BlitRect(X, Y, S, S, self.ColorSet['black'])
        text = font.render("<", True, self.ColorSet['white'])
        self.screen.blit(text, [TX, TY])
        if Update: self.UpdateScreen()
        return (X, Y, S, S)

    # Down
    def DownArrow(self, X=None, Y=None, SX=None, SY=False, Update=False):
        if SX == None: SX = int(self.res['y'] / 15)
        if SY == False: SY = SX
        if Y == None: Y = int(self.res['y'] - S)
        if X == None: X = int(self.res['x'] - S)
        BB = 2
        TX = int(X + SX / 3)
        TY = int(Y + SY / 6)
        TS = int(SX / 2)
        font = pygame.font.Font(self.defaultfontpath, TS)
        pygame.draw.rect(self.screen, self.ColorSet['black'], (X, Y, SX, SY), BB)
        self.BlitRect(X, Y, SX, SY, self.ColorSet['black'])
        text = font.render("v", True, self.ColorSet['white'])
        self.screen.blit(text, [TX, TY])
        if Update: self.UpdateScreen()
        return (X, Y, SX, SY)

    # Up
    def UpArrow(self, X=None, Y=None, SX=None, SY=False, Update=False):
        if SX == None: SX = int(self.res['y'] / 15)
        if SY == False: SY = SX
        if Y == None: Y = S
        if X == None: X = int(self.res['x'] - SX)
        BB = 2
        TX = int(X + SX / 3)
        TY = int(Y + SY / 6)
        TS = int(SX / 2)
        font = pygame.font.Font(self.defaultfontpath, TS)
        pygame.draw.rect(self.screen, self.ColorSet['black'], (X, Y, SX, SY), BB)
        self.BlitRect(X, Y, SX, SY, self.ColorSet['black'])
        text = font.render("^", True, self.ColorSet['white'])
        self.screen.blit(text, [TX, TY])
        if Update: self.UpdateScreen()
        return (X, Y, SX, SY)

    #
    # Get Game List from local game folder
    #
    def GetGameList(self):
        text = []
        GameFilename = {}
        fileiter = (os.path.join(root, f)
                    for root, _, files in os.walk('games')
                    for f in files)
        menu_data = [self.Lang.lang('game-list')]
        Games = []
        for foundfiles in fileiter:
            fileName, fileExtension = os.path.splitext(foundfiles)
            if fileExtension == '.py' and os.path.basename(fileName) != '__init__':
                Games.append(os.path.basename(fileName))
                GameFilename[fileName] = os.path.basename(fileName)
                menu_data.append(os.path.basename(fileName))
        # If Games list is empty, simulate it
        if len(Games) == 0:
            if self.Config.GetValue('SectionAdvanced','games')=='all':
                Games = self.Config.allgames
            else:
                Games = self.Config.officialgames
        # Display all games names
        txtgames = "/".join(menu_data[1:])
        self.Logs.Log("DEBUG", "Found these games : {}".format(txtgames))
        return Games

        #

    # Get Game description (from language file)
    #
    def GetDesc(self, Game):
        Desc = []
        try:
            Desc = self.Lang.lang('Description-{}'.format(Game))
        except:
            Desc.append(self.Lang.lang('game-no-desc'))
            self.Logs.Log("WARNING", "Unable to get a description for game {}".format(Game))
        return Desc

    #
    # Menu which display a table to choose the game
    #
    def GameList(self, Games):
        self.Logs.Log("DEBUG", "Waiting for game choice")
        sel = 0
        i = -1
        while True:
            # Round the clock of menu
            if sel > len(Games) - 1:
                sel = 0
            elif sel < 0:
                sel = len(Games) - 1
            # Init Clickable zone
            ClickZones = {}
            i += 1
            BB = 2

            # Base size of a game cel
            Y = int(self.res['y'] / 6)
            X = int(self.res['x'] / 15)
            W = int(self.res['x'] / 2.5)
            H = int(self.res['y'] / (len(Games) * 1.5))

            # Base size for Up and down arrow
            if (self.screen_proportions >= self.prop_limit):
                AX = int(X / 2)
                AW = int(X / 2)
            else:
                AX = 0
                AW = X
            AY = Y
            AH = int(H)

            # Get Game description of selected game
            Desc = self.GetDesc(Games[sel])

            # Detail box
            GX = int(self.res['x'] / 2.1)
            GY = Y
            GW = int(self.res['x'] / 2.1)
            GH = H * len(Games)
            Gspace = int(GW / 20)

            # Game Image size, relative to box container
            iW = int(GW - self.space * 2)
            iH = int(H * len(Games) / 3.5)

            # Game desc X and Y
            dX = GX + Gspace
            dY = GY + iH + Gspace + self.space

            # Draw background
            self.DisplayBackground()

            # Screen Titles
            self.MenuHeader(self.Lang.lang('game-list'))
            j = -1
            for G in Games:
                j += 1
                # First game, display arrow beside game name
                if j == 0:
                    ClickZones['up'] = self.UpArrow(AX, AY, AW, AH)
                if j == sel:
                    pygame.draw.rect(self.screen, self.ColorSet['grey'], (X, Y, W, H), 0)
                else:
                    self.BlitRect(X, Y, W, H, self.ColorSet['black'])
                # Display border
                pygame.draw.rect(self.screen, self.ColorSet['black'], (X, Y, W, H), BB)
                # Display game name
                ScaledGameName = self.ScaleTxt(G, W, H)
                font = pygame.font.Font(self.defaultfontpath, ScaledGameName[0])
                text = font.render(G, True, self.ColorSet['white'])
                self.screen.blit(text, [X + ScaledGameName[1], Y + ScaledGameName[2]])
                # Save clickable zone
                ClickZones["select|"+str(j)] = (X, Y, W, H)
                # Increment
                AY = Y  # Increment Arrow Y
                Y += H
            # Beside of last game name, print down arrow
            ClickZones['down'] = self.DownArrow(AX, AY, AW, AH)
            # Display detail box
            self.BlitRect(GX, GY, GW, GH, self.ColorSet['black'])
            # Display image (responsive)
            if (self.screen_proportions >= self.prop_limit):
                self.DisplayImage(self.GetPathOfFile('images', Games[sel] + ".png"), GX + self.space, GY + self.space,
                                  iW, iH, Scale=False, CenterX=True, CenterY=True)
            else:
                self.DisplayImage(self.GetPathOfFile('images', Games[sel] + ".png"), GX + self.space, GY + self.space,
                                  GW - self.space * 2, GH - self.space * 2, Scale=False, CenterX=True, CenterY=True)
            # Print game description, only if screen proportions allow it (width >= height)
            if self.screen_proportions >= self.prop_limit:
                idesc = 0
                # Get longest string of list
                Desc = Desc.splitlines()
                longestid = 0
                maxsize = 0
                i = 0
                for line in Desc:
                    font = pygame.font.Font(self.defaultfontpath, 50)  # Compare all string rendered
                    fontsize = font.size(line)
                    if fontsize[0] > maxsize:
                        maxsize = fontsize[0]
                        longestid = i
                    i += 1
                Scaled = self.ScaleTxt(Desc[longestid], GW - Gspace * 2, GH - iH)
                FS = min(Scaled[0], int(GW / 20))
                for line in Desc:
                    font = pygame.font.Font(self.defaultfontpath, FS)
                    text = font.render(line, True, self.ColorSet['white'])
                    self.screen.blit(text, [dX, dY + Gspace + Gspace * idesc])
                    idesc += 1
            # Arrow to go back and next
            ClickZones['escape'] = self.PreviousMenu()
            ClickZones['return'] = self.PressEnter(self.Lang.lang("OK"))

            # Update screen
            self.UpdateScreen()
            K = self.Inputs.ListenInputs(['arrows', 'alpha'],
                                         ['escape', 'enter', 'space', 'single-click',
                                          'PLAYERBUTTON','GAMEBUTTON','BACKUPBUTTON',
                                          'TOGGLEFULLSCREEN'])  # ToogleFullScreen Disabled because of arrows
            # Click cases
            #print("Zones are :"+str(ClickZones))
            Clicked=self.IsClicked(ClickZones, K)
            if Clicked:
                if "select|" in Clicked:
                    splitted=Clicked.split("|")
                    sel=int(splitted[1])
                    K=='enter'
                else:
                    K=Clicked
            """
            try:
                for key, GZone in ClickZone.items():
                    if self.IsClicked(GZone, K):
                        if key == 'escape':
                            return 'escape'
                        elif key == 'up' or key == 'down':
                            K = key
                        else:
                            sel = key
                            K = 'return'
            except Exception as e:
                print(e)
            """
            # Keyboard cases
            if K == 'return' or K == 'enter' or K == 'GAMEBUTTON':
                self.selectedgame = Games[sel]
                return self.selectedgame
            elif K == 'TOGGLEFULLSCREEN':  # Toggle fullscreen
                self.CreateScreen(True)
            elif K == 'down' or K == 'PLAYERBUTTON' or K=='space':
                sel += 1
            elif K == 'up':
                sel -= 1
            elif K == 'escape' or K=='BACKUPBUTTON':
                return 'escape'

    #
    # Menu which display a table to choose server (MasterServer Client)
    #
    def ServerList(self, NetMasterClient, NuPl):
        self.Inputs.shift = False  # Reinit Kbd Shift status
        # Display "Pending connexion..."
        self.DisplayBackground()
        self.InfoMessage([self.Lang.lang('master-client-connecting')], 1000)
        masterclientpolltime = int(self.Config.GetValue('SectionAdvanced', 'masterclientpolltime'))
        nexttick = int(pygame.time.get_ticks() / 1000) + masterclientpolltime
        minpolltime = 10
        while True:
            ClickZones = {}
            try:
                NetMasterClient.connect_master(self.Config.GetValue('SectionGlobals', 'masterserver'),
                                               int(self.Config.GetValue('SectionGlobals', 'masterport')))
            except:
                self.Logs.Log("ERROR", "Unable to reach Master Server : {} on port : {}".format(
                    self.Config.GetValue('SectionGlobals', 'masterserver'),
                    int(self.Config.GetValue('SectionGlobals', 'masterport'))))
                self.DisplayBackground()
                self.InfoMessage([self.Lang.lang('master-client-no-connection')])
                return 'escape'  # Tels master loop to turn back to previous menu
            List = NetMasterClient.wait_list(NuPl)  # get and clean server list
            NetMasterClient.close_cx()
            selected = 0
            # If list is empty (exactly zero result - Syntax "is" allow to differenciate Zero and False)
            if List == 0:
                # Loop and refresh periodically
                self.InfoMessage([self.Lang.lang('master-client-empty')], 2000)
                while True:
                    tick = int(pygame.time.get_ticks() / 1000)
                    if masterclientpolltime > minpolltime:
                        sec = str(nexttick - tick)
                        msg_str = self.Lang.lang('Autorefresh in %sec seconds') % {'sec': sec}
                        msg = u"{} - {}".format(self.Lang.lang('master-client-refresh'), msg_str)
                    else:
                        msg = self.Lang.lang('master-client-refresh')
                    self.InfoMessage([msg], 0, 'small', 'bottom')
                    # Arrow to go back and to refresh
                    #ClickZones['space'] = self.PressEnter(self.Lang.lang('Refresh'))
                    ClickZones['escape'] = self.PreviousMenu()
                    ClickZones['space'] = self.PressEnter(self.Lang.lang("Refresh"),None,None,None,None,False,'refresh.png')
                    self.UpdateScreen()
                    # Listen to inputs (non blocking)
                    K = self.Inputs.KbdAndMouse(['arrows', 'alpha'],
                                                ['escape', 'space', 'TOGGLEFULLSCREEN', 'single-click'])
                    # Mouse cases
                    Clicked=self.IsClicked(ClickZones, K)
                    if Clicked:
                        K=Clicked
                    # Keyboard cases
                    if K == 'TOGGLEFULLSCREEN':  # Toggle fullscreen
                        self.CreateScreen(True)
                    elif K == 'escape':
                        return K
                    elif K == 'space':
                        nexttick = int(pygame.time.get_ticks() / 1000) + masterclientpolltime
                        break
                    # Auto refresh (Only refresh if poll-time is above 10 sec)
                    if tick == nexttick and masterclientpolltime > minpolltime:
                        nexttick += masterclientpolltime
                        break
                    pygame.time.wait(500)  # A few ms to reduce cpu...
            # In case of network error (timeout for exemple)
            elif List is False:
                # Tell the user there is a network error
                msg = self.Lang.lang('network-error')
                # Display error msg
                self.InfoMessage([msg], 1000)
                # Simulate an escape key (back to menu)
                return 'escape'
            # In case of a list containing something
            else:
                self.Logs.Log("DEBUG", "Received a list with {} games".format(len(List)))
                displaymax = 10  # How many lines to display
                maxsel = min(len(List), displaymax)
                showst = 0
                showend = maxsel
                ListLength = len(List)
                while True:
                    ClickZones = {}
                    # Set the width of each column depending on screen width
                    if self.screen_proportions < 1:
                        colfactor = {'ID': 0, 'STATUS': 0, 'PLAYERS': 3, 'GAMENAME': 8, 'SERVERIP': 0, 'SERVERPORT': 0,
                                     'GAMECREATOR': 0, 'GAMETYPE': 0}
                    else:
                        colfactor = {'ID': 0, 'STATUS': 2, 'PLAYERS': 2, 'GAMENAME': 3, 'SERVERIP': 2, 'SERVERPORT': 2,
                                     'GAMECREATOR': 2, 'GAMETYPE': 2}
                    # Some basics
                    x = int(self.res['x'] / 17)
                    y = int(self.res['y'] / 17)
                    # Display basis
                    self.DisplayBackground()
                    self.MenuHeader(self.Lang.lang('master-client-title'), self.Lang.lang('master-client-refresh'))
                    # Init
                    celsizex = x
                    i = -1
                    # Cel position
                    posx = 0
                    posy = y * i + (4 * y)
                    # Draw table header
                    for Opt, Val in List[0].items():
                        try:
                            txt = self.Lang.lang("serverlist-header-{}".format(Opt))
                        except:
                            self.Logs.Log("WARNING", "No translation for table header {}".format(Opt))
                            txt = str(Opt)
                        posx += celsizex
                        # Get a width only if column is referenced in colfactor (backward compat purpose)
                        if Opt in colfactor:
                            celsizex = x * colfactor[Opt]
                        else:
                            celsizex = 0
                        # On a small screen , display only GAMENAME
                        if self.screen_proportions > 1 or Opt == "GAMENAME" or Opt == "PLAYERS":
                            self.BlitRect(posx, posy, celsizex, y, self.ColorSet['white'])
                            Scaled = self.ScaleTxt(txt, celsizex, y)
                            font = pygame.font.Font(self.defaultfontpath, Scaled[0])
                            textF = font.render(txt, True, self.ColorSet['black'])
                            self.screen.blit(textF, [posx + Scaled[1], posy + Scaled[2]])
                    # Optionnaly display UP arrow
                    if showst > 0:
                        ClickZones['up'] = self.UpArrow(posx + celsizex, posy + y, y)

                    # For each line of the table
                    i += 1

                    for Value in List[showst:showend]:
                        if selected == i:
                            celcolor = self.ColorSet['grey']
                        elif i % 2 == 0:
                            celcolor = self.ColorSet['blue']
                        else:
                            celcolor = self.ColorSet['black']
                        modulo = i % 2
                        celsizex = x
                        # Cel position
                        posx = 0
                        posy = y * i + (4 * y)
                        j = 1
                        # For each row of the table
                        for Opt, Val in Value.items():
                            if self.screen_proportions > 1 or Opt == "GAMENAME" or Opt == "PLAYERS":  # On a small screen , display only GAMENAME
                                posx += celsizex
                                celsizex = x * colfactor[Opt]
                                self.BlitRect(posx, posy, celsizex, y, celcolor)
                                Scaled = self.ScaleTxt(str(Val), celsizex, y)
                                font = pygame.font.Font(self.defaultfontpath, Scaled[0])
                                textF = font.render(str(Val), True, self.ColorSet['white'])
                                self.screen.blit(textF, [posx + Scaled[1], posy + Scaled[2]])
                            j += 1
                        ClickZones["select|"+str(i)] = (x, y * i + (4 * y), posx + celsizex - x, y)
                        i += 1
                    # Optionnaly display DOWN arrow
                    if ListLength > showend:
                        ClickZones['down'] = self.DownArrow(posx + celsizex, posy, y)
                    ClickZones['escape'] = self.PreviousMenu()  # Previous menu square
                    if selected>=0:
                        ClickZones['return'] = self.PressEnter(self.Lang.lang("OK"))
                    

                    # Custom refresh button (roughly centered)
                    RSX = int(self.res['x'] / 7)
                    RSY = int(self.res['y'] / 15)
                    RX = int(self.res['x']/2 - int(self.res['x'] / 15))
                    RY = int(self.res['y'] - self.res['y'] / 10)
                    ClickZones['space'] = self.PressEnter(self.Lang.lang("Refresh"),RX,RY,RSX,RSY,False,'refresh.png')
                    
                    self.UpdateScreen()  # Refresh screen

                    # Listen for any input
                    K = self.Inputs.ListenInputs(['arrows', 'alpha'],
                                                   ['enter', 'escape', 'space', 'TOGGLEFULLSCREEN', 'single-click'])
                    # Mouse
                    Clicked=self.IsClicked(ClickZones, K)
                    if Clicked:
                        if "select|" in Clicked:
                            splitted=Clicked.split("|")
                            selected=int(splitted[1])
                            # Auto-validation if list is one-item length
                            if ListLength==1:
                                K='enter'
                        else:
                            K=Clicked
                    """
                    try:
                        # Buttons
                        if 'escape' in ClickZones and self.IsClicked(ClickZones['escape'], key):
                            key = 'escape'
                        elif 'down' in ClickZones and self.IsClicked(ClickZones['down'], key):
                            showst += 1
                            showend += 1
                            if selected > 0:
                                selected -= 1
                        elif 'up' in ClickZones and self.IsClicked(ClickZones['up'], key):
                            showst -= 1
                            showend -= 1
                            if selected < maxsel - 1:
                                selected += 1
                        else:
                            for TheKey, Zone in ClickZone.items():
                                if self.IsClicked(Zone, key):
                                    selected = showst + TheKey
                                    return List[selected]
                    except Exception as e:
                        print("Error : {}".format(e))
                    """
                    # Keyboard
                    if K == 'down' and selected < maxsel - 1 and selected + showst < ListLength - 1:
                        selected += 1
                    elif K == 'down' and selected == maxsel - 1 and selected + showst < ListLength - 1:
                        showst += 1
                        showend += 1
                    elif K == 'down' and selected == maxsel - 1 and selected + showst == ListLength - 1:
                        showst = 0
                        showend = maxsel
                        selected = 0
                    elif K == 'TOGGLEFULLSCREEN':  # Toggle fullscreen
                        self.CreateScreen(True)
                    elif K == 'up' and selected > 0:
                        selected -= 1
                    elif K == 'up' and selected == 0 and showst > 0:
                        showst -= 1
                        showend -= 1
                    elif K == 'up' and selected == 0 and showst == 0:
                        selected = maxsel - 1
                        showst = max(0, ListLength - displaymax)
                        showend = ListLength
                    elif K == 'enter' or K == 'return':
                        return List[selected + showst]
                    elif K == 'space':
                        nexttick = int(pygame.time.get_ticks() / 1000) + masterclientpolltime
                        break
                    elif K == 'escape':
                        return K

    #
    # Version 2 of menu to choose options
    #
    def OptionsMenu2(self, GameOpts, Game):
        # Case of a game without options
        if GameOpts == {}:
            self.Logs.Log("DEBUG", "No options in this game. Why not ?")
            self.GameOpts = {}
            return self.GameOpts
        self.Logs.Log("DEBUG", "Waiting for game options")
        # Init
        num = '0'
        previous_K = None
        sel = 1
        ClickZones = {}
        numericmaxlen = 6
        editing = {}
        # Init Kbd Shift key status
        self.Inputs.shift = False
        # Loop
        while True:
            border = 2  # border in px
            fkeys = []
            self.DisplayBackground()
            # Fx sizing
            Fx = int(self.res['x'] / 40)  # Start point of first option
            Fy = int(self.res['y'] / 5.5)  # Start point of first option
            Fsize = int(min(self.res['x'] / 15, self.res['y'] / 20))  # Basic size of a box (height and width)
            space = int(Fsize / 2)  # Space between options
            Vsize = Fsize * 2  # Value size
            textsize = int(self.res['y'] / 35)  # Size of basic text
            #textsize = int(self.res['y'] / 25)  # Size of basic text
            # Display menu header
            self.MenuHeader("{} {}".format(self.Lang.lang('game-options'), Game),self.Lang.lang('game-options-binary'))
            # Init
            i = 1
            for EachOpt, EachValue in GameOpts.items():
                #print(editing)
                # Define Colors regarding of state (editing, selecting or none)
                if str(i) in editing and EachValue not in ['True','False']:
                    #Fxbgcolor = self.ColorSet['grey']
                    Fxbordercolor = self.ColorSet['blue']
                    bgcolor = self.ColorSet['grey']
                    bordercolor = self.ColorSet['black']
                elif sel == i:
                    #Fxbgcolor = self.ColorSet['green']
                    if EachValue in ['True','False']:
                        Fxbordercolor = self.ColorSet['black']
                    else:
                        Fxbordercolor = self.ColorSet['green']
                    bgcolor = self.ColorSet['blue']
                    bordercolor = self.ColorSet['black']
                else:
                    #Fxbgcolor = self.ColorSet['blue']
                    Fxbordercolor = self.ColorSet['black']
                    bgcolor = self.ColorSet['white']
                    bordercolor = self.ColorSet['black']
                
                # Define colors regarding of boolean state (On / Off)
                """
                if EachValue=='False':
                    OptBgcolor=self.ColorSet['red']
                    OptColor = self.ColorSet['black']
                else:
                    OptBgcolor=self.ColorSet['green']
                    OptColor = self.ColorSet['black']
                """
                
                # Try to translate Option name
                try:
                    AliasEachOpt = self.Lang.lang("{}-{}".format(Game, EachOpt))
                except:
                    AliasEachOpt = EachOpt
                    self.Logs.Log("ERROR", "No translation for option {} of Game {}".format(EachOpt, Game))

                # Determine the place of the option name
                if EachValue == 'True' or EachValue == 'False':
                    Tx = Fx + Fsize
                    Tw = Fsize * 12
                else:
                    Tx = Fx + Fsize + Fsize * 3
                    Tw = Fsize * 9

                # Scale Opt name
                ScaledOpt = self.ScaleTxt(AliasEachOpt, Tw - self.space * 2, Fsize)
                font = pygame.font.Font(self.defaultfontpath, ScaledOpt[0])
                textEachOpt = font.render(AliasEachOpt, True, self.ColorSet['black'])
                
                # Display Option name square
                self.BlitRect(Tx, Fy, Tw, Fsize, bgcolor)
                
                # Display Option name label
                self.screen.blit(textEachOpt, [Tx + self.space * 2, Fy + ScaledOpt[2]])
                
                # Append actual Fx key to the usable keys
                fkeys.append('f' + str(i))
                
                # For a value False (or turned false)
                if (EachValue == 'False' and str(i) not in editing) or (EachValue == 'True' and str(i) in editing):
                    # Draw Fx square and value
                    self.BlitRect(Fx, Fy, Fsize, Fsize, self.ColorSet['red'], True, Fxbordercolor)
                    try:
                        del editing[str(i)]
                    except:
                        pass
                    # Switch to False
                    GameOpts[EachOpt] = 'False'
                # For a value True (or turned true)
                elif (EachValue == 'True' and str(i) not in editing) or (EachValue == 'False' and str(i) in editing):
                    self.BlitRect(Fx, Fy, Fsize, Fsize, self.ColorSet['green'], True, Fxbordercolor)
                    try:
                        del editing[str(i)]
                    except:
                        pass
                    # Switch to true
                    GameOpts[EachOpt] = 'True'
                # Else its not a boolean
                else:
                    self.BlitRect(Fx, Fy, Fsize, Fsize, self.ColorSet['green'], True, bordercolor)
                # Put Fx square in clickable zone
                ClickZones['f' + str(i)] = (Fx, Fy, Fsize + Tw, Fsize)
                # Draw Fx
                F = "F" + str(i)
                ScaledF = self.ScaleTxt(F, Fsize, Fsize)
                font = pygame.font.Font(self.defaultfontpath, ScaledF[0])
                textF = font.render(F, True, self.ColorSet['white'])
                self.screen.blit(textF, [Fx + ScaledF[1], Fy + ScaledF[2]])

                # Option Value (only for NUMERIC Values)
                if (EachValue != 'False' and EachValue != 'True'):
                    if str(i) in editing:  # Start editing, clear value
                        #c = self.ColorSet['red']
                        if editing[str(i)] == '':
                            v = '_'
                        else:  # Append new char to the numeric value
                            try:
                                v = int(editing[str(i)])
                                GameOpts[EachOpt] = v
                            except Exception as e:
                                self.Logs.Log("WARNING", "Unknown input. Only integer allowed here. Ignoring.")
                    #### THE LINES BELOWS ARE WRONG, 'int' object has no attribute for .find ####
                    # Lookup for a float value
                    #elif EachValue.find('.')!=-1:
                     #   self.Logs.Log("WARNING", "%s Using float values is discouraged. Please try to use integers if possible".format(EachOpt))
                      #  v = float(EachValue)
                    # Fallback to an integer (can be something else, but it should be an error)
                    else:
                        v = int(EachValue)
                    #print(EachOpt)
                    #print(EachValue)
                    # Draw value box for valuable options
                    self.BlitRect(Fx + Fsize, Fy, Fsize * 3, Fsize, self.ColorSet['black'], True, bordercolor)
                    # Put value Fx box + Value box + Option box in clickable zone
                    ClickZones['f' + str(i)] = (Fx, Fy, Fsize + Tw + Fsize * 6, Fsize)
                    # Draw value
                    ScaledV = self.ScaleTxt(str(v), Fsize * 6, Fsize, None, 'fonts/Digital.ttf')
                    font = pygame.font.Font('fonts/Digital.ttf', ScaledV[0])
                    textEachValue = font.render(str(v), True, self.ColorSet['white'])
                    self.screen.blit(textEachValue, [Fx + Fsize + self.space * 2, Fy + ScaledV[2] - self.space])
                # Previous menu square
                ClickZones['escape'] = self.PreviousMenu()
                # Increment
                Fy += Fsize + space
                i += 1
            # Display OK
            ClickZones['return'] = self.PressEnter(self.Lang.lang("OK"))
            # Update display
            pygame.display.update()
            # Editing
            K = self.Inputs.ListenInputs(['num', 'fx', 'arrows'],
                                         ['BACKUPBUTTON', 'EXTRABUTTON','PLAYERBUTTON', 'GAMEBUTTON',
                                            'enter', 'escape','TOGGLEFULLSCREEN', 'single-click','space'])
            # Input - mouse
            Clicked=self.IsClicked(ClickZones, K)
            if Clicked:
                K=Clicked
            # Next !
            if (K == 'return' or K == 'enter' or K == 'GAMEBUTTON') and len(editing) == 0:
                self.GameOpts = GameOpts
                return GameOpts
            # Move selection up
            elif (K == 'PLAYERBUTTON' or K=='down') and len(editing)==0:
                sel+=1
                if sel==len(GameOpts)+1:
                    sel=1
            # Move selection down
            elif (K == 'up') and len(editing)==0:
                sel-=1
                if sel==0:
                    sel=len(GameOpts)
            # Toggle fullscreen on
            elif (K == 'TOGGLEFULLSCREEN') and len(editing) == 0:
                self.CreateScreen(True)
            # Toggle on editing mode with Enter or EXTRABUTTON
            elif (K == 'return' or K == 'enter' or K == 'GAMEBUTTON') and len(editing) > 0:
                editing = {}
            # Remove a char
            elif (K == 'backspace' or K=='BACKUPBUTTON') and len(editing) > 0:
                for k in editing:
                    editing[k] = editing[k][:-1]
            # Toggle on edit mode with Fx keys
            elif K in fkeys and len(editing) == 0:
                editing = {}
                editing[K[1:]] = ''
            # Toggle off editing mode with F keys
            elif K in fkeys and len(editing) > 0:
                editing = {}
            # Toggle on editing mode with Extrabutton
            elif (K == 'EXTRABUTTON' or K=='space') and len(editing)==0:
                editing = {}
                # Using buttons, prepare first input (kind, isn't it?)
                if K=='EXTRABUTTON':
                    editing[str(sel)] = '1'
                # Using keyboard, let the user blow himself up
                else:
                    editing[str(sel)] = ''
            # Add char to option
            elif (K == 'up' or K=='EXTRABUTTON') and len(editing) > 0:
                for k in editing:
                    if len(editing[k]) < numericmaxlen:
                        editing[k] = "{}0".format(editing[k])
                        num = '0'
            # Next number - round the numbers (edition context)
            elif (K == 'PLAYERBUTTON' or K == 'right') and len(editing) > 0:
                if num == 9 :  #  Eventually reset to 0 (round)
                    K = 0
                else:  # Or increment char
                    K = int(num) + 1
                num = K  #  Keep it in mind
                for k in editing:
                    if len(editing[k])>0:
                        editing[k] = "{}{}".format(editing[k][:-1], str(K))
                    else:
                        editing[k] = str(K)
            # Previous menu
            elif (K == 'escape' or K=='BACKUPBUTTON') and len(editing)==0:
                return 'escape'
            # Append a numeric value
            elif len(editing) > 0:
                for curr in editing:
                    # Unable setting a numeric value of more than numericmaxlen char
                    if len(editing[curr]) < numericmaxlen:
                        editing[curr] = "{}{}".format(editing[curr], K)

    #
    # Menu to select proper serial port
    #
    def SelectPort(self, ports):
        self.Logs.Log("DEBUG", "Please select game port")
        # Init
        fkeys = []
        self.Inputs.shift = False  # Reinit Kbd Shift status
        maxdisplayports = 8
        # Loop
        while True:
            border = 2  # border in px
            self.DisplayBackground()
            # Fx sizing
            Fx = int(self.res['x'] / 40)  # Start point of first option
            Fy = int(self.res['y'] / 5.5)  # Start point of first option
            Fsize = int(self.res['y'] / 15)  # Basic size of a box
            space = int(self.res['y'] / 40)  # Space between options
            Vsize = int(self.res['x'] - Fsize - Fx * 2)  # Value size
            textsize = int(self.res['y'] / 35)  # Size of basic text
            self.MenuHeader(self.Lang.lang("select-port"), self.Lang.lang("select-port-subtxt"))  # Display menu header
            # Init
            i = 1

            for portname in ports:
                # Append actual Fx key to the usable keys
                fkeys.append("f{}".format(i))
                # Draw Fx square and value
                self.BlitRect(Fx, Fy, Fsize, Fsize, self.ColorSet['red'], border, False)
                # Draw Fx
                F = "F{}".format(i)
                ScaledF = self.ScaleTxt(F, Fsize, Fsize)
                font = pygame.font.Font(self.defaultfontpath, ScaledF[0])
                textF = font.render(F, True, self.ColorSet['white'])
                self.screen.blit(textF, [Fx + ScaledF[1], Fy + ScaledF[2]])

                # Scale port name
                ScaledPort = self.ScaleTxt(portname, Vsize - self.space * 2, Fsize)
                font = pygame.font.Font(self.defaultfontpath, ScaledPort[0])  # Text size for second & third line
                txt = font.render(portname, True, self.ColorSet['black'])
                # Display port square
                self.BlitRect(Fx + Fsize, Fy, Vsize, Fsize, self.ColorSet['white'])
                # Display port name
                self.screen.blit(txt, [Fx + Fsize + ScaledPort[1], Fy + ScaledPort[2]])

                # Previous menu square
                self.PreviousMenu()
                # Update display
                pygame.display.update()
                # Increment
                Fy += Fsize + space
                # texty+=textsize
                i += 1
                # Limit to 10 ports
                if i > maxdisplayports:
                    self.Logs.Log("ERROR",
                                  "More than {} ports detected, but only {} first are displayed".format(maxdisplayports,
                                                                                                        maxdisplayports))
                    break
            K = self.Inputs.ListenInputs(['num', 'fx', 'arrows'], ['enter', 'escape', 'TOGGLEFULLSCREEN'])
            # What the user want to say?
            if (K == 'return' or K == 'enter'):
                pass
            elif (K == 'TOGGLEFULLSCREEN'):  # Toggle fullscreen
                self.CreateScreen(True)
            elif K in fkeys:
                selected = int(K[1:])
                return ports[selected - 1]
            elif K == 'escape':
                self.Logs.Log("DEBUG", "See ya dude !")
                sys.exit(0)

    #
    # Stats Screen
    #
    def DisplayRecords(self, data, record, gamename, gameoptions, current=False):
        self.Logs.Log("DEBUG","Displaying Hi score table for game \"" + gamename + "\" and options \"" + gameoptions + "\"")
        while True:
            # Init
            ClickZones = {}
            self.DisplayBackground()

            # Split game options
            gopts = gameoptions.split("|")
            txt_o = self.Lang.lang('Options: ')
            for o in gopts:
                if o != "":
                    txt_o += o + ","

            # Store number of columns to display
            cols = len(data[0])
            rows = len(data)

            # Calculate col size
            if self.res['x'] < self.res['y']:  # Vertical display
                colsize = int((self.res['x'] / cols) - (self.space * 2 / cols))
            else:
                colsize = int(self.res['x'] / (cols + 2))

            # Calculate row size
            rowsize = int(self.res['y'] / 24)
            BB = int(self.res['y'] / 200)

            # Print page header
            self.MenuHeader(self.Lang.lang('game-stats'), self.Lang.lang(record) + " - " + gamename + "(" + txt_o + ")")

            # Write table
            Y = int(self.res['y'] / 6)

            # Init before drawing
            if self.res['x'] < self.res['y']:  # Vertical display
                X = self.space
            else:
                X = int((self.res['x'] / 2) - ((cols * colsize) / 2))
            bgcolor = 'black'

            # Draw Table header
            if (current):
                txt = self.Lang.lang('this-game-stats')
            else:
                txt = self.Lang.lang('local-db-stats')
            self.BlitRect(X, Y, colsize * cols, rowsize, self.ColorSet[bgcolor], BB)
            Scaled = self.ScaleTxt(txt, colsize * cols - self.space * 2, rowsize)
            font = pygame.font.Font(self.defaultfontpath, Scaled[0])
            LSTtext_rd = font.render(txt, True, self.ColorSet['white'])
            self.screen.blit(LSTtext_rd, [X + Scaled[1] + self.space, Y + Scaled[2]])
            # X += colsize
            Y += rowsize

            # Draw first line (columns header)
            for i in range(0, cols):
                try:
                    if i == 0:
                        txt = self.Lang.lang('ranking')
                    elif i == 1:
                        txt = self.Lang.lang('Date')
                    elif i == 2:
                        txt = self.Lang.lang('Player')
                    elif i == 3:
                        txt = self.Lang.lang(record)
                except:
                    txt = "Error !"
                self.BlitRect(X, Y, colsize, rowsize, self.ColorSet[bgcolor], BB)
                Scaled = self.ScaleTxt(txt, colsize - self.space * 2, rowsize)
                font = pygame.font.Font(self.defaultfontpath, Scaled[0])
                LSTtext_rd = font.render(txt, True, self.ColorSet['white'])
                self.screen.blit(LSTtext_rd, [X + Scaled[1] + self.space, Y + Scaled[2]])
                X += colsize
            Y += rowsize

            # For every line of the table (except first which is hidden)
            for i in range(0, rows):
                # Reinit first col to left side of screen
                if self.res['x'] < self.res['y']:  # Vertical display
                    X = self.space
                else:
                    X = int((self.res['x'] / 2) - ((cols * colsize) / 2))
                # For every row
                for j in range(0, cols):
                    # Print count for first column, value otherwise
                    if j == 0:
                        bgcolor = 'black'
                        txt = str(i + 1)
                    elif data[i][0] == 1:
                        bgcolor = 'orange'
                        txt = str(data[i][j])
                    else:
                        bgcolor = 'green'
                        txt = str(data[i][j])
                    self.BlitRect(X, Y, colsize, rowsize, self.ColorSet[bgcolor], BB)
                    Scaled = self.ScaleTxt(txt, colsize - self.space * 2, rowsize)
                    font = pygame.font.Font(self.defaultfontpath, Scaled[0])
                    LSTtext_rd = font.render(txt, True, self.ColorSet['white'])
                    self.screen.blit(LSTtext_rd, [X + Scaled[1] + self.space, Y + Scaled[2]])
                    X += colsize
                Y += rowsize

            # Draw the "Start again" square
            ClickZones['enter'] = self.PressEnter(self.Lang.lang('start-again'), None, None, None, None, True)
            # Previous menu square
            ClickZones['escape'] = self.PreviousMenu()
            self.UpdateScreen()
            # Wait for an input
            K = self.Inputs.ListenInputs(['fx'], ['escape', 'enter', 'TOGGLEFULLSCREEN', 'BACKUPBUTTON', 'GAMEBUTTON', 'single-click'])
            # Analyse input (Mouse, keyboard and buttons)
            Clicked=self.IsClicked(ClickZones,K)
            if Clicked:
                K=Clicked
            try:
                if K == 'return' or K == 'enter' or K=='GAMEBUTTON':
                   return 'startagain'
                elif K == 'TOGGLEFULLSCREEN':
                   self.CreateScreen(True)
                elif K == 'escape' or K=='BACKUPBUTTON':
                   K=='escape'
            except Exception as e:
                print("Error : {}".format(e))
            return K

    #
    # This method fill background squares
    #
    def PlayerLine(self, y, playerid, actualplayer, nbplayers, waittime=False):
        # Please comment to explain
        self.teamingsize = self.pnsize / 5
        scoresize = self.boxwidth * 2
        # Player names' box
        if playerid == actualplayer:
            bgcolor = self.ColorSet['blue']
        else:
            bgcolor = self.ColorSet['black']
        self.BlitRect(self.space, y, self.pnsize - self.space, self.lineheight - self.space, bgcolor)
        # If teaming is enabled, display a colored square beside the player name
        if self.Teaming:
            # Convert Dict colors to a color list
            colors = list(self.ColorSet.values())
            # Reset color index after passing half number of players
            halfpl = round(nbplayers / 2)
            # Define team color - +2 avoid using white
            if playerid + 1 > halfpl:
                colorid = (playerid + 2) - halfpl
            else:
                colorid = playerid + 2
            # Display square for teaming
            self.BlitRect(self.space, y, self.teamingsize - self.space, self.lineheight - self.space, colors[colorid])
        if waittime:
            pygame.time.wait(waittime)
            self.UpdateScreen()
        # All other boxes
        for i in range(0, int(self.Config.GetValue('SectionGlobals', 'nbcol')) + 1):
            self.BlitRect(self.space + self.pnsize + self.boxwidth * i, y, self.boxwidth - self.space,
                          self.lineheight - self.space, self.ColorSet['black'])
            if waittime:
                pygame.time.wait(waittime)
                self.UpdateScreen()
        # Score box
        self.BlitRect(
            self.space + self.pnsize + self.boxwidth * (int(self.Config.GetValue('SectionGlobals', 'nbcol')) + 1), y,
            scoresize - self.space, self.lineheight - self.space, self.ColorSet['black'])
        if waittime:
            pygame.time.wait(waittime)
            self.UpdateScreen()

    #
    # This method display column headers
    #
    def Headers(self, Headers, nbpl):
        # self.boxwidth = int(self.res['x'] / 11.7)
        #FS = self.lineheight
        y = self.Position[0] - self.lineheight - self.space
        # print("Headers Y is : {}".format(y))
        #font = pygame.font.Font('fonts/Digital.ttf', FS)  # Text Size
        for i in range(0, int(self.Config.GetValue('SectionGlobals', 'nbcol')) + 1):
            # Limit header to 3 char
            txt = str(Headers[i][:3])
            Scaled = self.ScaleTxt(txt, self.boxwidth, self.lineheight)
            font = pygame.font.Font(self.defaultfontpath, Scaled[0])
            # Render text
            text = font.render(txt, True, self.ColorSet['white'])
            # Calculate place of text
            Xtxt = int(self.space + self.pnsize + self.boxwidth * i + Scaled[1])
            Ytxt = int(y + Scaled[2])
            # Create BG rect
            self.BlitRect(self.space + self.pnsize + self.boxwidth * i, y, self.boxwidth - self.space, self.lineheight,self.ColorSet['grey'], False, False, self.alpha + 10)
            # Display text
            self.screen.blit(text, [Xtxt, Ytxt])

    #
    # Refresh In-game screen
    #
    def RefreshGameScreen(self, Players, Round, MaxRound, RemDarts, nbdarts, LogoImg, Headers, actualplayer,TxtOnLogo=False, Wait=False):
        # Get number of players
        nbplayers = len(Players)

        # Recalculate line height
        self.DefineConstants(nbplayers)
        
        # Init ClickZones
        ClickZones={}

        # Clear
        self.screen.fill(self.ColorSet['black'])

        # Background image
        self.DisplayBackground()
        
        # Game Logo (or optionnaly "Text On Logo")
        if not TxtOnLogo:
            self.GameLogo(LogoImg)
        else:
            self.TxtOnLogo(str(TxtOnLogo))
        #
        # Game options
        #
        # If some options are displayed, use compact mode for remaining darts
        OptDisplayed = self.DisplayGameOptions()
        if OptDisplayed:
            # Rem Darts compact display
            self.DisplayRemDarts_compact(RemDarts, nbdarts)
        else:
            # Rem Darts normal :)
            self.DisplayRemDarts(RemDarts, nbdarts)
        #
        # Rounds
        #
        self.DisplayRound(Round, MaxRound)

        #
        # All players line by line
        #
        for P in Players:
            # Display all other info on the player line
            if TxtOnLogo:
                # Do not trigger animation
                self.PlayerLine(self.Position[P.ident], P.ident, actualplayer, nbplayers)
            else:
                # Trigger animation
                self.PlayerLine(self.Position[P.ident], P.ident, actualplayer, nbplayers,int(self.Config.GetValue('SectionAdvanced', 'animationduration')))
            # Display Player Score
            self.DisplayScore(self.Position[P.ident], P.GetScore())
            # Displayer player name box
            self.DisplayPlayerName(self.Position[P.ident], P.couleur, P.ident, actualplayer, P.PlayerName)
        # Display Headers
        self.Headers(Headers, len(Players))
        # Display Table Content
        self.DisplayTableContent(Players)
        # Display on-screen clickable buttons if requested
        if self.Config.GetValue('SectionGlobals', 'onscreenbuttons'):
            ClickZones=self.OnScreenButtons()
        # Refresh !
        self.UpdateScreen()
        # Wait if requested
        if Wait:
            pygame.time.wait(Wait)
        # Return Clickable zones
        return ClickZones

    #
    # Display an image on the middle top of the screen
    #
    def GameLogo(self, logoimage=False):
        # Local Constants
        X = self.pnsize + self.space
        Y = self.topspace
        SX = self.boxwidth * (int(self.Config.GetValue('SectionGlobals', 'nbcol')) + 1) - self.space
        SY = self.boxheight - self.lineheight - self.topspace - self.space
        # Display rect container - if a color is set in colorset
        self.BlitRect(X, Y, SX, SY, self.ColorSet['bg-logo'])
        # Display logo
        self.DisplayImage(self.GetPathOfFile('images', logoimage), X, Y, SX, SY, False, True)

    #
    # Display text instead of game logo
    #
    def TxtOnLogo(self, txt, Wait=False, Update=False):
        # Local Constants
        X = self.pnsize + self.space
        Y = self.topspace
        SX = self.boxwidth * (int(self.Config.GetValue('SectionGlobals', 'nbcol')) + 1) - self.space
        SY = self.boxheight - self.lineheight - self.topspace - self.space
        BorderColor = self.ColorSet['grey']
        BgColor = self.ColorSet['black']
        BorderSize = int(self.boxwidth / 20)
        TxtColor = self.ColorSet['white']
        Scaled = self.ScaleTxt(txt, SX, SY)
        font = pygame.font.Font(self.defaultfontpath, Scaled[0])
        # Display Rect container
        self.BlitRect(X, Y, SX, SY, self.ColorSet['bg-logo'], BorderSize, BorderColor)
        # Render text
        text = font.render(txt, True, TxtColor)
        # Text location
        TX = X + Scaled[1]
        TY = Y + Scaled[2]
        # Blit text
        self.screen.blit(text, [TX, TY])
        if Update: self.UpdateScreen()  # Refresh screen if requested
        if Wait: pygame.time.wait(Wait)  # Wait if requested

    #
    # Display a background image
    #
    def DisplayBackground(self, bgimage='background.png'):
        # If there is no background color in used colorset, try to use image
        if not self.ColorSet['bg-global']:
            imagefile = self.GetPathOfFile('images', bgimage)
            self.DisplayImage(imagefile, 0, 0, self.res['x'], self.res['y'], True)
        # Or fill with color set in colorset
        else:
            self.screen.fill(self.ColorSet['bg-global'])

    #
    # Scale and display an image
    #
    # used to avoid the libpng warning : libpng warning: iCCP: known incorrect sRGB profile
    def DisplayImage(self, imagepath, X, Y, SX=0, SY=0, Scale=False, CenterX=False, CenterY=False):
        try:
            if imagepath not in self.imagecache:
                self.Logs.Log("DEBUG", "Inserting image into cache {}".format(imagepath))
                self.imagecache[imagepath] = pygame.image.load(imagepath)
            loadimage = self.imagecache[imagepath]
            loadimage_size = loadimage.get_rect().size  # Get image size
            loadimage_prop = float(loadimage_size[0]) / float(loadimage_size[1])
        except Exception as e:
            self.Logs.Log("WARNING", "Unable to load image {}. Error was {}.".format(imagepath, e))
            return False
        ### Calculate image size
        # If requested, scale image to container
        if SX and SY and Scale:
            loadimage_SX = SX
            loadimage_SY = SY
            # Else, try first to fit into width
        elif not Scale and int(SX / loadimage_prop) <= int(SY):
            # print("scaled based on SX")
            loadimage_SX = int(SX)
            loadimage_SY = int(SX / loadimage_prop)
        # If it doesnt fit, try to
        elif not Scale:
            # print("scaled based on SY")
            loadimage_SX = int(SY * loadimage_prop)
            loadimage_SY = int(SY)
        # Calculate image position
        if CenterX:
            loadimage_X = int(X + (SX - loadimage_SX) / 2)
        else:
            loadimage_X = X
        if CenterY:
            loadimage_Y = int(Y + (SY - loadimage_SY) / 2)
        else:
            loadimage_Y = Y
        # Blit image according to above config
        loadimage = pygame.transform.scale(loadimage, (int(loadimage_SX), int(loadimage_SY)))
        self.screen.blit(loadimage, (loadimage_X, loadimage_Y))

    #
    #  Define and eventually refresh some constants (most of them depends of user resolution)
    #
    def DefineConstants(self, nbplayers=None):
        # Basic space
        self.space = int(self.res['y'] / 200)
        # Space at the top side of the screen
        self.topspace = self.space
        # Define bottom space
        if self.Config.GetValue('SectionGlobals', 'onscreenbuttons'):
            self.bottomspace = self.space*32
        else:
            self.bottomspace = self.space
        # Space on left side of the screen
        self.leftspace = int(self.res['x'] / 8)
        # Header for in-game screen boxes
        self.boxheaders = int(self.res['y'] / 25)
        self.boxheight = int(self.res['y'] / 2.5)
        # Nb col + 1 bull + 4 unit for player name and score
        self.boxwidth = int(self.res['x'] / (int(self.Config.GetValue('SectionGlobals', 'nbcol')) + 5))  
        # Transparency
        self.alpha = 210
        # Default font path
        self.defaultfontpath = 'fonts/Purisa.ttf'
        # Animation time (in ms)
        self.animation = 5
        ###### HEIGHT
        # All this sh** depends of the nb of players
        if nbplayers:
            # The size of the top and bottom part of the screen
            self.screen_top = self.boxheight - self.boxheaders - self.topspace
            self.screen_bottom = self.res['y'] - self.screen_top - self.bottomspace
            # Max lineheight is restrained to the space when 3 players plays (+ 1 header)
            max_lineheight = int(self.screen_bottom / 4)
            # Calculate lineheight
            # Screen size minus the header size, divided by number of players + 1 header
            self.lineheight = min(int(self.screen_bottom / (nbplayers + 1)),max_lineheight)
            # Define Y position of each line for each player
            self.Position = []
            for p in range(0, nbplayers):
                positemp = int(self.res['y'] - self.bottomspace - ((nbplayers - p) * (self.lineheight)))
                self.Position.append(positemp)

        ###### WIDTH (X Axis)
        # Player name box width
        self.pnsize = self.boxwidth * 2
        # Width of an in-game column
        self.colwidth = self.boxwidth

        ###### SCREEN PROPORTIONS
        # Proportion between screen Height and Width
        self.screen_proportions = float(float(self.res['x']) / float(self.res['y']))
        # Limit of proportion before considering the screen as vertical display
        self.prop_limit = 1

    #
    # Display name of the player if given, Player X otherwise
    #
    def DisplayPlayerName(self, y, couleur, ident, actualplayer, playername=None):
        if (playername == None):
            playername = 'Player ' + str(ident)
        if actualplayer == ident:
            txtcolor = self.ColorSet['black']
        else:
            txtcolor = self.ColorSet['white']
        #  Player name size depends of player name number of char (dynamic size)
        Scaled = self.ScaleTxt(playername, self.pnsize - 2 * self.space, self.lineheight)
        font = pygame.font.Font(self.defaultfontpath, Scaled[0])
        # Render the text. "True" means anti-aliased text.
        playernamex = self.space * 2 + Scaled[1]
        playernamey = y + Scaled[2]
        text = font.render(playername, True, txtcolor)
        self.screen.blit(text, [playernamex, playernamey])

    #
    # Fill-in table With DISPLAY-LEDS func
    #
    def DisplayTableContent(self, Players, Wait=False):
        for Player in Players:
            #self.Logs.Log("DEBUG", "Displaying table content for player {}".format(Player.ident))
            for Column, Value in enumerate(Player.LSTColVal):
                if len(Value) == 3:
                    color = Value[2]
                else:
                    color = None
                if Value[1] == 'image':  # Maybe you want to put images in the table?
                    self.DisplayLedsImg(self.Position[Player.ident], Value[0], Column)
                elif Value[1] == 'leds':  # Or you want to display leds style?
                    self.LedBox(self.Position[Player.ident], int(Value[0]), Column, color)
                else:  # Or fallback to default, it displays a string or int
                    self.TxtBox(self.Position[Player.ident], str(Value[0]), Column, color)
                if Wait:
                    pygame.time.wait(self.animation)

    #
    # Graphical representation of a number in the box, from 0 to 3
    #
    def LedBox(self, posy, NbLed, Col, Color=None):
        # 3 leds max
        # Constants
        scoresize = int(self.res['x'] / 5)
        # self.boxwidth = int(self.res['x'] / 11.7)
        #
        x = int(Col * self.boxwidth + self.pnsize + self.space)
        y = int(posy)
        xend = int(Col * self.boxwidth + self.boxwidth + self.pnsize - self.space / 4)
        yend = int(posy + self.lineheight - self.space * 2)
        if Color == None:
            Color = self.ColorSet['white']
        else:
            Color = self.ColorSet[Color]
        BB = int(self.res['y'] / 130)
        if NbLed == 1:
            pygame.draw.line(self.screen, Color, [x, y + self.space], [xend, yend], BB)
        elif NbLed == 2:
            pygame.draw.line(self.screen, Color, [x, y + self.space], [xend, yend], BB)
            pygame.draw.line(self.screen, Color, [x, yend], [xend, y + self.space], BB)
        elif NbLed == 3:
            self.BlitRect(self.space + self.pnsize + self.boxwidth * Col, y, self.boxwidth - self.space,
                          self.lineheight - self.space, Color)

    #
    # Display text or integer in the given column
    #
    def TxtBox(self, posy, Txt, Col, color=None):
        # keep max 4 char
        Txt = str(Txt[:4])

        # Asign default color if required
        if color == None: color = 'white'

        # Constants
        scoresize = int(self.res['x'] / 5)
        # self.boxwidth = int(self.res['x'] / 11.7)

        # Write text in box
        #print("Text is {}".format(str(Txt)))
        Scaled = self.ScaleTxt(Txt, self.boxwidth - self.space * 2, self.lineheight - self.space * 2)
        font = pygame.font.Font(self.defaultfontpath, Scaled[0])
        text = font.render(Txt, True, self.ColorSet[color])
        X=Col * self.boxwidth + self.pnsize + self.space * 2 + Scaled[1]
        Y=posy + Scaled[2]
        #print("X is : {} and Y is {}".format(X,Y))
        self.screen.blit(text, [X,Y])

    #
    # Display an image in a specified column of a given player
    #
    def DisplayLedsImg(self, posy, Image, Col):
        # Constants
        scoresize = int(self.res['x'] / 5)
        # self.boxwidth = int(self.res['x'] / 11.7)
        #
        imgHeight = int(self.lineheight - self.space * 3)
        imgWidth = int(min(self.boxwidth - self.space * 3, imgHeight))
        #
        X = int(Col * self.boxwidth + self.pnsize + self.space + (self.boxwidth - imgWidth) / 2)
        Y = int(posy + self.space)
        #
        imagefile = self.GetPathOfFile('images', '{}.png'.format(Image))
        self.DisplayImage(imagefile, X, Y, imgWidth, imgHeight, False, True, True)
        self.UpdateScreen()

    #
    # Display score for given player
    #
    def DisplayScore(self, posy, txt):
        color = color = self.ColorSet['white']
        txt = str(txt)
        scoresize = int(self.res['x'] / 5)
        # self.boxwidth = int(self.res['x'] / 11.7)
        #
        xtxt = int(self.pnsize + (int(self.Config.GetValue('SectionGlobals', 'nbcol')) + 1) * self.boxwidth)
        Scaled = self.ScaleTxt(txt, scoresize - self.space * 2, self.lineheight - self.space * 2)
        font = pygame.font.Font(self.defaultfontpath, Scaled[0])
        text = font.render(txt, True, self.ColorSet['white'])
        self.screen.blit(text, [xtxt + self.space * 2 + Scaled[1], posy + Scaled[2]])

    #
    # Display how many darts remain (only if game has no option so more room space available)
    #
    def DisplayRemDarts(self, nb, nbdarts, dartimage='target.png'):
        # Constants
        scoresize = int(self.res['x'] / 5)
        # self.boxwidth = int(self.res['x'] / 11.7)
        #
        X = int(self.space + self.pnsize + (self.boxwidth * 7))
        Y = self.topspace
        #
        SX = int(self.res['x'] - X - self.space)
        SY = self.boxheight
        #
        Th = self.boxheaders  # Basic title height
        #
        ImgHeight = min(int((SY - Th) / nbdarts), SX)
        ImgWidth = ImgHeight
        #
        Imgx = X + ((SX - ImgWidth) / 2)
        Imgy = Y + Th
        #
        imagefile = self.GetPathOfFile('images', dartimage)
        #
        ScaledFS = self.ScaleTxt(self.Lang.lang('remaining-darts'), SX, Th)
        fontsize = ScaledFS[0]
        font = pygame.font.Font(self.defaultfontpath, fontsize)
        xtxt = int(X + ScaledFS[1])
        ytxt = int(Y + ScaledFS[2])
        text = font.render(self.Lang.lang('remaining-darts'), True, self.ColorSet['white'])
        # Display
        self.BlitRect(X, Y, SX, SY, self.ColorSet['bg-darts-nb'])
        self.BlitRect(X, Y, SX, Th, self.ColorSet['bg-darts-nb-header'])
        # Pdartimage=pygame.transform.scale(Pdartimage,(ImgWidth,ImgHeight))
        self.screen.blit(text, [xtxt, ytxt])
        for x in range(0, nb):
            self.DisplayImage(imagefile, Imgx, Imgy + (x * ImgWidth), ImgWidth, ImgHeight)
            # self.screen.blit(Pdartimage, (Imgx,Imgy+(x*ImgWidth)))

    #
    # Compact version (when options are set in game)
    #
    def DisplayRemDarts_compact(self, nb, nbdarts, dartimage='target.png'):
        # Constants
        scoresize = int(self.res['x'] / 5)
        # self.boxwidth = int(self.res['x'] / 11.7)
        #
        X = int(self.space + self.pnsize + (self.boxwidth * 7))
        Y = self.topspace
        #
        SX = int(self.res['x'] - X - self.space)
        SY = int(self.res['y'] / 12)
        # Title height
        Th = self.boxheaders  # Basic title height
        #
        ImgHeight = min(int(SX / nbdarts), SY)
        ImgWidth = ImgHeight
        #
        Imgx = int(X + ((SX - ImgWidth * nbdarts) / 2))
        Imgy = int(Y + Th + ((SY - ImgHeight) / 2))
        #
        imagefile = self.GetPathOfFile('images', dartimage)
        #
        ScaledFS = self.ScaleTxt(self.Lang.lang('remaining-darts'), SX, Th)
        fontsize = ScaledFS[0]
        font = pygame.font.Font(self.defaultfontpath, fontsize)
        xtxt = int(X + ScaledFS[1])
        ytxt = int(Y + ScaledFS[2])
        text = font.render(self.Lang.lang('remaining-darts'), True, self.ColorSet['white'])
        # Display
        self.BlitRect(X, Y + Th, SX, SY, self.ColorSet['bg-darts-nb'])
        self.BlitRect(X, Y, SX, Th, self.ColorSet['bg-darts-nb-header'])
        # Pdartimage=pygame.transform.scale(Pdartimage,(ImgWidth,ImgHeight))
        self.screen.blit(text, [xtxt, ytxt])
        for x in range(0, nb):
            # self.screen.blit(Pdartimage, (Imgx+(x*ImgWidth),Imgy))
            self.DisplayImage(imagefile, Imgx + (x * ImgWidth), Imgy, ImgWidth, ImgHeight)

    #
    # Display game options during gameplay
    #
    def DisplayGameOptions(self):
        # Define options to be hidden on game screen
        HideOptions = {'totalround': False, 'max_round': False}
        # Remove them from dict
        Display_GameOpts = {k: v for k, v in self.GameOpts.items() if k not in HideOptions}  # Hide arbitrary options
        # Remove options when value is False
        Display_GameOpts = {key: value for key, value in Display_GameOpts.items() if
                            value != 'False'}  # Remove false options
        # Get number of options
        GameOpts_len = len(Display_GameOpts)
        # Stop here if there is no otion to display
        if GameOpts_len == 0: return False
        # Constants
        scoresize = int(self.res['x'] / 5)
        # self.boxwidth = int(self.res['x'] / 11.7)
        #
        X = int(self.space + self.pnsize + (self.boxwidth * 7))
        Y = self.topspace + int(self.res['y'] / 12) + int(self.res['y'] / 25) + self.space
        #
        SX = int(self.res['x'] - X - self.space)
        Th = self.boxheaders  # Basic title height
        MaxSy = int(self.screen_top - int(self.res['y'] / 12) - Th - self.topspace - self.space)
        SY = min(Th, int(MaxSy / GameOpts_len))
        # Display header
        self.BlitRect(X, Y, SX, Th, self.ColorSet['bg-optionslist-header'])
        ScaledFS = self.ScaleTxt(self.Lang.lang('game-options'), SX, SY)
        font = pygame.font.Font(self.defaultfontpath, ScaledFS[0])
        xtxt = int(X + ScaledFS[1])
        ytxt = int(Y + ScaledFS[2])
        text = font.render(self.Lang.lang('game-options'), True, self.ColorSet['white'])
        self.screen.blit(text, [xtxt, ytxt])
        Y += SY
        # Display options one by one
        for Opt, Val in Display_GameOpts.items():
            if Val != 'True':
                txt = self.Lang.lang('{}-{}'.format(self.selectedgame, Opt)) + ' : ' + str(Val)
            else:
                txt = self.Lang.lang('{}-{}'.format(self.selectedgame, Opt))
            ScaledFS = self.ScaleTxt(txt, SX, SY)
            fontsize = ScaledFS[0]
            font = pygame.font.Font(self.defaultfontpath, fontsize)
            xtxt = int(X + ScaledFS[1])
            ytxt = int(Y + ScaledFS[2])
            self.BlitRect(X, Y, SX, SY, self.ColorSet['bg-optionslist'])
            text = font.render(txt, True, self.ColorSet['white'])
            self.screen.blit(text, [xtxt, ytxt])
            Y += SY
        # Return True if some options are displayed
        return True

    #
    # Display Round
    #
    def DisplayRound(self, Round, MaxRound):
        # Constants
        scoresize = int(self.res['x'] / 5)
        #
        X = self.space
        Y = self.topspace
        #
        SX = int(self.pnsize - self.space)
        SY = self.boxheight
        # Title Y size
        Th = self.boxheaders
        #
        RndFs = int(SY / 12) * 5
        ScaledRnd = self.ScaleTxt(str(Round), SX, RndFs, None, 'fonts/Digital.ttf')
        fontFs = pygame.font.Font('fonts/Digital.ttf', ScaledRnd[0])
        Rnd = fontFs.render(str(Round), True, self.ColorSet['white'])
        RndX = X + ScaledRnd[1]
        RndY = Y + ScaledRnd[2] + self.space
        #
        RndOverFs = int(SY / 12) * 3
        ScaledRndOver = self.ScaleTxt(str(self.Lang.lang('over')), SX, RndOverFs, None, self.defaultfontpath)
        fontOverFs = pygame.font.Font(self.defaultfontpath, ScaledRndOver[0])
        RndOver = fontOverFs.render(str(self.Lang.lang('over')), True, self.ColorSet['white'])
        RndOverX = X + ScaledRndOver[1]
        RndOverY = Y + RndFs + ScaledRndOver[2] + self.space * 2
        #
        RndMaxFs = int(SY / 12) * 4
        ScaledRndMax = self.ScaleTxt(str(MaxRound), SX, RndMaxFs, None, 'fonts/Digital.ttf')
        fontMaxFs = pygame.font.Font('fonts/Digital.ttf', ScaledRndMax[0])
        RndMax = fontMaxFs.render(str(MaxRound), True, self.ColorSet['white'])
        RndMaxX = X + ScaledRndMax[1]
        RndMaxY = Y + RndFs + RndOverFs + ScaledRndMax[2]
        #
        ScaledTitle = self.ScaleTxt(str(self.Lang.lang('round')), SX, Th)
        font = pygame.font.Font(self.defaultfontpath, ScaledTitle[0])
        xtxt = X + ScaledTitle[1]
        ytxt = Y + ScaledTitle[2]
        text = font.render(self.Lang.lang('round'), True, self.ColorSet['white'])
        # Display
        self.BlitRect(X, Y, SX, SY, self.ColorSet['bg-round-nb'])
        self.BlitRect(X, Y, SX, Th, self.ColorSet['bg-round-nb-header'])
        self.screen.blit(text, [xtxt, ytxt])
        self.screen.blit(Rnd, [RndX, RndY])
        self.screen.blit(RndOver, [RndOverX, RndOverY])
        self.screen.blit(RndMax, [RndMaxX, RndMaxY])

    #
    # Display Round
    #
    def OnScreenButtons(self):
        # Init
        ClickZones={}
        
        # GAME BUTTON
        SX=(self.res['x'] - self.space * 6) / 4
        SY=self.space*30
        X=self.space
        Y=self.res['y'] - SY - self.space * 2
        
        # Blit Background rect
        self.BlitRect(X,Y,SX,SY, self.ColorSet['red'],2,self.ColorSet['grey'],self.alpha)
        ClickZones['GAMEBUTTON']=(X,Y,SX,SY)
        
        # Blit button
        self.CenterText(self.Lang.lang('Exit'),X,Y,SX,SY, self.ColorSet['black'])

        # BACKUP BUTTON
        X= X + self.space + SX
        
        # Blit Background rect
        self.BlitRect(X,Y,SX,SY, self.ColorSet['orange'],2,self.ColorSet['grey'],self.alpha)
        ClickZones['BACKUPBUTTON']=(X,Y,SX,SY)
        
        # Blit button
        self.CenterText(self.Lang.lang('Backup'),X,Y,SX,SY, self.ColorSet['black'])

        # MISS BUTTON
        X= X + self.space + SX
        
        # Blit Background rect
        self.BlitRect(X,Y,SX,SY, self.ColorSet['green'],2,self.ColorSet['grey'],self.alpha)
        ClickZones['MISSDART']=(X,Y,SX,SY)
        
        # Blit button
        self.CenterText(self.Lang.lang('Missed'),X,Y,SX,SY, self.ColorSet['black'])

        # PLAYER BUTTON
        X= X + self.space + SX
        
        # Blit Background rect
        self.BlitRect(X,Y,SX,SY, self.ColorSet['blue'],2,self.ColorSet['grey'],self.alpha)
        ClickZones['PLAYERBUTTON']=(X,Y,SX,SY)
        
        # Blit button
        self.CenterText(self.Lang.lang('Next Player'),X,Y,SX,SY, self.ColorSet['black'])
        
        # Return Dict of tuples representing clickage values
        return ClickZones


    #
    # Render text in a box, directly at best size
    #
    def CenterText(self,txt,X,Y,SX,SY,color=None, dafont=None):
        if not color:color=self.ColorSet['black']
        if not dafont:dafont=self.defaultfontpath
        # Display Text
        Scaled = self.ScaleTxt(txt, SX, SY)
        font = pygame.font.Font(dafont, Scaled[0])
        # Render text
        text = font.render(txt, True, color)
        # Calculate place of text
        Xtxt = int(X + Scaled[1])
        Ytxt = int(Y + Scaled[2])
        # Display text
        self.screen.blit(text, [Xtxt, Ytxt])

    #
    # Compare Key to clickable zone and return corresponding key
    #

    #
    # Show the player icon on the top right of the screen
    #
    def DisplayPressPlayer(self, txt='Press Player button', color='red'):
        H = int(self.res['y'] / 10)
        W = int(self.res['x'])
        X = 0
        Y = int((self.res['y'] / 2) - (H / 2))
        pygame.draw.rect(self.screen, self.ColorSet[color], (X, Y, W, H), 0)
        Scaled = self.ScaleTxt(txt, W, H)
        font = pygame.font.Font(self.defaultfontpath, Scaled[0])
        text = font.render(txt, True, self.ColorSet['black'])
        self.screen.blit(text, [X + Scaled[1], Y + Scaled[2]])
        # self.DisplayCenteredText(self.res['y']/2,txt,int(self.res['x']/20))
        self.UpdateScreen()

    #
    # Simply update the screen (after multiple updates for example)
    #
    def UpdateScreen(self):
        #pygame.display.flip()
        pygame.display.update()

    #
    # Espeak vocal synthetiser (untested on windows)
    #
    def Speech(self, text):
        # Check config
        speech = self.Config.GetValue('SectionAdvanced', 'speech')
        self.Logs.Log("DEBUG", "Trying to speech text {} with engine {}".format(text,speech))
        if speech=='espeak':
            r=self.Espeak(text)
        elif speech=='pyttsx3':
            r=self.Pyttsx3(text)
        else:
            self.Logs.Log("WARNING", "Unsupported speech engine : {}".format(speech))
            return False
        return r


    def Espeak(self,text):
        try:
            espeakpath = self.Config.GetValue('SectionGlobals', 'espeakpath')
            if espeakpath:
                if os.path.isfile(espeakpath):
                    try:
                        volume = self.SoundVolume
                        pid = subprocess.Popen([espeakpath, "-a", "{}".format(volume), "-s", "100", "-v", "fr", "\"{}\"".format(text)])
                    except Exception as e:
                        self.Logs.Log("WARNING", "Problem trying to use espeak : {}".format(e))
                        return False
                else:
                    self.Logs.Log("DEBUG", "Espeak path {} does not exists on your system".format(espeakpath))
                    return False
            else:
                self.Logs.Log("WARNING", "Espeak path is not set in your pydarts config file.")
                return False
        except Exception as e:
            self.Logs.Log("ERROR", "Unable to speech with espeak.")
            self.Logs.Log("DEBUG", "Error was : {}".format(e))
            return False

    #
    # Cross-platform text-to-speech syntetiser (should work better on windows)
    #
    def Pyttsx3(self, text):
        try:
            volume = round(self.SoundVolume / 100,1)
            self.tts.setProperty('volume',volume)
            self.tts.say(text)
            self.tts.runAndWait()
            return True
        except Exception as e:
            self.Logs.Log("WARNING", "Problem running cross-platform text-to-speech pyttsx3.")
            self.Logs.Log("DEBUG", "Error was : "+str(e))
            return False

    #
    # Play given sound. Search first in the home folder, then play default sound, or beep1 if not found.
    #
    def PlaySound(self, filename='beep1', PlayDefIfNotFound=True, fileformat='ogg'):
        sound = False
        if sys.platform=='win':separator="\\"
        else: separator="/"
        filetoplay = self.GetPathOfFile('sounds', '{}.{}'.format(filename, fileformat))
        if not filetoplay and PlayDefIfNotFound:
            self.Logs.Log("WARNING","Unable to load this audio file : {}.{}, playing default beep !".format(filename, fileformat))
            filetoplay = 'sounds/beep1.ogg'
        elif not filetoplay and not PlayDefIfNotFound:
            self.Logs.Log("DEBUG", "Sound file {} was not found and no default was selected!".format(filename))
            return False
        else:
            # Must be a good case, let's try to play the file
            try:
                sound = pygame.mixer.Sound(filetoplay)
                # Play only if sound is set
                if sound:
                    # Set volume to defined setting and play
                    Volume = round(float(self.SoundVolume) / 100, 1)
                    sound.set_volume(Volume)
                    sound.play()
                    return True
                else:
                    return False
            except:
                if PlayDefIfNotFound:
                    self.Logs.Log("WARNING", "Unable to load audio while trying to play file : {}".format(filetoplay))
                return False

    #
    # Set sound volume
    #
    def AdjustVolume(self, key):
        if key == 'VOLUME-DOWN' or key == '-':
            diff = -5
        elif key == 'VOLUME-UP' or key == '+':
            diff = 5
        self.SoundVolume += diff
        if self.SoundVolume < 0:
            self.SoundVolume = 0
        elif self.SoundVolume > 100:
            self.SoundVolume = 100
        self.Logs.Log("DEBUG", "Volume level is now {}".format(self.SoundVolume))
        self.PlaySound()
        return True

    #
    # Play player name at the begining of a round (priority : personnal sound / speech / beep)
    #
    def SoundStartRound(self, Player):
        # Try to play User Sound (user.ogg in the .pydarts directory)
        UserSound = self.PlaySound(Player, False)
        # If it fail, try to generate sound with text-to-speech
        if not UserSound:
            UserSpeech = self.Speech(str(Player))
            if not UserSpeech:
                self.PlaySound()

    #
    # Play Winner at the end of the Game (priority : personnal sound / speech / "you")
    #
    def SoundEndGame(self, Player):
        self.PlaySound('winneris', False)
        pygame.time.wait(2000)
        UserSound = self.PlaySound(Player, False)
        if not UserSound:
            UserSpeech = self.Speech(str(Player))
            if not UserSpeech:
                self.PlaySound('you', False)

    #
    # Method to play sound for double, triple and bullseye
    #
    def Sound4Touch(self, Touch):
        if Touch == "DB":
            self.PlaySound('doublebullseye')
        elif Touch == "SB":
            self.PlaySound('bullseye')
        else:
            self.PlaySound(Touch)

    #
    # Check the right path of a requested file in prefered order : preference path, then pydarts path. return good path of False if path doesn't exists
    #
    def GetPathOfFile(self, filefolder, filename):
        if sys.platform=='win':separator="\\"
        else: separator="/"
        # Set path for user and pygame
        pathuser = '{}{}.pydarts{}{}{}{}'.format(os.path.expanduser('~'),separator, separator, filefolder, separator, filename)
        pathpydarts = '{}{}{}'.format(filefolder, separator, filename)
        # Check if file exists in user preferences path
        if os.path.isfile(pathuser):
            return pathuser
        # Else checks if exists in default pydatrs game path
        elif os.path.isfile(pathpydarts):
            return pathpydarts
        # Else it's a real problem ! Returns false
        else:
            return False

    #
    # Nice hit animation
    #
    def NiceShot(self, msg='Nice Shot !'):
        # Image size
        ImgW = int(self.res['x'] / 3)
        ImgH = int(self.res['y'] / 8)
        # Image movement  step
        step = int(self.res['x'] / 10)
        # Time between images
        time = 20
        # Placement
        X = 0 - ImgW
        Y = int(self.res['y'] / 2.4)
        self.PlaySound('niceshot')
        while X < int(self.res['x'] - ImgW):
            X += step
            self.DisplayBackground()
            self.DisplayImage(self.GetPathOfFile('images', 'dart1.png'), X, Y, ImgW, ImgH)
            self.UpdateScreen()
            pygame.time.wait(time)
            self.DisplayBackground()
            self.DisplayImage(self.GetPathOfFile('images', 'dart2.png'), X, Y, ImgW, ImgH)
            self.UpdateScreen()
            pygame.time.wait(time)
        self.InfoMessage([msg], 3000, None, 'middle', 'big')

    #
    # Display message for network version mismatch (only for major versions : exemple 1.0.1 and 1.0.9 are supposed to be compatibles)
    #
    def VersionCheck(self, serverversion):
        if serverversion[:3] != self.Config.pyDartsVersion[:3]:
            self.Logs.Log('ERROR',
                          'Version of client ({}) and server ({}) do not match. This is strongly discouraged ! Please upgrade !'.format(
                              self.Config.pyDartsVersion, serverversion))
            self.InfoMessage([self.Lang.lang('version-mismatch')], 8000, None, 'middle', 'big')
        else:
            self.Logs.Log('DEBUG','Version of client ({}) and server ({}) are supposed to be compatible. Continuing...'.format(self.Config.pyDartsVersion, serverversion))

    #
    # Draw board Methods
    #
    def Drawtriple(self, AngleIndex, color=None):
        color = self.ColorSet['green'] if color == None else color
        radius_triple_out = int(min(self.res['y'], self.res['x']) / 5.3)
        width_triple = min(int(self.res['y'] / 38), int(self.res['x'] / 38))
        arcRect = ((self.res['x'] - (radius_triple_out * 2)) / 2, (self.res['y'] - (radius_triple_out * 2)) / 2,
                   radius_triple_out * 2, radius_triple_out * 2)
        pygame.draw.arc(self.screen, color, arcRect, math.radians(18 * 6.5 - 18 * (AngleIndex + 1)),
                        math.radians(18 * 6.5 - 18 * AngleIndex), width_triple)

    #
    def Drawdouble(self, AngleIndex, color=None):
        color = self.ColorSet['blue'] if color == None else color
        radius_double_out = int(min(self.res['y'], self.res['x']) / 3.3)
        width_double = min(int(self.res['y'] / 35), int(self.res['x'] / 35))
        arcRect = ((self.res['x'] - (radius_double_out * 2)) / 2, (self.res['y'] - (radius_double_out * 2)) / 2,
                   radius_double_out * 2, radius_double_out * 2)
        pygame.draw.arc(self.screen, color, arcRect, math.radians(18 * 6.5 - 18 * (AngleIndex + 1)),
                        math.radians(18 * 6.5 - 18 * AngleIndex), width_double)

    #
    def Drawsimple(self, AngleIndex, color=None):
        color = self.ColorSet['black'] if color == None else color
        radius_double_in = int(min(self.res['y'], self.res['x']) / 3.65)
        radius_triple_in = int(min(self.res['y'], self.res['x']) / 6)
        width_simple1 = min(int(self.res['y'] / 12), int(self.res['x'] / 12))
        width_simple2 = min(int(self.res['y'] / 8), int(self.res['x'] / 8))
        arcRect1 = ((self.res['x'] - (radius_double_in * 2)) / 2, (self.res['y'] - (radius_double_in * 2)) / 2,
                    radius_double_in * 2, radius_double_in * 2)
        arcRect2 = ((self.res['x'] - (radius_triple_in * 2)) / 2, (self.res['y'] - (radius_triple_in * 2)) / 2,
                    radius_triple_in * 2, radius_triple_in * 2)
        pygame.draw.arc(self.screen, color, arcRect1, math.radians(18 * 6.5 - 18 * (AngleIndex + 1)),
                        math.radians(18 * 6.5 - 18 * AngleIndex), width_simple1)
        pygame.draw.arc(self.screen, color, arcRect2, math.radians(18 * 6.5 - 18 * (AngleIndex + 1)),
                        math.radians(18 * 6.5 - 18 * AngleIndex), width_simple2)

    #
    def Drawbull(self, Simple=False, Double=False, color=None):
        color = self.ColorSet['red'] if color == None and Double else color
        color = self.ColorSet['orange'] if color == None and Simple else color
        width_simple = min(int(self.res['y'] / 30), int(self.res['x'] / 30))
        width_double = min(int(self.res['y'] / 60), int(self.res['x'] / 60))
        radius_center_out = int(min(self.res['y'], self.res['x']) / 22)
        radius_center_in = int(min(self.res['y'], self.res['x']) / 50)
        if Simple:
            pygame.draw.circle(self.screen, color, (int(self.res['x'] / 2), int(self.res['y'] / 2)), radius_center_out,width_simple)
        if Double:
            pygame.draw.circle(self.screen, color, (int(self.res['x'] / 2), int(self.res['y'] / 2)), radius_center_in,width_double)

    def Support(self):
        timeout=10000
        # Titles
        self.MenuHeader(self.Lang.lang('Support menu'))
        self.InfoMessage([self.Lang.lang('Please wait')])
        try:
            # Launch shell script
            self.child = pexpect.spawn('scripts/dwagent.sh', timeout=timeout, encoding='utf-8', ignore_sighup=True)
            self.child.timeout=timeout
            # Redirect output to stdout
            self.child.logfile = sys.stdout
            # Wait that option prompt is displayed
            self.child.expect('Option.*: ')
            # Sleep half a second
            time.sleep(0.5)
            # Send key "2" for "Run"
            self.child.sendline('2')
            # Expect first CTRL+C output
            self.child.expect('.*CTRL.*')
            # Eventually expect second CTRL+C output
            try:
                self.child.expect('CTRL.*')
            except:
                self.Logs.Log("WARNING", "Only one CTRL flag has been found by expect in output and timeout reached".format(e))
            # Get output
            out=self.child.before
            #
            lines = out.splitlines()
            # Get username and password from output
            for line in lines:
                if self.Lang.lang('Username') in line:
                    user=line.split(' : ')[1]
                if self.Lang.lang('Password') in line:
                    pwd=line.split(' : ')[1]
            self.Logs.Log("DEBUG", "Please provide username ({}) {} and password ({}) {} to support team !".format(self.Lang.lang('Username'),user,self.Lang.lang('Password'),pwd))
            msg=self.Lang.lang('Support code') + ":" + user + " "+self.Lang.lang('and')+" " + pwd
            self.InfoMessage([msg], 0, None, 'middle', 'big')
            K = self.Inputs.ListenInputs([], ['escape', 'enter', 'space', 'TOGGLEFULLSCREEN'],[])
        except Exception as e:
            self.Logs.Log("ERROR", "Unable to launch dwservice agent on this host. Please enable debug to know more.")
            self.Logs.Log("DEBUG", "Error was : {}".format(e))
        

