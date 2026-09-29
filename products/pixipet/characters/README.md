# Pixipet 캐릭터

Pixipet 앱이 화면에 띄우는 픽셀 아트 동물의 스프라이트와 애니메이션입니다. 레퍼런스 영상의 픽셀 아트 강아지를 분석해서 스타일 규칙을 정하고, 스프라이트를 코드(팔레트 + 문자 격자)로 작성합니다. `playground/2026-09-28-pixel-animals/`에서 시작한 실험을 2026-09-28에 이 프로덕트로 옮겼습니다.

## 파일

| 경로 | 내용 |
|---|---|
| `../../../playground/2026-09-28-pixel-animals/report.html` | 레퍼런스 분석과 재현 방법 보고서. **로컬에만 있고 저장소에는 올리지 않습니다** (아래 레퍼런스 참고) |
| `style-guide.md` | 우리 에셋의 제작 규칙 (해상도, 색, 테두리, 애니메이션, 데이터 형식, 이벤트 연결) |
| `docs/fox-design-log.md` | 여우 작업 기록: 원하는 느낌, 처음 구현한 내용, 수정 요청과 원인·조치. 다음 동물을 만들기 전에 먼저 읽습니다 |
| `docs/prompts.md` | 여우 작업에 사용한 프롬프트 원문 |
| `docs/hamster-design-log.md` | 햄스터 작업 기록: 햄스터에서 새로 알게 된 원하는 느낌, 수정 요청과 원인·조치, 확인을 기다리는 동작 |
| `docs/hamster-prompts.md` | 햄스터 작업에 사용한 프롬프트 원문 |
| `docs/penguin-design-log.md` | 펭귄 작업 기록: 황제펭귄과 새끼 디자인, 수정 요청과 원인·조치, 다음에 정할 동작 |
| `docs/penguin-prompts.md` | 펭귄 작업에 사용한 프롬프트 원문 |
| `docs/arctic-fox-design-log.md` | 북극여우 작업 기록: 여우에서 바꾼 털색과 머리 모양, 수정 요청과 원인·조치 |
| `docs/arctic-fox-prompts.md` | 북극여우 작업에 사용한 프롬프트 원문 |
| `sprites/<동물>.json` | 스프라이트 원본 데이터. 직접 편집하는 파일입니다 |
| `events.json` | OS 이벤트 → 반응(reaction) 연결. 동물과 무관합니다 |
| `tools/build.mjs` | 데이터를 검증하고 `dist/`를 생성합니다 |
| `tools/draft_fox.py`, `tools/fox_poses.py` | 여우 프레임 생성기와 손으로 그린 키 포즈 |
| `tools/draft_hamster.py` | 햄스터 프레임 생성기. 핵심 자세와 머리는 손으로 그린 문자 격자이고, 나머지 프레임은 이 격자를 바꿔 만듭니다 |
| `tools/draft_penguin.py` | 황제펭귄(과 새끼) 프레임 생성기. 기본 자세와 머리 방향, 돌아서기, 썰매, 날개는 손으로 그린 문자 격자입니다 |
| `tools/assemble_penguin.py` | 생성한 프레임과 동작 정의로 `sprites/penguin.json`을 씁니다 |
| `tools/assemble_hamster.py` | 생성한 프레임과 동작 정의로 `sprites/hamster.json`을 씁니다 |
| `tools/assemble_fox.py` | 생성한 프레임과 동작 정의로 `sprites/fox.json`을 씁니다. 프레임을 손으로 고친 뒤에는 실행하지 않습니다 |
| `tools/assemble_arctic_fox.py` | 여우 생성기의 머리 그림 몇 군데를 바꿔 실행하고, 여우의 동작 정의로 `sprites/arctic-fox.json`을 씁니다. 여우를 고친 뒤에도 다시 실행합니다 |
| `tools/render_video.py` | 모든 동작을 한 번씩 이어 붙인 소개 영상을 만듭니다. `python3 tools/render_video.py fox`, `arctic-fox`, `penguin`, `hamster`로 동물을 고르며, 결과는 `dist/<동물>-all-animations.mp4`입니다. 동물마다 무대가 다릅니다(여우: 해 질 녘 들판, 북극여우: 눈 내린 홋카이도, 펭귄: 백야의 남극 해빙, 햄스터: 저녁의 사육장). 동물 뒤에 무대 이름을 붙이면 다른 무대로 만듭니다(`hamster beach` → `dist/hamster-all-animations-beach.mp4`, 파도치는 모래사장). 햄스터 영상은 모래사장 무대를 쓰고, 사육장 무대(`hamster`)는 코드에만 남아 있습니다. Pillow, numpy, ffmpeg가 필요합니다 |
| `viewer.html` | 재생, 배율, 배경, 테두리, 격자, 어니언 스킨, 이벤트 시뮬레이터를 갖춘 뷰어 |
| `dist/` | 생성 결과: 뷰어 번들(`pet-data.js`), PNG 시트(테두리 없음·있음), 앱용 `*.sheet.json` |

## 작업 흐름

```sh
# sprites/*.json 또는 events.json을 고친 뒤 (햄스터는 python3 tools/assemble_hamster.py, 펭귄은 assemble_penguin.py,
# 여우를 고쳤으면 python3 tools/assemble_arctic_fox.py 먼저)
node tools/build.mjs
open viewer.html
```

`dist/`는 생성 파일이므로 직접 수정하지 않습니다. 빌드는 행 길이, 팔레트에 없는 문자, 없는 프레임 참조, 정의되지 않은 반응을 검사하고, 오류가 있으면 아무 파일도 쓰지 않습니다.

## 진행 상황

- 여우: **완성**(2026-09-28). 12개 동작 (`idle`, `walk`, `run`, `sit`, `lie_down`, `stretch`, `pounce`, `listen`, `curl_sleep`, `dig`, `lick`, `itch`)과 전환 동작 5개(`sit_up`, `lie_up`, `uncurl`, `dig_end`, `run_stop`). 돌아서기(`turn`). IDLE 마우스 추적(돌아서기 + 머리 5방향)과 눈 깜빡임. 50ms 틱, 119프레임. 달리기는 IK 다리의 8프레임 갤럽, 점프는 공중 구간 11프레임과 머리가 박힌 뒤 빼내는 동작, 기지개에는 하품이 있습니다. 소개 영상은 해 질 녘 배경과 패럴랙스 스크롤을 씁니다.
- 북극여우: **완성**(2026-09-29). 여우의 프레임 119개와 동작을 그대로 쓰고, 겨울털(흰색), 짧고 둥근 귀, 한 칸 짧은 주둥이로 바꿨습니다. 소개 영상 `dist/arctic-fox-all-animations.mp4`(눈 내린 홋카이도: 요테이산, 가문비나무와 자작나무, 도리이와 석등).
- 황제펭귄: **작업 중**(2026-09-29). 몸 13×19px(부리와 발 포함), 프레임 38×32, 17개 동작, 68프레임. 부모: `idle`, `walk`, `turn`, `slide`/`slide_stop`, `fall`, `flap`, `eat`, `preen`, `shake`, `sleep`/`wake`. 새끼(회색 솜털)가 나오는 동작: `brood`, `feed`, `walk_chick`, `sleep_chick`/`wake_chick`. 소개 영상 `dist/penguin-all-animations.mp4`(백야의 남극 해빙, 73초).
- 햄스터(정글리안): **작업 중**(2026-09-29). 몸 13×10px, 프레임 26×28, 23개 동작, 157프레임. 소개 영상 `dist/hamster-all-animations-beach.mp4`(모래사장). 확인 완료: `idle`, `walk`, `sit`, `sit_up`, `sniff`, `rear_look`, `turn`, `lie_down`, `lie_up`, `run`, `run_stop`, `burrow_in`, `hide`, `peek`. 다시 확인 대기: IDLE 마우스 추적(위 방향), `curl_sleep`, `uncurl`, `eat_seed`, `dig`, `dig_end`, `emerge`, `groom`(고개 숙임), 톱밥 더미 모양. 첫 확인 대기: `stretch`, `wheel`.
- 이벤트: 시스템 9개, 앱 3개(포모도로 타이머 2개, 클릭), 외부 2개(Claude Code 훅).

## 레퍼런스

- 영상: https://youtu.be/FE5FZ0nPXAc (Luiz Melo, "Dogs pack - Pixel Art Assets for GameDev")
- 에셋: https://luizmelo.itch.io/pet-dogs-pack (유료)
- `report.html`에는 분석을 위해 영상에서 복원한 프레임 데이터가 들어 있습니다. 이 프레임은 유료 에셋의 일부이므로 프로덕트에 쓰거나 따라 그리지 않습니다. 그래서 이 파일은 `.gitignore`에 넣어 로컬에만 두고, 저장소에는 올리지 않습니다.
