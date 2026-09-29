"""Writes sprites/penguin.json from the frames in draft_penguin.py.

Run this only while every penguin frame still comes from the generator.
After frames are edited by hand in sprites/penguin.json, edit that file directly.

Usage: python3 tools/assemble_penguin.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import draft_penguin as D  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), '..')

PALETTE = {
    'K': ('#1f2330', '등과 머리 (검정)'), 'k': ('#363c4d', '머리 윗면의 윤기, 감은 눈'),
    'F': ('#2c3140', '날개'), 'f': ('#4a5264', '날개 앞 가장자리'),
    # a step darker than the white outline, so the belly edge does not merge with it
    'w': ('#e3e7ed', '흰 배'), 'x': ('#c2c9d4', '흰 배 그림자, 날개 안쪽'),
    'Y': ('#f6dc8c', '연노랑 가슴'), 'y': ('#f1a833', '귀 옆 주황빛 노랑 무늬'),
    'B': ('#262731', '부리'), 'j': ('#e8844c', '아랫부리 주황 줄'),
    'o': ('#07070a', '눈 (깜빡일 때 바뀜)'),
    'p': ('#34343c', '가까운 발'), 'q': ('#202026', '먼 발'),
    'N': ('#4f6a86', '물고기 등'), 'n': ('#c4d2de', '물고기 배'), 'i': ('#07070a', '물고기 눈'),
    'e': ('#e8eef6', '튀는 눈가루, 테두리 없음'), 'E': ('#aebbd0', '멀어진 눈가루, 테두리 없음'),
    'z': ('#6f9bd1', '잠결 표시 (zzz), 테두리 없음'), 'D': ('#9fd0f0', '털어 낸 물방울, 테두리 없음'),
    # the chick
    'M': ('#26282f', '새끼 검은 모자'), 'W': ('#eceff3', '새끼 흰 얼굴'), 'c': ('#07070a', '새끼 눈'), 'b': ('#26282f', '새끼 부리'),
    'G': ('#9aa0aa', '새끼 회색 솜털'), 'H': ('#7c828d', '새끼 솜털 그림자, 감은 눈'), 'r': ('#4a4d56', '새끼 가까운 발'), 's': ('#373a42', '새끼 먼 발'),
}


def S(name, ticks, dx=None):
    return [name, ticks] if dx is None else [name, ticks, dx]


TICK_MS = 50   # must match the other animals: all share one tick

# The waddle moves 1px a cycle: each foot steps 1px, and the body catches up when the back foot
# comes down (the dx on walk_0), so neither foot slides.
WADDLE = [S('walk_0', 2, 1), S('walk_1', 2), S('walk_2', 2), S('walk_3', 2)]
FLAP = [S('flap_down', 1), S('flap_out', 1), S('flap_up', 2), S('flap_out', 1)]
PEEK_OUT = [S('brood_0', 4), S('brood_1', 2), S('brood_2', 2)]     # the chick's head comes out of the pouch
PEEK_IN = [S('brood_2', 2), S('brood_1', 2), S('brood_0', 4), S('stand', 2)]
BEG = [S('feed_beg_0', 3), S('feed_beg_1', 3)]

ANIMATIONS = {
    # breathing: the body swells 1px and settles
    'idle': {'loop': True, 'seq': [S('idle_0', 12), S('idle_1', 12)]},
    'walk': {'loop': True, 'seq': WADDLE},
    'turn': {'loop': False, 'hold': 0, 'flipAt': 2, 'seq': [S('turn_a', 1), S('turn_b', 2), S('turn_a', 1), S('idle_0', 1)]},
    # belly slide: tip forward onto the belly, then push with flippers and feet (2px a step)
    'slide': {'pose': ['stand', 'sliding'], 'loop': True, 'loopFrom': 3,
              'seq': [S('lean', 3), S('thud', 2), S('belly', 2, 1)] + [S(f'slide_{i}', 2, 2) for i in range(4)]},
    'slide_stop': {'pose': ['sliding', 'stand'], 'loop': False, 'hold': 4,
                   'seq': [S('belly', 2, 2), S('belly', 2, 1), S('belly', 3, 1), S('belly', 12), S('lean', 3), S('stand', 2)]},
    # a trip while waddling: tips over onto the belly, bounces once, lies a moment, gets up
    'fall': {'loop': False, 'hold': 4, 'seq': WADDLE + [S('walk_0', 2, 1), S('walk_1', 2), S('trip', 3), S('lean', 2, 1),
                                                          S('thud', 2), S('belly', 2), S('thud', 1), S('belly', 20), S('lean', 4), S('stand', 2)]},
    'flap': {'loop': False, 'hold': 4, 'seq': [S('idle_0', 4)] + FLAP * 4 + [S('flap_down', 2), S('stand', 2)]},
    # a fish drops from above into the open bill, goes down head first, a bump runs down the
    # throat, and a happy flap
    'eat': {'loop': False, 'hold': 6, 'seq': [
        S('idle_0_up', 6), S('eat_fall_0', 2), S('eat_fall_1', 2), S('eat_fall_2', 2),
        S('eat_gulp_0', 4), S('eat_gulp_1', 4), S('eat_gulp_2', 4), S('idle_0_up', 4),
        S('eat_swallow_0', 4), S('eat_swallow_1', 4), S('idle_0', 6)] + FLAP * 2 + [S('stand', 2)]},
    # the chick peeks out of the brood pouch on its parent's feet, looks up at it, looks around, ducks back
    'brood': {'loop': False, 'hold': 4, 'seq': PEEK_OUT + [S('brood_3', 16), S('brood_up', 10), S('brood_3', 6), S('brood_look', 16),
                                                           S('brood_3', 6)] + PEEK_IN},
    # the chick hops out, begs with its neck stretched up, and is fed bill to bill, twice
    'feed': {'loop': False, 'hold': 4, 'seq': PEEK_OUT + [S('brood_3', 6), S('feed_hop', 3), S('feed_stand', 6)] + BEG * 2
             + [S('feed_give', 8), S('feed_gulp', 6)] + BEG + [S('feed_give', 8), S('feed_gulp', 8), S('feed_stand', 6), S('feed_hop', 3),
                S('brood_3', 6)] + PEEK_IN},
    # waddling with the chick toddling behind
    'walk_chick': {'loop': True, 'seq': [S('follow_0', 2, 1), S('follow_1', 2), S('follow_2', 2), S('follow_3', 2)]},
    # asleep on its feet: the head sinks, the bill rests on the breast, z's rise
    'sleep': {'pose': ['stand', 'sleep'], 'loop': True, 'loopFrom': 1,
              'seq': [S('doze', 8)] + [S(f'sleep_{k}', 16) for k in range(4)]},
    'wake': {'pose': ['sleep', 'stand'], 'loop': False, 'hold': 4, 'seq': [S('doze', 6), S('stand', 4)]},
    # asleep with the chick asleep in the pouch
    'sleep_chick': {'pose': ['stand', 'sleep_chick'], 'loop': True, 'loopFrom': 5,
                    'seq': PEEK_OUT + [S('brood_3', 8), S('doze_chick', 10)] + [S(f'sleep_chick_{k}', 16) for k in range(4)]},
    'wake_chick': {'pose': ['sleep_chick', 'stand'], 'loop': False, 'hold': 4,
                   'seq': [S('doze_chick', 6), S('brood_3', 8)] + PEEK_IN},
    # preening: the head bows deep with the bill in the breast feathers and nibbles (the bowed head
    # bobs 1px), then nibbles under the lifted flipper, and straightens up
    'preen': {'loop': False, 'hold': 4, 'seq': [S('idle_0_down', 3), S('preen_0', 4)] + [S('preen_1', 2), S('preen_0', 2)] * 4
              + [S('preen_0', 3), S('preen_wing_0', 4)] + [S('preen_wing_1', 2), S('preen_wing_0', 2)] * 3
              + [S('preen_0', 3), S('idle_0_down', 3), S('stand', 2)]},
    # shaking off: a fast shiver with the flippers out, drops flying
    'shake': {'loop': False, 'hold': 4, 'seq': [S('idle_0', 4)] + [S('shake_0', 1), S('shake_1', 1)] * 8 + [S('stand', 3)]},
}

TRANSITIONS = {
    'sliding': {'stand': ['slide_stop']},
    'sleep': {'stand': ['wake']},
    'sleep_chick': {'stand': ['wake_chick']},
}

LOOK = {
    'animations': ['idle'],
    # the eye of the standing penguin; angles are measured from here
    'headCenter': [D.PX + 8, D.GROUND - len(D.STAND) + 1 + 3],
    # degrees toward the side the penguin faces: 90 = straight up, -90 = straight down
    'sectors': [{'dir': 'up', 'min': 60}, {'dir': 'up_fwd', 'min': 20}, {'dir': 'fwd', 'min': -20},
                {'dir': 'down_fwd', 'min': -60}, {'dir': 'down', 'min': -90}],
    'deadZone': 5,
    'turnMargin': 3,
    'frames': {d: {f'idle_{i}': f'idle_{i}_{d}' for i in range(2)} for d in D.LOOK_DIRS},
}

# on the black head a closed eye shows as a sheen-grey line
BLINK = {'animations': ['idle'], 'eye': 'o', 'closed': 'k', 'everyTicks': [50, 120], 'forTicks': 2, 'doubleChance': 0.25}

PLANNED = []

REACTIONS = {
    'alert': ['flap'], 'curious': ['brood'], 'greet': ['brood', 'flap'], 'wake': ['shake', 'flap'],
    'sleepy': ['sleep_chick'], 'celebrate': ['slide', 'flap'], 'busy': ['eat', 'feed'], 'wander': ['walk_chick'],
}
IDLE_VARIANTS = ['preen', 'brood', 'shake', 'fall']
CHICK_FRAMES = ('chick_',)    # the chick on its own (stand, waddle): used to build the chick scenes


def main():
    frames_all = D.frames()
    order = ['stand']
    for a in ANIMATIONS.values():
        for step in a['seq']:
            if step[0] not in order:
                order.append(step[0])
    order += [n for n in frames_all if n not in order and not n.startswith(CHICK_FRAMES)]
    J = lambda v: json.dumps(v, ensure_ascii=False)
    out = ['{', '  "name": "penguin",', '  "displayName": "황제펭귄",', '  "version": 1,',
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
    out += ['  },', f'  "transitions": {J(TRANSITIONS)},', f'  "look": {J(LOOK)},', '  "outline": {"skip": ["e", "E", "z", "D"]},',
            f'  "blink": {J(BLINK)},', f'  "planned": {J(PLANNED)},', f'  "idleVariants": {J(IDLE_VARIANTS)},', '  "reactions": {']
    items = list(REACTIONS.items())
    out += [f'    {J(k)}: {J(v)}' + (',' if i < len(items) - 1 else '') for i, (k, v) in enumerate(items)]
    out += ['  }', '}']
    text = '\n'.join(out) + '\n'
    json.loads(text)
    with open(os.path.join(ROOT, 'sprites', 'penguin.json'), 'w') as f:
        f.write(text)
    print(f'wrote sprites/penguin.json: {len(order)} frames, {len(ANIMATIONS)} animations')


if __name__ == '__main__':
    main()
