"""Frame generator for the orange and white American cocker spaniel.

A small, compact spaniel: the body drawn by hand (the topline sloping down from high withers to the
docked tail, a deep chest, a long neck carrying the head high, the feathering hanging from chest and
belly in clumps along a wavy hem, an orange saddle), the head by hand (a small rounded dome, a deep
stop, a short broad muzzle, the ears set low at eye level and hanging in a gourd of curls, an orange
crown and eye patch with a white blaze). Legs are two rigid bones and a paw each, 3px thick, turned
by angle per frame (as the Labrador's, see draft_lab.leg_pixels); they show only below the feathering.
assemble_cocker.py turns the result into sprites/cocker.json.

Usage: python3 tools/draft_cocker.py > /tmp/cocker-frames.json
"""
import json
import math

W, H = 56, 34
GROUND = H - 1
PX = 4

# ---- palette keys ------------------------------------------------------------------------------
# w/x: white coat and its shade (the feathering's hem), O/o/a: orange, its shade, its light, v/y: eye
# (top/bottom), e: nose, d: mouth, t: tongue, k/l: near/far leg, p/q: near/far paw

# ---- the body (facing right, the head and legs left out; the neck stops under the back of the head,
# where the head covers it, so a lowered head leaves nothing standing up) -------------------------
BODY = [
    "..........................................",
    "..........................................",
    "..........................................",
    "..........................w.w.............",
    "........................wwwww.............",
    "...ww..................wwwwww.............",
    "...www.............wwwwwwwwww.............",
    "....www...a....aaaaOwwwwwwwww.............",
    "......wwwaOaaaaOOOOOOwwwwwwwwww...........",
    "......wwwwOOOOOOOOOOwwwwwwwwwww...........",
    "......wwwwwOOOOOOOOwwwwwwwwwwww...........",
    "......wwwwwwwOOOOwwwwwwwwwwwwww...........",
    "......wwwwwwwwwwwwwwwwwwwwwww.............",
    "......wwwwwwwwwwwwwwwwwwwwww..............",
    "......wwwwwwwwwwwwwwwwwwwwww..............",
    "......wwwwwwwwwwwwwwwwwwwwww..............",
    ".........wwwwwwwwwwwwwwwwwww..............",
    ".........wwwwwwwwwwwwwwwwwww..............",
    ".........wwwwwwxxwwwwwwwwwww..............",
    ".........xwwxxx..wxxxwwwxxxx..............",
    "..........xx.....x...xxx..................",
]
# ---- the head (facing right; the ears hang over the neck and chest) ------------------------------
HEAD = [
    "...............................aaaaw......",
    "..............................aOOOOww.....",
    ".............................aOOOOOww.....",
    ".............................OOOOOOwww....",
    ".............................OOOOOvwwwwww.",
    ".............................oooooywwwwee.",
    ".............................OOOOoOwwwwwe.",
    ".............................OOOOowwwdddw.",
    ".............................OOOOowwwwtt..",
    ".............................OOOOo........",
    ".............................OOOOo........",
    ".............................OOOOOo.......",
    "............................oOOOOOo.......",
    "............................OOOOOOOo......",
    "...........................oOOOOOOOo......",
    "...........................OOOOOOOOo......",
    "...........................OOOOOOOOo......",
    "...........................OOOooOOoo......",
    "............................oo..oo........",
    "..........................................",
    "..........................................",
]
HEADROOM = 1                                   # an empty row over the body in the figure, so breathing (which lifts
                                               # the rows above the chest a row) does not cut off the top of the head
FW, FH = len(BODY[0]), HEADROOM + len(BODY) + 3   # the figure: the body's rows, then the legs' last rows to the ground
HEM = HEADROOM + 18                            # in the figure: the near legs show over the feathering from here down
EAR_FROM = 9                                   # in HEAD: the ear's rows below the jaw (they swing)
BREATH_ROW = 12


def blank(w=W, h=H):
    return [['.'] * w for _ in range(h)]


def rows_of(g):
    return [''.join(r) for r in g]


def put(g, rows, x0, y0):
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.' and 0 <= y0 + y < len(g) and 0 <= x0 + x < len(g[0]):
                g[y0 + y][x0 + x] = ch


def place(rows, ox, dy=0, g=None):
    """Put rows on the canvas with their bottom row on the ground (dy moves them up)."""
    g = g or blank()
    put(g, rows, ox, GROUND - len(rows) + 1 - dy)
    return g


# ---- legs: two rigid bones and a paw, 3px thick ---------------------------------------------------
BONES = {'front': (5.6, 3.8), 'hind': (5.2, 6.4)}
LEGS = {'far_hind': (7, 13, 'l', 'q'), 'near_hind': (10, 13, 'k', 'p'),      # (x, top row in the body, fur, paw)
        'far_front': (20, 15, 'l', 'q'), 'near_front': (24, 15, 'k', 'p')}
LEG_ORDER = ['far_hind', 'far_front', 'near_hind', 'near_front']
FRONT_FORMS = {'stand': (0, 0), 'reach': (18, 8), 'push': (-16, -20), 'lift': (-6, -100)}
HIND_FORMS = {'stand': (-25, 10), 'reach': (-5, 20), 'push': (-45, -5), 'lift': (-35, 45)}


def leg_pixels(kind, a1, a2, rows, thick=3, paw=2):
    """{(x, y): is paw} for one leg whose top-left pixel is (0, 0)."""
    l1, l2 = BONES[kind]
    px = {}
    x = y = 0.0
    for ang, length in ((a1, l1), (a2, l2)):
        sx, sy = math.sin(math.radians(ang)), math.cos(math.radians(ang))
        steps = int(length * 4)
        for i in range(steps + 1):
            t = length * i / steps
            X, Y = round(x + sx * t), int(y + sy * t)
            if Y < 0:
                continue
            flat = abs(ang) > 55
            for k in range(thick):
                px[(X, Y + k) if flat else (X + k, Y)] = False
        x, y = x + sx * length, y + sy * length
    bottom = max(Y for _, Y in px)
    if bottom >= rows - 1:                        # standing on it: a paw, toes forward
        right = max(X for X, Y in px if Y == bottom)
        for X, Y in list(px):
            if Y == bottom:
                px[(X, Y)] = True
        for k in range(1, paw + 1):
            px[(right + k, bottom)] = True
    return px


def legs_layer(poses, hind_dx=0):
    """{(x, y): ch} of the legs in the figure."""
    out = {}
    for name in LEG_ORDER:
        x0, top, fur, paw = LEGS[name]
        top += HEADROOM
        if 'hind' in name:
            x0 += hind_dx
        kind = 'hind' if 'hind' in name else 'front'
        form = poses.get(name, 'stand')
        forms = HIND_FORMS if kind == 'hind' else FRONT_FORMS
        a1, a2 = forms[form] if isinstance(form, str) else form
        for (X, Y), is_paw in leg_pixels(kind, a1, a2, FH - top).items():
            if 0 <= top + Y < FH:
                out[(x0 + X, top + Y, name)] = paw if is_paw else fur
    return out


def figure(body_rows, poses=None, sway=0, hind_dx=0):
    """The figure (FW x FH): the legs, the body over them, then the near legs again below HEM, where they
    show under the feathering; sway shifts the feathering's hem a column (it swings as the legs move)."""
    g = [['.'] * (FW + 4) for _ in range(FH)]
    for (x, y, name), ch in legs_layer(poses or {}, hind_dx).items():
        if 0 <= x < FW + 4:
            g[y][x] = ch
    top = HEADROOM - (len(body_rows) - len(BODY))     # a breathing body is a row taller: it rises into the headroom
    rows = ['.' * (FW + 4)] * top + [r + '....' for r in body_rows]
    rows += ['.' * (FW + 4)] * (FH - len(rows))
    if sway:
        rows = [shifted(r, sway) if y >= HEM else r for y, r in enumerate(rows)]
    put(g, rows, 0, 0)
    for (x, y, name), ch in legs_layer(poses or {}, hind_dx).items():
        if name.startswith('near') and y >= HEM and 0 <= x < FW + 4:
            g[y][x] = ch
    return rows_of(g)


def shifted(r, d):
    return ('.' * d + r[:-d]) if d > 0 else (r[-d:] + '.' * -d)


TAIL = (8, 9)                                    # in BODY: the docked tail is left of this column, above this row
TAIL_ROOT = (7.0, 8.0)
RUMP = (6, 9, 7, 10)                             # in BODY: the bit of rump at the tail's root (x0, x1, y0, y1)


def body(head=None, hx=0, hy=0, breath=False, ear=0, ear_up=0, tail=0, rump=0):
    """BODY with the head pasted at (hx, hy); ear swings the ears' lower rows ear columns, ear_up lifts
    them (flapping); tail turns the docked tail (degrees, positive: up and forward); rump lifts the bit
    of rump at the tail's root rump rows."""
    head = HEAD if head is None else head
    if ear:
        head = [shifted(r, ear) if EAR_FROM <= y < len(head) else r for y, r in enumerate(head)]
    if ear_up:
        head = ears_lifted(head, ear_up)
    src = [list(r) for r in BODY]
    if tail:
        cells = {(x, y): src[y][x] for y in range(TAIL[1]) for x in range(TAIL[0]) if src[y][x] != '.'}
        for x, y in cells:
            src[y][x] = '.'
        for (x, y), ch in turned(cells, -tail, TAIL_ROOT).items():
            if 0 <= y < len(src) and 0 <= x < FW and src[y][x] == '.':
                src[y][x] = ch
    if rump:                                     # the root of the tail bobs with it: only the little bit of rump
        x0, x1, y0, y1 = RUMP                        # it grows from moves a row (the whole hind end, then the trunk
        old = [r[:] for r in src]                    # too, read as the body moving apart)
        for x in range(x0, x1):
            for y in range(y0, y1):
                src[y][x] = '.'
            for y in range(y0, y1):
                if old[y][x] != '.' and 0 <= y - rump < len(src):
                    src[y - rump][x] = old[y][x]
            if rump > 0 and src[y1 - 1][x] == '.' and old[y1][x] != '.':
                src[y1 - 1][x] = old[y1][x]          # lifted, the row it leaves takes the fur below
    pad = max(0, -hy)
    g = [list(r) for r in [('.' * FW)] * pad + rows_of(src)]
    put(g, head, hx, hy + pad)
    rows = rows_of(g)
    if breath:                                   # the chest swells 1px: a body row below the jaw repeated, the rows
        at = BREATH_ROW + pad                        # above it rising (the top row kept: dropped, the head looked pressed)
        rows = rows[:at] + [rows[at]] + rows[at:]
    return rows[pad:] if pad else rows


def ears_lifted(head, k):
    """The ears' lower part lifted k rows and flared a pixel back (flapping up as it hops)."""
    g = [list(r) for r in head]
    cells = {(x, y): g[y][x] for y in range(EAR_FROM, len(g)) for x in range(0, 36) if g[y][x] != '.'}
    for x, y in cells:
        g[y][x] = '.'
    for (x, y), ch in cells.items():
        Y, X = y - k, x - (1 if k > 1 else 0)
        if 0 <= Y < len(g) and 0 <= X and g[Y][X] == '.':
            g[Y][X] = ch
    return rows_of(g)


def grounded(rows):
    while rows and not rows[-1].strip('.'):
        rows = rows[:-1]
    return rows


def stand_frames():
    out = {'stand': rows_of(place(figure(body()), PX))}
    out['idle_0'] = out['stand']
    out['idle_1'] = rows_of(place(figure(body(breath=True)), PX))
    return out


# ---- walking and running ---------------------------------------------------------------------------
STEP = ['reach', 'stand', 'push', None]
WALK_SWAY = [1, 0, -1, 0]                     # the feathering's hem and the ears swing a little each step


def walk_frames():
    out = {}
    for f in range(4):
        a, b = STEP[f], STEP[(f + 2) % 4]
        poses = {'near_hind': a or 'lift', 'far_front': a or 'lift', 'far_hind': b or 'lift', 'near_front': b or 'lift'}
        out[f'walk_{f}'] = rows_of(place(figure(body(ear=-WALK_SWAY[f]), poses, WALK_SWAY[f]), PX))
    return out


# the gallop (as the Labrador's): front paws land, push off as the hind legs swing forward, all four
# gather under the body, the hind paws land ahead, push off as the front legs reach, and it flies; the
# ears and the feathering stream back
RUN = [
    ({'far_front': (20, 10), 'near_front': (10, 2), 'far_hind': (-70, -60), 'near_hind': (-58, -40)}, 0),
    ({'far_front': (-20, -30), 'near_front': (-10, -18), 'far_hind': (10, 65), 'near_hind': (0, 40)}, 1),
    ({'far_front': (-30, -115), 'near_front': (-40, -125), 'far_hind': (50, 105), 'near_hind': (40, 90)}, 1),
    ({'far_front': (50, 30), 'near_front': (40, 15), 'far_hind': (18, 10), 'near_hind': (8, 2)}, 0),
    ({'far_front': (70, 60), 'near_front': (60, 45), 'far_hind': (-32, -22), 'near_hind': (-22, -12)}, 1),
    ({'far_front': (82, 80), 'near_front': (76, 70), 'far_hind': (-80, -80), 'near_hind': (-74, -68)}, 2),
]
RUN_EARS = [-1, -2, -3, -1, -2, -3]


RUN_REACH = 0.6                                  # the legs swing this much of the Labrador's (short legs under the
                                                 # feathering: the full swing looked far too big)


def run_frames():
    out = {}
    for f, (poses, lift) in enumerate(RUN):
        small = {n: (a1 * RUN_REACH, a2 * RUN_REACH) for n, (a1, a2) in poses.items()}
        out[f'run_{f}'] = rows_of(place(figure(body(ear=RUN_EARS[f]), small, -1), PX, min(lift, 1)))
    return out


# ---- head directions ---------------------------------------------------------------------------------
# Looking up, the head tips on the neck (columns in front of the back of the skull move up by their
# distance from it) and the ears stay hanging; looking down, the whole head comes down and a little
# forward, the pupils down, the top of the neck redrawn down to it.
LOOK_TILTS = {'up_fwd': -0.6, 'down_fwd': 0}
LOOK_DROP = {'up_fwd': (0, 0), 'down_fwd': (1, 2)}
LOOK_DIRS = list(LOOK_TILTS)
TILT_FROM = 33
MUZZLE_FROM = 36                                   # in HEAD: from this column the muzzle moves as one piece
EYE_AT = (34, 4)                                   # in HEAD: the eye's top pixel


def head_tilted(k, head=None):
    """(rows, dy): the head with column x moved round((x - TILT_FROM) * k) rows (k < 0: up), the muzzle
    (from MUZZLE_FROM) all by the same amount (moved column by column, the mouth line broke into steps);
    the ears (left of TILT_FROM) stay hanging."""
    head = head or HEAD
    pad = 6
    G = [['.'] * len(head[0]) for _ in range(len(head) + 2 * pad)]
    for x in range(len(head[0])):
        d = round((min(x, MUZZLE_FROM) - TILT_FROM) * k) if x > TILT_FROM else 0
        for y, r in enumerate(head):
            if r[x] != '.':
                G[y + pad + d][x] = r[x]
    return rows_of(G), -pad


MUZZLE_ROWS = (4, 9)                               # in HEAD: the muzzle's rows (below the forehead)


def bowed(head=None):
    """The head bowing: the muzzle tucked a pixel down and a pixel back, the crown and forehead as they
    are (tipping the columns down flattened the forehead's slope and the top of the head ran on forward)."""
    head = head or HEAD
    g = [list(r) + ['.'] for r in head] + [['.'] * (len(head[0]) + 1)]
    y0, y1 = MUZZLE_ROWS
    block = {(x, y): g[y][x] for y in range(y0, y1) for x in range(MUZZLE_FROM, len(head[0])) if g[y][x] != '.'}
    for (x, y) in block:
        g[y][x] = '.'
    for (x, y), ch in block.items():
        g[y + 1][x - 1] = ch
    for x in range(MUZZLE_FROM - 1, len(head[0])):           # the stop above the tucked muzzle, white fur
        if g[y0][x] == '.' and g[y0 - 1][x] != '.' and g[y0 + 1][x] != '.':
            g[y0][x] = 'w'
    return rows_of(g)


def gazing(way, head=None):
    """The head with the pupil a pixel up or down (left in the middle, it still looked ahead)."""
    g = [list(r) for r in head or HEAD]
    x, y = EYE_AT
    if way == 'down':
        g[y][x], g[y + 1][x], g[y + 2][x] = 'O', 'v', 'y'
    else:
        g[y - 1][x], g[y][x], g[y + 1][x] = 'v', 'y', 'o'
    return rows_of(g)


def neckline(rows, x0, x1, y1):
    """The top of the neck a straight line from the back at column x0 to the back of the head at (x1, y1),
    left of the head; above it cleared, below it filled."""
    g = [list(r) for r in rows]
    head = {(x, y) for y, r in enumerate(g) for x, ch in enumerate(r) if ch != '.' and x >= x1}
    y0 = next(y for y in range(len(g)) if g[y][x0] != '.')
    for x in range(x0, x1):
        yl = round(y0 + (y1 - y0) * (x - x0) / (x1 - x0))
        for y in range(yl):
            if (x, y) not in head:
                g[y][x] = '.'
        below = next((y for y in range(yl, len(g)) if g[y][x] != '.'), len(g))
        for y in range(yl, below):
            g[y][x] = 'w'
    return rows_of(g)


def look_frames():
    out = {}
    for d, k in LOOK_TILTS.items():
        head = gazing('down', bowed()) if d == 'down_fwd' else gazing('up')
        rows, dy = head_tilted(k, head)
        fx, fy = LOOK_DROP[d]
        for i, breath in enumerate((False, True)):
            b = body(rows, hx=fx, hy=dy + fy, breath=breath)
            if fy:                                         # the head lowered: the top of the neck comes down with
                b = neckline(b, 18, 29 + fx, fy + 3)       # it (the neck's top stuck up)
            out[f'idle_{i}_{d}'] = rows_of(place(figure(b), PX))
    return out


# ---- turning toward the viewer ------------------------------------------------------------------
# Face-on, drawn as its left half and mirrored (the face approved face-on): the small dome, the white
# blaze, the orange crown and eye patches, the big eyes, the 2px nose and the smile near the eyes, the
# ears hanging from eye level in gourds of curls, the chest feathering to a wavy hem, the paws.
FRONT_HALF = [
    ".....aaw",
    "....aOOw",
    "...aOOOw",
    "...OOOww",
    "..oOOOww",
    ".OoOvOww",
    ".OoOyOww",
    "OOooOwww",
    "OOOowwwe",
    "OOOowwwe",
    "OOOowwww",
    "OOOOo.dd",
    "OOOOO.wt",
    "OOOOOoww",
    "OOOOOo.w",
    ".OOOOoww",
    "..OoOwww",
    "...wwwww",
    "..wwwwww",
    ".wwwwwww",
    ".wwwwwww",
    "xwwxwwxw",
    ".x..x..x",
    "...ppp..",
    "..pppp..",
]
TURN_FRONT = [h + h[::-1] for h in FRONT_HALF]
TURN_SQUASH = 0.7
ANCHOR = (PX + 20, GROUND)


def turn_frames():
    """turn_a: three-quarter, the face-on head and chest over the side body seen short; turn_b: face-on,
    centred on the anchor (the point the sprite is mirrored about)."""
    side = place(figure(BODY + [], {}), PX)
    fw = len(TURN_FRONT[0])
    face_x = (ANCHOR[0] + PX + 36) // 2                 # halfway between the side face and the face-on one
    front_x = max(x for x in range(W) if any(side[y][x] != '.' for y in range(H)))
    g = blank()
    for X in range(W):                                    # the body squashed toward its chest, under the face
        x = round(front_x - (face_x - X) / TURN_SQUASH)
        if 0 <= x < W:
            for y in range(H):
                g[y][X] = side[y][x]
    fx = face_x - fw // 2
    for y in range(GROUND - 9, GROUND + 1):               # the side forelegs go under the face-on chest
        for x in range(fx, W):
            if g[y][x] in 'klpq':
                g[y][x] = '.'
    put(g, TURN_FRONT, fx, GROUND - len(TURN_FRONT) + 1)
    return {'turn_a': rows_of(g), 'turn_b': rows_of(place(TURN_FRONT, ANCHOR[0] - fw // 2 + 1))}


# ---- sitting -------------------------------------------------------------------------------------
# The body turned about the shoulder so the rump comes down to the ground (sheared, the back and the
# saddle broke apart), the feathering pooling on the ground, the head upright over the chest, the
# forelegs straight down under the chest feathering, the thigh folded at the side with a shade down its
# front and the hind paw forward on the ground.
SIT_TURN = -32                                   # degrees (negative: the rump down)
SHOULDER = (24.0, 12.0)


def turned(cells, deg, about):
    """{(x, y): ch} turned deg degrees about `about` (positive: clockwise on screen), each target pixel
    taking the source pixel it comes from (so the shape keeps no holes)."""
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    bx, by = about
    out = {}
    for Y in range(-20, FH + 20):
        for X in range(-20, FW + 20):
            x, y = X - bx, Y - by
            src = (round(bx + x * ca + y * sa), round(by - x * sa + y * ca))
            if src in cells:
                out[(X, Y)] = cells[src]
    return out


def sit_rows(head=None, breath=False):
    cells = {(x, y): ch for y, r in enumerate(BODY) for x, ch in enumerate(r)
             if ch != '.' and not (x >= 20 and y < 10)}       # the neck goes (turned, it stuck up behind the head)
    rot = turned(cells, SIT_TURN, SHOULDER)
    ground = FH - 1
    G = [['.'] * (FW + 4) for _ in range(FH)]
    for (x, y), ch in rot.items():                         # what reaches the ground pools on it
        y += HEADROOM
        if 0 <= x < FW + 4 and y >= 0:
            G[min(ground, y)][x] = ch if y < ground else 'x'
    for x in range(len(G[0])):                             # the feathering spread on the ground under the rump
        if any(G[y][x] != '.' for y in range(ground - 3, ground)) and G[ground][x] == '.':
            G[ground][x] = 'x'
    rows = rows_of(G)
    if breath:                                             # (the headroom row above takes the rise)
        at = BREATH_ROW + HEADROOM
        rows = rows[1:at] + [rows[at]] + rows[at:]
    G = [list(r) for r in rows]
    tops = [y for y in range(FH) if G[y][18] != '.']
    y0 = tops[0] if tops else 10
    for x in range(18, 31):                                # the neck: straight from the back up to the head
        yl = round(y0 + (4 + HEADROOM - y0) * (x - 18) / 12)
        below = next((y for y in range(yl, FH) if G[y][x] != '.'), FH)
        for y in range(yl, below):
            G[y][x] = 'w'
    put(G, HEAD if head is None else head, 0, HEADROOM)
    for x in (21, 22, 23, 25, 26, 27):                     # the forelegs, straight down from the chest
        ys = [y for y in range(FH) if G[y][x] not in '.']
        start = max(ys) + 1 if ys else 15
        for y in range(start, ground + 1):
            G[y][x] = 'p' if x >= 25 else 'q'
    G[ground][28] = 'p'
    cx, cy, rx, ry = 14, ground - 4, 5, 4                   # the folded thigh, a shade down its front
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d <= 1:
                G[y][x] = 'x' if (d > 0.7 and x > cx) else ('O' if G[y][x] in 'Oa' else 'w')
    for x in range(cx, cx + 5):                            # the hind paw forward on the ground
        G[ground][x] = 'p'
    return filled(G)


def filled(g):
    """Fill the gaps the outside cannot reach (the shear leaves small closed holes)."""
    h, w = len(g), len(g[0])
    seen, stack = set(), [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or not (0 <= x < w and 0 <= y < h) or g[y][x] != '.':
            continue
        seen.add((x, y))
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    for y in range(h):
        for x in range(w):
            if g[y][x] == '.' and (x, y) not in seen:
                g[y][x] = 'w'
    return rows_of(g)


def sinking_rump():
    rows = figure(body(), {'far_hind': (45, 105), 'near_hind': (45, 105)})
    g = [['.'] * len(rows[0]) for _ in rows]
    for x in range(len(rows[0])):
        d = 4 if x < 12 else 2 if x < 16 else 1 if x < 19 else 0
        for y in range(len(rows) - 1, -1, -1):
            if rows[y][x] != '.' and y + d < len(rows):
                g[y + d][x] = rows[y][x]
    return filled(g)


def sit_frames():
    return {'sit_0': rows_of(place(sit_rows(), PX)), 'sit_1': rows_of(place(sit_rows(breath=True), PX)),
            'sit_a': rows_of(place(sinking_rump(), PX))}


# ---- lying down ---------------------------------------------------------------------------------
# Belly down, the feathering spread on the ground, the forepaws out ahead of the chest, the head up.
LIE_DROP = 6


def lie(rows):
    fig = figure(rows, {})
    g = [['.'] * len(fig[0]) for _ in fig]
    for y, r in enumerate(fig):                            # the body comes down; what reaches the ground spreads
        for x, ch in enumerate(r):
            if ch != '.' and ch not in 'klpq':
                Y = min(FH - 1, y + LIE_DROP)
                if g[Y][x] == '.' or Y < FH - 1:
                    g[Y][x] = ch if Y < FH - 1 else 'x'
    for dx in range(0, 6):                                 # the forepaws out ahead of the chest
        for up, key in ((0, 'p'), (1, 'p')):
            x = 27 + dx
            if g[FH - 1 - up][x] == '.' or up == 0:
                g[FH - 1 - up][x] = key if dx > 1 else 'x'
    return rows_of(place(filled(g), PX))


def lie_frames():
    return {'lie_a': rows_of(place(lie_half(), PX)), 'lie_0': lie(body()), 'lie_1': lie(body(breath=True))}


def lie_half():
    """Halfway down: the body half lowered, the legs folding under it."""
    fig = figure(body(), {})
    g = [['.'] * len(fig[0]) for _ in fig]
    for y, r in enumerate(fig):
        for x, ch in enumerate(r):
            if ch != '.' and ch not in 'klpq':
                Y = min(FH - 1, y + LIE_DROP // 2)
                g[Y][x] = ch
    for x in (11, 12, 13, 25, 26, 27):
        for y in range(FH - 3, FH):
            if g[y][x] == '.':
                g[y][x] = 'p' if x in (12, 26) else 'q'
    return filled(g)


# ---- the merry wag ------------------------------------------------------------------------------
# A merry cocker wags its docked tail fast: the tail flicks up and down with the little bit of rump it
# grows from (moving the whole hind end, or the trunk after it, looked like the body coming apart); the
# ears bounce a little.
WAG = [(35, 1, 1), (0, 0, 0), (-25, 0, -1), (0, 0, 0)]        # (tail degrees, tail root rows up: only as it
                                                              # flicks up, a row each way was too much; ear swing)


def wag_frames():
    return {f'wag_{i}': rows_of(place(figure(body(tail=t, rump=r, ear=e), {}), PX))
            for i, (t, r, e) in enumerate(WAG)}


# ---- the ear-flapping hop -------------------------------------------------------------------------
# Excited, it bounces on the spot: a dip, a spring straight up off all four feet (the hind legs pushing
# down, not kicking back), the legs tucked under the belly at the top, reaching down again to land, the
# long ears flying up as it rises and comes down, flopping back as it lands.
HOP = [   # (frame, leg poses, rows up, ears lifted)
    ('hop_dip', {'near_front': (25, -40), 'far_front': (25, -40), 'near_hind': (15, -35), 'far_hind': (15, -35)}, 0, 0),
    ('hop_up', {'near_front': (4, 0), 'far_front': (0, -4), 'near_hind': (-12, 4), 'far_hind': (-16, 2)}, 3, 1),
    ('hop_top', {'near_front': (35, -70), 'far_front': (30, -75), 'near_hind': (70, -20), 'far_hind': (65, -25)}, 6, 3),
    ('hop_down', {'near_front': (12, 4), 'far_front': (8, 2), 'near_hind': (-8, 14), 'far_hind': (-12, 12)}, 3, 4),
    ('hop_land', {'near_front': (25, -40), 'far_front': (25, -40), 'near_hind': (15, -35), 'far_hind': (15, -35)}, 0, 2),
]


def hop_frames():
    out = {}
    for name, poses, lift, ear in HOP:
        rows = grounded(figure(body(ear_up=ear), poses))
        out[name] = rows_of(place(rows, PX, lift))
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
    out.update(wag_frames())
    out.update(hop_frames())
    return out


if __name__ == '__main__':
    print(json.dumps(frames(), indent=1))
