# Pixipet 캐릭터

Pixipet 앱이 화면에 띄우는 픽셀 아트 동물의 스프라이트와 애니메이션입니다. 레퍼런스 영상의 픽셀 아트 강아지를 분석해서 스타일 규칙을 정하고, 스프라이트를 코드(팔레트 + 문자 격자)로 작성합니다. `playground/2026-09-28-pixel-animals/`에서 시작한 실험을 2026-09-28에 이 프로덕트로 옮겼습니다.

## 파일

| 경로 | 내용 |
|---|---|
| `../../../playground/2026-09-28-pixel-animals/report.html` | 레퍼런스 분석과 재현 방법 보고서. **로컬에만 있고 저장소에는 올리지 않습니다** (아래 레퍼런스 참고) |
| `style-guide.md` | 우리 에셋의 제작 규칙 (해상도, 색, 테두리, 애니메이션, 데이터 형식, 이벤트 연결) |
| `docs/preferences.md` | 여러 동물을 만들며 받은 피드백을 주제별로 모은 원하는 스타일과 작업 방식. 새 동물을 만들기 전에 먼저 읽습니다 |
| `docs/fox-design-log.md` | 여우 작업 기록: 원하는 느낌, 처음 구현한 내용, 수정 요청과 원인·조치. 다음 동물을 만들기 전에 먼저 읽습니다 |
| `docs/prompts.md` | 여우 작업에 사용한 프롬프트 원문 |
| `docs/hamster-design-log.md` | 햄스터 작업 기록: 햄스터에서 새로 알게 된 원하는 느낌, 수정 요청과 원인·조치, 확인을 기다리는 동작 |
| `docs/hamster-prompts.md` | 햄스터 작업에 사용한 프롬프트 원문 |
| `docs/dachshund-design-log.md` | 닥스훈트 작업 기록: 코기와 구분되게 살린 특징, 수정 요청과 원인·조치 |
| `docs/dachshund-prompts.md` | 닥스훈트 작업에 사용한 프롬프트 원문 |
| `docs/shiba-design-log.md` | 시바견 작업 기록: 사진을 기준으로 잡은 비율, 뼈 마디가 있는 다리, 수정 요청과 원인·조치 |
| `docs/shiba-prompts.md` | 시바견 작업에 사용한 프롬프트 원문 |
| `docs/lab-design-log.md` | 래브라도 작업 기록: 대형견 비율, 입과 턱, 뼈 마디 다리, 수정 요청과 원인·조치 |
| `docs/lab-prompts.md` | 래브라도 작업에 사용한 프롬프트 원문 |
| `docs/beagle-design-log.md` | 비글 작업 기록: 안장 무늬, 오목한 스톱과 흰 줄, 기본 머리에서 만든 동작용 머리, 수정 요청과 원인·조치 |
| `docs/beagle-prompts.md` | 비글 작업에 사용한 프롬프트 원문 |
| `docs/collie-design-log.md` | 보더콜리 작업 기록: 정면을 먼저 확정하고 측면을 맞춘 머리, 양몰이 자세, 수정 요청과 원인·조치 |
| `docs/collie-prompts.md` | 보더콜리 작업에 사용한 프롬프트 원문 |
| `docs/corgi-design-log.md` | 웰시코기 작업 기록: 귀여운 비율로 다시 그린 과정, 수정 요청과 원인·조치 |
| `docs/corgi-prompts.md` | 웰시코기 작업에 사용한 프롬프트 원문 |
| `docs/penguin-design-log.md` | 펭귄 작업 기록: 황제펭귄과 새끼 디자인, 수정 요청과 원인·조치, 다음에 정할 동작 |
| `docs/penguin-prompts.md` | 펭귄 작업에 사용한 프롬프트 원문 |
| `docs/arctic-fox-design-log.md` | 북극여우 작업 기록: 여우에서 바꾼 털색과 머리 모양, 수정 요청과 원인·조치 |
| `docs/arctic-fox-prompts.md` | 북극여우 작업에 사용한 프롬프트 원문 |
| `sprites/<동물>.json` | 스프라이트 원본 데이터. 직접 편집하는 파일입니다 |
| `events.json` | OS 이벤트 → 반응(reaction) 연결. 동물과 무관합니다 |
| `tools/build.mjs` | 데이터를 검증하고 `dist/`를 생성합니다 |
| `tools/draft_fox.py`, `tools/fox_poses.py` | 여우 프레임 생성기와 손으로 그린 키 포즈 |
| `tools/draft_hamster.py` | 햄스터 프레임 생성기. 핵심 자세와 머리는 손으로 그린 문자 격자이고, 나머지 프레임은 이 격자를 바꿔 만듭니다 |
| `tools/draft_dachshund.py` | 닥스훈트 프레임 생성기. 코기와 같은 방식(손으로 그린 몸과 머리, 코드로 그린 다리) |
| `tools/assemble_dachshund.py` | 생성한 프레임과 동작 정의로 `sprites/dachshund.json`을 씁니다 |
| `tools/draft_shiba.py` | 시바견 프레임 생성기. 손으로 그린 몸과 머리, 길이가 고정된 뼈 두 개와 발로 코드가 그리는 다리 |
| `tools/assemble_shiba.py` | 생성한 프레임과 동작 정의로 `sprites/shiba.json`을 씁니다 |
| `tools/assemble_shiba_black.py` | 적색 시바의 프레임에 색만 바꾸고 눈 둘레에 황갈색을 넣어 `sprites/shiba-black.json`(흑갈색 시바)을 씁니다. 적색 시바를 고친 뒤 다시 실행합니다 |
| `tools/draft_lab.py` | 래브라도 프레임 생성기. 코드로 그린 몸, 손으로 그린 머리, 3px 뼈 마디 다리, 목을 축으로 돌리는 머리, 밑동을 축으로 흔들리는 귀 |
| `tools/assemble_lab.py` | 생성한 프레임과 동작 정의로 `sprites/lab.json`을 씁니다 |
| `tools/draft_beagle.py` | 비글 프레임 생성기. 코드로 그린 몸과 안장 무늬, 손으로 그린 머리, 2px 뼈 마디 다리, 기울이고 숙이는 머리, 밑동을 축으로 흔들리는 귀 |
| `tools/assemble_beagle.py` | 생성한 프레임과 동작 정의로 `sprites/beagle.json`을 씁니다 |
| `tools/draft_collie.py` | 보더콜리 프레임 생성기. 옆모습 레퍼런스의 실루엣 위에 손으로 다듬은 몸, 손으로 그린 머리, 3px 뼈 마디 다리(웅크린 자세에서는 몸만 기울이고 다리는 땅까지 따로 굽힘), 기울이고 숙이는 머리, 프리스비 |
| `tools/assemble_collie.py` | 생성한 프레임과 동작 정의로 `sprites/collie.json`을 씁니다 |
| `tools/draft_corgi.py` | 웰시코기 프레임 생성기. 몸, 머리 방향, 돌아서기, 앉기는 손으로 그린 문자 격자이고, 다리는 코드로 그립니다 |
| `tools/assemble_corgi.py` | 생성한 프레임과 동작 정의로 `sprites/corgi.json`을 씁니다 |
| `tools/draft_penguin.py` | 황제펭귄(과 새끼) 프레임 생성기. 기본 자세와 머리 방향, 돌아서기, 썰매, 날개는 손으로 그린 문자 격자입니다 |
| `tools/assemble_penguin.py` | 생성한 프레임과 동작 정의로 `sprites/penguin.json`을 씁니다 |
| `tools/assemble_hamster.py` | 생성한 프레임과 동작 정의로 `sprites/hamster.json`을 씁니다 |
| `tools/assemble_fox.py` | 생성한 프레임과 동작 정의로 `sprites/fox.json`을 씁니다. 프레임을 손으로 고친 뒤에는 실행하지 않습니다 |
| `tools/assemble_arctic_fox.py` | 여우 생성기의 머리 그림 몇 군데를 바꿔 실행하고, 여우의 동작 정의로 `sprites/arctic-fox.json`을 씁니다. 여우를 고친 뒤에도 다시 실행합니다 |
| `tools/render_video.py` | 모든 동작을 한 번씩 이어 붙인 소개 영상을 만듭니다. `python3 tools/render_video.py fox`, `arctic-fox`, `penguin`, `corgi`, `dachshund`, `shiba`, `shiba-black`, `lab`, `beagle`, `collie`, `hamster`로 동물을 고르며, 결과는 `dist/<동물>-all-animations.mp4`입니다. 동물마다 무대가 다릅니다(여우: 해 질 녘 들판, 북극여우: 눈 내린 홋카이도, 펭귄: 백야의 남극 해빙, 웰시코기: 소가 풀을 뜯는 목장 가장자리 잔디밭, 닥스훈트: 단풍잎이 떨어지는 가을 숲 가장자리, 시바견과 흑갈색 시바: 꽃잎이 휘날리는 봄의 벚꽃 산책로, 래브라도: 파스텔 톤의 교외 뒷마당, 비글: 풍차가 도는 미국 시골 농장, 보더콜리: 등대가 보이는 웨일스 바닷가 절벽 초원, 햄스터: 저녁의 사육장). 동물 뒤에 무대 이름을 붙이면 다른 무대로 만듭니다(`hamster beach` → `dist/hamster-all-animations-beach.mp4`, 파도치는 모래사장). 햄스터 영상은 모래사장 무대를 쓰고, 사육장 무대(`hamster`)는 코드에만 남아 있습니다. Pillow, numpy, ffmpeg가 필요합니다 |
| `viewer.html` | 재생, 배율, 배경, 테두리, 격자, 어니언 스킨, 이벤트 시뮬레이터를 갖춘 뷰어 |
| `dist/` | 생성 결과: 뷰어 번들(`pet-data.js`), PNG 시트(테두리 없음·있음), 앱용 `*.sheet.json` |

## 작업 흐름

```sh
# sprites/*.json 또는 events.json을 고친 뒤 (햄스터는 python3 tools/assemble_hamster.py, 펭귄은 assemble_penguin.py, 코기는 assemble_corgi.py, 닥스훈트는 assemble_dachshund.py, 시바견은 assemble_shiba.py와 assemble_shiba_black.py, 래브라도는 assemble_lab.py, 비글은 assemble_beagle.py, 보더콜리는 assemble_collie.py,
# 여우를 고쳤으면 python3 tools/assemble_arctic_fox.py 먼저)
node tools/build.mjs
open viewer.html
```

`dist/`는 생성 파일이므로 직접 수정하지 않습니다. 빌드는 행 길이, 팔레트에 없는 문자, 없는 프레임 참조, 정의되지 않은 반응을 검사하고, 오류가 있으면 아무 파일도 쓰지 않습니다.

## 진행 상황

- 여우: **완성**(2026-09-28). 12개 동작 (`idle`, `walk`, `run`, `sit`, `lie_down`, `stretch`, `pounce`, `listen`, `curl_sleep`, `dig`, `lick`, `itch`)과 전환 동작 5개(`sit_up`, `lie_up`, `uncurl`, `dig_end`, `run_stop`). 돌아서기(`turn`). IDLE 마우스 추적(돌아서기 + 머리 5방향)과 눈 깜빡임. 50ms 틱, 119프레임. 달리기는 IK 다리의 8프레임 갤럽, 점프는 공중 구간 11프레임과 머리가 박힌 뒤 빼내는 동작, 기지개에는 하품이 있습니다. 소개 영상은 해 질 녘 배경과 패럴랙스 스크롤을 씁니다.
- 북극여우: **완성**(2026-09-29). 여우의 프레임 119개와 동작을 그대로 쓰고, 겨울털(흰색), 짧고 둥근 귀, 한 칸 짧은 주둥이로 바꿨습니다. 소개 영상 `dist/arctic-fox-all-animations.mp4`(눈 내린 홋카이도: 요테이산, 가문비나무와 자작나무, 도리이와 석등).
- 닥스훈트(블랙탄): **완성**(2026-09-30). 늘어진 귀, 가는 주둥이, 긴 꼬리, 긴 소시지 몸, 프레임 50×28, 11개 동작(`idle`, `walk`, `run`/`run_stop`, `turn`, `sit`/`sit_up`, `lie_down`/`lie_up`, `burrow`, `wag`), 36프레임. 소개 영상 `dist/dachshund-all-animations.mp4`(가을 숲 가장자리, 45초).
- 시바견(적색): **완성**(2026-09-30). 실제 시바 사진을 기준으로 잡은 정사각형 몸, 둥근 귀, 크림색 눈썹과 우라지로, 엉덩이 위에 말린 꼬리, 뼈 마디가 있는 다리, 프레임 38×24, 13개 동작(`idle`, `walk`, `run`/`run_stop`, `turn`, `sit`/`sit_up`, `lie_down`/`lie_up`, `refuse`, `mikaeri`, `smile`, `shake`), 43프레임. 흑갈색 시바는 적색이 완성된 뒤 같은 그림에 색만 바꿔 추가합니다. 소개 영상 `dist/shiba-all-animations.mp4`(벚꽃 산책로, 52초).
- 흑갈색 시바: **완성**(2026-09-30). 적색 시바와 같은 그림과 13개 동작에 색만 바꿨습니다(검은 털, 황갈색 다리, 크림색 우라지로). 검은 머리에서 눈이 보이도록 눈 둘레(감은 눈, 스마일 눈 포함)에만 황갈색을 넣었습니다. 43프레임. 소개 영상 `dist/shiba-black-all-animations.mp4`(벚꽃 산책로).
- 래브라도 리트리버(노란색): **완성**(2026-09-30). 대형견다운 짧고 깊은 주둥이와 두툼한 목·가슴, 3px 뼈 마디 다리와 큰 발, 긴 늘어진 귀, 수달 꼬리, 프레임 54×34, 12개 동작(`idle`, `walk`, `run`/`run_stop`, `turn`, `sit`/`sit_up`, `lie_down`/`lie_up`, `wag`, `show`(노란 오리 장난감), `splash`), 39프레임. 소개 영상 `dist/lab-all-animations.mp4`(파스텔 톤의 교외 뒷마당, 48초).
- 비글(삼색): **완성**(2026-10-01). 등을 덮는 검은 안장 무늬, 황갈색 머리와 귀, 이마에서 주둥이로 이어지는 흰 줄, 오목한 스톱, 끝이 흰 깃발 꼬리, 흰 앞다리, 2px 뼈 마디 다리, 프레임 52×28, 13개 동작(`idle`, `walk`, `run`/`run_stop`, `turn`, `sit`/`sit_up`, `lie_down`/`lie_up`, `scent`, `howl`, `shake`, `steal`), 58프레임. 소개 영상 `dist/beagle-all-animations.mp4`(미국 시골 농장, 59초).
- 보더콜리(블랙 앤 화이트): **완성**(2026-10-02). 래브라도보다 조금 작은 몸과 작은 머리, 뒤로 살짝 접히는 귀와 분홍색 귀 안쪽, 정수리에서 주둥이로 이어지는 1칸 흰 줄, 눈을 감싸는 눈두덩, 웃는 입, 흰 가슴털, 3px 뼈 마디 다리(팔꿈치와 발목 아래는 흰색), 프레임 96×48(날아오는 프리스비를 위한 여백 포함), 12개 동작(`idle`, `walk`, `run`/`run_stop`, `turn`, `sit`/`sit_up`, `lie_down`/`lie_up`, `herd`, `chin`, `frisbee`), 50프레임. 소개 영상 `dist/collie-all-animations.mp4`(웨일스 바닷가 절벽 초원, 58초).
- 웰시코기: **완성**(2026-09-29). 몸 약 28×20px(머리와 귀를 크게 키운 귀여운 비율), 프레임 44×26, 13개 동작(`idle`, `walk`, `run`/`run_stop`, `turn`, `sit`/`sit_up`, `lie_down`(스플루트)/`lie_up`, `bark`, `roll`, `spin`, `fetch`), 45프레임. 소개 영상 `dist/corgi-all-animations.mp4`(목장 가장자리 잔디밭).
- 황제펭귄: **완성**(2026-09-29). 몸 13×19px(부리와 발 포함), 프레임 38×32, 17개 동작, 68프레임. 부모: `idle`, `walk`, `turn`, `slide`/`slide_stop`, `fall`, `flap`, `eat`, `preen`, `shake`, `sleep`/`wake`. 새끼(회색 솜털)가 나오는 동작: `brood`, `feed`, `walk_chick`, `sleep_chick`/`wake_chick`. 소개 영상 `dist/penguin-all-animations.mp4`(백야의 남극 해빙, 73초).
- 햄스터(정글리안): **완성**(2026-09-29). 몸 13×10px, 프레임 26×28, 23개 동작, 157프레임. 소개 영상 `dist/hamster-all-animations-beach.mp4`(모래사장). 모든 동작을 확인했습니다.
- 이벤트: 시스템 9개, 앱 3개(포모도로 타이머 2개, 클릭), 외부 2개(Claude Code 훅).

## 레퍼런스

- 영상: https://youtu.be/FE5FZ0nPXAc (Luiz Melo, "Dogs pack - Pixel Art Assets for GameDev")
- 에셋: https://luizmelo.itch.io/pet-dogs-pack (유료)
- `report.html`에는 분석을 위해 영상에서 복원한 프레임 데이터가 들어 있습니다. 이 프레임은 유료 에셋의 일부이므로 프로덕트에 쓰거나 따라 그리지 않습니다. 그래서 이 파일은 `.gitignore`에 넣어 로컬에만 두고, 저장소에는 올리지 않습니다.
