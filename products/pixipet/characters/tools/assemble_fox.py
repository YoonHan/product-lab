"""Writes sprites/fox.json from the draft frames in draft_fox.py.

Run this only while every fox frame still comes from the draft generator.
After frames are edited by hand in sprites/fox.json, edit that file directly.

Usage: python3 tools/assemble_fox.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import draft_fox as D  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), '..')

PALETTE = {
    'a': ('#ed985f', '털 밝음'), 'b': ('#d97b3d', '털 기본'), 'c': ('#c2692f', '털 어두움'),
    'd': ('#a85a25', '털 가장 어두움 (귀 뒤, 꼬리 경계)'), 'w': ('#f5ecdc', '크림'), 'x': ('#dbcdb8', '크림 그림자'),
    'k': ('#3b2c29', '가까운 다리'), 'l': ('#2a1f1d', '먼 다리'), 'e': ('#171213', '코'), 'o': ('#171213', '눈 (깜빡일 때 바뀜)'),
    'p': ('#f5ecdc', '가까운 발 (흰 양말)'), 'q': ('#dbcdb8', '먼 발 (흰 양말)'),
    't': ('#c9575a', '혀'), 'z': ('#6f9bd1', '잠결 표시 (zzz), 테두리 없음'), 'y': ('#7c5b40', '흙 (땅 파기)'),
}


def S(name, ticks, dx=None):
    return [name, ticks] if dx is None else [name, ticks, dx]


TICK_MS = 50   # one tick; slow poses hold several ticks, fast motion changes every tick

# hold: ticks to stay on the last frame before moving on (one-shot animations only)
# pose: [start, end] body pose; animations without it start and end standing
# flipAt: step at which the fox turns to face the other way (used by "turn")
ANIMATIONS = {
    'idle': {'loop': True, 'seq': [S('idle_0', 8), S('idle_1', 2), S('idle_2', 2), S('idle_3', 8)]},
    'walk': {'loop': True, 'moveX': 0.625, 'seq': [S(f'walk_{i}', 2) for i in range(8)]},
    'run': {'pose': ['stand', 'running'], 'loop': True, 'moveX': 2.5, 'seq': [S(f'run_{i}', 1) for i in range(8)]},
    'run_stop': {'pose': ['running', 'stand'], 'loop': False, 'hold': 4,
                 'seq': [S('walk_2', 2, 2), S('walk_3', 2, 2), S('walk_4', 4, 1), S('walk_5', 4, 1), S('stand', 4)]},
    # turning around: three-quarter view toward the viewer, face-on, then three-quarter the other way (0.25s)
    'turn': {'loop': False, 'hold': 0, 'flipAt': 2, 'seq': [S('turn_a', 1), S('turn_b', 2), S('turn_a', 1), S('idle_0', 1)]},
    'sit': {'pose': ['stand', 'sit'], 'loop': False, 'hold': 50,
            'seq': [S('sit_a', 2), S('sit_b', 2), S('sit_c', 2), S('sit_d', 2), S('sit_e', 2), S('sit_2', 2)]},
    'sit_up': {'pose': ['sit', 'stand'], 'loop': False, 'hold': 4,
               'seq': [S('sit_e', 2), S('sit_d', 2), S('sit_c', 2), S('sit_b', 2), S('sit_a', 2), S('stand', 2)]},
    'lie_down': {'pose': ['stand', 'lie'], 'loop': False, 'hold': 60,
                 'seq': [S('lie_a', 2), S('lie_0', 2), S('lie_b', 2), S('lie_1', 3), S('lie_2', 5), S('lie_3', 2)]},
    'lie_up': {'pose': ['lie', 'stand'], 'loop': False, 'hold': 4,
               'seq': [S('lie_2', 4), S('lieup_h', 3), S('lieup_0', 4), S('sit_2', 4), S('sit_e', 2), S('sit_d', 2), S('sit_c', 2),
                       S('sit_b', 2), S('sit_a', 2), S('stand', 2)]},
    'stretch': {'loop': False, 'hold': 8, 'seq': [
        S('stretch_a', 2), S('stretch_0', 2), S('stretch_b', 2), S('stretch_1', 2), S('stretch_2', 6),
        S('yawn_0', 2), S('yawn_1', 3), S('yawn_2', 12), S('yawn_1', 3), S('yawn_0', 2),                 # a big yawn
        S('stretch_2', 4), S('stretch_3', 8), S('stretch_2', 4), S('stretch_1', 2), S('stretch_b', 2), S('stretch_0', 2), S('stretch_a', 2), S('stand', 2)]},
    'pounce': {'loop': False, 'hold': 8, 'seq': [
        S('pounce_0', 3), S('pounce_1', 10),                                                          # sink and look up
        S('pounce_2', 2), S('pounce_1', 2), S('pounce_2', 2), S('pounce_1', 2), S('pounce_2', 2), S('pounce_1', 6),  # wiggle
        *[S(f'pounce_air_{i}', 1, 1 if i < 6 else None) for i in range(10)],                           # the leap
        S('pounce_air_10', 6),                                                                         # nose in the snow
        S('pounce_settle_0', 2), S('pounce_settle_1', 2), S('pounce_settle_2', 2), S('pounce_stuck', 5),  # rump comes down
        S('pounce_shove_0', 2), S('pounce_shove_1', 3), S('pounce_shove_0', 2), S('pounce_stuck', 3),    # shoves, stuck
        S('pounce_shove_0', 2), S('pounce_shove_1', 3), S('pounce_shove_0', 2), S('pounce_stuck', 2),
        S('pounce_shove_0', 2), S('pounce_shove_1', 5),                                                  # one big shove
        S('pounce_pop', 3, -1), S('pounce_pop_1', 3, -1),                                                   # head pops free
        S('stretch_1', 3), S('stretch_b', 2), S('stretch_0', 2), S('stretch_a', 2), S('stand', 2)]},
    'listen': {'loop': False, 'hold': 4, 'seq': [
        S('listen_0', 6), S('listen_2', 2), S('listen_0', 2), S('listen_3', 2), S('listen_0', 3), S('listen_2', 2),
        S('listen_0', 4), S('listen_1', 10), S('listen_4', 2), S('listen_1', 6), S('listen_4', 2), S('listen_1', 4),
        S('listen_0', 4), S('stand', 2)]},
    'curl_sleep': {'pose': ['lie', 'curl'], 'loop': True, 'loopFrom': 2,
                   'seq': [S('curl_0', 8), S('curl_1', 10), *[S(f'sleep_{i}', 2) for i in range(16)]]},
    'uncurl': {'pose': ['curl', 'lie'], 'loop': False,
               'seq': [S('curl_1', 4), S('uncurl_a', 4), S('uncurl_b', 4), S('curl_0', 4), S('lie_3', 4)]},
    'dig': {'pose': ['stand', 'bow'], 'loop': True, 'loopFrom': 5,
            'seq': [S('stretch_a', 2), S('stretch_0', 2), S('stretch_b', 2), S('stretch_1', 2), S('dig_h', 1),
                    S('dig_0', 2), S('dig_1', 2), S('dig_2', 2), S('dig_3', 2)]},
    'dig_end': {'pose': ['bow', 'stand'], 'loop': False, 'hold': 4,
                'seq': [S('dig_h', 1), S('stretch_1', 2), S('stretch_b', 2), S('stretch_0', 2), S('stretch_a', 2), S('stand', 2)]},
    'lick': {'loop': True, 'seq': [S('lick_0', 2), S('lick_1', 2), S('lick_2', 2), S('lick_1', 2)]},
    'itch': {'pose': ['stand', 'sit'], 'loop': True, 'loopFrom': 5,
             'seq': [S('sit_a', 2), S('sit_b', 2), S('sit_c', 2), S('sit_d', 2), S('sit_e', 2), S('itch_0', 2), S('itch_1', 2)]},
}

# Idle blinking: the eye colour 'o' is drawn as closed fur for a moment every few seconds.
BLINK = {'animations': ['idle'], 'eye': 'o', 'closed': 'd', 'everyTicks': [50, 120], 'forTicks': 2, 'doubleChance': 0.25}

# How to get from one pose to another. The player finds a path through this table
# whenever the next animation starts in a different pose than the current one ends.
TRANSITIONS = {
    'running': {'stand': ['run_stop']},
    'sit': {'stand': ['sit_up']},
    'lie': {'stand': ['lie_up']},
    'curl': {'lie': ['uncurl']},
    'bow': {'stand': ['dig_end']},
    'stand': {'sit': ['sit'], 'lie': ['lie_down']},
}

LOOK_DIRS = [d for d, v in D.LOOK.items() if v is not None]
LOOK = {
    'animations': ['idle'],
    # the eye of the standing fox; angles are measured from here
    'headCenter': [D.OX + 28, D.OY + 8],
    # degrees toward the side the fox faces: 90 = straight up, -90 = straight down
    'sectors': [{'dir': 'up', 'min': 60}, {'dir': 'up_fwd', 'min': 20}, {'dir': 'fwd', 'min': -20},
                {'dir': 'down_fwd', 'min': -60}, {'dir': 'down', 'min': -90}],
    'deadZone': 6,      # px around the head where the fox keeps its current look
    'turnMargin': 4,    # px the cursor must pass behind the fox before it turns around
    'frames': {d: {f'idle_{i}': f'idle_{i}_{d}' for i in range(4)} for d in LOOK_DIRS},
}

REACTIONS = {
    'alert': ['listen', 'pounce'], 'curious': ['listen'], 'greet': ['sit'], 'wake': ['stretch'],
    'sleepy': ['lie_down', 'curl_sleep'], 'celebrate': ['pounce', 'run'], 'busy': ['dig'], 'wander': ['walk'],
}


def main():
    frames_all = D.frames()
    order = ['stand']
    for a in ANIMATIONS.values():
        for step in a['seq']:
            if step[0] not in order:
                order.append(step[0])
    for d in LOOK_DIRS:
        order += [f'idle_{i}_{d}' for i in range(4)]
    J = lambda v: json.dumps(v, ensure_ascii=False)
    out = ['{', '  "name": "fox",', '  "displayName": "여우",', '  "version": 6,',
           f'  "tickMs": {TICK_MS},', f'  "size": {J([D.W, D.H])},', f'  "anchor": {J([17 + D.OX, 21 + D.OY])},', '  "palette": {']
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
    out += ['  },', '  "transitions": {']
    items = list(TRANSITIONS.items())
    out += [f'    {J(k)}: {J(v)}' + (',' if i < len(items) - 1 else '') for i, (k, v) in enumerate(items)]
    out += ['  },', '  "look": {']
    items = list(LOOK.items())
    out += [f'    {J(k)}: {J(v)}' + (',' if i < len(items) - 1 else '') for i, (k, v) in enumerate(items)]
    out += ['  },', '  "outline": {"skip": ["z"]},', f'  "blink": {J(BLINK)},', '  "planned": [],', '  "idleVariants": ["lick", "itch", "listen"],', '  "reactions": {']
    items = list(REACTIONS.items())
    out += [f'    {J(k)}: {J(v)}' + (',' if i < len(items) - 1 else '') for i, (k, v) in enumerate(items)]
    out += ['  }', '}']
    text = '\n'.join(out) + '\n'
    json.loads(text)
    with open(os.path.join(ROOT, 'sprites', 'fox.json'), 'w') as f:
        f.write(text)
    print(f'wrote sprites/fox.json: {len(order)} frames, {len(ANIMATIONS)} animations')


if __name__ == '__main__':
    main()
