<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# 🧬 AtomCode Daily

**探测 AtomCode 当前套餐，并在没有有效套餐时按 Max → Pro → Lite 自动领取免费 CodingPlan。**

[简体中文](README.md) | [English](docs/README.en.md) | [繁體中文](docs/README.zh-Hant.md) | [日本語](docs/README.ja.md) | [한국어](docs/README.ko.md) | [Português (BR)](docs/README.pt-BR.md)

<a href="https://github.com/L0NE-6/AtomCode-Daily/releases"><img src="https://img.shields.io/github/v/release/L0NE-6/AtomCode-Daily?style=for-the-badge&label=Release&color=2ea44f&logo=github" alt="Release" /></a>
<img src="https://img.shields.io/github/stars/L0NE-6/AtomCode-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" alt="Stars" />
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/%E9%9D%92%E9%BE%99-Ready-4EAA25?style=for-the-badge" alt="Qinglong" />
<a href="https://github.com/L0NE-6/AtomCode-Daily/actions/workflows/daily.yml"><img src="https://img.shields.io/github/actions/workflow/status/L0NE-6/AtomCode-Daily/daily.yml?branch=main&style=for-the-badge&label=Actions&logo=githubactions&logoColor=white" alt="GitHub Actions" /></a>
<img src="https://img.shields.io/github/license/L0NE-6/AtomCode-Daily?style=for-the-badge&label=License&color=F472B6" alt="License" />
<a href="https://github.com/L0NE-6/AtomCode-Daily/releases"><img src="https://img.shields.io/badge/%E2%AC%87%20Releases-%E4%B8%8B%E8%BD%BD-2ea44f?style=for-the-badge&logo=github&logoColor=white" alt="Releases Download" /></a>

[✨ 30 秒速览](#-30-秒速览) · [🚀 快速开始](#-快速开始) · [🐧 青龙部署](#-青龙部署) · [☁️ GitHub Actions](#-github-actions) · [🔧 环境变量](#-环境变量) · [❓ 常见问题](#-常见问题) · [🚫 使用边界](#usage-policy) · [✦ 星轨](#-星轨-star-trail)

</div>

---

<a id="usage-policy"></a>
## 🚫 使用边界与转载声明

> [!IMPORTANT]
> **官方版本永久免费。** 未经作者书面许可，禁止付费包装、搬运引流、冒充作者，或使用作者身份与二维码制造官方授权假象。违规内容可能被要求下架；作者可暂停更新、归档或删除仓库及相关 Release。

本项目仓库、脚本、部署说明和 Release 下载始终免费公开。未经作者明确书面许可，禁止将本项目包装为付费资源、内部版、独家版、会员权益、收费课程、付费部署或包更新服务；禁止搬运到其他账号、群组、频道、网盘、电商或付费平台进行涨粉、截流、倒卖和引流；禁止删除作者与版权信息后冒充原创；禁止使用作者昵称、头像、二维码和项目名称制造官方授权假象。

> 如需商业合作、品牌授权、联合分发或使用作者名义提供付费服务，请先取得作者明确书面授权。完整规则、收款码防诈骗说明和违规处理方式见 **[NOTICE.md](NOTICE.md)**。

> 官方仓库和 Release 始终免费。第三方以“下载费 / 激活费 / 内部版 / 代部署 / 会员门槛”等名义收费，均与作者无关，请停止付款并保留证据。

> 对上述违规行为，作者有权要求立即停止传播、删除内容并下架相关商品或页面；并可视情况暂停更新、归档或删除本仓库及相关 Release、向平台投诉或采取进一步必要措施。

---

## ✨ 30 秒速览

| 维度 | 说明 |
| :--- | :--- |
| **用途** | 查询 AtomCode 免费 CodingPlan 状态；没有有效套餐时自动尝试领取。 |
| **输入** | `ATOMCODE_TOKENS` 多账号令牌，或单账号 `ATOMCODE_TOKEN` / `ATOMCODE_REFRESH_TOKEN`。 |
| **输出** | 套餐名称、到期时间、剩余天数、首个可见额度窗口，以及多账号汇总。 |
| **部署** | 青龙面板、GitHub Actions、Windows / Linux 本地运行。 |
| **依赖** | Python 3 + `requests`；仓库 Actions 使用 Python 3.11。 |
| **成功判据** | 套餐仍在有效期，或领取接口明确返回成功 / `duplicate: true`；不以 HTTP 200 单独判定成功。 |

**核心能力**

- 读取 `status-v2`，存在有效套餐时不重复领取。
- 按 `Max → Pro → Lite` 级联尝试，命中即停。
- 可解析的 `expires_at` 优先于 `remaining_days`，过期套餐会重新进入领取流程。
- `duplicate: true` 按“已持有”处理，避免继续降级。
- access token 过期时自动续期，并保存轮换后的 refresh token。
- 支持多账号、代理和 PushPlus / Bark / 企业微信 / 钉钉推送。

## 🧭 工作方式

```text
读取 status-v2
    ├─ 套餐有效 ──> 输出状态并结束
    └─ 无有效套餐
          ├─ --query ──> 只报告可领取，不提交请求
          └─ 正常执行 ──> Max → Pro → Lite
                            ├─ success / duplicate ──> 停止
                            └─ 三档均拒绝 ──> 返回失败
```

> AtomCode 的免费权益是 CodingPlan 套餐授权，不是每日积分。脚本只在新账号、无套餐或套餐到期时执行领取。

## 🚀 快速开始

**1. 安装依赖**

```bash
python -m pip install -r requirements.txt
```

**2. 准备令牌**

如果本机已有 AtomCode / AtomGit 官方客户端 auth 文件，可以用转换工具读取：

```bash
python atomcode_auth.py --file path/to/auth.toml
python atomcode_auth.py --file path/to/auth.toml --write-env .env
```

也可以手动填写单账号：

```text
ATOMCODE_TOKEN=ACCESS_TOKEN
ATOMCODE_REFRESH_TOKEN=REFRESH_TOKEN
ATOMCODE_EXPIRES_AT=1799999999000
```

多账号使用每行一条记录：

```text
ATOMCODE_TOKENS=
主账号|ACCESS_TOKEN|REFRESH_TOKEN|1799999999000
小号|ACCESS_TOKEN|REFRESH_TOKEN
```

**3. 先查询，再领取**

```bash
python atomcode_daily.py --query
python atomcode_daily.py
```

## ⌨️ 命令行

| 命令 | 作用 |
| :--- | :--- |
| `python atomcode_daily.py` | 查询并在没有有效套餐时领取 |
| `python atomcode_daily.py --query` | 只查询状态，不提交领取请求 |
| `python atomcode_daily.py --only 1` | 只处理第 1 个账号 |
| `python atomcode_daily.py --no-notify` | 本轮不发送通知 |

退出码：`0` 表示套餐有效、已持有或本次成功领取；`1` 表示未找到令牌、选中账号不存在，或三档领取均失败。

## 🐧 青龙部署

```bash
pip3 install requests
```

在青龙环境变量中填写 `ATOMCODE_TOKENS`，再创建定时任务：

```text
20 8 * * * python3 atomcode_daily.py
```

续期后的 access token 与 refresh token 会写入 `atomcode_state.json`。该文件已加入 `.gitignore`；青龙环境建议使用可写且可持久化的目录，也可以通过 `ATOMCODE_STATE_FILE` 指定路径。

## ☁️ GitHub Actions

工作流位于 [`.github/workflows/daily.yml`](.github/workflows/daily.yml)。**默认只有手动触发**，定时段目前被注释；需要定时运行时再取消注释，并注意 GitHub cron 使用 UTC。

在仓库 `Settings → Secrets and variables → Actions` 中配置：

| Secret | 必填 | 说明 |
| :--- | :---: | :--- |
| `ATOMCODE_TOKENS` | 二选一 | 多账号令牌 |
| `ATOMCODE_TOKEN` | 二选一 | 单账号 access token |
| `ATOMCODE_REFRESH_TOKEN` | 否 | 单账号 refresh token |
| `ATOMCODE_EXPIRES_AT` | 否 | 令牌到期时间提示 |
| `ATOMCODE_PROXY` | 否 | HTTP(S) / SOCKS 代理 |
| `PLUSPLUS_TOKEN` | 否 | PushPlus 推送令牌 |
| `BARK_URL` | 否 | Bark 推送地址 |
| `WECOM_WEBHOOK` | 否 | 企业微信机器人 webhook |
| `DINGTALK_WEBHOOK` | 否 | 钉钉机器人 webhook |

Actions 运行环境不保留本地状态文件；如果上游轮换了 refresh token，需要重新导出并更新 Secret。长期运行优先使用青龙或带持久化目录的定时任务。

## 🔧 环境变量

### 账号与运行

| 变量 | 必填 | 说明 |
| :--- | :---: | :--- |
| `ATOMCODE_TOKENS` | 二选一 | 多账号，每行 `备注\|access\|refresh\|expires_at\|created_at\|expires_in` |
| `ATOMCODE_TOKEN` | 二选一 | 单账号 access token |
| `ATOMCODE_REFRESH_TOKEN` | 否 | 单账号 refresh token，强烈建议填写 |
| `ATOMCODE_EXPIRES_AT` | 否 | 毫秒或秒时间戳，也支持可解析的日期时间字符串 |
| `ATOMCODE_AUTH_FILE` | 否 | JSON auth 文件路径 |
| `ATOMCODE_STATE_FILE` | 否 | 续期状态文件路径，默认脚本同目录 `atomcode_state.json` |
| `ATOMCODE_PROXY` | 否 | HTTP(S) / SOCKS 代理 |
| `ATOMCODE_NO_NOTIFY` | 否 | 设为 `1` 时关闭推送 |
| `ATOMCODE_BROKER_BASE` | 高级 | 覆盖默认认证代理地址 |
| `ATOMCODE_CODINGPLAN_API_BASE` | 高级 | 覆盖默认 CodingPlan API 地址 |

### 推送

| 变量 | 说明 |
| :--- | :--- |
| `PLUSPLUS_TOKEN` | PushPlus 令牌 |
| `BARK_URL` | Bark 服务地址 |
| `WECOM_WEBHOOK` | 企业微信机器人 webhook，或仅填 key |
| `QYWX_TOKEN` | 企业微信 key 的兼容变量名 |
| `DINGTALK_WEBHOOK` | 钉钉机器人 webhook |

所有推送均为可选，推送失败不会改变套餐查询与领取退出码。

## ❓ 常见问题

<details>
<summary><b>为什么不是每天增加积分？</b></summary>

AtomCode 的免费权益是 CodingPlan 套餐授权，不是每日积分。脚本只在没有有效套餐或套餐过期时领取。
</details>

<details>
<summary><b>已经持有 Pro，会不会继续尝试 Lite？</b></summary>

不会。上游返回 `duplicate: true` 时会立即按“已持有”处理并停止级联。
</details>

<details>
<summary><b>refresh token 为什么会变化？</b></summary>

续期接口会轮换 access token 与 refresh token。脚本会保存新值；使用 Actions 时需要同步更新 Secret。
</details>

<details>
<summary><b>查询成功是否代表领取成功？</b></summary>

不代表。`--query` 只读取状态；正常执行时仍以领取接口的 `success` / `duplicate` 和退出码为准。
</details>

## 🔒 隐私说明

- 不收集、不上传账号数据；
- 日志不输出完整令牌；
- `atomcode_state.json` 与 `.env` 已加入 `.gitignore`；
- 只把令牌放在本地环境变量、GitHub Secrets 或青龙环境变量中；
- 不要在 Issue、README、Release 或公开聊天中粘贴令牌。

## 📦 版本与发布

- 当前发布版：`v1.0.2`（2026-11-04，文档发行版；脚本逻辑仍为 `v1.0.1`）。

## ☕ 支持与反馈

脚本免费使用，不包含账号数据。如果它节省了你的时间，可以自愿扫码支持：

<p align="center">
  <img src="assets/donate-wechat.png" width="260" alt="微信赞赏码" />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/donate-alipay.jpg" width="260" alt="支付宝收款码" />
</p>

> ⚠️ 收款码仅用于向作者自愿赞赏。任何第三方以代下载、代部署、内部资源或会员群为由收费，均与作者无关，请停止付款并保留证据。

遇到问题请先脱敏日志与令牌，再通过 [Issues](https://github.com/L0NE-6/AtomCode-Daily/issues) 反馈；版本变化见 [Releases](https://github.com/L0NE-6/AtomCode-Daily/releases)。

## ✦ 星轨 Star Trail

每一次运行是一束信号，每一次 Star 都会把它推向下一条轨道。

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=L0NE-6/AtomCode-Daily&type=Date&theme=dark" />
  <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=L0NE-6/AtomCode-Daily&type=Date&theme=light" />
  <img alt="AtomCode Daily Star Trail" src="https://api.star-history.com/svg?repos=L0NE-6/AtomCode-Daily&type=Date&theme=light" />
</picture>

<div align="center">

[Releases](https://github.com/L0NE-6/AtomCode-Daily/releases) · [Issues](https://github.com/L0NE-6/AtomCode-Daily/issues) · [⭐ Star](https://github.com/L0NE-6/AtomCode-Daily)

</div>
