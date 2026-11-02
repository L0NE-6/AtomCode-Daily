<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# AtomCode Daily

**Check the current AtomCode plan and claim a free CodingPlan with a Max → Pro → Lite fallback when no valid plan exists.**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

<img src="https://img.shields.io/github/v/release/L0NE-6/AtomCode-Daily?style=for-the-badge&label=Release&color=2ea44f&logo=github" />
<img src="https://img.shields.io/github/stars/L0NE-6/AtomCode-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" />
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />

</div>

> The complete Chinese documentation is available in [../README.md](../README.md).

## ✨ What it does

- Reads the current CodingPlan state from `status-v2`.
- Treats a plan as active only when its parsed expiry time is still in the future.
- Claims `Max → Pro → Lite` in order and stops at the first confirmed result.
- Stops immediately when the upstream returns `duplicate: true`.
- Refreshes access tokens and stores rotated refresh tokens when a writable state path is available.
- Supports multiple accounts, proxies, and PushPlus, Bark, WeCom, and DingTalk notifications.

## 🚀 Quick start

Run these commands from the repository root:

```bash
python -m pip install -r requirements.txt
python atomcode_auth.py --file path/to/auth.toml
```

`atomcode_auth.py` converts a local AtomCode/AtomGit auth file into the multi-account environment format. You can also fill the environment variable manually:

```text
ATOMCODE_TOKENS=
Main|ACCESS_TOKEN|REFRESH_TOKEN|1799999999000
Alt|ACCESS_TOKEN|REFRESH_TOKEN
```

Validate connectivity without claiming:

```bash
python atomcode_daily.py --query
```

Run the normal claim flow:

```bash
python atomcode_daily.py
python atomcode_daily.py --only 1
python atomcode_daily.py --no-notify
```

## 🐧 Qinglong

```bash
pip3 install requests
```

Set `ATOMCODE_TOKENS` in the panel variable list, then create a task such as:

```text
20 8 * * * python3 atomcode_daily.py
```

If refresh tokens rotate, keep `atomcode_state.json` on a writable and persistent path. `ATOMCODE_STATE_FILE` can point to that path.

## ☁️ GitHub Actions

The workflow is [../.github/workflows/daily.yml](../.github/workflows/daily.yml). It is manual-only by default because the schedule block is intentionally commented out.

Add the required repository secrets:

| Secret | Required | Purpose |
| :--- | :---: | :--- |
| `ATOMCODE_TOKENS` | One of two | Multi-account token records |
| `ATOMCODE_TOKEN` | One of two | Single-account access token |
| `ATOMCODE_REFRESH_TOKEN` | Optional | Refresh token for the single account |
| `ATOMCODE_EXPIRES_AT` | Optional | Access-token expiry hint |
| `ATOMCODE_PROXY` | Optional | HTTP(S) or SOCKS proxy |
| `PLUSPLUS_TOKEN`, `BARK_URL`, `WECOM_WEBHOOK`, `DINGTALK_WEBHOOK` | Optional | Notification channels |

To enable a schedule, uncomment the two schedule lines and remember that GitHub cron uses UTC. The current example is `20 0 * * *`, which is 08:20 in Beijing time. Actions does not persist the local state file; update the refresh-token secret if the upstream rotates it.

## 🔧 Key environment variables

| Variable | Required | Description |
| :--- | :---: | :--- |
| `ATOMCODE_TOKENS` | One of two | Multi-account records: `name\|access\|refresh\|expires_at\|created_at\|expires_in` |
| `ATOMCODE_TOKEN` | One of two | Single-account access token |
| `ATOMCODE_REFRESH_TOKEN` | Optional | Recommended refresh token |
| `ATOMCODE_EXPIRES_AT` | Optional | Millisecond/second timestamp or a parseable date-time string |
| `ATOMCODE_AUTH_FILE` | Optional | JSON auth file path |
| `ATOMCODE_STATE_FILE` | Optional | Rotated-token state file path |
| `ATOMCODE_PROXY` | Optional | HTTP(S) or SOCKS proxy |
| `ATOMCODE_NO_NOTIFY` | Optional | Set to `1` to disable notifications |
| `ATOMCODE_BROKER_BASE` | Advanced | Overrides the default auth broker base URL |
| `ATOMCODE_CODINGPLAN_API_BASE` | Advanced | Overrides the default CodingPlan API base URL |

## 📊 Success and exit codes

- Exit code `0`: the plan is valid, the account already holds a plan, or this run successfully claimed one.
- Exit code `1`: no token was found, the selected account did not exist, or every claim attempt failed.
- A successful HTTP response alone is not treated as a successful claim.

## 🔒 Privacy

- The project does not collect or upload account data.
- Logs mask credentials and never print a complete token.
- Keep `atomcode_state.json` and `.env` out of Git.
- Store tokens only in local environment variables, GitHub Secrets, or a Qinglong environment variable.

## Usage and redistribution

The official repository, scripts, deployment instructions, and Release downloads are free. Paid packaging, paid deployment, membership gating, resale, removal of attribution, impersonation of the author, use of the author's identity or QR codes as endorsement, and reposting to unrelated accounts, groups, or channels for traffic diversion are not permitted. Violations may require removal of the content; the author may pause updates, archive the repository, or delete it. See [../NOTICE.md](../NOTICE.md) for the complete rules.

## 🔗 Project links

- [Releases](https://github.com/L0NE-6/AtomCode-Daily/releases)
- [Issues](https://github.com/L0NE-6/AtomCode-Daily/issues)
- [Changelog](../CHANGELOG.md)
- [License](../LICENSE)
