"""Frame generator for the black and white border collie.

A light, quick herding dog, a little smaller than the Labrador: the body is drawn by hand over the
silhouette of a side reference taken down to low resolution (a level back, a deep chest under a thick
black mane with a white ruff down the front, a full belly, the tail carried low), the head by hand after the face-on head (a small head; ears set at the top corners and
falling back with a grey fur tip and a dusky pink inside; a thin white blaze over the crown and down
the forehead into the white muzzle; the eye in a soft socket wrapping it; the black cheek down to the
jaw; the open smile with the tongue). Legs are two rigid bones and a paw each, 3px thick, turned by
angle per frame (as the Labrador's, see draft_lab.leg_pixels): black at the top, white below the elbow
and the hock. assemble_collie.py turns the result into sprites/collie.json.

Usage: python3 tools/draft_collie.py > /tmp/collie-frames.json
"""
import json
import math

W, H = 96, 48                    # tall enough for the frisbee leap, wide enough for it to fly in
GROUND = H - 1
PX = 5

# ---- palette keys ------------------------------------------------------------------------------
# K/H: black coat and its sheen along the back, j: the folded thigh's shadow, w: white (blaze, muzzle,
# ruff), x: white in shade, S/s: the eye's socket and its lighter lower rim, o/v: eye (top/bottom), e:
# nose, d: mouth, t: tongue, i: inside of the ear, n: the ear's grey fur tip, k/l: near/far leg (black),
# p/q: near/far lower leg and paw (white)

# ---- the body (facing right, the head left out) ------------------------------------------------
# 50x23 above the legs; the head sits at HEAD_X, HEAD_Y. The tail is carried low behind the rump.
BODY = [
    "..................................................",
    "..................................................",
    "..................................................",
    "..................................................",
    "..................................................",
    "..................................................",
    "...............................H..................",
    ".............................HHK..................",
    "...........................HHKKKKK................",
    ".........................HHKKKKKKK................",
    "...........HHHHHHHHHH...KKKKKKKKKKwKKK............",
    "..........HKKKKKKKKKKHHHKKKKKKKKKKwwww............",
    ".........HKKKKKKKKKKKKKKKKKKKKKKKKwwww............",
    "........HKKKKKKKKKKKKKKKKKKKKKKKKKwwww............",
    "........KKKKKKKKKKKKKKKKKKKKKKKwwwwwwwww..........",
    ".......KKKKKKKKKKKKKKKKKKKKKKKKwwwwwwww...........",
    ".KKK..KKKKKKKKKKKKKKKKKKKKKKKKKwwwwwww............",
    "KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKwwwwwww............",
    "KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKwwwwww.............",
    ".KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKwwwwww.............",
    "..KKKKKKKKKKKKKKKKKKKKKKKKKKKKKwwwwww.............",
    "...KKKKKKKKKKKKKKKKKKKKKKKKKKKKwwwww..............",
    ".......KKKKK.KKKKK.......KKKKKKwwwww..............",
]
BW, BH = len(BODY[0]), len(BODY)
TAIL_X = 6                       # the tail: the pixels left of this column (behind the rump)
TAIL_ROOT = (6.0, 18.0)          # where it turns about

# ---- the head (facing right) ---------------------------------------------------------------------
HEAD = [
    "....KK............",
    "..KKKKK...........",
    "KKKKiiKK..........",
    "nKKKiiKK..........",
    "..KKKiKKKKw.......",
    ".KKKKKKKKKKw......",
    "KKKKKKKKKKKKw.....",
    "KKKKKKSSSKKKKw....",
    "KKKKKKSoSKKwwwwwee",
    "KKKKKKSvSKwwwwwwee",
    "KKKKKKSsSKwwwwwwee",
    ".KKKKKKKKKwwwwwww.",
    "..KKKKKKKdwddddd..",
    ".KKKKKKKKKwwdttt..",
    "..KKKKKKKwwwwtt...",
]
HEAD_X, HEAD_Y = 32, 0           # where the head sits on the body
EAR = {(x, y) for y, r in enumerate(HEAD[:4]) for x, ch in enumerate(r) if ch != '.' and x < 8}
EAR_BASE = (5.0, 3.5)            # in HEAD: where the ear turns about


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


def turned(cells, deg, about):
    """{(x, y): ch} turned deg degrees about `about` (positive: clockwise on screen), each target
    pixel taking the source pixel it comes from (so the shape keeps no holes)."""
    if not deg:
        return dict(cells)
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    bx, by = about
    xs = [x for x, _ in cells]
    ys = [y for _, y in cells]
    r = int(max(abs(max(xs) - bx), abs(min(xs) - bx), abs(max(ys) - by), abs(min(ys) - by))) + 2
    out = {}
    for Y in range(int(by) - r, int(by) + r + 1):
        for X in range(int(bx) - r, int(bx) + r + 1):
            x, y = X - bx, Y - by
            src = (round(bx + x * ca + y * sa), round(by - x * sa + y * ca))
            if src in cells:
                out[(X, Y)] = cells[src]
    return out


def tail(g, deg):
    """The low tail turned deg degrees about its root (negative: up and out behind)."""
    cells = {(x, y): g[y][x] for y in range(len(g)) for x in range(TAIL_X) if g[y][x] != '.'}
    for x, y in cells:
        g[y][x] = '.'
    for (x, y), ch in turned(cells, deg, TAIL_ROOT).items():
        if 0 <= y < len(g) and 0 <= x < TAIL_X + 1 and g[y][x] == '.':
            g[y][x] = ch


def ear_turned(deg, head=None):
    """The head with the ear turned deg degrees about its base (positive: the tip back and down, flat
    on the run; negative: up)."""
    head = head or HEAD
    g = [list(r) for r in head]
    cells = {}
    for x, y in EAR:
        cells[(x, y)] = g[y][x]
        g[y][x] = '.' if y < 3 else 'K'
    for (x, y), ch in turned(cells, deg, EAR_BASE).items():
        if 0 <= y < len(g) and 0 <= x < len(g[0]):
            g[y][x] = ch
    return rows_of(g)


def body(head=None, hx=HEAD_X, hy=HEAD_Y, tail_deg=0, breath=False):
    head = HEAD if head is None else head
    ww = max(BW, hx + len(head[0]))                               # (moved forward, the head's nose was cut off)
    g = [list(r) + ['.'] * (ww - BW) for r in BODY]
    tail(g, tail_deg)
    pad = max(0, -hy)
    g = [['.'] * ww for _ in range(pad)] + g
    put(g, head, hx, hy + pad)
    rows = rows_of(close_neck(g, hx))
    if breath:                                                    # the chest swells 1px
        at = BREATH_ROW + pad
        rows = rows[1:at] + [rows[at]] + rows[at:]
    return rows


BREATH_ROW = 16


def close_neck(g, hx):
    """Close gaps between a moved head and the neck (white under the chin, black behind)."""
    for _ in range(2):
        for y in range(1, len(g) - 1):
            for x in range(hx - 4, len(g[0]) - 1):
                if g[y][x] == '.' and g[y - 1][x] != '.' and g[y + 1][x] != '.' and g[y][x - 1] != '.':
                    g[y][x] = 'w' if 'w' in (g[y + 1][x], g[y][x - 1]) else 'K'
    for y in range(len(g)):                                  # and short gaps between the mane and a lowered head
        for x in range(hx - 6, hx + 2):
            if g[y][x] != '.' and g[y][x + 1] == '.':
                for n in (1, 2, 3):
                    if x + 1 + n < len(g[0]) and g[y][x + 1 + n] != '.' and all(g[y][x + k] == '.' for k in range(1, n + 1)):
                        for k in range(1, n + 1):
                            g[y][x + k] = 'K'
                        break
    return g


# ---- legs: two rigid bones and a paw, 3px thick, black above the elbow and the hock -----------------
LEG_ROWS = 13
BONES = {'front': (8.06, 4.42), 'hind': (5.98, 7.28)}
WHITE_FROM = {'front': 2, 'hind': 6}                           # rows down the leg where the white starts
LEGS = {'far_hind': (9, 'l', 'q'), 'near_hind': (13, 'k', 'p'), 'far_front': (25, 'l', 'q'), 'near_front': (29, 'k', 'p')}
LEG_ORDER = ['far_hind', 'far_front', 'near_hind', 'near_front']
FRONT_FORMS = {'stand': (0, 0), 'reach': (16, 10), 'push': (-14, -22), 'lift': (-8, -105), 'fold': (-30, -125)}
HIND_FORMS = {'stand': (-30, 8), 'reach': (-10, 18), 'push': (-48, -10), 'lift': (-45, 25), 'fold': (45, 105)}


def leg_pixels(kind, a1, a2, thick=3, paw=2, rows=None):
    """{(x, y): white} for one leg whose top-left pixel is (0, 0); white from WHITE_FROM along it; a paw
    when it reaches down `rows` (the leg rows)."""
    l1, l2 = BONES[kind]
    px = {}
    x = y = 0.0
    done = 0.0                                    # how far along the leg
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
                p = (X, Y + k) if flat else (X + k, Y)
                px[p] = px.get(p, False) or done + t >= WHITE_FROM[kind]
        x, y = x + sx * length, y + sy * length
        done += length
    bottom = max(Y for _, Y in px)
    if bottom >= (rows or LEG_ROWS) - 1:          # standing on it: a paw, toes forward
        right = max(X for X, Y in px if Y == bottom)
        for k in range(1, paw + 1):
            px[(right + k, bottom)] = True
        px[(right + 1, bottom - 1)] = True
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
        for (X, Y), white in leg_pixels(kind, a1, a2).items():
            if 0 <= Y < LEG_ROWS and 0 <= x0 + X < w:
                g[Y][x0 + X] = sock if white else fur
    return list(rows) + [''.join(r) for r in g]


def grounded(rows):
    while rows and not rows[-1].strip('.'):
        rows = rows[:-1]
    return rows


def stand_frames():
    out = {'stand': rows_of(place(with_legs(body()), PX))}
    out['idle_0'] = out['stand']
    out['idle_1'] = rows_of(place(with_legs(body(breath=True)), PX))
    return out


# ---- walking and running ---------------------------------------------------------------------------
STEP = ['reach', 'stand', 'push', None]
WALK_TAILS = [0, -6, 0, 6]                               # the low tail swaying a little


def walk_frames():
    out = {}
    for f in range(4):
        a, b = STEP[f], STEP[(f + 2) % 4]
        poses = {'near_hind': a, 'far_front': a, 'far_hind': b, 'near_front': b}
        out[f'walk_{f}'] = rows_of(place(with_legs(body(tail_deg=WALK_TAILS[f]), poses), PX))
    return out


def flex(rows, d, at=16):
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


# the gallop (as the Labrador's): front paws land, push off as the hind legs swing forward, all four
# gather under the body with the rump pulled in, the hind paws land ahead, push off as the front legs
# reach, and it flies stretched out; the head low and forward, the tail streaming out behind
RUN = [
    ({'far_front': (20, 10), 'near_front': (10, 2), 'far_hind': (-70, -60), 'near_hind': (-58, -40)}, 0, 0),
    ({'far_front': (-20, -30), 'near_front': (-10, -18), 'far_hind': (10, 65), 'near_hind': (0, 40)}, 0, 1),
    ({'far_front': (-30, -115), 'near_front': (-40, -125), 'far_hind': (50, 105), 'near_hind': (40, 90)}, 0, 1),
    ({'far_front': (50, 30), 'near_front': (40, 15), 'far_hind': (18, 10), 'near_hind': (8, 2)}, 0, 0),
    ({'far_front': (70, 60), 'near_front': (60, 45), 'far_hind': (-32, -22), 'near_hind': (-22, -12)}, 0, -1),
    ({'far_front': (82, 80), 'near_front': (76, 70), 'far_hind': (-80, -80), 'near_hind': (-74, -68)}, 1, -1),
]
RUN_EARS = [10, 20, 30, 10, 25, 35]                      # the ears laid back, more in the air
RUN_TAILS = [-30, -36, -40, -30, -36, -42]


def run_frames():
    return {f'run_{f}': rows_of(place(with_legs(flex(body(ear_turned(RUN_EARS[f]), hy=HEAD_Y + 1, tail_deg=RUN_TAILS[f]), d), poses, d), PX, lift))
            for f, (poses, lift, d) in enumerate(RUN)}


# ---- head directions ---------------------------------------------------------------------------------
# Looking up, the head tips on the neck as the beagle's: every column in front of the back of the skull
# moves up by its distance from there, so the muzzle swings most, the eye (all its columns moving
# together) with it. Looking down, the whole head comes down on the neck and a little forward, tipped
# only a little (tipped as far as it tips up, the muzzle stretched long).
LOOK_TILTS = {'up_fwd': -0.34, 'down_fwd': 0.12}
LOOK_DROP = {'up_fwd': (0, 0), 'down_fwd': (1, 3)}          # (columns forward, rows down)
LOOK_DIRS = list(LOOK_TILTS)
TILT_FROM = 4


def head_tilted(k, head=None):
    """(rows, dy): the head with column x moved round((x - TILT_FROM) * k) rows (k < 0: up)."""
    head = head or HEAD
    pad = 6
    G = [['.'] * len(head[0]) for _ in range(len(head) + 2 * pad)]
    for x in range(len(head[0])):
        d = round((x - TILT_FROM) * k) if x > TILT_FROM else 0
        for y, r in enumerate(head):
            if r[x] != '.':
                G[y + pad + d][x] = r[x]
    return rows_of(G), -pad


EYE_AT = (6, 7)                   # in HEAD: the socket's top-left (3 wide, 4 tall: o over v inside it)
LOOK_EYES = {'down_fwd': 'down'}   # looking down the eye looks down too (left in the middle it still
                                   # looked ahead)
GAZES = {'down': ["SSS", "SSS", "SoS", "SvS"]}     # the pupil a pixel down, the lid coming down over it


def gazing(way, head=None):
    """The head with the eye moved inside its socket."""
    g = [list(r) for r in head or HEAD]
    x0, y0 = EYE_AT
    for y, r in enumerate(GAZES[way]):
        for x, ch in enumerate(r):
            g[y0 + y][x0 + x] = ch
    return rows_of(g)


def look_frames():
    out = {}
    for d, k in LOOK_TILTS.items():
        rows, dy = head_tilted(k, gazing(LOOK_EYES[d]) if d in LOOK_EYES else None)
        fx, fy = LOOK_DROP[d]
        for i, breath in enumerate((False, True)):
            b = body(rows, hx=HEAD_X + fx, hy=HEAD_Y + dy + fy, breath=breath)
            out[f'idle_{i}_{d}'] = rows_of(place(with_legs(trimmed(b, -dy)), PX))
    return out


def trimmed(rows, pad):
    """The body rows with the head's extra padding rows taken off the top again where they are empty
    (so the legs stay on the ground and the canvas keeps its size)."""
    while pad and not rows[0].strip('.'):
        rows, pad = rows[1:], pad - 1
    return rows


# ---- turning toward the viewer ------------------------------------------------------------------
# Face-on, drawn as its left half and mirrored (the head approved face-on): the ears at the top corners
# with their grey tips out at the sides and the dusky pink inside, the thin blaze, the eyes in their
# sockets, the big nose in the white muzzle, the open smile, the black cheeks down to the white ruff.
FRONT_HALF = [
    "..KKKK.....",
    ".KKiiKKK.Kw",
    "KKKiKKKKKKw",
    "nKKKKKKKKKw",
    ".KKKKKKKKKw",
    "..KKKKKKKKw",
    "..KKKSSSKKw",
    ".KKKKSoSKKw",
    "..KKKSvSKww",
    "..KKKSsSKww",
    ".KKKKKKwwee",
    "..KKKKKwwee",
    "..KKKKKwwee",
    "..KKKKKKwwd",
    ".KKKKKKwddd",
    "..KKKKKdwtt",
    "..KKKKwwwtt",
    ".KKKwwwwwww",
    "..KKwwwwwww",
]
CHEST_HALF = [                       # the white ruff and the black shoulders under the face-on head
    "..KKKwwwwww",
    "...KKwwwwww",
    "...KKKwwwww",
    "....KKKwwww",
    ".....KKwwww",
]
TURN_FRONT = [h + h[::-1] for h in FRONT_HALF + CHEST_HALF]
FRONT_LEGS = ["ppp....ppp"] * (LEG_ROWS - 1) + ["pppp....pppp"]   # white all the way down; centred row by row


def front_legs():
    w = len(TURN_FRONT[0])
    rows = []
    for r in FRONT_LEGS:
        pad = (w - len(r)) // 2
        rows.append('.' * pad + r + '.' * (w - len(r) - pad))
    return rows


TURN_SQUASH = 0.7                 # the three-quarter body's length against the side body's
TURN_FACE = 39                    # the three-quarter face's centre column: about halfway between the side
                                  # face's and the face-on face's (on the anchor), so the face moves in
                                  # even steps (it jumped 5 then 11 columns and the turn looked choppy)


def turn_frames():
    """turn_a: three-quarter, the face-on head and chest over the side body seen short (squashed toward
    the chest), with the forelegs under the face-on chest; turn_b: face-on, centred on the anchor (the
    point the sprite is mirrored about)."""
    side = place(body(head=['.']), PX, LEG_ROWS)
    front_x = max(x for x in range(W) if any(side[y][x] != '.' for y in range(H)))
    g = blank()
    for X in range(W):                                        # the body squashed toward its chest, the chest
        x = round(front_x - (TURN_FACE - X) / TURN_SQUASH)    # under the face (the rear hid behind the head)
        if 0 <= x < W:
            for y in range(H):
                g[y][X] = side[y][x]
    for name in ('far_hind', 'near_hind'):                    # the hind legs drawn whole at their new places
        x0, fur, sock = LEGS[name]                            # (squashed, they broke up)
        X0 = round(TURN_FACE - (front_x - PX - x0) * TURN_SQUASH)
        for (X, Y), white in leg_pixels('hind', *HIND_FORMS['stand']).items():
            if 0 <= Y < LEG_ROWS and 0 <= X0 + X < W:
                g[GROUND - LEG_ROWS + 1 + Y][X0 + X] = sock if white else fur
    front = TURN_FRONT + front_legs()
    fw = len(front[0])
    fx = TURN_FACE - fw // 2
    ft = GROUND - len(front) + 1
    for y, r in enumerate(front):
        for x, ch in enumerate(r):
            if ch != '.' and 0 <= fx + x < W:
                g[ft + y][fx + x] = ch
    return {'turn_a': rows_of(g), 'turn_b': rows_of(place(front, ANCHOR[0] - fw // 2 + 1))}


# ---- sitting -------------------------------------------------------------------------------------
# The body shortened (seen from the side a sitting body is short) and sheared down toward the rump on
# the ground, the head upright over the chest, the white forelegs straight down, the black thigh folded
# at the side (lit along the top, a shadow at the front) with the white hind paw forward on the ground,
# the tail lying along the ground behind.
SIT_CUT = 8
SIT_DROP = 10


def sit_rows(head=None, hdy=0, breath=False):
    g = [list(r) for r in BODY]
    tail(g, 0)
    for y in range(len(g)):                                    # the tail goes; it lies on the ground instead
        for x in range(TAIL_X):
            g[y][x] = '.'
    x0, x1 = 6, 37                                             # the rump, the chest's front
    xf = 26                                                    # the shoulder: nothing moves in front of it
    cut = range(xf - SIT_CUT, xf)
    cols = [x for x in range(BW) if x not in cut]
    Hs = BH + LEG_ROWS
    ground = Hs - 1
    G = [['.'] * BW for _ in range(Hs)]
    for i, x in enumerate(cols):
        X = i + SIT_CUT
        d = round(SIT_DROP * min(1, (xf - x) / (xf - x0))) if x < xf else 0
        for y in range(BH):
            if g[y][x] != '.' and 0 <= X < BW and y + d <= ground:
                G[y + d][X] = g[y][x]
    put(G, HEAD if head is None else head, HEAD_X, HEAD_Y + hdy)
    close_neck(G, HEAD_X)
    neck_line(G, (HEAD_X, HEAD_Y + hdy + 6), (21, 16))
    for x in (29, 30, 31, 33, 34, 35):                         # the forelegs, straight down from the chest
        ys = [y for y in range(Hs) if G[y][x] != '.']
        for y in range(ys[-1] + 1 if ys else BH, Hs):
            G[y][x] = 'p' if x >= 33 else 'q'
    G[ground][36] = 'p'
    cx = 22
    draw_thigh(G, cx, ground - 4, 6, 4)                        # the folded thigh, behind the forelegs
    for x in range(cx - 1, cx + 6):                            # the white hind paw forward on the ground
        G[ground][x] = 'p'
    G[ground - 1][cx + 5] = 'p'
    rx0 = min(x for x in range(BW) if G[ground - 1][x] != '.')       # the tail from the rump along the ground,
    for x, up in [(rx0 - k, u) for k in range(0, 7) for u in (0, 1)] + [(rx0 - 7, 1), (rx0 - 7, 2), (rx0 - 8, 2)]:
        if 0 <= x and G[ground - up][x] == '.':                # its tip curling up (1px thick it read as a line)
            G[ground - up][x] = 'K'
    rows = rows_of(filled(G))
    if breath:
        rows = rows[1:BREATH_ROW + 4] + [rows[BREATH_ROW + 4]] + rows[BREATH_ROW + 4:]
    return rows


def neck_line(G, top, bottom):
    """The back of the sitting dog's neck a straight slope from the back of the skull down to the back
    (the standing neck's mane, kept as it was, stood up behind the head like a hump)."""
    (x0, y0), (x1, y1) = top, bottom
    for y in range(y0, y1 + 1):
        xl = round(x0 + (x1 - x0) * (y - y0) / (y1 - y0))
        for x in range(xl):
            G[y][x] = '.'
        right = next((x for x in range(xl, len(G[0])) if G[y][x] != '.'), None)
        if right is not None:
            for x in range(xl, right):
                G[y][x] = 'K'
        G[y][xl] = 'H'
        for x in range(xl + 1, min(xl + 4, len(G[0]))):           # the old sheen inside goes
            if G[y][x] == 'H':
                G[y][x] = 'K'


def draw_thigh(g, cx, cy, rx, ry):
    """The folded black thigh, an ellipse with an unbroken lit line along its top and back and a
    shadow line down its front (by ellipse distance the lit edge broke into dots; filled with shadow
    it read as a dark blob)."""
    cells = {(x, y) for y in range(cy - ry, cy + ry + 1) for x in range(cx - rx, cx + rx + 1)
             if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1}
    for x, y in cells:
        top = (x, y - 1) not in cells
        back = (x - 1, y) not in cells
        front = (x + 1, y) not in cells
        if (top and x <= cx + 2) or (back and y <= cy):
            g[y][x] = 'H'
        elif front and y >= cy - 1:
            g[y][x] = 'j'
        else:
            g[y][x] = 'K'


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
                g[y][x] = 'K'
    return g


def sinking_rump():
    """Halfway down: the hind legs fold and the rump sinks toward the ground, the chest stays up."""
    rows = with_legs(body(), {'far_hind': 'fold', 'near_hind': 'fold'})
    h, w = len(rows), len(rows[0])
    g = [['.'] * w for _ in range(h)]
    for x in range(w):
        d = 5 if x < 14 else 3 if x < 19 else 1 if x < 23 else 0
        for y in range(h - 1, -1, -1):
            if rows[y][x] != '.' and y + d < h:
                g[y + d][x] = rows[y][x]
    return rows_of(filled(g))


def sit_frames():
    return {'sit_0': rows_of(place(grounded(sit_rows()), PX)),
            'sit_1': rows_of(place(grounded(sit_rows(breath=True)), PX)),
            'sit_a': rows_of(place(grounded(sinking_rump()), PX))}


# ---- lying down ---------------------------------------------------------------------------------
# Belly down on the ground, the head up. The white forearms and paws reach out ahead of the ruff, the
# far paw a shade darker beside the near one; the folded hind leg is a rounded black thigh (lit along
# the top, a shadow at the front) with its white paw forward under the belly.
def lie(rows, chest=None):
    """chest: the chest's front column (worked out from the rows when the head is up)."""
    g = place(rows, PX, 1)
    xs = [x for x in range(W) if g[GROUND - 1][x] != '.']
    for x in range(min(xs) + 2, max(xs) - 4):              # the side resting on the ground
        g[GROUND][x] = 'K'
    FORE = [  # (dx from the chest's front, row from the ground, key); the far paw first, the near leg over it
        (6, 1, 'q'), (7, 1, 'q'), (5, 0, 'q'), (6, 0, 'q'), (7, 0, 'q'), (8, 0, 'q'),
        (-1, 1, 'q'), (0, 1, 'q'), (1, 1, 'q'), (2, 1, 'q'), (3, 1, 'p'), (4, 1, 'p'), (5, 1, 'p'),
        (-1, 0, 'p'), (0, 0, 'p'), (1, 0, 'p'), (2, 0, 'p'), (3, 0, 'p'), (4, 0, 'p'), (5, 0, 'p'), (6, 0, 'p'),
    ]
    chest = chest or max(x for x in range(W) if g[GROUND - 2][x] != '.' and x < PX + 40)
    for dx, up, ch in FORE:
        x, y = chest + dx, GROUND - up
        if 0 <= x < W and (g[y][x] == '.' or up < 2):
            g[y][x] = ch
    draw_thigh(g, PX + 12, GROUND - 4, 6, 4)               # the folded thigh
    for x in range(PX + 12, PX + 19):                      # the white hind paw forward under the belly
        g[GROUND][x] = 'p'
    for x in (PX + 17, PX + 18):
        g[GROUND - 1][x] = 'p'
    for y in range(GROUND - 3, GROUND + 1):                # close the gap under the belly
        xs = [x for x in range(W) if g[y][x] != '.']
        for x in range(min(xs), min(max(xs), PX + 36)):
            if g[y][x] == '.' and any(g[y][k] != '.' for k in range(max(0, x - 8), x)) and any(g[y][k] != '.' for k in range(x + 1, min(W, x + 9))):
                g[y][x] = 'K'
    return rows_of(g)


def lie_frames():
    down = grounded(with_legs(body(), {n: 'fold' for n in LEGS}))[:-3]
    return {'lie_a': rows_of(filled([list(r) for r in rows_of(place(down, PX))])),
            'lie_0': lie(body()), 'lie_1': lie(body(breath=True))}


# ---- herding: the eye, the stalk and the clap ------------------------------------------------------
# A border collie working sheep: the forequarters drop almost to the ground (the elbows bent deep, the
# shoulders low) while the hind legs stay nearly straight, so the rump is the highest point; the head
# goes down below the line of the back, the neck stretched forward, and the eyes fix ahead (the "eye");
# the tail hangs low. It stalks forward in slow, smooth, low strides, drops flat to the ground (the
# "clap") still staring, rises into the crouch again, creeps on, freezes mid-stride with a forepaw off
# the ground, then breaks into a run. (Bending the hind legs as deep as the front, knees forward, sank
# the rump and read as a dog cowering, not working.)
def bent(kind, a1, height):
    """(a1, a2) for a leg whose upper bone is at a1 degrees and whose paw comes height rows down: a
    foreleg's lower bone always forward (reaching), a hind leg's forward when the upper one slopes back."""
    l1, l2 = BONES[kind]
    c = max(-1.0, min(1.0, (height - l1 * math.cos(math.radians(a1))) / l2))
    a2 = math.degrees(math.acos(c))
    return a1, a2 if (kind == 'front' or a1 < 0) else -a2


HIND_H = 12                       # the hind paws this far down (standing: LEG_ROWS): the hind legs nearly
                                  # straight, the rump high
TILT = 6                          # the shoulders this many rows lower
BACK_CURVE = 1.7                  # how the back sinks toward the shoulders (1: a straight slope)
FRONT_DX = 0                      # the forelegs this many columns further forward
# the stalk: six frames a stride, one forepaw always planted while the other comes up off the ground
# (folded back), swings forward in the air and is set down ahead (swinging both on the ground, they slid
# back and forth like oars, and bent at the wrist they shuffled); a number is a planted leg's upper-bone
# angle (the leg bent to reach the ground), a list a leg in the air
LIFT_UP = [(50, 5), (-100, 3)]    # in the air, drawn as folded parts (the standing bones are longer than the
LIFT_FWD = [(60, 5), (20, 3)]     # crouched leg is tall, so lifted they still touched the ground): folded up
                                  # under the chest, then swung forward and hanging, about to be set down
STALK = [
    (55, 35), (45, LIFT_UP), (35, LIFT_FWD), (55, 35)[::-1], (LIFT_UP, 45), (LIFT_FWD, 35),
]
STALK_HIND = [(-20, -40), (-25, -35), (-30, -30), (-40, -20), (-35, -25), (-30, -30)]
HERD_HEAD = (3, 7)                # the head down below the back, the neck stretched: (columns forward, rows down)
HERD_TAIL = -40                   # the tail hanging low
EYE_HEAD = HEAD[:12] + [           # working, the mouth shut (the grin and the tongue looked playful), its line
    "..KKKKKKKwwdddd...",          # starting in the white (run into the black cheek it read as part of the
    ".KKKKKKKKKwwwww...",          # face's pattern)
    "..KKKKKKKwwww.....",
]


def herd_body(head=None, drop=HERD_HEAD):
    hx, hy = drop
    rows = body(head or EYE_HEAD, hx=HEAD_X + hx, hy=HEAD_Y + hy, tail_deg=HERD_TAIL)
    return withers_line(rows, (20, 10), (HEAD_X + hx, HEAD_Y + hy + 4))


def withers_line(rows, a, b):
    """The top of the neck a straight line from the withers to the back of the lowered head (the
    standing neck's mane stood up above it like a hump)."""
    g = [list(r) for r in rows]
    (x0, y0), (x1, y1) = a, b
    for x in range(x0, x1 + 1):
        yl = round(y0 + (y1 - y0) * (x - x0) / (x1 - x0))
        for y in range(yl):
            g[y][x] = '.'
        below = next((y for y in range(yl, len(g)) if g[y][x] != '.'), None)
        if below is not None:
            for y in range(yl, below):
                g[y][x] = 'K'
            g[yl][x] = 'H'
    return rows_of(g)


def crouched(rows, uppers, tilt=None, hind_h=None, power=None, front_dx=None):
    """The body tipped down at the front tilt rows (from the loin to the shoulder), then the legs drawn
    from where each meets the body down to the ground, each bent to reach it (uppers: the upper-bone
    angle of each leg, or a full (a1, a2) for a leg held off the ground). (Tipping the legs with the
    body broke their joints into steps.)"""
    tilt = TILT if tilt is None else tilt
    hind_h = HIND_H if hind_h is None else hind_h
    power = BACK_CURVE if power is None else power
    front_dx = FRONT_DX if front_dx is None else front_dx
    w = len(rows[0])
    # the back sinks in a curve, little over the loin and more and more toward the shoulders (tipped in a
    # straight line, the body did not look let down)
    tip = lambda x: round(tilt * max(0.0, min(1.0, (x - 8) / 18)) ** power)    # full at the forelegs
    top = len(rows)
    ground = top + tip(LEGS['near_hind'][0] + 1) + hind_h - 1
    g = [['.'] * w for _ in range(ground + 1)]
    for x in range(w):
        for y, r in enumerate(rows):
            if r[x] != '.':
                g[y + tip(x)][x] = r[x]
    for name in LEG_ORDER:
        x0, fur, sock = LEGS[name]
        kind = 'hind' if 'hind' in name else 'front'
        if kind == 'front':                                   # the forelegs set forward under the chest: the
            x0 += front_dx                                    # forepaws reach ahead, creeping up
        y0 = top + tip(x0 + 1)
        height = ground - y0 + 1
        a = uppers[name]
        if isinstance(a, list):                               # a leg in the air, in parts [(angle, length), ...]
            pixels = segment_pixels(kind, a)
        else:
            a1, a2 = a if isinstance(a, tuple) else bent(kind, a, height)
            pixels = leg_pixels(kind, a1, a2, rows=height)
        for (X, Y), white in pixels.items():
            if 0 <= y0 + Y <= ground and 0 <= x0 + X < w:
                g[y0 + Y][x0 + X] = sock if white else fur
    return rows_of(place(grounded(rows_of(filled_under(g, top, tip))), PX))


def filled_under(g, top, tip):
    """Close the gap the tip leaves between the body and the tops of the legs (only where it tipped)."""
    for x in range(len(g[0])):
        for y in range(top, top + tip(x)):
            if g[y][x] == '.' and any(g[k][x] != '.' for k in range(y)) and g[top + tip(x)][x] in 'kl':
                g[y][x] = 'K'
    return g


def segment_pixels(kind, segs, thick=3, rows=None):
    """{(x, y): white} for a leg drawn as segments [(angle, length), ...] (as leg_pixels)."""
    px = {}
    x = y = 0.0
    done = 0.0
    for ang, length in segs:
        sx, sy = math.sin(math.radians(ang)), math.cos(math.radians(ang))
        steps = int(length * 4)
        for i in range(steps + 1):
            t = length * i / steps
            X, Y = round(x + sx * t), int(y + sy * t)
            if Y < 0:
                continue
            flat = abs(ang) > 55
            for k in range(thick):
                p = (X, Y + k) if flat else (X + k, Y)
                px[p] = px.get(p, False) or done + t >= WHITE_FROM[kind]
        x, y = x + sx * length, y + sy * length
        done += length
    bottom = max(Y for _, Y in px)
    if rows and bottom >= rows - 1:               # a paw, toes forward
        right = max(X for X, Y in px if Y == bottom)
        for k in (1, 2):
            px[(right + k, bottom)] = True
    return px


def legs_at(nf, ff, nh, fh):
    return {'near_front': nf, 'far_front': ff, 'near_hind': nh, 'far_hind': fh}


def herd_frames():
    out = {}
    half_tilt = TILT // 2
    out['herd_down'] = crouched(herd_body(drop=(1, 3)), legs_at(20, 20, -30, -30), half_tilt, 12)
    out['herd_crouch'] = crouched(herd_body(), legs_at(42, 42, -30, -30))
    for i in range(len(STALK)):
        out[f'herd_stalk_{i}'] = crouched(herd_body(), legs_at(*STALK[i], *STALK_HIND[i]))
    frozen = legs_at(55, 30, -20, -40)
    frozen['near_front'] = (25, -60)                              # mid-stride, the forepaw held off the ground
    out['herd_freeze'] = crouched(herd_body(), frozen)
    chest = max(x for x in range(W) if place(body(), PX, 1)[GROUND - 2][x] != '.' and x < PX + 40)
    out['herd_clap'] = lie(withers_line(body(EYE_HEAD, hx=HEAD_X + 3, hy=HEAD_Y + 6, tail_deg=HERD_TAIL // 2),
                                        (20, 10), (HEAD_X + 3, HEAD_Y + 10)), chest + 7)
    return out


# ---- chin on the paws -----------------------------------------------------------------------------
# Lying down, it lays its chin on its forepaws with a sigh and looks up from under its brows without
# lifting the head (the pupils up in their sockets), then down again; it breathes and blinks.
CHIN_DROP = (2, 7)                # the head on the paws: (columns forward, rows down); the paws reach out
                                  # further so they show from under the chin (under it, they were hidden)
GAZES['up'] = ["SoS", "SvS", "SSS", "SsS"]       # the pupil a pixel up, looking up from under the brow


def chin_frames():
    chest = max(x for x in range(W) if place(body(), PX, 1)[GROUND - 2][x] != '.' and x < PX + 40)
    fx, fy = CHIN_DROP
    out = {}
    for name, (dx, dy, gaze, breath) in {
        'chin_a': (1, 3, None, False), 'chin_0': (fx, fy, None, False), 'chin_1': (fx, fy, None, True),
        'chin_up': (fx, fy, 'up', False),
    }.items():
        head = gazing(gaze) if gaze else HEAD
        b = 1 if breath else 0                                # (breathing lifts the rows above the chest one)
        rows = withers_line(body(head, hx=HEAD_X + dx, hy=HEAD_Y + dy, breath=breath),   # (the standing mane
                            (20, 10 - b), (HEAD_X + dx, HEAD_Y + dy + 4 - b))            # stuck up as a spike)
        out[name] = lie(rows, chest + (CHIN_DROP[0] + 4 if dy > 3 else 0))
    return out


# ---- the frisbee jump catch ------------------------------------------------------------------------
# A red frisbee sails in from ahead and above; the collie watches it come (head up), dips, springs up
# with the body tipped up, catches it in the jaws at the top of the leap, comes down front paws first and
# trots off holding it, tail going.
FRISBEE = ["...FFFFF...", "fFFFFFFFFFf"]            # edge-on: a low dome over a long thin rim (three rows read
                                                      # as fat, seven wide as a cap)
# it flies in fast from the far right edge toward the dog, dropping a little; the dog takes off while it
# is still well ahead and meets it at the top of the leap (waiting till it was overhead, the catch was late)
FAR = [(FRISBEE, (91, 2)), (FRISBEE, (83, 3)), (FRISBEE, (75, 3)), (FRISBEE, (67, 4))]
JUMP = [                          # (frame, body tip (rows per column, > 0: nose up), rows up, leg poses, frisbee)
    ('fris_dip', 0, 0, 'dip', (60, 4)),
    ('fris_jump_0', 0.3, 3, 'push', (53, 2)),
    ('fris_jump_1', 0.12, 8, 'tuck', 'mouth'),
    ('fris_fall', -0.2, 4, 'reach', 'mouth'),
]


def draw_frisbee(g, x, y, art=None):
    for dy, r in enumerate(art or FRISBEE):
        for dx, ch in enumerate(r):
            if ch != '.' and 0 <= y + dy < H and 0 <= x + dx < W:
                g[y + dy][x + dx] = ch


def with_frisbee_in_mouth(head):
    """The head with the frisbee held in the front of the jaws (over the tongue)."""
    g = [list(r) + ['.'] * 6 for r in head]
    for dy, r in enumerate(FRISBEE):
        for dx, ch in enumerate(r):
            if ch != '.':
                g[12 + dy][11 + dx] = ch
    return rows_of(g)


def tipped(rows, k):
    """The whole dog tipped by shifting each column k rows per column from the middle (k > 0: nose up).
    (Turned by rotation, the head broke up and the nose came off.)"""
    if not k:
        return rows
    h, w = len(rows), len(rows[0])
    pad = int(abs(k) * w / 2) + 2
    g = [['.'] * w for _ in range(h + 2 * pad)]
    for x in range(w):
        d = round((x - w / 2) * k)
        for y, r in enumerate(rows):
            if r[x] != '.':
                g[y + pad - d][x] = r[x]
    return grounded(rows_of(g))


def fris_frames():
    up_head, up_dy = head_tilted(LOOK_TILTS['up_fwd'])
    held = with_frisbee_in_mouth(HEAD)
    held_up, held_dy = head_tilted(-0.2, held)
    legs = {
        'dip': {n: bent('front' if 'front' in n else 'hind', a, 11) for n, a in
                (('near_front', -15), ('far_front', -15), ('near_hind', 10), ('far_hind', 10))},
        'push': {'near_front': (-20, -110), 'far_front': (-30, -120), 'near_hind': (-60, -50), 'far_hind': (-70, -60)},
        'tuck': {'near_front': (-40, -125), 'far_front': (-30, -115), 'near_hind': (30, 100), 'far_hind': (40, 110)},
        'reach': {'near_front': (25, 15), 'far_front': (35, 25), 'near_hind': (-50, -40), 'far_hind': (-60, -50)},
    }
    out = {}
    watching = with_legs(trimmed(body(up_head, hy=HEAD_Y + up_dy), -up_dy))
    for i, (art, (x, y)) in enumerate(FAR):                  # it watches the frisbee fly in
        g = blank()
        place(watching, PX, 0, g)
        draw_frisbee(g, x, y, art)
        out[f'fris_watch_{i}'] = rows_of(g)
    for name, deg, lift, pose, fris in JUMP:
        if fris == 'mouth':
            rows = with_legs(trimmed(body(held_up, hy=HEAD_Y + held_dy, tail_deg=-30), -held_dy), legs[pose])
        else:
            rows = with_legs(trimmed(body(up_head, hy=HEAD_Y + up_dy, tail_deg=-20), -up_dy), legs[pose])
        rows = tipped(rows, deg)
        g = blank()
        place(rows, PX, lift, g)
        if fris != 'mouth':
            draw_frisbee(g, *fris)
        out[name] = rows_of(g)
    out['fris_land'] = rows_of(place(with_legs(body(held, tail_deg=-10), {'near_front': (10, 5), 'far_front': (18, 10)}), PX))
    out['fris_hold'] = rows_of(place(with_legs(body(held, tail_deg=-20)), PX))
    out['fris_hold_1'] = rows_of(place(with_legs(body(held, tail_deg=6)), PX))
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
    out.update(herd_frames())
    out.update(chin_frames())
    out.update(fris_frames())
    return out


ANCHOR = (PX + 25, GROUND)

if __name__ == '__main__':
    print(json.dumps(frames(), indent=1))
