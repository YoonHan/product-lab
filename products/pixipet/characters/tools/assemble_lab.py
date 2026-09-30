"""Writes sprites/lab.json from the frames in draft_lab.py.

Run this only while every Labrador frame still comes from the generator.
After frames are edited by hand in sprites/lab.json, edit that file directly.

Usage: python3 tools/assemble_lab.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import draft_lab as D  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), '..')

PALETTE = {
    'b': ('#e8c68a', '털 기본 (노란색)'), 'a': ('#f3dbab', '털 밝음'), 'c': ('#cfa865', '털 어두움'),
    'd': ('#7c5a34', '털 가장 어두움, 입선, 감은 눈'), 'E': ('#cf9d58', '귀 (조금 진한 금빛)'),
    'w': ('#f5e6c6', '연한 가슴, 주둥이, 배'), 'x': ('#e0c89a', '연한 털 그림자'),
    'e': ('#2a1f1d', '코'), 'o': ('#2a1f1d', '눈 위 (깜빡일 때 털 색)'), 'v': ('#2a1f1d', '눈 아래 (깜빡일 때 감은 눈 선)'),
    'r': ('#eaa393', '볼터치'), 't': ('#d9646c', '혀'),
    'k': ('#e8c68a', '가까운 다리'), 'l': ('#c9a060', '먼 다리'), 'p': ('#f3dcae', '가까운 다리 아래쪽 뼈와 발 (연한 색)'),
    'q': ('#d9bd88', '먼 다리 아래쪽 뼈와 발 (연한 색)'),
    'Y': ('#ffd42a', '노란 오리 장난감'), 'y': ('#e3a91c', '오리 그림자'), 'O': ('#f08a2c', '오리 부리, 삑 소리 표시'),
    'K': ('#2a1f1d', '오리 눈'), 'W': ('#ffffff', '개의 몸 위에 그린 오리 테두리, 테두리 없음'),
    'P': ('#8cc3e6', '물웅덩이, 테두리 없음'), 'Q': ('#d6ecf8', '웅덩이 물결, 테두리 없음'), 'Z': ('#bfe3f2', '튀는 물방울, 테두리 없음'),
}


def S(name, ticks, dx=None):
    return [name, ticks] if dx is None else [name, ticks, dx]


TICK_MS = 50   # must match the other animals: all share one tick

WAG = [S(f'wag_{i}', 2) for i in range(4)]
PRANCE = [S('show_0', 3), S('show_1', 3)]
SQUEAK = [S('show_squeeze', 2), S('show_hold', 5)]
SPLASH = [S('splash_1', 3), S('splash_2', 2), S('splash_3', 3), S('splash_4', 2), S('splash_5', 3)]

ANIMATIONS = {
    'idle': {'loop': True, 'seq': [S('idle_0', 12), S('idle_1', 12)]},
    # jointed 3px legs, no body bob, the ears flapping gently, the tail swaying
    'walk': {'loop': True, 'moveX': 0.34, 'seq': [S(f'walk_{i}', 3) for i in range(4)]},
    # a dog's gallop: legs fold under and stretch out, the back flexes, the ears fly
    'run': {'pose': ['stand', 'running'], 'loop': True, 'moveX': 3.0, 'seq': [S(f'run_{i}', 1) for i in range(6)]},
    'run_stop': {'pose': ['running', 'stand'], 'loop': False, 'hold': 4,
                 'seq': [S('walk_2', 2, 2), S('walk_3', 2, 1), S('walk_0', 3), S('stand', 2)]},
    'turn': {'loop': False, 'hold': 0, 'flipAt': 2, 'seq': [S('turn_a', 1), S('turn_b', 2), S('turn_a', 1), S('idle_0', 1)]},
    'sit': {'pose': ['stand', 'sit'], 'loop': False, 'hold': 40, 'seq': [S('sit_a', 3), S('sit_0', 12), S('sit_1', 12), S('sit_0', 2)]},
    'sit_up': {'pose': ['sit', 'stand'], 'loop': False, 'hold': 4, 'seq': [S('sit_a', 3), S('stand', 2)]},
    'lie_down': {'pose': ['stand', 'lie'], 'loop': False, 'hold': 60,
                 'seq': [S('lie_a', 3), S('lie_0', 16), S('lie_1', 14), S('lie_0', 2)]},
    'lie_up': {'pose': ['lie', 'stand'], 'loop': False, 'hold': 4, 'seq': [S('lie_a', 3), S('stand', 2)]},
    # wagging hard: the thick tail sweeps up, out and down, the ears flop
    'wag': {'loop': False, 'hold': 4, 'seq': WAG * 6 + [S('stand', 2)]},
    # showing off the rubber duck held in its jaws: a proud prance, then two squeaks
    'show': {'loop': False, 'hold': 4, 'seq': [S('show_hold', 8)] + PRANCE * 4 + [S('show_hold', 6)] + SQUEAK * 2 + [S('show_hold', 6), S('stand', 2)]},
    # splashing in a puddle: front paws stamped in turn, drops flying
    'splash': {'loop': False, 'hold': 4, 'seq': [S('splash_0', 8)] + SPLASH + SPLASH[1:] + SPLASH[1:] + [S('splash_0', 8), S('stand', 2)]},
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
    # the eye of the standing Labrador; angles are measured from here
    'headCenter': [_eye[0], _eye[1] + 1],
    'sectors': [{'dir': 'up_fwd', 'min': 25}, {'dir': 'fwd', 'min': -25}, {'dir': 'down_fwd', 'min': -90}],
    'deadZone': 5,
    'turnMargin': 4,
    'frames': {d: {f'idle_{i}': f'idle_{i}_{d}' for i in range(2)} for d in D.LOOK_DIRS},
}

BLINK = {'animations': ['idle'], 'swap': {'o': 'b', 'v': 'd'}, 'everyTicks': [50, 120], 'forTicks': 2, 'doubleChance': 0.25}

PLANNED = []

REACTIONS = {
    'alert': ['wag'], 'curious': ['splash'], 'greet': ['wag', 'show'], 'wake': ['wag'],
    'sleepy': ['lie_down'], 'celebrate': ['splash', 'wag'], 'busy': ['show'], 'wander': ['walk'],
}
IDLE_VARIANTS = ['wag', 'show', 'splash']


def main(animal='lab', display='래브라도 리트리버', palette=None, frames_all=None, in_progress=False):
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
    out += ['  },', f'  "transitions": {J(TRANSITIONS)},', f'  "look": {J(LOOK)},', '  "outline": {"skip": ["Z", "P", "Q", "W"]},',
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
