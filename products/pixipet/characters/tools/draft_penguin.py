"""Frame generator for the emperor penguin (and its chick).

The key poses and every head direction are drawn by hand below: the head is only 7px wide,
too small to rotate in code. Everything else is derived from them. assemble_penguin.py turns
the result into sprites/penguin.json.

Usage: python3 tools/draft_penguin.py > /tmp/penguin-frames.json
"""
import json

# Frame canvas: room behind and in front of the standing penguin for the belly slide and the
# fall, and in front of it for the chick.
W, H = 38, 32        # tall enough for a fish dropping from above into the bill
GROUND = H - 1
PX = 14                  # x of the stand pose's left edge: room behind it for the slide's snow spray

# ---- palette keys ------------------------------------------------------------------------------
# K/k: black back and head, its sheen on top; F/f: flipper, its lit front edge
# w/x: white belly, its shadow; Y/y: pale yellow breast, orange-yellow ear patch
# B/j: bill, the orange stripe on the lower bill; o: eye (blinking turns it into sheen)
# p/q: near/far foot; N/n/i: fish back, belly and eye; e/E: snow flake, faded (no outline)
# chick: G/H grey down and its shadow, W white face mask, M black cap, c eye, b bill, r/s feet

# ---- key poses (facing right) ------------------------------------------------------------------
STAND = [
    ".....kkk.....",
    "....kkkkk....",
    "...kKKKKKK...",
    "...KKKKKoKBB.",
    "...KKKKyyjBBB",
    "...KKKyyYw...",
    "..KKKKyYww...",
    "..KKKKYwww...",
    "..KKKKFwww...",
    "..KKKKFfww...",
    "..KKKKFfww...",
    "..KKKKFFww...",
    "..KKKKKFwx...",
    "..KKKKKwwx...",
    "..KKKKwwwx...",
    "..KKKKwwx....",
    "..KKKKxxx....",
    ".KKKK.xx.....",
    "...qq..pp....",
]
HEAD_ROWS = 5        # rows 0-4 are the head; look directions replace them

# Head directions, drawn by hand. Looking up lifts the bill and shows the throat; looking down
# tucks the bill toward the breast. Each keeps the back of the skull where it is so the head
# turns on the neck instead of sliding.
LOOK_HEADS = {
    'up': [
        "......kk.B...",
        "....kkkkkBj..",
        "...kKKKKoBj..",
        "...KKKKKKKY..",
        "...KKKKyyYw..",
    ],
    'up_fwd': [
        ".....kkk.....",
        "....kkkkk..BB",
        "...kKKKKKBBj.",
        "...KKKKKoKj..",
        "...KKKKyyYw..",
    ],
    'down_fwd': [
        ".....kkk.....",
        "....kkkkk....",
        "...kKKKKKK...",
        "...KKKKKoKK..",
        "...KKKKyyjBBB",
    ],
    'down': [
        "......kk.....",
        "....kkkkk....",
        "...kKKKKKK...",
        "...KKKKKKoK..",
        "...KKKKyyKjB.",
    ],
}
# 'down' also lowers the chin into the breast: row 5 gets the bill tip
DOWN_ROW5 = "...KKKyyYwB.."

# Turning around: three-quarter view (both eyes, bill below and between them, nearer the far
# eye) and face-on. Same height as the stand pose.
TURN_3Q = [
    ".....kkkk....",
    "....kkkkkk...",
    "...kKKKKKKK..",
    "...KKoKKKoKB.",
    "...KyKKKKjBB.",
    "...yyKKKKY...",
    "..KyYwwwwY...",
    "..KYwwwwww...",
    ".FKKwwwwwww..",
    ".FKKwwwwwww..",
    ".FfKwwwwwww..",
    ".FfKwwwwwww..",
    "..FKwwwwwwx..",
    "..KKwwwwwwx..",
    "..KKwwwwwwx..",
    "..KKxwwwwx...",
    "..KKKxxxx....",
    ".KKK.........",
    "...qq..pp....",
]
TURN_FRONT = [
    "....kkkkk....",
    "...kkkkkkk...",
    "..kKKKKKKKk..",
    "..KKoKKKoKK..",
    "..KKKKBKKKK..",
    "..yKKKjKKKy..",
    ".KyYwwwwwYyK.",
    ".KYwwwwwwwYK.",
    "FKwwwwwwwwwKF",
    "FKwwwwwwwwwKF",
    "FfwwwwwwwwwfF",
    ".FwwwwwwwwwF.",
    ".KwwwwwwwwwK.",
    ".KwwwwwwwwwK.",
    ".KwwwwwwwwwK.",
    ".KxwwwwwwwxK.",
    "..xxwwwwwxx..",
    "...xxxxxxx...",
    "..pp.....qq..",
]

# The chick: grey down, black cap, white face mask, flat feet showing on both sides (chosen over
# toes peeking out under the down).
CHICK_BODY = [
    "..MMMM..",
    ".MMMMMM.",
    ".MWWcWMb",
    ".MWWWWM.",
    ".GGGGGG.",
    "GGGGGGGG",
    "GGGGGGGH",
    "GHGGGGHH",
]
CHICK_FEET = [".HHHHHH.", ".ss..rr."]      # 2px feet: 3px looked too big for the body
CHICK_BOB_ROW = 5      # a row of down below the face: repeating it lifts the whole head evenly


def blank():
    return [['.'] * W for _ in range(H)]


def place(rows, ox, dy=0, g=None):
    """Put hand-drawn rows on the canvas with their bottom row on the ground (dy moves them up)."""
    g = g or blank()
    top = GROUND - len(rows) + 1 - dy
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.' and 0 <= top + y < H and 0 <= ox + x < W:
                g[top + y][ox + x] = ch
    return g


def rows_of(g):
    return [''.join(r) for r in g]


def body(breath=False, head=None, flipper=0):
    """The standing penguin as rows. Breathing in repeats one belly row so the whole body grows
    1px evenly (raising part of the outline reads as a lump). flipper=-1 swings the lower
    flipper 1px back."""
    rows = list(STAND)
    if head:
        rows[:HEAD_ROWS] = head
    if head is LOOK_HEADS['down']:
        rows[5] = DOWN_ROW5
    if flipper:
        # the flipper tip (rows 11-12) swings; its root (rows 8-10) stays on the shoulder
        for y in (11, 12):
            r = list(rows[y])
            xs = [x for x, ch in enumerate(r) if ch in 'Ff']
            for x in xs:
                r[x] = 'K' if x < 6 else 'w'
            for x in xs:
                r[x + flipper] = rows[y][x]
            rows[y] = ''.join(r)
    if breath:
        rows.insert(13, rows[13])
    return rows


def feet(rows, back=0, front=0):
    """Redraw the feet row. back/front shift the far (back) and near (front) foot by that many px;
    None lifts that foot off the ground (hidden under the belly)."""
    rows = list(rows)
    r = ['.'] * len(rows[-1])
    if back is not None:
        for x in (3 + back, 4 + back):
            r[x] = 'q'
    if front is not None:
        for x in (7 + front, 8 + front):
            r[x] = 'p'
    rows[-1] = ''.join(r)
    return rows


def stand_frames():
    out = {'stand': rows_of(place(body(), PX))}
    for i, breath in enumerate((False, True)):
        out[f'idle_{i}'] = rows_of(place(body(breath), PX))
        for d, h in LOOK_HEADS.items():
            out[f'idle_{i}_{d}'] = rows_of(place(body(breath, head=h), PX))
    return out


# Waddle: tiny steps, one foot at a time; the body rises 1px over the supporting foot and the
# flipper tips swing 1px back on every step. Swinging them forward puts a dark blot on the belly.
WADDLE = [  # (back foot, front foot, breath, flipper)
    (0, 0, False, 0),
    (0, None, True, -1),
    (0, 1, False, 0),
    (None, 1, True, -1),
]


def walk_frames():
    return {f'walk_{i}': rows_of(place(feet(body(breath, flipper=fl), b, f), PX))
            for i, (b, f, breath, fl) in enumerate(WADDLE)}


def turn_frames():
    return {'turn_a': rows_of(place(TURN_3Q, PX)), 'turn_b': rows_of(place(TURN_FRONT, PX))}


def chick_frames():
    """The chick on its own, standing in front of where the adult stands, and a 4-frame waddle:
    the body bobs 1px by repeating a row of down (repeating the top row would lift only the
    cap, like a lid) and one foot lifts on each bob."""
    cx = PX + 15
    rows = CHICK_BODY + CHICK_FEET
    up = rows[:CHICK_BOB_ROW] + [rows[CHICK_BOB_ROW]] + rows[CHICK_BOB_ROW:]
    out = {'chick_stand': rows_of(place(rows, cx))}
    for i, (r, lift) in enumerate(((rows, None), (up, 's'), (rows, None), (up, 'r'))):
        r = list(r)
        if lift:
            r[-1] = r[-1].replace(lift, '.')
        out[f'chick_walk_{i}'] = rows_of(place(r, cx))
    return out


# ---- lying on the belly: the belly slide and the fall ------------------------------------------
# Leaning forward on the way down (and back up): the body tipped about 45 degrees, flippers back.
LEAN = [
    "........kkk....",
    ".......kkkkkk..",
    "......KKKKKKKk.",
    ".....KKKKKKoKBB",
    "....KKKKKKyyjBB",
    "...KKKKKKyYww..",
    "..KKKKKKKYwww..",
    "..KKKFFfwwww...",
    ".KKKKFfwwww....",
    ".KKKFFwwwww....",
    "KKKKKwwwwx.....",
    "KKKKwwwwx......",
    ".KKxwwxx.......",
    "..qqpp.........",
]
LEAN_X = PX + 1          # keeps the feet where the standing penguin has them
# Flat on the belly, head up and forward, feet trailing behind. The near flipper lies back along
# the side; on the slide it pumps up and down and the feet kick.
BELLY = [
    "........kkkkkk.......",
    "....KKKKKKKKKKKkk....",
    "..KKKKKKKKKKKKKKKKk..",
    ".KKKKKKKKKKKKKKKKoKB.",
    "qKKKKFFFFfKKKKKyyjBBB",
    "pKKxwwwwwwwwwwwyYw...",
    "..xxxwwwwwwwwwwwwx...",
]
BELLY_X = PX - 5
BELLY_FLIPPER_UP = [(4, 3, 'F'), (5, 3, 'F'), (6, 3, 'f'), (7, 4, 'F'), (8, 4, 'f')]   # tip raised off the side
BELLY_KICK = {'q': (0, 3), 'p': (0, 5)}   # the kicking feet: one up, one down (swapped on the other frame)
_B, _G = BELLY_X, GROUND
# Snow kicked up by the feet: a lumpy puff churned up right behind them that rolls back and
# changes shape, and flakes thrown back in an arc that fall and fade (e bright, E faded; neither
# has an outline). Loose 2px dashes hanging in the air read as dust, not snow.
SPRAY_PUFF = [
    ([(_B-2, _G), (_B-3, _G), (_B-4, _G), (_B-3, _G-1), (_B-2, _G-1)], [(_B-5, _G), (_B-4, _G-1)]),
    ([(_B-2, _G), (_B-3, _G), (_B-4, _G-1), (_B-3, _G-1), (_B-5, _G)], [(_B-6, _G), (_B-5, _G-1), (_B-4, _G-2)]),
    ([(_B-2, _G), (_B-3, _G), (_B-3, _G-1), (_B-4, _G)], [(_B-5, _G-1), (_B-6, _G-1), (_B-7, _G), (_B-5, _G-2)]),
    ([(_B-2, _G), (_B-2, _G-1), (_B-3, _G), (_B-4, _G)], [(_B-6, _G), (_B-7, _G-1), (_B-8, _G), (_B-5, _G-1)]),
]
SPRAY_ARC = [(_B-2, _G-1), (_B-4, _G-2), (_B-6, _G-3), (_B-8, _G-3), (_B-10, _G-2), (_B-11, _G)]


def spray(i):
    """(bright, faded) flake cells on slide frame i of 4."""
    bright, faded = list(SPRAY_PUFF[i][0]), list(SPRAY_PUFF[i][1])
    for k in range(3):                       # three flakes, two steps apart along the arc
        s = (i + 2 * k) % len(SPRAY_ARC)
        x, y = SPRAY_ARC[s]
        (bright if s < 3 else faded).append((x, y))
        if s < 2:
            bright.append((x - 1, y))        # bigger just after the kick
    return bright, faded


def put(g, ox, rows, pixels):
    """Paint (x, y, ch) given in the coordinates of `rows` placed at ox on the ground."""
    top = GROUND - len(rows) + 1
    for x, y, ch in pixels:
        if 0 <= top + y < H and 0 <= ox + x < W:
            g[top + y][ox + x] = ch
    return g


def belly(kick=0, flipper_up=False, lift=0):
    g = place(BELLY, BELLY_X, lift)
    if flipper_up:
        top = GROUND - len(BELLY) + 1 - lift
        for x in range(4, 10):
            if g[top + 4][BELLY_X + x] in 'Ff':
                g[top + 4][BELLY_X + x] = 'K'
        for x, y, ch in BELLY_FLIPPER_UP:
            g[top + y][BELLY_X + x] = ch
    if kick:
        top = GROUND - len(BELLY) + 1 - lift
        g[top + 4][BELLY_X] = 'p'
        g[top + 5][BELLY_X] = 'q'
    return g


def belly_frames():
    out = {'lean': rows_of(place(LEAN, LEAN_X)), 'belly': rows_of(belly())}
    # sliding: the flipper pumps and the feet kick (every other frame), and snow sprays back
    for i in range(4):
        g = belly(i % 2, i % 2 == 1)
        for cells, ch in zip(spray(i), 'eE'):
            for x, y in cells:
                if 0 <= x < W and g[y][x] == '.':
                    g[y][x] = ch
        out[f'slide_{i}'] = rows_of(g)
    # the fall: a trip (front foot caught, body tipping), the lean, a thud with a 1px bounce
    trip = feet(body(flipper=-1), 0, None)
    out['trip'] = rows_of(place(trip, PX))
    out['thud'] = rows_of(belly(lift=1))
    return out


# ---- flapping ----------------------------------------------------------------------------------
# The near flipper swings out from the shoulder: up and back (its tip above the back), straight
# back, and down and back. The rest of it is painted over the belly/back where it was.
FLIPPER_PIXELS = [(x, y) for y, r in enumerate(STAND) for x, ch in enumerate(r) if ch in 'Ff']
def _shape(rows, y0, x0=0):
    """(x, y, ch) for a small drawing whose top-left is (x0, y0) in STAND coordinates."""
    return [(x0 + x, y0 + y, ch) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch != '.']


# Each flipper is a flat paddle from the shoulder, 3px wide there and tapering to a 1px tip,
# about as long as the folded flipper. The back is wide and black, so a raised flipper only reads
# where it reaches past the back's outline: 2px out is enough (3-4px looked like a long arm), with
# its pale underside (x) along the trailing edge.
FLAPS = {
    'up': _shape([
        "F.......",
        ".FFx....",
        "..FFx...",
        "...FFx..",
        "....FFx.",
        ".....FFx",
    ], 3, -1),
    'out': _shape([
        "..FFFFF",
        "FFFFFFx",
        ".xxxxx.",
    ], 7, 0),
    'down': _shape([
        ".....FFx",
        "....FFx.",
        "...FFx..",
        "..FFx...",
        ".FFx....",
        "FFx.....",
    ], 8, 0),
}


FLAP_PAD = 3          # columns added on the left for the flipper tip that reaches past the back


def flapping(pose, breath=False, head=None):
    """The standing penguin with the near flipper in one flap pose; the rows are FLAP_PAD
    columns wider on the left, so place them at PX - FLAP_PAD."""
    rows = [['.'] * FLAP_PAD + list(r) for r in body(head=head)]
    for x, y in FLIPPER_PIXELS:
        rows[y][FLAP_PAD + x] = 'w' if x >= 6 else 'K'
    for x, y, ch in FLAPS[pose]:
        rows[y][FLAP_PAD + x] = ch
    rows = [''.join(r) for r in rows]
    if breath:
        rows.insert(13, rows[13])
    return rows


def flap_frames():
    out = {}
    for pose in FLAPS:
        out[f'flap_{pose}'] = rows_of(place(flapping(pose, breath=pose == 'up', head=LOOK_HEADS['up_fwd']), PX - FLAP_PAD))
    return out


# ---- eating a fish -----------------------------------------------------------------------------
# A fish drops from above; the penguin looks up with its bill open, catches it, gulps it down
# head first (the fish gets shorter in the bill) and swallows (a bump runs down the throat).
OPEN_UP = [                        # looking up, bill open
    "......kk.B.B.",
    "....kkkkkBjB.",
    "...kKKKKoBjj.",
    "...KKKKKKKY..",
    "...KKKKyyYw..",
]


# The fish, drawn swimming to the right: forked tail, dark back with a dorsal fin, silver belly,
# a black eye behind the snout. Hanging head down (falling into the bill) it is turned a quarter.
FISH = [
    "....NN..",
    "N..NNNiN",
    ".NNnnnnn",
    "N...nn..",
]
FISH_DOWN = [''.join(FISH[len(FISH) - 1 - y][x] for y in range(len(FISH))) for x in range(len(FISH[0]))]


def fish_at(g, x, y, rows=None):
    """The fish with the tip of its head at (x, y); rows lets a gulp cut off the part in the bill."""
    rows = FISH_DOWN if rows is None else rows
    for dy, r in enumerate(rows):
        for dx, ch in enumerate(r):
            px_, py_ = x - 1 + dx, y - len(rows) + 1 + dy
            if ch != '.' and 0 <= px_ < W and 0 <= py_ < H:
                g[py_][px_] = ch
    return g


def eat_frames():
    out = {}
    bill_x, bill_y = PX + 10, GROUND - len(STAND) + 1 - 1      # just above the open bill
    for i, dy in enumerate((10, 6, 3)):                         # the fish falls, tipping head down
        g = place(body(head=OPEN_UP), PX)
        out[f'eat_fall_{i}'] = rows_of(fish_at(g, bill_x + (3 if i == 0 else 0), bill_y - dy, FISH if i == 0 else None))
    for i, keep in enumerate((5, 3, 1)):                        # gulping it down, head first
        g = place(body(head=OPEN_UP if keep > 1 else LOOK_HEADS['up']), PX)
        out[f'eat_gulp_{i}'] = rows_of(fish_at(g, bill_x, bill_y, FISH_DOWN[:keep]))
    for i, y in enumerate((5, 7)):                               # the swallow runs down the throat
        rows = [list(r) for r in body()]
        rows[y][10] = 'Y' if y == 5 else 'w'
        out[f'eat_swallow_{i}'] = rows_of(place([''.join(r) for r in rows], PX))
    return out


def frames():
    out = {}
    out.update(stand_frames())
    out.update(walk_frames())
    out.update(turn_frames())
    out.update(chick_frames())
    out.update(belly_frames())
    out.update(flap_frames())
    out.update(eat_frames())
    return out


LOOK_DIRS = list(LOOK_HEADS)
ANCHOR = (PX + 6, GROUND)

if __name__ == '__main__':
    print(json.dumps(frames(), indent=1))
