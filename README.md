## main에 커밋되었을 때 트리거되는 워크플로우 탐색

`repository_dispatch`로 메인에 커밋을 남기는 `commit.yaml`을 트리거해도 `after-commit-on-main-pat-token.yaml`이 트리거되지 않는다. 
권한 문제인가 싶어 `commit.yaml`에서 기존에 사용하던 기본 GITHUB_TOKEN 말고 권한을 가진 PAT_TOKEN도 사용해 봤지만 메인 커밋 후 트리거되어야 할 다른 워크플로우가 트리거되지 않았다.

main에 push가 아니라 특정 워크플로우를 listening 하는 워크플로우인 `after-commit-on-main-wrofklow-run.yaml`은 `commit.yaml`이 종료되었을 때 정상적으로 트리거되었다.