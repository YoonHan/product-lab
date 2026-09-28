# CLAUDE.md

이 저장소는 여러 독립 프로덕트의 디자인 리소스를 관리하는 저장소입니다. 디렉터리 구조와 리소스별 규칙은 `README.md`에 정의되어 있으며, 리소스를 추가하거나 수정할 때 반드시 따릅니다.

- 프로덕트 리소스는 `products/<product-name>/` 아래에 둡니다. 새 프로덕트는 `scripts/new-product.sh <product-name>`으로 만들고, `products/_template/`에는 리소스를 추가하지 않습니다.
- 한 프로덕트의 리소스가 다른 프로덕트의 리소스를 참조하지 않도록 합니다.
- 특정 프로덕트에 속하지 않는 실험은 `playground/YYYY-MM-DD-<slug>/`에 만들고 `README.md`를 포함합니다.
- 이미지를 추가할 때는 `<name>.meta.yaml` 메타데이터 파일을 함께 작성합니다.
- 새 바이너리 확장자는 커밋 전에 `git lfs track`으로 등록합니다.
- 새 PoC는 `poc/YYYY-MM-DD-<slug>/` 디렉터리에 만들고 `README.md`를 포함합니다.
- 토큰 원본은 `design-system/tokens/`의 DTCG 형식 JSON이며, `design-system/dist/`는 직접 수정하지 않습니다.
