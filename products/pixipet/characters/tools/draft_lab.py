"""Frame generator for the yellow Labrador retriever.

A heavy big dog: the body is drawn with shapes in code (a deep chest, a thick neck, the thigh and
chest down to the legs, a hanging otter tail), the head by hand (a broad skull, a short deep muzzle
with a thick upper lip over a set-back lower jaw, long drop ears). Legs are two rigid bones and a big
paw each, 3px thick, turned by angle per frame (as the shiba's, see draft_shiba.leg_pixels), the lower
bone a paler tone so the joints show. assemble_lab.py turns the result into sprites/lab.json.

Usage: python3 tools/draft_lab.py > /tmp/lab-frames.json
"""
import json
import math

W, H = 54, 34
GROUND = H - 1
PX = 6

# ---- palette keys ------------------------------------------------------------------------------
# b/a/c/d: coat base/light/shade/darkest (mouth, shut eye), E: ear (a warmer gold), w/x: pale chest,
# muzzle and belly and its shadow, e: nose, o/v: eye (top/bottom), r: blush, t: tongue, k/l: near/far
# leg, p/q: near/far lower leg and paw (paler), Y/y/O: the rubber duck, its shade and its beak, W: the
# duck's rim over the dog (white, no outline of its own), P/Q: puddle water
# and its light, Z: splashed drops, z: squeak lines (P, Q, Z and z have no outline)

# ---- the head (facing right) ---------------------------------------------------------------------
# 17x13: skull 12 long, muzzle 5, square at the nose; two rows of upper lip between the nose and the
# smiling mouth, the lip hanging over at the front, the lower jaw set back under it with the tongue
HEAD = [
    "...bbbbbbb.......",
    "..bbbbbbbbba.....",
    ".EEbbbbbbbbba....",
    "EEEEbbbbbbbbb....",
    "EEEEbbbbbbbbb....",
    "EEEEEbbbobbbbbbb.",
    "EEEEEbbbvbbbbbbee",
    "EEEEEbbbbbrbwwwwe",
    ".EEEEbbbbbbbwwwww",
    ".EEEEbbbbbbbdwwww",
    "..EEEbbbbbbbbdddw",
    "...EEbbbbbbbbtd..",
    "....Ebbbbbbbbw...",
]
EYE = (8, 5)                     # in HEAD


EAR_BASE = (3.0, 3.0)                    # in HEAD: where the ear hangs from


def ear_flapped(deg, head=None):
    """The hanging ear turned deg degrees about its base (positive: the tip swings back and up, out
    behind the head; negative: forward and down). Where the ear lifts off the head the skull shows;
    below the jaw, the neck behind. (Moving the ear's pixels by a fixed amount only made it shorter.)"""
    head = head or HEAD
    g = [list(r) for r in head]
    ear = {(x, y) for y, r in enumerate(head) for x, ch in enumerate(r) if ch == 'E'}
    for x, y in ear:                             # the skull behind the ear, inside the head's outline
        g[y][x] = 'b' if (y <= 9 and x >= 2) else '.'
    pad = 8
    G = [['.'] * (len(g[0]) + pad) for _ in range(len(g) + pad)]
    for y, r in enumerate(g):
        for x, ch in enumerate(r):
            if ch != '.':
                G[y + pad][x + pad] = ch
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    bx, by = EAR_BASE
    for Y in range(len(G)):
        for X in range(len(G[0])):
            x, y = X - pad - bx, Y - pad - by          # back-rotate: the tip swings back (to -x) for deg > 0
            if (round(bx + x * ca + y * sa), round(by - x * sa + y * ca)) in ear:
                G[Y][X] = 'E'
    return rows_of(G), -pad, -pad
HEAD_X, HEAD_Y = 22, 2           # where the head sits on the body
TOP = 2                          # rows of room above the head (looking up)


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


BW, BH = 44, 22                  # the body canvas (head included), above the legs
BACK = 9                         # the row of the back line
TRUNK = (6, 29)


def trunk(g, back=BACK, x0=TRUNK[0], x1=TRUNK[1], bottom_row=BH - 1):
    """The trunk: the thigh and the chest reach down to the legs, the belly tucks up between them;
    the rump and the chest round off."""
    for x in range(x0, x1 + 1):
        bottom = bottom_row if (x - x0 < 9 or x1 - x < 9) else bottom_row - 2
        top = back + (1 if x - x0 < 2 else 0)
        if x == x0:
            top, bottom = back + 2, bottom - 3
        if x == x0 + 1:
            bottom -= 1
        if x == x1:
            top, bottom = back + 1, bottom - 2
        for y in range(top, bottom + 1):
            g[y][x] = 'b'
    for y in range(back - 1, back + 5):                           # a thick neck up to the head
        for x in range(x1 - 8 + (back + 5 - y) // 2, x1 + 1 - (back + 5 - y) // 3):
            g[y][x] = 'b'


def shade(g, back=BACK, x0=TRUNK[0], x1=TRUNK[1], chest_bottom=BH - 1):
    for x in range(x0 + 1, x1 - 6):                               # lit back
        if g[back][x] == 'b':
            g[back][x] = 'a'
    for y in range(len(g)):                                       # shaded rump
        xs = [x for x in range(x0 + 4) if g[y][x] == 'b']
        if xs:
            g[y][xs[0]] = 'c'
    for x in range(x0 + 3, x1 - 3):                               # the belly's shadow
        ys = [y for y in range(len(g)) if g[y][x] != '.']
        if ys and ys[-1] > back + 4:
            g[ys[-1]][x] = 'x'
    for y in range(back + 3, chest_bottom + 1):                   # a pale chest
        xs = [x for x in range(len(g[0])) if g[y][x] == 'b']
        if xs:
            for x in xs[-3 if y < chest_bottom - 2 else -2:]:
                g[y][x] = 'w'


def tail(g, back=BACK, x0=TRUNK[0], pose='down'):
    """The otter tail, thick at the root: hanging down in a gentle curve, or out behind (wagging)."""
    paths = {
        'down': ((-1, 1, 3), (-2, 2, 3), (-2, 3, 3), (-3, 4, 3), (-3, 5, 2), (-3, 6, 2), (-3, 7, 2), (-2, 8, 1)),
        'out': ((-1, 1, 3), (-3, 1, 3), (-5, 2, 3), (-7, 2, 2), (-8, 3, 2), (-9, 3, 1)),
        'up': ((-1, 0, 3), (-2, -1, 3), (-3, -2, 2), (-4, -3, 2), (-5, -4, 2), (-5, -5, 1)),
        'side': ((-1, 1, 3), (-2, 2, 3), (-4, 3, 3), (-5, 4, 2), (-6, 5, 2), (-6, 6, 1)),
    }
    for dx, dy, w in paths[pose]:
        for k in range(w):
            x, y = x0 + dx + k, back + dy
            if 0 <= x < len(g[0]) and 0 <= y < len(g) and g[y][x] == '.':
                g[y][x] = 'b'


def put(g, rows, x0, y0):
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.' and 0 <= y0 + y < len(g) and 0 <= x0 + x < len(g[0]):
                g[y0 + y][x0 + x] = ch


def body(head=HEAD, hx=HEAD_X, hy=HEAD_Y, tail_pose='down', breath=False):
    g = [['.'] * BW for _ in range(BH)]
    trunk(g)
    put(g, head, hx, hy)
    shade(g)
    tail(g, pose=tail_pose)
    rows = rows_of(g)
    if breath:                                                    # the chest swells 1px
        rows = rows[1:BREATH_ROW] + [rows[BREATH_ROW]] + rows[BREATH_ROW:]
    return rows


BREATH_ROW = 15

# ---- legs: two rigid bones and a big paw, 3px thick ----------------------------------------------
LEG_ROWS = 10
BONES = {'front': (6.6, 3.6), 'hind': (4.6, 5.6)}
LEGS = {'far_hind': (7, 'l', 'q'), 'near_hind': (11, 'k', 'p'), 'far_front': (21, 'l', 'q'), 'near_front': (25, 'k', 'p')}
LEG_ORDER = ['far_hind', 'far_front', 'near_hind', 'near_front']
FRONT_FORMS = {'stand': (0, 0), 'reach': (16, 10), 'push': (-14, -22), 'lift': (-8, -105), 'fold': (-30, -125)}
HIND_FORMS = {'stand': (-18, 0), 'reach': (0, 12), 'push': (-40, -22), 'lift': (-10, 55), 'fold': (45, 105)}


def leg_pixels(kind, a1, a2, thick=3, paw=2):
    """{(x, y): pale} for one leg whose top-left pixel is (0, 0)."""
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
            for k in range(thick):
                p = (X, Y + k) if flat else (X + k, Y)
                px[p] = px.get(p, False) or (bone == 1 and t > 0.8)
        x, y = x + sx * length, y + sy * length
    bottom = max(Y for _, Y in px)
    if bottom >= LEG_ROWS - 1:                    # standing on it: a big paw, toes forward
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
        for (X, Y), pale in leg_pixels(kind, a1, a2).items():
            if 0 <= Y < LEG_ROWS and 0 <= x0 + X < w:
                g[Y][x0 + X] = sock if pale else fur
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


WALK_EARS = [0, 14, 0, 14]                               # a gentle flap each step (degrees)


def walk_frames():
    out = {}
    for f in range(4):
        a, b = STEP[f], STEP[(f + 2) % 4]
        poses = {'near_hind': a, 'far_front': a, 'far_hind': b, 'near_front': b}
        head = ear_flapped(WALK_EARS[f])
        out[f'walk_{f}'] = rows_of(place(with_legs(body_with_head(head, tail_pose=('down', 'side', 'down', 'side')[f]), poses), PX))
    return out


def flex(rows, d, at=15):
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


# a dog's gallop (as the shiba's): front paws land, push off as the hind legs swing forward, all four
# gather under the body with the rump pulled in, the hind paws land ahead, push off as the front legs
# reach, and it flies stretched out 1px up; the tail streams out behind
RUN = [
    ({'far_front': (20, 10), 'near_front': (10, 2), 'far_hind': (-70, -60), 'near_hind': (-58, -40)}, 0, 0),
    ({'far_front': (-20, -30), 'near_front': (-10, -18), 'far_hind': (10, 65), 'near_hind': (0, 40)}, 0, 1),
    ({'far_front': (-30, -115), 'near_front': (-40, -125), 'far_hind': (50, 105), 'near_hind': (40, 90)}, 0, 1),
    ({'far_front': (50, 30), 'near_front': (40, 15), 'far_hind': (18, 10), 'near_hind': (8, 2)}, 0, 0),
    ({'far_front': (70, 60), 'near_front': (60, 45), 'far_hind': (-32, -22), 'near_hind': (-22, -12)}, 0, -1),
    ({'far_front': (82, 80), 'near_front': (76, 70), 'far_hind': (-80, -80), 'near_hind': (-74, -68)}, 1, -1),
]


# the ears bounce with the gallop: flung down on each landing, up and back in the air, streaming out
# behind at full stretch
RUN_EARS = [-10, 20, 50, -10, 30, 65]                  # flung forward on landing, out behind in the air


def run_frames():
    return {f'run_{f}': rows_of(place(with_legs(flex(body_with_head(ear_flapped(RUN_EARS[f]), tail_pose='out'), d), poses, d), PX, lift))
            for f, (poses, lift, d) in enumerate(RUN)}


# ---- head directions ---------------------------------------------------------------------------------
# The whole head turns on the neck (it was only moved up and down, the eye keeping its place on the
# face and the muzzle still level): rotated about the back of the jaw, the muzzle swings up (or down)
# and the eye with it along the arc, the ears swinging the other way. Turned pixel by pixel the eye and
# the nose broke up, so they are redrawn whole at their turned places.
PIVOT = (4.0, 11.0)                      # in HEAD: the back of the jaw, where the neck joins
PAD = 6                                  # room around the head for the turn


def head_turned(deg, head=None, mouth=True):
    """(rows, dx, dy): the head turned deg degrees (negative: muzzle up), on a padded grid whose
    top-left sits (dx, dy) from the head's usual top-left."""
    head = head or HEAD
    h, w = len(head), len(head[0])
    src = {(x, y): ch for y, r in enumerate(head) for x, ch in enumerate(r) if ch != '.'}
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    px, py = PIVOT
    G = [['.'] * (w + 2 * PAD) for _ in range(h + 2 * PAD)]
    for Y in range(h + 2 * PAD):
        for X in range(w + 2 * PAD):
            x, y = X - PAD - px, Y - PAD - py                    # back-rotate into the source head
            ch = src.get((round(px + x * ca + y * sa), round(py - x * sa + y * ca)))
            if ch:
                G[Y][X] = ch
    fwd = lambda x, y: (round(PAD + px + (x - px) * ca - (y - py) * sa), round(PAD + py + (x - px) * sa + (y - py) * ca))
    for r in G:                                              # clear the broken eye, nose and mouth ...
        for X, ch in enumerate(r):
            if ch in 'ove':
                r[X] = 'b'
            elif ch in 'dt' and mouth:
                r[X] = 'w'
    ex, ey = fwd(EYE[0], EYE[1] + 0.5)                       # ... and draw them whole
    G[ey - 1][ex], G[ey][ex] = 'o', 'v'
    nx, ny = fwd(15.5, 6.5)
    for X, Y in ((nx - 1, ny - 1), (nx, ny - 1), (nx - 1, ny), (nx, ny)):
        G[Y][X] = 'e'
    for a0, b0 in (((12, 9), (13, 10)), ((13, 10), (15, 10))) if mouth else ():   # the mouth line, redrawn straight
        (x0, y0), (x1, y1) = fwd(*a0), fwd(*b0)
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            G[round(y0 + (y1 - y0) * i / n)][round(x0 + (x1 - x0) * i / n)] = 'd'
    if mouth:
        tx, ty = fwd(13, 11)                                 # the tongue under it
        G[ty][tx] = 't'
        if G[ty][tx + 1] != '.':
            G[ty][tx + 1] = 't'
    keep = largest_part(G)                                   # drop bits cut off by the turn
    for Y, r in enumerate(G):
        for X in range(len(r)):
            if r[X] != '.' and (X, Y) not in keep:
                r[X] = '.'
    for _ in range(2):                                       # tidy the turned edge: lone pixels go
        for Y in range(1, len(G) - 1):
            for X in range(1, len(G[0]) - 1):
                n = sum(G[Y + dy][X + dx] != '.' for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if G[Y][X] != '.' and n <= 1:
                    G[Y][X] = '.'
                elif G[Y][X] == '.' and n >= 3:
                    G[Y][X] = G[Y][X - 1] if G[Y][X - 1] != '.' else G[Y][X + 1]
    return rows_of(G), -PAD, -PAD


def largest_part(G):
    """The pixels of the largest 4-connected piece of the grid."""
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


LOOK_ANGLES = {'up_fwd': -24, 'down_fwd': 20}
LOOK_DIRS = list(LOOK_ANGLES)


def body_with_head(rows_dx_dy, tail_pose='down', breath=False):
    head, dx, dy = rows_dx_dy
    rows = body(head, hx=HEAD_X + dx, hy=HEAD_Y + dy, tail_pose=tail_pose, breath=breath)
    g = [list(r) for r in rows]                              # close any gap between the chin and the chest
    for y in range(1, len(g) - 1):
        for x in range(HEAD_X, len(g[0]) - 1):
            if g[y][x] == '.' and g[y - 1][x] != '.' and g[y + 1][x] != '.' and g[y][x - 1] != '.':
                g[y][x] = 'w' if 'w' in (g[y + 1][x], g[y][x - 1]) else 'b'
    for y in range(len(g)):                                   # and short notches between the chin and the throat
        for x in range(HEAD_X, len(g[0]) - 4):
            if g[y][x] != '.' and g[y][x + 1] == '.':
                for n in (1, 2, 3):
                    if g[y][x + 1 + n] != '.' and all(g[y][x + k] == '.' for k in range(1, n + 1)):
                        for k in range(1, n + 1):
                            g[y][x + k] = g[y][x] if g[y][x] in 'bw' else 'w'
                        break
    return rows_of(filled(g))


def look_frames():
    out = {}
    for d, deg in LOOK_ANGLES.items():
        turned = head_turned(deg, HEAD[:-1] if deg > 0 else None)   # looking down the chin row tucks away
        for i, breath in enumerate((False, True)):
            out[f'idle_{i}_{d}'] = rows_of(place(with_legs(body_with_head(turned, breath=breath)), PX))
    return out


# ---- turning toward the viewer ------------------------------------------------------------------
# Face-on, drawn as its left half and mirrored: a broad crown, the ears hanging at the sides, the eyes,
# the pale muzzle with a big nose in the middle, the smiling mouth and tongue, the pale chest, the
# front legs 3px with big paws.
FRONT_HALF = [
    "....bbbb",
    "..bbbbbb",
    ".Ebbbbbb",
    "EEbbbbbb",
    "EEbbbbbb",
    "EEbobbbb",
    "EEbvbbbw",
    "EEbbbbww",
    "EEbbwwwe",
    ".EbbwwwE",
    "..bbwdwd",
    "..bbbwtt",
    "...bbbww",
    "...bbbww",
    "...bbbbw",
    "...bbbbw",
    "..bbbbbw",
    "..bbbbbb",
]
FRONT_HALF[9] = ".Ebbwwwe"
TURN_FRONT = [h + h[::-1] for h in FRONT_HALF]
FRONT_LEGS = ["..kkk......kkk.."] * 7 + ["..ppp......ppp.."] * 2 + [".pppp......pppp."]
# three-quarter: the face-on head over the side body, which is foreshortened, the tail still behind
def turn_frames():
    side = with_legs(body(head=[]), {})
    g = place(side, PX)
    top = GROUND - len(side) + 1
    for y in range(len(TURN_FRONT)):
        for x in range(len(TURN_FRONT[0])):
            X, Y = PX + 17 + x, top + HEAD_Y + y
            if TURN_FRONT[y][x] != '.':
                g[Y][X] = TURN_FRONT[y][x]
    return {'turn_a': rows_of(g), 'turn_b': rows_of(place(TURN_FRONT + FRONT_LEGS, PX + 12))}


# ---- sitting -------------------------------------------------------------------------------------
# The rump on the ground, the chest up with the front legs straight, the head (the stand head) over
# them; the folded hind leg is a lit, rounded thigh with a shadow along its front edge and its big paw
# forward on the ground; the tail lies along the ground behind.
def sinking_rump():
    """Halfway down: the hind legs fold and the rump sinks toward the ground, the chest stays up
    (with the rump left up, the folded hind legs hung in the air)."""
    rows = with_legs(body(), {'far_hind': 'fold', 'near_hind': 'fold'})
    h, w = len(rows), len(rows[0])
    g = [['.'] * w for _ in range(h)]
    for x in range(w):
        d = 5 if x < 14 else 3 if x < 18 else 1 if x < 21 else 0
        for y in range(h - 1, -1, -1):
            if rows[y][x] != '.' and y + d < h:
                g[y + d][x] = rows[y][x]
    return rows_of(filled(g))


def filled(g):
    """Fill the gaps the outside cannot reach (the shear leaves small closed holes under the belly)."""
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
                g[y][x] = 'x'
    return g


def sit_frames():
    """Sitting up, the body is seen short from the side: about as wide as the standing trunk is deep,
    a little more at the thigh (drawn as wide as the standing body it looked bloated, much narrower
    it looked like a puppy)."""
    g = [['.'] * 30 for _ in range(28)]
    hx = 10
    put(g, HEAD, hx, 0)
    for y in range(9, 28):                                        # the upright body, narrowing to the neck
        t = (y - 9) / 18
        x0 = round(12 - 4 * t - 1.6 * math.sin(math.pi * t))   # the back rounds out a little from the neck
        x1 = 23 if y < 12 else 24
        for x in range(x0, x1 + 1):
            if g[y][x] == '.':
                g[y][x] = 'b'
    for y in range(12, 22):                                       # the pale chest down the front
        xs = [x for x in range(30) if g[y][x] == 'b']
        for x in xs[-2:]:
            g[y][x] = 'w'
    for y in range(19, 28):                                       # the front legs, straight down
        for x in (19, 20, 21, 22, 23, 24):
            if x in (19, 20, 21) and y < 22:
                continue
            g[y][x] = ('k' if x > 21 else 'l') if y < 25 else ('p' if x > 21 else 'q')
    g[27][25] = 'p'
    cx, cy, rx, ry = 12, 22, 6, 5                                 # the thigh, lit, shadowed at the front
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d <= 1:
                g[y][x] = 'c' if (d > 0.65 and x > cx) else ('a' if y < cy - 1 else 'b')
    for x in range(13, 20):                                       # the hind paw forward on the ground
        g[27][x] = 'p'
    g[26][18] = 'p'
    for x, y in ((6, 27), (5, 27), (4, 27), (3, 27), (6, 26)):    # the tail along the ground
        if g[y][x] == '.':
            g[y][x] = 'b'
    for y in range(9, 28):                                        # shaded back of the body
        xs = [x for x in range(30) if g[y][x] == 'b']
        if xs:
            g[y][xs[0]] = 'c'
    rows = rows_of(g)
    return {'sit_0': rows_of(place(rows, PX + 6)),
            'sit_1': rows_of(place(rows[1:15] + [rows[15]] + rows[15:], PX + 6)),
            'sit_a': rows_of(place(sinking_rump(), PX))}


# ---- lying down ---------------------------------------------------------------------------------
# Belly down on the ground. Only the forearms and big pale paws show ahead of the chest (a long flat
# strip along the ground looked wrong), their top a shade darker than the body; the folded hind leg is a rounded thigh (lit
# on top, shadowed at the front) with its pale paw forward under the belly. (Drawn as two rows of body
# colour tucked under the chest and a few paw pixels under the rump, the legs read as part of the body.)
def lie(rows):
    g = place(rows, PX, 1)                                 # the body rests on the ground
    xs = [x for x in range(W) if g[GROUND - 1][x] != '.']
    for x in range(min(xs) + 2, max(xs) - 1):              # the belly on the ground, in shade
        g[GROUND][x] = 'x'
    # the front legs: the elbow under the chest, only the forearm and the paw showing ahead of it, the
    # forearm rising a little toward the elbow and the paws under the muzzle; the far paw a shade darker
    # beside the near one, a little ahead (stacked on top of it, it read as a lump)
    FORE = [  # (dx from the chest's front, row from the ground, key); the far paw first, the near leg over it
        (8, 1, 'q'), (9, 1, 'q'), (10, 1, 'q'), (7, 0, 'q'), (8, 0, 'q'), (9, 0, 'q'), (10, 0, 'q'), (11, 0, 'q'),
        (-2, 2, 'l'), (-1, 2, 'l'), (0, 2, 'l'), (1, 2, 'l'),
        (-3, 1, 'l'), (-2, 1, 'l'), (-1, 1, 'k'), (0, 1, 'k'), (1, 1, 'k'), (2, 1, 'k'), (3, 1, 'k'), (4, 1, 'k'),
        (5, 1, 'p'), (6, 1, 'p'), (7, 1, 'p'),
        (-3, 0, 'k'), (-2, 0, 'k'), (-1, 0, 'k'), (0, 0, 'k'), (1, 0, 'k'), (2, 0, 'k'), (3, 0, 'k'), (4, 0, 'k'),
        (5, 0, 'p'), (6, 0, 'p'), (7, 0, 'p'), (8, 0, 'p'),
    ]
    chest = max(x for x in range(W) if g[GROUND - 2][x] != '.' and x < PX + TRUNK[1] + 4)
    for dx, up, ch in FORE:
        x, y = chest + dx, GROUND - up
        if 0 <= x < W and (g[y][x] == '.' or up < 2):
            g[y][x] = ch
    cx, cy, rx, ry = PX + 11, GROUND - 5, 6, 4             # the folded thigh
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d <= 1:
                g[y][x] = 'c' if (d > 0.62 and (x > cx or y > cy)) else ('a' if y < cy - 1 else 'b')
    for x in range(PX + 12, PX + 20):                      # the hind paw forward under the belly
        g[GROUND][x] = 'c' if x == PX + 12 else 'p'
    g[GROUND - 1][PX + 18], g[GROUND - 1][PX + 19] = 'p', 'p'
    for y in range(GROUND - 3, GROUND + 1):                # the belly down on the ground: close the gap under it
        xs = [x for x in range(W) if g[y][x] != '.']
        for x in range(min(xs), min(max(xs), PX + TRUNK[1])):   # only under the body, not over the front legs
            if g[y][x] == '.' and any(g[y][k] != '.' for k in range(max(0, x - 8), x)) and any(g[y][k] != '.' for k in range(x + 1, min(W, x + 9))):
                g[y][x] = 'x'
    return rows_of(g)


def lie_frames():
    return {'lie_a': rows_of(filled([list(r) for r in rows_of(place(grounded(with_legs(body(), {n: 'fold' for n in LEGS}))[:-3], PX))])),
            'lie_0': lie(body()), 'lie_1': lie(body(breath=True))}


# ---- wagging with the whole body -------------------------------------------------------------------
# A Labrador's thick tail wags so hard the whole back end swings with it: the tail sweeps up, out and
# down while the rump swings back and forth under it (the hind legs going with the rump), the ears
# flop and the mouth stays open in a grin.
# The body and the hind legs stay put (moving the rump and hind legs together looked like sliding):
# the wag shows in the tail sweeping wide and fast and the ears flopping.
WAG = [('up', 10, None), ('side', -8, None), ('out', 18, None), ('side', -8, None)]   # tail, ear, rump roll
# (changing the rump's outline by a pixel made it heave as if breathing, so the rump stays as it is)
def rump_rolled(rows, way):
    """The rump's outline, below the tail root: a pixel rounder as it swings toward the viewer, a pixel
    flatter as it swings away (recolouring the whole thigh light or dark read as a stain)."""
    if not way:
        return rows
    g = [list(r) for r in rows]
    for y in range(BACK + 5, BH - 2):
        xs = [x for x in range(TRUNK[0] + 4) if g[y][x] != '.']
        if not xs:
            continue
        x = xs[0]
        if way == 'toward' and x > 0:
            g[y][x - 1] = 'c'
        elif way == 'away':
            g[y][x] = '.'
    return rows_of(g)


def wag_frames():
    out = {}
    for i, (pose, ear, way) in enumerate(WAG):
        rows = rump_rolled(body_with_head(ear_flapped(ear), tail_pose=pose), way)
        out[f'wag_{i}'] = rows_of(place(with_legs(rows), PX))
    return out


# ---- showing off the rubber duck ------------------------------------------------------------------------
# Carrying a yellow rubber duck in its jaws, it holds its head up proudly and prances with its tail
# going, and squeaks it twice (the duck squashes, orange marks pop out in front of it: yellow ones
# vanished against the duck). The duck is in every frame.
DUCK = [                      # 8x6: a saturated yellow with a shaded underside, an orange beak
    "....YY..",
    "...YYKYO",
    "YY.YYYYO",
    "YYYYYYy.",
    "yYYYYyy.",
    ".yyyy...",
]
DUCK_SQUASHED = [
    "....YY..",
    "YY.YYKYO",
    "YYYYYYYO",
    "yYYYYYyy",
    ".yyyyy..",
]


def draw(g, art, x, y):
    for dy, r in enumerate(art):
        for dx, ch in enumerate(r):
            if ch != '.' and 0 <= y + dy < H and 0 <= x + dx < W:
                g[y + dy][x + dx] = ch
    return g


def mouth(rows):
    """(x, y) of the tongue's first pixel, where the duck is held."""
    return next((x, y) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch == 't')


def with_duck_in_mouth(rows, squashed=False):
    """The duck held at the tongue, with its own white rim drawn over the dog (overlapping the muzzle
    its outline was lost inside the dog and the yellow merged into the coat)."""
    g = [list(r) for r in rows]
    tx, ty = mouth(rows)
    art = DUCK_SQUASHED if squashed else DUCK
    x0, y0 = tx - 1, ty - 1
    cells = {(x0 + dx, y0 + dy) for dy, r in enumerate(art) for dx, ch in enumerate(r) if ch != '.'}
    for x, y in cells:
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in cells and 0 <= ny < H and 0 <= nx < W and g[ny][nx] != '.':
                g[ny][nx] = 'W'
    draw(g, art, x0, y0)
    if squashed:                                          # the squeak
        row = [x for x, ch in enumerate(g[ty]) if ch != '.']       # the squeak, out beside the face
        left, right = min(row), max(row)
        for x, y in ((left - 2, ty), (left - 3, ty - 1), (left - 2, ty - 2), (right + 2, ty), (right + 3, ty - 1), (right + 2, ty - 2)):
            if 0 <= x < W and g[y][x] == '.':
                g[y][x] = 'O'
    return rows_of(g)


def head_holding(squashed=False):
    """HEAD with the jaws open around the duck (pasted over the smiling mouth it did not look held):
    the tongue and the mouth line go, the lower jaw drops a row, the duck sits between the jaws with
    its head sticking out past the nose, and the near lips close over its back half."""
    art = DUCK_SQUASHED if squashed else DUCK
    w, h = len(HEAD[0]) + 5, len(HEAD) + 2
    g = [['.'] * w for _ in range(h)]
    for y, r in enumerate(HEAD):
        for x, ch in enumerate(r):
            if ch == '.':
                continue
            if ch in 'dt':
                ch = 'w'
            yy = y + 1 if (y >= 10 and x >= 9) else y          # the lower jaw (not the ear) drops a row
            g[yy][x] = ch
    for y in range(9, 12):                                    # fill the dropped jaw's back
        for x in range(9, 12):
            if g[y][x] == '.':
                g[y][x] = 'b'
    x0, y0 = 11, 8
    cells = {(x0 + dx, y0 + dy): ch for dy, r in enumerate(art) for dx, ch in enumerate(r) if ch != '.'}
    lips = {(x, y): g[y][x] for (x, y) in cells if x < 14 and g[y][x] != '.' and y in (8, 9, 12, 13)}
    for (x, y), ch in cells.items():                          # the duck's rim, then the duck
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in cells and 0 <= ny < h and 0 <= nx < w and g[ny][nx] != '.':
                g[ny][nx] = 'W'
    for (x, y), ch in cells.items():
        g[y][x] = ch
    for (x, y), ch in lips.items():                           # the near lips over its back half
        g[y][x] = ch
    return rows_of(g)


def show_frames():
    """Held in the jaws from start to end (bent only 20 degrees the head could not reach the ground to
    pick the duck up, so it arrives carrying it)."""
    out = {}
    held, squeezed = head_holding(), head_holding(True)
    up = head_turned(LOOK_ANGLES['up_fwd'], held, mouth=False)
    out['show_hold'] = rows_of(place(with_legs(body(held, tail_pose='side')), PX))
    for i, (pose, lifted) in enumerate((('up', 'near_front'), ('side', 'far_front'))):   # a proud prance
        rows = with_legs(body_with_head(up, tail_pose=pose), {lifted: (30, -40)})
        out[f'show_{i}'] = rows_of(place(rows, PX))
    out['show_squeeze'] = rows_of(place(with_legs(body(squeezed, tail_pose='up')), PX))
    g = [list(r) for r in out['show_squeeze']]
    tx, ty = next((x, y) for y, r in enumerate(g) for x, ch in enumerate(r) if ch == 'O')
    for x, y in ((tx + 2, ty - 1), (tx + 3, ty - 3), (tx + 1, ty - 4), (tx + 3, ty + 1)):   # the squeak
        if 0 <= x < W and g[y][x] == '.':
            g[y][x] = 'O'
    out['show_squeeze'] = rows_of(g)
    return out


# ---- splashing in a puddle -----------------------------------------------------------------------------
# Standing in a puddle (flat water on the ground, drawn behind the paws), it stamps its front paws in
# turn, each one lifted high and slapped down, water flying up and out from it in drops; the tail goes
# and the ears flop with each stamp.
PUDDLE = (PX + 6, 34)                                     # left edge and width, on the ground


def puddle(g):
    x0, w = PUDDLE
    for x in range(x0, x0 + w):
        t = abs((x - x0) / (w - 1) * 2 - 1)
        g[GROUND][x] = 'P'
        if t < 0.8:
            g[GROUND - 1][x] = 'P' if t > 0.2 or x % 3 else 'Q'
    return g


def splashes(x, spread):
    """Drops thrown up from a paw that has just come down at x: a crown of drops rising (spread 0)
    and flying further out and up the next frame (spread 2)."""
    s = spread
    return [(x - 3 - s, GROUND - 3 - s), (x - 2 - s, GROUND - 5 - s), (x - 4 - 2 * s, GROUND - 2 - s // 2),
            (x + 1, GROUND - 5 - s), (x + 4 + s, GROUND - 3 - s), (x + 5 + s, GROUND - 5 - s),
            (x + 6 + 2 * s, GROUND - 2 - s // 2), (x + 2, GROUND - 7 - s), (x - 1 - s, GROUND - 7 - s)]


def splash_frames():
    out = {}
    near_x, far_x = PX + LEGS['near_front'][0] + 2, PX + LEGS['far_front'][0] + 2
    steps = [
        ('splash_0', {}, 'down', 0, None),
        ('splash_1', {'near_front': (30, -40)}, 'up', 16, None),
        ('splash_2', {}, 'side', -10, (near_x, 0)),
        ('splash_3', {'far_front': (30, -40)}, 'up', 16, (near_x, 2)),
        ('splash_4', {}, 'side', -10, (far_x, 0)),
        ('splash_5', {'near_front': (30, -40)}, 'up', 16, (far_x, 2)),
    ]
    for name, poses, tail_pose, ear, drop in steps:
        g = puddle(blank())
        g = place(with_legs(body_with_head(ear_flapped(ear), tail_pose=tail_pose), poses), PX, 0, g)
        if drop:
            for x, y in splashes(*drop):
                if 0 <= x < W and 0 <= y < H and g[y][x] == '.':
                    g[y][x] = 'Z'
            if drop[1] == 0:                                  # a ripple ring where the paw hit
                for dx in (-4, -3, 4, 5):
                    X = drop[0] + dx
                    if 0 <= X < W and g[GROUND - 1][X] in '.P':
                        g[GROUND - 1][X] = 'Q'
        out[name] = rows_of(g)
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
    out.update(show_frames())
    out.update(splash_frames())
    return out


ANCHOR = (PX + 16, GROUND)

if __name__ == '__main__':
    print(json.dumps(frames(), indent=1))
