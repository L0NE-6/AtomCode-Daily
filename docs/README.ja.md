<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# AtomCode Daily

**AtomCode の現在のプランを確認し、有効なプランがない場合は Max → Pro → Lite の順で無料 CodingPlan を取得します。**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

<img src="https://img.shields.io/github/v/release/L0NE-6/AtomCode-Daily?style=for-the-badge&label=Release&color=2ea44f&logo=github" />
<img src="https://img.shields.io/github/stars/L0NE-6/AtomCode-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" />
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />

</div>

> 完全な中国語ドキュメントは [../README.md](../README.md) を参照してください。

## ✨ 主な機能

- `status-v2` を読み取り、有効なプランがある場合は重複取得しません。
- `Max → Pro → Lite` の順で試し、最初に成功した時点で停止します。
- 解析可能な `expires_at` を `remaining_days` より優先し、期限切れプランを再取得の対象にします。
- `duplicate: true` は「既に保有」として扱い、下位プランへの移行を防ぎます。
- access token の期限切れ時に自動更新し、ローテーション後の refresh token を保存します。
- 複数アカウント、プロキシ、PushPlus、Bark、WeCom、DingTalk 通知に対応します。

## 🚀 最短セットアップ

リポジトリのルートで実行します。

```bash
python -m pip install -r requirements.txt
python atomcode_auth.py --file path/to/auth.toml
```

単一アカウント：

```text
ATOMCODE_TOKEN=ACCESS_TOKEN
ATOMCODE_REFRESH_TOKEN=REFRESH_TOKEN
```

複数アカウント：

```text
ATOMCODE_TOKENS=
メイン|ACCESS_TOKEN|REFRESH_TOKEN|1799999999000
サブ|ACCESS_TOKEN|REFRESH_TOKEN
```

状態確認のみ：

```bash
python atomcode_daily.py --query
```

通常実行：

```bash
python atomcode_daily.py
python atomcode_daily.py --only 1
python atomcode_daily.py --no-notify
```

## 🐧 Qinglong

```bash
pip3 install requests
```

環境変数 `ATOMCODE_TOKENS` を設定し、次のようなタスクを作成します。

```text
20 8 * * * python3 atomcode_daily.py
```

更新後のトークンは `atomcode_state.json` に保存されます。書き込み可能で永続的なディレクトリを使用し、必要なら `ATOMCODE_STATE_FILE` で保存先を指定してください。

## ☁️ GitHub Actions

ワークフローは [../.github/workflows/daily.yml](../.github/workflows/daily.yml) です。現在は手動実行のみで、スケジュール行はコメントアウトされています。

| Secret | 必須 | 用途 |
| :--- | :---: | :--- |
| `ATOMCODE_TOKENS` | いずれか | 複数アカウントのトークン |
| `ATOMCODE_TOKEN` | いずれか | 単一アカウントの access token |
| `ATOMCODE_REFRESH_TOKEN` | 任意 | 単一アカウントの refresh token |
| `ATOMCODE_PROXY` | 任意 | プロキシ |
| `PLUSPLUS_TOKEN` / `BARK_URL` / `WECOM_WEBHOOK` / `DINGTALK_WEBHOOK` | 任意 | 通知 |

定時実行を有効にする場合はコメントを外します。GitHub の cron は UTC です。Actions はローカル状態ファイルを保持しないため、refresh token がローテーションされた場合は Secret を更新してください。

## 🔧 主な環境変数

| 変数 | 説明 |
| :--- | :--- |
| `ATOMCODE_TOKENS` | 複数アカウント。`名前\|access\|refresh\|expires_at\|created_at\|expires_in` |
| `ATOMCODE_TOKEN` | 単一アカウントの access token |
| `ATOMCODE_REFRESH_TOKEN` | 単一アカウントの refresh token |
| `ATOMCODE_EXPIRES_AT` | タイムスタンプまたは解析可能な日時文字列 |
| `ATOMCODE_AUTH_FILE` | JSON auth ファイルのパス |
| `ATOMCODE_STATE_FILE` | トークン状態ファイルのパス |
| `ATOMCODE_PROXY` | HTTP(S) / SOCKS プロキシ |
| `ATOMCODE_NO_NOTIFY` | `1` で通知を無効化 |

## 📊 成功条件

有効なプラン、`success: true`、または `duplicate: true` を成功として扱います。全プランの取得拒否、トークン未設定、対象アカウントなしは失敗です。HTTP 200 だけでは成功と判定しません。

## 🔒 プライバシー

- アカウントデータを収集・アップロードしません。
- ログに完全なトークンを出力しません。
- `atomcode_state.json`、`.env`、各種トークンを Git にコミットしないでください。
- 認証情報はローカル環境変数、GitHub Secrets、Qinglong の環境変数にだけ保存してください。

## 🔗 リンク

- [Releases](https://github.com/L0NE-6/AtomCode-Daily/releases)
- [Issues](https://github.com/L0NE-6/AtomCode-Daily/issues)
- [Changelog](../CHANGELOG.md)
- [License](../LICENSE)
