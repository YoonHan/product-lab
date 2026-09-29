"""Writes sprites/arctic-fox.json: the fox in its white winter coat, with short rounded ears
and a 1px shorter snout, as arctic foxes have.

The frames come from the fox generator (draft_fox.py, fox_poses.py) with a few head drawings
replaced in the source text before it runs, so fixes to the fox reach the arctic fox too.
Every replacement must match exactly once, or nothing is written. Animations, timing, look
and reactions are the fox's (assemble_fox.py).

Usage: python3 tools/assemble_arctic_fox.py
"""
import importlib.util
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))

# (old, new) replacements in the source text; every one must match exactly once
POSES_EDITS = [
    # the head block reused by sit, bow, itch, lie...: no ear tips, snout 1px shorter
    ('    "....d..k.....",\n', '    ".............",\n'),
    ('    ".cbbbbbbobbbb",\n', '    ".cbbbbbbobbb.",\n'),
    ('    "ccbbbbbbbbbbe",\n', '    "ccbbbbbbbbbe.",\n'),
    # three-quarter head in the turn: no ear tips (the face itself already suits the short snout)
    ("    (22, 22, 'd'), (22, 27, 'k'),\n", ''),
    # face-on head: no ear tips
    ("    (22, 15, 'k'), (22, 25, 'k'),\n", ''),
    # curled up: the laid-back ear loses its tip
    ("    (19, 24, 'd'),\n", ''),
]
DRAFT_EDITS = [
    ("    (2, 25, 'd'), (2, 28, 'k'), (3, 24, 'dd')", "    (3, 24, 'dd')"),
    ("(8, 22, 'cbbbbbbobbbb'),", "(8, 22, 'cbbbbbbobbb'),"),
    ("(9, 21, 'ccbbbbbbbbbbe'),", "(9, 21, 'ccbbbbbbbbbe'),"),
    # the nose that RotSprite places by hand, and the lick tongue, sit 1px further back
    ("(x0 + 12, y0 + 8, 'e')", "(x0 + 11, y0 + 8, 'e')"),
    ("nose_x, nose_y = HX + 12, HY + 7", "nose_x, nose_y = HX + 11, HY + 7"),
    # listen: the short ears perk up by one rounded row, and swivel back from there
    ("up = edit(up, [(HX + 4, HY - 2, 'd'), (HX + 7, HY - 2, 'k')])",
     "up = edit(up, [(HX + 3, HY - 1, 'd'), (HX + 4, HY - 1, 'd'), (HX + 6, HY - 1, 'k'), (HX + 7, HY - 1, 'k')])"),
    ("near_tip, far_tip = (HX + 7, HY - 2), (HX + 4, HY - 2)", "near_tip, far_tip = (HX + 7, HY - 1), (HX + 4, HY - 1)"),
    # yawn: the open mouth moves back with the nose; 'm' is the dark mouth (the red fox reused
    # its dark leg colour 'k', which is pale on the arctic fox)
    ("    out['yawn_0'] = edit(out['stretch_2'], shut + [(x, 37, 'k') for x in range(32, 36)] +\n"
     "                         [(31, 38, 'w'), (32, 38, 'w'), (33, 38, 'w'), (34, 38, 'x')])",
     "    out['yawn_0'] = edit(out['stretch_2'], shut + [(x, 37, 'm') for x in range(31, 35)] +\n"
     "                         [(30, 38, 'w'), (31, 38, 'w'), (32, 38, 'w'), (33, 38, 'x')])"),
    ("    out['yawn_1'] = edit(out['stretch_2'], shut + [(x, 37, 'k') for x in range(32, 36)] +\n"
     "                         [(31, 38, 'w'), (32, 38, 't'), (33, 38, 't'), (34, 38, 'w'), (35, 38, 'x')])",
     "    out['yawn_1'] = edit(out['stretch_2'], shut + [(x, 37, 'm') for x in range(31, 35)] +\n"
     "                         [(30, 38, 'w'), (31, 38, 't'), (32, 38, 't'), (33, 38, 'w'), (34, 38, 'x')])"),
    ("    out['yawn_2'] = edit(out['stretch_2'], shut + [(x, 37, 'k') for x in range(32, 37)] +\n"
     "                         [(31, 38, 'w'), (32, 38, 'k'), (33, 38, 't'), (34, 38, 't'), (35, 38, 'k')] +\n"
     "                         [(32, 39, 'w'), (33, 39, 'w'), (34, 39, 'w'), (35, 39, 'x')])",
     "    out['yawn_2'] = edit(out['stretch_2'], shut + [(x, 37, 'm') for x in range(31, 36)] +\n"
     "                         [(30, 38, 'w'), (31, 38, 'm'), (32, 38, 't'), (33, 38, 't'), (34, 38, 'm')] +\n"
     "                         [(31, 39, 'w'), (32, 39, 'w'), (33, 39, 'w'), (34, 39, 'x')])"),
]

# Winter coat: every fur colour a cool white one step darker than the white outline, so the
# silhouette still reads; legs, paws and the ear backs are white too, only the eyes and nose stay dark.
PALETTE = {
    'a': ('#e6eaef', '털 밝음'), 'b': ('#d9dfe6', '털 기본'), 'c': ('#c1cad5', '털 어두움'),
    'd': ('#a6b2c0', '털 가장 어두움 (귀 뒤, 꼬리 경계)'), 'w': ('#eaeef2', '가슴·꼬리 끝'), 'x': ('#cdd4dd', '가슴 그림자'),
    'k': ('#cdd4dd', '가까운 다리'), 'l': ('#aeb9c6', '먼 다리'), 'e': ('#171213', '코'), 'o': ('#171213', '눈 (깜빡일 때 바뀜)'),
    'p': ('#dde2e8', '가까운 발'), 'q': ('#bcc6d1', '먼 발'),
    't': ('#c9575a', '혀'), 'm': ('#4a3a3c', '입 안 (하품)'), 'z': ('#6f9bd1', '잠결 표시 (zzz), 테두리 없음'), 'y': ('#7c5b40', '흙 (땅 파기)'),
}


def load(name, edits):
    src = open(os.path.join(TOOLS, name + '.py')).read()
    for old, new in edits:
        n = src.count(old)
        if n != 1:
            sys.exit(f'{name}.py: {n} matches for {old!r}; update the replacements in assemble_arctic_fox.py')
        src = src.replace(old, new)
    mod = importlib.util.module_from_spec(importlib.util.spec_from_loader(name, loader=None))
    mod.__file__ = os.path.join(TOOLS, name + '.py')
    sys.modules[name] = mod           # later imports of this module get the arctic version
    exec(compile(src, mod.__file__, 'exec'), mod.__dict__)
    return mod


def trim_nose_nubs(fr):
    """A turned head can leave one snout pixel past the hand-placed nose; drop it so the nose
    is the tip again."""
    out = {}
    for name, rows in fr.items():
        g = [list(r) for r in rows]
        for y, r in enumerate(g):
            for x, ch in enumerate(r):
                if ch == 'e' and x + 2 < len(r) and y + 1 < len(g):
                    if r[x + 1] in 'abc' and r[x + 2] == '.' and g[y + 1][x + 1] == '.':
                        r[x + 1] = '.'
        out[name] = [''.join(r) for r in g]
    return out


def main():
    load('fox_poses', POSES_EDITS)
    D = load('draft_fox', DRAFT_EDITS)
    sys.path.insert(0, TOOLS)
    import assemble_fox as A          # imports the arctic draft_fox loaded above
    frames = {k: [''.join(r) if not isinstance(r, str) else r for r in v] for k, v in D.frames().items()}
    A.write('arctic-fox', '북극여우', 1, PALETTE, trim_nose_nubs(frames))


if __name__ == '__main__':
    main()
