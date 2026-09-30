"""Renders a showcase video that plays every animation of one animal once, with a label badge.

Needs Pillow, numpy and ffmpeg. Frames are drawn from sprites/<animal>.json exactly as the app
would draw them (white 1px outline, integer scale) and piped to ffmpeg; one tick = one video
frame. Each animal has its own stage: the fox runs across a field at sunset, the arctic fox
across snow in Hokkaido at dusk, the penguin on Antarctic sea ice under the midnight sun, the
corgi plays on a park lawn on a sunny day, and the hamster potters about its enclosure in the
evening, on deep wood-shaving bedding.

Usage: python3 tools/render_video.py [fox|arctic-fox|penguin|corgi|dachshund|shiba|shiba-black|hamster] [stage] [out.mp4]
       stages: fox (the fox's default), hokkaido (the arctic fox's), antarctica (the penguin's),
               park (the corgi's), forest (the dachshund's), sakura (both shibas'), hamster (the enclosure), beach (a sandy beach by the sea)
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(__file__), '..')
_args = sys.argv[1:]
ANIMAL = _args.pop(0) if _args and not _args[0].endswith('.mp4') else 'fox'
DEFAULT_STAGE = {'arctic-fox': 'hokkaido', 'penguin': 'antarctica', 'corgi': 'park', 'dachshund': 'forest', 'shiba': 'sakura', 'shiba-black': 'sakura'}.get(ANIMAL, ANIMAL)
STAGE = _args.pop(0) if _args and not _args[0].endswith('.mp4') else DEFAULT_STAGE     # e.g. "hamster beach"
OUT = _args[0] if _args else os.path.join(ROOT, 'dist', f'{ANIMAL}-all-animations' + ('' if STAGE == DEFAULT_STAGE else f'-{STAGE}') + '.mp4')

VIDEO_W, VIDEO_H = 1280, 720
SCALE = 8                      # sprite pixel -> video pixels
GROUND_Y = 600                 # where the paws touch, in video pixels
# Sunset stage. The sky is a smooth gradient; the sun, its reflection and the ground detail are
# drawn on the sprite's 8px grid so they read as pixel art next to the fox.
HORIZON_Y = 560                # the far edge of the ground, behind the fox's legs
SKY = [(0, (22, 24, 56)), (230, (52, 46, 98)), (420, (132, 78, 126)), (520, (228, 128, 110)),
       (HORIZON_Y, (255, 176, 112))]                       # (video y, colour)
GROUND = [(HORIZON_Y, (178, 92, 82)), (600, (132, 66, 76)), (720, (58, 30, 50))]
SUN = ((944, HORIZON_Y + 16), 76, (255, 238, 170), (255, 150, 84))   # centre, radius, top, bottom colour
SUN_GLOW = ((255, 190, 120), 0.55, (620, 260))          # colour, strength, radii
# Parallax while the fox walks or runs: each layer scrolls against its direction at a share of
# the fox's speed. The sky and the sun stay put, stars barely move, the horizon drifts, and the
# ground moves faster the nearer it is (as fast as the fox where its paws touch).
STAR_SPEED = 0.02
HORIZON_SPEED = 0.2
def ground_speed(y):
    if y <= GROUND_Y:
        return HORIZON_SPEED + (1 - HORIZON_SPEED) * (y - HORIZON_Y) / (GROUND_Y - HORIZON_Y)
    return 1 + 0.8 * (y - GROUND_Y) / (720 - GROUND_Y)
STARS = 70                     # early-evening stars, thinning out toward the glowing horizon
FONT = ('/System/Library/Fonts/AppleSDGothicNeo.ttc', 4)   # SemiBold
FADE = 4                       # frames for the badge to fade in / out
GAP = 20                       # 1 second pause between animations (no badge)
BADGE_GAP = 40                 # video pixels between the fox's highest point and the badge

# (animation, badge text, how long to show it). Loops run for the given ticks; one-shots
# play once and rest on their last frame for the given ticks. Ordered so each animation
# starts in the pose the previous one ends in.
SEGMENTS = [
    ('idle', 'IDLE · 숨쉬기와 눈 깜빡임', 60),
    ('look', 'LOOK · 마우스 따라보기', 0),   # a scripted cursor goes left, then back right
    ('walk', 'WALK · 걷기', 48),
    ('run', 'RUN · 달리기', 48),
    ('run_stop', 'RUN STOP · 멈추기', 6),
    ('turn', 'TURN · 돌아서기', 10),
    ('turn', 'TURN · 돌아서기', 10),
    ('sit', 'SIT · 앉기', 20),
    ('sit_up', 'SIT UP · 일어서기', 6),
    ('lie_down', 'LIE DOWN · 엎드리기', 20),
    ('curl_sleep', 'CURL SLEEP · 웅크려 자기', 64),
    ('uncurl', 'UNCURL · 몸 풀기', 4),
    ('lie_up', 'LIE UP · 엎드렸다 일어서기', 6),
    ('stretch', 'STRETCH · 기지개', 6),
    ('pounce', 'POUNCE · 사냥 점프', 8),
    ('listen', 'LISTEN · 귀 기울이기', 6),
    ('dig', 'DIG · 땅 파기', 48),
    ('dig_end', 'DIG END · 파기 마치기', 6),
    ('lick', 'LICK · 코 핥기', 40),
    ('itch', 'ITCH · 목 긁기', 40),
    ('sit_up', 'SIT UP · 일어서기', 6),
    ('idle', 'IDLE · 숨쉬기', 30),
]


def make_background():
    import numpy as np
    P = SCALE
    ys = np.arange(VIDEO_H)
    yy, xx = np.mgrid[0:VIDEO_H, 0:VIDEO_W]
    def ramp(stops):
        return np.stack([np.interp(ys, [y for y, _ in stops], [c[k] for _, c in stops]) for k in range(3)], -1)
    sky, ground = ramp(SKY), ramp(GROUND)
    img = np.where((yy < HORIZON_Y)[..., None], sky[:, None, :], ground[:, None, :]).astype(float)
    (sx, sy), r, top, bottom = SUN
    # glow around the sun, much weaker on the ground
    col, k, (rx, ry) = SUN_GLOW
    a = k * np.exp(-(((xx - sx) / rx) ** 2 + ((yy - sy) / ry) ** 2) * 2.2)
    a = a * np.where(yy < HORIZON_Y, 1.0, 0.35)
    img = img * (1 - a[..., None]) + np.array(col) * a[..., None]
    # pixel helpers on the 8px grid
    cells_x, cells_y = xx // P, yy // P
    cx, cy = (xx // P) * P + P / 2, (yy // P) * P + P / 2
    def paint(mask, colour, alpha=1.0):
        nonlocal img
        m = mask[..., None] * alpha
        img = img * (1 - m) + np.array(colour, float) * m
    # the sun: a pixel disc, cut by the horizon, shaded top to bottom with two dark bands near
    # its lower edge like heat shimmer
    disc = (((cx - sx) ** 2 + (cy - sy) ** 2) <= r * r) & (yy < HORIZON_Y)
    t = np.clip((cy - (sy - r)) / r, 0, 1)[..., None]
    sun = np.array(top, float) * (1 - t) + np.array(bottom, float) * t
    img = np.where(disc[..., None], sun, img)
    for band in (HORIZON_Y - 4 * P, HORIZON_Y - 2 * P):
        paint(disc & (yy >= band) & (yy < band + P), SKY[-1][1], 0.85)
    # the ground under the sun catches its light (a soft warm patch, not a mirror-like reflection)
    lit = 0.30 * np.exp(-(((xx - sx) / 420) ** 2 + ((yy - HORIZON_Y) / 70) ** 2))
    img = img * (1 - (lit * (yy >= HORIZON_Y))[..., None]) + np.array((236, 140, 100.)) * (lit * (yy >= HORIZON_Y))[..., None]
    # ground: a lit rim at the horizon, then furrows that spread out toward the viewer
    paint((yy >= HORIZON_Y) & (yy < HORIZON_Y + P), (236, 138, 102), 0.55)
    for dy in (3, 6, 10, 15):
        y0 = HORIZON_Y + dy * P
        paint((yy >= y0) & (yy < y0 + P // 2 * (1 + (dy > 6))), (40, 18, 36), 0.18)
    img += np.random.default_rng(7).uniform(-1.2, 1.2, img.shape)   # dither so the gradient never bands
    return Image.fromarray(np.clip(img, 0, 255).astype('uint8')).convert('RGBA')


def make_stars():
    import math, random
    rnd = random.Random(11)
    P = SCALE
    stars = []
    while len(stars) < STARS:
        x, y = rnd.randrange(1, VIDEO_W // P - 1), rnd.randrange(1, 44)
        if rnd.random() > (1 - y / 44) ** 1.5:        # fewer stars the lower (brighter) the sky
            continue
        if any(abs(x - sx) < 3 and abs(y - sy) < 3 for sx, sy, *_ in stars):
            continue
        bright = rnd.random() < 0.12
        stars.append((x, y, bright, rnd.uniform(0.35, 0.8) * (1 - y / 60),
                      rnd.uniform(0, 2 * math.pi), rnd.uniform(1.2, 3.2)))
    return stars


def draw_stars(canvas, stars, t, travelled=0.0):
    """Stars twinkle at their own pace; bright ones flash a small cross at their peak."""
    import math
    P = SCALE
    layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    shift = round(travelled * STAR_SPEED)                 # in sprite px (= grid cells)
    cols = VIDEO_W // P
    for x, y, bright, base, phase, period in stars:
        x = (x - shift) % cols
        s = 0.5 + 0.5 * math.sin(2 * math.pi * t / period + phase)
        a = base * (0.35 + 0.65 * s ** 2)
        colour = (255, 244, 226)
        d.rectangle([x * P, y * P, x * P + P - 1, y * P + P - 1], fill=colour + (int(255 * a),))
        if bright and s > 0.55:
            arm = int(255 * a * (s - 0.55) / 0.45 * 0.7)
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                X, Y = (x + dx) * P, (y + dy) * P
                d.rectangle([X, Y, X + P - 1, Y + P - 1], fill=colour + (arm,))
    canvas.alpha_composite(layer)


def make_props():
    """Things on the ground that scroll: (x cell, cells [(dx, dy)], y of the base, colour, alpha).
    The period is wider than the screen so the pattern does not visibly repeat."""
    import random
    rnd = random.Random(5)
    P = SCALE
    period = VIDEO_W // P * 2
    props = []
    base = HORIZON_Y // P - 1                            # tufts standing on the horizon
    for x in rnd.sample(range(period), 44):
        h = rnd.randint(1, 2)
        cells = [(0, -i) for i in range(h)] + ([(rnd.choice([-1, 1]), 0)] if rnd.random() < 0.6 else [])
        props.append((x, cells, base, (96, 48, 70), 0.9))
    # pebbles catch the sunset on top and cast a dark cell below; larger nearer the viewer
    for _ in range(60):
        y = rnd.randrange(HORIZON_Y // P + 1, VIDEO_H // P - 1)
        near = (y * P - HORIZON_Y) / (VIDEO_H - HORIZON_Y)
        x = rnd.randrange(period)
        wide = [(0, 0), (1, 0)] if near > 0.4 else [(0, 0)]
        props.append((x, wide, y, (222, 140, 110), 0.45 + 0.4 * near))
        props.append((x, [(dx, 1) for dx, _ in wide], y, (44, 20, 36), 0.35 + 0.3 * near))
    for _ in range(26):                                  # grass on the ground, taller nearer
        y = rnd.randrange(HORIZON_Y // P + 2, VIDEO_H // P)
        near = (y * P - HORIZON_Y) / (VIDEO_H - HORIZON_Y)
        h = 1 + int(near * 2.5)
        cells = [(0, -i) for i in range(h)] + [(-1, -(h // 2)), (1, -max(0, h - 2))][:1 + int(near > 0.5)]
        props.append((rnd.randrange(period), cells, y, (176, 92, 88), 0.5 + 0.4 * near))   # rim-lit grass
    return period, props


def draw_props(canvas, props, travelled):
    P = SCALE
    period, items = props
    layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x, cells, y, colour, alpha in items:
        speed = HORIZON_SPEED if y * P < HORIZON_Y else ground_speed(y * P + P / 2)
        sx = (x - round(travelled * speed)) % period - 4   # snapped to the 8px grid
        if sx < -4 or sx > VIDEO_W // P + 4:
            continue
        for dx, dy in cells:
            X, Y = (sx + dx) * P, (y + dy) * P
            d.rectangle([X, Y, X + P - 1, Y + P - 1], fill=colour + (int(255 * alpha),))
    canvas.alpha_composite(layer)


def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def load():
    with open(os.path.join(ROOT, 'sprites', f'{ANIMAL}.json')) as f:
        return json.load(f)


class Frames:
    """Sprite frames at 1px scale with the 4-direction white outline, cached per variant."""

    def __init__(self, s):
        self.s, self.cache = s, {}

    def get(self, name, flip=False, blink=False):
        key = (name, flip, blink)
        if key in self.cache:
            return self.cache[key]
        s = self.s
        w, h = s['size']
        b = s['blink']
        swap = (b.get('swap') or {b['eye']: b['closed']}) if blink else {}
        img = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0))
        px = img.load()
        rows = s['frames'][name]
        skip = set(s.get('outline', {}).get('skip', []))      # colours drawn without the outline
        for y, r in enumerate(rows):
            for x, ch in enumerate(r):
                if ch != '.' and ch not in skip:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        px[x + 1 + dx, y + 1 + dy] = (255, 255, 255, 255)
        for y, r in enumerate(rows):
            for x, ch in enumerate(r):
                ch = swap.get(ch, ch)
                if ch != '.':
                    px[x + 1, y + 1] = hexrgb(s['palette'][ch]['hex']) + (255,)
        if flip:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        img = img.resize((img.width * SCALE, img.height * SCALE), Image.NEAREST)
        self.cache[key] = img
        return img


def play_once(anim):
    """Ticks of one pass through an animation: list of (frame, step index)."""
    out = []
    for i, step in enumerate(anim['seq']):
        out += [(step[0], i)] * step[1]
    return out


def timeline(s):
    """Per-tick list of (frame, flip, blink, segment index or None during a pause, cursor, move).
    move is how far the fox travels that tick in sprite pixels (+ right), as the viewer moves it:
    moveX every tick plus a step's dx when the step starts."""
    anims, ticks, facing = s['animations'], [], 1
    blink_at = {25, 26, 48, 49, 52, 53}          # a single and a double blink in the first idle
    idle = play_once(anims['idle'])
    for seg_i, (name, label, extra) in enumerate(SEGMENTS):
        if name == 'look':
            facing = look_segment(s, ticks, seg_i, facing)
            end_pose, last = 'stand', None
        else:
            a = anims[name]
            once = play_once(a)
            if a['loop']:
                intro = sum(st[1] for st in a['seq'][:a.get('loopFrom', 0)])
                body = once[intro:] or once
                seq = once[:intro] + [body[i % len(body)] for i in range(extra)]
            else:
                seq = once + [once[-1]] * extra
            for n, (f, step) in enumerate(seq):
                starts = n == 0 or seq[n - 1][1] != step
                if a.get('flipAt') is not None and step == a['flipAt'] and starts:
                    facing *= -1
                move = (a.get('moveX') or 0) + ((a['seq'][step][2] if len(a['seq'][step]) > 2 else 0) or 0 if starts else 0)
                ticks.append((f, facing < 0, seg_i == 0 and n in blink_at, seg_i, None, move * facing))
            end_pose, last = a.get('pose', ['stand', 'stand'])[1], seq[-1][0]
        if seg_i == len(SEGMENTS) - 1 or end_pose in ('running', 'sliding'):   # flows straight into stopping
            continue
        # the pause: breathe when standing, keep breathing when asleep, otherwise hold the pose
        if end_pose == 'stand':
            pause = [idle[t % len(idle)][0] for t in range(GAP)]
        elif end_pose in LOOP_POSES:                      # asleep, hidden: keep the loop going
            a = anims[LOOP_POSES[end_pose]]
            body = play_once(a)[sum(st[1] for st in a['seq'][:a.get('loopFrom', 0)]):]
            pause = [body[t % len(body)][0] for t in range(GAP)]
        else:
            pause = [last] * GAP
        ticks += [(f, facing < 0, False, None, None, 0) for f in pause]
    return ticks


# Cursor path for the LOOK segment: (tick, x, y) in video pixels. It starts in front of the fox,
# rises over its head to behind it (the fox turns around), dips low on the left, then sweeps
# back to the right (the fox turns again).
CURSOR_PATH = [(0, 960, 400), (24, 900, 160), (44, 670, 110), (68, 360, 210), (88, 300, 520),
               (104, 520, 650), (128, 930, 620), (148, 960, 400), (168, 960, 400)]


def cursor_at(t):
    for (t0, x0, y0), (t1, x1, y1) in zip(CURSOR_PATH, CURSOR_PATH[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / max(1, t1 - t0)
            u = u * u * (3 - 2 * u)                     # ease in and out
            return (x0 + (x1 - x0) * u, y0 + (y1 - y0) * u)
    return CURSOR_PATH[-1][1:]


def look_segment(s, ticks, seg_i, facing):
    """Idle with cursor tracking, using the same rules as the viewer and the app."""
    anims, lk = s['animations'], s['look']
    ax, ay = s['anchor']
    idle = play_once(anims['idle'])
    turn = play_once(anims['turn'])
    flip_at = anims['turn']['flipAt']
    sprite_top = GROUND_Y - (ay + 1) * SCALE
    look_dir, turning = 'fwd', None
    for t in range(CURSOR_PATH[-1][0] + 1):
        cx, cy = cursor_at(t)
        if turning is not None:
            f, step = turn[turning]
            if step == flip_at and (turning == 0 or turn[turning - 1][1] != step):
                facing *= -1
            turning = turning + 1 if turning + 1 < len(turn) else None
            ticks.append((f, facing < 0, False, seg_i, (cx, cy), 0))
            continue
        body_x = VIDEO_W / 2
        if (facing > 0 and cx < body_x - lk['turnMargin'] * SCALE) or (facing < 0 and cx > body_x + lk['turnMargin'] * SCALE):
            turning = 0
            f, _ = turn[0]
            ticks.append((f, facing < 0, False, seg_i, (cx, cy), 0))
            turning = 1
            continue
        hx = VIDEO_W / 2 + (lk['headCenter'][0] - ax) * SCALE * facing
        hy = sprite_top + (lk['headCenter'][1] + 1) * SCALE
        fwd, up = (cx - hx) / SCALE * facing, (hy - cy) / SCALE
        if (fwd * fwd + up * up) ** 0.5 >= lk['deadZone']:
            import math
            deg = max(-90, min(90, math.degrees(math.atan2(up, fwd))))
            look_dir = next((sec['dir'] for sec in lk['sectors'] if deg >= sec['min']), lk['sectors'][-1]['dir'])
        f, _ = idle[t % len(idle)]
        ticks.append((lk['frames'].get(look_dir, {}).get(f, f), facing < 0, False, seg_i, (cx, cy), 0))
    return facing


# The LOOK cursor is something the animal would watch: a sunflower seed that bobs 1px for the
# hamster, a butterfly that flaps for the fox, for the arctic fox in the snow a shima-enaga
# (Hokkaido's white long-tailed tit) that flaps and faces the way it flies, and a fish for the
# penguin, and a tennis ball for the corgi. Pixel art with the
# sprites' white 1px outline, CURSOR_PX video pixels per pixel, centred on the cursor point.
CURSOR_PX = 4
CURSOR_COLOURS = {
    'O': (255, 255, 255, 255),                           # outline
    'K': (24, 22, 26, 255), 'G': (150, 148, 144, 255),   # seed shell and its stripes
    'Y': (255, 170, 60, 255), 'y': (214, 110, 40, 255), 'B': (40, 30, 34, 255),   # butterfly
    'E': (246, 244, 240, 255), 'N': (92, 88, 96, 255), 'P': (214, 170, 164, 255),  # shima-enaga (and K)
    'U': (79, 106, 134, 255), 'u': (196, 210, 222, 255),                             # fish (and K for its eye)
    'T': (200, 220, 60, 255), 'W': (245, 247, 232, 255),                             # tennis ball
    'R': (220, 62, 42, 255), 'r': (160, 40, 30, 255),                                # red dragonfly (and K)
    'V': (196, 216, 232, 255), 'v': (150, 172, 196, 255),                            # its wings
}
SEED = """
...OOOO...
..OKKKKO..
.OKGKKGKO.
OKKGKKGKKO
OKKGKKGKKO
OKKGKKGKKO
OKKGKKGKKO
OKKGKKGKKO
OKKGKKGKKO
.OKGKKGKO.
.OKGKKGKO.
.OKGKKGKO.
.OKGKKGKO.
..OKKKKO..
..OKKKKO..
...OKKO...
....OO....
"""
BUTTERFLY = ["""
.OOO.....OOO.
OyYYO...OYYyO
OYYYYO.OYYYYO
OYYYYOBOYYYYO
.OYYYOBOYYYO.
..OOYOBOYOO..
..OYYOBOYYO..
..OyYOBOYyO..
...OOO.OOO...
""", """
.............
....OO.OO....
...OYYOYYO...
...OYYBYYO...
...OYOBOYO...
...OYOBOYO...
...OyOBOyO...
....OO.OO....
.............
"""]


ENAGA = ["""
......OOOO....
..OO.OEEEEO...
.ONNOEEEEEEO..
..ONNEEEEKEKO.
OOOOEEEEEEEO..
OKKKEPEEEEEO..
.OOOKEEEEEO...
.....OOOOO....
""", """
......OOOO....
.....OEEEEO...
....OEEEEEEO..
...OEEEEEKEKO.
OOOOEEEEEEEO..
OKKKENNEEEEO..
.OOOKONNEEO...
.....OOOOO....
"""]


# the penguin's fish (as in its eat animation); the tail fork beats between the two frames
FISH = ["""
.....OO...
.O..OUUOO.
OUOOUUUKUO
.OUUuuuuuO
OUOOOuuOO.
.O...OO...
""", """
.....OO...
..O.OUUOO.
.OUOUUUKUO
.OUUuuuuuO
.OUOOuuOO.
..O..OO...
"""]


# the corgi's tennis ball (as in its fetch animation), its seam turning
TENNIS = ["""
.OOO.
OWTTO
OTWTO
OTTWO
.OOO.
""", """
.OOO.
OTTWO
OTWTO
OWTTO
.OOO.
"""]


def outlined(art):
    """Pads the art by one pixel and draws the white 1px outline (4 directions) around it."""
    rows = art.strip('\n').split('\n')
    w = max(map(len, rows)) + 2
    grid = ['.' * w] + ['.' + r.ljust(w - 2, '.') + '.' for r in rows] + ['.' * w]
    fill = lambda x, y: 0 <= y < len(grid) and 0 <= x < w and grid[y][x] != '.'
    return '\n'.join(''.join('O' if c == '.' and any(fill(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                              else c for x, c in enumerate(r)) for y, r in enumerate(grid))


# the dachshund's red dragonfly (an autumn akatombo) seen from above, head to the right: a long red
# tail, big dark eyes, and two pairs of pale wings that beat
_DRAGONFLY_WINGS_OUT = """
..........vv.vv...
..........VV.VV...
..........VV.VV...
..........VV.VV...
"""
_DRAGONFLY_WINGS_BEAT = """
..................
..................
..........vv.vv...
..........VV.VV...
"""
_DRAGONFLY_BODY = """
...........rRRrKK.
rRRrRRrRRRRRRRRRRR
...........rRRrKK.
"""
DRAGONFLY = [outlined(w.strip('\n') + '\n' + _DRAGONFLY_BODY.strip('\n') + '\n' + '\n'.join(w.strip('\n').split('\n')[::-1]))
             for w in (_DRAGONFLY_WINGS_OUT, _DRAGONFLY_WINGS_BEAT)]


def pixel_art(art):
    rows = art.strip('\n').split('\n')
    img = Image.new('RGBA', (max(map(len, rows)) * CURSOR_PX, len(rows) * CURSOR_PX), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            if c in CURSOR_COLOURS:
                d.rectangle((x * CURSOR_PX, y * CURSOR_PX, (x + 1) * CURSOR_PX - 1, (y + 1) * CURSOR_PX - 1),
                            fill=CURSOR_COLOURS[c])
    return img


def draw_cursor(canvas, x, y, t):
    """The LOOK cursor centred on (x, y) at LOOK tick t."""
    if ANIMAL == 'hamster':
        img, y = pixel_art(SEED), y + (CURSOR_PX if (t // 6) % 2 else 0)
    elif ANIMAL == 'corgi':                      # a tennis ball, bouncing gently
        img, y = pixel_art(TENNIS[(t // 4) % 2]), y - (CURSOR_PX if (t // 6) % 2 else 0)
    elif ANIMAL in ('arctic-fox', 'penguin', 'dachshund'):
        if ANIMAL == 'dachshund':               # a red dragonfly darting about
            img, y = pixel_art(DRAGONFLY[t % 2]), y + (CURSOR_PX if (t // 5) % 2 else 0)
        elif ANIMAL == 'arctic-fox':
            img, y = pixel_art(ENAGA[(t // 2) % 2]), y + (CURSOR_PX if (t // 6) % 2 else 0)
        else:                                    # a fish swimming through the air, its tail beating
            img, y = pixel_art(FISH[(t // 3) % 2]), y + (CURSOR_PX if (t // 8) % 2 else 0)
        # face the way it moves (it faces right as drawn); hold the last way while it hovers
        dx = next((cursor_at(u)[0] - cursor_at(u - 1)[0] for u in range(t, 0, -1)
                   if cursor_at(u)[0] != cursor_at(u - 1)[0]), 1)
        if dx < 0:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
    else:
        img = pixel_art(BUTTERFLY[(t // 3) % 2])
    canvas.alpha_composite(img, (int(x - img.width / 2), int(y - img.height / 2)))


def top_row(rows):
    return next(y for y, r in enumerate(rows) if r.strip('.'))


def badge(layer, text, alpha, font, cx, bottom):
    d = ImageDraw.Draw(layer)
    tw = d.textlength(text, font=font)
    pad_x, h = 32, 64
    w = tw + pad_x * 2
    x0, y0 = cx - w / 2, max(12, bottom - h)
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=h / 2,
                        fill=(16, 20, 28, int(165 * alpha)), outline=(255, 255, 255, int(38 * alpha)), width=2)
    d.text((cx, y0 + h / 2), text, font=font, fill=(255, 255, 255, int(255 * alpha)), anchor='mm')


def fox_stage():
    background, stars, props = make_background(), make_stars(), make_props()
    def draw_moving(canvas, t, travelled):
        draw_stars(canvas, stars, t, travelled)
        draw_props(canvas, props, travelled)
    return background, draw_moving


# ---- hamster: an enclosure in the evening -----------------------------------------------------
# A room wall behind the glass, warmed by a desk lamp on the left. On the far edge of the bedding stand the hamster's things: a wooden hideout, a wheel, a
# food bowl with seeds, and a water bottle hanging from the lid. The floor is deep wood-shaving
# bedding: pale, with slanted strands, loose curls and a few sunflower seeds lying about.
HAMSTER = dict(
    SCALE=12, GROUND_Y=600, HORIZON_Y=528,
    WALL=[(0, (36, 30, 44)), (260, (62, 48, 58)), (528, (98, 74, 70))],
    FLOOR=[(528, (206, 186, 150)), (600, (220, 201, 164)), (720, (188, 164, 124))],
    LAMP=((170, 140), (255, 196, 128), 0.42, (560, 360)),      # centre, colour, strength, radii
    SEGMENTS=[
        ('idle', 'IDLE · 숨쉬기와 눈 깜빡임', 60),
        ('look', 'LOOK · 마우스 따라보기', 0),
        ('walk', 'WALK · 걷기', 48),
        ('run', 'RUN · 달리기', 48),
        ('run_stop', 'RUN STOP · 멈추기', 6),
        ('turn', 'TURN · 돌아서기', 10),
        ('turn', 'TURN · 돌아서기', 10),
        ('sniff', 'SNIFF · 킁킁', 8),
        ('rear_look', 'REAR LOOK · 일어서서 두리번', 6),
        ('sit', 'SIT · 앉기', 20),
        ('groom', 'GROOM · 세수', 6),
        ('eat_seed', 'EAT SEED · 해바라기씨 먹기', 6),
        ('sit_up', 'SIT UP · 일어서기', 6),
        ('stretch', 'STRETCH · 기지개', 6),
        ('wheel', 'WHEEL · 쳇바퀴 타기', 6),
        ('lie_down', 'LIE DOWN · 엎드리기', 20),
        ('curl_sleep', 'CURL SLEEP · 몸 말고 자기', 64),
        ('uncurl', 'UNCURL · 몸 풀기', 4),
        ('lie_up', 'LIE UP · 엎드렸다 일어서기', 6),
        ('dig', 'DIG · 톱밥 파기', 6),
        ('burrow_in', 'BURROW IN · 톱밥 속으로', 4),
        ('hide', 'HIDE · 숨어서 얼굴 내밀기', 150),
        ('emerge', 'EMERGE · 나오기', 6),
        ('idle', 'IDLE · 숨쉬기', 30),
    ],
)


def hamster_stage():
    import numpy as np, random
    P, H0 = SCALE, HORIZON_Y
    ys = np.arange(VIDEO_H)
    yy, xx = np.mgrid[0:VIDEO_H, 0:VIDEO_W]
    ramp = lambda stops: np.stack([np.interp(ys, [y for y, _ in stops], [c[k] for _, c in stops]) for k in range(3)], -1)
    img = np.where((yy < H0)[..., None], ramp(HAMSTER['WALL'])[:, None, :], ramp(HAMSTER['FLOOR'])[:, None, :]).astype(float)
    (lx, ly), col, k, (rx, ry) = HAMSTER['LAMP']
    a = k * np.exp(-(((xx - lx) / rx) ** 2 + ((yy - ly) / ry) ** 2) * 2.0)
    a = a * np.where(yy < H0, 1.0, 0.45)
    img = img * (1 - a[..., None]) + np.array(col) * a[..., None]
    def paint(mask, colour, alpha=1.0):
        nonlocal img
        m = mask[..., None] * alpha
        img = img * (1 - m) + np.array(colour, float) * m
    # where the bedding meets the back of the tank: a shaded seam and a lit lip of shavings
    paint((yy >= H0) & (yy < H0 + P), (150, 122, 92), 0.55)
    paint((yy >= H0 - P // 2) & (yy < H0), (40, 30, 34), 0.25)
    # bedding strands: short slanted strokes on the grid, sparser and smaller far away
    rnd = np.random.default_rng(3)
    # (sparse: packed tightly they read as sand)
    for _ in range(110):
        y = int(rnd.integers(H0 // P + 1, VIDEO_H // P))
        near = (y * P - H0) / (VIDEO_H - H0)
        x = int(rnd.integers(0, VIDEO_W // P))
        n = 2 + int(near * 1.5)
        shade = (176, 152, 114) if rnd.random() < 0.65 else (238, 226, 198)
        rise = rnd.random() < 0.5
        for i in range(n):
            X, Y = (x + i) * P, (y - (i // 2 if rise else 0)) * P
            paint((xx >= X) & (xx < X + P) & (yy >= Y) & (yy < Y + P), shade, 0.30 + 0.25 * near)
    img += np.random.default_rng(7).uniform(-1.2, 1.2, img.shape)
    background = Image.fromarray(np.clip(img, 0, 255).astype('uint8')).convert('RGBA')

    # far things on the back edge of the bedding, drawn once on a strip twice the screen wide
    cols, base = VIDEO_W // P * 2, H0 // P            # base: the row they stand on
    far = Image.new('RGBA', (cols * P, VIDEO_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(far)
    def cell(x, y, colour, alpha=255):
        d.rectangle([x * P, y * P, x * P + P - 1, y * P + P - 1], fill=colour + (alpha,))
    haze = lambda c, t=0.28: tuple(int(v * (1 - t) + w * t) for v, w in zip(c, (98, 74, 70)))
    def hideout(x0):                                   # a little wooden house with a round door
        wood, dark, roof, door = haze((150, 104, 66)), haze((112, 76, 48)), haze((120, 70, 52)), haze((46, 32, 30))
        for y in range(base - 7, base):
            for x in range(x0, x0 + 10):
                cell(x, y, wood if (y - base) % 2 else dark)
        for i in range(6):                             # roof
            for x in range(x0 - 1 + i, x0 + 11 - i):
                cell(x, base - 8 - i, roof)
        for y, xs in ((base - 1, range(x0 + 3, x0 + 7)), (base - 2, range(x0 + 3, x0 + 7)),
                      (base - 3, range(x0 + 3, x0 + 7)), (base - 4, range(x0 + 4, x0 + 6))):
            for x in xs:
                cell(x, y, door)
    def wheel(x0):                                     # a spare running wheel on its stand, like the sprite's
        import math
        rim, spoke, stand, disc = haze((85, 123, 149)), haze((122, 160, 182), 0.4), haze((104, 118, 130)), haze((195, 219, 230), 0.4)
        r, cxw, cyw = 6.5, x0 + 7, base - 9
        for x in range(x0, x0 + 15):
            for y in range(cyw - 8, cyw + 8):
                dd = math.hypot(x + 0.5 - cxw - 0.5, y + 0.5 - cyw - 0.5)
                if r - 1 <= dd < r:
                    cell(x, y, rim)
                elif dd < r - 1 and (x == cxw or y == cyw or x - cxw == y - cyw or x - cxw == cyw - y):
                    cell(x, y, spoke)
                elif dd < r - 1:
                    cell(x, y, disc, 200)
        for i in range(9):                             # the stand
            cell(cxw - i // 2 - 1, cyw + 1 + i, stand); cell(cxw + i // 2 + 1, cyw + 1 + i, stand)
    def bowl(x0):                                      # a ceramic bowl heaped with seeds
        clay, rim_c, seed, stripe = haze((214, 196, 172)), haze((236, 222, 200)), haze((58, 52, 48)), haze((150, 142, 132))
        for x in range(x0, x0 + 9):
            cell(x, base - 3, rim_c)
        for y, (a, b) in ((base - 2, (0, 9)), (base - 1, (1, 8))):
            for x in range(x0 + a, x0 + b):
                cell(x, y, clay)
        for x, c in zip(range(x0 + 1, x0 + 8), (seed, stripe, seed, seed, stripe, seed, seed)):
            cell(x, base - 4, c)
        for x, c in zip(range(x0 + 3, x0 + 6), (seed, stripe, seed)):
            cell(x, base - 5, c)
    def bottle(x0):                                    # a water bottle hanging from the lid
        glass, water, metal = haze((190, 214, 226), 0.2), haze((120, 170, 204), 0.2), haze((170, 176, 180))
        for y in range(0, 22):
            for x in range(x0, x0 + 3):
                cell(x, y, water if y > 7 else glass, 170)
        for y in range(22, 27):
            cell(x0 + 1, y, metal)
        cell(x0 + 2, 27, metal)
    # placed so the middle of the screen (the hamster and its badge) is open wall both at the
    # start and after walking and running, when the strip has scrolled about 20 cells
    for x in (12, 12 + cols // 2):
        hideout(x)
    for x in (30, 30 + cols // 2):
        bowl(x)
    for x in (92, 92 + cols // 2):
        wheel(x)
    for x in (104, 104 + cols // 2):
        bottle(x)

    # near things on the bedding that scroll by depth: loose curls of shaving and seeds
    rnd = random.Random(5)
    period = cols
    props = []
    for _ in range(70):
        y = rnd.randrange(H0 // P + 1, VIDEO_H // P - 1)
        near = (y * P - H0) / (VIDEO_H - H0)
        x = rnd.randrange(period)
        curl = [(0, 0), (1, 0), (1, -1)] if rnd.random() < 0.5 else [(0, 0), (1, -1)]
        props.append((x, curl, y, (240, 228, 200), 0.55 + 0.35 * near))
        props.append((x, [(1, 0)], y, (164, 138, 100), 0.4 + 0.3 * near))
    for _ in range(9):                                 # a few sunflower seeds dropped on the bedding
        y = rnd.randrange(H0 // P + 2, VIDEO_H // P - 1)
        x = rnd.randrange(period)
        props.append((x, [(0, 0), (1, 0)], y, (58, 52, 48), 0.95))       # a dark seed lying on its side
        props.append((x, [(1, -1)], y, (140, 132, 122), 0.95))            # with a light stripe on top
    props = (period, props)

    def draw_moving(canvas, t, travelled):
        shift = round(travelled * HORIZON_SPEED) * P % far.width
        canvas.alpha_composite(far, (-shift, 0))
        if shift > far.width - VIDEO_W:
            canvas.alpha_composite(far, (far.width - shift, 0))
        draw_props(canvas, props, travelled)
    return background, draw_moving


# ---- beach: a sandy shore on a bright day -----------------------------------------------------
# Sky with the sun high on the right, a blue sea that glitters where the sunlight hits it,
# waves running up the shore and drawing back over darker wet sand, and warm dry sand in front
# (not too pale, or the white outline and the white belly would melt into it).
BEACH = dict(
    SKY=[(0, (104, 178, 226)), (200, (150, 205, 236)), (300, (214, 238, 247))],
    HORIZON=300,                      # where the sea meets the sky
    SEA=[(300, (46, 110, 170)), (420, (48, 142, 186)), (500, (72, 180, 196))],
    SHORE=512,                        # the mean waterline; waves run a few cells up and down from it
    SAND=[(512, (196, 168, 120)), (600, (214, 186, 136)), (720, (198, 168, 118))],
    SUN=((1010, 104), 42, (255, 250, 228)),
)


def beach_stage():
    import numpy as np, math, random
    P, B = SCALE, BEACH
    ys = np.arange(VIDEO_H)
    yy, xx = np.mgrid[0:VIDEO_H, 0:VIDEO_W]
    ramp = lambda stops: np.stack([np.interp(ys, [y for y, _ in stops], [c[k] for _, c in stops]) for k in range(3)], -1)
    sky, sea, sand = ramp(B['SKY']), ramp(B['SEA']), ramp(B['SAND'])
    img = np.where((yy < B['HORIZON'])[..., None], sky[:, None, :],
                   np.where((yy < B['SHORE'])[..., None], sea[:, None, :], sand[:, None, :])).astype(float)
    (sx, sy), r, sun_c = B['SUN']
    glow = 0.5 * np.exp(-(((xx - sx) / 380) ** 2 + ((yy - sy) / 260) ** 2) * 2.0) * (yy < B['HORIZON'])
    img = img * (1 - glow[..., None]) + np.array((255, 246, 214.)) * glow[..., None]
    cx, cy = (xx // P) * P + P / 2, (yy // P) * P + P / 2
    disc = ((cx - sx) ** 2 + (cy - sy) ** 2) <= r * r
    img = np.where(disc[..., None], np.array(sun_c, float), img)
    # the sea is brighter along the sun's path, a soft band below the sun
    path = 0.22 * np.exp(-((xx - sx) / 150) ** 2) * ((yy >= B['HORIZON']) & (yy < B['SHORE']))
    img = img * (1 - path[..., None]) + np.array((200, 232, 240.)) * path[..., None]
    def paint(mask, colour, alpha=1.0):
        nonlocal img
        m = mask[..., None] * alpha
        img = img * (1 - m) + np.array(colour, float) * m
    paint((yy >= B['HORIZON']) & (yy < B['HORIZON'] + P // 2), (230, 244, 250), 0.35)   # a hazy horizon line
    # dry sand: fine grain and ripples, sparse so it reads as sand rather than noise
    rnd = np.random.default_rng(9)
    for _ in range(160):
        y = int(rnd.integers(B['SHORE'] // P + 3, VIDEO_H // P))
        near = (y * P - B['SHORE']) / (VIDEO_H - B['SHORE'])
        x = int(rnd.integers(0, VIDEO_W // P))
        n = 1 + int(near * 2.5) if rnd.random() < 0.5 else 1
        shade = (176, 146, 100) if rnd.random() < 0.6 else (232, 208, 160)
        for i in range(n):
            X, Y = (x + i) * P, y * P
            paint((xx >= X) & (xx < X + P) & (yy >= Y) & (yy < Y + P), shade, 0.35 + 0.3 * near)
    img += np.random.default_rng(7).uniform(-1.2, 1.2, img.shape)
    background = Image.fromarray(np.clip(img, 0, 255).astype('uint8')).convert('RGBA')

    rnd = random.Random(21)
    cols = VIDEO_W // P
    hor, shore = B['HORIZON'] // P, B['SHORE'] // P
    # glints: dense in the column under the sun, sparse over the rest of the sea; each twinkles
    # at its own quick pace and the brightest flash a small cross at their peak
    glints = []
    sun_col = sx // P
    while len(glints) < 220:
        y = rnd.randrange(hor + 2, shore - 1)                  # not on the horizon line itself
        depth = (y - hor) / max(1, shore - hor)
        if rnd.random() < 0.75:
            x = sun_col + round(rnd.gauss(0, 2 + 5.5 * depth))      # the sun's path widens toward the shore
        else:
            x = rnd.randrange(cols * 2)
        on_path = abs(x - sun_col) < 3 + 7 * depth
        bright = on_path and rnd.random() < 0.4
        glints.append((x, y, bright, on_path, rnd.uniform(0.6, 1.0) if on_path else rnd.uniform(0.3, 0.7),
                       rnd.uniform(0, 2 * math.pi), rnd.uniform(1.0, 2.6),   # slow: quick glints pull the eye off the hamster
                       2 if depth > 0.45 and rnd.random() < 0.5 else 1))
    clouds = []
    for cx0, cy0, w in ((10, 5, 9), (46, 8, 12), (78, 4, 8), (120, 7, 10), (160, 5, 9)):
        cells = [(i, 0) for i in range(w)] + [(i, -1) for i in range(2, w - 2)] + [(i, -2) for i in range(4, w - 4)]
        clouds.append((cx0, cy0, cells))
    # sand props that scroll by depth: small shells (pink and white) and pebbles
    period = cols * 2
    props = []
    for _ in range(26):
        y = rnd.randrange(shore + 4, VIDEO_H // P - 1)
        near = (y * P - B['SHORE']) / (VIDEO_H - B['SHORE'])
        x = rnd.randrange(period)
        kind = rnd.random()
        if kind < 0.4:
            props.append((x, [(0, 0), (1, 0), (0, -1)], y, (240, 200, 196), 0.9))      # a pink shell
            props.append((x, [(1, -1)], y, (255, 238, 232), 0.9))
        elif kind < 0.7:
            props.append((x, [(0, 0), (1, 0)], y, (248, 244, 232), 0.85))               # a white shell
            props.append((x, [(0, 1), (1, 1)], y, (170, 142, 100), 0.5))
        else:
            props.append((x, [(0, 0)] + ([(1, 0)] if near > 0.5 else []), y, (128, 120, 110), 0.85))   # a pebble
            props.append((x, [(0, 1)], y, (160, 132, 92), 0.5))
    props = (period, props)

    def draw_moving(canvas, t, travelled):
        layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        def cell(x, y, colour, a):
            d.rectangle([x * P, y * P, x * P + P - 1, y * P + P - 1], fill=colour + (int(255 * max(0, min(1, a))),))
        # clouds drift a little
        cshift = round(travelled * 0.03)
        for cx0, cy0, cells in clouds:
            for dx, dy in cells:
                cell((cx0 + dx - cshift) % (cols * 2) - 10, cy0 + dy, (250, 252, 255), 0.55)
        # sun glints on the sea
        sshift = round(travelled * 0.12)
        wshift0 = round(travelled * 0.3)
        for x, y, bright, on_path, base, phase, period_s, size in glints:
            s_ = 0.5 + 0.5 * math.sin(2 * math.pi * t / period_s + phase)
            a = base * s_ ** 2
            if a < 0.05:
                continue
            # the sun's path stays under the sun (a reflection moves with the viewer, not the
            # sea); only the scattered glints drift with the water
            X = x if on_path else (x - sshift) % (cols * 2)
            if X >= cols:
                continue
            colour = (255, 255, 250) if bright else (236, 248, 255)
            for i in range(size):
                cell(X + i, y, colour, a)
            if bright and s_ > 0.6:
                arm = a * (s_ - 0.6) / 0.4 * 0.85
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if y + dy > hor:                           # never up into the sky
                        cell(X + dx, y + dy, colour, arm)
        # crests roll in from the open sea, three at a time, one every third of a wave: far ones
        # are thin, faint and close together, and they brighten and spread apart as they near
        # the shore (perspective), where the front one breaks into the foam on the sand
        for k in range(3):
            ph = (t / 4.0 + 0.55 + k / 3) % 1.0
            crest = hor + 4 + round((shore - 2 - hor - 4) * ph ** 1.5)
            gap = 3 if ph < 0.4 else 5                               # broken more when far away
            for x in range(cols + 2):
                if (x * 7 + k * 11 + round(t * 4)) % gap == 0:
                    continue                                          # broken, not a ruled line
                wob = round(0.7 * math.sin((x + wshift0) * 0.35 + t + k * 2.1))
                cell(x, crest + wob, (235, 250, 252), 0.15 + 0.6 * ph)
        # waves: the foam line runs up the shore and back every 4 seconds; the sand it leaves
        # behind is darker and wet, and a thin line of foam follows each wave's edge
        up = 0.5 - 0.5 * math.cos(2 * math.pi * t / 4.0)          # 0 = drawn back, 1 = furthest up
        reach = shore + round(1 + 3 * up)
        wshift = round(travelled * 0.5)
        for x in range(cols + 2):
            wob = round(0.8 * math.sin((x + wshift) * 0.5 + t * 1.3) + 0.6 * math.sin((x + wshift) * 0.23 - t))
            edge = reach + wob
            for y in range(shore, edge):
                cell(x, y, (86, 186, 196), 0.85 - 0.18 * (y - shore))       # thin water over the sand
            cell(x, edge, (255, 255, 255), 0.9)                              # foam
            if (x + wshift) % 3 == 0:
                cell(x, edge - 1, (255, 255, 255), 0.5)
            # a lace of foam trailing behind the edge, left on the water as the wave draws back
            lace = edge - 2 - round(1.5 * (1 - up))
            if (x * 5 + wshift + round(t * 3)) % 4 < 2 and lace > shore - 3:
                cell(x, lace, (255, 255, 255), 0.35 + 0.3 * (1 - up))
            for y in range(edge + 1, shore + 5):
                cell(x, y, (150, 122, 84), 0.45 * (1 - (y - edge) / 5))      # wet sand
        canvas.alpha_composite(layer)
        draw_props(canvas, props, travelled)
    return background, draw_moving


# ---- arctic fox: a snowy evening in Hokkaido -------------------------------------------------
# Blue hour after snowfall. Mt. Yotei ("Ezo Fuji") stands in the pink afterglow, a line of snowy
# firs and white birches runs along the horizon, and a red torii and a lit stone lantern stand
# at the edge of the field. Snow keeps falling, slowly. The snow near the fox is in blue shade,
# clearly darker than its white coat, so the fox and its white outline still read.
HOKKAIDO = dict(
    SKY=[(0, (20, 26, 56)), (200, (42, 54, 98)), (380, (104, 108, 160)), (480, (190, 156, 188)),
         (560, (232, 190, 200))],
    SNOW=[(560, (196, 204, 228)), (600, (156, 170, 206)), (720, (112, 128, 172))],
    MOUNTAIN=(1000, 312, 330),        # peak x, peak y, half width at the horizon (video px)
    TORII_X=58, LANTERN_X=162,        # cells on the horizon layer (drawn 20 cells left): clear of the fox
                                      # before the run and after it (the layer scrolls 32 cells)
)
H_COLOURS = {
    'S': (238, 243, 250), 's': (206, 216, 234),             # snow on things, its shade
    'K': (46, 36, 50), 'R': (200, 64, 52), 'r': (148, 44, 42), 'D': (70, 56, 64),   # torii
    'G': (132, 138, 156), 'g': (98, 104, 124), 'L': (255, 196, 110),                # stone lantern
    'W': (232, 230, 222), 'B': (58, 56, 66),                  # birch bark and its marks
    'F': (40, 60, 82), 'f': (30, 46, 66),                     # firs
}
TORII = """
.SSSSSSSSSSSSSSSS.
KKKKKKKKKKKKKKKKKK
.rRRRRRRRRRRRRRRr.
...RR...ss...RR...
.RRRRRRRRRRRRRRRR.
...RR...RR...RR...
...RR........RR...
...RR........RR...
...RR........RR...
...rR........rR...
...rR........rR...
..DDDD......DDDD..
"""
LANTERN = """
...SS...
.SSSSSS.
GGGGGGGG
.gGGGGg.
..GLLG..
..GLLG..
..gGGg..
...GG...
...GG...
..gGGg..
.GGGGGG.
"""


def hokkaido_stage():
    import numpy as np, math, random
    P, Hk = SCALE, HOKKAIDO
    ys = np.arange(VIDEO_H)
    yy, xx = np.mgrid[0:VIDEO_H, 0:VIDEO_W]
    ramp = lambda stops: np.stack([np.interp(ys, [y for y, _ in stops], [c[k] for _, c in stops]) for k in range(3)], -1)
    img = np.where((yy < HORIZON_Y)[..., None], ramp(Hk['SKY'])[:, None, :], ramp(Hk['SNOW'])[:, None, :]).astype(float)
    cx, cy = (xx // P) * P + P / 2, (yy // P) * P + P / 2
    def paint(mask, colour, alpha=1.0):
        nonlocal img
        m = mask[..., None] * alpha
        img = img * (1 - m) + np.array(colour, float) * m
    # afterglow low in the west (left) of the sky
    glow = 0.35 * np.exp(-(((xx - 180) / 700) ** 2 + ((yy - HORIZON_Y) / 170) ** 2)) * (yy < HORIZON_Y)
    img = img * (1 - glow[..., None]) + np.array((250, 196, 190.)) * glow[..., None]
    # Mt. Yotei: a broad cone with concave flanks, snow over its upper half with a ragged edge,
    # lit pink on the left (the afterglow) and blue on the right
    mx, my, half = Hk['MOUNTAIN']
    d = np.abs(cx - mx) / half
    top = my + (HORIZON_Y - my) * (1 - (1 - np.clip(d, 0, 1)) ** 1.6)
    peak_flat = (np.abs(cx - mx) < 2 * P)
    cone = (cy >= np.where(peak_flat, my, top)) & (cy < HORIZON_Y) & (d <= 1)
    rnd = random.Random(3)
    jag = {c: rnd.choice([-2, -1, 0, 0, 1, 2]) * P for c in range(VIDEO_W // P + 1)}
    snowline = my + 0.46 * (HORIZON_Y - my) + np.vectorize(jag.get)(xx // P)
    left = cx < mx
    paint(cone, (86, 96, 140))
    paint(cone & left, (120, 112, 150), 0.6)
    paint(cone & (cy < snowline), (218, 224, 240))
    paint(cone & (cy < snowline) & left, (246, 222, 226), 0.55)
    # gullies: a few darker streaks down the snow on the shaded side
    for gx in (mx + 3 * P, mx + 9 * P, mx + 16 * P):
        paint(cone & (np.abs(cx - gx - (cy - my) * 0.35) < P / 2) & (cy < snowline + 3 * P) & (cy > my + 3 * P),
              (170, 180, 210), 0.7)
    # the far edge of the snowfield catches the afterglow
    paint((yy >= HORIZON_Y) & (yy < HORIZON_Y + P), (236, 214, 224), 0.5)
    img += np.random.default_rng(7).uniform(-1.2, 1.2, img.shape)
    background = Image.fromarray(np.clip(img, 0, 255).astype('uint8')).convert('RGBA')

    cols, base = VIDEO_W // P, HORIZON_Y // P - 1
    period = cols * 2
    def art(text):
        rows = text.strip('\n').split('\n')
        return [(x, y - len(rows) + 1, ch) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch != '.']
    horizon = []            # (x cell, [(dx, dy, colour key)]) on the horizon layer
    # firs of mixed heights, each with snow on the tips of its tiers
    x = 0
    while x < period:
        h = rnd.randint(3, 7)
        cells = []
        for i in range(h):
            w = max(0, (h - i) // 2 - (i == h - 1))
            for dx in range(-w, w + 1):
                cells.append((dx, -i, 'S' if (i % 2 == 1 and abs(dx) == w) or i == h - 1 else rnd.choice('Ff')))
        horizon.append((x, cells))
        x += rnd.randint(2, 5) if rnd.random() < 0.8 else rnd.randint(6, 10)
    # birches in front of the firs: white trunks with dark marks and a few bare twigs
    for bx in (8, 12, 47, 102, 118, 150, 196, 231):
        h = rnd.randint(9, 13)
        cells = [(0, -i, 'B' if rnd.random() < 0.22 else 'W') for i in range(h)]
        for i in range(h // 2, h, 2):
            s_ = rnd.choice([-1, 1])
            cells += [(s_, -i, 'B'), (2 * s_, -i - 1, 'B')]
        horizon.append((bx, cells))
    horizon.append((Hk['TORII_X'], art(TORII)))
    horizon.append((Hk['LANTERN_X'], art(LANTERN)))
    # on the snow, scrolling with the ground: drifts (a lit crest over a blue shadow, longer
    # nearer the viewer) and dry grass poking through, so the ground visibly moves on a run
    props = []
    for _ in range(46):
        y = rnd.randrange(HORIZON_Y // P + 1, VIDEO_H // P)
        near = (y * P - HORIZON_Y) / (VIDEO_H - HORIZON_Y)
        x, w = rnd.randrange(period), rnd.randint(2, 3) + int(near * 6)
        lift = [0 if abs(i - w / 2) > w / 4 else -1 for i in range(w)] if w > 4 else [0] * w
        props.append((x, [(i, lift[i]) for i in range(w)], y, (230, 236, 250), 0.35 + 0.35 * near))
        props.append((x + 1, [(i, 1) for i in range(w - 1)], y, (92, 106, 156), 0.22 + 0.25 * near))
    for _ in range(22):
        y = rnd.randrange(HORIZON_Y // P + 1, VIDEO_H // P)
        near = (y * P - HORIZON_Y) / (VIDEO_H - HORIZON_Y)
        h = 1 + int(near * 2.5)
        cells = [(0, -i) for i in range(h)] + ([(rnd.choice([-1, 1]), -h + 1)] if h > 1 else [])
        props.append((rnd.randrange(period), cells, y, (96, 84, 88), 0.55 + 0.35 * near))
    props = (period, props)
    # sparkles on the snow: few and slow, so they never pull the eye off the fox
    sparkles = [(rnd.randrange(period), rnd.randrange(HORIZON_Y // P + 2, VIDEO_H // P), rnd.uniform(0.3, 0.6),
                 rnd.uniform(0, 2 * math.pi), rnd.uniform(1.6, 3.4)) for _ in range(34)]
    # falling snow in two layers: far flakes are small, faint and slow; near ones bigger and faster
    flakes = [(rnd.uniform(0, VIDEO_W), rnd.uniform(0, VIDEO_H), far) for far in [True] * 90 + [False] * 34]

    def draw_moving(canvas, t, travelled):
        hshift = round(travelled * HORIZON_SPEED)
        # the lantern's warm light, on the grid, under everything on the horizon
        glow = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        lx = (Hk['LANTERN_X'] - hshift) % period - 20 + 3.5
        ly = base - 6.5
        for gx in range(int(lx) - 8, int(lx) + 9):
            for gy in range(int(ly) - 6, base + 1):
                r_ = math.hypot(gx + 0.5 - lx, (gy + 0.5 - ly) * 1.2)
                if r_ < 7:
                    gd.rectangle([gx * P, gy * P, gx * P + P - 1, gy * P + P - 1], fill=(255, 186, 110, int(255 * 0.22 * (1 - r_ / 7) ** 1.5)))
        canvas.alpha_composite(glow)
        layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        dr = ImageDraw.Draw(layer)
        def cell(x, y, colour, a, size=P):
            dr.rectangle([x, y, x + size - 1, y + size - 1], fill=colour + (int(255 * max(0, min(1, a))),))
        for x0, cells in horizon:
            sx = (x0 - hshift) % period - 20
            if sx < -20 or sx > cols + 2:
                continue
            for dx, dy, ch in cells:
                cell((sx + dx) * P, (base + dy) * P, H_COLOURS[ch], 1)
        canvas.alpha_composite(layer)
        draw_props(canvas, props, travelled)
        layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        dr = ImageDraw.Draw(layer)
        gshift = lambda y: round(travelled * ground_speed(y * P + P / 2))
        for x, y, base_a, phase, per in sparkles:
            s_ = 0.5 + 0.5 * math.sin(2 * math.pi * t / per + phase)
            a = base_a * s_ ** 3
            if a > 0.05:
                X = (x - gshift(y)) % period
                if X < cols:
                    cell(X * P, y * P, (250, 252, 255), a)
        for x0, y0, far in flakes:
            speed, drift, size, a = (26, 0.35, P // 2, 0.5) if far else (58, 0.9, P, 0.8)
            y = (y0 + speed * t) % (VIDEO_H + 20) - 10
            x = (x0 + 14 * math.sin(t * 0.8 + y0) - travelled * SCALE * drift * 0.25) % VIDEO_W
            cell(int(x // size) * size, int(y // size) * size, (246, 249, 255), a, size)
        canvas.alpha_composite(layer)
    return background, draw_moving


# ---- penguin: Antarctic sea ice under the midnight sun ----------------------------------------
# The sun sits low over the sea and never sets; the sky is gold at the horizon and pale blue
# above. Tabular icebergs drift on a strip of dark sea, a colony of tiny penguins stands at the
# far edge of the ice, and the sea ice runs to the viewer with drifts and cracks. The ice near the
# penguin is in cool shade, darker than its white belly.
PENGUIN = dict(
    SCALE=10, GROUND_Y=600, HORIZON_Y=470,
    SEGMENTS=[
        ('idle', 'IDLE · 숨쉬기와 눈 깜빡임', 60),
        ('look', 'LOOK · 마우스 따라보기', 0),
        ('walk', 'WALK · 뒤뚱뒤뚱 걷기', 48),
        ('turn', 'TURN · 돌아서기', 10),
        ('turn', 'TURN · 돌아서기', 10),
        ('slide', 'SLIDE · 배 썰매', 40),
        ('slide_stop', 'SLIDE STOP · 멈추고 일어서기', 8),
        ('flap', 'FLAP · 날개 파닥이기', 8),
        ('fall', 'FALL · 넘어졌다 일어나기', 8),
        ('eat', 'EAT · 물고기 먹기', 10),
        ('preen', 'PREEN · 깃털 다듬기', 8),
        ('shake', 'SHAKE · 몸 털기', 8),
        ('brood', 'BROOD · 새끼 품기', 8),
        ('feed', 'FEED · 새끼에게 먹이 주기', 8),
        ('walk_chick', 'WALK CHICK · 새끼와 걷기', 48),
        ('sleep', 'SLEEP · 서서 자기', 64),
        ('wake', 'WAKE · 깨기', 6),
        ('sleep_chick', 'SLEEP CHICK · 새끼와 같이 자기', 64),
        ('wake_chick', 'WAKE · 깨기', 6),
        ('idle', 'IDLE · 숨쉬기와 눈 깜빡임', 30),
    ],
)
ANTARCTICA = dict(
    SKY=[(0, (70, 116, 186)), (240, (132, 170, 214)), (400, (222, 208, 214)), (470, (252, 220, 184))],
    SEA=[(470, (34, 58, 96)), (500, (44, 74, 116))],
    ICE_EDGE=500,
    ICE=[(500, (214, 226, 242)), (560, (176, 194, 224)), (600, (160, 180, 216)), (720, (122, 144, 190))],
    SUN=((250, 430), 26, (255, 244, 214)),
    RANGE=(620, 1280, 392),          # far mountains beyond the sea: x from, x to, highest peak y
)


def antarctica_stage():
    import numpy as np, math, random
    P, A = SCALE, ANTARCTICA
    ys = np.arange(VIDEO_H)
    yy, xx = np.mgrid[0:VIDEO_H, 0:VIDEO_W]
    ramp = lambda stops: np.stack([np.interp(ys, [y for y, _ in stops], [c[k] for _, c in stops]) for k in range(3)], -1)
    hor, edge = HORIZON_Y, A['ICE_EDGE']
    img = np.where((yy < hor)[..., None], ramp(A['SKY'])[:, None, :],
                   np.where((yy < edge)[..., None], ramp(A['SEA'])[:, None, :], ramp(A['ICE'])[:, None, :])).astype(float)
    (sx, sy), r, sun_c = A['SUN']
    glow = 0.45 * np.exp(-(((xx - sx) / 420) ** 2 + ((yy - sy) / 150) ** 2)) * (yy < hor)
    img = img * (1 - glow[..., None]) + np.array((255, 226, 186.)) * glow[..., None]
    cx, cy = (xx // P) * P + P / 2, (yy // P) * P + P / 2
    disc = (((cx - sx) ** 2 + (cy - sy) ** 2) <= r * r) & (yy < hor)
    img = np.where(disc[..., None], np.array(sun_c, float), img)
    # far mountains of the ice sheet beyond the sea: pale, lit gold on the sunward (left) slopes
    x0r, x1r, peak = A['RANGE']
    prof = np.full(VIDEO_W // P + 1, hor, float)
    for px_, py_, half in ((700, peak + 30, 90), (820, peak, 130), (960, peak + 22, 110), (1090, peak + 8, 120), (1220, peak + 34, 90)):
        c_ = np.arange(VIDEO_W // P + 1) * P + P / 2
        prof = np.minimum(prof, py_ + np.abs(c_ - px_) / half * (hor - py_))
    prof = np.round(prof / P) * P                   # on the grid
    ridge = prof[(xx // P)]
    rising = np.append(prof[1:] < prof[:-1], False)[(xx // P)]     # left (sunward) slopes
    far = (cy >= ridge) & (cy < hor) & (cx >= x0r) & (cx <= x1r)
    cap = far & (cy < ridge + 2 * P)
    img = np.where(far[..., None], np.array((168, 182, 216.)), img)
    img = np.where(cap[..., None], np.array((222, 230, 246.)), img)
    img = np.where((cap & rising)[..., None], np.array((244, 226, 222.)), img)
    # the sun's road on the sea: short bright dashes that widen toward the ice
    road = (yy >= hor) & (yy < edge) & (np.abs(cx - sx) < 30 + (cy - hor) * 1.2) & (((cx // P) + (cy // P)) % 3 == 0)
    img = np.where(road[..., None], np.array((255, 226, 176.)), img)
    rim = (yy >= edge) & (yy < edge + P)
    img = np.where(rim[..., None], img * 0.5 + np.array((250, 240, 236.)) * 0.5, img)
    img += np.random.default_rng(7).uniform(-1.2, 1.2, img.shape)
    background = Image.fromarray(np.clip(img, 0, 255).astype('uint8')).convert('RGBA')

    rnd = random.Random(9)
    cols = VIDEO_W // P
    period = cols * 2
    hor_c, edge_c = hor // P, edge // P
    # tabular icebergs: flat tops, a lit face and a shaded face, sitting on the waterline
    bergs = []
    for x0, w, h in ((24, 14, 3), (48, 6, 2), (112, 16, 3), (140, 8, 2), (176, 18, 4), (212, 7, 2), (240, 12, 3)):
        cells = []
        for dx in range(w):
            top = h - (1 if dx in (0, w - 1) else 0)
            for dy in range(top):
                cells.append((dx, -dy - 1, (248, 250, 255) if dy == top - 1 else (206, 224, 244) if dx < w * 0.6 else (150, 180, 222)))
        bergs.append((x0, cells))
    # the colony far away: little penguins (black back, white front) in loose groups
    colony = []
    for gx in (18, 26, 90, 97, 160, 170, 214):
        for k in range(rnd.randint(3, 6)):
            colony.append(gx + k * 2 + rnd.randint(0, 1))
    # on the ice, scrolling with the ground: drifts and cracks
    props = []
    for _ in range(40):
        y = rnd.randrange(edge_c + 2, VIDEO_H // P)
        near = (y * P - edge) / (VIDEO_H - edge)
        x, w = rnd.randrange(period), rnd.randint(2, 3) + int(near * 5)
        props.append((x, [(i, 0) for i in range(w)], y, (236, 242, 252), 0.35 + 0.3 * near))
        props.append((x + 1, [(i, 1) for i in range(w - 1)], y, (104, 124, 176), 0.2 + 0.25 * near))
    for _ in range(14):                                   # cracks in the sea ice: thin zigzags
        y = rnd.randrange(edge_c + 3, VIDEO_H // P - 1)
        near = (y * P - edge) / (VIDEO_H - edge)
        x = rnd.randrange(period)
        cells, cy_ = [], 0
        for i in range(3 + int(near * 5)):
            cells.append((i, cy_))
            if rnd.random() < 0.35:
                cy_ += rnd.choice((-1, 1))
        props.append((x, cells, y, (92, 116, 170), 0.35 + 0.3 * near))
    props = (period, props)
    sparkles = [(rnd.randrange(period), rnd.randrange(edge_c + 1, VIDEO_H // P), rnd.uniform(0.3, 0.6),
                 rnd.uniform(0, 2 * math.pi), rnd.uniform(1.8, 3.6)) for _ in range(28)]

    def draw_moving(canvas, t, travelled):
        layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        dr = ImageDraw.Draw(layer)
        def cell(x, y, colour, a=1.0):
            dr.rectangle([x * P, y * P, x * P + P - 1, y * P + P - 1], fill=colour + (int(255 * max(0, min(1, a))),))
        bshift = round(travelled * 0.1 + t * 0.15)          # icebergs drift slowly on their own too
        for x0, cells in bergs:
            X = (x0 - bshift) % period - 20
            for dx, dy, col in cells:
                cell(X + dx, edge_c + dy, col)
        cshift = round(travelled * HORIZON_SPEED)
        for x0 in colony:
            X = (x0 - cshift) % period - 10
            cell(X, edge_c, (30, 34, 46))           # head and back
            cell(X, edge_c + 1, (226, 230, 238))    # white front
            cell(X, edge_c + 2, (226, 230, 238))
        canvas.alpha_composite(layer)
        draw_props(canvas, props, travelled)
        layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        dr = ImageDraw.Draw(layer)
        for x, y, base_a, phase, per in sparkles:
            s_ = 0.5 + 0.5 * math.sin(2 * math.pi * t / per + phase)
            a = base_a * s_ ** 3
            if a > 0.05:
                X = (x - round(travelled * ground_speed(y * P + P / 2))) % period
                if X < cols:
                    cell(X, y, (255, 255, 255), a)
        canvas.alpha_composite(layer)
    return background, draw_moving


# ---- corgi: a lawn at the edge of a farm on a sunny day --------------------------------------------
# A clear spring day: puffy clouds drift by, cows graze on a far pasture behind a wooden ranch fence
# with round trees beyond, and the lawn is dotted with tufts and little flowers.
CORGI = dict(
    SCALE=8, GROUND_Y=600, HORIZON_Y=500,
    SEGMENTS=[
        ('idle', 'IDLE · 숨쉬기와 눈 깜빡임', 60),
        ('look', 'LOOK · 마우스 따라보기', 0),
        ('walk', 'WALK · 걷기', 48),
        ('turn', 'TURN · 돌아서기', 10),
        ('turn', 'TURN · 돌아서기', 10),
        ('run', 'RUN · 달리기', 48),
        ('run_stop', 'RUN STOP · 멈추기', 6),
        ('sit', 'SIT · 앉기', 10),
        ('sit_up', 'SIT UP · 일어서기', 6),
        ('lie_down', 'LIE DOWN · 엎드리기 (스플루트)', 10),
        ('lie_up', 'LIE UP · 일어서기', 6),
        ('bark', 'BARK · 짖기', 8),
        ('roll', 'ROLL · 배 보이며 구르기', 8),
        ('spin', 'SPIN · 신나서 빙글빙글', 8),
        ('fetch', 'FETCH · 공 물어오기', 10),
        ('idle', 'IDLE · 숨쉬기와 눈 깜빡임', 30),
    ],
)
PARK = dict(
    SKY=[(0, (96, 164, 226)), (300, (150, 200, 238)), (500, (206, 232, 246))],
    LAWN=[(500, (132, 186, 96)), (600, (112, 170, 80)), (720, (88, 146, 64))],
    PASTURE=((168, 206, 128), (140, 190, 100)),
    COW={'W': (246, 244, 238), 'K': (44, 40, 44), 'n': (232, 160, 160), 'D': (60, 54, 56),
         'B': (150, 96, 60), 'b': (120, 74, 46)},
)
PASTURE_ROWS = 8                                          # the tree line sits this many cells behind the fence
# far cows, 11x6 cells facing right: head up, grazing with the muzzle on the grass, and chewing with
# the head lifted a row
COW_FRAMES = {
    'up':    ["........KWK", "WWKKWWWKKWK", "WKKKWWKWKnn", "WWWWWnWW...", "D.D...D.D..", "D.D...D.D.."],
    'graze': ["...........", "WWKKWWWK...", "WKKKWWKWK..", "WWWWWnWWKWK", "D.D...D.Knn", "D.D...D.D.."],
    'chew':  ["...........", "WWKKWWWK...", "WKKKWWKWKWK", "WWWWWnWWKnn", "D.D...D.D..", "D.D...D.D.."],
}
BROWN_COW = str.maketrans({'W': 'B', 'K': 'b'})


def cow_frame(t, phase):
    """Grazing in bursts: nibble (muzzle down, then up a row) for a few seconds, then lift the head."""
    c = (t + phase) % 7.0
    if c < 4.6:
        return 'graze' if int(c / 0.35) % 3 else 'chew'
    return 'up'


def park_stage():
    """A sunny lawn at the edge of a farm: cows graze on the far pasture behind a wooden ranch fence."""
    import numpy as np, math, random
    P, K = SCALE, PARK
    ys = np.arange(VIDEO_H)
    yy, xx = np.mgrid[0:VIDEO_H, 0:VIDEO_W]
    ramp = lambda stops: np.stack([np.interp(ys, [y for y, _ in stops], [c[k] for _, c in stops]) for k in range(3)], -1)
    img = np.where((yy < HORIZON_Y)[..., None], ramp(K['SKY'])[:, None, :], ramp(K['LAWN'])[:, None, :]).astype(float)
    img = np.where(((yy >= HORIZON_Y) & (yy < HORIZON_Y + P))[..., None], img * 0.6 + np.array((170, 210, 120.)) * 0.4, img)
    cols, base = VIDEO_W // P, HORIZON_Y // P - 1
    top = base - PASTURE_ROWS
    for y in range(top, base + 1):                         # the far pasture, lighter with distance
        f = (y - top) / PASTURE_ROWS
        img[y * P:(y + 1) * P] = [a + (b - a) * f for a, b in zip(*K['PASTURE'])]
    img += np.random.default_rng(7).uniform(-1.2, 1.2, img.shape)
    background = Image.fromarray(np.clip(img, 0, 255).astype('uint8')).convert('RGBA')
    rnd = random.Random(21)
    period = cols * 2
    clouds = []                                           # puffy clouds: round tops on a flat base, a shaded belly
    for i in range(7):
        cx0, cy0, w = i * period // 7 + rnd.randrange(16), rnd.randrange(9, 30), rnd.randint(12, 20)
        bumps = [(rnd.randint(3, w // 2), rnd.randint(3, 4)), (rnd.randint(w // 2, w - 4), rnd.randint(2, 3))]
        cells = set((dx, dy) for dx in range(w) for dy in (0, -1))
        for bx, r in bumps:
            cells |= {(dx, dy) for dx in range(bx - r, bx + r + 1) for dy in range(-r - 1, 1)
                      if (dx - bx) ** 2 + (dy + 1) ** 2 <= r * r + 1 and 0 <= dx < w}
        clouds.append((cx0, cy0, [(dx, dy, dy == 0) for dx, dy in sorted(cells)]))
    trees = []                                            # round trees along the far edge of the pasture
    x = 0
    while x < period:
        r = rnd.randint(3, 5)
        trees.append((x, r, rnd.random() < 0.5))
        x += r * 2 + rnd.randint(-1, 3)
    cows = []                                             # a small herd spread along the pasture
    x = 6
    while x < period - 12:
        brown, flip = rnd.random() < 0.2, rnd.random() < 0.5
        cows.append((x, rnd.randint(3, 4), brown, flip, rnd.uniform(0, 7)))
        x += rnd.choice((18, 26, 38, 52))
    props = []
    for _ in range(40):                                   # grass tufts, taller nearer the viewer
        y = rnd.randrange(HORIZON_Y // P + 2, VIDEO_H // P)
        near = (y * P - HORIZON_Y) / (VIDEO_H - HORIZON_Y)
        h = 1 + int(near * 2)
        cells = [(0, -i) for i in range(h)] + ([(1, -h + 1)] if h > 1 else [])
        props.append((rnd.randrange(period), cells, y, (70, 128, 52), 0.6 + 0.3 * near))
    petals = [(250, 250, 240), (250, 214, 80), (240, 150, 180), (190, 160, 230)]
    for _ in range(70):                                   # flowers: dots far off, little four-petal ones nearer
        y = rnd.randrange(HORIZON_Y // P + 2, VIDEO_H // P)
        near = (y * P - HORIZON_Y) / (VIDEO_H - HORIZON_Y)
        col, x = rnd.choice(petals), rnd.randrange(period)
        if near < 0.35:
            props.append((x, [(0, 0)], y, col, 0.9))
            props.append((x, [(0, 1)], y, (70, 128, 52), 0.7))
        else:
            props.append((x, [(0, 2), (0, 3)], y, (70, 128, 52), 0.8))
            props.append((x, [(-1, 1), (1, 1), (0, 0), (0, 2)], y, col, 0.95))
            props.append((x, [(0, 1)], y, (250, 200, 60) if col != (250, 214, 80) else (220, 130, 50), 1.0))
    props = (period, props)

    def draw_moving(canvas, t, travelled):
        layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        dr = ImageDraw.Draw(layer)
        def cell(x, y, colour, a=1.0):
            dr.rectangle([x * P, y * P, x * P + P - 1, y * P + P - 1], fill=colour + (int(255 * a),))
        cshift = round(travelled * 0.03 + t * 0.3)
        for cx0, cy0, cells in clouds:
            X = (cx0 - cshift) % period - 16
            for dx, dy, belly in cells:
                cell(X + dx, cy0 + dy, (222, 234, 246) if belly else (252, 253, 255), 0.95)
        tshift = round(travelled * HORIZON_SPEED)
        for x0, r, dark in trees:                          # a trunk and a round crown, lit on top
            X = (x0 - tshift) % period - 10
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if dx * dx + dy * dy <= r * r + 1:
                        col = (58, 118, 58) if dark else (74, 138, 64)
                        cell(X + dx, top - r - 1 + dy, (96, 160, 80) if dy < -r // 2 else col)
            cell(X, top, (110, 80, 56))
        for x0, back, brown, flip, phase in cows:
            X = (x0 - tshift) % period - 12
            rows = COW_FRAMES[cow_frame(t, phase)]
            for ry, row in enumerate(rows):
                row = row.translate(BROWN_COW) if brown else row
                for rx, ch in enumerate(row[::-1] if flip else row):
                    if ch != '.':
                        cell(X + rx, base - back - len(rows) + 1 + ry, K['COW'][ch])
        fshift = round(travelled * 0.35)
        for x in range(cols + 2):                          # a wooden ranch fence: two rails, a post every 8 cells
            cell(x, base - 3, (160, 112, 72)); cell(x, base - 1, (160, 112, 72))
            if (x + fshift) % 8 == 0:
                for y in range(base - 4, base + 1):
                    cell(x, y, (122, 82, 52))
        canvas.alpha_composite(layer)
        draw_props(canvas, props, travelled)
    return background, draw_moving


# ---- dachshund: the edge of an autumn forest ----------------------------------------------------
# A clear autumn afternoon: a hazy far wood and, nearer, the forest edge in orange, red and yellow
# with a few dark firs; leaves drift down, and the dry meadow in front is strewn with fallen leaves,
# tufts and a few red toadstools.
DACHSHUND = dict(
    SCALE=8, GROUND_Y=600, HORIZON_Y=500,
    SEGMENTS=[
        ('idle', 'IDLE · 숨쉬기와 꼬리', 60),
        ('look', 'LOOK · 마우스 따라보기', 0),
        ('walk', 'WALK · 걷기', 48),
        ('turn', 'TURN · 돌아서기', 10),
        ('turn', 'TURN · 돌아서기', 10),
        ('run', 'RUN · 달리기', 48),
        ('run_stop', 'RUN STOP · 멈추기', 6),
        ('sit', 'SIT · 앉기', 10),
        ('sit_up', 'SIT UP · 일어서기', 6),
        ('lie_down', 'LIE DOWN · 엎드리기', 10),
        ('lie_up', 'LIE UP · 엎드렸다 일어서기', 6),
        ('wag', 'WAG · 꼬리 흔들기', 8),
        ('burrow', 'BURROW · 굴 파고 들어가기', 10),
        ('idle', 'IDLE · 숨쉬기와 꼬리', 30),
    ],
)
FOREST = dict(
    SKY=[(0, (112, 162, 214)), (280, (178, 202, 222)), (500, (246, 224, 182))],
    GROUND=[(500, (178, 158, 84)), (600, (150, 128, 62)), (720, (110, 90, 46))],
    HAZE=(226, 214, 190),
    FAR=[(196, 126, 72), (206, 164, 84), (160, 112, 70), (124, 126, 76)],
    NEAR=[((228, 122, 44), (246, 162, 70), (184, 88, 34)), ((198, 64, 42), (226, 104, 64), (150, 44, 34)),
          ((236, 186, 62), (250, 214, 110), (196, 142, 44)), ((214, 150, 52), (238, 186, 90), (170, 110, 40))],
    FIR=((56, 88, 62), (78, 112, 76)),
    TRUNK=(86, 60, 44),
    LEAVES=[(230, 124, 44), (204, 70, 44), (238, 188, 64), (190, 110, 52)],
)


def forest_stage():
    import numpy as np, math, random
    P, K = SCALE, FOREST
    ys = np.arange(VIDEO_H)
    yy = np.mgrid[0:VIDEO_H, 0:VIDEO_W][0]
    ramp = lambda stops: np.stack([np.interp(ys, [y for y, _ in stops], [c[k] for _, c in stops]) for k in range(3)], -1)
    split = (HORIZON_Y // P) * P                           # the meadow starts right under the trees' foot
    img = np.where((yy < split)[..., None], ramp(K['SKY'])[:, None, :], ramp(K['GROUND'])[:, None, :]).astype(float)
    img += np.random.default_rng(5).uniform(-1.2, 1.2, img.shape)
    background = Image.fromarray(np.clip(img, 0, 255).astype('uint8')).convert('RGBA')
    rnd = random.Random(33)
    cols, base = VIDEO_W // P, HORIZON_Y // P - 1
    period = cols * 2

    def strip(draw_trees):
        """A layer of trees one period wide, drawn once and scrolled."""
        im = Image.new('RGBA', (period * P, VIDEO_H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        def cell(x, y, col):
            for X in (x % period, x % period - period):
                d.rectangle([X * P, y * P, X * P + P - 1, y * P + P - 1], fill=col + (255,))
        draw_trees(cell)
        return im

    haze = lambda c, f: tuple(int(a + (b - a) * f) for a, b in zip(c, K['HAZE']))

    def far_wood(cell):                                  # a dense, hazy wood: overlapping crowns down to the ground
        x = 0
        while x < period:
            r = rnd.randint(4, 7); top = base - 10 - rnd.randint(0, 6); col = haze(rnd.choice(K['FAR']), 0.45)
            for dx in range(-r, r + 1):
                for y in range(top - r, base + 1):
                    if y > top or dx * dx + (y - top) ** 2 <= r * r + 1:
                        cell(x + dx, y, col)
            x += r + rnd.randint(1, 4)

    def forest_edge(cell):                               # the nearer edge: round autumn crowns on trunks, a few firs
        x = 0
        while x < period:
            if rnd.random() < 0.2:                       # a dark fir
                h = rnd.randint(14, 20)
                for i in range(h):
                    w = (i * 5) // h // 1 + (i % 3 == 2)
                    for dx in range(-w, w + 1):
                        cell(x + dx, base - 2 - h + i, K['FIR'][1] if dx < 0 and i % 3 == 0 else K['FIR'][0])
                cell(x, base - 1, K['TRUNK']); cell(x, base, K['TRUNK'])
                x += 6 + rnd.randint(0, 3)
                continue
            r = rnd.randint(4, 7); trunk = rnd.randint(4, 7); cy = base - trunk - r
            mid, lit, shade = rnd.choice(K['NEAR'])
            for y in range(cy + r - 1, base + 1):
                cell(x, y, K['TRUNK']); cell(x + 1, y, K['TRUNK'])
            for dx in range(-r, r + 2):
                for dy in range(-r, r + 1):
                    if (dx - 0.5) ** 2 + dy * dy <= r * r + 1:
                        col = lit if dy < -r // 2 and dx <= r // 2 else (shade if dy > r // 2 or dx > r * 2 // 3 else mid)
                        cell(x + dx, cy + dy, col)
            for _ in range(3):                           # a few leaves showing the crown's texture
                cell(x + rnd.randint(-r + 2, r - 1), cy + rnd.randint(-r + 2, r - 2), shade)
            x += r * 2 + rnd.randint(-2, 2)
        for x in range(period):                          # undergrowth along the foot of the trees
            h = 1 + (x * 7 + x // 5) % 3
            for y in range(base - h + 1, base + 1):
                cell(x, y, (132, 110, 52) if (x + y) % 4 else (150, 92, 44))

    far, edge = strip(far_wood), strip(forest_edge)
    props = []
    for _ in range(90):                                  # fallen leaves, thicker near the trees
        y = rnd.randrange(HORIZON_Y // P + 1, VIDEO_H // P)
        near = (y * P - HORIZON_Y) / (VIDEO_H - HORIZON_Y)
        if rnd.random() < near * 0.6:
            continue
        cells = [(0, 0)] if near < 0.3 or rnd.random() < 0.4 else rnd.choice(([(0, 0), (1, 0)], [(0, 0), (1, -1)], [(0, 0), (0, -1)]))
        props.append((rnd.randrange(period), cells, y, rnd.choice(K['LEAVES']), 0.9))
    for _ in range(36):                                  # dry grass tufts
        y = rnd.randrange(HORIZON_Y // P + 2, VIDEO_H // P)
        near = (y * P - HORIZON_Y) / (VIDEO_H - HORIZON_Y)
        h = 1 + int(near * 2)
        cells = [(0, -i) for i in range(h)] + ([(1, -h + 1)] if h > 1 else [])
        props.append((rnd.randrange(period), cells, y, (120, 104, 44), 0.7 + 0.2 * near))
    for _ in range(5):                                   # red toadstools with white spots
        y = rnd.randrange(HORIZON_Y // P + 3, VIDEO_H // P - 1); x = rnd.randrange(period)
        props.append((x, [(0, 0), (0, -1)], y, (240, 228, 206), 1.0))
        props.append((x, [(-1, -2), (0, -2), (1, -2), (0, -3)], y, (206, 52, 40), 1.0))
        props.append((x, [(1, -2)], y, (250, 244, 236), 1.0))
    props = (period, props)
    falling = [(rnd.uniform(0, VIDEO_W), rnd.uniform(0, VIDEO_H), rnd.uniform(0, 6.3), rnd.choice(K['LEAVES']),
                rnd.uniform(34, 60)) for _ in range(16)]

    def draw_moving(canvas, t, travelled):
        for layer, speed in ((far, 0.1), (edge, HORIZON_SPEED)):
            sx = round(travelled * speed) % period * P
            canvas.alpha_composite(layer.crop((sx, 0, sx + VIDEO_W, VIDEO_H)) if sx + VIDEO_W <= layer.width
                                   else Image.fromarray(np.concatenate([np.asarray(layer)[:, sx:], np.asarray(layer)[:, :sx + VIDEO_W - layer.width]], 1)))
        draw_props(canvas, props, travelled)
        dr = ImageDraw.Draw(canvas)
        for x0, y0, ph, col, speed in falling:           # leaves drifting down, swaying and tumbling
            y = (y0 + speed * t) % (VIDEO_H + 40) - 20
            x = (x0 + 30 * math.sin(t * 1.1 + ph) - travelled * SCALE * 0.5) % VIDEO_W
            X, Y = int(x // P) * P, int(y // P) * P
            cells = ((0, 0), (P, 0)) if int(t * 3 + ph) % 2 else ((0, 0), (P, P))
            for dx, dy in cells:
                dr.rectangle([X + dx, Y + dy, X + dx + P - 1, Y + dy + P - 1], fill=col + (255,))
    return background, draw_moving


# ---- shiba: a riverside path under cherry blossom in spring ------------------------------------------
# A warm spring afternoon: a peach-tinted sky with a soft sun glow, hazy far hills, the river glinting
# behind a bank of yellow rapeseed, cherry trees in full bloom along the path, and petals blowing
# across the whole scene on the breeze, gusting now and then; the warm earth path is strewn with them.
SHIBA = dict(
    SCALE=8, GROUND_Y=600, HORIZON_Y=500,
    SEGMENTS=[
        ('idle', 'IDLE · 숨쉬기와 눈 깜빡임', 60),
        ('look', 'LOOK · 마우스 따라보기', 0),
        ('walk', 'WALK · 걷기', 48),
        ('turn', 'TURN · 돌아서기', 10),
        ('turn', 'TURN · 돌아서기', 10),
        ('run', 'RUN · 달리기', 48),
        ('run_stop', 'RUN STOP · 멈추기', 6),
        ('sit', 'SIT · 앉기', 10),
        ('sit_up', 'SIT UP · 일어서기', 6),
        ('lie_down', 'LIE DOWN · 엎드리기', 10),
        ('lie_up', 'LIE UP · 엎드렸다 일어서기', 6),
        ('mikaeri', 'MIKAERI · 뒤돌아보기', 8),
        ('smile', 'SMILE · 시바 스마일', 8),
        ('shake', 'SHAKE · 몸 털기', 8),
        ('refuse', 'REFUSE · 산책 거부', 10),
        ('idle', 'IDLE · 숨쉬기와 눈 깜빡임', 30),
    ],
)
SAKURA = dict(
    SKY=[(0, (138, 186, 230)), (220, (206, 212, 230)), (400, (248, 218, 214)), (500, (254, 232, 204))],
    GROUND=[(500, (240, 214, 170)), (600, (228, 196, 150)), (720, (206, 170, 124))],
    HILLS=(214, 196, 204), HILLS_NEAR=(196, 190, 170),
    RIVER=(150, 200, 214), GLINT=(250, 250, 240),
    BANK=(176, 196, 106), RAPE=(250, 218, 70),
    BLOSSOM=((255, 230, 236), (248, 196, 212), (234, 164, 190)),     # lit, mid, shade
    TRUNK=(112, 78, 66),
    PETALS=[(255, 214, 226), (250, 190, 210), (255, 236, 240), (240, 170, 196)],
)


def sakura_stage():
    import numpy as np, math, random
    P, K = SCALE, SAKURA
    ys = np.arange(VIDEO_H)
    yy, xx = np.mgrid[0:VIDEO_H, 0:VIDEO_W]
    ramp = lambda stops: np.stack([np.interp(ys, [y for y, _ in stops], [c[k] for _, c in stops]) for k in range(3)], -1)
    split = (HORIZON_Y // P) * P
    img = np.where((yy < split)[..., None], ramp(K['SKY'])[:, None, :], ramp(K['GROUND'])[:, None, :]).astype(float)
    glow = 0.35 * np.exp(-(((xx - 1010) / 380) ** 2 + ((yy - 120) / 220) ** 2))        # the spring sun, soft
    img = img * (1 - glow[..., None]) + np.array((255, 244, 214.)) * glow[..., None]
    img += np.random.default_rng(11).uniform(-1.2, 1.2, img.shape)
    background = Image.fromarray(np.clip(img, 0, 255).astype('uint8')).convert('RGBA')
    rnd = random.Random(41)
    cols, base = VIDEO_W // P, HORIZON_Y // P - 1
    period = cols * 2

    def strip(draw):
        im = Image.new('RGBA', (period * P, VIDEO_H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        def cell(x, y, col):
            for X in (x % period, x % period - period):
                d.rectangle([X * P, y * P, X * P + P - 1, y * P + P - 1], fill=col + (255,))
        draw(cell)
        return im

    def hills(cell):                                     # two hazy ridges far off, a few pink trees on them
        for x in range(period):
            t1 = int(base - 16 - 5 * (0.5 + 0.5 * math.sin(x / 19)) - 2 * math.sin(x / 7))
            t2 = int(base - 11 - 3 * (0.5 + 0.5 * math.sin(x / 13 + 2)))
            for y in range(t1, base - 7):
                cell(x, y, K['HILLS'])
            for y in range(t2, base - 7):
                cell(x, y, K['HILLS_NEAR'])
            if x % 11 == 0:
                cell(x, t2 - 1, (236, 200, 212)); cell(x + 1, t2 - 1, (236, 200, 212))

    def bank_and_trees(cell):                            # the river, a rapeseed bank, the cherry trees
        for x in range(period):
            for y in range(base - 7, base - 4):
                cell(x, y, K['RIVER'])
            for y in range(base - 4, base + 1):
                cell(x, y, K['BANK'])
            if (x * 5) % 3 == 0:
                cell(x, base - 4, K['RAPE'])
            if (x * 7) % 4 == 0:
                cell(x, base - 3, K['RAPE'])
        x = 2
        lit, mid, shade = K['BLOSSOM']
        while x < period:
            r = rnd.randint(7, 9); cy = base - 9 - r
            for y in range(cy, base + 1):                # the trunk, branching into the crown
                cell(x, y, K['TRUNK']); cell(x + 1, y, K['TRUNK'])
            for bx, by in ((-3, 2), (-2, 3), (3, 2), (4, 3), (-1, 4), (2, 4)):
                cell(x + bx, cy + r - by + 2, K['TRUNK'])
            for dx in range(-r - 4, r + 6):
                for dy in range(-r, r + 2):                  # a round crown with a ragged, drooping underside
                    if (dx / 1.35) ** 2 + dy * dy <= r * r - 1 + rnd.random() * 3 and (dy < r - 2 or rnd.random() < 0.35):
                        col = lit if dy < -r // 2 + (dx < 0) else (shade if dy > r // 3 else mid)
                        if rnd.random() < 0.08:
                            col = shade if col != shade else mid
                        cell(x + dx, cy + dy, col)
            x += r * 2 + rnd.randint(2, 6)

    far, near = strip(hills), strip(bank_and_trees)
    glints = [(rnd.randrange(period), base - 7 + rnd.randrange(3), rnd.uniform(0, 6.3)) for _ in range(30)]
    props = []
    for _ in range(160):                                 # petals lying on the path, thicker under the trees
        y = rnd.randrange(HORIZON_Y // P + 1, VIDEO_H // P)
        near_ = (y * P - HORIZON_Y) / (VIDEO_H - HORIZON_Y)
        if rnd.random() < near_ * 0.5:
            continue
        cells = [(0, 0)] if near_ < 0.5 or rnd.random() < 0.6 else [(0, 0), (1, 0)]
        props.append((rnd.randrange(period), cells, y, rnd.choice(K['PETALS']), 0.95))
    for _ in range(26):                                  # little grass tufts along the path's edge
        y = rnd.choice((HORIZON_Y // P + 1, VIDEO_H // P - 1, VIDEO_H // P - 2))
        props.append((rnd.randrange(period), [(0, 0), (0, -1)], y, (150, 176, 92), 0.9))
    props = (period, props)
    # petals in the air: each drifts left on the breeze (faster in gusts), sways, and flutters between
    # three shapes; nearer petals are bigger, faster and more opaque
    flying = []
    for _ in range(80):
        depth = rnd.random() ** 0.7
        flying.append((rnd.uniform(0, VIDEO_W), rnd.uniform(0, VIDEO_H), rnd.uniform(0, 6.3), rnd.choice(K['PETALS']), depth))
    SHAPES = [((0, 0), (1, 0)), ((0, 0), (1, 1)), ((0, 0),)]

    def draw_moving(canvas, t, travelled):
        for layer, speed in ((far, 0.08), (near, HORIZON_SPEED)):
            sx = round(travelled * speed) % period * P
            if sx + VIDEO_W <= layer.width:
                canvas.alpha_composite(layer.crop((sx, 0, sx + VIDEO_W, VIDEO_H)))
            else:
                a = np.asarray(layer)
                canvas.alpha_composite(Image.fromarray(np.concatenate([a[:, sx:], a[:, :sx + VIDEO_W - layer.width]], 1)))
        dr = ImageDraw.Draw(canvas)
        gshift = round(travelled * HORIZON_SPEED)
        for gx, gy, ph in glints:                        # the river glinting
            if math.sin(t * 2.2 + ph) > 0.6:
                X = (gx - gshift) % period
                if X < cols:
                    dr.rectangle([X * P, gy * P, X * P + P - 1, gy * P + P - 1], fill=K['GLINT'] + (255,))
        draw_props(canvas, props, travelled)
        gust = 1 + 1.6 * max(0.0, math.sin(t * 0.45)) ** 3   # the breeze picks up now and then
        layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for x0, y0, ph, col, depth in flying:
            size = P if depth > 0.35 else P // 2
            fall, wind = 22 + 30 * depth, (40 + 60 * depth) * gust
            y = (y0 + fall * t + 10 * math.sin(t * 1.7 + ph)) % (VIDEO_H + 40) - 20
            x = (x0 - wind * t + 16 * math.sin(t * 1.3 + ph * 2) - travelled * SCALE * (0.2 + 0.6 * depth)) % (VIDEO_W + 40) - 20
            X, Y = int(x // size) * size, int(y // size) * size
            a = int(255 * (0.55 + 0.45 * depth))
            for dx, dy in SHAPES[int(t * 4 + ph * 3) % 3]:
                d.rectangle([X + dx * size, Y + dy * size, X + dx * size + size - 1, Y + dy * size + size - 1], fill=col + (a,))
        canvas.alpha_composite(layer)
    return background, draw_moving


STAGES = {'fox': fox_stage, 'hamster': hamster_stage, 'beach': beach_stage, 'hokkaido': hokkaido_stage,
          'antarctica': antarctica_stage, 'park': park_stage, 'forest': forest_stage,
          'sakura': sakura_stage}
LOOP_POSES = {'curl': 'curl_sleep', 'burrow': 'hide', 'sleep': 'sleep', 'sleep_chick': 'sleep_chick'}


def main():
    conf = {'hamster': HAMSTER, 'penguin': PENGUIN, 'corgi': CORGI, 'dachshund': DACHSHUND, 'shiba': SHIBA, 'shiba-black': SHIBA}.get(ANIMAL)
    if conf:
        g = globals()
        for key in ('SCALE', 'GROUND_Y', 'HORIZON_Y', 'SEGMENTS'):
            g[key] = conf[key]
    s = load()
    frames = Frames(s)
    font = ImageFont.truetype(FONT[0], 32, index=FONT[1])
    ax, ay = s['anchor']
    ticks = timeline(s)
    fps = round(1000 / s['tickMs'])
    sprite_top = GROUND_Y - (ay + 1) * SCALE            # video y of the frame's top edge (with outline)
    # each segment's badge sits just above the highest point the fox reaches in it
    seg_ticks = {}
    for i, t in enumerate(ticks):
        if t[3] is not None:
            seg_ticks.setdefault(t[3], []).append(i)
    badge_bottom = {seg: sprite_top + min(top_row(s['frames'][ticks[i][0]]) for i in idx) * SCALE - BADGE_GAP
                    for seg, idx in seg_ticks.items()}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    if STAGE == 'beach':
        globals()['HORIZON_Y'] = BEACH['SHORE']        # the sand starts at the waterline
    background, draw_moving = STAGES[STAGE]()
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                           '-s', f'{VIDEO_W}x{VIDEO_H}', '-r', str(fps), '-i', '-',
                           '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '14', '-preset', 'slow',
                           '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
    travelled = 0.0                                      # sprite px the fox has run so far
    for i, (name, flip, blink, seg, cursor, move) in enumerate(ticks):
        travelled += move
        canvas = background.copy()
        draw_moving(canvas, i / fps, travelled)
        sprite = frames.get(name, flip, blink)
        # the anchor (feet centre) sits at the middle of the ground line; +1 for the outline padding
        axs = (s['size'][0] - 1 - ax) if flip else ax
        canvas.alpha_composite(sprite, (VIDEO_W // 2 - (axs + 1) * SCALE, sprite_top))
        if seg is not None:
            idx = seg_ticks[seg]
            alpha = min(1, (i - idx[0] + 1) / FADE, (idx[-1] - i + 1) / FADE)
            layer = Image.new('RGBA', (VIDEO_W, VIDEO_H), (0, 0, 0, 0))
            badge(layer, SEGMENTS[seg][1], alpha, font, VIDEO_W // 2, badge_bottom[seg])
            canvas.alpha_composite(layer)
        if cursor:
            draw_cursor(canvas, *cursor, i - seg_ticks[seg][0])
        ff.stdin.write(canvas.convert('RGB').tobytes())
    ff.stdin.close()
    ff.wait()
    print(f'wrote {os.path.relpath(OUT, ROOT)}: {len(ticks)} frames, {len(ticks) / fps:.1f}s at {fps}fps')


if __name__ == '__main__':
    main()
