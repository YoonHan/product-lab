"""Renders a showcase video that plays every fox animation once, with a label badge.

Needs Pillow and ffmpeg. Frames are drawn from sprites/fox.json exactly as the app would
draw them (white 1px outline, integer scale) and piped to ffmpeg; one tick = one video frame.

Usage: python3 tools/render_video.py [out.mp4]
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'dist', 'fox-all-animations.mp4')

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
    with open(os.path.join(ROOT, 'sprites', 'fox.json')) as f:
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
        swap = {s['blink']['eye']: s['blink']['closed']} if blink else {}
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
        if seg_i == len(SEGMENTS) - 1 or end_pose == 'running':   # running flows straight into stopping
            continue
        # the pause: breathe when standing, keep breathing when asleep, otherwise hold the pose
        if end_pose == 'stand':
            pause = [idle[t % len(idle)][0] for t in range(GAP)]
        elif end_pose == 'curl':
            body = play_once(anims['curl_sleep'])[sum(st[1] for st in anims['curl_sleep']['seq'][:2]):]
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


def draw_cursor(canvas, x, y, size=1.6):
    """A macOS-style arrow pointer with its tip at (x, y), drawn smooth at 4x and scaled down."""
    ss = 4
    pts = [(0, 0), (0, 17), (4.2, 13), (7, 19.5), (9.8, 18.3), (7.2, 12.2), (12.5, 12.2)]
    w, h = int(16 * size * ss), int(24 * size * ss)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    poly = [(2 * ss + px * size * ss, 2 * ss + py * size * ss) for px, py in pts]
    d.polygon(poly, fill=(0, 0, 0, 255))
    inner = [(2 * ss + px * size * ss, 2 * ss + py * size * ss) for px, py in
             [(1.4, 3.2), (1.4, 13.6), (4.6, 10.6), (7.6, 17.4), (8.6, 17), (5.8, 10.6), (10, 10.6)]]
    d.polygon(inner, fill=(255, 255, 255, 255))
    img = img.resize((w // ss, h // ss), Image.LANCZOS)
    canvas.alpha_composite(img, (int(x - 2 * size), int(y - 2 * size)))


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


def main():
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
    background = make_background()
    stars = make_stars()
    props = make_props()
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                           '-s', f'{VIDEO_W}x{VIDEO_H}', '-r', str(fps), '-i', '-',
                           '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '14', '-preset', 'slow',
                           '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
    travelled = 0.0                                      # sprite px the fox has run so far
    for i, (name, flip, blink, seg, cursor, move) in enumerate(ticks):
        travelled += move
        canvas = background.copy()
        draw_stars(canvas, stars, i / fps, travelled)
        draw_props(canvas, props, travelled)
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
            draw_cursor(canvas, *cursor)
        ff.stdin.write(canvas.convert('RGB').tobytes())
    ff.stdin.close()
    ff.wait()
    print(f'wrote {os.path.relpath(OUT, ROOT)}: {len(ticks)} frames, {len(ticks) / fps:.1f}s at {fps}fps')


if __name__ == '__main__':
    main()
