"""Frame generator for the Pembroke Welsh corgi.

The key poses and head views are drawn by hand below; the legs are drawn in code (four 2px legs,
far legs a step darker and a little behind their near partner). assemble_corgi.py turns the
result into sprites/corgi.json.

Usage: python3 tools/draft_corgi.py > /tmp/corgi-frames.json
"""
import json

# Frame canvas: room in front for the ball, above for hops, behind and in front for the run.
W, H = 44, 26
GROUND = H - 1
PX = 5                   # x of the stand pose's left edge

# ---- palette keys ------------------------------------------------------------------------------
# S: saddle (back and top of the head; same as b on the red coat), b/a/c/d: fur base/light/dark/
# darkest, w/x: white and its shadow, n: inner ear, r: blush, e: nose, t: tongue,
# o/v: eye (top/bottom pixel; blinking turns o into fur and v into a dark lid line),
# k/l: near/far leg fur, p/q: near/far white sock

# ---- key poses (facing right) ------------------------------------------------------------------
# Cute before literal: a big head raised in front of a short round loaf of a body, tall ears with
# pink insides, a 1x2 eye with a blush under it, a white blaze and muzzle, a happy open mouth.
BODY = [
    "..............S.....S.......",
    ".............SS....SSS......",
    ".............SSS...SnS......",
    "............SSSS..SSnS......",
    "............SSSS..SnnS......",
    "............SSSSSSSnnSS.....",
    ".............SSSSSSSSSS.....",
    "............bSSSSSSSSSSS....",
    "...........bbSSSSSbbSwSS....",
    "...........bbbSSSSbobwwwS...",
    "..SSSSSSSSSbbbbbbbbvbwwwwwe.",
    ".SSSSSSSSSSbbbbbbbbrwwwwdd..",
    "aSSSSSSSSSSbbbbbbbbbwwwwtt..",
    "abbbbbbbbbbbbbbbbbbwwwwwt...",
    "abbbbbbbbbbbbbbbbbbwwwwwx...",
    "abbbbbbbbbbbbbbbbbwwwwwx....",
    ".cbbbbbxxxxxxxxxxbbbwwx.....",
]
BREATH_ROW = 14          # a body row below the face: repeating it swells the whole body evenly
LEG_ROWS = 3             # fur, white sock, white paw
# the four legs: (x of the left column in BODY coordinates, fur, sock); far legs first
LEGS = {'far_hind': (2, 'l', 'q'), 'near_hind': (4, 'k', 'p'),
        'far_front': (15, 'l', 'q'), 'near_front': (17, 'k', 'p')}
LEG_ORDER = ['far_hind', 'far_front', 'near_hind', 'near_front']


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


def with_legs(body, poses=None, lift=0):
    """The body rows plus four legs. poses maps a leg to (mid dx, paw dx), or None to lift the paw
    off the ground (the leg is 1 row shorter). lift raises the body (the legs stay 3 rows, so the
    whole dog leaves the ground)."""
    poses = poses or {}
    width = len(body[0])
    legs = [['.'] * width for _ in range(LEG_ROWS)]
    for name in LEG_ORDER:
        x0, fur, sock = LEGS[name]
        pose = poses.get(name, (0, 0))
        if pose is None:
            rows = [(0, fur), (1, sock)]
            dxs = [0, 1]
        else:
            mid, paw = pose
            rows = [(0, fur), (1, sock), (2, sock)]
            dxs = [0, mid, paw]
        for (y, ch), dx in zip(rows, dxs):
            for i in range(2):
                x = x0 + i + dx
                if 0 <= x < width:
                    legs[y][x] = ch
    rows = list(body) + [''.join(r) for r in legs]
    return rows, lift


def breathe(rows):
    return rows[:BREATH_ROW] + [rows[BREATH_ROW]] + rows[BREATH_ROW:]


def stand_frames():
    out = {}
    rows, _ = with_legs(BODY)
    out['stand'] = rows_of(place(rows, PX))
    out['idle_0'] = out['stand']
    rows, _ = with_legs(breathe(BODY))
    out['idle_1'] = rows_of(place(rows, PX))
    return out


# Walking: diagonal pairs move together (near hind with far front), half a cycle apart. A planted
# paw goes from 1px forward to 1px back over two frames while the body moves 1px a frame, so it
# stays put on the ground; the lifted paw swings forward. The body bobs 1px on the lift frames.
STEP = [(0, 1), (0, 0), (0, -1), None]      # per frame: (mid dx, paw dx) or lifted


def walk_frames():
    out = {}
    for f in range(4):
        a, b = STEP[f], STEP[(f + 2) % 4]
        poses = {'near_hind': a, 'far_front': a, 'far_hind': b, 'near_front': b}
        body = breathe(BODY) if f % 2 else BODY
        rows, _ = with_legs(body, poses)
        out[f'walk_{f}'] = rows_of(place(rows, PX))
    return out


# Running: a bouncy gallop on short legs. Stretched out (front paws reaching forward, hind paws
# pushing back), then airborne 1px with the legs tucked, then gathered (paws under the body).
# The body rises only on the airborne frame (1px, once a stride); also swelling it on every other
# frame made the back shake up and down.
RUN = [
    ({'far_front': (1, 2), 'near_front': (1, 3), 'far_hind': (-1, -2), 'near_hind': (-1, -3)}, 0, False),
    ({'far_front': None, 'near_front': None, 'far_hind': None, 'near_hind': None}, 1, False),
    ({'far_front': (0, -1), 'near_front': (-1, -2), 'far_hind': (0, 1), 'near_hind': (1, 2)}, 0, False),
    ({'far_front': (0, 1), 'near_front': (0, 0), 'far_hind': (0, 0), 'near_hind': (0, -1)}, 0, False),
]


def run_frames():
    out = {}
    for f, (poses, lift, breath) in enumerate(RUN):
        rows, _ = with_legs(breathe(BODY) if breath else BODY, poses)
        out[f'run_{f}'] = rows_of(place(rows, PX, lift))
    return out


# ---- head directions (mouse tracking) -----------------------------------------------------------
# The head turns on the neck as a whole: looking up, the crown and ears tip back and the snout
# comes up (nose 3 rows higher); looking down, the snout tucks down toward the chest, no longer
# than when looking ahead. Only the
# columns from HEAD_X on change, the back stays. Each replaces BODY rows 0-13.
HEAD_X = 11
LOOK_HEADS = {
    'up_fwd': [
        ".............S.....S........",
        "............SS....SSS.......",
        "............SSS...SnS.......",
        "...........SSSS..SSnS.......",
        "...........SSSS..SnnS.......",
        "...........SSSSSSSnnSS......",
        "............SSSSSSSSSSS.....",
        "............bSSSSSSSSwwwe...",
        "...........bbSSSSSbbwwwwdd..",
        "...........bbbSSSSbobwwwwt..",
        "..SSSSSSSSSbbbbbbbbvbwwwtt..",
        ".SSSSSSSSSSbbbbbbbbrwwwww...",
        "aSSSSSSSSSSbbbbbbbbbwwwww...",
        "abbbbbbbbbbbbbbbbbbwwwwwx...",
    ],
    'down_fwd': [
        "............................",
        "...............S.....S......",
        "..............SS....SSS.....",
        "..............SSS...SnS.....",
        ".............SSSS..SSnS.....",
        ".............SSSS..SnnS.....",
        ".............SSSSSSSnnSS....",
        "............bSSSSSSSSSSSS...",
        "...........bbSSSSSSbbSSSS...",
        "...........bbbSSSSSbobSwwS..",
        "..SSSSSSSSSbbbbbbbbbvbwwww..",
        ".SSSSSSSSSSbbbbbbbbbrwwwww..",
        "aSSSSSSSSSSbbbbbbbbbbwwwwwe.",
        "abbbbbbbbbbbbbbbbbbbwwwwdd..",
    ],
}
LOOK_DIRS = list(LOOK_HEADS)


def with_head(head):
    rows = list(BODY)
    for y, r in enumerate(head):
        rows[y] = r
    return rows


def look_frames():
    out = {}
    for d, head in LOOK_HEADS.items():
        body = with_head(head)
        for i, breath in enumerate((False, True)):
            rows, _ = with_legs(breathe(body) if breath else body)
            out[f'idle_{i}_{d}'] = rows_of(place(rows, PX))
    return out


# ---- turning toward the viewer ------------------------------------------------------------------
# Three-quarter view: the body foreshortened, the head turned toward the viewer with both eyes
# showing and the nose below between them, nearer the far eye. Face-on: both ears up, the blaze
# down the middle, the nose in the middle below the eyes, the white chest and front legs.
TURN_3Q = [
    "..........S.....S.......",
    ".........SS....SSS......",
    ".........SnS...SnS......",
    "........SSnS..SSnnS.....",
    "........SnnSSSSnnnS.....",
    "........SSSSSSSSSSS.....",
    "........SSSSSSwSSSSS....",
    ".......bbobbSwwSbobb....",
    "..SSSSSbbvbwwwwwbvbb....",
    ".SSSSSSbrbwwwwwwwrbb....",
    "aSSSSSSbbwwwwewwwwbb....",
    "aSSSSSSSbwwwwttwwwb.....",
    "abbbbbbbbbwwwwtwwwb.....",
    "abbbbbbbbbbwwwwwwbb.....",
    "abbbbbbbbbbwwwwwwbb.....",
    ".cbbbxxxxxbbwwwwbb......",
]
# the face-on view is drawn as its left half and mirrored, so the nose, mouth and tongue sit exactly
# on the middle (drawn freehand, the tongue and mouth were a pixel off and read as half a mouth)
TURN_FRONT_HALF = [
    "..S.....",
    ".SS.....",
    ".SnS....",
    ".SnnS...",
    ".SnnSSSS",
    ".SSSSSSS",
    ".SSSSSSw",
    "SSbobSSw",
    "Sbbvbbww",
    "Sbrbwwww",
    ".bbwwwwe",
    ".bbwwwdt",
    "..bwwwwt",
    "..bbwwww",
    ".bbbwwww",
    ".bbbwwww",
]
TURN_FRONT = [h + h[::-1] for h in TURN_FRONT_HALF]
TURN_3Q_LEGS = ["..ll.kk....ll.kk........", "..qq.pp....qq.pp........", "..qq.pp....qq.pp........"]
TURN_FRONT_LEGS = ["..ll.kk..kk.ll..", "..qq.pp..pp.qq..", "..qq.pp..pp.qq.."]


def turn_frames():
    return {'turn_a': rows_of(place(TURN_3Q + TURN_3Q_LEGS, PX + 4)),
            'turn_b': rows_of(place(TURN_FRONT + TURN_FRONT_LEGS, PX + 8))}


# ---- sitting -------------------------------------------------------------------------------------
# Sitting: the rump on the ground behind, the chest up and the front legs straight, the head raised
# above them; the folded hind leg shows as a rounded thigh with its white paw forward on the ground.
# The head is the stand head (BODY rows 0-12 from HEAD_X on), moved back and up.
SIT_BODY = [   # 16px wide: sitting up, the body is seen short from the side (as wide as the standing
               # body it read as fat)
    ".......abbbbbbbwwwx.........",
    ".......abbbbbbbwwwwx........",
    "......abbbbbbbbwwwwx........",
    "......abbbbbbbbwwwx.........",
    ".....abbbbbbbbbwwwx.........",
    ".....abbbbbbbbbwwx..........",
    "....abbbcccbbbbwwx..........",
    "....abbcbbbcbbbwwx..........",
    "....cbcbbbbbcllkkx..........",
    "....ccbcbbbbcqqpp...........",
    ".....ccccpppp.qqpp..........",
]
SIT_HEAD_DX = -6          # the head sits this much further back than when standing


def head_block(head=None):
    """The head: BODY rows 0-12 (or a look head) from HEAD_X on, the rest blank."""
    src = with_head(head) if head else BODY
    return ['.' * HEAD_X + r[HEAD_X:] for r in src[:13]]


def sit_rows(head=None):
    rows = [r[-SIT_HEAD_DX:] + '.' * -SIT_HEAD_DX for r in head_block(head)]
    return rows + SIT_BODY


def shear(rows, drop):
    """Columns moved down by drop(x) (clipped at the bottom): the rump sinks while the head stays."""
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
    # halfway down: the rump sinks 2px (the hind legs fold to their paws), the chest stays
    body = shear(BODY, lambda x: 2 if x < 7 else 1 if x < 11 else 0)
    rows, _ = with_legs(body, {'far_hind': None, 'near_hind': None})
    out['sit_a'] = rows_of(place(rows, PX))
    out['sit_0'] = rows_of(place(sit_rows(), PX + 4))
    out['sit_1'] = rows_of(place(breathe_at(sit_rows(), 15), PX + 4))
    return out


def breathe_at(rows, y):
    return rows[:y] + [rows[y]] + rows[y:]


# ---- lying down: the corgi sploot ----------------------------------------------------------------
# Belly flat on the ground, the front paws forward under the chin, the hind legs stretched straight
# back with the white soles showing: the frog-legged "sploot" corgis are known for.
# the front legs reaching forward under the chin: fur, then the white paws (white all the way
# merged with the white chest and did not read as legs)
FRONT_PAWS = dict(zip(range(PX + 24, PX + 29), 'kkkpp'))   # out past the chest, under the chin


def front_paws(g):
    for x, ch in FRONT_PAWS.items():
        g[GROUND][x] = ch
    for x in (PX + 27, PX + 28):         # the paws are 2px tall, so the legs read at app size
        g[GROUND - 1][x] = 'p'
    return g


def lie_frames():
    out = {}
    # going down: the legs fold to 1 row and the body lowers 2px
    rows, _ = with_legs(BODY, {n: None for n in LEGS})
    out['lie_a'] = rows_of(place(rows[:-1], PX))
    # down: the body on the ground, front paws forward
    g = place(BODY, PX)
    front_paws(g)
    out['lie_0'] = rows_of(g)
    # sploot: the hind legs slide back along the ground, soles up
    for i, reach in enumerate((3, 5)):
        g = place(BODY, PX)
        front_paws(g)
        for k in range(reach):
            g[GROUND][PX - k] = 'k' if k < reach - 1 else 'p'
            g[GROUND - 1][PX - k] = 'l' if k < reach - 1 else 'q'
        out[f'lie_{i + 1}'] = rows_of(g)
    g = [list(r) for r in out['lie_2']]
    out['lie_3'] = rows_of(place(breathe(BODY), PX, 0, g))            # breathing while down
    return out


# ---- barking -------------------------------------------------------------------------------------
# Front paws braced 1px forward, the head up a little; on each bark the mouth opens wide (no tongue)
# and the body jolts back 1px, with two short arcs in front of the mouth (no outline).
BARK_MOUTH = {10: "..SSSSSSSSSbbbbbbbbvbwwwwwe.", 11: ".SSSSSSSSSSbbbbbbbbrwwwddd..", 12: "aSSSSSSSSSSbbbbbbbbbwwwdd...",
              13: "abbbbbbbbbbbbbbbbbbwwwwwx..."}
BARK_ARCS = [(28, 8), (29, 9), (29, 10), (28, 11), (30, 6), (31, 7), (31, 8), (31, 9), (31, 10), (31, 11), (30, 12)]
BRACE = {'far_front': (0, 1), 'near_front': (1, 1)}


def bark_frames():
    """Both frames use the same head, so the whole dog moves: on the bark it lunges 1px forward
    (head and body together, the paws planted) with the mouth wide open."""
    out = {}
    rows, _ = with_legs(BODY, BRACE)
    out['bark_0'] = rows_of(place(rows, PX))
    body = list(BODY)
    for y, r in BARK_MOUTH.items():
        body[y] = r
    legs = rows[len(BODY):]
    g = place(legs, PX)
    g = place(body, PX + 1, LEG_ROWS, g)                   # the lunge: everything above the paws
    top = GROUND - len(rows) + 1
    for x, y in BARK_ARCS:
        if 0 <= PX + 1 + x < W:
            g[top + y][PX + 1 + x] = 'z'
    out['bark_1'] = rows_of(g)
    return out


# ---- rolling over for a belly rub ----------------------------------------------------------------
# Lying down, then over onto its side (the ears fold back flat, the short legs tuck up), then on its
# back: the body turned upside down puts the back on the ground and the white belly on top, the ears
# lie folded back on the ground behind the head (turned upside down as they were, they stood on
# the ground like a headstand) and the little legs stay tucked, paws curled, paddling.
FOLDED_EARS = [".........SSSSS..", "........SSnnnSS."]      # lying back along the head, 2 rows
EAR_ROWS = 5                                               # BODY rows 0-4 are only ears


def no_ears(body):
    return ['.' * len(body[0])] * EAR_ROWS + body[EAR_ROWS:]


def roll_frames():
    out = {}
    # rolling onto its side: lying low, ears folded back, legs tucked forward under the belly
    body = no_ears(BODY)
    g = place(body, PX)
    top = GROUND - len(body) + 1
    overlay_rows(g, FOLDED_EARS, PX + 4, top + EAR_ROWS - 1)
    for x, y, ch in ((PX + 23, GROUND - 1, 'k'), (PX + 24, GROUND - 1, 'p'), (PX + 24, GROUND - 2, 'p')):
        g[y][x] = ch                                       # a front paw curled up at the chest
    out['roll_side'] = rows_of(g)
    for k in range(2):
        out[f'belly_{k}'] = rows_of(place(belly_up(k), PX))
    return out


def overlay_rows(g, rows, x0, y0):
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.' and 0 <= y0 + y < H and 0 <= x0 + x < W:
                g[y0 + y][x0 + x] = ch
    return g


# the tucked legs on its back: a short thigh up and the paw curled forward, paddling in turn
TUCKED = [  # per frame: (x in BODY columns, fur, paw dx)
    [(3, 'l', 1), (5, 'k', 0), (15, 'l', 0), (17, 'k', 1)],
    [(3, 'l', 0), (5, 'k', 1), (15, 'l', 1), (17, 'k', 0)],
]


BELLY_HEAD_DX = 6


def belly_up(k):
    """On its back: the torso turned over (back on the ground, the white belly and chest up, the
    little legs tucked with curled paws) and the head lying on its side at ground level, looking
    at you, ears folded back. Turning the whole standing dog over put the head under the body
    (a headstand); turning the head over too hid the belly."""
    flip = lambda rows: list(reversed(rows))
    width = W - PX                                       # the head sits further right than when standing
    torso = flip([r[:21].ljust(width, '.') for r in BODY[10:17]])
    torso = [list(r) for r in torso]
    for y in range(3):                                   # the belly faces up, white from rump to chest
        for x in range(5, 21):
            if torso[y][x] != '.':
                torso[y][x] = 'x' if y == 0 else 'w'
    # the head is turned over too (crown on the ground, chin up: left upright on a turned-over body
    # it read as a monster) and lies at the front of the chest, clear of the belly
    # its lowest rows are trimmed from the neck side into a rounded jaw: taken whole they were the
    # neck and chest line, which turned over became a long flat chin
    jaw = {10: 1, 11: 3, 12: 5}
    head = flip([('.' * (HEAD_X + BELLY_HEAD_DX + jaw.get(y, 0)) + r[HEAD_X + jaw.get(y, 0):])[:width]
                 for y, r in enumerate(BODY[:13]) if y >= EAR_ROWS])
    h = len(head) + 1
    g = [['.'] * width for _ in range(h)]
    for rows in (torso, head):
        off = h - len(rows)
        for y, r in enumerate(rows):
            for x, ch in enumerate(r):
                if ch != '.':
                    g[off + y][x] = ch
    top = h - len(torso)
    for x, fur, dx in TUCKED[k]:                         # thighs up off the belly, paws curled
        if x > 16:
            continue                                     # the front legs are tucked against the chest
        sock = 'p' if fur == 'k' else 'q'
        for i in range(2):
            g[top - 1][x + i] = fur
            g[top - 2][x + i + dx] = sock
    for x, y, ch in ((20 - k, top, 'p'), (21 - k, top, 'p'), (20, top + 1, 'k')):
        g[y][x] = ch                                     # a front paw curled on the chest
    for y, r in enumerate(FOLDED_EARS[::-1]):            # ears folded back, lying on the ground behind the crown
        for x, ch in enumerate(r):
            if ch != '.' and g[h - 2 + y][HEAD_X + BELLY_HEAD_DX - 6 + x] == '.':
                g[h - 2 + y][HEAD_X + BELLY_HEAD_DX - 6 + x] = ch
    return [''.join(r) for r in g]


# ---- spinning with joy ---------------------------------------------------------------------------
# A full turn in place with little hops: side, face-on, the other side, and from behind (the round
# corgi rump with its white fluff), back to the side.
TURN_BACK = [
    "...S.......S....",
    "..SS.......SS...",
    "..SSS.....SSS...",
    "..SSSS...SSSS...",
    "..SSSSSSSSSSS...",
    "..SSSSSSSSSSS...",
    "...SSSSSSSSS....",
    "..bbbbbbbbbbbb..",
    ".bbbbbbbbbbbbbb.",
    "abbbbbbbbbbbbbba",
    "abbbbbwwwwbbbbba",
    "abbbbwwwwwwbbbba",
    "abbbbbwwwwbbbbba",
    ".cbbbbbwwbbbbbc.",
    ".ccbbbbbbbbbbcc.",
    "..cccbbbbbbccc..",
]
TURN_BACK_LEGS = ["..ll.kk..kk.ll..", "..qq.pp..pp.qq..", "..qq.pp..pp.qq.."]


def spin_frames():
    return {'spin_back': rows_of(place(TURN_BACK + TURN_BACK_LEGS, PX + 8)),
            'spin_back_hop': rows_of(place(TURN_BACK + TURN_BACK_LEGS[:1] + TURN_BACK_LEGS[1:2], PX + 8, 2)),
            'turn_b_hop': rows_of(place(TURN_FRONT + TURN_FRONT_LEGS[:2], PX + 8, 2))}


# ---- fetching the ball ---------------------------------------------------------------------------
# A tennis ball rolls in and stops in front; the corgi trots up, dips its head, takes it in its mouth
# and brings it back, then drops it and looks up, waiting for the next throw.
# a 3x3 tennis ball (2x2 was too small to read), its white seam turning as it rolls
BALL_ROLL = [["UTT", "TUT", "TTU"], ["TTU", "TUT", "UTT"], ["TTT", "UUU", "TTT"], ["TUT", "TUT", "TUT"]]
BALL = BALL_ROLL[0]


def ball_at(g, x, frame=0, y=None):
    y = GROUND - 2 if y is None else y
    for dy, r in enumerate(BALL_ROLL[frame % 4]):
        for dx, ch in enumerate(r):
            if 0 <= x + dx < W and 0 <= y + dy < H:
                g[y + dy][x + dx] = ch
    return g


def play_bow():
    """Front end down, rump up: the chest sinks onto the folded front legs (3px, the leg height, so
    nothing is cut off: sinking it 5px clipped the body and it looked thin) and the head, looking
    down, brings the mouth to the ground."""
    blank_rows = ['.' * len(BODY[0])] * LEG_ROWS
    body = shear(with_head(LOOK_HEADS['down_fwd']) + blank_rows, lambda x: 0 if x < 6 else min(LEG_ROWS, (x - 6) // 2 + 1))
    hind, _ = with_legs(BODY, {'far_front': None, 'near_front': None})
    g = [list(r) for r in body]
    for y, r in enumerate(hind[len(BODY):]):              # the hind legs stay standing
        for x, ch in enumerate(r):
            if ch != '.' and x < 10:
                g[len(BODY) + y][x] = ch
    for x in (15, 16, 17, 18):                            # the folded front paws, flat under the chest
        g[-1][x] = 'p' if x > 16 else 'q'
    return [''.join(r) for r in g]


BALL_REST = 30            # canvas x where the rolling ball stops, at the corgi's nose
BALL_DROP = PX + 15       # canvas x where it is set down, at its front paws (facing you)


def fetch_frames():
    """Every frame has the ball, and while it is on the ground it stays where it is (frames without
    it made it blink)."""
    out = {}
    # the ball rolls in from the right and stops at the nose while the corgi watches it
    for i, x in enumerate((38, 35, 32, BALL_REST)):
        rows, _ = with_legs(with_head(LOOK_HEADS['down_fwd']))
        out[f'fetch_ball_{i}'] = rows_of(ball_at(place(rows, PX), x, i))
    # the play bow down to it, the grab, and up with it in the mouth
    out['fetch_bow'] = rows_of(ball_at(place(play_bow(), PX), BALL_REST, 3))
    out['fetch_grab'] = rows_of(ball_at(place(play_bow(), PX), BALL_REST - 1, 3, GROUND - 3))
    for f in range(1):
        rows, _ = with_legs(BODY)
        g = place(rows, PX)
        top = GROUND - len(rows) + 1
        out['fetch_carry_0'] = rows_of(ball_at(g, PX + 24, 0, top + 11))
    # bringing it to you: turned toward the viewer with the ball in its mouth, then set down
    g = place(TURN_3Q + TURN_3Q_LEGS, PX + 4)
    top = GROUND - len(TURN_3Q + TURN_3Q_LEGS) + 1
    out['fetch_3q'] = rows_of(ball_at(g, PX + 4 + 12, 0, top + 10))
    g = place(TURN_FRONT + TURN_FRONT_LEGS, PX + 8)
    top = GROUND - len(TURN_FRONT + TURN_FRONT_LEGS) + 1
    out['fetch_front'] = rows_of(ball_at(g, BALL_DROP, 0, top + 11))
    g = place(TURN_FRONT + TURN_FRONT_LEGS, PX + 8)
    out['fetch_front_drop'] = rows_of(ball_at(g, BALL_DROP, 2))
    # turning back to the side, the ball left lying at its front paws (drawn in front of them)
    out['fetch_3q_drop'] = rows_of(ball_at(place(TURN_3Q + TURN_3Q_LEGS, PX + 4), BALL_DROP, 2))
    rows, _ = with_legs(with_head(LOOK_HEADS['up_fwd']))
    out['fetch_drop'] = rows_of(ball_at(place(rows, PX), BALL_DROP, 2))
    out['bow'] = rows_of(place(play_bow(), PX))
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
    out.update(bark_frames())
    out.update(roll_frames())
    out.update(spin_frames())
    out.update(fetch_frames())
    return out


ANCHOR = (PX + 11, GROUND)

if __name__ == '__main__':
    print(json.dumps(frames(), indent=1))
