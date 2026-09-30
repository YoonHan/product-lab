"""Frame generator for the shiba inu (red; a black and tan variant reuses these frames).

The body, head views and poses are drawn by hand below; the legs are drawn in code (four 2px
legs, far legs a step darker). Proportions follow a side photo of a shiba in a show stance: about
as long as tall, legs a little under half the height, a small head carried over the chest, a big
tail curl on the rump. assemble_shiba.py turns the result into sprites/shiba.json.

Usage: python3 tools/draft_shiba.py > /tmp/shiba-frames.json
"""
import json

W, H = 38, 24            # room in front and behind for the run, above for hops
GROUND = H - 1
PX = 5

# ---- palette keys ------------------------------------------------------------------------------
# b/a/c/d: coat base/light/dark/darkest, w/x: cream (urajiro) and its shadow, n: inner ear,
# e: nose, o/v: eye (top/bottom; blinking turns o into coat and v into a dark lid line),
# r: blush, t: tongue, k/l: near/far leg, p/q: near/far cream sock, L: leash, z: motion lines,
# Z: water drops (L, z and Z have no outline)

# ---- the body (facing right) ---------------------------------------------------------------------
# Rounded ears leaning forward, a cream eyebrow dot over the eye, a short muzzle, cream from the
# muzzle down the throat to the chest (2-3 columns: wider it read as a fat throat), the underside
# tapering back from the chin; a tail curled on the rump showing its cream underside.
BODY = [
    ".................bb..bb......",
    "................bnb.bnb......",
    "....aaa........bbbbbbbb......",
    "...abbba.......bbbbbbbbb.....",
    "..abbbbba......bbbbwwbbb.....",
    "..abwwwbb......bbbbbobbbb....",
    "..abwbbbb......bbbbbvwwwwe...",
    "...abbbbbbbbbbbbbbbbrwwwd....",
    "...abbbbbbbbbbbbbbbbbwx......",
    "...abbbbbbbbbbbbbbbbwx.......",
    "...abbbbbbbbbbbbbbbwwx.......",
    "...abbbbbbbbbbbbbbbwwx.......",
    "....cbbbbbbbbbbbbbbwx........",
    ".....cbbbxxxxxxxbbwwx........",
]
BREATH_ROW = 10          # a chest row: repeating it swells the body 1px
LEG_ROWS = 7             # 5 coat, 2 cream sock
LEGS = {'far_hind': (4, 'l', 'q'), 'near_hind': (7, 'k', 'p'),       # far legs 3px off, so a gap
        'far_front': (13, 'l', 'q'), 'near_front': (16, 'k', 'p')}      # shows between the pairs
LEG_ORDER = ['far_hind', 'far_front', 'near_hind', 'near_front']
HEAD_X = 15              # the head: BODY rows 0-9 from this column on


def blank():
    return [['.'] * W for _ in range(H)]


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


# Legs with rigid bones. Shifting a leg row by row let its length stretch and bend from frame to
# frame, and it swung like a squid's tentacle; now each leg is two straight bones of fixed length
# that turn at a joint, plus the paw. A pose gives the two bone angles in degrees from straight
# down (positive = forward). The front leg is the forearm and, from the wrist, the pastern; the hind
# leg is the lower thigh (angled back from the knee) and, from the hock, the long hind foot. A paw
# on the ground points forward (3px with the toes). The whole lower bone is cream (as on a shiba's
# lower legs), so the colour changes at the wrist and hock and the bend shows.
import math
BONES = {'front': (4.6, 2.5), 'hind': (3.2, 3.9)}
FRONT_FORMS = {
    'stand': (0, 0),
    'reach': (16, 10),         # planted ahead, the leg slanting forward
    'push': (-14, -22),        # planted behind, the heel lifting
    'lift': (-8, -105),        # the wrist bends and the paw folds back
    'fold': (-30, -125),       # folded right up (lying down, sitting down)
}
HIND_FORMS = {
    'stand': (-18, 0),
    'reach': (0, 12),          # brought forward under the body
    'push': (-40, -22),        # pushing off behind
    'lift': (-10, 55),         # the hock flexes and the paw swings forward
    'fold': (45, 105),
}


def leg_pixels(kind, a1, a2):
    """{(x, y): is_cream} for one leg whose top-left pixel is (0, 0)."""
    l1, l2 = BONES[kind]
    px = {}
    x, y = 0.0, 0.0
    for bone, (ang, length) in enumerate(((a1, l1), (a2, l2))):
        sx, sy = math.sin(math.radians(ang)), math.cos(math.radians(ang))
        steps = int(length * 4)
        for i in range(steps + 1):
            t = length * i / steps
            X, Y = round(x + sx * t), int(y + sy * t)
            if Y < 0:
                continue
            cream = bone == 1 and t > 0.6
            flat = abs(ang) > 55
            for p in ((X, Y), (X, Y + 1) if flat else (X + 1, Y)):
                px[p] = px.get(p, False) or cream
        x, y = x + sx * length, y + sy * length
    bottom = max(Y for _, Y in px)
    if bottom >= LEG_ROWS - 1:                       # standing on it: the toes point forward
        right = max(X for X, Y in px if Y == bottom)
        px[(right + 1, bottom)] = True
    return px


def with_legs(body, poses=None, hind_dx=0):
    """The body rows plus four legs; poses maps a leg to a form name (None: 'lift') or a pair of
    bone angles. hind_dx moves the hind legs with the rump (the spine flexing on the run)."""
    poses = poses or {}
    width = len(body[0])
    legs = [['.'] * width for _ in range(LEG_ROWS)]
    for name in LEG_ORDER:
        x0, fur, sock = LEGS[name]
        kind = 'hind' if 'hind' in name else 'front'
        if kind == 'hind':
            x0 += hind_dx
        form = poses.get(name, 'stand')
        forms = HIND_FORMS if kind == 'hind' else FRONT_FORMS
        a1, a2 = forms['lift' if form is None else form] if isinstance(form, (str, type(None))) else form
        for (X, Y), cream in leg_pixels(kind, a1, a2).items():
            if 0 <= Y < LEG_ROWS and 0 <= x0 + X < width:
                legs[Y][x0 + X] = sock if cream else fur
    return list(body) + [''.join(r) for r in legs]


def flex(body, d, at=12):
    """The spine flexing on the run: the rump and tail (columns before at) move d columns
    (+1 gathered, -1 stretched out)."""
    out = []
    for r in body:
        rear, front = r[:at], r[at:]
        if d > 0:
            rear = '.' * d + rear[:-d]
        elif d < 0:
            rear = rear[-d:] + rear[-1] * -d
        out.append(rear + front)
    return out


def breathe(rows, at=BREATH_ROW):
    return rows[:at] + [rows[at]] + rows[at:]


def stand_frames():
    out = {'stand': rows_of(place(with_legs(BODY), PX))}
    out['idle_0'] = out['stand']
    out['idle_1'] = rows_of(place(with_legs(breathe(BODY)), PX))
    return out


# ---- walking and running ---------------------------------------------------------------------------
# Walking: diagonal pairs together, half a cycle apart; a planted paw goes from 1px forward to 1px
# back over two frames while the body moves 1px a frame. The body does not bob: with the longer,
# jointed legs the stepping reads on its own, and a 1px bob every other frame bounced.
STEP = ['reach', 'stand', 'push', None]


def walk_frames():
    out = {}
    for f in range(4):
        a, b = STEP[f], STEP[(f + 2) % 4]
        poses = {'near_hind': a, 'far_front': a, 'far_hind': b, 'near_front': b}
        out[f'walk_{f}'] = rows_of(place(with_legs(BODY, poses), PX))
    return out


# Running: a dog's gallop, not a horse's: the legs fold flat under the body and stretch out flat,
# and the back flexes. Front paws land, push off as the hind legs swing forward, all four gather under
# the body (the rump comes forward), the hind paws land ahead, push off as the front legs reach, and
# the dog flies stretched out (the rump back, the body 1px up, once a stride).
# (leg forms, lift, spine flex)
RUN = [
    ({'far_front': (20, 10), 'near_front': (10, 2), 'far_hind': (-70, -60), 'near_hind': (-58, -40)}, 0, 0),
    ({'far_front': (-20, -30), 'near_front': (-10, -18), 'far_hind': (10, 65), 'near_hind': (0, 40)}, 0, 1),
    ({'far_front': (-30, -115), 'near_front': (-40, -125), 'far_hind': (50, 105), 'near_hind': (40, 90)}, 0, 1),
    ({'far_front': (50, 30), 'near_front': (40, 15), 'far_hind': (18, 10), 'near_hind': (8, 2)}, 0, 0),
    ({'far_front': (70, 60), 'near_front': (60, 45), 'far_hind': (-32, -22), 'near_hind': (-22, -12)}, 0, -1),
    ({'far_front': (82, 80), 'near_front': (76, 70), 'far_hind': (-80, -80), 'near_hind': (-74, -68)}, 1, -1),
]


def run_frames():
    return {f'run_{f}': rows_of(place(with_legs(flex(BODY, d), poses, d), PX, lift))
            for f, (poses, lift, d) in enumerate(RUN)}


# ---- head directions (mouse tracking) -----------------------------------------------------------
# The head turns on the neck as a whole. Looking up, the crown and ears tip back a column and the
# muzzle comes up 2 rows, showing more cream under the jaw; looking down, the head drops 2 rows
# where it is (moved forward too, it read as poking the head out) and the nose tucks under the muzzle. Each replaces BODY rows 0-9 from HEAD_X on.
LOOK_HEADS = {
    'up_fwd': [
        "................bb..bb.......",
        "...............bnb.bnb.......",
        "...............bbbbbbbb......",
        "...............bbbbwwbbb.....",
        "...............bbbbbobbwwe...",
        "...............bbbbbvwwwwd...",
        "...............bbbbbrwwwx....",
        "...............bbbbbwwwx.....",
        "...............bbbbbwwx......",
        "...............bbbbbwx.......",
    ],
    'down_fwd': [                  # the whole head lowered 2 rows in place, the nose tucked under
        ".............................",
        ".............................",
        ".................bb..bb......",
        "................bnb.bnb......",
        "...............bbbbbbbb......",
        "...............bbbbbbbbb.....",
        "...............bbbbwwbbb.....",
        "...............bbbbbobbbb....",
        "...............bbbbbvwwwww...",
        "...............bbbbbrwwwe....",
    ],
}
LOOK_DIRS = list(LOOK_HEADS)


def with_head(head, body=None):
    rows = list(body or BODY)
    for y, r in enumerate(head):
        rows[y] = rows[y][:HEAD_X] + r[HEAD_X:]
    return rows


def look_frames():
    out = {}
    for d, head in LOOK_HEADS.items():
        body = with_head(head)
        for i, breath in enumerate((False, True)):
            out[f'idle_{i}_{d}'] = rows_of(place(with_legs(breathe(body) if breath else body), PX))
    return out


# ---- turning toward the viewer ------------------------------------------------------------------
# Face-on: drawn as its left half and mirrored so it is exactly symmetric: rounded ears, cream
# eyebrow dots, the eyes, the cream muzzle and cheeks (the urajiro mask), the nose in the middle,
# the cream throat and chest, the front legs with cream socks.
FRONT_HALF = [                     # 12px wide; the cheeks stay full down to the nose row and round off
    "..bb..",                      # to the chin (14px was broad, tapering from the eyes read as a triangle)
    ".bnb..",
    ".bnbbb",
    "bbbbbb",
    "bbwbbb",
    "bbobbb",
    "bbvbww",
    "bwwwww",
    "bwwwwe",
    ".bwwwd",
    "..bwww",
    "..bbww",
    "..bbbw",
    "..bbbw",
]
TURN_FRONT = [h + h[::-1] for h in FRONT_HALF]
FRONT_LEGS = ["..kk....kk..", "..kk....kk..", "..kk....kk..", "..kk....kk..", "..kk....kk..",
              "..pp....pp..", ".ppp....ppp."]
# Three-quarter: the face-on head over the side body, which is foreshortened (the middle of the
# back dropped) with the tail curl still showing behind.
BODY_3Q = [
    "....aaa.........",
    "...abbba........",
    "..abbbbba.......",
    "..abwwwbb.......",
    "..abwbbbb.......",
    "...abbbbbbbbbbbb",
    "...abbbbbbbbbbbb",
    "...abbbbbbbbbbbb",
    "...abbbbbbbbbbbb",
    "...abbbbbbbbbbbb",
    "....cbbbbbbbbbbb",
    ".....cbbbxxxxbbb",
]
# the hind legs under the side body, the front legs under the face-on chest
LEGS_3Q = [".....lkk.....kk....kk..."] * 5 + [".....qpp.....pp....pp...", ".....qppp...ppp...ppp.."]


def turn_frames():
    g = place(BODY_3Q + LEGS_3Q, PX + 2)
    top = GROUND - LEG_ROWS - len(TURN_FRONT) + 1
    for y, r in enumerate(TURN_FRONT):
        for x, ch in enumerate(r):
            if ch != '.':
                g[top + y][PX + 2 + 9 + x] = ch
    return {'turn_a': rows_of(g), 'turn_b': rows_of(place(TURN_FRONT + FRONT_LEGS, PX + 9))}


# ---- sitting -------------------------------------------------------------------------------------
# The rump on the ground, the chest up and the front legs straight, the head (the stand head) raised
# over them; the folded hind leg is a lit, rounded thigh with a shadow along its front edge, the
# cream hock at the back and the lower leg lying along the ground to its paw in front (an outlined
# thigh read as a tent); the tail curl rests on the rump behind. Seen from the side the sitting body is short.
SIT = [
    "............bb..bb.....",
    "...........bnb.bnb.....",
    "..........bbbbbbbb.....",
    "..........bbbbbbbbb....",
    "..........bbbbwwbbb....",
    "..........bbbbbobbbb...",
    "..........bbbbbvwwwwe..",
    ".........bbbbbbrwwwd...",
    "........abbbbbbbwx.....",
    "...aaa..abbbbbbwx......",
    "..abbba.abbbbbwwx......",
    ".abbbbbaabbbbbwwx......",
    ".abwwwbbbbbbbbwwx......",
    ".abwbbbbbbbbbbwwx......",
    "..abbbbbbbbbbbkkx......",
    "..abbbbaaabbbbkk.......",
    "..abbbaaaaabbbkk.......",
    "..abbbaaaaaacbkk.......",
    "..awbbbaaaacbbkk.......",
    "..awwbbbbccbbbpp.......",
    "...wwkkkkkppp.ppp......",
]


def sit_frames():
    out = {}
    # halfway down: the hind legs fold (lifted) and the rump sinks 2px, the chest stays
    body = shear(BODY, lambda x: 2 if x < 9 else 1 if x < 13 else 0)
    out['sit_a'] = rows_of(place(with_legs(body, {'far_hind': 'fold', 'near_hind': 'fold'}), PX))
    out['sit_0'] = rows_of(place(SIT, PX + 4))
    out['sit_1'] = rows_of(place(breathe(SIT, 11), PX + 4))
    return out


def shear(rows, drop):
    """Columns moved down by drop(x) (clipped at the bottom)."""
    h, w = len(rows), len(rows[0])
    g = [['.'] * w for _ in range(h)]
    for x in range(w):
        d = drop(x)
        for y in range(h - 1, -1, -1):
            if rows[y][x] != '.' and y + d < h:
                g[y + d][x] = rows[y][x]
    return [''.join(r) for r in g]


# ---- lying down ---------------------------------------------------------------------------------
# Belly on the ground, the front legs reaching forward under the chin (coat, then the cream paws),
# the hind leg folded at the side with its cream paw showing under the rump.
def lie(body):
    g = place(body, PX)
    for x, ch in zip(range(PX + 17, PX + 24), 'kkkkkpp'):
        g[GROUND][x] = ch
    for x in (PX + 22, PX + 23):
        g[GROUND - 1][x] = 'p'
    for x, ch in zip(range(PX + 4, PX + 9), 'ppkkk'):          # the folded hind leg's paw at the side
        g[GROUND][x] = ch
    return rows_of(g)


def lie_frames():
    # going down: the legs fold and the body lowers
    body = with_legs(BODY, {n: 'fold' for n in LEGS})
    return {'lie_a': rows_of(place(body[:-2], PX)), 'lie_0': lie(BODY), 'lie_1': lie(breathe(BODY))}


# ---- refusing the walk ----------------------------------------------------------------------------
# A leash runs from the collar up out of the frame. The shiba braces: rump down, front legs pushed out
# ahead, head lowered and pulled back; each tug drags it 1px forward and it leans back again. Then it
# flops flat on its belly (front legs stretched out ahead, hind legs back, chin on the ground, eyes
# shut) and will not budge.
COLLAR = (18, 8)                     # in BODY coordinates


def grounded(rows):
    """Drop empty rows at the bottom, so the lowest paw stands on the ground."""
    while rows and not rows[-1].strip('.'):
        rows = rows[:-1]
    return rows


def leash(g, x, y):
    """A taut leash from (x, y) up to the frame's top right edge."""
    x1, y1 = W - 1, 0
    n = max(abs(x1 - x), abs(y1 - y))
    for i in range(n + 1):
        X, Y = round(x + (x1 - x) * i / n), round(y + (y1 - y) * i / n)
        if g[Y][X] == '.':
            g[Y][X] = 'L'
    return g


BRACE_LEGS = {'far_front': (38, 20), 'near_front': (30, 14), 'far_hind': (20, 30), 'near_hind': (12, 22)}


def refuse_frames():
    rows = with_legs(BODY)
    out = {'refuse_stand': rows_of(leash(place(rows, PX), PX + COLLAR[0], GROUND - len(rows) + 1 + COLLAR[1]))}
    head = LOOK_HEADS['down_fwd']
    body = shear(with_head(head), lambda x: 1 if x < 12 else 0)       # the rump sinks, the head drops
    for name, dx in (('refuse_brace', 0), ('refuse_tug', 1)):
        rows = grounded(with_legs(body, BRACE_LEGS))
        g = place(rows, PX - 1 + dx)
        top = GROUND - len(rows) + 1
        out[name] = rows_of(leash(g, PX - 1 + dx + COLLAR[0], top + COLLAR[1] + 1))
    # flopped flat: the lying body with the head down on the ground and the eyes shut
    flat = with_head(head)
    flat = closed_eyes(flat)
    g = place(flat[2:], PX)                                           # the head's top rows are empty
    for x, ch in zip(range(PX + 18, PX + 26), 'kkkkkppp'):          # front legs flat out ahead
        g[GROUND][x] = ch
    for k, ch in enumerate('kkkpp'):                                  # hind legs flat out behind
        g[GROUND][PX + 4 - k] = ch
    top = GROUND - len(flat[2:]) + 1
    out['refuse_flop'] = rows_of(leash(g, PX + COLLAR[0], top + COLLAR[1] - 1))
    g = place(grounded(with_legs(body, {n: 'fold' for n in LEGS})), PX - 1)
    rows = grounded(with_legs(body, {n: 'fold' for n in LEGS}))
    top = GROUND - len(rows) + 1
    out['refuse_down'] = rows_of(leash(g, PX - 1 + COLLAR[0], top + COLLAR[1] + 1))
    return out


# ---- mikaeri: looking back over the shoulder --------------------------------------------------------
# Standing side on, the head turns back over the shoulder to the viewer: halfway (the face-on head
# on the neck), then fully (further back over the withers, the muzzle turned a column to the left).
FRONT_HEAD = TURN_FRONT[:10]


def head_over(body, x0, head=None):
    rows = [list(r) for r in body]
    for y in range(10):                          # clear the side head
        for x in range(HEAD_X, len(rows[y])):
            if y < 7 or x > 20:
                rows[y][x] = '.'
    for y, r in enumerate(head or FRONT_HEAD):
        for x, ch in enumerate(r):
            if ch != '.' and 0 <= x0 + x < len(rows[y]):
                rows[y][x0 + x] = ch
    return [''.join(r) for r in rows]


# looking back and to the left: the face-on head with the muzzle and nose a column to the left
FRONT_HEAD_BACK = [r if not 7 <= y <= 9 else r[1:] + r[-1] for y, r in enumerate(FRONT_HEAD)]


def mikaeri_frames():
    out = {}
    for name, head, x0 in (('mikaeri_a', FRONT_HEAD, 13), ('mikaeri', FRONT_HEAD_BACK, 10)):
        body = head_over(BODY, x0, head)
        out[name] = rows_of(place(with_legs(body), PX))
    return out


# ---- the shiba smile ---------------------------------------------------------------------------------
# Face-on, the eyes squeeze into happy arcs and the mouth opens wide with the tongue out, panting.
SMILE_HALF = [r for r in FRONT_HALF]
SMILE_HALF[5] = "bbdbbb"                         # the eye squeezed into an arc: ^
SMILE_HALF[6] = "bdbdww"
SMILE_HALF[9] = ".bwddd"                          # the mouth wide open, corners up
SMILE_HALF[10] = "..bdtt"
SMILE_HALF[11] = "..bbtt"
SMILE_PANT = list(SMILE_HALF)
SMILE_PANT[11] = "..bbww"                         # the tongue in a little between pants


def smile_frames():
    out = {}
    for name, half in (('smile', SMILE_HALF), ('smile_pant', SMILE_PANT)):
        face = [h + h[::-1] for h in half]
        out[name] = rows_of(place(face + FRONT_LEGS, PX + 9))
    return out


# ---- shaking off ----------------------------------------------------------------------------------------
# From photos of dogs shaking off: the head does not nod (nodding with lines in front of the mouth read
# as barking) but twists around the muzzle, the eyes squeezed shut and the ears flung out; the legs
# stand wide; the shake runs from the head down the body to the rump, the fur standing out in tufts.
# The body stays on its legs (moved over planted legs it came apart from them) and does not rise
# (that nodded the head); the shake shows in the fur flung out in tufts and the tail curl swinging. The head stays side on (a face-on frame looked like it turned to the viewer, and its shut eyes read as
# a smile); the twist shows as the head rolling one way and the other: rolled toward the viewer the far
# ear is flung out behind and the near ear stands, rolled away both ears flatten and more cream shows
# under the jaw.
def closed_eyes(rows):
    """The eyes squeezed shut: a 2x1 dark line (a lone dark pixel read as a smudge, 3px as too long)."""
    g = [list(r) for r in rows]
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch == 'o':
                for dx in (-1, 0):
                    if g[y][x + dx] in 'bo':
                        g[y][x + dx] = 'd'
            elif ch == 'v':
                g[y][x] = 'b'
    return [''.join(r) for r in g]


def side_head(ears, jaw=None, squash=False):
    """The side head with the eyes shut; ears replaces rows 0-1, jaw rows 8-9. squash drops a crown
    row, so the top of the head comes down 1px as it rolls."""
    rows = [r for r in BODY[:10]]
    rows[0], rows[1] = ears
    if jaw:
        rows[8], rows[9] = jaw
    if squash:
        rows = ['.' * len(rows[0])] + rows[:3] + rows[4:]
    return closed_eyes(rows)


# The head rolls about the muzzle, the line through the nose as its axis, like a drill. Seen from the
# side the nose stays put, and the two sides of the head trade places: rolled with the crown toward
# the viewer, the near eye and ear drop down the side of the head and the far eye and ear come up over
# the top; rolled the other way, the near eye and ear ride up. The cheek and jaw cream stays the same
# in every view, so it does not flicker as the head rolls.
# (Tilting the head around the nose in the picture plane looked like a sideways nod, not a roll.)
PAD = 4                                          # rows of room above the body, kept for the tufts
ROLL_HEADS = {
    'toward': [
        ".............................",
        ".................bb..........",          # the far ear, up over the top
        "................bnbb.........",
        "...............bbbbddbb......",          # the far eye (shut) at the top of the head
        "..............bnbbbbbbbb.....",          # the near ear, dropped down the side
        "...............bbbbwwbbbb....",          # the eyebrow goes down with the eye
        "...............bbbbddwwwwe...",          # the near eye, lower
        "...abbbbbbbbbbbbbbbbrwwwd....",
        "...abbbbbbbbbbbbbbbbbwx......",
        "...abbbbbbbbbbbbbbbbwx.......",
    ],
    'away': [
        "....................bb.......",          # the near ear, up
        "...................bnb.......",
        "...............bbbbbbbb......",
        "...............bbbbwwbbb.....",
        "...............bbbbddbbb.....",          # the near eye, higher
        "...............bbbbbbbbbb....",
        "...............bbbbbbwwwwe...",
        "...abbbbbbbbbbbbbbbbrwwwd....",          # the cheek and jaw cream as in the other views
        "...abbbbbbbbbbbbbbbbbwx......",          # (widening it here made it flicker)
        "...abbbbbbbbbbbbbbbbwx.......",
    ],
}
_EMPTY = ['.' * len(BODY[0])] * PAD
SHAKE_BODIES = {'level': _EMPTY + closed_eyes(BODY),
                'toward': _EMPTY + with_head(ROLL_HEADS['toward'], closed_eyes(BODY)),
                'away': _EMPTY + with_head(ROLL_HEADS['away'], closed_eyes(BODY))}
WIDE = {'far_front': (12, 6), 'near_front': (8, 4), 'far_hind': (-30, -8), 'near_hind': (-26, -6)}
SHAKE_ARCS = {                                   # short motion lines at the sides, never ahead of the mouth
    'head': [(14, 0), (13, 1), (24, 0), (25, 1)],                 # above and behind the head
    'rump': [(0, 6), (-1, 7), (-1, 8), (0, 12), (-1, 13)],
}


def tufts(rows, phase, x_from=3, x_to=17):
    g = [list(r) for r in rows]
    h, w = len(g), len(g[0])
    for x in range(x_from, x_to + 1):
        if (x + phase) % 2:
            continue
        ys = [y for y in range(h) if g[y][x] != '.']
        if not ys:
            continue
        top, bottom = ys[0], ys[-1]
        if top > 0 and g[top][x] in 'bac':
            g[top - 1][x] = 'b'
        if bottom + 1 < h and g[bottom][x] in 'bxc':
            g[bottom + 1][x] = 'x'
    return [''.join(r) for r in g]


def tail_swung(rows, d):
    """The tail curl on the rump (rows 2-6, columns before 10) moved d columns."""
    out = list(rows)
    for y in range(2, 7):
        r = rows[y]
        rear = r[:10]
        rear = ('.' * d + rear[:-d]) if d > 0 else (rear[-d:] + '.' * -d) if d < 0 else rear
        out[y] = rear + r[10:]
    return out


# The torso rolls too, half a beat behind the head and the other way: rolled toward the viewer the lit
# back shows along the top, rolled away the cream belly shows along the bottom.
def torso_rolled(rows, way):
    g = [list(r) for r in rows]
    top = PAD + 7
    if way == 'toward':
        for x in range(4, 15):
            if g[top][x] == 'b':
                g[top][x] = 'a'
    elif way == 'away':
        for x in range(6, 17):
            if g[top + 6][x] in 'bx':
                g[top + 6][x] = 'w'
    return [''.join(r) for r in g]


# water flung off the coat: single pale drops (no outline) flying out from the back, the belly and the
# head, further out each frame of a swing
DROPS = [
    [(6, 5), (10, 4), (14, 6), (4, 17), (12, 18), (27, 7)],
    [(5, 3), (9, 2), (13, 4), (3, 18), (11, 19), (29, 6), (27, 3)],
]


def shake_frames():
    out = {}
    empty = '.' * len(BODY[0])

    def frame(head, torso, tail, phase, span, drops):
        body = SHAKE_BODIES[head]
        body = body[:PAD] + tail_swung(body[PAD:], tail)
        body = torso_rolled(tufts(body, phase, *span), torso)
        rows = with_legs(body, WIDE)
        g = place(rows, PX)
        top = GROUND - len(rows) + 1
        for x, y in (DROPS[drops] if drops is not None else []):
            X, Y = PX + x, top + y
            if 0 <= X < W and 0 <= Y < H and g[Y][X] == '.':
                g[Y][X] = 'Z'
        return rows_of(g)

    # 1: the head starts on its own; 2: the whole body, the torso rolling against the head, water
    # flying; 3: it dies out at the rump and tail
    out['shake_h0'] = frame('toward', 'level', 0, 0, (14, 17), None)
    out['shake_h1'] = frame('away', 'level', 0, 1, (14, 17), None)
    out['shake_b0'] = frame('toward', 'away', 1, 0, (3, 17), 0)
    out['shake_b1'] = frame('level', 'level', 0, 1, (3, 17), 1)
    out['shake_b2'] = frame('away', 'toward', -1, 0, (3, 17), 0)
    out['shake_r0'] = frame('level', 'level', 1, 1, (3, 9), None)
    out['shake_r1'] = frame('level', 'level', -1, 0, (3, 9), None)
    out['shake_level'] = frame('level', 'level', 0, 1, (14, 17), None)
    # settling: the fur still fluffed, eyes shut a moment
    out['shake_end'] = rows_of(place(with_legs(tufts([empty] + closed_eyes(BODY), 0)), PX))
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
    out.update(refuse_frames())
    out.update(mikaeri_frames())
    out.update(smile_frames())
    out.update(shake_frames())
    return out


ANCHOR = (PX + 12, GROUND)

if __name__ == '__main__':
    print(json.dumps(frames(), indent=1))
