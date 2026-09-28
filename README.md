# design-by-code-resources

여러 프로덕트(웹/앱 서비스)에서 사용하는 디자인 리소스를 생성하고 관리하는 저장소입니다. 프로덕트들은 서로 독립적인 경우가 많으므로, 리소스를 프로덕트 단위로 분리해서 관리합니다.

## 디렉터리 구조

```
products/
  _template/              새 프로덕트를 만들 때 복사하는 기본 구조
  <product-name>/
    design-system/
      tokens/
        primitive/        원시 값 (color palette, spacing scale, font size 등)
        semantic/         의미 토큰 (color.bg.surface, color.text.primary 등), primitive를 참조
      themes/             테마별 semantic 토큰 오버라이드 (light, dark 등)
      components/         컴포넌트 명세 (anatomy, variant, 사용하는 토큰)
      dist/               빌드 산출물 (CSS 변수, Tailwind, iOS, Android), git에서 제외
    images/
      generated/          생성형 AI로 만든 이미지
      external/           외부에서 가져온 이미지 (스톡, 직접 촬영, 제공받은 이미지)
    svg/
      icons/              UI 아이콘
      logos/              로고, 워드마크
      illustrations/      일러스트, 스팟 그래픽
    poc/                  코드로 작성한 웹 페이지 HTML PoC

scripts/                  저장소 전체에서 사용하는 자동화 스크립트
```

새 프로덕트는 다음 명령으로 만듭니다.

```sh
scripts/new-product.sh <product-name>
```

## 공통 규칙

- **파일/디렉터리 이름**: 소문자 kebab-case를 사용합니다. (`arrow-left.svg`, `hero-banner.png`)
- **프로덕트 간 참조 금지**: 한 프로덕트의 리소스가 다른 프로덕트의 리소스를 참조하지 않도록 합니다. 다른 프로덕트의 리소스가 필요하면 복사해서 사용합니다.
- **프로덕트 내부 참조**: PoC와 컴포넌트 명세는 같은 프로덕트의 토큰과 SVG를 복사하지 말고, 상대 경로로 참조합니다.

## 바이너리 파일 (Git LFS)

이미지, 영상, 폰트, 디자인 원본 파일은 Git LFS로 관리합니다. 추적 대상 확장자는 `.gitattributes`에 정의되어 있습니다. SVG, JSON, HTML처럼 텍스트로 된 파일은 일반 Git으로 관리합니다.

저장소를 새로 받는 환경에서는 한 번만 다음 명령을 실행합니다.

```sh
brew install git-lfs
git lfs install
```

새로운 바이너리 확장자를 추가해야 하면 파일을 커밋하기 전에 `git lfs track "*.<ext>"`를 실행합니다.

## design-system

- 토큰은 [W3C Design Tokens(DTCG)](https://www.designtokens.org/) 형식의 `*.tokens.json` 파일로 작성합니다. 플랫폼에 종속되지 않는 단일 원본을 유지하고, 플랫폼별 결과물은 빌드해서 `dist/`에 생성합니다.
- `semantic` 토큰은 반드시 `primitive` 토큰을 참조(`{color.blue.500}`)하며, 원시 값을 직접 쓰지 않습니다.
- 컴포넌트 코드에서는 `semantic` 토큰만 사용합니다.

## images

이미지마다 같은 이름의 메타데이터 파일(`<name>.meta.yaml`)을 함께 둡니다. 출처와 라이선스를 추적하기 위해서입니다.

```yaml
# images/generated/hero-banner.meta.yaml
source: generated
model: <사용한 모델>
prompt: |
  <생성에 사용한 프롬프트>
created: 2026-09-28
```

```yaml
# images/external/team-photo.meta.yaml
source: external
origin: <원본 URL 또는 제공처>
license: <라이선스 종류, 예: Unsplash License>
attribution: <필요한 경우 표기 문구>
created: 2026-09-28
```

## svg

- `viewBox`를 유지하고, 고정 `width`/`height`는 제거합니다.
- 단색 아이콘은 `fill="currentColor"`를 사용해 색을 외부에서 제어할 수 있도록 합니다.
- 아이콘은 `24x24` 그리드를 기본으로 하고, 다른 크기가 필요하면 `icons/16/`처럼 크기별 디렉터리로 나눕니다.

## poc

PoC마다 독립된 디렉터리를 만들고, 그 안에서 완결되도록 작성합니다.

```
poc/
  2026-09-28-landing-hero/
    index.html
    README.md         목적, 검증하려는 내용, 결론
    assets/           이 PoC에서만 쓰는 리소스
```

- 디렉터리 이름은 `YYYY-MM-DD-<slug>` 형식을 사용해 생성 순서대로 정렬되도록 합니다.
- 같은 프로덕트의 토큰과 SVG는 상대 경로로 참조합니다.
