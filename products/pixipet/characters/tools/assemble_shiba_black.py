"""Writes sprites/shiba-black.json: the black and tan shiba, the red shiba's frames recoloured.

The drawing and every animation are the red shiba's (draft_shiba.py, assemble_shiba.py); only the
palette changes, plus tan around the eyes: a black eye on a black head vanished, so each eye (open,
shut or smiling) sits on a tan patch, as on a real black and tan shiba. The cream urajiro stays
cream and meets the black directly.

Usage: python3 tools/assemble_shiba_black.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import draft_shiba as D  # noqa: E402
import assemble_shiba as A  # noqa: E402

PALETTE = dict(A.PALETTE)
PALETTE.update({
    'b': ('#2b2426', '털 기본 (검은색)'), 'a': ('#4a3f41', '털 밝음 (검은 털의 윤기)'), 'c': ('#1d1819', '털 어두움'),
    'd': ('#120e0f', '털 가장 어두움, 감은 눈 선, 입'),
    'n': ('#e9d8c4', '귀 안쪽'),
    'k': ('#c78848', '가까운 다리 (황갈색)'), 'l': ('#a26a34', '먼 다리 (황갈색)'),
    'T': ('#c78848', '눈 둘레 황갈색'),
})


def tan_eyes(rows):
    """Tan on the black pixels touching an eye: open (o, v), or shut and smiling (d, on the head)."""
    g = [list(r) for r in rows]
    h, w = len(g), len(g[0])

    def near(x, y, keys):
        return any(0 <= x + dx < w and 0 <= y + dy < h and rows[y + dy][x + dx] in keys
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    for y in range(h):
        for x in range(w):
            if rows[y][x] == 'b' and (near(x, y, 'ov') or (x >= D.PX + 9 and y < D.GROUND - 9 and near(x, y, 'd'))):
                g[y][x] = 'T'
    return [''.join(r) for r in g]


if __name__ == '__main__':
    A.main('shiba-black', '흑갈색 시바', PALETTE, {n: tan_eyes(r) for n, r in D.frames().items()})
