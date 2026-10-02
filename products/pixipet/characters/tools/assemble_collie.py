"""Writes sprites/collie.json from the frames in draft_collie.py.

Run this only while every border collie frame still comes from the generator.
After frames are edited by hand in sprites/collie.json, edit that file directly.

Usage: python3 tools/assemble_collie.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import draft_collie as D  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), '..')

PALETTE = {
    'K': ('#231f26', '검은 털'), 'H': ('#4a4348', '검은 털 윤기 (등, 허벅지 윗선)'), 'j': ('#141115', '접힌 허벅지 앞쪽 그림자'),
    'w': ('#f4f2f0', '흰 털 (흰 줄, 주둥이, 가슴 털)'),
    'S': ('#383345', '눈두덩 (깜빡일 때 눈 위 칸)'), 's': ('#4a4560', '눈두덩 아래 테두리'),
    'o': ('#120d0f', '눈 위 (깜빡일 때 눈두덩 색)'), 'v': ('#120d0f', '눈 아래 (깜빡일 때 감은 눈 선)'),
    'e': ('#141013', '코'), 'd': ('#2a2226', '입선, 감은 눈'), 't': ('#e8788a', '혀'),
    'i': ('#7a5a66', '귀 안쪽'), 'n': ('#5d6478', '귀 끝 회색 털'),
    'k': ('#262224', '가까운 다리 윗부분 (검은 털)'), 'l': ('#3a3438', '먼 다리 윗부분 (검은 털)'),
    'p': ('#f6f4f0', '가까운 다리 아래쪽과 발 (흰색)'), 'q': ('#d9d5d0', '먼 다리 아래쪽과 발 (흰색 그림자)'),
    'F': ('#e8503a', '프리스비'), 'f': ('#b8382a', '프리스비 테두리 그림자'),
}


def S(name, ticks, dx=None):
    return [name, ticks] if dx is None else [name, ticks, dx]


TICK_MS = 50   # must match the other animals: all share one tick

STALK = [S(f'herd_stalk_{i}', 4, 1) for i in range(len(D.STALK))]   # 1px a step, slow and low

ANIMATIONS = {
    'idle': {'loop': True, 'seq': [S('idle_0', 12), S('idle_1', 12)]},
    # jointed 3px legs, the low tail swaying a little
    'walk': {'loop': True, 'moveX': 0.34, 'seq': [S(f'walk_{i}', 3) for i in range(4)]},
    # a gallop: the head down a pixel, the ears laid back, the tail streaming out behind
    'run': {'pose': ['stand', 'running'], 'loop': True, 'moveX': 3.0, 'seq': [S(f'run_{i}', 1) for i in range(6)]},
    'run_stop': {'pose': ['running', 'stand'], 'loop': False, 'hold': 4,
                 'seq': [S('walk_2', 2, 2), S('walk_3', 2, 1), S('walk_0', 3), S('stand', 2)]},
    # quick, as for the other animals; the three-quarter body is short so the face moves in even steps,
    # and the face-on frame sits on the anchor so the flip does not jump
    'turn': {'loop': False, 'hold': 0, 'flipAt': 2, 'seq': [S('turn_a', 1), S('turn_b', 2), S('turn_a', 1), S('idle_0', 1)]},
    'sit': {'pose': ['stand', 'sit'], 'loop': False, 'hold': 40,
            'seq': [S('sit_a', 3), S('sit_0', 12), S('sit_1', 12), S('sit_0', 2)]},
    'sit_up': {'pose': ['sit', 'stand'], 'loop': False, 'hold': 4, 'seq': [S('sit_a', 3), S('stand', 2)]},
    'lie_down': {'pose': ['stand', 'lie'], 'loop': False, 'hold': 60,
                 'seq': [S('lie_a', 3), S('lie_0', 16), S('lie_1', 14), S('lie_0', 2)]},
    'lie_up': {'pose': ['lie', 'stand'], 'loop': False, 'hold': 4, 'seq': [S('lie_a', 3), S('stand', 2)]},
    # working sheep: drops low, stalks forward lifting each forepaw clear, drops flat staring (the clap),
    # rises and stalks on, freezes mid-stride with the eye, then breaks into a run
    'herd': {'loop': False, 'hold': 4,
             'seq': [S('herd_down', 3), S('herd_crouch', 16)] + STALK * 2 +
                    [S('herd_down', 2), S('herd_clap', 22), S('herd_down', 2), S('herd_crouch', 8)] + STALK +
                    [S('herd_freeze', 20)] + STALK + [S('herd_crouch', 4)] + [S(f'run_{i}', 1, 3) for i in range(6)] * 2 +
                    [S('walk_2', 2, 2), S('walk_3', 2, 1), S('walk_0', 3), S('stand', 2)]},
    # lying down with the chin on the forepaws, looking up from under the brows now and then
    'chin': {'loop': False, 'hold': 4,
             'seq': [S('lie_a', 3), S('lie_0', 10), S('chin_a', 3), S('chin_0', 14), S('chin_1', 14), S('chin_0', 6), S('chin_up', 16),
                     S('chin_0', 14), S('chin_1', 14), S('chin_up', 12), S('chin_0', 8), S('chin_a', 3), S('lie_0', 6), S('lie_a', 3), S('stand', 2)]},
    # a frisbee flies in fast from the right; it takes off early, meets it at the top of the leap and
    # trots about holding it, tail going
    'frisbee': {'loop': False, 'hold': 4,
                'seq': [S(f'fris_watch_{i}', 2) for i in range(len(D.FAR))] +
                       [S('fris_dip', 2), S('fris_jump_0', 2, 1), S('fris_jump_1', 4, 1), S('fris_fall', 3, 1), S('fris_land', 3),
                        S('fris_hold', 6), S('fris_hold_1', 4), S('fris_hold', 4), S('fris_hold_1', 4), S('fris_hold', 10), S('stand', 2)]},
}

TRANSITIONS = {
    'running': {'stand': ['run_stop']},
    'sit': {'stand': ['sit_up']},
    'lie': {'stand': ['lie_up']},
    'stand': {'sit': ['sit'], 'lie': ['lie_down']},
}

_eye = next((x, y) for y, r in enumerate(D.frames()['stand']) for x, ch in enumerate(r) if ch == 'o')
LOOK = {
    'animations': ['idle'],
    # the eye of the standing collie; angles are measured from here
    'headCenter': [_eye[0], _eye[1] + 1],
    'sectors': [{'dir': 'up_fwd', 'min': 25}, {'dir': 'fwd', 'min': -25}, {'dir': 'down_fwd', 'min': -90}],
    'deadZone': 5,
    'turnMargin': 4,
    'frames': {d: {f'idle_{i}': f'idle_{i}_{d}' for i in range(2)} for d in D.LOOK_DIRS},
}

# blinking while sitting and lying down too, and resting the chin on the paws
BLINK = {'animations': ['idle', 'sit', 'lie_down', 'chin'], 'swap': {'o': 'S', 'v': 'd'}, 'everyTicks': [50, 120], 'forTicks': 2, 'doubleChance': 0.25}

PLANNED = []

REACTIONS = {
    'alert': ['herd'], 'curious': ['herd'], 'greet': ['frisbee'], 'wake': ['frisbee'],
    'sleepy': ['chin', 'lie_down'], 'celebrate': ['frisbee'], 'busy': ['herd'], 'wander': ['walk'],
}
IDLE_VARIANTS = ['herd', 'chin', 'frisbee']


def main(animal='collie', display='보더콜리', palette=None, frames_all=None, in_progress=False):
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
