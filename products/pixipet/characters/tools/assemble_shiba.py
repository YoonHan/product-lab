"""Writes sprites/shiba.json from the frames in draft_shiba.py.

Run this only while every shiba frame still comes from the generator.
After frames are edited by hand in sprites/shiba.json, edit that file directly.

Usage: python3 tools/assemble_shiba.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import draft_shiba as D  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), '..')

PALETTE = {
    'b': ('#d99345', '털 기본 (적색)'), 'a': ('#ecb468', '털 밝음'), 'c': ('#b87330', '털 어두움'),
    'd': ('#7e4a1f', '털 가장 어두움, 감은 눈 선, 입'),
    'w': ('#f4e8d2', '크림색 털 (우라지로: 눈썹, 주둥이, 목, 가슴, 꼬리 안쪽)'), 'x': ('#dccbb0', '크림색 털 그림자'),
    'n': ('#f0d9c0', '귀 안쪽'), 'r': ('#eba09a', '볼터치'), 'e': ('#1c1616', '코'), 't': ('#d9646c', '혀'),
    'o': ('#1c1616', '눈 위 (깜빡일 때 털 색)'), 'v': ('#1c1616', '눈 아래 (깜빡일 때 감은 눈 선)'),
    'k': ('#d99345', '가까운 다리'), 'l': ('#b87330', '먼 다리'), 'p': ('#f4e8d2', '가까운 다리 아래쪽 뼈와 발 (크림)'),
    'q': ('#dccbb0', '먼 다리 아래쪽 뼈와 발 (크림)'),
    'L': ('#c8402f', '목줄, 테두리 없음'), 'z': ('#e7b44a', '몸 털기 움직임 선, 테두리 없음'),
    'Z': ('#bfe3f2', '몸 털기 물방울, 테두리 없음'),
}


def S(name, ticks, dx=None):
    return [name, ticks] if dx is None else [name, ticks, dx]


TICK_MS = 50   # must match the other animals: all share one tick

PANT = [S('smile', 5), S('smile_pant', 4)]
# the head starts on its own, the whole body joins with the torso rolling against the head and water
# flying, then it dies out at the rump; 1 tick a frame
H_, B_, R_ = ['shake_h0', 'shake_level', 'shake_h1', 'shake_level'], ['shake_b0', 'shake_b1', 'shake_b2', 'shake_b1'], ['shake_r0', 'shake_r1']
SHAKE = [S(n, 1) for n in H_ * 2 + B_ * 4 + R_ * 3]
TUG = [S('refuse_tug', 2), S('refuse_brace', 8)]

ANIMATIONS = {
    # breathing: the chest swells 1px and settles
    'idle': {'loop': True, 'seq': [S('idle_0', 12), S('idle_1', 12)]},
    # jointed legs, no body bob (a 1px bob every other frame bounced)
    'walk': {'loop': True, 'moveX': 0.5, 'seq': [S(f'walk_{i}', 2) for i in range(4)]},
    # a dog's gallop: legs fold under and stretch out, the back flexes, 1px up once a stride
    'run': {'pose': ['stand', 'running'], 'loop': True, 'moveX': 2.5, 'seq': [S(f'run_{i}', 1) for i in range(6)]},
    'run_stop': {'pose': ['running', 'stand'], 'loop': False, 'hold': 4,
                 'seq': [S('walk_2', 2, 2), S('walk_3', 2, 1), S('walk_0', 3), S('stand', 2)]},
    'turn': {'loop': False, 'hold': 0, 'flipAt': 2, 'seq': [S('turn_a', 1), S('turn_b', 2), S('turn_a', 1), S('idle_0', 1)]},
    'sit': {'pose': ['stand', 'sit'], 'loop': False, 'hold': 40, 'seq': [S('sit_a', 3), S('sit_0', 12), S('sit_1', 12), S('sit_0', 2)]},
    'sit_up': {'pose': ['sit', 'stand'], 'loop': False, 'hold': 4, 'seq': [S('sit_a', 3), S('stand', 2)]},
    'lie_down': {'pose': ['stand', 'lie'], 'loop': False, 'hold': 60,
                 'seq': [S('lie_a', 3), S('lie_0', 16), S('lie_1', 14), S('lie_0', 2)]},
    'lie_up': {'pose': ['lie', 'stand'], 'loop': False, 'hold': 4, 'seq': [S('lie_a', 3), S('stand', 2)]},
    # refusing the walk: braced against the leash, dragged 1px on each tug, then flat on the ground
    'refuse': {'loop': False, 'hold': 4, 'seq': [S('refuse_stand', 8), S('refuse_brace', 10)] + TUG * 3
               + [S('refuse_down', 3), S('refuse_flop', 40), S('refuse_down', 3), S('refuse_stand', 8), S('stand', 2)]},
    # mikaeri: looking back over the shoulder at the viewer
    'mikaeri': {'loop': False, 'hold': 4, 'seq': [S('idle_0', 4), S('mikaeri_a', 2), S('mikaeri', 30), S('mikaeri_a', 2), S('idle_0', 2)]},
    # the shiba smile: face-on, eyes squeezed shut, mouth open, panting
    'smile': {'loop': False, 'hold': 4, 'seq': [S('turn_a', 2), S('turn_b', 4)] + PANT * 4 + [S('turn_b', 4), S('turn_a', 2), S('idle_0', 2)]},
    # shaking off: eyes shut, the head twists, the shake runs down to the rump, legs wide
    'shake': {'loop': False, 'hold': 4, 'seq': SHAKE + [S('shake_end', 6), S('stand', 4)]},
}

TRANSITIONS = {
    'running': {'stand': ['run_stop']},
    'sit': {'stand': ['sit_up']},
    'lie': {'stand': ['lie_up']},
    'stand': {'sit': ['sit'], 'lie': ['lie_down']},
}

LOOK = {
    'animations': ['idle'],
    # the eye of the standing shiba; angles are measured from here
    'headCenter': [D.PX + 20, D.GROUND - len(D.BODY) - D.LEG_ROWS + 1 + 5],
    'sectors': [{'dir': 'up_fwd', 'min': 25}, {'dir': 'fwd', 'min': -25}, {'dir': 'down_fwd', 'min': -90}],
    'deadZone': 5,
    'turnMargin': 4,
    'frames': {d: {f'idle_{i}': f'idle_{i}_{d}' for i in range(2)} for d in D.LOOK_DIRS},
}

BLINK = {'animations': ['idle'], 'swap': {'o': 'b', 'v': 'd'}, 'everyTicks': [50, 120], 'forTicks': 2, 'doubleChance': 0.25}

PLANNED = []

REACTIONS = {
    'alert': ['mikaeri'], 'curious': ['mikaeri'], 'greet': ['smile'], 'wake': ['shake'],
    'sleepy': ['lie_down'], 'celebrate': ['smile', 'run'], 'busy': ['refuse'], 'wander': ['walk'],
}
IDLE_VARIANTS = ['mikaeri', 'shake', 'smile']


def main():
    frames_all = D.frames()
    order = ['stand']
    for a in ANIMATIONS.values():
        for step in a['seq']:
            if step[0] not in order:
                order.append(step[0])
    order += [n for n in frames_all if n not in order]
    J = lambda v: json.dumps(v, ensure_ascii=False)
    out = ['{', '  "name": "shiba",', '  "displayName": "시바견",', '  "version": 1,',
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
    out += ['  },', f'  "transitions": {J(TRANSITIONS)},', f'  "look": {J(LOOK)},', '  "outline": {"skip": ["L", "z", "Z"]},',
            f'  "blink": {J(BLINK)},', f'  "planned": {J(PLANNED)},', f'  "idleVariants": {J(IDLE_VARIANTS)},', '  "reactions": {']
    items = list(REACTIONS.items())
    out += [f'    {J(k)}: {J(v)}' + (',' if i < len(items) - 1 else '') for i, (k, v) in enumerate(items)]
    out += ['  }', '}']
    text = '\n'.join(out) + '\n'
    json.loads(text)
    with open(os.path.join(ROOT, 'sprites', 'shiba.json'), 'w') as f:
        f.write(text)
    print(f'wrote sprites/shiba.json: {len(order)} frames, {len(ANIMATIONS)} animations')


if __name__ == '__main__':
    main()
