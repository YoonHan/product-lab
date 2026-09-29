"""Writes sprites/corgi.json from the frames in draft_corgi.py.

Run this only while every corgi frame still comes from the generator.
After frames are edited by hand in sprites/corgi.json, edit that file directly.

Usage: python3 tools/assemble_corgi.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import draft_corgi as D  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), '..')

PALETTE = {
    'S': ('#d9853c', '등과 정수리 (붉은 털에서는 털 기본과 같음)'), 'b': ('#d9853c', '털 기본'), 'a': ('#eba35a', '털 밝음'),
    'c': ('#bb6c2c', '털 어두움'), 'd': ('#8f4f20', '털 가장 어두움, 감은 눈 선, 입'),
    # a step darker than the white outline, so the chest and muzzle edges do not merge with it
    'w': ('#f3ede3', '흰 가슴, 주둥이, 이마 줄'), 'x': ('#d9cfc1', '흰 털 그림자'),
    'n': ('#e7a39c', '귀 안쪽'), 'r': ('#eba09a', '볼터치'), 'e': ('#1c1616', '코'), 't': ('#d9646c', '혀'),
    'o': ('#1c1616', '눈 위 (깜빡일 때 털 색)'), 'v': ('#1c1616', '눈 아래 (깜빡일 때 감은 눈 선)'),
    'k': ('#d9853c', '가까운 다리'), 'l': ('#b56629', '먼 다리'), 'p': ('#f3ede3', '가까운 흰 양말'), 'q': ('#d9cfc1', '먼 흰 양말'),
    'T': ('#c8dc3c', '테니스공'), 'U': ('#f5f7e8', '테니스공 줄'),
    'z': ('#e7b44a', '짖는 소리 선, 테두리 없음'),
}


def S(name, ticks, dx=None):
    return [name, ticks] if dx is None else [name, ticks, dx]


TICK_MS = 50   # must match the other animals: all share one tick

BARK = [S('bark_1', 2), S('bark_0', 4)]
PADDLE = [S('belly_0', 3), S('belly_1', 3)]
# a full turn in place with little hops: face-on, from behind, face-on again (going from one view
# straight to the next reads as spinning at this speed, with no left-facing frames needed)
SPIN = [S('turn_a', 2), S('turn_b_hop', 2), S('turn_b', 1), S('spin_back_hop', 2), S('spin_back', 1), S('turn_b_hop', 2), S('turn_a', 2), S('idle_0', 2)]

ANIMATIONS = {
    # breathing: the whole body swells 1px and settles
    'idle': {'loop': True, 'seq': [S('idle_0', 12), S('idle_1', 12)]},
    'walk': {'loop': True, 'moveX': 0.5, 'seq': [S(f'walk_{i}', 2) for i in range(4)]},
    # a bouncy gallop: one 1px rise a stride, 2 ticks a frame
    'run': {'pose': ['stand', 'running'], 'loop': True, 'moveX': 2.0, 'seq': [S(f'run_{i}', 2) for i in range(4)]},
    'run_stop': {'pose': ['running', 'stand'], 'loop': False, 'hold': 4,
                 'seq': [S('walk_2', 2, 2), S('walk_3', 2, 1), S('walk_0', 3), S('stand', 2)]},
    'turn': {'loop': False, 'hold': 0, 'flipAt': 2, 'seq': [S('turn_a', 1), S('turn_b', 2), S('turn_a', 1), S('idle_0', 1)]},
    'sit': {'pose': ['stand', 'sit'], 'loop': False, 'hold': 40, 'seq': [S('sit_a', 3), S('sit_0', 12), S('sit_1', 12), S('sit_0', 2)]},
    'sit_up': {'pose': ['sit', 'stand'], 'loop': False, 'hold': 4, 'seq': [S('sit_a', 3), S('stand', 2)]},
    # lying down into the sploot: the legs fold, the belly goes down, the hind legs slide back
    'lie_down': {'pose': ['stand', 'lie'], 'loop': False, 'hold': 60,
                 'seq': [S('lie_a', 3), S('lie_0', 4), S('lie_1', 3), S('lie_2', 16), S('lie_3', 14), S('lie_2', 2)]},
    'lie_up': {'pose': ['lie', 'stand'], 'loop': False, 'hold': 4, 'seq': [S('lie_1', 3), S('lie_0', 3), S('lie_a', 3), S('stand', 2)]},
    # barking: the whole dog lunges forward on each bark, three times
    'bark': {'loop': False, 'hold': 4, 'seq': [S('bark_0', 4)] + BARK * 3 + [S('bark_0', 4), S('stand', 2)]},
    # rolling over for a belly rub: down, over onto its side, onto its back paddling, and back up
    'roll': {'loop': False, 'hold': 4, 'seq': [S('lie_a', 3), S('lie_0', 4), S('roll_side', 3)] + PADDLE * 6
             + [S('roll_side', 3), S('lie_0', 4), S('lie_a', 3), S('stand', 2)]},
    'spin': {'loop': False, 'hold': 4, 'seq': SPIN * 3 + [S('bark_0', 3), S('bark_1', 2), S('bark_0', 4), S('stand', 2)]},
    # fetch: a tennis ball rolls up to its nose; it bows to take it, turns to you, sets it down and
    # waits for the next throw
    'fetch': {'loop': False, 'hold': 10, 'seq': [S(f'fetch_ball_{i}', 3) for i in range(4)] + [
        S('fetch_ball_3', 6), S('fetch_bow', 3), S('fetch_grab', 6), S('fetch_carry_0', 8), S('fetch_3q', 3),
        S('fetch_front', 12), S('fetch_front_drop', 10), S('fetch_3q_drop', 3), S('fetch_drop', 16)]},
}

TRANSITIONS = {
    'running': {'stand': ['run_stop']},
    'sit': {'stand': ['sit_up']},
    'lie': {'stand': ['lie_up']},
    'stand': {'sit': ['sit'], 'lie': ['lie_down']},
}

LOOK = {
    'animations': ['idle'],
    # the eye of the standing corgi; angles are measured from here
    'headCenter': [D.PX + 19, D.GROUND - len(D.BODY) - D.LEG_ROWS + 1 + 9],
    # three head directions: the head is big, and five steps were too close to tell apart
    'sectors': [{'dir': 'up_fwd', 'min': 25}, {'dir': 'fwd', 'min': -25}, {'dir': 'down_fwd', 'min': -90}],
    'deadZone': 5,
    'turnMargin': 4,
    'frames': {d: {f'idle_{i}': f'idle_{i}_{d}' for i in range(2)} for d in D.LOOK_DIRS},
}

BLINK = {'animations': ['idle'], 'swap': {'o': 'b', 'v': 'd'}, 'everyTicks': [50, 120], 'forTicks': 2, 'doubleChance': 0.25}

PLANNED = []

REACTIONS = {
    'alert': ['bark'], 'curious': ['sit'], 'greet': ['spin', 'roll'], 'wake': ['spin'],
    'sleepy': ['lie_down'], 'celebrate': ['spin', 'bark'], 'busy': ['fetch'], 'wander': ['walk'],
}
IDLE_VARIANTS = ['bark', 'roll', 'fetch']


def main():
    frames_all = D.frames()
    order = ['stand']
    for a in ANIMATIONS.values():
        for step in a['seq']:
            if step[0] not in order:
                order.append(step[0])
    order += [n for n in frames_all if n not in order and n != 'bow']
    J = lambda v: json.dumps(v, ensure_ascii=False)
    out = ['{', '  "name": "corgi",', '  "displayName": "웰시코기",', '  "version": 1,', '  "inProgress": true,',
           f'  "tickMs": {TICK_MS},', f'  "size": {J([D.W, D.H])},', f'  "anchor": {J(list(D.ANCHOR))},', '  "palette": {']
    items = list(PALETTE.items())
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
    out += ['  },', f'  "transitions": {J(TRANSITIONS)},', f'  "look": {J(LOOK)},', '  "outline": {"skip": ["z"]},',
            f'  "blink": {J(BLINK)},', f'  "planned": {J(PLANNED)},', f'  "idleVariants": {J(IDLE_VARIANTS)},', '  "reactions": {']
    items = list(REACTIONS.items())
    out += [f'    {J(k)}: {J(v)}' + (',' if i < len(items) - 1 else '') for i, (k, v) in enumerate(items)]
    out += ['  }', '}']
    text = '\n'.join(out) + '\n'
    json.loads(text)
    with open(os.path.join(ROOT, 'sprites', 'corgi.json'), 'w') as f:
        f.write(text)
    print(f'wrote sprites/corgi.json: {len(order)} frames, {len(ANIMATIONS)} animations')


if __name__ == '__main__':
    main()
