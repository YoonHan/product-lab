"""Writes sprites/dachshund.json from the frames in draft_dachshund.py.

Run this only while every dachshund frame still comes from the generator.
After frames are edited by hand in sprites/dachshund.json, edit that file directly.

Usage: python3 tools/assemble_dachshund.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import draft_dachshund as D  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), '..')

PALETTE = {
    'B': ('#2e2628', '검은 털'), 'H': ('#4b3f41', '검은 털 윤기 (등과 정수리)'), 'D': ('#1f191b', '늘어진 귀 (한 단계 어둡게)'),
    'n': ('#c9853f', '황갈색 (눈썹 점, 뺨, 주둥이, 가슴, 다리)'), 'N': ('#a8692e', '황갈색 그림자'),
    'e': ('#140f10', '코'), 'o': ('#140f10', '눈 위 (깜빡일 때 검은 털)'), 'v': ('#140f10', '눈 아래 (깜빡일 때 황갈색 선)'),
    'm': ('#d9646c', '혀'), 'r': ('#d98a7e', '볼터치'),
    'k': ('#c9853f', '가까운 다리'), 'l': ('#a8692e', '먼 다리'),
    'y': ('#8a6a4a', '흙더미'), 'Y': ('#6a5038', '흙더미 그늘'),
    'f': ('#9c7a52', '날아가는 흙덩이, 테두리 없음'), 'F': ('#6f5a44', '멀어진 흙덩이, 테두리 없음'),
}


def S(name, ticks, dx=None):
    return [name, ticks] if dx is None else [name, ticks, dx]


TICK_MS = 50   # must match the other animals: all share one tick

WAG = [S(f'wag_{i}', 1) for i in range(4)]
DIG = [S(f'dig_{i}', 2) for i in range(4)]
IN_HOLE = [S(f'burrow_{i}', 2) for i in range(4)]

ANIMATIONS = {
    # breathing, with a slow wag of the tail on the breath in
    'idle': {'loop': True, 'seq': [S('idle_0', 12), S('idle_1', 12)]},
    'walk': {'loop': True, 'moveX': 0.5, 'seq': [S(f'walk_{i}', 2) for i in range(4)]},
    # the long ears lift back when airborne and swing down on landing; one 1px rise a stride
    'run': {'pose': ['stand', 'running'], 'loop': True, 'moveX': 2.0, 'seq': [S(f'run_{i}', 2) for i in range(4)]},
    'run_stop': {'pose': ['running', 'stand'], 'loop': False, 'hold': 4,
                 'seq': [S('walk_2', 2, 2), S('walk_3', 2, 1), S('walk_0', 3), S('stand', 2)]},
    'turn': {'loop': False, 'hold': 0, 'flipAt': 2, 'seq': [S('turn_a', 1), S('turn_b', 2), S('turn_a', 1), S('idle_0', 1)]},
    'sit': {'pose': ['stand', 'sit'], 'loop': False, 'hold': 40, 'seq': [S('sit_a', 3), S('sit_0', 12), S('sit_1', 12), S('sit_0', 2)]},
    'sit_up': {'pose': ['sit', 'stand'], 'loop': False, 'hold': 4, 'seq': [S('sit_a', 3), S('stand', 2)]},
    'lie_down': {'pose': ['stand', 'lie'], 'loop': False, 'hold': 60, 'seq': [S('lie_a', 3), S('lie_0', 14), S('lie_1', 14), S('lie_0', 2)]},
    'lie_up': {'pose': ['lie', 'stand'], 'loop': False, 'hold': 4, 'seq': [S('lie_a', 3), S('stand', 2)]},
    # a burrow hound: digs with the front paws (dirt flies back under the belly and piles up behind),
    # pushes its head into the heap it made, wags its rump and tail, and backs out with dirt on its head
    'burrow': {'loop': False, 'hold': 4, 'seq': DIG * 4 + IN_HOLE * 5 + [S('burrow_out', 10), S('stand', 2)]},
    # happy: the tail wags fast and the ears bounce
    'wag': {'loop': False, 'hold': 4, 'seq': WAG * 14 + [S('stand', 2)]},
}

TRANSITIONS = {
    'running': {'stand': ['run_stop']},
    'sit': {'stand': ['sit_up']},
    'lie': {'stand': ['lie_up']},
    'stand': {'sit': ['sit'], 'lie': ['lie_down']},
}

LOOK = {
    'animations': ['idle'],
    # the eye of the standing dachshund; angles are measured from here
    'headCenter': [D.PX + 25, D.GROUND - len(D.BODY) - D.LEG_ROWS + 1 + 4],
    'sectors': [{'dir': 'up_fwd', 'min': 25}, {'dir': 'fwd', 'min': -25}, {'dir': 'down_fwd', 'min': -90}],
    'deadZone': 5,
    'turnMargin': 4,
    'frames': {d: {f'idle_{i}': f'idle_{i}_{d}' for i in range(2)} for d in D.LOOK_DIRS},
}

BLINK = {'animations': ['idle'], 'swap': {'o': 'B', 'v': 'n'}, 'everyTicks': [50, 120], 'forTicks': 2, 'doubleChance': 0.25}

PLANNED = []

REACTIONS = {
    'alert': ['wag'], 'curious': ['burrow'], 'greet': ['wag'], 'wake': ['wag'],
    'sleepy': ['lie_down'], 'celebrate': ['run', 'wag'], 'busy': ['burrow'], 'wander': ['walk'],
}
IDLE_VARIANTS = ['wag', 'sit']


def main():
    frames_all = D.frames()
    order = ['stand']
    for a in ANIMATIONS.values():
        for step in a['seq']:
            if step[0] not in order:
                order.append(step[0])
    order += [n for n in frames_all if n not in order]
    J = lambda v: json.dumps(v, ensure_ascii=False)
    out = ['{', '  "name": "dachshund",', '  "displayName": "닥스훈트",', '  "version": 1,',
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
    out += ['  },', f'  "transitions": {J(TRANSITIONS)},', f'  "look": {J(LOOK)},', '  "outline": {"skip": ["f", "F"]},',
            f'  "blink": {J(BLINK)},', f'  "planned": {J(PLANNED)},', f'  "idleVariants": {J(IDLE_VARIANTS)},', '  "reactions": {']
    items = list(REACTIONS.items())
    out += [f'    {J(k)}: {J(v)}' + (',' if i < len(items) - 1 else '') for i, (k, v) in enumerate(items)]
    out += ['  }', '}']
    text = '\n'.join(out) + '\n'
    json.loads(text)
    with open(os.path.join(ROOT, 'sprites', 'dachshund.json'), 'w') as f:
        f.write(text)
    print(f'wrote sprites/dachshund.json: {len(order)} frames, {len(ANIMATIONS)} animations')


if __name__ == '__main__':
    main()
