<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# AtomCode Daily

**查詢 AtomCode 目前方案，並在沒有有效方案時依 Max → Pro → Lite 自動領取免費 CodingPlan。**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

<img src="https://img.shields.io/github/v/release/L0NE-6/AtomCode-Daily?style=for-the-badge&label=Release&color=2ea44f&logo=github" />
<img src="https://img.shields.io/github/stars/L0NE-6/AtomCode-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" />
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />

</div>

> 完整中文文件請見 [../README.md](../README.md)。

## ✨ 核心能力

- 讀取 `status-v2`，有有效方案時不重複領取。
- 依 `Max → Pro → Lite` 級聯嘗試，命中即停止。
- 可解析的 `expires_at` 優先於 `remaining_days`，過期方案會重新進入領取流程。
- 上游回傳 `duplicate: true` 時視為已持有，避免繼續降級。
- access token 過期時自動續期，並保存輪換後的 refresh token。
- 支援多帳號、代理與 PushPlus、Bark、企業微信、釘釘通知。

## 🚀 最短可行設定

從倉庫根目錄執行：

```bash
python -m pip install -r requirements.txt
python atomcode_auth.py --file path/to/auth.toml
```

單帳號：

```text
ATOMCODE_TOKEN=ACCESS_TOKEN
ATOMCODE_REFRESH_TOKEN=REFRESH_TOKEN
```

多帳號：

```text
ATOMCODE_TOKENS=
主帳號|ACCESS_TOKEN|REFRESH_TOKEN|1799999999000
小號|ACCESS_TOKEN|REFRESH_TOKEN
```

先驗證狀態，再正式領取：

```bash
python atomcode_daily.py --query
python atomcode_daily.py
```

## 🐧 青龍面板

```bash
pip3 install requests
```

在面板設定 `ATOMCODE_TOKENS`，建立任務：

```text
20 8 * * * python3 atomcode_daily.py
```

`atomcode_state.json` 會保存輪換後的令牌；請放在可寫且持久化的目錄，或透過 `ATOMCODE_STATE_FILE` 指定位置。

## ☁️ GitHub Actions

工作流為 [../.github/workflows/daily.yml](../.github/workflows/daily.yml)。目前只保留手動觸發，排程區塊是註解狀態。

必要 Secrets：

| Secret | 必填 | 用途 |
| :--- | :---: | :--- |
| `ATOMCODE_TOKENS` | 二選一 | 多帳號令牌 |
| `ATOMCODE_TOKEN` | 二選一 | 單帳號 access token |
| `ATOMCODE_REFRESH_TOKEN` | 否 | 單帳號 refresh token |
| `ATOMCODE_PROXY` | 否 | 代理 |
| `PLUSPLUS_TOKEN` / `BARK_URL` / `WECOM_WEBHOOK` / `DINGTALK_WEBHOOK` | 否 | 通知 |

若要啟用排程，取消 workflow 中的註解；GitHub cron 使用 UTC。Actions 不保留本地狀態檔案，refresh token 輪換後要更新 Secret。

## 🔧 關鍵環境變數

| 變數 | 說明 |
| :--- | :--- |
| `ATOMCODE_TOKENS` | 多帳號，每行 `備註\|access\|refresh\|expires_at\|created_at\|expires_in` |
| `ATOMCODE_TOKEN` | 單帳號 access token |
| `ATOMCODE_REFRESH_TOKEN` | 單帳號 refresh token |
| `ATOMCODE_EXPIRES_AT` | 到期時間提示，支援時間戳或日期時間字串 |
| `ATOMCODE_AUTH_FILE` | JSON auth 檔案路徑 |
| `ATOMCODE_STATE_FILE` | 令牌狀態檔案路徑 |
| `ATOMCODE_PROXY` | HTTP(S) / SOCKS 代理 |
| `ATOMCODE_NO_NOTIFY` | 設為 `1` 關閉通知 |

## 📊 成功判據

有效方案、`success: true` 或 `duplicate: true` 視為本輪成功；三檔都被拒絕、未設定令牌或指定帳號不存在時返回失敗。只有 HTTP 200 不足以證明領取成功。

## 🔒 隱私

- 不收集或上傳帳號資料。
- 日誌不輸出完整令牌。
- 不要把 `atomcode_state.json`、`.env`、access token 或 refresh token 提交到 Git。
- 只使用本機環境變數、GitHub Secrets 或青龍環境變數保存憑證。

## 🔗 專案連結

- [Releases](https://github.com/L0NE-6/AtomCode-Daily/releases)
- [Issues](https://github.com/L0NE-6/AtomCode-Daily/issues)
- [Changelog](../CHANGELOG.md)
- [License](../LICENSE)
