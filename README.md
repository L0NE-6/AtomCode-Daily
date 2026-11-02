# AtomCode 免费 CodingPlan 自动领取

单文件 Python 青龙脚本，用于探测 AtomCode 当前套餐，并在没有有效套餐时按 `Max → Pro → Lite` 自动领取免费 CodingPlan。

## 功能

- 查询 `status-v2`，有效套餐不会重复领取。
- 可解析的到期时间会按当前时间校验，过期套餐重新进入领取流程。
- 按 `Max → Pro → Lite` 级联领取，命中即停。
- `duplicate: true` 按“已持有”处理，立即停止，避免降级。
- access token 自动续期，并保存轮换后的 refresh token。
- 多账号、代理、PushPlus、Bark、企业微信、钉钉。
- 输出套餐名称、剩余天数和首个可见额度窗口。

## 环境变量

| 变量 | 必填 | 说明 |
| :--- | :-: | :--- |
| `ATOMCODE_TOKENS` | 二选一 | 多账号，每行 `备注\|access\|refresh\|expires_at\|created_at\|expires_in` |
| `ATOMCODE_TOKEN` | 二选一 | 单账号 access token |
| `ATOMCODE_REFRESH_TOKEN` | 否 | refresh token，强烈建议填写 |
| `ATOMCODE_EXPIRES_AT` | 否 | 毫秒或秒时间戳，也支持日期时间字符串 |
| `ATOMCODE_AUTH_FILE` | 否 | JSON auth 文件 |
| `ATOMCODE_STATE_FILE` | 否 | 续期状态文件 |
| `ATOMCODE_PROXY` | 否 | HTTP(S)/SOCKS 代理 |
| `ATOMCODE_NO_NOTIFY=1` | 否 | 关闭推送 |

多账号示例：

```text
ATOMCODE_TOKENS=
主账号|access_token|refresh_token|1799999999000
小号|access_token|refresh_token
```

官方客户端 auth 文件可直接转换：

```bash
python atomcode_auth.py --file path/to/auth.toml
python atomcode_auth.py --file path/to/auth.toml --write-env .env
```

## 运行

```bash
python atomcode_daily.py
python atomcode_daily.py --query
python atomcode_daily.py --only 1
python atomcode_daily.py --no-notify
```

退出码：

- `0`：套餐有效、已持有，或本次成功领取
- `1`：令牌缺失、全部失败，或三档均被拒绝

## 青龙

```bash
pip3 install requests
```

```text
20 8 * * * python3 atomcode_daily.py
```

续期后的 access token 与 refresh token 会写入 `atomcode_state.json`，已加入 `.gitignore`。青龙环境建议挂载可写目录。

## GitHub Actions

工作流位于 `.github/workflows/daily.yml`。至少配置：

- `ATOMCODE_TOKENS`，或单账号三项
- 可选推送密钥

公开仓库不要把 token 写入代码。Actions 不保留本地状态文件；refresh token 轮换后需要更新 Secret。长期运行优先使用青龙。

## 常见问题

<details>
<summary><b>为什么不是每天增加积分？</b></summary>

AtomCode 的免费权益是 CodingPlan 套餐授权，不是每日积分。脚本只在新账号、无套餐或套餐到期时领取。
</details>

<details>
<summary><b>已经持有 Pro，会不会继续试 Lite</b></summary>

不会。`duplicate:true` 会立即终止级联。只有上游明确返回未持有且未成功时才继续下一档。
</details>

<details>
<summary><b>refresh token 为什么会变化</b></summary>

续期接口会轮换 access token 与 refresh token。脚本会保存新值；如果使用 Actions，需要同步更新 Secret。
</details>

## 隐私

- 不收集、不上传账号数据；
- 日志不输出完整令牌；
- `atomcode_state.json` 和 `.env` 已加入 `.gitignore`。

## ☕ 支持与投喂

<p align="center">
  <img src="assets/donate-wechat.png" width="260" alt="微信赞赏码" />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/donate-alipay.jpg" width="260" alt="支付宝收款码" />
</p>

## License

MIT
