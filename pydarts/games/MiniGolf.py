# -*- coding: utf-8 -*-
"""
MiniGolf game for pyDarts V2 layout.

Dart segment → direction of the golf shot (angle from board position).
Bull (SB/DB) → perfect aim toward the hole.

Coordinates are floats in [0..1] relative to the game rect.
Animation: ball slides smoothly with ease-out deceleration over ~3 seconds.
           If it passes over the hole during travel, it falls in.
"""

import math
import pygame

# ---------------------------------------------------------------------------
# Segment → direction
# ---------------------------------------------------------------------------
_ORDER = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
SEGMENT_ANGLE = {num: i * 18.0 for i, num in enumerate(_ORDER)}  # 0° = top


def segment_to_direction(segment_key):
    """Return (dx, dy) unit vector or None for bull keys."""
    key = segment_key.upper()
    if key in ('SB', 'DB', '25', '50'):
        return None  # Bull: aim at hole

    prefix = key[0] if key[0] in ('S', 'T', 'D') else ''
    num_str = key[len(prefix):] if prefix else key
    try:
        num = int(num_str)
    except ValueError:
        return None

    if num not in SEGMENT_ANGLE:
        return None

    rad = math.radians(SEGMENT_ANGLE[num])
    return (math.sin(rad), -math.cos(rad))   # pygame: y down


# ---------------------------------------------------------------------------
# Level data  (positions/sizes in [0..1] relative to game rect)
# ---------------------------------------------------------------------------
LEVELS = [
    {
        # Narrow corridor: walls on both sides, one-way gate to the green.
        # Ball enters the green from below through the gap; gate prevents exit.
        #
        #  y=0.03 ┌──────────────── GREEN ─────────────────┐
        #         │              [HOLE]                    │
        #  y=0.26 ├────────[==]──────────────[==]──────────┤  ← one-way gate (gap at center)
        #         │        │    COULOIR       │             │
        #         │        │                 │             │
        #  y=0.87 │        │   ● start       │             │
        #         └────────┴─────────────────┴─────────────┘
        'name': 'Le Couloir',
        'par': 3,
        'start': (0.50, 0.85),
        'hole':  (0.50, 0.14),
        'obstacles': [
            # Wall blocks on each side — corridor from x=0.33 to x=0.67.
            {'type': 'wall',         'rect': (0.03, 0.30, 0.30, 0.67)},   # left block
            {'type': 'wall',         'rect': (0.67, 0.30, 0.30, 0.67)},   # right block
            # One-way gate (corridor width only): passes going UP, bounces going DOWN.
            {'type': 'one_way_down', 'rect': (0.33, 0.25, 0.34, 0.05)},
            # Obstacle in the corridor (offset to force a slight angle)
            {'type': 'wall',         'rect': (0.44, 0.52, 0.12, 0.04)},
        ],
    },
    {
        'name': 'Le Dogleg',
        'par': 3,
        'start': (0.15, 0.80),
        'hole':  (0.85, 0.20),
        'obstacles': [
            {'type': 'wall',  'rect': (0.10, 0.45, 0.55, 0.08)},
            {'type': 'wall',  'rect': (0.65, 0.45, 0.08, 0.40)},
            {'type': 'water', 'rect': (0.10, 0.55, 0.55, 0.15)},
        ],
    },
    {
        'name': "L'Ile",
        'par': 3,
        'start': (0.10, 0.50),
        'hole':  (0.90, 0.50),
        'obstacles': [
            {'type': 'water', 'rect': (0.20, 0.15, 0.60, 0.25)},
            {'type': 'water', 'rect': (0.20, 0.60, 0.60, 0.25)},
            {'type': 'wall',  'rect': (0.42, 0.38, 0.16, 0.24)},
        ],
    },
]

# ---------------------------------------------------------------------------
# Physics constants
# ---------------------------------------------------------------------------
POWER       = 0.50   # shot travel distance (fraction of game rect)
HOLE_RADIUS = 0.04   # ball captured when closer than this
BALL_RADIUS = 0.018
EPSILON     = 0.002  # stop just before wall
MARGIN      = 0.03   # course boundary (ball bounces off this)


def _ray_rect_t_normal(px, py, dx, dy, rx, ry, rw, rh):
    """
    Return (t, axis) of first intersection of ray with AABB, or (None, None).
    axis is 'x' (reflect dx) or 'y' (reflect dy).
    """
    t_min_x = t_min_y = -float('inf')
    t_max_x = t_max_y =  float('inf')

    if abs(dx) > 1e-9:
        t1, t2 = (rx - px) / dx, (rx + rw - px) / dx
        t_min_x, t_max_x = (t1, t2) if t1 < t2 else (t2, t1)
    else:
        if not (rx <= px <= rx + rw):
            return None, None

    if abs(dy) > 1e-9:
        t1, t2 = (ry - py) / dy, (ry + rh - py) / dy
        t_min_y, t_max_y = (t1, t2) if t1 < t2 else (t2, t1)
    else:
        if not (ry <= py <= ry + rh):
            return None, None

    t_enter = max(t_min_x, t_min_y)
    t_exit  = min(t_max_x, t_max_y)

    if t_enter > t_exit or t_exit < 0 or t_enter < 0:
        return None, None

    axis = 'x' if t_min_x >= t_min_y else 'y'
    return t_enter, axis


def move_ball(bx, by, dx, dy, power, obstacles):
    """
    Compute the full ball path after a shot, with bouncing off both
    border walls and obstacle walls.
    Returns (end_x, end_y, path, hit_water) where path is a list of
    (x,y) waypoints including start and end (and each bounce point).
    """
    remaining = power
    x, y = bx, by
    path = [(x, y)]

    for _ in range(16):   # max segments (bounces)
        if remaining <= EPSILON:
            break

        candidates = []

        # Obstacle walls → bounce (reflect off hit face)
        for obs in obstacles:
            otype = obs['type']
            if otype == 'wall':
                pass  # always active
            elif otype == 'one_way_down' and dy <= 0:
                continue  # ball going up: pass through
            elif otype not in ('wall', 'one_way_down'):
                continue
            rx, ry, rw, rh = obs['rect']
            t, axis = _ray_rect_t_normal(x, y, dx, dy, rx, ry, rw, rh)
            if t is not None and t > EPSILON:
                candidates.append((t - EPSILON, 'obs_' + axis))

        # Course borders → bounce
        if abs(dx) > 1e-9:
            t_bx = (MARGIN - x) / dx if dx < 0 else (1 - MARGIN - x) / dx
            if t_bx > EPSILON:
                candidates.append((t_bx, 'border_x'))
        if abs(dy) > 1e-9:
            t_by = (MARGIN - y) / dy if dy < 0 else (1 - MARGIN - y) / dy
            if t_by > EPSILON:
                candidates.append((t_by, 'border_y'))

        near = [(t, h) for t, h in candidates if t <= remaining]
        if near:
            t_best, hit = min(near, key=lambda c: c[0])
        else:
            t_best, hit = remaining, None

        x += dx * t_best
        y += dy * t_best
        remaining -= t_best

        if hit in ('obs_x', 'border_x'):
            dx = -dx
            path.append((x, y))
        elif hit in ('obs_y', 'border_y'):
            dy = -dy
            path.append((x, y))
        else:
            break   # no hit — full distance done

    x = max(MARGIN, min(1 - MARGIN, x))
    y = max(MARGIN, min(1 - MARGIN, y))
    path.append((x, y))

    # Deduplicate
    clean = [path[0]]
    for p in path[1:]:
        if math.hypot(p[0]-clean[-1][0], p[1]-clean[-1][1]) > 1e-6:
            clean.append(p)

    hit_water = any(
        obs['type'] == 'water'
        and obs['rect'][0] <= x <= obs['rect'][0] + obs['rect'][2]
        and obs['rect'][1] <= y <= obs['rect'][1] + obs['rect'][3]
        for obs in obstacles
    )

    total = sum(
        math.hypot(clean[i+1][0]-clean[i][0], clean[i+1][1]-clean[i][1])
        for i in range(len(clean)-1)
    )
    return x, y, clean, total, hit_water


# ---------------------------------------------------------------------------
# Animation
# ---------------------------------------------------------------------------
ANIM_DURATION = 1.5   # seconds for full-power shot


class _Anim:
    """
    Ball travel animation following a multi-segment bouncing path.
    path    : list of (x,y) waypoints from move_ball()
    travel  : total path length
    """

    def __init__(self, pid, path, travel, event):
        self.pid          = pid
        self.path         = path
        self.result_event = event
        self.elapsed      = 0.0
        self.done         = False

        # Segment lengths for proportional time allocation
        self.seg_lens = [
            math.hypot(path[i+1][0]-path[i][0], path[i+1][1]-path[i][1])
            for i in range(len(path)-1)
        ]
        self.total = max(sum(self.seg_lens), 1e-6)
        self.duration = max(ANIM_DURATION * (travel / POWER), 0.1)

    def advance(self, dt):
        if self.done:
            return
        self.elapsed = min(self.elapsed + dt, self.duration)
        if self.elapsed >= self.duration:
            self.done = True

    def current_pos(self):
        """Ease-out quadratic along the waypoint path."""
        t_global = self.elapsed / self.duration
        t_eased  = 1.0 - (1.0 - t_global) ** 2
        dist_target = t_eased * self.total

        accumulated = 0.0
        for i, seg_len in enumerate(self.seg_lens):
            if accumulated + seg_len >= dist_target or i == len(self.seg_lens) - 1:
                frac = (dist_target - accumulated) / seg_len if seg_len > 1e-9 else 0.0
                frac = max(0.0, min(1.0, frac))
                ax, ay = self.path[i]
                bx, by = self.path[i+1]
                return (ax + frac * (bx - ax), ay + frac * (by - ay))
            accumulated += seg_len

        return self.path[-1]

    def check_hole(self, hole_pos):
        """Snap to hole and finish if ball passes over it."""
        if self.result_event == 'hole' or self.done:
            return False
        cx, cy = self.current_pos()
        hx, hy = hole_pos
        if math.hypot(cx - hx, cy - hy) < HOLE_RADIUS:
            # Truncate path at current position
            cur = self.current_pos()
            self.path = self.path[:1] + [cur, hole_pos]
            self.seg_lens = [
                math.hypot(self.path[i+1][0]-self.path[i][0],
                           self.path[i+1][1]-self.path[i][1])
                for i in range(len(self.path)-1)
            ]
            self.total    = max(sum(self.seg_lens), 1e-6)
            self.result_event = 'hole'
            self.done = True
            return True
        return False


# ---------------------------------------------------------------------------
# Game
# ---------------------------------------------------------------------------
class MiniGolfGame:
    DARTS_PER_TURN = 3

    def __init__(self, players):
        self.players    = players
        self.nb_players = len(players)
        self.current_hole = 0
        self.scores     = {p.ident: [] for p in players}
        self._anim      = None
        self._pending_finalize = None   # queued finalize after animation ends
        self._init_hole()

    # ------------------------------------------------------------------
    def _init_hole(self):
        sx, sy = self.level['start']
        self.ball_pos         = {p.ident: (sx, sy) for p in self.players}
        self.shots            = {p.ident: 0         for p in self.players}
        self.hole_done        = {p.ident: False      for p in self.players}
        self.turn_order       = [p.ident for p in self.players]
        self.current_turn_idx = 0
        self.darts_this_turn  = 0
        self._anim            = None
        self._pending_finalize = None

    @property
    def level(self):
        return LEVELS[self.current_hole % len(LEVELS)]

    @property
    def active_player_ident(self):
        return self.turn_order[self.current_turn_idx]

    @property
    def is_animating(self):
        return self._anim is not None and not self._anim.done

    # ------------------------------------------------------------------
    def _next_turn(self):
        for _ in range(self.nb_players):
            self.current_turn_idx = (self.current_turn_idx + 1) % self.nb_players
            self.darts_this_turn  = 0
            if not self.hole_done[self.turn_order[self.current_turn_idx]]:
                return
        self._end_hole()

    def _end_hole(self):
        par = self.level['par']
        for pid in self.turn_order:
            taken = self.shots[pid] if self.hole_done[pid] else par + 3
            self.scores[pid].append(taken)
        self.current_hole += 1
        self._init_hole()

    # ------------------------------------------------------------------
    def process_segment(self, segment_key):
        """Start a shot animation. Returns immediately; animation plays in render()."""
        if self.is_animating:
            return {'event': 'busy'}

        pid = self.active_player_ident
        if self.hole_done[pid]:
            self._next_turn()
            return {'event': 'already_done'}

        bx, by = self.ball_pos[pid]
        hx, hy = self.level['hole']

        # Direction
        is_bull = segment_key.upper() in ('SB', 'DB', '25', '50')
        if is_bull:
            dist = math.hypot(hx - bx, hy - by)
            dx, dy = ((hx-bx)/dist, (hy-by)/dist) if dist > 1e-6 else (0, -1)
        else:
            direction = segment_to_direction(segment_key)
            if direction is None:
                return {'event': 'invalid'}
            dx, dy = direction

        # Physics — returns full bouncing path
        nx, ny, path, travel, hit_water = move_ball(bx, by, dx, dy, POWER,
                                                    self.level['obstacles'])
        event = 'water' if hit_water else 'ok'

        # Start animation along the computed path
        self._anim = _Anim(pid, path, travel, event)

        # Store what to finalize when animation ends
        self._pending_finalize = {
            'pid':       pid,
            'from_pos':  (bx, by),
            'dest':      (nx, ny),
            'event':     event,
            'hit_water': hit_water,
        }

        self.shots[pid] += 1
        self.darts_this_turn += 1

        return {'event': 'animating', 'player': pid}

    def _finalize(self, final_event):
        """Called when animation ends. Updates ball_pos and advances turn."""
        pf = self._pending_finalize
        if pf is None:
            return
        pid = pf['pid']

        if final_event == 'hole':
            self.ball_pos[pid] = self.level['hole']
            self.hole_done[pid] = True
        elif pf['hit_water']:
            self.ball_pos[pid] = pf['from_pos']   # reset on water
        else:
            self.ball_pos[pid] = pf['dest']

        # Advance turn if darts exhausted or hole done
        if self.darts_this_turn >= self.DARTS_PER_TURN or self.hole_done[pid]:
            self._next_turn()

        self._pending_finalize = None
        self._anim = None

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def render(self, screen, rect, colorset, dt=0.0):
        """Draw current hole into `rect`. Pass dt (seconds) each frame."""
        r  = rect
        ox, oy = r.x, r.y

        def px(rx, ry):
            return int(ox + rx * r.width), int(oy + ry * r.height)

        def obs_rect(o):
            rx, ry, rw, rh = o['rect']
            return pygame.Rect(int(ox + rx*r.width), int(oy + ry*r.height),
                               int(rw*r.width),       int(rh*r.height))

        # --- Advance animation ---
        if self._anim:
            self._anim.advance(dt)
            sank = self._anim.check_hole(self.level['hole'])
            if self._anim.done:
                final_event = self._anim.result_event
                self._finalize(final_event)

        # --- Background (rough / hors-piste) ---
        pygame.draw.rect(screen, (60, 40, 10), r)

        # --- Course fairway (délimitée par MARGIN) ---
        fairway = pygame.Rect(
            int(r.x + MARGIN * r.width),
            int(r.y + MARGIN * r.height),
            int((1 - 2*MARGIN) * r.width),
            int((1 - 2*MARGIN) * r.height),
        )
        pygame.draw.rect(screen, (34, 120, 34), fairway)
        pygame.draw.rect(screen, (20, 80, 20), fairway, max(2, int(MARGIN * r.width * 0.3)))

        # --- Level label ---
        sq = min(r.width, r.height)
        try:
            font_sm = pygame.font.Font('fonts/Purisa.ttf', max(int(sq * 0.038), 12))
        except Exception:
            font_sm = pygame.font.SysFont(None, max(int(sq * 0.038), 12))

        lbl = font_sm.render(
            "Trou %d/%d — %s  (par %d)" % (
                self.current_hole + 1, len(LEVELS),
                self.level['name'], self.level['par']),
            True, (220, 220, 220))
        screen.blit(lbl, (r.x + 8, r.y + 6))

        # --- Obstacles ---
        for obs in self.level['obstacles']:
            pr = obs_rect(obs)
            if obs['type'] == 'wall':
                pygame.draw.rect(screen, (80, 50, 20), pr)
                pygame.draw.rect(screen, (60, 35, 10), pr, 2)
            elif obs['type'] == 'water':
                pygame.draw.rect(screen, (30, 80, 180), pr)
                pygame.draw.rect(screen, (20, 60, 150), pr, 2)
            elif obs['type'] == 'one_way_down':
                # Draw as a green bar with upward arrows (entry direction)
                pygame.draw.rect(screen, (20, 160, 20), pr)
                pygame.draw.rect(screen, (10, 120, 10), pr, 2)
                # Arrows pointing up (↑) spaced along the gate
                arrow_spacing = max(pr.width // 5, 1)
                cy_arrow = pr.centery
                for ax in range(pr.left + arrow_spacing, pr.right, arrow_spacing):
                    ah = max(pr.height // 2, 3)
                    pygame.draw.line(screen, (255, 255, 255),
                                     (ax, cy_arrow + ah), (ax, cy_arrow - ah), 2)
                    pygame.draw.polygon(screen, (255, 255, 255), [
                        (ax,       cy_arrow - ah),
                        (ax - ah//2, cy_arrow),
                        (ax + ah//2, cy_arrow),
                    ])

        # --- Trail: path drawn up to current animated ball position ---
        if self._anim and self._anim.seg_lens:
            t_raw    = self._anim.elapsed / self._anim.duration
            t_eased  = 1.0 - (1.0 - t_raw) ** 2
            dist_tgt = t_eased * self._anim.total
            trail_c  = (255, 80, 80) if self._anim.result_event == 'water' \
                       else (255, 255, 150)
            accumulated = 0.0
            for i, seg_len in enumerate(self._anim.seg_lens):
                a = self._anim.path[i]
                b = self._anim.path[i+1]
                if accumulated + seg_len <= dist_tgt:
                    pygame.draw.line(screen, trail_c, px(*a), px(*b), 2)
                    accumulated += seg_len
                else:
                    frac = ((dist_tgt - accumulated) / seg_len) if seg_len > 1e-9 else 0
                    mid  = (a[0] + frac*(b[0]-a[0]), a[1] + frac*(b[1]-a[1]))
                    pygame.draw.line(screen, trail_c, px(*a), px(*mid), 2)
                    break

        # --- Hole ---
        hpx, hpy = px(*self.level['hole'])
        hole_r = max(int(HOLE_RADIUS * r.width), 6)
        pygame.draw.circle(screen, (10, 10, 10), (hpx, hpy), hole_r)
        pygame.draw.circle(screen, (200, 200, 200), (hpx, hpy), hole_r, 2)
        flag_h = int(sq * 0.08)
        pygame.draw.line(screen, (200, 200, 200), (hpx, hpy), (hpx, hpy - flag_h), 2)
        pygame.draw.polygon(screen, (220, 50, 50), [
            (hpx,                  hpy - flag_h),
            (hpx + int(sq*0.04),   hpy - int(flag_h*0.7)),
            (hpx,                  hpy - int(flag_h*0.4)),
        ])

        # --- Balls ---
        ball_r = max(int(BALL_RADIUS * r.width), 5)
        active = self.active_player_ident

        # Collect ball draw positions (animated or static)
        anim_pid = self._anim.pid if self._anim else None

        for p in self.players:
            if self.hole_done[p.ident]:
                continue

            if self._anim and p.ident == anim_pid:
                bx, by = self._anim.current_pos()
            else:
                bx, by = self.ball_pos[p.ident]

            bpx, bpy = px(bx, by)
            color = p.GetColor() or (200, 200, 200)
            is_active = (p.ident == active)
            r_draw = ball_r + 2 if is_active else ball_r
            pygame.draw.circle(screen, color, (bpx, bpy), r_draw)
            pygame.draw.circle(screen, (255, 255, 255), (bpx, bpy), r_draw, 2)

        # --- HUD: active player info ---
        for p in self.players:
            if p.ident == active:
                state = "animation..." if self.is_animating else \
                        "coup %d  (flechette %d/%d)" % (
                            self.shots[p.ident] + 1,
                            self.darts_this_turn + 1,
                            self.DARTS_PER_TURN)
                info = "%s — %s" % (p.PlayerName, state)
                info_s = font_sm.render(info, True, (255, 255, 150))
                screen.blit(info_s, (r.x + 8, r.y + r.height - info_s.get_height() - 8))
                break
