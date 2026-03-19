"""
Interactive test for MiniGolf + V2 layout.
Run from pydarts/ directory:  python ../test_minigolf.py

Keyboard controls (simulate dart hits):
  8 2 4 6  → directions (numpad-style: 8=up, 2=down, 4=left, 6=right)
  7 9 1 3  → diagonals
  B        → Bull (aim at hole)
  ESC      → quit
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pydarts'))

import pygame
pygame.init()

# --- Stubs ---
class FakeLogs:
    def Log(self, *a): pass

class FakeConfig:
    pyDartsVersion = "1.2.0-wifi"
    _data = {
        'sectionglobals':  {'fullscreen':'0','resx':'1280','resy':'720',
                            'colorset':'dark','onscreenbuttons':'0',
                            'nbcol':'3','soundvolume':'50'},
        'sectionadvanced': {'animationduration':'5','speech':'none'},
    }
    def GetValue(self, sec, key):
        return self._data.get(sec.lower(), {}).get(key.lower(), '0')

class FakeLang:
    def lang(self, k): return k

class FakePlayer:
    def __init__(self, ident, name, color):
        self.ident      = ident
        self.PlayerName = name
        self.score      = 0
        self.couleur    = color
        self.LSTColVal  = [('', 'txt', None)] * 3
    def GetScore(self):  return int(self.score)
    def GetColor(self):  return self.couleur

# --- Setup ---
from include import CScreen
from games.MiniGolf import MiniGolfGame, LEVELS

screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("MiniGolf V2 Test")

S = CScreen.CScreen(FakeConfig(), FakeLogs(), FakeLang())
S.res    = {'x': 1280, 'y': 720}
S.screen = screen

players = [
    FakePlayer(0, 'Alice',  (220, 100, 100)),
    FakePlayer(1, 'Bob',    (100, 200, 100)),
]

game = MiniGolfGame(players)
S.DefineConstantsV2(nbplayers=len(players))

# Key → segment mapping (for testing)
KEY_SEGS = {
    pygame.K_8: 'S20',  # up
    pygame.K_2: 'S3',   # down
    pygame.K_6: 'S6',   # right
    pygame.K_4: 'S11',  # left
    pygame.K_7: 'S20',  # up-left  (approx)
    pygame.K_9: 'S1',   # up-right
    pygame.K_1: 'S19',  # down-left
    pygame.K_3: 'S4',   # down-right
    pygame.K_b: 'SB',   # bull → aim at hole
    pygame.K_t: 'T20',  # triple 20
    pygame.K_d: 'D20',  # double 20
}

clock   = pygame.time.Clock()
message = "8=haut 2=bas 4=gauche 6=droite  B=bull  T=T20  D=D20"

running = True
while running:
    dt = clock.tick(60) / 1000.0   # seconds since last frame

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key in KEY_SEGS and not game.is_animating:
                seg = KEY_SEGS[event.key]
                result = game.process_segment(seg)
                message = "%s  [%s]" % (seg, result.get('event', '?'))
                print(message)

    # --- Sync fake player scores for panel ---
    for p in players:
        p.score = sum(game.scores[p.ident])
        shots_this_hole = game.shots[p.ident]
        for i in range(3):
            p.LSTColVal[i] = ('coup %d' % (i+1) if i < shots_this_hole else '', 'txt', None)

    # --- Draw ---
    screen.fill((20, 20, 20))
    S.DrawScoresPanel(players, actualplayer=game.active_player_ident)
    S.DrawRoundPanel(players,  actualplayer=game.active_player_ident)

    colorset = S.ColorSet
    S.DrawGameArea(render_callback=lambda r: game.render(screen, r, colorset, dt))

    pygame.display.flip()

pygame.quit()
