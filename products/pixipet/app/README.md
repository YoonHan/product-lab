# Pixipet macOS 앱

화면에 픽셀 아트 동물을 띄워 두는 macOS 전용 앱의 소스 코드 자리입니다. 아직 만들지 않았습니다.

- 캐릭터 데이터는 `../characters/dist/`의 결과물(`*.sheet.json`, PNG 시트)을 씁니다. 앱이 원본(`../characters/sprites/`)을 직접 읽지 않도록 합니다.
- 앱이 지켜야 할 규칙(정수배 확대, 흰색 1px 테두리 생성, 틱, 자세 전환, 마우스 추적, OS 이벤트 연결)은 `../characters/style-guide.md`에 있습니다.
- 다른 프로그램이 보내는 이벤트는 URL 스킴 `pixipet://event/<이벤트 id>`로 받습니다.
