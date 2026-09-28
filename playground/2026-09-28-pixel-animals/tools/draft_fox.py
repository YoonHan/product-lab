"""Draft generator for fox frames (stand, idle, walk).

Prints a JSON object of frames to stdout. It is a starting point only:
once frames are copied into sprites/fox.json and hand-edited, that file is
the source of truth. Do not pipe this over sprites/fox.json.

Usage: python3 tools/draft_fox.py > /tmp/fox-frames.json
"""
import json
import math

# Frame canvas. The standing fox was drawn on a 34x22 grid; OX/OY place that
# grid inside the larger canvas so jumps and stretches have room.
W, H = 40, 42
OX, OY = 3, 20
POSE_DY = OY - 8   # key poses in fox_poses.py were drawn with OY = 8
GROUND, LEG_TOP = 21 + OY, 16 + OY

# Torso, head and tail as (row, start column, pixels); legs are added per frame.
TORSO = [
    (10, 6, 'cbbbb'), (11, 3, 'cbbbbbba'), (12, 1, 'xcbbbbbbbd'), (13, 0, 'wxccbbbbdc'),
    (14, 0, 'wwxcccbbc'), (15, 0, 'wwwxccc'), (16, 1, 'wwx'),
    (2, 25, 'd'), (2, 28, 'k'), (3, 24, 'dd'), (3, 27, 'kk'), (4, 24, 'dcd'), (4, 27, 'kbk'),
    (5, 23, 'dccbbab'), (6, 23, 'cbbaaaab'), (7, 23, 'cbbaaaabb'), (8, 22, 'cbbbbbbobbbb'),
    (9, 21, 'ccbbbbbbbbbbe'), (10, 24, 'wwwwwwx'),
    # the back rises 1px mid-body
    (9, 15, 'aaaaaa'), (10, 11, 'baaabbbbbba'), (10, 22, 'bb'), (11, 9, 'cbbbbbbbbbbbbbbwwwwx'),
    (12, 8, 'ccbbbbbbbbbbbbbbwwwwx'), (13, 8, 'cccbbbbbbbbbbbbbwwwx'),
    (14, 9, 'ccccxxxxbbbbbbwwwx'), (15, 8, 'ddccc'), (15, 19, 'cbbbwwx'),
]

# Leg poses: x offset of each row from LEG_TOP down; fewer rows = paw lifted.
POSES = {
    'fwd2': [0, 0, 1, 1, 2, 2], 'fwd1': [0, 0, 0, 1, 1, 1], 'mid': [0, 0, 0, 0, 0, 0],
    'back1': [0, 0, 0, -1, -1, -1], 'back2': [0, 0, -1, -1, -2, -2],
    'liftB': [0, 0, -1, -2, -2], 'liftM': [0, 0, 0, -1], 'liftF': [0, 0, 1, 1, 2],
}
WALK_CYCLE = ['fwd2', 'fwd1', 'back1', 'back2', 'liftB', 'liftM', 'liftF', 'liftF']
# Diagonal pairs move together, half a cycle apart. All legs are 2px wide; the far legs are a
# step darker and sit slightly behind their near partner, so from the rear the order is
# far hind, near hind, far front, near front. Far legs are drawn first.
FAR_HIND = dict(x=8, w=2, top='d', col='l')
NEAR_HIND = dict(x=11, w=2, top='c', col='k')
FAR_FRONT = dict(x=19, w=2, top='d', col='l')
NEAR_FRONT = dict(x=22, w=2, top='c', col='k')


def blank():
    return [['.'] * W for _ in range(H)]


def paint(g, segs, ox=OX, oy=OY):
    for y, x, s in segs:
        for i, ch in enumerate(s):
            if ch != ' ':
                g[y + oy][x + ox + i] = ch
    return g


def shift(g, y0, y1, dy, x0=0, x1=W - 1):
    src = [r[:] for r in g]
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            g[y][x] = '.'
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if src[y][x] != '.' and 0 <= y + dy < H:
                g[y + dy][x] = src[y][x]
    return g


PAW = {'k': 'p', 'l': 'q'}   # leg colour -> paw colour (white socks)


def paint_paw(g, x, y, w, col, toe=False):
    """Colour the paw at the end of a leg: w pixels wide, plus one toe pixel forward on the ground."""
    for j in range(w + (1 if toe else 0)):
        if 0 <= y < H and 0 <= x + j < W:
            g[y][x + j] = PAW.get(col, col)


def leg(g, spec, pose):
    offs = POSES[pose]
    for i, o in enumerate(offs):
        for k in range(spec['w']):
            g[LEG_TOP + i][spec['x'] + OX + o + k] = spec['top'] if (i == 0 and k == 0 and spec['w'] == 2) else spec['col']
    last = LEG_TOP + len(offs) - 1
    paint_paw(g, spec['x'] + OX + offs[-1], last, spec['w'], spec['col'], toe=(len(offs) == 6 and spec['w'] == 2))


# Head box on the standing canvas and the column the head turns around (back of the skull).
HEAD_BOX = (OX + 21, OY + 1, W - 1, OY + 10)
HEAD_PIVOT_X = OX + 23
# Look directions used while idling: (tilt per column, extra lift). Positive tilt raises the snout.
# Look directions used while idling: head rotation in degrees (positive = snout up).
# Each entry is ('rs', degrees, drop, pivot): the head is rotated with a small RotSprite
# (positive degrees lift the snout) and then lowered by `drop` pixels. Looking down lowers
# the whole head instead of bending it far, which keeps the face readable at this size.
LOOK = {'up': ('rs', 55, 0), 'up_fwd': ('rs', 25, 0), 'fwd': None,
        'down_fwd': ('rs', -22, 0, (OX + 24, OY + 10)), 'down': ('rs', -30, 3, (OX + 24, OY + 10))}
HEAD_PIVOT = (OX + 23, OY + 9)   # neck joint the head rotates around


def rotate_head(g, deg):
    """Rotate the head pixels around the neck joint (nearest neighbour, shape preserved)."""
    x0, y0, x1, y1 = HEAD_BOX
    px, py = HEAD_PIVOT
    src = [r[:] for r in g]
    is_head = lambda x, y: x0 + 1 <= x <= x1 and y0 <= y <= y1 and src[y][x] != '.' and x > px - 1
    for y in range(y0, y1 + 1):
        for x in range(x0 + 1, x1 + 1):
            if is_head(x, y):
                g[y][x] = '.'
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    painted = set()
    for y in range(max(0, y0 - 8), min(H, y1 + 8)):
        for x in range(x0 - 2, W):
            # inverse rotation: screen y points down, positive deg lifts the snout
            dx, dy = x - px, y - py
            sx = round(px + dx * ca - dy * sa)
            sy = round(py + dx * sa + dy * ca)
            if 0 <= sx < W and 0 <= sy < H and is_head(sx, sy):
                g[y][x] = src[sy][sx]
                painted.add((x, y))
    # close any gap between the turned head and the body with neck fur
    for x in range(px - 1, px + 5):
        col = [y for y in range(H) if (x, y) in painted]
        if not col:
            continue
        y = max(col) + 1
        while y < H and g[y][x] == '.' and y <= y1 + 2:
            g[y][x] = 'w' if x >= px + 2 else 'b'
            y += 1
    return g


def rotsprite_head(g, deg, drop=0, pivot=None, scale=8, at=None):
    """Rotate the head cleanly: upscale 8x, rotate, then take the most common colour of each
    8x8 block (a simple RotSprite). Keeps 1px features like the eye and nose intact.
    `at` is the head block's top-left corner when the head is not where the standing fox has it."""
    from collections import Counter
    sx0, sy0 = (at[0] - HEAD_BOX[0], at[1] - HEAD_BOX[1] - 1) if at else (0, 0)
    x0, y0, x1, y1 = HEAD_BOX[0] + sx0, HEAD_BOX[1] + sy0, W - 1, HEAD_BOX[3] + sy0
    hx = HEAD_PIVOT[0] + sx0                 # the head is everything right of the neck joint
    px, py = pivot or (HEAD_PIVOT[0] + sx0, HEAD_PIVOT[1] + sy0)   # the point it turns around
    src = [r[:] for r in g]
    # The ears are thin triangles that a majority-vote rotation would shave down, so they are
    # left out of the rotation and pasted back, unrotated, onto the turned head.
    ear_rows = range(y0 + 1, y0 + 4)
    ears = {'far': [], 'near': []}
    for y in ear_rows:
        for x in range(x0 + 3, x0 + 10):
            if src[y][x] != '.':
                ears['far' if x < x0 + 6 else 'near'].append((x, y, src[y][x]))
    ear_px = {(x, y) for e in ears.values() for x, y, _ in e}
    is_head = lambda x, y: (x0 + 1 <= x <= x1 and y0 <= y <= y1 and src[y][x] != '.' and x > hx - 1
                            and (x, y) not in ear_px)
    for y in range(y0, y1 + 1):
        for x in range(x0 + 1, x1 + 1):
            if is_head(x, y) or (x, y) in ear_px:
                g[y][x] = '.'
    a = math.radians(deg); ca, sa = math.cos(a), math.sin(a)
    painted = set()
    for y in range(max(0, y0 - 8), min(H, y1 + 10)):
        for x in range(x0 - 2, W):
            votes = Counter(); total = 0
            for sy_ in range(scale):
                for sx_ in range(scale):
                    # sample point inside the destination pixel, rotated back into the source
                    dx = x + (sx_ + 0.5) / scale - px - 0.5
                    dy = y - drop + (sy_ + 0.5) / scale - py - 0.5
                    sx = math.floor(px + 0.5 + dx * ca - dy * sa)
                    sy = math.floor(py + 0.5 + dx * sa + dy * ca)
                    total += 1
                    if 0 <= sx < W and 0 <= sy < H and is_head(sx, sy):
                        votes[src[sy][sx]] += 1
            if votes and sum(votes.values()) * 2 > total:
                # the eye and nose win ties so they never vanish
                ch = max(votes, key=votes.get)
                g[y][x] = ch
                painted.add((x, y))
    # drop stray pixels that ended up with no neighbour at all (rotation noise at ear tips)
    for (x, y) in list(painted):
        if all(not (0 <= x + dx < W and 0 <= y + dy < H) or g[y + dy][x + dx] == '.'
               for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]):
            g[y][x] = '.'; painted.discard((x, y))
    # the eye and the nose share a colour, so place each of them as exactly one rotated pixel
    for y in range(H):
        for x in range(W):
            if (x, y) in painted and g[y][x] in 'eo':
                g[y][x] = 'b'
    for ex, ey, ch in [(x0 + 8, y0 + 7, 'o'), (x0 + 12, y0 + 8, 'e')]:    # eye, nose on the standing head
        ux, uy = ex + 0.5 - px - 0.5, ey + 0.5 - py - 0.5
        rx = math.floor(px + 0.5 + ux * ca + uy * sa); ry = math.floor(py + 0.5 - ux * sa + uy * ca) + drop
        if 0 <= rx < W and 0 <= ry < H:
            g[ry][rx] = ch
    # paste the ears: each keeps its shape and moves with the point where it meets the head
    for pixels in ears.values():
        if not pixels:
            continue
        bx = sum(x for x, _, _ in pixels) / len(pixels) + 0.5
        by = max(y for _, y, _ in pixels) + 1.0            # the ear's base on top of the head
        ux, uy = bx - px - 0.5, by - py - 0.5
        rx = px + 0.5 + ux * ca + uy * sa; ry = py + 0.5 - ux * sa + uy * ca + drop
        ox, oy = round(rx - bx), round(ry - by)
        for x, y, ch in pixels:
            if 0 <= x + ox < W and 0 <= y + oy < H:
                g[y + oy][x + ox] = ch
                painted.add((x + ox, y + oy))
    # close gaps between the turned head and the neck: below the head, and sideways behind it
    for x in range(hx - 1, hx + 5):
        col = [y for y in range(H) if (x, y) in painted]
        if not col:
            continue
        y = max(col) + 1
        while y < H and g[y][x] == '.' and y <= y1 + 2:
            g[y][x] = 'w' if x >= hx + 2 else 'b'
            y += 1
    for y in range(y0, y1 + 3):
        row = [x for x in range(W) if (x, y) in painted]
        if not row:
            continue
        x = min(row) - 1
        gap = 0
        while x > x0 - 3 and g[y][x] == '.' and gap < 3:
            x -= 1; gap += 1
        if 0 < gap < 3 and g[y][x] != '.':
            for xx in range(x + 1, min(row)):
                g[y][xx] = 'b'
    return g


def tilt_head(g, k, lift, drop):
    """Tilt the head by k px per column (snout up for k > 0), then move it by lift/drop."""
    x0, y0, x1, y1 = HEAD_BOX
    px = HEAD_PIVOT[0]
    src = [r[:] for r in g]
    for y in range(y0, y1 + 1):
        for x in range(px + 1, x1 + 1):
            g[y][x] = '.'
    for y in range(y0, y1 + 1):
        for x in range(px + 1, x1 + 1):
            ch = src[y][x]
            if ch != '.':
                ny = y - round((x - px) * k) - lift + drop
                if 0 <= ny < H:
                    g[ny][x] = ch
    if drop:   # the back of the skull follows the drop; the neck behind it stays
        for y in range(y1, y0 - 1, -1):
            for x in range(x0 + 1, px + 1):
                if src[y][x] != '.' and y < OY + 9:
                    g[y][x] = '.'
        for y in range(y0, y1 + 1):
            for x in range(x0 + 1, px + 1):
                if src[y][x] != '.' and y < OY + 9 and y + drop < H:
                    g[y + drop][x] = src[y][x]
    return g


def turn_head(g, look):
    if look[0] == 'rs':
        return rotsprite_head(g, *look[1:])
    return rotate_head(g, look[1]) if look[0] == 'rot' else tilt_head(g, *look[1:])


def frame(breath=0, tail_up=0, poses=None, look=None):
    g = paint(blank(), TORSO)
    if look:
        turn_head(g, look)
    if tail_up:
        shift(g, 10 + OY, 16 + OY, -1, OX, 5 + OX)
    if breath:
        shift(g, 0, 15 + OY, 1)
    p = poses or {}
    for spec, name in [(FAR_HIND, 'far_hind'), (FAR_FRONT, 'far_front'), (NEAR_HIND, 'near_hind'), (NEAR_FRONT, 'near_front')]:
        leg(g, spec, p.get(name, 'mid'))
    return [''.join(r) for r in g]


def pose(segs):
    return [''.join(r) for r in paint(blank(), segs, 0, POSE_DY)]


def rows_of(g):
    return [''.join(r) for r in g]


def grid(rows):
    return [list(r) for r in rows]


def shear(rows, k, pivot_x, lift=0):
    # tilt the whole sprite: columns right of pivot_x rise by k px per column, then raise by `lift`
    src = grid(rows); out = [['.'] * W for _ in range(H)]
    for x in range(W):
        dy = -round((x - pivot_x) * k) - lift
        for y in range(H):
            ch = src[y][x]
            if ch != '.' and 0 <= y + dy < H:
                out[y + dy][x] = ch
    return rows_of(out)


# Leg joints on the standing canvas: (x, y) of the top pixel, width, colours.
JOINTS = {
    'far_hind': (8 + OX, LEG_TOP, 2, 'd', 'l'), 'far_front': (19 + OX, LEG_TOP, 2, 'd', 'l'),
    'near_hind': (11 + OX, LEG_TOP, 2, 'c', 'k'), 'near_front': (22 + OX, LEG_TOP, 2, 'c', 'k'),
}
LEG_ORDER = ['far_hind', 'far_front', 'near_hind', 'near_front']


def line_leg(g, name, dx, dy, k=0.0, lift=0, pivot_x=12):
    """Straight leg from a joint moved by the same shear as the body to joint + (dx, dy)."""
    x0, y0, w, top, col = JOINTS[name]
    y0 += -round((x0 - pivot_x) * k) - lift
    n = max(abs(dx), abs(dy), 1)
    for i in range(n + 1):
        x = x0 + round(dx * i / n); y = y0 + round(dy * i / n)
        for j in range(w):
            if 0 <= y < H and 0 <= x + j < W:
                g[y][x + j] = top if (i == 0 and j == 0 and w == 2) else col
    paint_paw(g, x0 + dx, y0 + dy, w, col)


def seg(g, x0, y0, x1, y1, w, colors, start=0, brush=False):
    """Draw a leg segment `w` pixels wide. colors(i, j) picks each pixel.
    brush=True also fills the pixel above each step of a shallow segment (wider than tall), which
    would otherwise read as a thin staircase; steeper segments already look 2px thick."""
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        x = x0 + round((x1 - x0) * i / n); y = y0 + round((y1 - y0) * i / n)
        thick = brush and abs(x1 - x0) > abs(y1 - y0) and i > 0
        for j in range(w):
            for yy in ([y, y - 1] if thick else [y]):
                if 0 <= yy <= GROUND and 0 <= x + j < W:
                    g[yy][x + j] = colors(start + i, j)
    return n


LEG_BONES = {  # upper, lower bone length and which way the middle joint folds (1: forward)
    'front': (2.6, 3.0, 1),    # the wrist folds forward
    'hind': (2.8, 3.0, -1),    # the hock folds back
}


def solve_knee(kind, px_, py_):
    """2-bone IK: knee offset for a paw at (px_, py_) from the joint, with fixed bone lengths.
    A paw out of reach is pulled in along the same direction (the leg is straight)."""
    a, b, bend = LEG_BONES[kind]
    d = math.hypot(px_, py_)
    if d > a + b:
        px_, py_ = px_ * (a + b) / d, py_ * (a + b) / d
        d = a + b
    d = max(d, abs(a - b) + 0.01)
    ang = math.atan2(py_, px_)
    off = math.acos(max(-1, min(1, (a * a + d * d - b * b) / (2 * a * d))))
    k = ang - bend * off       # y points down, so turning by -off puts the knee in front
    return (round(a * math.cos(k)), round(a * math.sin(k))), (round(px_), round(py_))


def jleg(g, name, knee, paw, k=0.0, lift=0, pivot_x=12, brush=True):
    """Two-segment leg: joint -> knee (elbow / hock) -> paw, offsets relative to the joint."""
    x0, y0, w, top, col = JOINTS[name]
    y0 += -round((x0 - pivot_x) * k) - lift
    kx, ky = x0 + knee[0], y0 + knee[1]
    px_, py_ = x0 + paw[0], y0 + paw[1]
    colors = (lambda i, j: top if (i == 0 and j == 0) else col) if w == 2 else (lambda i, j: col)
    n = seg(g, x0, y0, kx, ky, w, colors, brush=brush)
    seg(g, kx, ky, px_, py_, w, colors, n, brush=brush)
    paint_paw(g, px_, min(py_, GROUND), w, col, toe=(w == 2 and py_ >= GROUND))


def torso_only():
    return rows_of(paint(blank(), TORSO))


DIG_HEAD = (-25, 1)   # (degrees, drop) of the head while digging


def frames():
    import fox_poses as P
    out = {'stand': frame(), 'sit_pose': pose(P.SIT), 'lie_pose': pose(P.LIE), 'curl_pose': pose(P.CURL), 'bow_pose': pose(P.BOW), 'itch_pose': pose(P.ITCH)}
    for i, (b, t) in enumerate([(0, 0), (0, 1), (1, 1), (1, 0)]):
        out[f'idle_{i}'] = frame(b, t)
    for f in range(8):
        a, b = WALK_CYCLE[f], WALK_CYCLE[(f + 4) % 8]
        out[f'walk_{f}'] = frame(1 if f in (1, 5) else 0, 1 if f in (2, 3, 4, 5) else 0,
                                 {'near_hind': a, 'far_front': a, 'far_hind': b, 'near_front': b})
    out.update(pounce_frames())
    out.update(look_frames())
    out.update(other_frames())
    out['turn_a'] = [''.join(r) for r in paint(blank(), P.THREE_QUARTER, 0, 0)]
    out['turn_b'] = [''.join(r) for r in paint(blank(), P.FRONT, 0, 0)]
    return out


def posed(k, lift, legs, pivot_x=12, tail_up=0):
    """Body tilted by `k`, raised by `lift`, legs as {name: (dx, dy)} from each joint."""
    t = paint(blank(), TORSO)
    if tail_up:
        shift(t, 10 + OY, 16 + OY, -tail_up, OX, 6 + OX)
    g = grid(shear(rows_of(t), k, pivot_x, lift))
    for name in LEG_ORDER:
        if name in legs:
            line_leg(g, name, *legs[name], k=k, lift=lift, pivot_x=pivot_x)
    return rows_of(g)


def rotate_all(rows, deg, pivot, lift=0, dx=0):
    """Rotate the whole sprite around pivot (positive = nose up), then move it up by lift."""
    a = math.radians(deg); ca, sa = math.cos(a), math.sin(a)
    px, py = pivot
    src = grid(rows); out = [['.'] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            ux, uy = x - dx - px, y + lift - py
            sx = round(px + ux * ca - uy * sa); sy = round(py + ux * sa + uy * ca)
            if 0 <= sx < W and 0 <= sy < H and src[sy][sx] != '.':
                out[y][x] = src[sy][sx]
    return out


def rot_point(x, y, deg, pivot, lift=0, dx=0):
    a = math.radians(deg); ca, sa = math.cos(a), math.sin(a)
    px, py = pivot
    ux, uy = x - px, y - py
    return round(px + ux * ca + uy * sa) + dx, round(py - ux * sa + uy * ca) - lift


def flying(deg, lift, legs, pivot=None, tail_up=0, dx=0):
    """Body rotated by deg; legs as {name: (knee, paw)} relative to each rotated joint.
    A paw of 'G' is placed on the ground."""
    pivot = pivot or (OX + 16, OY + 12)
    t = paint(blank(), TORSO)
    if tail_up:
        shift(t, 10 + OY, 16 + OY, -tail_up, OX, 6 + OX)
    g = rotate_all(rows_of(t), deg, pivot, lift, dx)
    for name in LEG_ORDER:
        if name not in legs:
            continue
        x0, y0, w, top, col = JOINTS[name]
        jx, jy = rot_point(x0, y0 - 1, deg, pivot, lift, dx)
        jy += 1
        _, paw = legs[name]
        # only the paw is used; the knee comes from the fixed bone lengths
        (kdx, kdy), (pdx, pdy) = solve_knee('front' if 'front' in name else 'hind',
                                            paw[0], (GROUND - jy) if paw[1] == 'G' else paw[1])
        kx, ky = jx + kdx, jy + kdy
        px_, py_ = jx + pdx, jy + pdy
        colors = (lambda i, j: top if (i == 0 and j == 0) else col) if w == 2 else (lambda i, j: col)
        n = seg(g, jx, jy, kx, ky, w, colors)
        seg(g, kx, ky, px_, py_, w, colors, n)
        paint_paw(g, px_, py_, w, col)
    return rows_of(g)


def flying_joint_y(name, deg, lift, pivot=None, dx=0):
    pivot = pivot or (OX + 16, OY + 12)
    x0, y0, *_ = JOINTS[name]
    return rot_point(x0, y0 - 1, deg, pivot, lift, dx)[1] + 1


def pounce_frames():
    """Mouse pounce: crouch and wiggle, launch steeply, arch at the top, dive nose-first.
    The airborne keys get an in-between each, interpolating angle, height and legs."""
    tuck = {'near_front': ((1, 2), (3, 3)), 'far_front': ((1, 2), (2, 3)),
            'near_hind': ((-1, 2), (1, 4)), 'far_hind': ((-1, 2), (0, 4))}
    KEYS = [  # (degrees, lift, legs, tail_up)
        (35, 1, {'near_hind': ((-2, 3), (-4, 'G')), 'far_hind': ((-1, 3), (-3, 'G')),        # launch
                 'near_front': ((1, 2), (3, 2)), 'far_front': ((1, 2), (2, 3))}, 0),
        (55, 8, {'near_hind': ((-2, 3), (-4, 6)), 'far_hind': ((-1, 3), (-3, 6)),            # rising steeply
                 'near_front': ((1, 2), (3, 2)), 'far_front': ((1, 2), (2, 3))}, 0),
        (10, 15, tuck, 1),                                                                  # apex, curled up
        (-45, 13, {'near_front': ((1, 3), (2, 6)), 'far_front': ((1, 3), (1, 6)),            # turning over
                   'near_hind': ((-1, -1), (-3, -2)), 'far_hind': ((-1, -1), (-2, -3))}, 1),
        (-70, 7, {'near_front': ((0, 3), (0, 6)), 'far_front': ((-1, 3), (-1, 6)),           # diving nose-first
                  'near_hind': ((-1, -2), (-2, -4)), 'far_hind': ((-1, -2), (-1, -4))}, 2),
        (-78, 0, {'near_front': ((0, 2), (0, 'G')), 'far_front': ((-1, 2), (-1, 'G')),       # nose in the ground
                  'near_hind': ((-1, -2), (-1, -4)), 'far_hind': ((-1, -2), (0, -4))}, 2),
    ]
    def numeric(deg, lift, legs):
        return {n: (kn, (pw[0], GROUND - flying_joint_y(n, deg, lift) if pw[1] == 'G' else pw[1])) for n, (kn, pw) in legs.items()}
    # getting ready: the fox sinks down on folded legs and looks up at where the mouse is
    def crouch(drop, head_deg, tail=0, rump=0):
        paws = {'far_hind': (1, 'G'), 'near_hind': (1, 'G'), 'far_front': (2, 'G'), 'near_front': (2, 'G')}
        g = grid(flying(0, -drop, {n: (None, pw) for n, pw in paws.items()}, tail_up=tail))
        if rump:                                          # the rump wiggles up before the leap
            g = grid(moved(rows_of(g), 0, OX + 12, 0, GROUND - 2, 0, -rump, keep=True))
        if head_deg:
            g = rotsprite_head(g, head_deg, 0, (HEAD_PIVOT[0], HEAD_PIVOT[1] + drop),
                               at=(HEAD_BOX[0], HEAD_BOX[1] + 1 + drop))
        return rows_of(g)
    out = {'pounce_0': crouch(2, 20), 'pounce_1': crouch(3, 40), 'pounce_2': crouch(3, 40, tail=1, rump=1)}
    air = []
    for i, (deg, lift, legs, tail) in enumerate(KEYS):
        air.append(flying(deg, lift, legs, tail_up=tail))
        if i == len(KEYS) - 1:
            break
        ndeg, nlift, nlegs, ntail = KEYS[i + 1]
        mdeg, mlift = (deg + ndeg) / 2, round((lift + nlift) / 2)
        a, b = numeric(deg, lift, legs), numeric(ndeg, nlift, nlegs)
        mid = {}
        for n in a:
            (ka, pa), (kb, pb) = a[n], b[n]
            kn = (round((ka[0] + kb[0]) / 2), round((ka[1] + kb[1]) / 2))
            pw = [round((pa[0] + pb[0]) / 2), round((pa[1] + pb[1]) / 2)]
            if pw[1] >= GROUND - flying_joint_y(n, mdeg, mlift):
                pw[1] = 'G'
            mid[n] = (kn, tuple(pw))
        air.append(flying(mdeg, mlift, mid, tail_up=max(tail, ntail)))
    # the dive carries further forward so the head lands where the stuck pose has its hole
    AIR_DX = [0, 0, 0, 0, 0, 0, 1, 3, 5, 6, 7]
    for i, rows in enumerate(air):
        out[f'pounce_air_{i}'] = moved(rows, 0, W - 1, 0, H - 1, AIR_DX[i], 0)
    # Stuck: the head stays buried while the rump comes down until the hind paws reach the ground
    # (a play bow with the head in the snow). Then the fox braces all four legs and shoves its body
    # back and up, again and again, until the head pops free. The head is drawn once and never
    # moves while it is stuck; only the body turns about the neck and shifts, and the legs are
    # solved from fixed-length bones so the planted paws stay where they are.
    import fox_poses as P
    NECK = (28, 37)                                       # where the neck bends in the bow pose
    BOW_HEAD = (25, 17 + POSE_DY)                         # head block corner in the bow pose
    # the bow is a long, stretched pose; stuck in the snow the fox is hunched up instead, so the
    # body is squeezed toward the neck and the hind legs come forward with it
    SQUEEZE = 0.8
    sq = lambda x: round(NECK[0] + (x - NECK[0]) * SQUEEZE)
    BOW_JOINTS = {'far_hind': (sq(8), 34), 'near_hind': (sq(11), 35), 'far_front': (28, 38), 'near_front': (26, 38)}
    legless = [sg for sg in P.BOW if not (sg[1] in (8, 11) and sg[0] >= 22 and sg[2][:1] in 'lkqp'
                                          or sg[0] >= 39 and sg[1] >= 27) and sg != (22, 8, 'dl')]
    bow = grid(pose(legless))
    head_px = {(x, y) for y in range(H) for x in range(W)
               if bow[y][x] != '.' and x >= BOW_HEAD[0] + 2 and y <= BOW_HEAD[1] + 8}
    body = [['.' if (x, y) in head_px else bow[y][x] for x in range(W)] for y in range(H)]
    squeezed = [['.'] * W for _ in range(H)]
    for x in range(W):
        src_x = round(NECK[0] + (x - NECK[0]) / SQUEEZE)
        if 0 <= src_x < W and x <= NECK[0]:
            for y in range(H):
                squeezed[y][x] = body[y][src_x]
        elif x > NECK[0]:
            for y in range(H):
                squeezed[y][x] = body[y][x]
    body = squeezed
    only_head = [[bow[y][x] if (x, y) in head_px else '.' for x in range(W)] for y in range(H)]
    buried_head = rotsprite_head([r[:] for r in only_head], -65, 0, NECK, at=BOW_HEAD)
    popping_head = rotsprite_head([r[:] for r in only_head], -32, 0, NECK, at=BOW_HEAD)
    lifted_head = rotsprite_head([r[:] for r in only_head], -8, 0, NECK, at=BOW_HEAD)
    MOUND = [(x, GROUND) for x in range(28, 37)] + [(x, GROUND - 1) for x in range(29, 36)] + \
            [(30, GROUND - 2), (33, GROUND - 2), (34, GROUND - 2)]
    planted = {'far_hind': (sq(7), GROUND), 'near_hind': (sq(10), GROUND), 'far_front': (32, GROUND), 'near_front': (30, GROUND)}
    NECK_TOP, HOLE = (25, 35), (32, 39)                   # neck from the chest down into the hole
    def neck(g, start):
        """A 6px-thick neck from `start` (moves with the body) to the hole (stays put): orange,
        with the cream throat along its lower side."""
        (ax, ay), (bx, by) = start, HOLE
        L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
        for y in range(H):
            for x in range(W):
                t = ((x + 0.5 - ax) * ux + (y + 0.5 - ay) * uy) / L
                if not 0.2 <= t <= 1.05:             # starts inside the chest, so no bump on the back
                    continue
                side = (y + 0.5 - ay) * ux - (x + 0.5 - ax) * uy   # > 0: throat side (below)
                if -2.5 <= side <= 3.0:
                    g[y][x] = 'w' if side > 1.3 else 'x' if side > 0.5 else 'b'
    def stuck(turn=0.0, shove=(0, 0), paws=None, head=None, mound=MOUND, dirt=()):
        """Body turned about the neck by `turn` (negative raises the rump) and shoved by (dx, dy)."""
        sx, sy = shove
        g = rotate_all(rows_of(body), turn, NECK, -sy, sx)
        if shove != (0, 0) and head is not None:          # popping out: keep the neck joined up
            base = rotate_all(rows_of(body), turn, NECK, 0, 0)
            for y in range(H):
                for x in range(NECK[0] - 6, NECK[0] + 3):
                    if g[y][x] == '.' and base[y][x] != '.':
                        g[y][x] = base[y][x]
        if head is None:                                  # buried: only the neck shows, going in
            neck(g, rot_point(*NECK_TOP, turn, NECK, -sy, sx))
            for y in range(H - 1):                        # fill notches (up to 2px) where the neck meets the back
                for x in range(1, W - 2):
                    if (g[y][x] == '.' and g[y][x - 1] != '.' and g[y + 1][x] != '.'
                            and (g[y][x + 1] != '.' or (g[y][x + 2] != '.' and g[y + 1][x + 1] != '.'))):
                        g[y][x] = g[y + 1][x]
        else:
            for y in range(H):
                for x in range(W):
                    if head[y][x] != '.' and y < GROUND - 1:
                        g[y][x] = head[y][x]
        for n in LEG_ORDER:
            jx, jy = rot_point(*BOW_JOINTS[n], turn, NECK, -sy, sx)
            x0, y0, w, top, col = JOINTS[n]
            px_, py_ = (paws or planted)[n]
            (kdx, kdy), (pdx, pdy) = solve_knee('front' if 'front' in n else 'hind', px_ - jx, py_ - jy)
            colors = lambda i, j, top=top, col=col: top if (i == 0 and j == 0) else col
            k = seg(g, jx, jy, jx + kdx, jy + kdy, w, colors)
            seg(g, jx + kdx, jy + kdy, jx + pdx, jy + pdy, w, colors, k)
            paint_paw(g, jx + pdx, min(jy + pdy, GROUND), w, col, toe=(jy + pdy >= GROUND))
        for x, y in list(mound) + list(dirt):
            if 0 <= x < W and 0 <= y < H and (g[y][x] == '.' or (x, y) in mound):
                g[y][x] = 'y'
        return rows_of(g)
    # rump coming down: hind legs hang until they reach the ground
    hanging = {'far_hind': (sq(9), GROUND - 4), 'near_hind': (sq(12), GROUND - 3), **{n: planted[n] for n in ('far_front', 'near_front')}}
    g = grid(out['pounce_air_10'])                         # the snow heaps up the moment the head goes in
    for x, y in MOUND:
        if g[y][x] == '.' or g[y][x] in 'wxbcd':
            g[y][x] = 'y'
    out['pounce_air_10'] = rows_of(g)
    out['pounce_settle_0'] = stuck(-40, paws={**hanging, 'far_hind': (sq(12), GROUND - 9), 'near_hind': (sq(15), GROUND - 8)})
    out['pounce_settle_1'] = stuck(-24, paws={**hanging, 'far_hind': (sq(10), GROUND - 5), 'near_hind': (sq(13), GROUND - 4)})
    out['pounce_settle_2'] = stuck(-10, paws={**planted, 'far_hind': (sq(8), GROUND - 1), 'near_hind': (sq(11), GROUND - 1)})
    out['pounce_stuck'] = stuck()
    # shoving back and up along the diagonal, dirt flying at the hole
    spray = lambda k: [(27 - k, GROUND - 3 - k), (37 + k, GROUND - 4 - k), (38 + k, GROUND - 4 - k), (26 - k, GROUND - 2)]
    out['pounce_shove_0'] = stuck(6, (-2, 0))            # leaning back: rump drops, legs slant
    out['pounce_shove_1'] = stuck(12, (-4, 1), dirt=spray(0))   # hauling with everything
    # the head comes free: out of the ground with a burst of dirt, then up into the bow
    out['pounce_pop'] = stuck(10, (-3, 0), head=popping_head, mound=MOUND[:9] + MOUND[9:16],
                              dirt=spray(1) + [(31, GROUND - 7), (32, GROUND - 8), (35, GROUND - 6)])
    out['pounce_pop_1'] = stuck(4, (-1, -1), head=lifted_head, mound=MOUND[:9] + MOUND[9:12],
                                dirt=[(33, GROUND - 10), (36, GROUND - 9), (26, GROUND - 5)])
    return out

def edit(rows, pixels):
    g = grid(rows)
    for x, y, ch in pixels:
        g[y][x] = ch
    return rows_of(g)


def moved(rows, x0, x1, y0, y1, dx, dy, keep=False):
    """Move the pixels inside a box by (dx, dy). Vacated pixels become transparent,
    or keep the original picture underneath when keep=True (e.g. a neck stretching)."""
    g = grid(rows); src = grid(rows)
    if not keep:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                g[y][x] = '.'
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if src[y][x] != '.' and 0 <= y + dy < H and 0 <= x + dx < W:
                g[y + dy][x + dx] = src[y][x]
    return rows_of(g)


def to_ground(name, k, lift, pivot_x=12, dx=0):
    """Leg from a (sheared) joint straight down to the ground, offset by dx."""
    x0, y0, *_ = JOINTS[name]
    y = y0 - round((x0 - pivot_x) * k) - lift
    return (dx, GROUND - y)


def other_frames():
    import fox_poses as P
    out = {}
    stand = frame()
    HX, HY = OX + 21, OY + 2          # head block top-left on the standing canvas

    # --- run: gallop with jointed legs (knee / hock bends); 'G' puts the paw on the ground
    def run(k, lift, legs, tail=0, head_dy=0, brush=True):
        t = paint(blank(), TORSO)
        if tail:
            shift(t, 10 + OY, 16 + OY, -tail, OX, 6 + OX)
        if head_dy:
            t = grid(moved(rows_of(t), HX + 1, W - 1, 0, HY + 7, 0, head_dy))
        g = grid(shear(rows_of(t), k, 12, lift))
        for name in LEG_ORDER:
            knee, paw = legs[name]
            x0, y0, *_ = JOINTS[name]
            gy = GROUND - (y0 - round((x0 - 12) * k) - lift)
            paw = (paw[0], gy if paw[1] == 'G' else paw[1])
            jleg(g, name, knee, paw, k, lift, brush=brush)
        return rows_of(g)
    # A gallop, as a fox runs: the front paws land, then the hind paws, the hinds push off and the
    # fox flies stretched out, front legs reaching forward and hind legs kicked back. Near and far
    # legs of a pair move almost together. Legs are two bones of fixed length (LEG_BONES); each
    # frame only says where the paw is and the knee is solved from the bone lengths, so legs never
    # stretch or shrink. On the ground a paw slides back at the running speed.
    RUN_FRAMES = 8                                        # 1 tick each: a stride every 0.4s
    STANCE = 0.3                                          # share of the stride a paw is on the ground
    RUN_STRIDE = {'front': (4, -2), 'hind': (2, -4)}      # paw x on the ground: lands, leaves
    RUN_SWING = {  # (phase, paw x, height above the ground) after the paw leaves the ground
        'front': [(0.42, -1, 3), (0.6, 1, 3), (0.78, 6, 3), (0.92, 5, 1.5)],   # fold, then reach far forward
        'hind': [(0.42, -6, 3), (0.65, -6, 3), (0.85, 0, 3)],                 # kick back and hold, fold forward
    }
    RUN_PHASE = {'near_front': 0.0, 'far_front': 0.94, 'near_hind': 0.7, 'far_hind': 0.64}
    def paw_path(kind, phase, ground):
        fx, bx = RUN_STRIDE[kind]
        if phase < STANCE:                                # planted: slides from front to back
            t = phase / STANCE
            return fx + (bx - fx) * t, ground
        keys = [(STANCE, bx, 0)] + RUN_SWING[kind] + [(1.0, fx, 0)]
        for (p0, x0_, h0), (p1, x1_, h1) in zip(keys, keys[1:]):
            if p0 <= phase <= p1:
                t = (1 - math.cos(math.pi * (phase - p0) / (p1 - p0))) / 2
                return x0_ + (x1_ - x0_) * t, ground - (h0 + (h1 - h0) * t)
        return fx, ground
    for i in range(RUN_FRAMES):
        f = i / RUN_FRAMES
        down = sum(((f + RUN_PHASE[n]) % 1) < STANCE for n in LEG_ORDER)
        lift = 1 if down == 0 else 0                      # a 1px float while all paws are off the ground
        pitch = 0.0                                       # no see-saw: it made the back line wobble
        legs = {}
        for n in LEG_ORDER:
            kind = 'front' if 'front' in n else 'hind'
            x0, y0, *_ = JOINTS[n]
            ground = GROUND - (y0 - round((x0 - 12) * pitch) - lift)
            px_, py_ = paw_path(kind, (f + RUN_PHASE[n]) % 1, ground)
            if n.startswith('far'):
                px_ -= 1                                  # the far leg sits 1px further back
            legs[n] = solve_knee(kind, px_, py_)
        # the head rides with the body (a separate dip doubled the bob); the tail lifts while airborne
        out[f'run_{i}'] = run(pitch, lift, legs, 1 if lift else 0, 0, brush=False)

    # --- sit: the rear lowers around the front legs, then the drawn sitting pose
    def rear_down(k):
        legs = {n: to_ground(n, k, 0, 25) for n in LEG_ORDER}
        legs['near_hind'] = (legs['near_hind'][0] + 2, legs['near_hind'][1])
        legs['far_hind'] = (legs['far_hind'][0] + 2, legs['far_hind'][1])
        return posed(k, 0, legs, pivot_x=25)
    for i, k in enumerate([0.06, 0.12, 0.18, 0.24, 0.3]):
        out[f'sit_{"abcde"[i]}'] = rear_down(k)
    out['sit_0'] = out['sit_b']; out['sit_1'] = out['sit_d']
    out['sit_2'] = pose(P.SIT)

    # --- lie down: rear first, then the chest, then the drawn lying pose
    out['lie_a'] = rear_down(0.08)
    out['lie_0'] = rear_down(0.15)
    low = {n: to_ground(n, 0.05, -3) for n in LEG_ORDER}
    low['near_front'] = (2, low['near_front'][1]); low['far_front'] = (2, low['far_front'][1])
    out['lie_1'] = posed(0.05, -3, low)
    mid = {n: to_ground(n, 0.1, -1) for n in LEG_ORDER}
    mid['near_front'] = (1, mid['near_front'][1]); mid['far_front'] = (1, mid['far_front'][1])
    out['lie_b'] = posed(0.1, -1, mid)
    out['lie_2'] = moved(pose(P.LIE), 20, 39, 0, H - 1, 0, -1)          # head still coming down
    out['lie_3'] = pose(P.LIE)
    # getting up: the chest rises on straightened front legs while the rear stays down
    no_front_paws = [s for s in P.LIE if not (s[0] >= 28 and s[1] >= 26)]
    def chest_up(deg):
        g = rotate_all(pose(no_front_paws), deg, (OX + 10, GROUND), 0)
        for leg_x, top_col, col in [(OX + 21, 'd', 'l'), (OX + 24, 'c', 'k')]:
            # the leg starts under the chest: only look at the lowest few rows so the chin never counts
            body = [y for y in range(GROUND - 5, GROUND + 1) if g[y][leg_x] != '.' or g[y][leg_x + 1] != '.']
            top = max(min(body) if body else GROUND - 4, GROUND - 5)
            for y in range(top, GROUND + 1):
                for j in range(2):
                    g[y][leg_x + j] = top_col if (y == top and j == 0) else col
            paint_paw(g, leg_x, GROUND, 2, col, toe=True)
        return rows_of(g)
    out['lieup_h'] = chest_up(7)      # halfway
    out['lieup_0'] = chest_up(14)

    # --- curl up and sleep; the last two frames breathe
    out['curl_0'] = moved(pose(P.LIE), OX + 21, W - 1, OY + 5, OY + 13, 0, 2)   # whole head lowered onto the paws
    out['curl_1'] = pose(P.CURL)
    out['curl_2'] = moved(pose(P.CURL), 9, 21, 0, 23 + POSE_DY, 0, 1)   # breathe out: back sinks 1px (head stays)
    # sleeping: z's rise 1px a step from the head, swaying a little and growing as they go,
    # then break up into loose pixels and vanish; a new z starts every 8 steps
    Z_GLYPHS = {3: ["zzz", "..z", ".z.", "zzz"],
                4: ["zzzz", "..z.", ".z..", "zzzz"],
                5: ["zzzzz", "...z.", "..z..", ".z...", "zzzzz"]}
    Z_LIFE = [3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5]      # glyph size per step of a z's life
    def z_pixels(age):
        size = Z_LIFE[age]
        cx = 27.5 + age * 0.45 + 0.8 * math.sin(age * 0.8)
        cy = 28.5 - age
        x0, y0 = round(cx - size / 2), round(cy - len(Z_GLYPHS[size]) / 2)
        pix = [(x0 + dx, y0 + dy) for dy, r in enumerate(Z_GLYPHS[size]) for dx, ch in enumerate(r) if ch == 'z']
        if age == len(Z_LIFE) - 2:          # fading: the corners go first
            pix = [p for i, p in enumerate(pix) if i % 4 != 3]
        elif age == len(Z_LIFE) - 1:        # then only every other pixel is left
            pix = [p for i, p in enumerate(pix) if i % 2 == 0]
        return pix
    SLEEP_STEPS = 16                         # 2 ticks each; the body breathes out, then in
    for i in range(SLEEP_STEPS):
        body = out['curl_2'] if i < SLEEP_STEPS // 2 else out['curl_1']
        pix = []
        for start in range(0, SLEEP_STEPS, 8):
            age = (i - start) % SLEEP_STEPS
            if age < len(Z_LIFE):
                pix += z_pixels(age)
        out[f'sleep_{i}'] = edit(body, [(x, y, 'z') for x, y in pix])
    # waking up: the head lifts out of the tail, then the body half unrolls
    out['uncurl_a'] = moved(pose(P.CURL), 21, 29, 0, 26 + POSE_DY, 1, -2, keep=True)
    half = grid(out['curl_0']); squeezed = [['.'] * W for _ in range(H)]
    cx = OX + 16
    for x in range(W):
        sx = round(cx + (x - cx) / 0.8)
        if 0 <= sx < W:
            for y in range(H):
                squeezed[y][x] = half[y][sx]
    out['uncurl_b'] = rows_of(squeezed)

    # --- stretch: into the play bow and back
    fwd = {n: to_ground(n, -0.15, 0) for n in LEG_ORDER}
    fwd['near_front'] = (3, fwd['near_front'][1]); fwd['far_front'] = (3, fwd['far_front'][1])
    out['stretch_0'] = posed(-0.15, 0, fwd, tail_up=1)
    for name, k, reach in [('stretch_a', -0.07, 1), ('stretch_b', -0.22, 4)]:
        legs = {n: to_ground(n, k, 0) for n in LEG_ORDER}
        legs['near_front'] = (reach, legs['near_front'][1]); legs['far_front'] = (reach, legs['far_front'][1])
        out[name] = posed(k, 0, legs, tail_up=1)
    fwd2 = {n: to_ground(n, -0.3, 0) for n in LEG_ORDER}
    fwd2['near_front'] = (5, fwd2['near_front'][1]); fwd2['far_front'] = (5, fwd2['far_front'][1])
    out['stretch_1'] = posed(-0.3, 0, fwd2, tail_up=1)
    out['stretch_2'] = pose(P.BOW)
    out['stretch_3'] = moved(pose(P.BOW), 24, 39, 0, 26 + POSE_DY, 0, 1)   # head dips while holding
    # yawning in the bow: the eyes shut and the lower jaw swings open around the corner of the
    # mouth, showing the dark mouth and the tongue
    shut = [(32, 35, 'd'), (33, 35, 'd')]
    out['yawn_0'] = edit(out['stretch_2'], shut + [(x, 37, 'k') for x in range(32, 36)] +
                         [(31, 38, 'w'), (32, 38, 'w'), (33, 38, 'w'), (34, 38, 'x')])
    out['yawn_1'] = edit(out['stretch_2'], shut + [(x, 37, 'k') for x in range(32, 36)] +
                         [(31, 38, 'w'), (32, 38, 't'), (33, 38, 't'), (34, 38, 'w'), (35, 38, 'x')])
    # widest: two rows of open mouth, the upper jaw untouched and the opening behind the nose
    out['yawn_2'] = edit(out['stretch_2'], shut + [(x, 37, 'k') for x in range(32, 37)] +
                         [(31, 38, 'w'), (32, 38, 'k'), (33, 38, 't'), (34, 38, 't'), (35, 38, 'k')] +
                         [(32, 39, 'w'), (33, 39, 'w'), (34, 39, 'w'), (35, 39, 'x')])

    # --- dig: play-bow body with the front raised a little so the front legs can bend.
    # Each front paw reaches forward, pulls back under the chest, flicks back (throwing dirt)
    # and lifts forward again; the two paws are half a cycle apart.
    no_front = [s for s in P.BOW if not (s[0] >= 27 and s[1] >= 27)]
    body = grid(pose(no_front))
    raised = [['.'] * W for _ in range(H)]
    for x in range(W):
        up = 0 if x < 17 else 1 if x < 20 else 2
        for y in range(H):
            if body[y][x] != '.' and y - up >= 0:
                raised[y - up][x] = body[y][x]
    # raising the columns in steps leaves 1px notches in the back line: fill them from below
    for y in range(H - 1):
        for x in range(1, W - 1):
            if (raised[y][x] == '.' and raised[y][x - 1] != '.' and raised[y][x + 1] != '.'
                    and raised[y + 1][x] != '.'):
                raised[y][x] = raised[y + 1][x]
    # the head drops toward the hole the paws are digging
    hx_, hy_ = 25, 17 + POSE_DY - 2         # head block corner after the raise
    bent = lambda deg, drop: rotsprite_head([r[:] for r in raised], deg, drop, (hx_ + 3, hy_ + 8), at=(hx_, hy_))
    half_bent = bent(DIG_HEAD[0] // 2, 0)     # in-between for lowering / raising the head
    raised = bent(*DIG_HEAD)
    chest_y = max(y for y in range(H) if raised[y][27] != '.')
    near_sh, far_sh = (27, chest_y + 1), (25, chest_y + 1)
    DIG_LEG = {  # (elbow, paw) offsets from the shoulder; 'G' = on the ground
        'lift': ((2, 1), (3, 3)),      # paw raised forward, wrist hanging down
        'reach': ((2, 2), (4, 'G')),   # strikes the ground ahead
        'scrape': ((0, 2), (0, 'G')),  # pulled back under the chest
        'kick': ((-1, 2), (-3, 1)),    # flicked back, throwing dirt
    }
    def dig_leg(g, sh, name, top, col):
        (ex, ey), (px_, py_) = DIG_LEG[name]
        sx, sy = sh
        py_ = GROUND if py_ == 'G' else sy + py_
        colors = lambda i, j: top if (i == 0 and j == 0) else col
        n = seg(g, sx, sy, sx + ex, sy + ey, 2, colors)
        seg(g, sx + ex, sy + ey, sx + px_, py_, 2, colors, n)
        paint_paw(g, sx + px_, py_, 2, col, toe=(py_ >= GROUND))
    near_cycle = ['lift', 'reach', 'scrape', 'kick']
    far_cycle = ['scrape', 'kick', 'lift', 'reach']
    clump = lambda x, y: [(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]   # 2x2 clod of dirt
    dirt = [  # clods in flight each frame, thrown back under the belly and past the hind legs
        clump(15, GROUND - 6) + [(8, GROUND - 1)],
        clump(19, GROUND - 3) + clump(11, GROUND - 5),
        clump(15, GROUND - 6) + [(6, GROUND)],
        clump(19, GROUND - 3) + clump(9, GROUND - 3),
    ]
    for i in range(4):
        g = [r[:] for r in raised]
        dig_leg(g, far_sh, far_cycle[i], 'd', 'l')
        dig_leg(g, near_sh, near_cycle[i], 'c', 'k')
        mound = [(29, GROUND), (30, GROUND), (31, GROUND), (32, GROUND), (30, GROUND - 1), (31, GROUND - 1)]
        for x, y in dirt[i] + mound:   # dirt in flight + a small mound at the hole
            if g[y][x] == '.':
                g[y][x] = 'y'
        out[f'dig_{i}'] = rows_of(g)
        if i == 0:   # first dig frame with the head only half lowered
            g = [r[:] for r in half_bent]
            dig_leg(g, far_sh, far_cycle[0], 'd', 'l')
            dig_leg(g, near_sh, near_cycle[0], 'c', 'k')
            for x, y in mound:
                if g[y][x] == '.':
                    g[y][x] = 'y'
            out['dig_h'] = rows_of(g)

    # --- listen: head rises, ears perk up, then the head tilts
    up = moved(stand, HX, 39, 0, HY + 8, 0, -1, keep=True)
    up = edit(up, [(HX + 4, HY - 2, 'd'), (HX + 7, HY - 2, 'k')])        # ears one pixel taller
    tilt = moved(up, HX + 9, 39, 0, HY + 7, 0, 1, keep=True)             # snout side drops: head tilts
    near_tip, far_tip = (HX + 7, HY - 2), (HX + 4, HY - 2)
    def flick(rows, tip, to):
        return edit(rows, [(tip[0], tip[1], '.'), (to, tip[1], 'k' if tip == near_tip else 'd')])
    out['listen_0'] = up
    out['listen_2'] = flick(up, near_tip, HX + 6)      # near ear swivels back
    out['listen_3'] = flick(up, far_tip, HX + 3)       # far ear swivels back
    out['listen_1'] = tilt
    out['listen_4'] = flick(tilt, near_tip, HX + 6)


    # --- lick: tongue comes out and flicks up to the nose
    nose_x, nose_y = HX + 12, HY + 7
    out['lick_0'] = edit(stand, [(nose_x - 1, nose_y + 1, 't')])
    out['lick_1'] = edit(stand, [(nose_x - 1, nose_y + 1, 't'), (nose_x, nose_y + 1, 't'), (nose_x, nose_y + 2, 't')])
    out['lick_2'] = edit(stand, [(nose_x, nose_y + 1, 't'), (nose_x + 1, nose_y, 't')])

    # --- itch: the lifted hind paw scratches up and down
    out['itch_0'] = pose(P.itch(0))
    out['itch_1'] = pose(P.itch(1))
    return out



IDLE_PHASES = [(0, 0), (0, 1), (1, 1), (1, 0)]   # (breath, tail_up) for idle_0..3


def look_frames():
    """Idle frames with the head turned toward each look direction."""
    out = {}
    for name, look in LOOK.items():
        if look is None:
            continue
        for i, (b, t) in enumerate(IDLE_PHASES):
            out[f'idle_{i}_{name}'] = frame(b, t, look=look)
    return out


if __name__ == '__main__':
    print(json.dumps(frames(), indent=1))