"""Hand-drawn fox key poses on the 40x30 canvas (absolute coordinates).

Each pose is a list of (row, start column, pixels). Poses reuse the head
block from the standing fox so the face stays identical across animations.
"""

# Head block of the standing fox: 13 columns x 9 rows, placed by its top-left corner.
HEAD = [
    "....d..k.....",
    "...dd.kk.....",
    "...dcdkbk....",
    "..dccbbab....",
    "..cbbaaaab...",
    "..cbbaaaabb..",
    ".cbbbbbbobbbb",
    "ccbbbbbbbbbbe",
    "...wwwwwwwx..",
]
STAND_HEAD_AT = (24, 10)   # (x, y) of the head block in the standing pose


def head(x, y, rows=HEAD):
    return [(y + i, x, r.replace('.', ' ')) for i, r in enumerate(rows)]


SIT_BODY = [
    # tail lying on the ground behind the haunch
    (25, 7, 'cbbbb'),
    (26, 4, 'xcbbbbbbc'),
    (27, 2, 'wxccbbbbbc'),
    (28, 2, 'wwxccccccd'),
    (29, 3, 'wwxxccccdd'),
    # neck and back slope down from the head to the haunch
    (15, 21, 'cbbb'),
    (16, 20, 'cbbbbwwwwwwx'),
    (17, 19, 'cbbbbbwwwwwx'),
    (18, 18, 'caabbbbwwwwx'),
    (19, 16, 'caaabbbbbwwwx'),
    (20, 14, 'caaaabbbbbbwwx'),
    (21, 13, 'cbaaabbbbbbbwwx'),
    (22, 12, 'ccbbbbbbbbbbc'),
    (23, 12, 'ccbbbbbbbbbc'),
    (24, 12, 'dccbbbbbbbc'),
    (25, 12, 'dccbbbbbbcc'),
    (26, 12, 'ddccbbbccc'),
    (27, 13, 'ddcccccd'),
]
# far front leg sits just behind the near one; both 2px
SIT_FAR_FRONT = [(22, 24, 'dl')] + [(y, 24, 'll') for y in range(23, 29)] + [(29, 23, 'qqq')]
SIT_HIND_FOOT = [(28, 15, 'kkkk'), (29, 15, 'kkkkpp')]
SIT_NEAR_FRONT = [(22, 27, 'ck')] + [(y, 27, 'kk') for y in range(23, 29)] + [(29, 27, 'ppp')]
SIT = SIT_BODY + SIT_FAR_FRONT + SIT_HIND_FOOT + SIT_NEAR_FRONT + head(22, 7)


LIE = [
    # tail on the ground behind
    (25, 5, 'cbbbb'), (26, 2, 'xcbbbbbc'), (27, 0, 'wxccbbbbc'), (28, 0, 'wwxcccccd'), (29, 1, 'wwxxcccdd'),
    # body resting on the ground, back line slightly rounded
    (21, 13, 'caaaaaaab'),
    (22, 10, 'cbbaabbbbbbbbbbwwx'),
    (23, 9, 'ccbbbbbbbbbbbbbbwwwx'),
    (24, 9, 'ccbbbbbbbbbbbbbbwwwx'),
    (25, 9, 'cccbbbbbbbbbbbbbwwx'),
    (26, 9, 'dcccbbbbbbbbbbbcwwx'),
    (27, 10, 'ddcccxxxxxxcccwwx'),
    (28, 11, 'dddccxxxxxxccx'),
    # neck: fur at the back, cream throat joining the jaw to the chest
    (21, 22, 'bbwww'), (22, 28, 'wwx'), (23, 29, 'x'),   # throat curves from the chin into the chest
    # elbow: the upper foreleg comes out of the chest, then the forearm lies flat
    (28, 25, 'x'), (27, 27, 'ck'),
    # folded hind foot, far front paw, near front paw stretched forward
    (29, 12, 'kkkpp'),
    (29, 28, 'llllqq'),
    (28, 26, 'ckkkpp'), (29, 27, 'kkkpp'),
] + head(24, 13)

CURL = [
    # body curled into a dome
    (20, 13, 'caaaaaab'),
    (21, 11, 'cbaaaaaaaabb'),
    (22, 10, 'cbbbbbbbbbbbc'),
    (23, 9, 'ccbbbbbbbbbbbc'),
    (24, 9, 'ccbbbbbbbbbbc'),
    (25, 9, 'cccbbbbbbbbbc'),
    (26, 9, 'dcccbbbbbbbcc'),
    (27, 9, 'ddcccccccccd'),
    # head resting at the front: ear laid back, eyes closed
    (19, 24, 'd'),
    (20, 23, 'dd'),
    (21, 23, 'dcbba'),
    (22, 22, 'dcbbaaab'),
    (23, 22, 'cbbbbbbbb'),
    (24, 22, 'cbbeebbbbb'),
    (25, 22, 'ccbbbbbbbb'),
    (26, 22, 'dccbbbbbb'),
    # tail wraps along the bottom and its white tip covers the nose
    (27, 21, 'cbbbbbbb'),
    (28, 10, 'ddcccbbbbbbbbbbbbbbbwx'),
    (29, 11, 'dddcccccccccccccxxww'),
    (25, 31, 'ww'), (26, 30, 'xwww'), (27, 29, 'bxwww'),
]

BOW = [
    # tail raised behind the high rump, white tip up
    (12, 4, 'ww'), (13, 3, 'wwxc'), (14, 3, 'wxcbb'), (15, 4, 'ccbbb'), (16, 6, 'cbbb'),
    # back slopes from the high rump down to the chest on the ground
    (16, 10, 'caaab'),
    (17, 9, 'cbbaaaab'),
    (18, 9, 'ccbbbbaaab'),
    (19, 9, 'cccbbbbbbaab'),
    (20, 10, 'cccbbbbbbbbaab'),
    (21, 10, 'dccbbbbbbbbbbab'),
    (22, 11, 'dcxxbbbbbbbbbbb'),
    (23, 13, 'xxxbbbbbbbbbwww'),
    (24, 17, 'xxbbbbbbwwww'),
    (25, 20, 'xxbbbbwwwwx'),
    (26, 23, 'xbbwwwwx'),
    # thigh: the rump comes down over both hind legs so they stay joined to the body
    (20, 9, 'd'), (21, 8, 'dd'), (22, 8, 'ddc'),
    # hind legs straight, front legs flat on the ground reaching forward
    (22, 8, 'dl'), (23, 8, 'll'), (24, 8, 'll'), (25, 8, 'll'), (26, 8, 'll'), (27, 8, 'll'), (28, 8, 'll'), (29, 8, 'qqq'),
    (23, 11, 'kk'), (24, 11, 'kk'), (25, 11, 'kk'), (26, 11, 'kk'), (27, 11, 'kk'), (28, 11, 'kk'), (29, 11, 'ppp'),
    (29, 29, 'llllqq'),
    (27, 27, 'ckkpp'), (28, 28, 'kkkkpp'),
] + head(25, 17)

def itch(foot_dy=0):
    # near hind leg lifted to the neck; the paw sits over the cream chest so it reads as a leg
    leg = [(17 + foot_dy, 24 - foot_dy, 'ppp'), (18 + foot_dy, 23 - foot_dy, 'kk'), (19, 22, 'kk'), (20, 21, 'kk'),
           (21, 20, 'kk'), (22, 19, 'ckk')]
    return SIT_BODY + SIT_FAR_FRONT + SIT_NEAR_FRONT + leg + head(22, 8)


ITCH = itch()


# ---- turning toward the viewer (absolute coordinates on the 40x42 canvas, ground = row 41) ----

FRONT = [
    # tail peeks out on one side, resting on the ground
    (38, 27, 'bbb'), (39, 26, 'cbbbb'), (40, 26, 'ccbbww'), (41, 27, 'xwww'),
    # hind legs behind the front legs, at the sides
    (36, 14, 'cc'), (37, 14, 'dl'), (38, 14, 'll'), (39, 14, 'll'), (40, 14, 'll'), (41, 14, 'qq'),
    (36, 25, 'cc'), (37, 25, 'ld'), (38, 25, 'll'), (39, 25, 'll'), (40, 25, 'll'), (41, 25, 'qq'),
    # ears, face, cream muzzle
    (22, 15, 'k'), (22, 25, 'k'),
    (23, 15, 'kd'), (23, 24, 'dk'),
    (24, 15, 'kdc'), (24, 23, 'cdk'),
    (25, 15, 'dcbbbbbbbcd'),
    (26, 14, 'cbbaaaaaaabbc'),
    (27, 14, 'cbbaaaaaaabbc'),
    (28, 14, 'cbbobbbbbobbc'),
    (29, 14, 'cwwwbbbbbwwwc'),
    (30, 16, 'xwwwewwwx'),
    (31, 17, 'xwwwwwx'),
    # neck and cream chest
    (32, 15, 'cbbwwwwwbbc'),
    (33, 14, 'cbbbwwwwwbbbc'),
    (34, 14, 'cbbbwwwwwbbbc'),
    (35, 14, 'ccbbxwwwxbbcc'),
    # front legs
    (36, 17, 'ck'), (37, 17, 'kk'), (38, 17, 'kk'), (39, 17, 'kk'), (40, 17, 'kk'), (41, 16, 'ppp'),
    (36, 22, 'kc'), (37, 22, 'kk'), (38, 22, 'kk'), (39, 22, 'kk'), (40, 22, 'kk'), (41, 22, 'ppp'),
]

THREE_QUARTER = [
    # tail hangs behind the short, foreshortened body
    (33, 8, 'cbb'), (34, 5, 'xcbbbb'), (35, 4, 'wxccbbc'), (36, 4, 'wwxccc'), (37, 5, 'wwx'),
    # body seen at an angle
    (31, 13, 'cbaaaaaab'),
    (32, 12, 'cbbbbbbbbbw'), (32, 23, 'wwwwx'),
    (33, 11, 'ccbbbbbbbbbw'), (33, 23, 'wwwwx'),
    (34, 11, 'ccbbbbbbbbbbwwwwx'),
    (35, 11, 'cccbbbbbbbbbwwx'),
    (36, 12, 'dccxxxxxbbbwx'),
    # legs: far hind, near hind, far front, near front
    (37, 12, 'dl'), (38, 12, 'll'), (39, 12, 'll'), (40, 12, 'll'), (41, 12, 'qqq'),
    (37, 15, 'ck'), (38, 15, 'kk'), (39, 15, 'kk'), (40, 15, 'kk'), (41, 15, 'ppp'),
    (37, 21, 'dl'), (38, 21, 'll'), (39, 21, 'll'), (40, 21, 'll'), (41, 21, 'qqq'),
    (37, 24, 'ck'), (38, 24, 'kk'), (39, 24, 'kk'), (40, 24, 'kk'), (41, 24, 'ppp'),
    # head turned toward the viewer: both eyes show, 4px apart (6px face-on), and the nose sits
    # below between them, nearer the far eye, with the muzzle 1px out on the right. A nose
    # beyond both eyes mixes a side-view nose with face-on eyes.
    (22, 22, 'd'), (22, 27, 'k'),
    (23, 21, 'dd'), (23, 26, 'kk'),
    (24, 21, 'dcd'), (24, 26, 'kbk'),
    (25, 21, 'dcbbbbab'),
    (26, 20, 'cbbaaaaabb'),
    (27, 20, 'cbbaaaaabbb'),
    (28, 20, 'cbbobbbobbb'),
    (29, 20, 'cwwwbbbwwwwc'),
    (30, 21, 'xwwwwwewx'),
    (31, 22, 'xwwwwx'),
]
