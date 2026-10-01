"""Frame generator for the tricolour beagle.

A medium hound: a short square body under a black blanket saddle, a thick flag tail carried up with a
white tip, white chest, belly and forelegs, tan thighs; the head by hand (a domed skull cut straight
down to the stop, a flat nose bridge, a square muzzle with a thick upper lip over a set-back jaw, a
white blaze from the forehead front widening into the muzzle, long round-tipped drop ears). Legs are
two rigid bones and a paw each, 2px (as the shiba's, see draft_shiba.leg_pixels), the lower bone white
so the joints show. assemble_beagle.py turns the result into sprites/beagle.json.

Usage: python3 tools/draft_beagle.py > /tmp/beagle-frames.json
"""
import json
import math

W, H = 52, 28
GROUND = H - 1
PX = 5

# ---- palette keys ------------------------------------------------------------------------------
# b/a/c: tan base/light/shade, K/H: black saddle and its sheen, E: ear (a deeper tan), w/x: white and
# its shade, d: mouth line, shut eye, e: nose, o/v: eye (top/bottom), r: blush, t: tongue, k/l:
# near/far upper hind leg (tan), p/q: near/far white lower leg and paw

# ---- the head (facing right) ---------------------------------------------------------------------
# 14x12. The forehead is cut straight from the crown down to the stop at the eye (bulged out, it read
# as a lump), the nose bridge runs flat to the nose; the blaze runs down the forehead front (a tan
# forehead front left beyond it read as the far ear standing up) and the white of the muzzle meets
# the tan cheek in a curve, sweeping back from under the eye to the jaw (a straight vertical edge
# looked cut with a knife); the jowl under the mouth tapers into the neck.
HEAD = [
    "...bbbbbb.....",
    "..bbbbbbbb....",
    ".bbbbbbbbw....",
    "EEbbbbbbbww...",
    "EEEbbbbobwwwwe",
    "EEEEbbbvbwwwwe",
    "EEEEbbbbwwwwww",
    "EEEEEbbwwwwwww",
    ".EEEEbbwdwwww.",
    ".EEEEEbwwddd..",
    "..EEEEbww.....",
    "...EEbbw......",
]
EYE = (7, 4)                     # in HEAD: the eye's top pixel
NOSE = (13, 4)                   # the nose's top pixel (1x2)
EAR_BASE = (2.0, 3.0)            # where the ear hangs from

BW, BH = 40, 20                  # the body canvas (head included), above the legs
TOP = 3                          # rows of room above the head (looking up, the tail)
BACK = 7 + TOP                   # the row of the back line
TRUNK = (5, 21)
HEAD_X, HEAD_Y = TRUNK[1] - 3, TOP
SADDLE = (TRUNK[0] + 1, TRUNK[1] - 5, 6)


def blank(w=W, h=H):
    return [['.'] * w for _ in range(h)]


def rows_of(g):
    return [''.join(r) for r in g]


def place(rows, ox, dy=0, g=None):
    """Put rows on the canvas with their bottom row on the ground (dy moves them up)."""
    g = g or blank()
    top = GROUND - len(rows) + 1 - dy
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.' and 0 <= top + y < H and 0 <= ox + x < W:
                g[top + y][ox + x] = ch
    return g


def put(g, rows, x0, y0):
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.' and 0 <= y0 + y < len(g) and 0 <= x0 + x < len(g[0]):
                g[y0 + y][x0 + x] = ch


def trunk(g, back=BACK, x0=TRUNK[0], x1=TRUNK[1], bottom=BH - 1, saddle=SADDLE):
    """The square trunk with a thick neck, the black saddle draped over the back like a blanket, the
    white chest down the front and the white belly underneath."""
    for x in range(x0, x1 + 1):
        bot = bottom if (x - x0 < 6 or x1 - x < 6) else bottom - 1
        top = back + (1 if x - x0 < 2 else 0)
        if x == x0:
            top, bot = back + 2, bot - 2
        if x == x1:
            top, bot = back + 1, bot - 1
        for y in range(top, bot + 1):
            g[y][x] = 'b'
    for y in range(back - 1, back + 4):                     # the neck
        for x in range(x1 - 6 + (back + 4 - y) // 2, x1 + 1 - (back + 4 - y) // 3):
            g[y][x] = 'b'
    sx0, sx1, depth = saddle
    for x in range(sx0, sx1 + 1):
        t = (x - sx0) / max(1, sx1 - sx0)
        d = round(depth * (0.45 + 0.55 * math.sin(math.pi * t) ** 0.6))
        ys = [y for y in range(len(g)) if g[y][x] != '.']
        for y in ys[:d]:
            g[y][x] = 'H' if y == ys[0] else 'K'
    for y in range(back + 3, bottom + 1):                   # white chest and belly
        xs = [x for x in range(len(g[0])) if g[y][x] != '.']
        if xs:
            for x in xs[-3:]:
                g[y][x] = 'w'
    for x in range(x0 + 3, x1 - 2):
        ys = [y for y in range(len(g)) if g[y][x] != '.']
        if ys and ys[-1] >= bottom - 2:
            g[ys[-1]][x] = 'w'
            if ys[-1] - 1 > back + 3 and x > x0 + 6:
                g[ys[-1] - 1][x] = 'w'


# the flag tail from the root on the rump: thick at the root (black under the saddle), tan, white tip
TAILS = {
    'up': [(0, 0), (0, -1), (-1, -2), (-1, -3), (-1, -4), (-1, -5), (0, -6), (0, -7)],
    'back': [(0, 0), (-1, -1), (-2, -2), (-3, -3), (-4, -3), (-5, -4), (-6, -5), (-7, -5)],   # swept back
    'fwd': [(0, 0), (0, -1), (0, -2), (0, -3), (1, -4), (1, -5), (2, -6), (2, -7)],          # tipped forward
    'lean': [(0, 0), (0, -1), (-1, -2), (-1, -3), (-2, -4), (-2, -5), (-2, -6), (-3, -7)],     # swaying back a little
    'out': [(0, 0), (-1, 0), (-2, -1), (-3, -1), (-4, -1), (-5, -2), (-6, -2), (-7, -2)],     # streaming out (run)
}


def tail(g, x, y, pose='up'):
    for i, (dx, dy) in enumerate(TAILS[pose]):
        flat = pose == 'out'
        for k in (0, 1, 2) if i < 3 else (0, 1) if i < 7 else (0,) if not flat else (0,):
            X, Y = (x + dx, y + dy + k) if flat else (x + dx + k, y + dy)
            if 0 <= Y < len(g) and 0 <= X < len(g[0]) and (g[Y][X] == '.' or i < 2):
                g[Y][X] = 'w' if i >= 6 else ('K' if i < 2 else 'b')


def body(head=None, hx=HEAD_X, hy=HEAD_Y, tail_pose='up', breath=False):
    g = [['.'] * BW for _ in range(BH)]
    trunk(g)
    put(g, head or HEAD, hx, hy)
    tail(g, TRUNK[0], BACK, tail_pose)
    rows = rows_of(g)
    if breath:                                               # the chest swells 1px
        rows = rows[1:BREATH_ROW] + [rows[BREATH_ROW]] + rows[BREATH_ROW:]
    return rows


BREATH_ROW = BACK + 5

# ---- legs: two rigid bones and a paw, 2px ----------------------------------------------------------
LEG_ROWS = 7
BONES = {'front': (4.6, 2.5), 'hind': (3.2, 3.9)}
# far hind, near hind (tan thighs, white hocks); the forelegs all white, the far pair a shade darker
LEGS = {'far_hind': (TRUNK[0] + 1, 'l', 'q'), 'near_hind': (TRUNK[0] + 4, 'k', 'p'),
        'far_front': (TRUNK[1] - 5, 'q', 'q'), 'near_front': (TRUNK[1] - 2, 'p', 'p')}
LEG_ORDER = ['far_hind', 'far_front', 'near_hind', 'near_front']
FRONT_FORMS = {'stand': (0, 0), 'reach': (16, 10), 'push': (-14, -22), 'lift': (-8, -105), 'fold': (-30, -125)}
HIND_FORMS = {'stand': (-18, 0), 'reach': (0, 12), 'push': (-40, -22), 'lift': (-10, 55), 'fold': (45, 105)}


def leg_pixels(kind, a1, a2):
    """{(x, y): is_white} for one leg whose top-left pixel is (0, 0)."""
    l1, l2 = BONES[kind]
    px = {}
    x = y = 0.0
    for bone, (ang, length) in enumerate(((a1, l1), (a2, l2))):
        sx, sy = math.sin(math.radians(ang)), math.cos(math.radians(ang))
        steps = int(length * 4)
        for i in range(steps + 1):
            t = length * i / steps
            X, Y = round(x + sx * t), int(y + sy * t)
            if Y < 0:
                continue
            flat = abs(ang) > 55
            for p in ((X, Y), (X, Y + 1) if flat else (X + 1, Y)):
                px[p] = px.get(p, False) or (bone == 1 and t > 0.6)
        x, y = x + sx * length, y + sy * length
    bottom = max(Y for _, Y in px)
    if bottom >= LEG_ROWS - 1:                       # standing on it: the toes point forward
        right = max(X for X, Y in px if Y == bottom)
        px[(right + 1, bottom)] = True
    return px


def with_legs(rows, poses=None, hind_dx=0):
    poses = poses or {}
    w = len(rows[0])
    g = [['.'] * w for _ in range(LEG_ROWS)]
    for name in LEG_ORDER:
        x0, fur, sock = LEGS[name]
        kind = 'hind' if 'hind' in name else 'front'
        if kind == 'hind':
            x0 += hind_dx
        form = poses.get(name, 'stand')
        forms = HIND_FORMS if kind == 'hind' else FRONT_FORMS
        a1, a2 = forms['lift' if form is None else form] if isinstance(form, (str, type(None))) else form
        for (X, Y), pale in leg_pixels(kind, a1, a2).items():
            if 0 <= Y < LEG_ROWS and 0 <= x0 + X < w:
                g[Y][x0 + X] = sock if pale else fur
    return list(rows) + [''.join(r) for r in g]


def grounded(rows):
    while rows and not rows[-1].strip('.'):
        rows = rows[:-1]
    return rows


# ---- the ears and the head turning (as the Labrador's) ------------------------------------------------
def pad_head(head, pad):
    G = [['.'] * (len(head[0]) + 2 * pad) for _ in range(len(head) + 2 * pad)]
    for y, r in enumerate(head):
        for x, ch in enumerate(r):
            if ch != '.':
                G[y + pad][x + pad] = ch
    return G


def ear_flapped(deg, head=None):
    """(rows, dx, dy): the ear turned deg degrees about its base (positive: the tip swings back and up,
    out behind the head; negative: forward). Where the ear lifts off the head the skull shows."""
    head = head or HEAD
    g = [list(r) for r in head]
    ear = {(x, y) for y, r in enumerate(head) for x, ch in enumerate(r) if ch == 'E'}
    ear_top = min(y for _, y in ear) if ear else 0
    for x, y in ear:                             # the skull behind the ear, inside the head's outline
        g[y][x] = 'b' if (y - ear_top <= 6 and x >= 2) else '.'
    pad = 8
    G = pad_head(g, pad)
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    bx, by = EAR_BASE[0], EAR_BASE[1] + ear_top - 3
    for Y in range(len(G)):
        for X in range(len(G[0])):
            x, y = X - pad - bx, Y - pad - by
            if (round(bx + x * ca + y * sa), round(by - x * sa + y * ca)) in ear:
                G[Y][X] = 'E'
    return rows_of(G), -pad, -pad


PIVOT = (4.0, 10.0)                      # in HEAD: the back of the jaw, where the neck joins
PAD = 6


def head_turned(deg, head=None, ear=0):
    """(rows, dx, dy): the whole head turned deg degrees about the back of the jaw (negative: muzzle
    up); the eye, the nose and the mouth line are redrawn whole at their turned places (turned pixel
    by pixel they broke up). ear swings the ear the other way on top. Not used for frames directly: the
    sniffing and howling heads were drawn by hand from its output."""
    head = head or HEAD
    if ear:
        rows, dx, dy = ear_flapped(ear, head)
        head = [r[-dx:len(r) + dx] for r in rows[-dy:len(rows) + dy]]
    h, w = len(head), len(head[0])
    src = {(x, y): ch for y, r in enumerate(head) for x, ch in enumerate(r) if ch != '.'}
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    px, py = PIVOT
    G = [['.'] * (w + 2 * PAD) for _ in range(h + 2 * PAD)]
    for Y in range(h + 2 * PAD):
        for X in range(w + 2 * PAD):
            x, y = X - PAD - px, Y - PAD - py
            ch = src.get((round(px + x * ca + y * sa), round(py - x * sa + y * ca)))
            if ch:
                G[Y][X] = ch
    fwd = lambda x, y: (round(PAD + px + (x - px) * ca - (y - py) * sa), round(PAD + py + (x - px) * sa + (y - py) * ca))
    for r in G:                                              # clear the broken eye, nose and mouth ...
        for X, ch in enumerate(r):
            if ch in 'ov':
                r[X] = 'b'
            elif ch in 'ed':
                r[X] = 'w'
    ex, ey = fwd(EYE[0], EYE[1] + 0.5)                       # ... and draw them whole
    G[ey - 1][ex], G[ey][ex] = 'o', 'v'
    nx, ny = fwd(NOSE[0] + 0.5, NOSE[1] + 1)
    G[ny - 1][nx], G[ny][nx] = 'e', 'e'
    for a0, b0 in (((8, 8), (9, 9)), ((9, 9), (11, 9))):     # the mouth line, redrawn straight
        (x0, y0), (x1, y1) = fwd(*a0), fwd(*b0)
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            G[round(y0 + (y1 - y0) * i / n)][round(x0 + (x1 - x0) * i / n)] = 'd'
    keep = largest_part(G)
    for Y, r in enumerate(G):
        for X in range(len(r)):
            if r[X] != '.' and (X, Y) not in keep:
                r[X] = '.'
    for _ in range(2):                                       # tidy the turned edge
        for Y in range(1, len(G) - 1):
            for X in range(1, len(G[0]) - 1):
                n = sum(G[Y + dy][X + dx] != '.' for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if G[Y][X] != '.' and n <= 1:
                    G[Y][X] = '.'
                elif G[Y][X] == '.' and n >= 3:
                    G[Y][X] = G[Y][X - 1] if G[Y][X - 1] != '.' else G[Y][X + 1]
    return rows_of(G), -PAD, -PAD


def largest_part(G):
    seen, best = set(), set()
    for Y, r in enumerate(G):
        for X, ch in enumerate(r):
            if ch == '.' or (X, Y) in seen:
                continue
            part, stack = set(), [(X, Y)]
            while stack:
                x, y = stack.pop()
                if (x, y) in part or not (0 <= y < len(G) and 0 <= x < len(G[0])) or G[y][x] == '.':
                    continue
                part.add((x, y))
                stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            seen |= part
            if len(part) > len(best):
                best = part
    return best


def filled(g, below=None):
    """Fill the gaps the outside cannot reach (rows from below on are left alone: the gap between a
    lifted leg and the others filled in and the legs merged into a white block)."""
    h, w = len(g), len(g[0])
    seen, stack = set(), [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or not (0 <= x < w and 0 <= y < h) or g[y][x] != '.':
            continue
        seen.add((x, y))
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    for y in range(h if below is None else min(h, below)):
        for x in range(w):
            if g[y][x] == '.' and (x, y) not in seen:
                g[y][x] = 'w' if y > BACK + 2 else 'b'
    return g


def body_with_head(rows_dx_dy, tail_pose='up', breath=False):
    head, dx, dy = rows_dx_dy
    rows = body(head, hx=HEAD_X + dx, hy=HEAD_Y + dy, tail_pose=tail_pose, breath=breath)
    g = [list(r) for r in rows]
    for y in range(1, len(g) - 1):                           # close a gap between the chin and the chest
        for x in range(HEAD_X, len(g[0]) - 1):
            if g[y][x] == '.' and g[y - 1][x] != '.' and g[y + 1][x] != '.' and g[y][x - 1] != '.':
                g[y][x] = 'w' if 'w' in (g[y + 1][x], g[y][x - 1]) else 'b'
    return rows_of(filled(g))


def stand_frames():
    out = {'stand': rows_of(place(with_legs(body()), PX))}
    out['idle_0'] = out['stand']
    out['idle_1'] = rows_of(place(with_legs(body(breath=True)), PX))
    return out


# ---- walking and running ---------------------------------------------------------------------------
# Walking: diagonal pairs together, no body bob; the ears swing a little each step, the tail sways.
STEP = ['reach', 'stand', 'push', None]
WALK_EARS = [0, 10, 0, 10]
WALK_TAILS = ['up', 'fwd', 'up', 'lean']
# the lifted paws fold less on the short beagle legs: folded right back, the lifted fore paw met the
# lifted hind paw swinging forward and the white legs closed into a loop
WALK_FRONT_LIFT = (8, -45)
WALK_HIND_LIFT = (-14, 30)


def walk_frames():
    out = {}
    for f in range(4):
        a, b = STEP[f], STEP[(f + 2) % 4]
        poses = {'near_hind': a or WALK_HIND_LIFT, 'far_front': a or WALK_FRONT_LIFT, 'far_hind': b or WALK_HIND_LIFT, 'near_front': b or WALK_FRONT_LIFT}
        rows = body_with_head(ear_flapped(WALK_EARS[f]), tail_pose=WALK_TAILS[f])
        out[f'walk_{f}'] = rows_of(place(with_legs(rows, poses), PX))
    return out


def flex(rows, d, at=12):
    """The spine flexing on the run: the rump and tail (columns before at) move d columns."""
    out = []
    for r in rows:
        rear, front = r[:at], r[at:]
        if d > 0:
            rear = '.' * d + rear[:-d]
        elif d < 0:
            rear = rear[-d:] + rear[-1] * -d
        out.append(rear + front)
    return out


# a dog's gallop (as the shiba's): the legs fold under and stretch out flat, the back flexes, the body
# rises 1px once a stride; the ears fly, the tail streams out behind
RUN = [
    ({'far_front': (20, 10), 'near_front': (10, 2), 'far_hind': (-70, -60), 'near_hind': (-58, -40)}, 0, 0),
    ({'far_front': (-20, -30), 'near_front': (-10, -18), 'far_hind': (10, 65), 'near_hind': (0, 40)}, 0, 1),
    ({'far_front': (-30, -115), 'near_front': (-40, -125), 'far_hind': (50, 105), 'near_hind': (40, 90)}, 0, 1),
    ({'far_front': (50, 30), 'near_front': (40, 15), 'far_hind': (18, 10), 'near_hind': (8, 2)}, 0, 0),
    ({'far_front': (70, 60), 'near_front': (60, 45), 'far_hind': (-32, -22), 'near_hind': (-22, -12)}, 0, -1),
    ({'far_front': (82, 80), 'near_front': (76, 70), 'far_hind': (-80, -80), 'near_hind': (-74, -68)}, 1, -1),
]
RUN_EARS = [-10, 20, 45, -10, 30, 55]


def run_frames():
    return {f'run_{f}': rows_of(place(with_legs(flex(body_with_head(ear_flapped(RUN_EARS[f]), tail_pose='out'), d), poses, d), PX, lift))
            for f, (poses, lift, d) in enumerate(RUN)}


# ---- head directions ---------------------------------------------------------------------------------
# The head tips on the neck: every column in front of the back of the skull moves up (or down) by its
# distance from there, so the muzzle swings most and the eye moves with it, the crown and the ears
# stay (turned by rotation, the 14px head lost its straight forehead and its stop, and the nose broke
# off). The ears swing a little the other way. Looking down, the chin row tucks away.
LOOK_TILTS = {'up_fwd': (-0.36, 12), 'down_fwd': (0.3, -8)}
LOOK_DIRS = list(LOOK_TILTS)
TILT_FROM = 4                                            # the column the head tips about


def head_tilted(k, head=None):
    """(rows, dx, dy): the head with column x moved round((x - TILT_FROM) * k) rows (k < 0: up)."""
    head = head or HEAD
    pad = 4
    G = [['.'] * len(head[0]) for _ in range(len(head) + 2 * pad)]
    for x in range(len(head[0])):
        d = round((x - TILT_FROM) * k) if x > TILT_FROM else 0
        for y, r in enumerate(head):
            if r[x] != '.':
                G[y + pad + d][x] = r[x]
    return rows_of(G), 0, -pad


def look_frames():
    out = {}
    for d, (k, ear) in LOOK_TILTS.items():
        rows, dx, dy = head_tilted(k, HEAD[:-1] if k > 0 else None)
        rows, ex, ey = ear_flapped(ear, rows)
        for i, breath in enumerate((False, True)):
            out[f'idle_{i}_{d}'] = rows_of(place(with_legs(body_with_head((rows, dx + ex, dy + ey), breath=breath)), PX))
    return out


# ---- turning toward the viewer ------------------------------------------------------------------
# Face-on, drawn as its left half and mirrored: a domed tan crown, the white blaze down the middle
# widening into the white muzzle, the eyes either side of it, the nose at the bottom of the muzzle,
# the long ears hanging at the sides of the face, the white chest and forelegs.
FRONT_HALF = [
    "....bbb",
    "..bbbbb",
    ".bbbbbb",
    "Ebbbbbw",
    "EEbbbbw",
    "EEbobbw",
    "EEbvbww",
    "EEbbwww",
    "EEbwwww",
    "EEbwwwe",
    "EEEwwwd",
    ".EEwwdd",
    ".EEwwww",
    "..Ebwww",
    "..bbwww",
    "..bbbww",
    "..bbbww",
]
TURN_FRONT = [h + h[::-1] for h in FRONT_HALF]
FRONT_LEGS = ["...pp....pp..."] * 6 + ["..ppp....ppp.."]


def turn_frames():
    """turn_a: the face-on head and chest over the side body's back half, with the forelegs under the
    face-on chest (the side body's forelegs left at one edge of it made the chest look as if it floated
    over nothing on the other side)."""
    side = with_legs(body(head=['.']), {})
    g = place(side, PX)
    top = GROUND - len(side) + 1
    fx = PX + HEAD_X - 2
    for y in range(GROUND - LEG_ROWS + 1, GROUND + 1):         # the side forelegs go
        for x in range(fx - 1, W):
            g[y][x] = '.'
    for y, r in enumerate(TURN_FRONT):
        for x, ch in enumerate(r):
            if ch != '.':
                g[top + HEAD_Y + y][fx + x] = ch
    for y, r in enumerate(FRONT_LEGS):                         # the forelegs under the face-on chest
        for x, ch in enumerate(r):
            if ch != '.':
                g[GROUND - LEG_ROWS + 1 + y][fx + x] = ch
    # face-on, centred on the anchor, the point the sprite is mirrored about: the face then steps evenly
    # from the three-quarter frame to the middle and on to the mirrored three-quarter frame (placed off
    # the anchor, it jumped sideways when the sprite flipped)
    fw = len(TURN_FRONT[0])
    return {'turn_a': rows_of(g), 'turn_b': rows_of(place(TURN_FRONT + FRONT_LEGS, ANCHOR[0] - fw // 2 + 1))}


# ---- sitting -------------------------------------------------------------------------------------
# The standing trunk shortened (seen from the side a sitting body is short) and sheared down toward the
# rump, so the back slopes down to the rump on the ground with the saddle still draped over it (drawn
# by hand, the saddle became a strap down the back; tipped by rotation, the chest swung out forward
# and the neck came off the head); the head upright over the chest, the white forelegs straight, the
# tan thigh folded at the side (lit on top, a shadow at the front) with the white hind paw forward on
# the ground, and the flag tail up behind the rump.
SIT_CUT = 4                                                # columns taken out behind the shoulder (out of the
                                                           # middle, the deepest part of the saddle went)
SIT_DROP = 9                                               # how far the rump comes down


def sit_rows(head=None):
    """head: (rows, dx, dy) in place of the stand head (tipped up or down, an ear flicked)."""
    g = [['.'] * BW for _ in range(BH)]
    trunk(g)
    x0, x1 = TRUNK
    cut = range(x1 - 5 - SIT_CUT, x1 - 5)
    cols = [x for x in range(BW) if x not in cut]
    Hs = BH + LEG_ROWS
    ground = Hs - 1
    G = [['.'] * BW for _ in range(Hs)]
    xf = x1 - 4                                            # the shoulder: nothing moves in front of it
    for i, x in enumerate(cols):
        X = i + SIT_CUT                                    # keep the chest where it was
        d = round(SIT_DROP * min(1, (xf - x) / (xf - x0))) if x < xf else 0
        for y in range(BH):
            if g[y][x] != '.' and 0 <= X < BW and y + d <= ground:
                G[y + d][X] = g[y][x]
    hr, hdx, hdy = head or (HEAD, 0, 0)
    put(G, hr, HEAD_X + hdx, HEAD_Y + hdy)
    for x in (x1 - 4, x1 - 3, x1 - 1, x1):                 # the white forelegs, straight down from the chest
        ys = [y for y in range(Hs) if G[y][x] != '.']
        for y in range(ys[-1] + 1 if ys else BH, Hs):
            G[y][x] = 'p' if x >= x1 - 1 else 'q'
    G[ground][x1 + 1] = 'p'
    cx, cy, rx, ry = x1 - 9, ground - 3, 4, 3             # the folded thigh, behind the forelegs (over them,
                                                           # the far foreleg vanished into it)
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d <= 1:
                G[y][x] = 'c' if (d > 0.6 and x > cx) else ('a' if y < cy - 1 else 'b')
    for x in range(cx - 1, min(cx + 6, x1 - 5)):             # the white hind paw forward on the ground, short of
        G[ground][x] = 'p'                                 # the forelegs (touching them, the gap between the
    G[ground - 1][min(cx + 5, x1 - 6)] = 'p'                # forelegs filled in and they merged with the chest)
    rx0 = min(x for x in range(BW) if any(G[y][x] != '.' for y in range(Hs)))
    ty = min(y for y in range(Hs) if G[y][rx0 + 1] != '.')
    tail(G, rx0 + 1, ty, 'lean')
    return rows_of(filled(G))


# Sitting is not a statue: it breathes, lifts its nose to sniff the air (quick little twitches),
# flicks an ear; the eyes blink too (see assemble_beagle.BLINK). (Looking down at the ground as well
# was one move too many.)
SIT_HEADS = {
    'sit_0': (0, 0), 'sit_sniff_0': (-0.22, 6), 'sit_sniff_1': (-0.3, 6),
    'sit_ear': (0, 30),
}


def sit_frames():
    out = {}
    for name, (k, ear) in SIT_HEADS.items():
        rows, dx, dy = head_tilted(k, HEAD[:-1] if k > 0 else None) if k else (HEAD, 0, 0)
        if ear:
            rows, ex, ey = ear_flapped(ear, rows)
            dx, dy = dx + ex, dy + ey
        out[name] = rows_of(place(grounded(sit_rows((rows, dx, dy))), PX))
    out['sit_1'] = rows_of(place(breathe(grounded(sit_rows())), PX))
    out['sit_a'] = rows_of(place(sinking_rump(), PX))
    return out


def breathe(rows, at=None):
    at = at or BREATH_ROW
    return rows[1:at] + [rows[at]] + rows[at:]


def sinking_rump():
    """Halfway down: the hind legs fold and the rump sinks toward the ground, the chest stays up."""
    rows = with_legs(body(), {'far_hind': 'fold', 'near_hind': 'fold'})
    h, w = len(rows), len(rows[0])
    g = [['.'] * w for _ in range(h)]
    for x in range(w):
        d = 4 if x < 11 else 2 if x < 15 else 1 if x < 18 else 0
        for y in range(h - 1, -1, -1):
            if rows[y][x] != '.' and y + d < h:
                g[y + d][x] = rows[y][x]
    return rows_of(filled(g))


# ---- lying down ---------------------------------------------------------------------------------
# Belly down on the ground. Only the white forearms and paws show ahead of the chest (their top a
# shade darker so they stand off the white chest), the far paw beside the near one; the folded hind
# leg is a rounded tan thigh with its white paw forward under the belly.
def lie(rows):
    rows = [list(r) for r in rows]
    for y in range(BH - 3, BH):                            # lying, the white belly is underneath: the side shows tan
        for x in range(TRUNK[0] + 2, TRUNK[1] - 4):
            if rows[y][x] == 'w':
                rows[y][x] = 'c' if y == BH - 1 else 'b'
    g = place(rows_of(rows), PX, 1)
    xs = [x for x in range(W) if g[GROUND - 1][x] != '.']
    for x in range(min(xs) + 2, max(xs) - 4):              # the side resting on the ground, in shade
        g[GROUND][x] = 'c'
    FORE = [  # (dx from the chest's front, row from the ground, key); the far paw first, the near leg over it
        (5, 1, 'q'), (6, 1, 'q'), (4, 0, 'q'), (5, 0, 'q'), (6, 0, 'q'), (7, 0, 'q'),
        (-1, 1, 'q'), (0, 1, 'q'), (1, 1, 'q'), (2, 1, 'q'), (3, 1, 'p'), (4, 1, 'p'),
        (-1, 0, 'p'), (0, 0, 'p'), (1, 0, 'p'), (2, 0, 'p'), (3, 0, 'p'), (4, 0, 'p'), (5, 0, 'p'),
    ]
    chest = max(x for x in range(W) if g[GROUND - 2][x] != '.' and x < PX + TRUNK[1] + 3)
    for dx, up, ch in FORE:
        x, y = chest + dx, GROUND - up
        if 0 <= x < W and (g[y][x] == '.' or up < 2):
            g[y][x] = ch
    cx, cy, rx, ry = PX + 9, GROUND - 3, 5, 3             # the folded thigh, under the saddle; its back edge
    for y in range(cy - ry, cy + ry + 1):                  # stops at the rump (the ellipse's 1px tip sticking
        for x in range(cx - rx + 1, cx + rx + 1):          # out behind read as a pointed hock)
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d <= 1:
                g[y][x] = 'c' if (d > 0.6 and (x > cx or y > cy)) else ('a' if y < cy - 1 else 'b')
    for x in range(PX + 9, PX + 15):                       # the white hind paw forward under the belly, its
        g[GROUND][x] = 'c' if x == PX + 9 else 'p'         # toes a rounded 2x2 (one raised pixel at the tip
    for x in (PX + 13, PX + 14):                           # read as a pointed toe)
        g[GROUND - 1][x] = 'p'
    for y in range(GROUND - 3, GROUND + 1):                # close the gap under the belly
        xs = [x for x in range(W) if g[y][x] != '.']
        for x in range(min(xs), min(max(xs), PX + TRUNK[1])):
            if g[y][x] == '.' and any(g[y][k] != '.' for k in range(max(0, x - 8), x)) and any(g[y][k] != '.' for k in range(x + 1, min(W, x + 9))):
                g[y][x] = 'c'
    return rows_of(g)


def lie_frames():
    down = grounded(with_legs(body(), {n: 'fold' for n in LEGS}))[:-2]
    return {'lie_a': rows_of(filled([list(r) for r in rows_of(place(down, PX))])),
            'lie_0': lie(body()), 'lie_1': lie(body(breath=True))}


# ---- scent tracking ---------------------------------------------------------------------------------
# A hound on a trail: nose down on the ground, the neck stretched down in front of the chest, the long
# ears hanging to the ground beside the face (sweeping up the scent), the tail up like a flag and
# wagging; it walks slowly along the trail, the nose twitching as it sniffs.
# The head for sniffing is the stand head itself turned 35 degrees nose down (the turn redrawn by hand
# from head_turned): the round white muzzle, the eye and the blaze stay as they are, the ear hangs down
# the back of the head, the mouth line runs down the back of the muzzle. The chin comes down to the
# ground with the nose just above it. (A head redrawn pointing straight down read as a flat, broad face
# and needed a neck far too long; tipping the columns of the stand head bent the mouth line into steps.)
# Sniffing, the head bobs a pixel.
NOSE_DOWN = [
    "...bbbbb.....",
    ".EEbbbbbbb...",
    "EEEEbbbbbbb..",
    "EEEEbbbbbbb..",
    "EEEEbbbobbw..",
    "EEEEbbbvbww..",
    "EEEEbbbbwww..",
    "EEEEbwwwwww..",
    ".EEEbwwwwwwwe",
    "..EEwdwwwwwwe",
    "...Ewwdwwwww.",
    ".......dwww..",
]


def leg_reaching(kind, rows_down, lean=1, off=0):
    """Bone angles (off + lean * a, off - lean * a) that bend a leg until it reaches rows_down rows:
    off swings the whole leg forward (+) or back (-), the bend keeps the paw on the ground."""
    for a in range(0, 80, 2):
        px = leg_pixels(kind, off + lean * a, off - lean * a)
        if max(Y for _, Y in px) <= rows_down - 1:
            return off + lean * a, off - lean * a
    return off + 60 * lean, off - 60 * lean


# the bent forelegs step too (left still, they slid along the ground as the dog walked): planted ahead,
# under, behind, then lifted 2 rows and brought forward
FRONT_STEP = {'reach': (8, 0), 'stand': (0, 0), 'push': (-8, 0), None: (2, 1)}   # (swing, rows up)


FRONT_DROP = 1                    # how far the shoulders come down when the nose goes to the ground


def front_down(tail_pose='up', step=None):
    """The body with its forequarters lowered: the trunk tips forward (the back sloping down from the
    rump to the shoulders) on bent forelegs, the hind legs straight (with only the neck and head going
    down, the body stayed level and the neck stretched like a giraffe's). step: walk poses for the hind
    legs (the forelegs stay bent, stepping a little)."""
    rows = body(head=['.'], tail_pose=tail_pose)
    x0, x1 = TRUNK
    drop = lambda x: round(FRONT_DROP * max(0.0, min(1.0, (x - x0 - 4) / (x1 - x0 - 4))))
    Ht = BH + LEG_ROWS
    g = [['.'] * BW for _ in range(Ht)]
    for x in range(BW):
        d = drop(min(x, x1))
        for y in range(BH):
            if rows[y][x] != '.':
                g[y + d][x] = rows[y][x]
    step = step or {}
    for name in LEG_ORDER:
        x, fur, sock = LEGS[name]
        kind = 'hind' if 'hind' in name else 'front'
        d = drop(x + 1)
        if kind == 'hind':
            form = step.get(name, 'stand')
            a1, a2 = HIND_FORMS[form] if isinstance(form, str) else form
        else:
            off, up = FRONT_STEP[step.get(name, 'stand')]
            a1, a2 = leg_reaching('front', LEG_ROWS - d - up, lean=-1, off=off)   # the forearm slants back
        px = leg_pixels(kind, a1, a2)
        bottom = max(Y for _, Y in px)
        if kind == 'front' or bottom < LEG_ROWS - 1:
            if kind == 'hind' or bottom >= LEG_ROWS - d - 1 - FRONT_STEP[step.get(name, 'stand')][1]:
                right = max(X for X, Y in px if Y == bottom)
                px[(right + 1, bottom)] = True
        for (X, Y), pale in px.items():
            yy = BH + d + Y
            if 0 <= yy < Ht and 0 <= x + X < BW:
                g[yy][x + X] = sock if pale else fur
    return rows_of(filled(g, BH - 2))


def nose_down(rows, head=None, dx=0, lift=0):
    """rows (a body with legs, no head, forequarters lowered) with the head tipped down low in front of
    the chest, the chin on the ground, and a short neck from the lowered withers down to it."""
    head = head or NOSE_DOWN
    g = [list(r) for r in rows]
    h = len(g)
    x1 = TRUNK[1]
    hx, hy = x1 - 1 + dx, h - len(head) - lift
    top = BACK - 1 + FRONT_DROP
    for y in range(top, hy + 5):                              # the neck, from the lowered withers
        t = (y - top) / max(1, hy + 4 - top)
        xa = round(x1 - 5 + (hx + 1 - x1 + 5) * t)
        xb = round(x1 + 1 + (hx + 8 - x1 - 1) * t)
        for x in range(xa, min(xb, len(g[0]) - 1) + 1):
            if g[y][x] == '.' or (x > x1 and g[y][x] in 'wb'):
                g[y][x] = 'b'
    put(g, head, hx, hy)
    return rows_of(filled(g, BH - 2))


SCENT_TAILS = ['up', 'fwd', 'up', 'lean']


# a slow, short-stepped walk, diagonal pairs together as in walk_frames: the paws only just leave the
# ground (a lifted hind paw swung forward met the bent forelegs, the white outline filled the 1px gap
# between them and the legs merged into one white block)
SCENT_HIND_LIFT = (-20, 12)
SCENT_STEPS = []
for _f in range(4):
    _a, _b = STEP[_f], STEP[(_f + 2) % 4]
    SCENT_STEPS.append(({'near_hind': _a or SCENT_HIND_LIFT, 'far_front': _a, 'far_hind': _b or SCENT_HIND_LIFT, 'near_front': _b},
                        ['up', 'fwd', 'up', 'lean'][_f]))


def scent_frames():
    out = {}
    for f, (step, tail_pose) in enumerate(SCENT_STEPS):
        rows = front_down(tail_pose, step)
        out[f'scent_{f}'] = rows_of(place(nose_down(rows, lift=f % 2), PX))
    return out


# ---- the "aroo" howl -----------------------------------------------------------------------------------
# Sitting, the head thrown back with the muzzle pointing at the sky, the lips rounded into an O, the
# ears falling back off the face; the howl comes out in waves (sound marks rising from the nose) while
# the mouth opens and closes a little.
HOWL = [                          # the stand head turned 40 degrees muzzle up (redrawn by hand from
    "..........we.",              # head_turned): the same rounded muzzle, the nose at its tip, the stop a
    "...bbb...wwe.",              # notch between the crown and the bridge, the ear falling back; the lips
    "..bbbbwwwwww.",              # a little apart under the tip. (Drawn from scratch, the top of the
    ".bbbbbbwwwwww",              # muzzle met the nose in a right angle and the muzzle was too long.)
    "bbbbbbobwwwwd",
    "bbbbbbvbwwwdd",
    "bbbbbbbbwwwd.",
    "bbbbbbbwwww..",
    "EEEEbbbbwww..",
    "EEEEEEbbbww..",
    ".EEEEEEEEbw..",
    "..EEEEEEbb...",
    "....EEEEE....",
]
HOWL_OPEN = list(HOWL)
HOWL_OPEN[4] = "bbbbbbobwwwdd"                 # the O opens wider
HOWL_OPEN[5] = "bbbbbbvbwwdtd"
HOWL_OPEN[6] = "bbbbbbbbwwdd."
HOWL_DX = -2                                   # the turned head's back sits a little behind the stand head's


# The sound: pale arcs spreading out from the nose in the direction it points, clear of the mouth (little
# yellow humps right at the mouth read as spit), one ring nearer, the next further out. HOWL_MARKS 'none'
# leaves them out.
HOWL_MARKS = 'arcs'
_NEAR = [(-1, -2), (0, -2), (1, -1), (2, 0), (2, 1)]
_FAR = [(-1, -3), (0, -3), (1, -3), (2, -2), (3, -1), (3, 0), (3, 1)]
SOUND = [[(14 + x, 2 + y) for x, y in _NEAR], [(16 + x, 1 + y) for x, y in _FAR]]


def howl_frames():
    out = {}
    rows, dx, dy = head_tilted(-0.36)
    out['howl_a'] = rows_of(place(grounded(sit_rows((rows, dx, dy))), PX))
    for name, head, waves in (('howl_0', HOWL, ()), ('howl_1', HOWL_OPEN, (0,)), ('howl_2', HOWL_OPEN, (1,))):
        rows = grounded(sit_rows((head, HOWL_DX, 0)))
        g = place(rows, PX)
        top = GROUND - len(rows) + 1
        for w in waves if HOWL_MARKS == 'arcs' else ():
            for x, y in SOUND[w]:
                X, Y = PX + HEAD_X + x, top + HEAD_Y + y
                if 0 <= X < W and 0 <= Y < H and g[Y][X] == '.':
                    g[Y][X] = 'm'
        out[name] = rows_of(g)
    return out


# ---- shaking the head, ears flapping --------------------------------------------------------------------
# The body stands still (moving it came apart from the legs on the shiba); the head twists about the
# muzzle, the eyes squeezed shut, and the long ears are flung out: rolled one way the near ear flies up
# and out behind the head, rolled the other it swings forward onto the cheek (further, it covered the
# face and the head became a blob) while the far ear flies up
# over the crown. Short motion marks at the sides; then the ears flop back and it blinks.
def closed_eyes(rows):
    """The eye squeezed shut: a 2x1 dark line."""
    g = [list(r) for r in rows]
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch == 'o':
                g[y][x] = 'd'
                if x > 0 and g[y][x - 1] == 'b':
                    g[y][x - 1] = 'd'
            elif ch == 'v':
                g[y][x] = 'b'
    return rows_of(g)


FAR_EAR_UP = [(3, -1), (4, -1), (2, -2), (3, -2), (1, -3), (2, -3), (0, -4), (1, -4)]   # over the crown
SHAKE = {                          # (near ear degrees, head rows up/down, far ear up, motion marks)
    'shake_0': (105, -1, False, [(-8, 0), (-9, 1), (-9, 4), (-10, 5)]),
    'shake_1': (-15, 0, True, [(15, -1), (16, 0), (16, 4), (17, 5)]),
    'shake_settle': (30, 0, False, []),
}


def shake_frames():
    out = {}
    for name, (ear, k, far, marks) in SHAKE.items():
        rows, dx, dy = ear_flapped(ear)                        # the head moves whole: k rows up (tipping
        dy += k                                                # its columns split the muzzle off the head)
        g = [list(r) for r in rows]
        top = next(y for y, r in enumerate(rows) if r.strip('.'))
        left = -dx
        if far:
            for x, y in FAR_EAR_UP:
                X, Y = left + x, top + y
                if 0 <= Y < len(g) and 0 <= X < len(g[0]) and g[Y][X] == '.':
                    g[Y][X] = 'E'
        rows = closed_eyes(rows_of(g)) if name != 'shake_settle' else rows_of(g)
        body_rows = body_with_head((rows, dx, dy))
        full = with_legs(body_rows)
        G = [list(r) for r in rows_of(place(full, PX))]
        gtop = GROUND - len(full) + 1
        for x, y in marks:
            X, Y = PX + HEAD_X + x, gtop + HEAD_Y + y
            if 0 <= X < W and 0 <= Y < H and G[Y][X] == '.':
                G[Y][X] = 'z'
        out[name] = rows_of(G)
    return out


# ---- stealing a treat -------------------------------------------------------------------------------------
# A bone biscuit lies on the ground ahead. The beagle spots it (head down, eyes on it), checks the viewer
# over its shoulder, then creeps up on it low (bent legs, head level and low, tail down), snatches it,
# lifts its head with the biscuit in its jaws and gallops off with it; it gulps it down and licks its
# lips. The biscuit stays put on the ground (the steps move the dog 1px each, the biscuit is drawn 1px
# further back each frame) and is in every frame until eaten.
BISCUIT = [                      # 7x3 dog-bone biscuit with a shaded underside
    "GG...GG",
    ".GGGGg.",
    "gg...gg",
]
TREAT_AHEAD = 17                 # the biscuit's left end, this far ahead of the near fore paw at first
SNEAK_STEPS = 8
CROUCH = {                       # bent legs: the body 1px lower, the paws still on the ground
    'front': {'reach': (38, -8), 'stand': (26, -24), 'push': (8, -40), None: (24, -70)},
    'hind': {'reach': (-14, 26), 'stand': (-32, 16), 'push': (-50, -6), None: (-24, 50)},
}
TAILS['low'] = [(0, 0), (-1, 1), (-2, 1), (-3, 2), (-4, 2), (-5, 3), (-6, 3), (-7, 4)]


def draw_biscuit(g, x, bottom):
    for dy, r in enumerate(BISCUIT):
        for dx, ch in enumerate(r):
            X, Y = x + dx, bottom - len(BISCUIT) + 1 + dy
            if ch != '.' and 0 <= X < W and 0 <= Y < H and g[Y][X] == '.':
                g[Y][X] = ch
    return g


def treat_x(k):
    """The biscuit's left end in frame coordinates after the dog has moved k pixels."""
    return PX + LEGS['near_front'][0] + 3 + TREAT_AHEAD - k


def holding_head():
    """HEAD with the biscuit between the jaws: the lower jaw dropped a row and the mouth line gone,
    the biscuit sticking out past the nose, the near lip over its back end; a white rim (no outline of
    its own) around the biscuit where it lies over the dog, or it melted into the tan."""
    w, h = len(HEAD[0]) + 5, len(HEAD) + 1
    g = [['.'] * w for _ in range(h)]
    for y, r in enumerate(HEAD):
        for x, ch in enumerate(r):
            if ch == '.':
                continue
            if ch == 'd':
                ch = 'w'
            yy = y + 1 if (y >= 9 and x >= 7) else y
            g[yy][x] = ch
    for x in range(7, 11):                                   # close the dropped jaw's back
        if g[9][x] == '.':
            g[9][x] = 'w'
    x0, y0 = 10, 8
    cells = {(x0 + dx, y0 + dy): ch for dy, r in enumerate(BISCUIT) for dx, ch in enumerate(r) if ch != '.'}
    lips = {(x, y): g[y][x] for (x, y) in cells if x < 12 and g[y][x] != '.' and y == 8}
    for (x, y) in cells:
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in cells and 0 <= ny < h and 0 <= nx < w and g[ny][nx] != '.':
                g[ny][nx] = 'W'
    for (x, y), ch in cells.items():
        g[y][x] = ch
    for (x, y), ch in lips.items():
        g[y][x] = ch
    return rows_of(g)


def steal_frames():
    out = {}
    look_down = head_tilted(0.3, HEAD[:-1])
    g = place(with_legs(body_with_head(look_down)), PX)
    out['steal_spot'] = rows_of(draw_biscuit(g, treat_x(0), GROUND))
    # a glance at the viewer: the face-on head over the side body (as turn_a)
    g = [list(r) for r in turn_frames()['turn_a']]
    out['steal_check'] = rows_of(draw_biscuit(g, treat_x(0), GROUND))
    for k in range(SNEAK_STEPS):
        f = k % 4
        a, b = STEP[f], STEP[(f + 2) % 4]
        poses = {n: (CROUCH['hind' if 'hind' in n else 'front'][p]) for n, p in
                 (('near_hind', a), ('far_front', a), ('far_hind', b), ('near_front', b))}
        rows = grounded(with_legs(body_with_head(head_tilted(0.14, HEAD[:-1]), tail_pose='low'), poses))
        g = place(rows, PX)
        out[f'steal_sneak_{k}'] = rows_of(draw_biscuit(g, treat_x(k + 1), GROUND))
    rows = front_down('up')
    g = [['.'] * W for _ in range(H)]
    draw_biscuit(g, treat_x(SNEAK_STEPS), GROUND)            # under the muzzle, drawn first
    grab = [list(r) for r in rows_of(place(nose_down(rows), PX))]
    for y in range(H):
        for x in range(W):
            if grab[y][x] != '.':
                g[y][x] = grab[y][x]
    out['steal_grab'] = rows_of(g)
    held = holding_head()
    out['steal_hold'] = rows_of(place(with_legs(body(held, tail_pose='up')), PX))
    for f, (poses, lift, d) in enumerate(RUN):
        rows = flex(body_with_head(ear_flapped(RUN_EARS[f], held), tail_pose='out'), d)
        out[f'steal_run_{f}'] = rows_of(place(with_legs(rows, poses, d), PX, lift))
    gulp = [list(r) for r in HEAD]                           # gulped down: licking the lips
    gulp[8][13] = 't'
    gulp[9][12] = 't'
    out['steal_gulp'] = rows_of(place(with_legs(body(rows_of(gulp), tail_pose='fwd')), PX))
    return out


def frames():
    out = {}
    out.update(stand_frames())
    out.update(walk_frames())
    out.update(run_frames())
    out.update(look_frames())
    out.update(turn_frames())
    out.update(sit_frames())
    out.update(lie_frames())
    out.update(scent_frames())
    out.update(howl_frames())
    out.update(shake_frames())
    out.update(steal_frames())
    return out


ANCHOR = (PX + 13, GROUND)

if __name__ == '__main__':
    print(json.dumps(frames(), indent=1))
