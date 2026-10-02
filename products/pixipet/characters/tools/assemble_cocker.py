"""Writes sprites/cocker.json from the frames in draft_cocker.py.

Run this only while every cocker spaniel frame still comes from the generator.
After frames are edited by hand in sprites/cocker.json, edit that file directly.

Usage: python3 tools/assemble_cocker.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import draft_cocker as D  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), '..')

PALETTE = {
    'w': ('#f6f1ea', '흰 털'), 'x': ('#ddd4c8', '흰 털 그림자 (장식털 밑단)'),
    'O': ('#e0994a', '주황 털 (귀, 정수리, 눈 둘레, 등 무늬)'), 'o': ('#c47f36', '주황 털 그림자 (귀 가장자리, 곱슬 끝)'),
    'a': ('#f2b56c', '주황 털 밝음'),
    'v': ('#120d0f', '눈 위 (깜빡일 때 털 색)'), 'y': ('#120d0f', '눈 아래 (깜빡일 때 감은 눈 선)'),
    'e': ('#1a1416', '코'), 'd': ('#6a4430', '입선, 감은 눈'), 't': ('#e07a86', '혀'),
    'k': ('#f6f1ea', '가까운 다리 (흰색)'), 'l': ('#d5ccbf', '먼 다리 (흰색 그림자)'),
    'p': ('#f6f1ea', '가까운 발'), 'q': ('#d5ccbf', '먼 발'),
}


def S(name, ticks, dx=None):
    return [name, ticks] if dx is None else [name, ticks, dx]


TICK_MS = 50   # must match the other animals: all share one tick

WAG = [S(f'wag_{i}', 1) for i in range(4)]
HOP = [S('hop_dip', 3), S('hop_up', 2), S('hop_top', 3), S('hop_down', 2), S('hop_land', 3)]

ANIMATIONS = {
    'idle': {'loop': True, 'seq': [S('idle_0', 12), S('idle_1', 12)]},
    # jointed 3px legs under the feathering, its hem and the ears swinging a little each step
    'walk': {'loop': True, 'moveX': 0.34, 'seq': [S(f'walk_{i}', 3) for i in range(4)]},
    # a gallop with a small swing (short legs), the ears and the feathering streaming back
    'run': {'pose': ['stand', 'running'], 'loop': True, 'moveX': 3.0, 'seq': [S(f'run_{i}', 1) for i in range(6)]},
    'run_stop': {'pose': ['running', 'stand'], 'loop': False, 'hold': 4,
                 'seq': [S('walk_2', 2, 2), S('walk_3', 2, 1), S('walk_0', 3), S('stand', 2)]},
    'turn': {'loop': False, 'hold': 0, 'flipAt': 2, 'seq': [S('turn_a', 1), S('turn_b', 2), S('turn_a', 1), S('idle_0', 1)]},
    'sit': {'pose': ['stand', 'sit'], 'loop': False, 'hold': 40,
            'seq': [S('sit_a', 3), S('sit_0', 12), S('sit_1', 12), S('sit_0', 2)]},
    'sit_up': {'pose': ['sit', 'stand'], 'loop': False, 'hold': 4, 'seq': [S('sit_a', 3), S('stand', 2)]},
    'lie_down': {'pose': ['stand', 'lie'], 'loop': False, 'hold': 60,
                 'seq': [S('lie_a', 3), S('lie_0', 16), S('lie_1', 14), S('lie_0', 2)]},
    'lie_up': {'pose': ['lie', 'stand'], 'loop': False, 'hold': 4, 'seq': [S('lie_a', 3), S('stand', 2)]},
    # the merry cocker: the docked tail flicking fast with the root of it, the ears bouncing
    'wag': {'loop': False, 'hold': 4, 'seq': WAG * 8 + [S('stand', 6)] + WAG * 6 + [S('stand', 2)]},
    # bouncing on the spot, the long ears flying up in the air and flopping as it lands
    'hop': {'loop': False, 'hold': 4, 'seq': HOP * 3 + [S('stand', 2)]},
}

TRANSITIONS = {
    'running': {'stand': ['run_stop']},
    'sit': {'stand': ['sit_up']},
    'lie': {'stand': ['lie_up']},
    'stand': {'sit': ['sit'], 'lie': ['lie_down']},
}

_eye = next((x, y) for y, r in enumerate(D.frames()['stand']) for x, ch in enumerate(r) if ch == 'v')
LOOK = {
    'animations': ['idle'],
    # the eye of the standing cocker; angles are measured from here
    'headCenter': [_eye[0], _eye[1] + 1],
    'sectors': [{'dir': 'up_fwd', 'min': 25}, {'dir': 'fwd', 'min': -25}, {'dir': 'down_fwd', 'min': -90}],
    'deadZone': 5,
    'turnMargin': 4,
    'frames': {d: {f'idle_{i}': f'idle_{i}_{d}' for i in range(2)} for d in D.LOOK_DIRS},
}

# blinking while sitting and lying down too
BLINK = {'animations': ['idle', 'sit', 'lie_down'], 'swap': {'v': 'O', 'y': 'd'}, 'everyTicks': [50, 120], 'forTicks': 2, 'doubleChance': 0.25}

PLANNED = []

REACTIONS = {
    'alert': ['hop'], 'curious': ['wag'], 'greet': ['wag', 'hop'], 'wake': ['wag'],
    'sleepy': ['lie_down'], 'celebrate': ['hop', 'wag'], 'busy': ['wag'], 'wander': ['walk'],
}
IDLE_VARIANTS = ['wag', 'hop']


def main(animal='cocker', display='코커 스패니얼', palette=None, frames_all=None, in_progress=False):
    """Writes sprites/<animal>.json."""
    palette = palette or PALETTE
    frames_all = frames_all or D.frames()
    order = ['stand']
    for a in ANIMATIONS.values():
        for step in a['seq']:
            if step[0] not in order:
                order.append(step[0])
    order += [n for n in frames_all if n not in order]
    J = lambda v: json.dumps(v, ensure_ascii=False)
    out = ['{', f'  "name": {J(animal)},', f'  "displayName": {J(display)},', '  "version": 1,'] + (['  "inProgress": true,'] if in_progress else []) + [
           f'  "tickMs": {TICK_MS},', f'  "size": {J([D.W, D.H])},', f'  "anchor": {J(list(D.ANCHOR))},', '  "palette": {']
    items = list(palette.items())
    out += [f'    {J(k)}: {J({"hex": h, "role": r})}' + (',' if i < len(items) - 1 else '') for i, (k, (h, r)) in enumerate(items)]
    out += ['  },', '  "frames": {']
    for i, name in enumerate(order):
        rows = frames_all[name]
        out.append(f'    {J(name)}: [')
        out += [f'      {J(r)}' + (',' if j < len(rows) - 1 else '') for j, r in enumerate(rows)]
        out.append('    ]' + (',' if i < len(order) - 1 else ''))
    out += ['  },', '  "animations": {']
    items = list(ANIMATIONS.items())
    out += [f'    {J(k)}: {J(v)}' + (',' if i < len(items) - 1 else '') for i, (k, v) in enumerate(items)]
    out += ['  },', f'  "transitions": {J(TRANSITIONS)},', f'  "look": {J(LOOK)},', '  "outline": {"skip": []},',
            f'  "blink": {J(BLINK)},', f'  "planned": {J(PLANNED)},', f'  "idleVariants": {J(IDLE_VARIANTS)},', '  "reactions": {']
    items = list(REACTIONS.items())
    out += [f'    {J(k)}: {J(v)}' + (',' if i < len(items) - 1 else '') for i, (k, v) in enumerate(items)]
    out += ['  }', '}']
    text = '\n'.join(out) + '\n'
    json.loads(text)
    with open(os.path.join(ROOT, 'sprites', f'{animal}.json'), 'w') as f:
        f.write(text)
    print(f'wrote sprites/{animal}.json: {len(order)} frames, {len(ANIMATIONS)} animations')


if __name__ == '__main__':
    main()
