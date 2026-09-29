"""Frame generator for the black and tan dachshund.

The body, head views and poses are drawn by hand below; the legs are drawn in code the same way
as the corgi's (four 2px legs, far legs a step darker and a little behind). assemble_dachshund.py
turns the result into sprites/dachshund.json.

Usage: python3 tools/draft_dachshund.py > /tmp/dachshund-frames.json
"""
import json

W, H = 50, 28            # room in front for the burrow's heap, behind for the dirt it throws back
GROUND = H - 1
PX = 8

# ---- palette keys ------------------------------------------------------------------------------
# B/H/D: black coat, its sheen on top, the darker hanging ear; n/N: tan and its shadow;
# e: nose, o/v: eye (top/bottom; blinking turns o into black and v into a tan lid line),
# m: tongue, r: blush, k/l: near/far leg (tan), y/Y: dirt and its shadow, f/F: flying dirt, faded
# (no outline)

# ---- the body (facing right) ---------------------------------------------------------------------
# A big round head raised above a long low sausage body, a long ear hanging to below the jaw, a
# slim tapering snout (3 rows: joined to the throat and chest in one tan piece it read as a heavy
# jowl), a black throat and a small 2x2 tan patch on the chest (3 rows read as a big bib), a long
# tail held up.
BODY = [
    ".....................HHHHH............",
    "....................HBBBBBH...........",
    "...................BBBBBBBBB..........",
    "..................BBBBBBBnBBB.........",
    "..................BDDDBBnoBBBB........",
    ".................BDDDDDBnvnnnnnB......",
    ".BB..............BDDDDDBnnnnnnnne.....",
    "..B..............BDDDDDDnrnnnnm.......",
    "..BHHHHHHHHHHHHHHDDDDDDBBnnnn.........",
    "...BBBBBBBBBBBBBBBDDDDBBBB............",
    "...BBBBBBBBBBBBBBBBDDBBnnB............",
    "...BBBBBBBBBBBBBBBBBBBnnBB............",
    "...BBBBBBBBBBBBBBBBBBBBBB.............",
    "....NBBBBBBBBBBBBBBBBBBB..............",
]
BREATH_ROW = 11
LEG_ROWS = 3
LEGS = {'far_hind': (4, 'l'), 'near_hind': (6, 'k'), 'far_front': (18, 'l'), 'near_front': (20, 'k')}
LEG_ORDER = ['far_hind', 'far_front', 'near_hind', 'near_front']
HEAD_X = 17
TAIL = [(1, 6), (2, 6), (2, 7)]         # the tail's pixels in BODY (its root at (2, 8) stays)
TAILS = {                               # wagging positions of the tail
    'up': [(1, 6), (2, 6), (2, 7)],
    'high': [(2, 4), (2, 5), (2, 6), (2, 7)],
    'back': [(0, 7), (1, 7), (2, 7)],
}


def blank():
    return [['.'] * W for _ in range(H)]


def rows_of(g):
    return [''.join(r) for r in g]


def place(rows, ox, dy=0, g=None):
    g = g or blank()
    top = GROUND - len(rows) + 1 - dy
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.' and 0 <= top + y < H and 0 <= ox + x < W:
                g[top + y][ox + x] = ch
    return g


def with_tail(body, pose='up'):
    g = [list(r) for r in body]
    for x, y in TAIL:
        g[y][x] = '.'
    for x, y in TAILS[pose]:
        g[y][x] = 'B'
    return [''.join(r) for r in g]


def with_legs(body, poses=None):
    """The body rows plus four 3-row tan legs; poses maps a leg to (mid dx, paw dx), or None to
    lift the paw (the leg is 1 row shorter)."""
    poses = poses or {}
    width = len(body[0])
    legs = [['.'] * width for _ in range(LEG_ROWS)]
    for name in LEG_ORDER:
        x0, fur = LEGS[name]
        pose = poses.get(name, (0, 0))
        steps = [(0, 0), (1, 1)] if pose is None else [(0, 0), (1, pose[0]), (2, pose[1])]
        for y, dx in steps:
            for i in range(2):
                if 0 <= x0 + i + dx < width:
                    legs[y][x0 + i + dx] = fur
    return list(body) + [''.join(r) for r in legs]


def breathe(rows, at=BREATH_ROW):
    return rows[:at] + [rows[at]] + rows[at:]


def stand_frames():
    out = {'stand': rows_of(place(with_legs(BODY), PX))}
    out['idle_0'] = out['stand']
    out['idle_1'] = rows_of(place(with_legs(breathe(with_tail(BODY, 'high'))), PX))     # a slow wag while breathing
    return out


# ---- walking and running ---------------------------------------------------------------------------
STEP = [(0, 1), (0, 0), (0, -1), None]


def walk_frames():
    out = {}
    for f in range(4):
        a, b = STEP[f], STEP[(f + 2) % 4]
        poses = {'near_hind': a, 'far_front': a, 'far_hind': b, 'near_front': b}
        body = with_tail(BODY, ('up', 'high', 'up', 'back')[f])
        out[f'walk_{f}'] = rows_of(place(with_legs(breathe(body) if f % 2 else body, poses), PX))
    return out


# The long ear flaps on the run: it lifts back off the head when airborne and swings down on landing.
EAR = [(x, y) for y, r in enumerate(BODY) for x, ch in enumerate(r) if ch == 'D']


def ear_moved(body, dx, dy):
    g = [list(r) for r in body]
    for x, y in EAR:
        g[y][x] = 'B'
    for x, y in EAR:
        if 0 <= y + dy < len(g) and 0 <= x + dx < len(g[0]):
            g[y + dy][x + dx] = 'D'
    return [''.join(r) for r in g]


RUN = [  # (leg poses, lift, ear dx, ear dy, tail)
    ({'far_front': (1, 2), 'near_front': (1, 3), 'far_hind': (-1, -2), 'near_hind': (-1, -3)}, 0, 0, 0, 'back'),
    ({'far_front': None, 'near_front': None, 'far_hind': None, 'near_hind': None}, 1, -1, -2, 'back'),
    ({'far_front': (0, -1), 'near_front': (-1, -2), 'far_hind': (0, 1), 'near_hind': (1, 2)}, 0, -1, -1, 'up'),
    ({'far_front': (0, 1), 'near_front': (0, 0), 'far_hind': (0, 0), 'near_hind': (0, -1)}, 0, 0, 1, 'up'),
]


def run_frames():
    out = {}
    for f, (poses, lift, edx, edy, tail) in enumerate(RUN):
        body = ear_moved(with_tail(BODY, tail), edx, edy)
        out[f'run_{f}'] = rows_of(place(with_legs(body, poses), PX, lift))
    return out


# ---- head directions ---------------------------------------------------------------------------
# The whole head tips on the neck: up, the crown goes back and the slim snout rises 2 rows; down,
# the head lowers a row and the snout points down. Each replaces BODY rows 0-9.
LOOK_HEADS = {
    'up_fwd': [
        "....................HHHHH.............",
        "...................HBBBBBH............",
        "..................BBBBBBBBB...........",
        "..................BBBBBBnBBnnnnnB.....",
        ".................BDDDBBnonnnnnnnne....",
        ".................BDDDDDBnvnnrnnm......",
        ".BB..............BDDDDDBnnnnn.........",
        "..B..............BDDDDDDBB............",
        "..BHHHHHHHHHHHHHHDDDDDDBBBB...........",
        "...BBBBBBBBBBBBBBBDDDDBBBB............",
    ],
    'down_fwd': [
        "......................................",
        ".....................HHHHH............",
        "....................HBBBBBH...........",
        "...................BBBBBBBBB..........",
        "..................BBBBBBBnBBB.........",
        "..................BDDDBBnoBBBB........",
        ".BB..............BDDDDDBnvnnnnB.......",
        "..B..............BDDDDDBnnnnnnnne.....",
        "..BHHHHHHHHHHHHHHDDDDDDDnrnnnm........",
        "...BBBBBBBBBBBBBBBDDDDBBBnnn..........",
    ],
}
LOOK_DIRS = list(LOOK_HEADS)


def with_head(head, body=None):
    rows = list(body or BODY)
    for y, r in enumerate(head):
        rows[y] = r
    return rows


def look_frames():
    out = {}
    for d, head in LOOK_HEADS.items():
        body = with_head(head)
        out[f'idle_0_{d}'] = rows_of(place(with_legs(body), PX))
        out[f'idle_1_{d}'] = rows_of(place(with_legs(breathe(with_tail(body, 'high'))), PX))
    return out


# ---- turning toward the viewer -----------------------------------------------------------------
# Face-on: drawn as the left half and mirrored so it is exactly symmetric. Both long ears hang at
# the sides, the tan eyebrow dots over the eyes, the short tan muzzle with the nose in the middle,
# a tan patch on the chest. Three-quarter: the face-on head over the side body cut short.
FRONT_HALF = [
    "....HHHH",
    "...HBBBB",
    "..BBBBBB",
    ".DBBBnBB",
    "DDBBnoBB",
    "DDDBnvnn",
    "DDDBnnnn",
    "DDDDnnne",
    ".DDDBnnm",
    ".DDDBBBB",
    "..DDBBBn",
    "...BBBBn",
    "...BBBBB",
    "...BBBBB",
]
TURN_FRONT = [h + h[::-1].replace('m', 'm') for h in FRONT_HALF]
TURN_FRONT_LEGS = ["..ll.kk..kk.ll..", "..ll.kk..kk.ll..", "..ll.kk..kk.ll.."]


def turn_frames():
    out = {'turn_b': rows_of(place(TURN_FRONT + TURN_FRONT_LEGS, PX + 12))}
    # three-quarter: the side body up to the neck, with the face-on head over its front
    side = [r[:HEAD_X + 1] + '.' * (len(r) - HEAD_X - 1) for r in BODY]
    rows = with_legs(side, {'far_front': (0, 0), 'near_front': (0, 0)})
    g = place(rows, PX)
    top = GROUND - len(rows) + 1
    for y, r in enumerate(TURN_FRONT):
        for x, ch in enumerate(r):
            if ch != '.':
                g[top + y][PX + 13 + x] = ch
    out['turn_a'] = rows_of(g)
    return out


# ---- sitting -------------------------------------------------------------------------------------
# Sitting up: the long back slopes from the rump on the ground to the chest, the front legs straight,
# the head raised above them; the tail lies along the ground behind. The torso is 14px wide: sitting,
# the body is seen short from the side.
SIT_BODY = [
    "..........BBBBBBBBBB..........",
    ".........BBBBBBBBBnnB.........",
    "........BBBBBBBBBBnnBB........",
    ".......BBBBBBBBBBBBBB.........",
    "......BBBBBBBBBBBBBBB.........",
    ".....BBBBBBBBBBBBBBB..........",
    "....BBBBHHHBBBBBBBB...........",
    "....BBBHBBBHBBlkkB............",
    "...BBBHBBBBBHllkk.............",
    "BBBBBBHkkkkHBllkk.............",
    "BBB.NNkkkk...llkk.............",
]
SIT_HEAD_DX = -6


def head_block(head=None):
    src = with_head(head) if head else BODY
    return ['.' * HEAD_X + r[HEAD_X:] for r in src[:10]]


def sit_rows(head=None):
    width = len(SIT_BODY[0])
    head = [(r[-SIT_HEAD_DX:] + '.' * -SIT_HEAD_DX)[:width].ljust(width, '.') for r in head_block(head)]
    return head + [r.ljust(width, '.') for r in SIT_BODY]


def shear(rows, drop):
    h, w = len(rows), len(rows[0])
    g = [['.'] * w for _ in range(h)]
    for x in range(w):
        d = drop(x)
        for y in range(h - 1, -1, -1):
            if rows[y][x] != '.' and y + d < h:
                g[y + d][x] = rows[y][x]
    return [''.join(r) for r in g]


def sit_frames():
    out = {}
    body = shear(BODY + ['.' * len(BODY[0])] * 2, lambda x: 2 if x < 8 else 1 if x < 13 else 0)
    rows = with_legs(body[:len(BODY)], {'far_hind': None, 'near_hind': None})
    out['sit_a'] = rows_of(place(rows, PX))
    out['sit_0'] = rows_of(place(sit_rows(), PX + 6))
    out['sit_1'] = rows_of(place(breathe(sit_rows(), 14), PX + 6))
    return out


# ---- lying down ----------------------------------------------------------------------------------
# The long body flat on the ground, the front legs reaching forward under the chin (fur, then the
# paws: past the chest so they read as legs), the tail along the ground behind.
def lie_frames():
    out = {}
    out['lie_a'] = rows_of(place(with_legs(BODY, {n: None for n in LEGS})[:-1], PX))
    for i, breath in enumerate((False, True)):
        body = with_tail(BODY, 'back')
        g = place(breathe(body) if breath else body, PX)
        for x in range(PX + 22, PX + 28):
            g[GROUND][x] = 'k' if x < PX + 26 else 'l'
        for x in (PX + 26, PX + 27):
            g[GROUND - 1][x] = 'k'
        out[f'lie_{i}'] = rows_of(g)
    return out


# ---- burrowing -----------------------------------------------------------------------------------
# A burrow hound: the front end goes down, the front paws dig in turn and throw dirt back under the
# body, a heap grows in front of the nose, then the head goes into the hole behind the heap and
# only the rump and the wagging tail show; then it backs out with dirt on its head.
def bow_body(head=None):
    """Front end down 3px onto the folded front legs, rump up (nothing is cut off)."""
    base = with_head(head) if head else BODY
    body = shear(base + ['.' * len(base[0])] * LEG_ROWS, lambda x: 0 if x < 8 else min(LEG_ROWS, (x - 8) // 2 + 1))
    hind = with_legs(base, {'far_front': None, 'near_front': None})
    g = [list(r) for r in body]
    for y, r in enumerate(hind[len(base):]):
        for x, ch in enumerate(r):
            if ch != '.' and x < 12:
                g[len(base) + y][x] = ch
    return g


def heap(g, x0, size, seed):
    """An irregular heap of dirt standing on the ground at x0: the peak off-centre, the slopes
    uneven, shaded underneath, a few clods on it."""
    import random
    rnd = random.Random(seed)
    peak = x0 + size * 3 // 5
    for x in range(x0, x0 + size * 2):
        d = x - peak
        h = size - (abs(d) * (2 if d > 0 else 1)) // 2
        h += rnd.choice((0, 0, 1)) if 0 < h < size else 0
        for k in range(max(0, h)):
            y = GROUND - k
            if 0 <= x < W and 0 <= y < H:
                g[y][x] = 'Y' if k == 0 or (x > peak and k < 2) else 'y'
    return g


def fling(g, pts):
    for x, y in pts:
        for dx in range(2):                     # 2px clods: 1px dots read as specks
            if 0 <= x + dx < W and 0 <= y < H and g[y][x + dx] == '.':
                g[y][x + dx] = 'f'
    return g


# the path of a clod thrown back (BODY x, rows above the ground): off the front paws, low under the
# belly between the legs, then up and out behind the rump, and down
THROW = [(16, 1), (11, 2), (6, 3), (1, 5), (-3, 6), (-6, 5), (-8, 3), (-9, 1)]


def burrow_frames():
    out = {}
    heap_end = PX + 34                            # the heap's far edge: it grows back toward the dog from here
    for i in range(4):
        g = bow_body(LOOK_HEADS['down_fwd'])
        # the front paws dig in turn: one scoops forward, the other rakes back under the chest
        for name, reach in (('far_front', (1, -2)[i % 2]), ('near_front', (-2, 1)[i % 2])):
            x0, fur = LEGS[name]
            for dx in range(2):
                g[-1][x0 + dx + reach] = fur
        rows = [''.join(r) for r in g]
        grid = place(rows, PX)
        heap(grid, heap_end - 2 * (2 + i), 2 + i, 11)
        heap(grid, PX - 8, 2 + i // 2, 5)            # the dirt it throws back piles up behind it
        for k in range(3):                           # three clods along the arc, two steps apart
            j = (i + 2 * k) % len(THROW)
            x, y = THROW[j]
            ch = 'f' if j < 5 else 'F'               # faded as they fly off
            for dx in range(2):
                if 0 <= PX + x + dx < W and grid[GROUND - y][PX + x + dx] == '.':
                    grid[GROUND - y][PX + x + dx] = ch
        out[f'dig_{i}'] = rows_of(grid)
    # into the hole: the head goes down behind the heap, the rump stays up and the tail wags
    for i, tail in enumerate(('up', 'high', 'up', 'back')):
        base = with_tail(BODY, tail)
        body = shear(base + ['.' * len(base[0])] * (LEG_ROWS + 4), lambda x: 0 if x < 8 else min(LEG_ROWS + 4, (x - 8) // 2 + 1))
        hind = with_legs(base, {'far_front': None, 'near_front': None, 'near_hind': ((0, 1), (0, 0))[i % 2]})
        g = [list(r) for r in body[:len(base) + LEG_ROWS]]
        for y, r in enumerate(hind[len(base):]):
            for x, ch in enumerate(r):
                if ch != '.' and x < 12:
                    g[len(base) + y][x] = ch
        grid = place([''.join(r) for r in g], PX)
        for row in grid:                          # the head is down the hole: nothing of it shows
            for x in range(PX + 22, W):
                row[x] = '.'
        heap(grid, heap_end - 14, 7, 11)          # the heap it dug, grown over the hole and the head
        out[f'burrow_{i}'] = rows_of(grid)
    # backing out with dirt on its head, then shaking it off
    g = place(with_legs(with_head(LOOK_HEADS['down_fwd'])), PX)
    heap(g, heap_end - 12, 6, 11)
    top = next(y for y in range(H) if any(ch != '.' for ch in g[y][PX + 18:PX + 30]))
    for x, dy in ((PX + 21, 0), (PX + 22, 0), (PX + 23, 1), (PX + 25, 0), (PX + 26, 0)):
        g[top + dy][x] = 'y'                      # dirt sitting on the crown, not floating above it
    out['burrow_out'] = rows_of(g)
    return out


# ---- wagging the tail ------------------------------------------------------------------------------
# Happy: the tail wags fast through three positions, the ears bounce with it and the mouth is open.
def wag_frames():
    out = {}
    for i, (tail, edy) in enumerate((('up', 0), ('high', -1), ('up', 0), ('back', 1))):
        body = ear_moved(with_tail(BODY, tail), 0, edy)
        out[f'wag_{i}'] = rows_of(place(with_legs(body), PX))
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
    out.update(burrow_frames())
    out.update(wag_frames())
    return out


ANCHOR = (PX + 13, GROUND)

if __name__ == '__main__':
    print(json.dumps(frames(), indent=1))
