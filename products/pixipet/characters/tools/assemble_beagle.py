"""Writes sprites/beagle.json from the frames in draft_beagle.py.

Run this only while every beagle frame still comes from the generator.
After frames are edited by hand in sprites/beagle.json, edit that file directly.

Usage: python3 tools/assemble_beagle.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import draft_beagle as D  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), '..')

PALETTE = {
    'b': ('#c98746', '황갈색 털 기본'), 'a': ('#dca464', '황갈색 털 밝음'), 'c': ('#a86a32', '황갈색 털 어두움'),
    'K': ('#2e2729', '검은 안장 무늬'), 'H': ('#4a3f41', '안장 무늬 윤기'), 'E': ('#a8672f', '귀 (조금 진한 황갈색)'),
    'w': ('#f7f3ec', '흰 털 (주둥이, 흰 줄, 가슴, 배, 꼬리 끝)'), 'x': ('#dcd4c6', '흰 털 그림자'),
    'd': ('#6b4526', '입선, 감은 눈'), 'e': ('#1f1718', '코'),
    'o': ('#1f1718', '눈 위 (깜빡일 때 털 색)'), 'v': ('#1f1718', '눈 아래 (깜빡일 때 감은 눈 선)'),
    'r': ('#e9a293', '볼터치'), 't': ('#d9646c', '혀'),
    'k': ('#c98746', '가까운 뒷다리 허벅지'), 'l': ('#a86a32', '먼 뒷다리 허벅지'),
    'p': ('#f7f3ec', '가까운 다리 아래쪽 뼈와 발 (흰색), 앞다리'), 'q': ('#dcd4c6', '먼 다리 아래쪽 뼈와 발 (흰색 그림자)'),
    'G': ('#e2b36e', '뼈다귀 과자'), 'g': ('#b88444', '과자 그림자'),
    'W': ('#ffffff', '개의 몸 위에 그린 과자 테두리, 테두리 없음'),
    'z': ('#e7b44a', '고개 털기 움직임 표시, 테두리 없음'), 'm': ('#d4ccf2', '하울링 음파 곡선, 테두리 없음'),
}


def S(name, ticks, dx=None):
    return [name, ticks] if dx is None else [name, ticks, dx]


TICK_MS = 50   # must match the other animals: all share one tick

SNIFF = [S('sit_sniff_1', 2), S('sit_sniff_0', 2)]
HOWL = [S('howl_1', 4), S('howl_2', 4)]
SHAKE = [S('shake_0', 2), S('shake_1', 2)]

ANIMATIONS = {
    'idle': {'loop': True, 'seq': [S('idle_0', 12), S('idle_1', 12)]},
    # jointed 2px legs, no body bob, the ears swinging a little, the tail swaying
    'walk': {'loop': True, 'moveX': 0.34, 'seq': [S(f'walk_{i}', 3) for i in range(4)]},
    # a dog's gallop: legs fold under and stretch out, the back flexes, the ears fly
    'run': {'pose': ['stand', 'running'], 'loop': True, 'moveX': 3.0, 'seq': [S(f'run_{i}', 1) for i in range(6)]},
    'run_stop': {'pose': ['running', 'stand'], 'loop': False, 'hold': 4,
                 'seq': [S('walk_2', 2, 2), S('walk_3', 2, 1), S('walk_0', 3), S('stand', 2)]},
    # quick, as for the other animals; the face-on frame sits on the anchor so the flip does not jump
    'turn': {'loop': False, 'hold': 0, 'flipAt': 2, 'seq': [S('turn_a', 1), S('turn_b', 2), S('turn_a', 1), S('idle_0', 1)]},
    # sitting is not a statue: it breathes, sniffs the air and flicks an ear (and blinks, see BLINK)
    'sit': {'pose': ['stand', 'sit'], 'loop': False, 'hold': 40,
            'seq': [S('sit_a', 3), S('sit_0', 12), S('sit_1', 12), S('sit_0', 14), S('sit_sniff_0', 4)] + SNIFF * 3 +
                   [S('sit_0', 10), S('sit_1', 12), S('sit_ear', 3), S('sit_0', 10), S('sit_1', 12), S('sit_0', 2)]},
    'sit_up': {'pose': ['sit', 'stand'], 'loop': False, 'hold': 4, 'seq': [S('sit_a', 3), S('stand', 2)]},
    'lie_down': {'pose': ['stand', 'lie'], 'loop': False, 'hold': 60,
                 'seq': [S('lie_a', 3), S('lie_0', 16), S('lie_1', 14), S('lie_0', 2)]},
    'lie_up': {'pose': ['lie', 'stand'], 'loop': False, 'hold': 4, 'seq': [S('lie_a', 3), S('stand', 2)]},
    # following a trail: nose down by the ground, a slow short-stepped walk, the head bobbing as it sniffs
    'scent': {'loop': False, 'hold': 4, 'moveX': 0.25, 'seq': [S(f'scent_{i}', 4) for i in range(4)] * 4 + [S('stand', 2)]},
    # sitting, the muzzle up at the sky, "aroo" in waves
    'howl': {'loop': False, 'hold': 4,
             'seq': [S('sit_a', 3), S('sit_0', 8), S('howl_a', 3), S('howl_0', 4)] + HOWL * 3 + [S('howl_0', 4)] + HOWL * 2 +
                    [S('howl_0', 6), S('howl_a', 3), S('sit_0', 8), S('sit_a', 3), S('stand', 2)]},
    # shaking the head, the long ears flung out, the body still
    'shake': {'loop': False, 'hold': 4, 'seq': SHAKE * 4 + [S('shake_settle', 3), S('stand', 2)]},
    # stealing a treat: spots it, checks the viewer, creeps up (1px a step, so the biscuit stays put on the
    # ground), snatches it and gallops off, then gulps it down
    'steal': {'loop': False, 'hold': 4,
              'seq': [S('steal_spot', 12), S('steal_check', 14), S('steal_spot', 6)] +
                     [S(f'steal_sneak_{k}', 4, 1) for k in range(D.SNEAK_STEPS)] +
                     [S('steal_grab', 6), S('steal_hold', 8)] + [S(f'steal_run_{i}', 1, 3) for i in range(6)] * 2 +
                     [S('steal_hold', 6), S('steal_gulp', 10), S('stand', 2)]},
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
    # the eye of the standing beagle; angles are measured from here
    'headCenter': [_eye[0], _eye[1] + 1],
    'sectors': [{'dir': 'up_fwd', 'min': 25}, {'dir': 'fwd', 'min': -25}, {'dir': 'down_fwd', 'min': -90}],
    'deadZone': 5,
    'turnMargin': 4,
    'frames': {d: {f'idle_{i}': f'idle_{i}_{d}' for i in range(2)} for d in D.LOOK_DIRS},
}

# blinking while sitting and lying down too, not only standing
BLINK = {'animations': ['idle', 'sit', 'lie_down'], 'swap': {'o': 'b', 'v': 'd'}, 'everyTicks': [50, 120], 'forTicks': 2, 'doubleChance': 0.25}

PLANNED = []

REACTIONS = {
    'alert': ['howl'], 'curious': ['scent'], 'greet': ['shake', 'howl'], 'wake': ['shake'],
    'sleepy': ['lie_down'], 'celebrate': ['howl', 'shake'], 'busy': ['steal'], 'wander': ['scent', 'walk'],
}
IDLE_VARIANTS = ['scent', 'howl', 'shake', 'steal']


def main(animal='beagle', display='비글', palette=None, frames_all=None, in_progress=False):
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
    out += ['  },', f'  "transitions": {J(TRANSITIONS)},', f'  "look": {J(LOOK)},', '  "outline": {"skip": ["W", "z", "m"]},',
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
