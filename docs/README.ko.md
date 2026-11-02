<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# AtomCode Daily

**AtomCode의 현재 플랜을 확인하고, 유효한 플랜이 없을 때 Max → Pro → Lite 순서로 무료 CodingPlan을 자동 수령합니다.**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

<img src="https://img.shields.io/github/v/release/L0NE-6/AtomCode-Daily?style=for-the-badge&label=Release&color=2ea44f&logo=github" />
<img src="https://img.shields.io/github/stars/L0NE-6/AtomCode-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" />
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />

</div>

> 전체 중국어 문서는 [../README.md](../README.md)에서 확인하세요.

## ✨ 핵심 기능

- `status-v2`를 읽고 유효한 플랜이 있으면 중복 수령하지 않습니다.
- `Max → Pro → Lite` 순서로 시도하며 첫 성공에서 중지합니다.
- 파싱 가능한 `expires_at`을 `remaining_days`보다 우선하여 만료된 플랜을 다시 수령 대상으로 처리합니다.
- `duplicate: true`는 이미 보유한 것으로 처리하여 하위 플랜으로 내려가지 않습니다.
- access token 만료 시 자동 갱신하고 교체된 refresh token을 저장합니다.
- 다중 계정, 프록시, PushPlus, Bark, WeCom, DingTalk 알림을 지원합니다.

## 🚀 최단 설정

저장소 루트에서 실행합니다.

```bash
python -m pip install -r requirements.txt
python atomcode_auth.py --file path/to/auth.toml
```

단일 계정:

```text
ATOMCODE_TOKEN=ACCESS_TOKEN
ATOMCODE_REFRESH_TOKEN=REFRESH_TOKEN
```

다중 계정:

```text
ATOMCODE_TOKENS=
메인|ACCESS_TOKEN|REFRESH_TOKEN|1799999999000
서브|ACCESS_TOKEN|REFRESH_TOKEN
```

상태만 확인:

```bash
python atomcode_daily.py --query
```

일반 실행:

```bash
python atomcode_daily.py
python atomcode_daily.py --only 1
python atomcode_daily.py --no-notify
```

## 🐧 Qinglong

```bash
pip3 install requests
```

패널 환경 변수에 `ATOMCODE_TOKENS`를 설정하고 작업을 만듭니다.

```text
20 8 * * * python3 atomcode_daily.py
```

갱신된 토큰은 `atomcode_state.json`에 저장됩니다. 쓰기 가능한 영구 디렉터리를 사용하고 필요하면 `ATOMCODE_STATE_FILE`로 경로를 지정하세요.

## ☁️ GitHub Actions

워크플로는 [../.github/workflows/daily.yml](../.github/workflows/daily.yml)입니다. 현재는 수동 실행만 제공되며 일정 부분은 주석 처리되어 있습니다.

| Secret | 필수 | 용도 |
| :--- | :---: | :--- |
| `ATOMCODE_TOKENS` | 둘 중 하나 | 다중 계정 토큰 |
| `ATOMCODE_TOKEN` | 둘 중 하나 | 단일 계정 access token |
| `ATOMCODE_REFRESH_TOKEN` | 선택 | 단일 계정 refresh token |
| `ATOMCODE_PROXY` | 선택 | 프록시 |
| `PLUSPLUS_TOKEN` / `BARK_URL` / `WECOM_WEBHOOK` / `DINGTALK_WEBHOOK` | 선택 | 알림 |

정기 실행을 사용하려면 주석을 해제하세요. GitHub cron은 UTC 기준입니다. Actions는 로컬 상태 파일을 유지하지 않으므로 refresh token이 교체되면 Secret을 갱신해야 합니다.

## 🔧 주요 환경 변수

| 변수 | 설명 |
| :--- | :--- |
| `ATOMCODE_TOKENS` | 다중 계정: `이름\|access\|refresh\|expires_at\|created_at\|expires_in` |
| `ATOMCODE_TOKEN` | 단일 계정 access token |
| `ATOMCODE_REFRESH_TOKEN` | 단일 계정 refresh token |
| `ATOMCODE_EXPIRES_AT` | 타임스탬프 또는 파싱 가능한 날짜/시간 |
| `ATOMCODE_AUTH_FILE` | JSON auth 파일 경로 |
| `ATOMCODE_STATE_FILE` | 토큰 상태 파일 경로 |
| `ATOMCODE_PROXY` | HTTP(S) / SOCKS 프록시 |
| `ATOMCODE_NO_NOTIFY` | `1`이면 알림 비활성화 |

## 📊 성공 기준

유효한 플랜, `success: true` 또는 `duplicate: true`를 이번 실행의 성공으로 봅니다. 세 플랜 모두 거부되거나 토큰이 없거나 선택한 계정이 없으면 실패입니다. HTTP 200만으로 성공을 판단하지 않습니다.

## 🔒 개인정보

- 계정 데이터를 수집하거나 업로드하지 않습니다.
- 로그에 전체 토큰을 출력하지 않습니다.
- `atomcode_state.json`, `.env`, access token, refresh token을 Git에 커밋하지 마세요.
- 자격 증명은 로컬 환경 변수, GitHub Secrets 또는 Qinglong 환경 변수에만 보관하세요.

## 사용 범위 및 재배포 안내

공식 저장소, 스크립트, 배포 설명 및 Release 다운로드는 무료입니다. 유료 패키징, 유료 배포 대행, 회원 전용화, 재판매, 저작자 표시 삭제, 저작자 사칭, 저작자의 신원이나 QR 코드를 보증처럼 사용하는 행위, 무관한 계정·그룹·채널로 옮겨 트래픽을 유도하는 행위는 허용되지 않습니다. 위반 콘텐츠는 삭제 요청될 수 있으며, 저작자는 업데이트를 중단하거나 저장소를 보관 또는 삭제할 수 있습니다. 전체 규칙은 [../NOTICE.md](../NOTICE.md)를 참고하세요.

## 🔗 링크

- [Releases](https://github.com/L0NE-6/AtomCode-Daily/releases)
- [Issues](https://github.com/L0NE-6/AtomCode-Daily/issues)
- [Changelog](../CHANGELOG.md)
- [License](../LICENSE)
