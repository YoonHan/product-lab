"""Writes sprites/hamster.json from the frames in draft_hamster.py.

Run this only while every hamster frame still comes from the generator.
After frames are edited by hand in sprites/hamster.json, edit that file directly.

Usage: python3 tools/assemble_hamster.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import draft_hamster as D  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), '..')

PALETTE = {
    'a': ('#b8a998', '털 밝음'), 'b': ('#9a8a79', '털 기본'), 'c': ('#7d6e60', '털 어두움'),
    'd': ('#4e433b', '털 가장 어두움 (등 줄무늬, 귀)'), 'w': ('#f4efe8', '흰 배'), 'x': ('#d6ccc1', '흰 배 그림자'),
    'n': ('#e3a7a7', '귀 안쪽'), 'e': ('#d9848c', '코'), 'r': ('#e9b4ae', '볼터치'),
    'o': ('#171213', '눈 위 (깜빡일 때 털 색)'), 'v': ('#171213', '눈 아래 (깜빡일 때 감은 눈 선)'),
    # the tail is a step darker than the belly: in pure white it merges with the white outline
    # and the 2x2 pompom reads twice its size
    't': ('#cbbfb2', '방울 꼬리 (흰 테두리와 섞이지 않게 한 단계 어둡게)'), 'u': ('#a39688', '방울 꼬리 그림자'),
    'p': ('#efd6cf', '가까운 발'), 'q': ('#d2b6ae', '먼 발'), 'j': ('#e0a09a', '들어 올린 앞발'),
    'i': ('#b8505a', '입 안 (하품)'), 'g': ('#fbf6e9', '앞니, 해바라기씨 줄무늬'), 's': ('#3e3a36', '해바라기씨'), 'k': ('#8c8278', '씨앗 껍질 부스러기, 테두리 없음'),
    'z': ('#6f9bd1', '잠결 표시 (zzz), 테두리 없음'),
    'y': ('#e6d6b4', '톱밥'), 'h': ('#c2a87c', '톱밥 결, 그늘'), 'm': ('#9c845c', '톱밥 더미 아랫면'),
    'W': ('#c3dbe6', '쳇바퀴 뒤판'), 'S': ('#7aa0b6', '쳇바퀴 살'), 'R': ('#557b95', '쳇바퀴 테'), 'H': ('#f2f6f8', '쳇바퀴 축'),
    'F': ('#7d8c96', '쳇바퀴 받침대'),
    'f': ('#eadcbd', '날아가는 대팻밥, 테두리 없음'), 'l': ('#c2a87c', '날아가는 대팻밥 그늘, 테두리 없음'),
}


def S(name, ticks, dx=None):
    return [name, ticks] if dx is None else [name, ticks, dx]


TICK_MS = 50   # must match the fox: all animals share one tick

# Sniffing: the head flicks up about 20 degrees and back, quickly, twice in a row.
FLICK = [S('sniff_0', 1), S('sniff_1', 1), S('sniff_0', 1), S('idle_0', 1)]
REAR_FLICK = [S('rear_um', 1), S('rear_up', 1), S('rear_um', 1), S('rear_0', 1)]
RISE = [S('sit_a', 2), S('sit_b', 2), S('sit_0', 2), S('rear_mid', 2)]
PEEK = [S('peek_0', 3), S('peek_1', 3), S('peek_2', 14), S('peek_left', 10), S('peek_2', 5), S('peek_right', 10),
        S('peek_2', 8), S('peek_1', 3), S('peek_0', 3)]
ANIMATIONS = {
    # breathing: a short breath in, a longer rest breathed out
    'idle': {'loop': True, 'seq': [S('idle_0', 10), S('idle_1', 6)]},
    'walk': {'loop': True, 'moveX': 0.5, 'seq': [S(f'walk_{i}', 2) for i in range(4)]},
    'sit': {'pose': ['stand', 'sit'], 'loop': False, 'hold': 40, 'seq': [S('sit_a', 2), S('sit_b', 2), S('sit_0', 2)]},
    'sit_up': {'pose': ['sit', 'stand'], 'loop': False, 'hold': 4, 'seq': [S('sit_b', 2), S('sit_a', 2), S('idle_0', 2)]},
    # stand up on the hind legs, sniff, turn the face to the viewer and back, sniff, come down
    'rear_look': {'loop': False, 'hold': 4, 'seq': [
        *RISE, S('rear_0', 6), *REAR_FLICK * 2, S('rear_0', 6),
        S('rear_q', 2), S('rear_front', 12), S('rear_q', 2), S('rear_0', 6), *REAR_FLICK * 2, S('rear_0', 4),
        *RISE[::-1], S('idle_0', 2)]},
    # turning around: three-quarter view toward the viewer, face-on, then three-quarter the other way (0.25s)
    'turn': {'loop': False, 'hold': 0, 'flipAt': 2, 'seq': [S('turn_a', 1), S('turn_b', 2), S('turn_a', 1), S('idle_0', 1)]},
    'run': {'pose': ['stand', 'running'], 'loop': True, 'moveX': 1.5, 'seq': [S(f'run_{i}', 1) for i in range(4)]},
    'run_stop': {'pose': ['running', 'stand'], 'loop': False, 'hold': 4,
                 'seq': [S('walk_1', 2, 1), S('walk_2', 2, 1), S('walk_3', 3), S('idle_0', 2)]},
    'lie_down': {'pose': ['stand', 'lie'], 'loop': False, 'hold': 60, 'seq': [S('lie_a', 3), S('lie_0', 3)]},
    'lie_up': {'pose': ['lie', 'stand'], 'loop': False, 'hold': 4, 'seq': [S('lie_a', 3), S('idle_0', 2)]},
    # falling asleep: eyes shut, head bowed, curl into a ball, then breathe slowly while z's rise (repeats from step 3)
    'curl_sleep': {'pose': ['lie', 'curl'], 'loop': True, 'loopFrom': 3,
                   'seq': [S('lie_shut', 8), S('curl_half', 6), S('curl_0', 10), *[S(f'sleep_{i}', 2) for i in range(16)]]},
    # waking: the head comes out of the ball, then the body unrolls onto the belly
    'uncurl': {'pose': ['curl', 'lie'], 'loop': False, 'seq': [S('curl_0', 4), S('curl_half', 5), S('lie_shut', 4), S('lie_0', 4)]},
    # a long stretch and a big yawn (mouth at most 2 rows), then back
    'stretch': {'loop': False, 'hold': 6, 'seq': [
        S('stretch_0', 2), S('stretch_1', 4), S('stretch_2', 3),
        S('yawn_0', 2), S('yawn_1', 3), S('yawn_2', 12), S('yawn_1', 3), S('yawn_0', 2),
        S('stretch_2', 3), S('stretch_1', 4), S('stretch_0', 2), S('idle_0', 2)]},
    # washing the face: paws to the mouth, then rub over the nose and up over the eyes, three strokes
    'groom': {'pose': ['sit', 'sit'], 'loop': False, 'hold': 20, 'seq': [
        S('groom_0', 3), *[S(f, 2) for f in ('groom_1', 'groom_2', 'groom_1', 'groom_0')] * 3, S('sit_0', 4)]},
    # a sunflower seed: pick it up, nibble, turn it, nibble, stuff it into the cheek pouch, chew
    'eat_seed': {'pose': ['sit', 'sit'], 'loop': False, 'hold': 20, 'seq': [
        S('eat_look', 8), S('eat_pick', 4), S('eat_up', 3), S('eat_0', 3),
        *[S('eat_1', 1), S('eat_0', 1), S('eat_1', 1), S('eat_2', 1)] * 3, S('eat_0', 4),
        *[S('eat_half_1', 1), S('eat_half', 1)] * 5, S('eat_half', 3), S('eat_push', 4), S('eat_puff', 6),
        *[S('eat_chew', 2), S('eat_puff', 2)] * 4, S('eat_puff', 10), S('sit_0', 4)]},
    # digging into the bedding: the paws scratch, shavings fly, and the heaps at the nose and
    # behind the rump grow a step every stroke cycle
    'dig': {'pose': ['stand', 'digging'], 'loop': False, 'hold': 6,
            'seq': [S(f'dig_{c}_{i}', 2) for c in range(len(D.DIG_HEAPS)) for i in range(4)]},
    'dig_end': {'pose': ['digging', 'stand'], 'loop': False, 'hold': 4, 'seq': [S('dig_end_0', 3), S('dig_end_1', 3), S('idle_0', 2)]},
    # burrowing in: the pile rises over the hamster until only the mound is left
    'burrow_in': {'pose': ['digging', 'burrow'], 'loop': False, 'hold': 0,
                  'seq': [S('burrow_0', 3), S('burrow_1', 3), S('burrow_2', 3), S('mound_0', 4)]},
    # hidden: the mound breathes, and now and then the face pokes out and looks around
    'hide': {'pose': ['burrow', 'burrow'], 'loop': True, 'loopFrom': 0, 'seq': [
        *[S('mound_0', 10), S('mound_1', 10)] * 3, *PEEK]},
    'peek': {'pose': ['burrow', 'burrow'], 'loop': False, 'hold': 4, 'seq': [*PEEK, S('mound_0', 4)]},
    # coming out: the face, then the body pushes up and the pile slumps and scatters
    'emerge': {'pose': ['burrow', 'stand'], 'loop': False, 'hold': 4, 'seq': [
        S('emerge_peek_0', 2), S('emerge_peek_1', 2), S('emerge_peek_2', 4), S('emerge_0', 3), S('emerge_1', 3), S('emerge_2', 3), S('emerge_3', 3), S('idle_0', 2)]},
    # running in the wheel: step in, start slowly, full speed, slow down, stop, step out
    'wheel': {'loop': False, 'hold': 4, 'seq': [
        S('wheel_stand_0', 8),
        *[S(f'wheel_run_{n % 4}_{n % 8}', 2) for n in range(8)],
        *[S(f'wheel_run_{n % 4}_{3 * n % 8}', 1) for n in range(48)],     # full speed: 16.9 degrees a tick
        *[S(f'wheel_run_{n % 4}_{n % 8}', 2) for n in range(8)],
        S('wheel_stand_0', 3), S('wheel_stand_1', 4), S('wheel_stand_1', 8), S('idle_0', 2)]},
    'sniff': {'loop': False, 'hold': 4, 'seq': [S('idle_0', 2), *FLICK * 2]},
}

TRANSITIONS = {
    'running': {'stand': ['run_stop']},
    'sit': {'stand': ['sit_up']},
    'lie': {'stand': ['lie_up']},
    'curl': {'lie': ['uncurl']},
    'digging': {'stand': ['dig_end'], 'burrow': ['burrow_in']},
    'burrow': {'stand': ['emerge']},
    'stand': {'sit': ['sit'], 'lie': ['lie_down'], 'digging': ['dig']},
}

LOOK = {
    'animations': ['idle'],
    # the eye of the standing hamster; angles are measured from here
    'headCenter': list(D.S(11, 3)),
    # degrees toward the side the hamster faces: 90 = straight up, -90 = straight down
    'sectors': [{'dir': 'up', 'min': 60}, {'dir': 'up_fwd', 'min': 20}, {'dir': 'fwd', 'min': -20},
                {'dir': 'down_fwd', 'min': -60}, {'dir': 'down', 'min': -90}],
    'deadZone': 4,      # px around the head where the hamster keeps its current look (smaller than the fox's head)
    'turnMargin': 3,    # px the cursor must pass behind the hamster before it turns around
    'frames': {d: {f'idle_{i}': f'idle_{i}_{d}' for i in range(2)} for d in D.LOOK_DIRS},
}

BLINK = {'animations': ['idle'], 'swap': {'o': 'a', 'v': 'd'}, 'everyTicks': [50, 120], 'forTicks': 2, 'doubleChance': 0.25}

# Animations still to draw. Reactions may name them already; the player skips them until they exist.
PLANNED = []

REACTIONS = {
    'alert': ['rear_look'], 'curious': ['sniff', 'rear_look'], 'greet': ['rear_look', 'groom'], 'wake': ['stretch', 'wheel'],
    'sleepy': ['lie_down', 'curl_sleep'], 'celebrate': ['run', 'eat_seed'], 'busy': ['dig', 'hide'], 'wander': ['walk'],
}
IDLE_VARIANTS = ['sniff', 'groom', 'rear_look']


def main():
    frames_all = D.frames()
    order = ['stand']
    for a in ANIMATIONS.values():
        for step in a['seq']:
            if step[0] not in order:
                order.append(step[0])
    order += [n for n in frames_all if n not in order]
    J = lambda v: json.dumps(v, ensure_ascii=False)
    out = ['{', '  "name": "hamster",', '  "displayName": "드워프 햄스터 (정글리안)",', '  "version": 1,', '  "inProgress": true,',
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
    out += ['  },', f'  "transitions": {J(TRANSITIONS)},', f'  "look": {J(LOOK)},', '  "outline": {"skip": ["z", "f", "l", "k"]},', f'  "blink": {J(BLINK)},', f'  "planned": {J(PLANNED)},',
            f'  "idleVariants": {J(IDLE_VARIANTS)},', '  "reactions": {']
    items = list(REACTIONS.items())
    out += [f'    {J(k)}: {J(v)}' + (',' if i < len(items) - 1 else '') for i, (k, v) in enumerate(items)]
    out += ['  }', '}']
    text = '\n'.join(out) + '\n'
    json.loads(text)
    with open(os.path.join(ROOT, 'sprites', 'hamster.json'), 'w') as f:
        f.write(text)
    print(f'wrote sprites/hamster.json: {len(order)} frames, {len(ANIMATIONS)} animations')


if __name__ == '__main__':
    main()
