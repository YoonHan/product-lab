"""Frame generator for the Djungarian dwarf hamster.

The key poses (stand, sit, rear) are drawn by hand below; everything else is derived from
them in code. assemble_hamster.py turns the result into sprites/hamster.json.

Usage: python3 tools/draft_hamster.py > /tmp/hamster-frames.json
"""
import json
import math

# Frame canvas. The hamster is small, but the canvas leaves room for the burrow mound and
# for standing up on the hind legs.
W, H = 26, 28      # tall enough for the running wheel; everything else stands on the bottom rows
GROUND = H - 1

# ---- key poses (facing right) --------------------------------------------------------------
# a-d: grey-brown fur, light to darkest (d is also the dorsal stripe along the top)
# w/x: white belly and its shadow; n: inner ear; e: nose; r: blush
# o/v: eye (top/bottom pixel; blinking turns o into fur and v into a dark lid line)
# t/u: pompom tail and its shadow; p/q: near/far foot; j: front paws held up
STAND = [
    "......dd.dd...",
    "....ddddddnd..",
    "...daaaaaaaad.",
    "..daaaaaaaaoab",
    "..dbbbaaaabvbb",
    "ttcbbbbbbbbrbe",
    "tucbbbbbbbwwww",
    "..ccbbbbwwwwx.",
    "...ccxwwwwwx..",
    "....qp...qp...",
]
SIT = [
    ".....dd.dd...",
    "....dddddnd..",
    "...daaaaaaad.",
    "...daaaaaaoab",
    "..dbbaaaaavbb",
    "..dbbbbbbbrbe",
    ".dbbbbbbbwwww",
    ".dbbbbbbwwjx.",
    ".cbbbbbbwjjx.",
    "tcbbbbbbwwwx.",
    "tucbbbbbwwwx.",
    ".ccbbbbxwwx..",
    "..ccqqppppx..",
]
REAR = [
    "....dd.dd...",
    "...dddddnd..",
    "..daaaaaaad.",
    "..daaaaaaoab",
    "..dbaaaaavbe",
    "..dbbbbbbrw.",
    "..dbbbbbbww.",
    "..dbbbbbwwj.",
    ".dbbbbbbwjj.",
    ".cbbbbbbwwx.",
    ".cbbbbbwwwx.",
    ".cbbbbbwwwwx",
    "tcbbbbbwwwwx",
    "tucbbbcxwwx.",
    "..ccqqppppx.",
]
# In-betweens from standing to sitting, drawn by hand: rotating the whole sprite shrinks the
# eye to one pixel and smears the ears and feet at this size. The rump sinks (the tail goes
# from 4 to 2 px above the ground) while the head rises; the front feet leave the ground in
# SIT_B and become the paws held at the chest.
SIT_A = [
    "......dd.dd...",
    "....ddddddnd..",
    "...daaaaaaaad.",
    "..daaaaaaaaoab",
    "..dbbbaaaabvbb",
    ".dbbbbbbbbbrbe",
    "tcbbbbbbbbwwww",
    "tucbbbbbbwwwx.",
    ".ccbbbbbwwwx..",
    "..ccxwwwwwx...",
    "...qqp...qp...",
]
SIT_B = [
    "......dd.dd...",
    ".....dddddnd..",
    "....daaaaaaad.",
    "...daaaaaaaoab",
    "..dbbbaaaaavbb",
    "..dbbbbbbbbrbe",
    ".dbbbbbbbbwwww",
    ".cbbbbbbbwwwx.",
    "tcbbbbbbwwjjx.",
    "tucbbbbbwwjx..",
    ".ccbbbbxwwx...",
    "..ccqqppp.....",
]
# Where each key pose sits on the canvas. The hind feet stay on the same columns in every
# pose, so changing pose never makes the hamster slide.
PLACE = {'stand': 6, 'sit': 6, 'rear': 6}
ANCHOR = (13, GROUND)


def blank():
    return [['.'] * W for _ in range(H)]


def place(rows, ox, dy=0):
    """Put hand-drawn rows on the canvas with their bottom row on the ground (dy moves them up)."""
    g = blank()
    top = GROUND - len(rows) + 1 - dy
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.' and 0 <= top + y < H and 0 <= ox + x < W:
                g[top + y][ox + x] = ch
    return g


def rows_of(g):
    return [''.join(r) for r in g]


# ---- stand-based frames -----------------------------------------------------------------------
SX = PLACE['stand']
STAND_TOP = GROUND - len(STAND) + 1


def S(x, y):
    """Canvas position of a pixel given in STAND coordinates."""
    return SX + x, STAND_TOP + y


def stand(breath=False, head=None):
    """The standing hamster, optionally with its top rows replaced by another head.
    Breathing in makes every column 1px taller at the same row (below the tail, and below
    any replaced head), so the round outline keeps its shape and the whole body swells
    evenly. Raising only part of the back reads as a lump coming and going."""
    rows = list(head) + STAND[len(head):] if head else list(STAND)
    if breath:
        at = max(7, len(head or []))
        rows.insert(at, rows[at])
    return place(rows, SX)


def feet(g, hind=(0, 0), front=(0, 0)):
    """Redraw the four feet. Each pair is (near dx, far dx); None lifts that foot off the ground.
    The hind pair sits under the haunch (stand x4-5), the front pair under the chest (x9-10)."""
    y = GROUND
    for x in range(W):
        g[y][x] = '.'
    for base, (near, far) in ((4, hind), (9, front)):
        if far is not None:
            x, _ = S(base + far, 0); g[y][x] = 'q'
        if near is not None:
            x, _ = S(base + 1 + near, 0)
            g[y][x] = 'p'
    return g


def idle_frames():
    out = {'stand': rows_of(stand())}
    out['idle_0'] = rows_of(stand())
    out['idle_1'] = rows_of(stand(breath=True))
    return out


# Sniffing heads, drawn by hand (rows 0-6 of STAND replaced). The whole head tilts up:
# SNIFF_MID lifts the snout 1px, SNIFF_UP (about 20 degrees) also lifts the eye and forehead.
# The jaw rises with the snout, so the outline under the chin moves too and the white throat
# shows below it; leaving rows 5-6 at the old chin column keeps the old mouth line in place.
# 45 degrees reads as throwing the head back rather than sniffing. Rotating the head in code
# does not work at this size: it is only 6px wide, and the stripe, ears and eye get mixed up.
SNIFF_MID = [
    "......dd.dd...",
    "....ddddddnd..",
    "...daaaaaaaad.",
    "..daaaaaaaaoab",
    "..dbbbaaaabvbe",
    "ttcbbbbbbbbrww",
    "tucbbbbbbbwww.",
]
SNIFF_UP = [
    "......dd.dd...",
    "....ddddddndd.",
    "...daaaaaaaoab",
    "..daaaaaaaavbe",
    "..dbbbaaaabrbw",
    "ttcbbbbbbbbww.",
    "tucbbbbbbbwww.",
]


def sniff_frames():
    return {'sniff_0': rows_of(place(SNIFF_MID + STAND[7:], SX)),
            'sniff_1': rows_of(place(SNIFF_UP + STAND[7:], SX))}


# Head directions for following the cursor while idling (rows of STAND replaced). Looking
# down tucks the face toward the chest instead of bending the head far, like the fox.
LOOK_HEADS = {
    # the back of the head keeps the standing outline (rows 1-2 start at x4 and x3); starting
    # them 1px further back made the back rise in a square corner
    'up': [
        "......dd.dd...",
        "....dddddndabe",
        "...daaaaaoabbw",
        "..daaaaaavrbw.",
        "..dbbbaaabbww.",
        "ttcbbbbbbbwww.",
        "tucbbbbbbbwww.",
    ],
    'up_fwd': SNIFF_UP,
    'down_fwd': [
        "......dd.dd...",
        "....ddddddnd..",
        "...daaaaaaaad.",
        "..daaaaaaaaod.",
        "..dbbbaaaabvab",
        "ttcbbbbbbbbrbb",
        "tucbbbbbbbwwbe",
    ],
    'down': [
        "......dd.dd...",
        "....ddddddnd..",
        "...daaaaaaaad.",
        "..daaaaaaaaab.",
        "..dbbbaaaaaabb",
        "ttcbbbbbbbbobb",
        "tucbbbbbbbbvrb",
        "..ccbbbbwwwbe.",
    ],
}
LOOK_DIRS = list(LOOK_HEADS)


def look_frames():
    return {f'idle_{i}_{d}': rows_of(stand(breath=bool(i), head=h)) for d, h in LOOK_HEADS.items() for i in range(2)}


# Turning around: the body turns toward the viewer (three-quarter view, then face-on) instead
# of the side view being squashed and flipped.
TURN_3Q = [
    "......dd..dd..",
    ".....dddnddnd.",
    "...ddaaaaaaaad",
    "..daaaaaaoaaob",
    ".dbbbaaaavbbvb",
    "tcbbbbbbbrwewb",
    "tucbbbbbbwwww.",
    ".ccbbbbwwwwwx.",
    "..ccxwwwwwwx..",
    "...qp...pqp...",
]
TURN_FRONT = [
    "..dd....dd..",
    ".ddnddddndd.",
    ".daaaaaaaad.",
    "daaoaaaaoaad",
    "dbbvbbbbvbbd",
    "cbrbweewbrbc",
    "cbbwwwwwwbbc",
    "ccbwwwwwwbcc",
    ".ccxwwwwxcc.",
    "..pp....pp..",
]


def turn_frames():
    return {'turn_a': rows_of(place(TURN_3Q, SX)), 'turn_b': rows_of(place(TURN_FRONT, SX + 1))}


# Standing tall and looking around. The body below the head stays REAR; only the head is
# redrawn. REAR_Q turns the face toward the viewer (both eyes show), REAR_FRONT faces the
# viewer. REAR_UM/REAR_UP are the sniff heads for the tall pose, drawn like SNIFF_MID/UP.
REAR_UM = [
    "....dd.dd...",
    "...dddddnd..",
    "..daaaaaaad.",
    "..daaaaaaobe",
    "..dbaaaaavrw",
    "..dbbbbbbww.",
]
REAR_UP = [
    "....dd.dd...",
    "...dddddndd.",
    "..daaaaaaoab",
    "..daaaaaavbe",
    "..dbaaaaarw.",
    "..dbbbbbbww.",
]
REAR_Q = [
    "....dd..dd..",
    "...dddnddnd.",
    "..daaaaaaaad",
    "..daaaaoaaob",
    "..dbaaavbbvb",
    "..dbbbbrwewb",
    "..dbbbbwwww.",
]
REAR_FRONT = [
    "...dd...dd..",
    "..ddnddddnd.",
    "..daaaaaaaad",
    "..daaoaaaoad",
    "..dbbvbbbvbd",
    "..dbrwwwewrb",
    "..dbbwwwwwb.",
]


def rear_frames():
    rx = PLACE['rear']
    out = {'rear_0': rows_of(place(REAR, rx)),
           'rear_mid': rows_of(place(REAR[:10] + REAR[11:], rx))}   # one body row shorter than REAR
    for name, head in (('rear_um', REAR_UM), ('rear_up', REAR_UP), ('rear_q', REAR_Q), ('rear_front', REAR_FRONT)):
        out[name] = rows_of(place(head + REAR[len(head):], rx))
    return out


# ---- helpers on hand-drawn rows -------------------------------------------------------------

def widen(rows, at, n=1):
    """Stretch every row by n px at column `at` (the pixel there is repeated). Like the
    breathing row, this lengthens the body evenly so the outline keeps its shape."""
    return [r[:at] + r[at] * n + r[at:] for r in rows]


def eyes_shut(rows):
    """Closed eyes: the top eye pixel becomes fur, the bottom one a dark lid line."""
    return [r.replace('o', 'a').replace('v', 'd') for r in rows]


# ---- lying down and sleeping ----------------------------------------------------------------
# Lying flattens the body evenly (a whole row taken out, like breathing in reverse) and the
# feet disappear under the belly; the front paws rest on the ground in front of the chest.
LIE_A = STAND[:7] + STAND[8:]
LIE = STAND[:6] + [
    "tucbbbbbbbwwww",
    ".ccbbbbbbwwwjj",
]
# Half curled (the head bowed toward the belly, eye shut): the step between lying and the ball,
# on the way to sleep and on waking up.
CURL_HALF = [
    ".....dd.dd..",
    "...ddddddnd.",
    "..daaaaaaaad",
    ".daaaaaaaaab",
    "dbbbaaaaaddb",
    "cbbbbbbbbbrb",
    "cbbbbbbbbbwe",
    "tccbbbbbbwwx",
    ".uccccxxwwx.",
]
# Sleeping curled into a ball: the face is hidden and only the ears show. The dorsal stripe
# (2px) arcs along the curled back from behind the ears down to the rump, set one pixel in from
# the edge so fur shows on both sides of it; right at the edge it reads as a shadow or outline.
# A crease arcs down the front where the tucked head meets the body, and the paws peek out at
# the bottom front.
CURL = [
    "....aaa.dd...",
    "..aadddadnd..",
    ".aadddaaaaad.",
    "aaddaaaacaaab",
    "addbbbbbcaabb",
    "addbbbbbbcbbb",
    "cddbbbbbbcbbc",
    "cbddbbbbbbcjx",
    ".ccdbbbbbcjjx",
    "..cccccccxxx.",
]
CURL_IN = CURL[:6] + CURL[5:]          # breathing in while asleep: one row taller, evenly

# z's rise from above the head, 1px a step, swaying a little and growing, then break up.
# Smaller than the fox's: glyphs of 3 and 4 px.
Z_GLYPHS = {3: ["zzz", "..z", ".z.", "zzz"], 4: ["zzzz", "..z.", ".z..", "zzzz"]}
Z_LIFE = [3, 3, 3, 4, 4, 4, 4, 4, 4, 4]


def z_pixels(age, start):
    size = Z_LIFE[age]
    cx = start[0] + age * 0.4 + 0.7 * math.sin(age * 0.8)
    cy = start[1] - age
    x0, y0 = round(cx - size / 2), round(cy - len(Z_GLYPHS[size]) / 2)
    pix = [(x0 + dx, y0 + dy) for dy, r in enumerate(Z_GLYPHS[size]) for dx, ch in enumerate(r) if ch == 'z']
    if age == len(Z_LIFE) - 2:
        pix = [p for i, p in enumerate(pix) if i % 4 != 3]
    elif age == len(Z_LIFE) - 1:
        pix = [p for i, p in enumerate(pix) if i % 2 == 0]
    return pix


SLEEP_STEPS = 16


def sleep_frames():
    out = {'lie_a': rows_of(place(LIE_A, SX)), 'lie_0': rows_of(place(LIE, SX)),
           'lie_shut': rows_of(place(eyes_shut(LIE), SX)),
           'curl_half': rows_of(place(CURL_HALF, SX)),
           'curl_0': rows_of(place(CURL, SX)), 'curl_1': rows_of(place(CURL_IN, SX))}
    head_top = (SX + 9, GROUND - len(CURL) - 3)      # z's start clear of the ears
    for i in range(SLEEP_STEPS):
        g = place(CURL_IN if i < SLEEP_STEPS // 2 else CURL, SX)
        for start in range(0, SLEEP_STEPS, 8):
            age = (i - start) % SLEEP_STEPS
            if age < len(Z_LIFE):
                for x, y in z_pixels(age, head_top):
                    if 0 <= x < W and 0 <= y < H and g[y][x] == '.':
                        g[y][x] = 'z'
        out[f'sleep_{i}'] = rows_of(g)
    return out


# ---- stretching and yawning -----------------------------------------------------------------
# The body stretches long: columns are added in the middle of the back (behind the ears, so
# they stay apart), the front feet reach forward and the hind feet push back. At full stretch
# the head lifts like SNIFF_UP and yawns: eyes shut, the lower jaw drops so the mouth opens
# forward (at most 2 rows, like the fox), and a front tooth shows under the nose. Opening
# the mouth with the head level does not read: right under the nose is already the chest.
YAWN_HEADS = {
    0: eyes_shut(SNIFF_UP),
    1: eyes_shut(SNIFF_UP[:4]) + [
        "..dbbbaaaabrig",
        "ttcbbbbbbbbwwx",
        "tucbbbbbbbwww.",
    ],
    2: eyes_shut(SNIFF_UP[:4]) + [
        "..dbbbaaaabrig",
        "ttcbbbbbbbbwii",
        "tucbbbbbbbwwwx",
    ],
}


def stretch_rows(n, reach, head=None):
    rows = (list(head) + STAND[len(head):9]) if head else STAND[:9]
    rows = widen(rows, 4, n)
    feet_row = list('.' * len(rows[0]))
    for x, ch in ((3 - reach // 2, 'q'), (4 - reach // 2, 'p'), (9 + n + reach, 'q'), (10 + n + reach, 'p')):
        feet_row[max(0, x)] = ch
    return rows + [''.join(feet_row)]


def stretch_frames():
    out = {'stretch_0': rows_of(place(stretch_rows(1, 1), SX - 1)),
           'stretch_1': rows_of(place(stretch_rows(2, 2), SX - 1)),
           'stretch_2': rows_of(place(stretch_rows(2, 2, SNIFF_UP), SX - 1))}
    for k, head in YAWN_HEADS.items():
        out[f'yawn_{k}'] = rows_of(place(stretch_rows(2, 2, head), SX - 1))
    return out


# ---- sitting: grooming and eating ----------------------------------------------------------
def sit_with(repl, width=15):
    """SIT with some rows replaced (row index -> text); rows are padded so props fit in front."""
    rows = [r.ljust(width, '.') for r in SIT]
    for y, r in repl.items():
        rows[y] = r.ljust(width, '.')
    return rows


# Grooming: the paws come up to the mouth, rub over the nose and up over the eyes (eyes shut),
# and back. The head bows the whole time: the ears move 2px forward, the eye and nose 2px down
# (the eye to rows 4-5, the nose to row 7) and the chin tucks into the chest. The arms (white fur, x) always join the paws to the
# chest so they never float.
GROOM_HEAD = {0: ".......dd.dd.", 1: ".....ddddddnd", 2: "...daaaaaaaad", 3: "...daaaaaaaab"}
GROOM = {
    0: {**GROOM_HEAD, 4: "..dbbaaaaaoab", 5: "..dbbbbbbbvbb", 6: ".dbbbbbbbbrbb", 7: ".dbbbbbbwwwbe", 8: ".cbbbbbbwwxjj"},
    1: {**GROOM_HEAD, 4: "..dbbaaaaaaab", 5: "..dbbbbbbbdbb", 6: ".dbbbbbbbbrjj", 7: ".dbbbbbbwwxjj", 8: ".cbbbbbbwwx.."},
    2: {**GROOM_HEAD, 4: "..dbbaaaaajjb", 5: "..dbbbbbbbjjb", 6: ".dbbbbbbbbrxb", 7: ".dbbbbbbwwwxe", 8: ".cbbbbbbwwx.."},
}
# Eating a sunflower seed. The seed is 3x4 (dark with a light stripe, pointed at both ends) and
# is held out in front of the mouth, so the white outline goes all the way round it; a 2x3 seed
# tucked against the face could not be seen at 2.5x. Nibbling moves the seed and paws 1px down
# and up and drops husk crumbs (k, no outline). Then the paws push it into the cheek pouch and
# the cheek puffs out over the chest and bulges 1px forward.
SEED = [".s.", "sgs", "sgs", ".s."]
SEED_HALF = [".s.", "sgs", ".s."]
SEED_LYING = [(0, 0, 's'), (1, 0, 'g'), (2, 0, 's'), (0, 1, 's'), (1, 1, 's'), (2, 1, 'g'), (3, 1, 's')]


def sit_no_paws(src=SIT, width=17):
    """The sitting rows with the paws held at the chest turned back into chest fur."""
    return [list(r.ljust(width, '.').replace('j', 'w')) for r in src]


def holding(dy=0, seed=SEED, crumbs=()):
    rows = sit_no_paws()
    top = 6 + dy - len(seed) + 1
    for j, r in enumerate(seed):
        for i, ch in enumerate(r):
            if ch != '.':
                rows[top + j][13 + i] = ch
    for x, y, ch in [(12, 6 + dy, 'j'), (13, 6 + dy, 'j'), (11, 6 + dy, 'x')] + [(11, 6 + k, 'x') for k in range(dy)]:
        rows[y][x] = ch                                  # paws under the seed, arms back to the chest
    for x, y in crumbs:
        rows[y][x] = 'k'
    return [''.join(r) for r in rows]


def seed_on_ground(src, x0, y0):
    rows = sit_no_paws(src) if src is SIT else [list(r.ljust(17, '.')) for r in src]
    for dx, dy, ch in SEED_LYING:
        rows[y0 + dy][x0 + dx] = ch
    return [''.join(r) for r in rows]


EAT = {
    'look': seed_on_ground(SIT, 12, 11),
    'pick': seed_on_ground(SIT_B, 11, 10),
    'up': holding(2),
    '0': holding(0),
    '1': holding(1, crumbs=[(14, 9)]),
    '2': holding(0, crumbs=[(15, 11)]),
    'half': holding(0, SEED_HALF),
    'half_1': holding(1, SEED_HALF, crumbs=[(13, 10)]),
    'push': sit_with({5: "..dbbbbbbbrjj", 6: ".dbbbbbbbwxx.", 7: ".dbbbbbbwwx..", 8: ".cbbbbbbwwwx."}),
    'puff': sit_with({5: "..dbbbbbbbrbe", 6: ".dbbbbbbbbbbw", 7: ".dbbbbbbbbbbx", 8: ".cbbbbbbbwjjx"}),
    'chew': sit_with({5: "..dbbbbbbbrbe", 6: ".dbbbbbbbbbbw", 7: ".dbbbbbbbbbx.", 8: ".cbbbbbbbwjjx"}),   # the cheek wobbles 1px
}


def sit_frames():
    out = {f'groom_{k}': rows_of(place(sit_with(v), PLACE['sit'])) for k, v in GROOM.items()}
    for k, rows in EAT.items():
        out[f'eat_{k}'] = rows_of(place([r.ljust(17, '.') for r in rows], PLACE['sit']))
    return out


# ---- running --------------------------------------------------------------------------------
# A fast scurry in four frames: gathered (feet bunched under the belly), push off (the body
# stretches 1px long and rises 1px, the front feet reach), stretched out (feet spread front
# and back), landing. Stretching and rising are done evenly (a column and a row repeated), so
# the round outline never gets a bump.
RUN = [
    # (stretch, rise, hind feet (near, far) dx, front feet (near, far) dx); None = lifted
    (0, False, (1, 1), (-1, -1)),
    (1, True, (-1, 0), (1, None)),
    (1, True, (-2, -1), (2, 1)),
    (0, False, (0, -1), (1, 0)),
]


def run_rows(n, rise, hind, front):
    rows = widen(STAND[:9], 4, n) if n else list(STAND[:9])
    if rise:
        rows.insert(7, rows[7])
    feet_row = ['.'] * len(rows[0])
    for base, (near, far) in ((4, hind), (9 + n, front)):
        if far is not None:
            feet_row[base + far] = 'q'
        if near is not None:
            feet_row[base + 1 + near] = 'p'
    return rows + [''.join(feet_row)]


def run_frames():
    return {f'run_{i}': rows_of(place(run_rows(*f), SX)) for i, f in enumerate(RUN)}


# ---- digging and hiding in the bedding -------------------------------------------------------
# The app draws the hamster on the bottom edge of the screen, so it cannot dig down below the
# ground line. Instead it digs where it stands: bedding flies back over its shoulders and
# piles up around it, it burrows into the pile until only a mound is left, and it pokes its
# face out of the top. The mound is centred on the anchor, so nothing drifts sideways.
MOUND_CX, MOUND_RX = 13.5, 10.5
# y: light shavings, h: shavings in shade, m: the shaded underside of the pile


def mound(g, h, rx=MOUND_RX, cx=MOUND_CX, seed=0):
    """Draw a bedding mound h px tall in front of whatever is already there.

    A clean half-ellipse reads as rice in a bowl, so the pile is loose: the peak sits off
    centre with a steeper side and a longer, gentler side with a second, smaller shoulder of
    shavings on it, the top edge is a little lumpy, and a few shavings lie around the foot. The shavings show as slanted strands (h) in the
    pale fill, not as dots: dots read as grains of rice."""
    if h <= 0:
        return g
    peak = cx + 0.18 * rx                     # the peak leans toward the front
    left, right = rx * 1.12, rx * 0.88        # a long gentle back slope, a steeper front
    tops = {}
    for x in range(W):
        d = x + 0.5 - peak
        u = d / (left if d < 0 else right)
        if abs(u) >= 1:
            continue
        lump = 0.06 * math.sin(x * 1.9 + seed) + 0.05 * math.sin(x * 3.7 + 2 * seed)
        height = h * (1 - u * u) ** 0.8 * (1 + lump)
        sd = (x + 0.5 - (peak - 0.55 * left)) / (0.35 * left)     # a smaller shoulder of shavings on the back slope
        if abs(sd) < 1:
            height = max(height, 0.62 * h * (1 - sd * sd) ** 0.8)
        tops[x] = GROUND - max(1, round(height)) + 1
    for x, top in tops.items():
        u = (x + 0.5 - peak) / (left if x + 0.5 < peak else right)
        for y in range(max(0, top), GROUND + 1):
            if y == top:
                ch = 'y'
            elif y == GROUND:
                ch = 'm'
            elif y == GROUND - 1 or (u > 0.55 and y > top + 1):
                ch = 'h'
            else:
                ch = 'h' if (x + 2 * (y + 19 - GROUND)) % 5 == 0 else 'y'   # strands counted from the ground
            g[y][x] = ch
    if h >= 3 and tops:                       # loose shavings around the foot of the pile
        x0, x1 = min(tops), max(tops)
        for x, y in ((x0 - 2, GROUND), (x1 + 2, GROUND), (x1 + 1, GROUND - 1 if h > 5 else GROUND)):
            if 0 <= x < W and g[y][x] == '.':
                g[y][x] = 'h'
    return g


# Flying shavings are little curls and slivers of 2-3 px (f light, l shaded), drawn without
# the white outline, which would turn them into stars. Single pixels read as grains of rice.
FLAKES = [
    [(0, 0, 'f'), (1, 0, 'l')],                  # a sliver
    [(0, 0, 'f'), (1, 1, 'l')],                  # a sliver on edge
    [(0, 0, 'f'), (1, 0, 'f'), (1, 1, 'l')],     # a curl
    [(0, 1, 'l'), (1, 0, 'f')],
]


def bits(g, pts):
    """Flying shavings at (x, y[, flake]) canvas positions."""
    for p in pts:
        x, y = p[:2]
        for dx, dy, ch in FLAKES[p[2] if len(p) > 2 else 0]:
            if 0 <= x + dx < W and 0 <= y + dy < H and g[y + dy][x + dx] == '.':
                g[y + dy][x + dx] = ch
    return g


# Digging: head down (the LOOK 'down' head), the front paws scratch in turn and shavings fly
# back over the shoulders (canvas coordinates). The shavings pile up in two heaps, at the nose
# and (bigger, since they are thrown back) behind the rump, growing a step every stroke cycle,
# so the scratching paws stay in view while the pile visibly builds up.
# (x, rows above the ground, flake)
DIG_BITS = [[(7, 11, 2), (4, 8, 0)], [(5, 13, 1), (2, 10, 3)], [(3, 14, 0), (6, 11, 3), (1, 7, 1)], [(2, 12, 2), (5, 9, 0)]]
DIG_PAWS = [((0, 0), (1, None)), ((0, 0), (-1, 1)), ((0, 0), (None, 0)), ((0, 0), (1, -1))]
# (front, back, near) height per stroke cycle: at the nose, behind the rump (bigger, since the
# shavings are thrown back), and in front of the body on the viewer's side, drawn over the feet
# and belly so the hamster sits in the growing pile
DIG_HEAPS = [(0, 1, 0), (1, 1, 1), (1, 2, 1), (2, 2, 2), (2, 3, 2), (3, 3, 3)]


def heaps(g, front, back, near=0):
    """The digging heaps, the side ones topped with a couple of loose curls of shaving."""
    mound(g, front, rx=3.0, cx=22.0)
    mound(g, back, rx=3.5 + 0.5 * back, cx=3.5)
    mound(g, near, rx=5.5, cx=12.0)
    for cx, h, flake in ((21, front, 2), (3, back, 3)):
        if h >= 2:
            for x, y, ch in FLAKES[flake]:
                yy = GROUND - h - 1 + y
                if 0 <= yy < H and g[yy][cx + x] == '.':
                    g[yy][cx + x] = ch
    return g


def bowed(g, k=0.2, pivot=6):
    """Tip the body toward the ground like the fox's digging bow: every column moves by
    round((x - pivot) * k), so the chest and head come down 1px and the rump goes up 1px while
    the columns over the hind feet stay put (the legs never leave the ground). The feet row is
    left empty for dig_paws to draw."""
    out = blank()
    for x in range(W):
        dy = round((x - SX - pivot) * k)
        for y in range(GROUND):
            if g[y][x] != '.' and y + dy <= GROUND:
                out[y + dy][x] = g[y][x]
    return out


def dig_paws(g, hind, front):
    """The feet on the ground row, drawn over the lowered chest (without clearing it)."""
    for base, (near, far) in ((4, hind), (9, front)):
        if far is not None:
            g[GROUND][S(base + far, 0)[0]] = 'q'
        if near is not None:
            g[GROUND][S(base + 1 + near, 0)[0]] = 'p'
    return g


def dig_frames():
    out = {}
    head = LOOK_HEADS['down']
    for c, (f, b, n) in enumerate(DIG_HEAPS):
        for i in range(4):
            g = bowed(stand(head=head, breath=bool(i % 2)))   # bowed to the ground; the body pumps 1px with each stroke
            dig_paws(g, *DIG_PAWS[i])
            bits(g, [(x, GROUND - up, f) for x, up, f in DIG_BITS[i]])
            out[f'dig_{c}_{i}'] = rows_of(heaps(g, f, b, n))
    f, b, n = DIG_HEAPS[-1]
    for k, (df, db) in enumerate(((1, 1), (2, 2))):     # done digging: the heaps slump and scatter
        g = stand(); bits(g, [(1, GROUND - 3 - k, 1), (23, GROUND - 4 + k, 3)])
        out[f'dig_end_{k}'] = rows_of(heaps(g, f - df, b - db, n - df - 1))
    # burrowing in: the hamster sinks its head, the pile rises over it
    for k, h in enumerate((5, 7, 9)):
        g = dig_paws(bowed(stand(head=head)), (0, 0), (0, 0)) if k < 2 else stand(head=LOOK_HEADS['down_fwd'])
        if k == 0:
            heaps(g, f, b, n)                           # the heaps from digging are swallowed by the rising pile
        out[f'burrow_{k}'] = rows_of(mound(g, h))
    out['mound_0'] = rows_of(mound(blank(), 10))
    out['mound_1'] = rows_of(mound(blank(), 10, rx=MOUND_RX + 0.4))     # the mound breathes
    # the face pops out of the top, facing the viewer; it can look to either side
    face = TURN_FRONT[:6]
    fx = SX + 1
    for k, rise in enumerate((4, 6, 7)):
        g = blank()
        top = GROUND - 10 - rise + 3
        for y, r in enumerate(face):
            for x, ch in enumerate(r):
                if ch != '.' and 0 <= top + y < H:
                    g[top + y][fx + x] = ch
        out[f'peek_{k}'] = rows_of(mound(g, 10))
    # looking to either side: the three-quarter head (REAR_Q), mirrored for the other side,
    # both centred over the mound like the face-on head
    for name, rows, ox in (('peek_left', [r[::-1] for r in REAR_Q[:6]], SX + 2), ('peek_right', REAR_Q[:6], SX)):
        g = blank(); top = GROUND - 10 - 7 + 3
        for y, r in enumerate(rows):
            for x, ch in enumerate(r):
                if ch != '.':
                    g[top + y][ox + x] = ch
        out[name] = rows_of(mound(g, 10))
    # coming out: the face-on head pokes out (eyes 1px closer together than when peeking), the
    # hamster pushes up through the top (three-quarter view, eyes 1px closer than when turning),
    # and the pile slumps and scatters
    front_close = [r[:7] + ('o' if r[8] == 'o' else 'v' if r[8] == 'v' else r[7]) + r[7] + r[9:]
                   if ('o' in r[8:9] or 'v' in r[8:9]) else r for r in TURN_FRONT]
    q_close = [r[:9] + ('a' if r[9] in 'ov' else r[9]) + (r[9] if r[9] in 'ov' else r[10]) + r[11:] for r in TURN_3Q]
    for k, rise in enumerate((4, 6, 7)):
        g = blank()
        top = GROUND - 10 - rise + 3
        for y, r in enumerate(front_close[:6]):
            for x, ch in enumerate(r):
                if ch != '.' and 0 <= top + y < H:
                    g[top + y][fx + x] = ch
        out[f'emerge_peek_{k}'] = rows_of(mound(g, 10))
    TURN_3Q_CLOSE = q_close
    g = place(TURN_3Q_CLOSE, SX, dy=4); out['emerge_0'] = rows_of(mound(g, 8))
    g = place(TURN_3Q_CLOSE, SX, dy=1); out['emerge_1'] = rows_of(bits(mound(g, 4), [(4, GROUND - 6), (22, GROUND - 5)]))
    g = stand(); out['emerge_2'] = rows_of(bits(mound(g, 2), [(2, GROUND - 3), (24, GROUND - 2), (6, GROUND - 7)]))
    g = stand(); out['emerge_3'] = rows_of(bits(mound(g, 1), [(1, GROUND), (25, GROUND - 1)]))
    return out


# ---- running in the wheel ---------------------------------------------------------------------
# A solid-backed plastic wheel (W disc, R rim, S ribs, H hub) on an A-frame stand (F), drawn
# behind the hamster, which runs in place on the inside of the rim. The wheel is a true circle,
# 26px across (about twice the hamster's length, like a real wheel): its centre sits on a pixel
# corner so it is as wide as it is tall. A wheel only a little bigger than the hamster made the
# spread feet poke out through the rim. The disc has 8 ribs, so turning it by 45 degrees looks
# the same: the spin is drawn in 8 steps of 5.625 degrees. Slow: 1 step a frame; full speed:
# 3 steps (16.9 degrees) a frame; both join up after 8 frames. Anything under 4 steps (half a
# rib apart) reads as turning forward; 4 steps would flip between two looks with no direction,
# and more would seem to turn backward. The bottom of the wheel moves backward under the feet
# (clockwise).
WHEEL_C, WHEEL_R = (13.0, 13.0), 13.0


def wheel_rings():
    """The wheel's pixels: the disc, and a rim of exactly two pixel rings: the disc pixels that
    touch the outside (sideways or up/down), then the ones touching those the same way. Every
    column across the top and bottom and every row down the sides then has exactly 2 rim
    pixels. Cutting the rim as 'within 1.5px of the edge' gave 1px in some columns and rows
    (thin spots), and adding diagonal neighbours gave 3px in others."""
    cx, cy = WHEEL_C
    disc = {(x, y) for y in range(H) for x in range(W) if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= WHEEL_R ** 2}
    near = lambda x, y: ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
    outer = {p for p in disc if any(q not in disc for q in near(*p))}
    inner = {p for p in disc - outer if any(q in outer for q in near(*p))}
    return disc, outer | inner


WHEEL_DISC, WHEEL_RIMSET = wheel_rings()


def wheel(g, step):
    import math
    cx, cy = WHEEL_C
    rot = math.radians(step * 45 / 8)
    for (x, y) in WHEEL_DISC:
        dx, dy = x + 0.5 - cx, y + 0.5 - cy
        r = math.hypot(dx, dy)
        if (x, y) in WHEEL_RIMSET:
            ch = 'R'
        elif r < 2.0:
            ch = 'H'
        else:
            a = (math.atan2(dy, dx) - rot) % (math.pi / 4)
            off = min(a, math.pi / 4 - a) * r                  # distance from the nearest rib, in px
            ch = 'S' if off < 0.55 else 'W'                    # a rib, about 1px wide
        g[y][x] = ch
    # the A-frame stand in front of the disc: from the hub down to a foot on each side
    for t in range(1, GROUND - int(cy) + 1):
        for sx in (-1, 1):
            x = math.floor(cx + sx * (0.5 + t * 0.55)) if sx > 0 else math.floor(cx - 0.5 - t * 0.55)
            y = int(cy) + t
            if 0 <= y < H and 0 <= x < W and (g[y][x] in 'WS' or g[y][x] == '.'):
                g[y][x] = 'F'
    return g


def wheel_floor(x):
    """The row the feet stand on at column x: the lowest disc row just above the rim."""
    rows = [y for (xx, y) in WHEEL_DISC if xx == x and (xx, y) not in WHEEL_RIMSET and y > WHEEL_C[1]]
    return max(rows) if rows else None


def in_wheel(rows, step):
    """The hamster (rows with its feet on the last row) on the inside of the wheel. The body sits
    on the lowest point of the curve; each foot then follows the curve up to the floor under
    it, so no foot pokes through the rim."""
    g = wheel(blank(), step)
    floor = wheel_floor(round(WHEEL_C[0] - 0.5))
    top = floor - len(rows) + 1
    feet = []
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch == '.':
                continue
            X, Y = SX + x, top + y
            if y == len(rows) - 1:
                feet.append((X, ch))
            else:
                g[Y][X] = ch
    for X, ch in feet:
        f = wheel_floor(X)
        if f is not None:
            g[min(f, floor)][X] = ch                             # raised where the floor curves up
    return g


def wheel_frames():
    out = {f'wheel_stand_{k}': rows_of(in_wheel(STAND, k)) for k in range(8)}
    for i, f in enumerate(RUN):
        for k in range(8):
            out[f'wheel_run_{i}_{k}'] = rows_of(in_wheel(run_rows(*f), k))
    return out


# Walk: each foot steps through planted-forward, planted-mid, planted-back, lifted. The near
# hind and far front feet move together, the other diagonal half a cycle later.
WALK_PHASES = [1, 0, -1, None]


def walk_frames():
    out = {}
    for f in range(4):
        a, b = WALK_PHASES[f], WALK_PHASES[(f + 2) % 4]
        g = stand(breath=bool(f % 2))   # the body bobs 1px on every other step
        out[f'walk_{f}'] = rows_of(feet(g, hind=(a, b), front=(b, a)))
    return out


def frames():
    out = {}
    out.update(idle_frames())
    out.update(sniff_frames())
    out.update(walk_frames())
    out['sit_a'] = rows_of(place(SIT_A, PLACE['sit']))
    out['sit_b'] = rows_of(place(SIT_B, PLACE['sit']))
    out['sit_0'] = rows_of(place(SIT, PLACE['sit']))
    out.update(rear_frames())
    out.update(look_frames())
    out.update(turn_frames())
    out.update(sleep_frames())
    out.update(stretch_frames())
    out.update(sit_frames())
    out.update(run_frames())
    out.update(dig_frames())
    out.update(wheel_frames())
    return out


if __name__ == '__main__':
    print(json.dumps(frames(), indent=1))
