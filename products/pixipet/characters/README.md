# Pixipet 캐릭터

Pixipet 앱이 화면에 띄우는 픽셀 아트 동물의 스프라이트와 애니메이션입니다. 레퍼런스 영상의 픽셀 아트 강아지를 분석해서 스타일 규칙을 정하고, 스프라이트를 코드(팔레트 + 문자 격자)로 작성합니다. `playground/2026-09-28-pixel-animals/`에서 시작한 실험을 2026-09-28에 이 프로덕트로 옮겼습니다.

## 파일

| 경로 | 내용 |
|---|---|
| `../../../playground/2026-09-28-pixel-animals/report.html` | 레퍼런스 분석과 재현 방법 보고서. **로컬에만 있고 저장소에는 올리지 않습니다** (아래 레퍼런스 참고) |
| `style-guide.md` | 우리 에셋의 제작 규칙 (해상도, 색, 테두리, 애니메이션, 데이터 형식, 이벤트 연결) |
| `docs/fox-design-log.md` | 여우 작업 기록: 원하는 느낌, 처음 구현한 내용, 수정 요청과 원인·조치. 다음 동물을 만들기 전에 먼저 읽습니다 |
| `docs/prompts.md` | 여우 작업에 사용한 프롬프트 원문 |
| `sprites/<동물>.json` | 스프라이트 원본 데이터. 직접 편집하는 파일입니다 |
| `events.json` | OS 이벤트 → 반응(reaction) 연결. 동물과 무관합니다 |
| `tools/build.mjs` | 데이터를 검증하고 `dist/`를 생성합니다 |
| `tools/draft_fox.py`, `tools/fox_poses.py` | 여우 프레임 생성기와 손으로 그린 키 포즈 |
| `tools/assemble_fox.py` | 생성한 프레임과 동작 정의로 `sprites/fox.json`을 씁니다. 프레임을 손으로 고친 뒤에는 실행하지 않습니다 |
| `tools/render_video.py` | 모든 동작을 한 번씩 이어 붙인 소개 영상을 `dist/fox-all-animations.mp4`로 만듭니다. Pillow와 ffmpeg가 필요합니다 |
| `viewer.html` | 재생, 배율, 배경, 테두리, 격자, 어니언 스킨, 이벤트 시뮬레이터를 갖춘 뷰어 |
| `dist/` | 생성 결과: 뷰어 번들(`pet-data.js`), PNG 시트(테두리 없음·있음), 앱용 `*.sheet.json` |

## 작업 흐름

```sh
# sprites/*.json 또는 events.json을 고친 뒤
node tools/build.mjs
open viewer.html
```

`dist/`는 생성 파일이므로 직접 수정하지 않습니다. 빌드는 행 길이, 팔레트에 없는 문자, 없는 프레임 참조, 정의되지 않은 반응을 검사하고, 오류가 있으면 아무 파일도 쓰지 않습니다.

## 진행 상황

- 여우: **완성**(2026-09-28). 12개 동작 (`idle`, `walk`, `run`, `sit`, `lie_down`, `stretch`, `pounce`, `listen`, `curl_sleep`, `dig`, `lick`, `itch`)과 전환 동작 5개(`sit_up`, `lie_up`, `uncurl`, `dig_end`, `run_stop`). 돌아서기(`turn`). IDLE 마우스 추적(돌아서기 + 머리 5방향)과 눈 깜빡임. 50ms 틱, 119프레임. 달리기는 IK 다리의 8프레임 갤럽, 점프는 공중 구간 11프레임과 머리가 박힌 뒤 빼내는 동작, 기지개에는 하품이 있습니다. 소개 영상은 해 질 녘 배경과 패럴랙스 스크롤을 씁니다.
- 이벤트: 시스템 9개, 앱 3개(포모도로 타이머 2개, 클릭), 외부 2개(Claude Code 훅).

## 레퍼런스

- 영상: https://youtu.be/FE5FZ0nPXAc (Luiz Melo, "Dogs pack - Pixel Art Assets for GameDev")
- 에셋: https://luizmelo.itch.io/pet-dogs-pack (유료)
- `report.html`에는 분석을 위해 영상에서 복원한 프레임 데이터가 들어 있습니다. 이 프레임은 유료 에셋의 일부이므로 프로덕트에 쓰거나 따라 그리지 않습니다. 그래서 이 파일은 `.gitignore`에 넣어 로컬에만 두고, 저장소에는 올리지 않습니다.
