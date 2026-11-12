#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AtomCode 免费 CodingPlan 自动领取

环境变量：
  ATOMCODE_TOKENS   多账号，换行或 & 分隔：
                    备注|access_token[|refresh_token[|expires_at[|created_at|expires_in]]]
  ATOMCODE_TOKEN    单账号 access_token
  ATOMCODE_REFRESH_TOKEN
  ATOMCODE_EXPIRES_AT
  ATOMCODE_AUTH_FILE
  ATOMCODE_STATE_FILE
  ATOMCODE_PROXY
  ATOMCODE_NO_NOTIFY=1

命令：
  python atomcode_daily.py
  python atomcode_daily.py --query
  python atomcode_daily.py --only 1
  python atomcode_daily.py --no-notify

依赖：requests
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone

import requests
import urllib3

urllib3.disable_warnings()

try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

BROKER_BASE = os.getenv("ATOMCODE_BROKER_BASE", "").strip().rstrip("/") or "https://acs.atomgit.com"
API_BASE = (
    os.getenv("ATOMCODE_CODINGPLAN_API_BASE", "").strip().rstrip("/")
    or "https://api.gitcode.com/api/v5"
)
REFRESH_PATH = "/oauth/refresh"
STATUS_PATH = "/coding-plan/status-v2"
CLAIM_PATH = "/coding-plan/claim-v2"
USER_AGENT = "checkin-daily/1.0"
TIERS = ("Max", "Pro", "Lite")
REFRESH_WINDOW_SEC = 3600
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.getenv("ATOMCODE_STATE_FILE", "").strip() or os.path.join(
    SCRIPT_DIR, "atomcode_state.json"
)


class AtomCodeError(Exception):
    pass


def log(message):
    print(str(message), flush=True)


def strip_bearer(token):
    text = str(token or "").strip()
    if text.lower().startswith("bearer "):
        text = text[7:].strip()
    return text


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return default


def save_json(path, value):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    temp = path + ".tmp"
    with open(temp, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(temp, path)


def load_state():
    value = load_json(STATE_FILE, {})
    if not isinstance(value, dict):
        value = {}
    value.setdefault("accounts", {})
    return value


def parse_timestamp(value):
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        number = float(value)
        if number <= 0:
            return 0
        return int(number * 1000) if number < 100000000000 else int(number)
    text = str(value).strip()
    if not text:
        return 0
    try:
        number = float(text)
        return int(number * 1000) if number < 100000000000 else int(number)
    except Exception:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return int(datetime.strptime(text[:19], fmt).timestamp() * 1000)
        except Exception:
            continue
    return 0


def first_text(record, keys):
    for key in keys:
        value = record.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def normalize_account(record, index):
    if not isinstance(record, dict):
        return None
    tokens = record.get("tokens") if isinstance(record.get("tokens"), dict) else {}
    user = record.get("user") if isinstance(record.get("user"), dict) else {}

    def pick(keys):
        value = first_text(record, keys)
        return value or first_text(tokens, keys)

    access = strip_bearer(
        pick(("accessToken", "access_token", "token"))
    )
    refresh = strip_bearer(
        pick(("refreshToken", "refresh_token"))
    )
    if not access and not refresh:
        return None
    user_id = pick(("userId", "user_id", "uid")) or first_text(user, ("id", "userId"))
    username = pick(("username", "userName")) or first_text(user, ("username", "name"))
    name = first_text(record, ("name", "nickname")) or username or user_id or (
        "账号%d" % index
    )
    expires_at = parse_timestamp(
        pick(("expiresAt", "expires_at"))
    )
    created_at = parse_timestamp(
        pick(("createdAt", "created_at"))
    )
    added_at = parse_timestamp(
        pick(("addedAt", "added_at"))
    )
    try:
        expires_in = int(float(pick(("expiresIn", "expires_in")) or 0))
    except Exception:
        expires_in = 0
    if not expires_at and expires_in > 0:
        basis = created_at or added_at
        if basis:
            expires_at = basis + expires_in * 1000
    key = user_id or username or name
    return {
        "name": name,
        "key": key,
        "user_id": user_id,
        "access_token": access,
        "refresh_token": refresh,
        "expires_at": expires_at,
    }


def load_accounts():
    accounts = []
    auth_file = os.getenv("ATOMCODE_AUTH_FILE", "").strip()
    if auth_file and os.path.isfile(auth_file):
        value = load_json(auth_file, None)
        if isinstance(value, dict) and isinstance(value.get("accounts"), list):
            value = value["accounts"]
        elif isinstance(value, dict):
            value = [value]
        if isinstance(value, list):
            for index, item in enumerate(value, 1):
                account = normalize_account(item, index)
                if account:
                    accounts.append(account)

    raw = os.getenv("ATOMCODE_TOKENS", "").strip()
    if raw:
        for line in re.split(r"[\r\n&]+", raw):
            line = line.strip()
            if not line:
                continue
            parts = [part.strip() for part in line.split("|")]
            if len(parts) < 2:
                log("跳过格式不正确的 AtomCode 账号")
                continue
            record = {
                "name": parts[0] or ("账号%d" % (len(accounts) + 1)),
                "access_token": parts[1],
                "refresh_token": parts[2] if len(parts) > 2 else "",
                "expires_at": parts[3] if len(parts) > 3 else "",
                "created_at": parts[4] if len(parts) > 4 else "",
                "expires_in": parts[5] if len(parts) > 5 else "",
            }
            account = normalize_account(record, len(accounts) + 1)
            if account:
                accounts.append(account)

    if not accounts:
        record = {
            "name": "账号1",
            "access_token": os.getenv("ATOMCODE_TOKEN", ""),
            "refresh_token": os.getenv("ATOMCODE_REFRESH_TOKEN", ""),
            "expires_at": os.getenv("ATOMCODE_EXPIRES_AT", ""),
        }
        account = normalize_account(record, 1)
        if account:
            accounts.append(account)
    return accounts


class AtomCodeClient:
    def __init__(self, account, state):
        self.state = state
        self.name = account["name"]
        self.key = account["key"]
        saved = (state.get("accounts") or {}).get(self.key, {})
        self.user_id = saved.get("user_id") or account.get("user_id", "")
        self.access_token = strip_bearer(
            saved.get("access_token") or account.get("access_token")
        )
        self.refresh_token = strip_bearer(
            saved.get("refresh_token") or account.get("refresh_token")
        )
        self.expires_at = int(saved.get("expires_at") or account.get("expires_at") or 0)
        self.session = requests.Session()
        self.session.verify = False
        proxy = os.getenv("ATOMCODE_PROXY", "").strip()
        if proxy:
            self.session.proxies.update({"http": proxy, "https": proxy})

    def save_tokens(self):
        self.state.setdefault("accounts", {})[self.key] = {
            "name": self.name,
            "user_id": self.user_id,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at,
            "updated_at": int(time.time()),
        }
        try:
            save_json(STATE_FILE, self.state)
        except Exception as exc:
            log("令牌状态保存失败：%s" % exc)

    def expiring(self):
        return bool(
            self.expires_at
            and self.expires_at - REFRESH_WINDOW_SEC * 1000 <= int(time.time() * 1000)
        )

    def refresh(self):
        if not self.refresh_token:
            raise AtomCodeError("access_token 已失效，且没有 refresh_token")
        try:
            response = self.session.post(
                BROKER_BASE + REFRESH_PATH,
                json={"refresh_token": self.refresh_token},
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "User-Agent": USER_AGENT,
                },
                timeout=30,
            )
        except Exception as exc:
            raise AtomCodeError("令牌续期请求失败：%s" % exc)
        try:
            payload = response.json()
        except Exception:
            payload = {}
        if response.status_code in (401, 403):
            raise AtomCodeError("refresh_token 已失效，请重新登录")
        if response.status_code < 200 or response.status_code >= 300:
            raise AtomCodeError("令牌续期失败 HTTP %s" % response.status_code)
        access = strip_bearer(payload.get("access_token"))
        if not access:
            raise AtomCodeError("令牌续期未返回 access_token")
        self.access_token = access
        rotated = strip_bearer(payload.get("refresh_token"))
        if rotated:
            self.refresh_token = rotated
        user = payload.get("user") if isinstance(payload.get("user"), dict) else {}
        self.user_id = (
            str(user.get("id") or payload.get("user_id") or self.user_id).strip()
        )
        try:
            expires_in = int(payload.get("expires_in") or 0)
        except Exception:
            expires_in = 0
        if expires_in > 0:
            self.expires_at = int(time.time() * 1000) + expires_in * 1000
        self.save_tokens()

    def request(self, method, path, body=None, what="请求"):
        if (not self.access_token or self.expiring()) and self.refresh_token:
            self.refresh()
        if not self.access_token:
            raise AtomCodeError("缺少 access_token")
        url = API_BASE + path
        headers = {
            "Authorization": "Bearer " + self.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        }
        try:
            response = self.session.request(
                method, url, json=body, headers=headers, timeout=30
            )
        except Exception as exc:
            raise AtomCodeError("%s失败：%s" % (what, exc))
        if response.status_code in (401, 403) and self.refresh_token:
            self.refresh()
            headers["Authorization"] = "Bearer " + self.access_token
            try:
                response = self.session.request(
                    method, url, json=body, headers=headers, timeout=30
                )
            except Exception as exc:
                raise AtomCodeError("%s重试失败：%s" % (what, exc))
        try:
            payload = response.json()
        except Exception:
            payload = {"message": response.text[:240]}
        if response.status_code < 200 or response.status_code >= 300:
            message = payload.get("message") or payload.get("msg") or ""
            raise AtomCodeError(
                "%s失败 HTTP %s：%s" % (what, response.status_code, message)
            )
        return payload

    def status(self):
        return self.request("GET", STATUS_PATH, what="套餐状态查询")

    def claim(self, tier):
        return self.request(
            "POST", CLAIM_PATH, body={"plan_type": tier}, what="%s 档领取" % tier
        )


def active_plan(status):
    plan = status.get("codingplan_free") if isinstance(status, dict) else None
    if not isinstance(plan, dict):
        return None
    name = str(plan.get("plan_name") or "").strip()
    expires_at = str(plan.get("expires_at") or "").strip()
    try:
        remaining = int(plan.get("remaining_days") or 0)
    except Exception:
        remaining = 0
    expiry_ts = None
    if expires_at:
        try:
            text = expires_at[:-1] + "+00:00" if expires_at.endswith("Z") else expires_at
            expiry = datetime.fromisoformat(text)
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone(timedelta(hours=8)))
            expiry_ts = expiry.timestamp()
        except Exception:
            expiry_ts = None
    # 有可解析的到期时间时以它为准；缺失/不可解析时才用 remaining_days。
    # 旧实现只看 expires_at 非空，过期套餐也会被当成有效，永远不会续领。
    active = expiry_ts > time.time() if expiry_ts is not None else remaining > 0
    if not active:
        return None
    return name, expires_at, remaining


def plan_tier(status):
    """从 status-v2 的套餐名或 plan_type 中识别 Max / Pro / Lite。"""
    plan = status.get("codingplan_free") if isinstance(status, dict) else None
    name = ""
    if isinstance(plan, dict):
        name = str(plan.get("plan_name") or "").strip()
    if not name and isinstance(status, dict):
        name = str(status.get("plan_type") or status.get("planType") or "").strip()
    lowered = name.lower()
    for tier in TIERS:
        if tier.lower() in lowered:
            return tier
    return ""


def verified_plan(status):
    """返回同时具备有效套餐和可识别档位的 status-v2 证据。"""
    plan = active_plan(status)
    tier = plan_tier(status)
    if not plan or not tier:
        return None
    name, expires_at, remaining = plan
    return tier, name, expires_at, remaining


def describe_plan(status, prefix):
    confirmed = verified_plan(status)
    if not confirmed:
        return ""
    tier, name, expires_at, remaining = confirmed
    text = "%s（%s 档" % (prefix, tier)
    if name:
        text += "：%s" % name
    text += "）"
    if remaining > 0:
        text += "，剩余 %s 天" % remaining
    elif expires_at:
        text += "，到期 %s" % expires_at
    quota = quota_summary(status)
    if quota:
        text += "；" + quota
    return text


def quota_summary(status):
    windows = status.get("rate_limit_windows") if isinstance(status, dict) else None
    if not isinstance(windows, list):
        return ""
    for item in windows:
        if not isinstance(item, dict):
            continue
        try:
            show = int(item.get("show_enable") or 0)
            limit = int(item.get("call_limit") or 0)
            used = int(item.get("calls_used") or 0)
            hours = int(item.get("window_hours") or 0)
        except Exception:
            continue
        if show != 1 or limit <= 0:
            continue
        text = "已用 %s/%s 次" % (used, limit)
        if hours > 0:
            text += "（每 %s 小时滚动）" % hours
        reset = str(item.get("reset_at_display") or "").strip()
        if reset:
            text += "，%s 重置" % reset
        return text
    return ""


def classify_claim(payload):
    message = str(payload.get("message") or payload.get("msg") or "").strip()
    plan_name = str(payload.get("plan_name") or payload.get("planName") or "").strip()
    if payload.get("duplicate") is True:
        return "held", message, plan_name
    if payload.get("success") is True:
        return "granted", message, plan_name
    return "refused", message, plan_name


def run_account(client, query_only=False):
    status = client.status()
    if verified_plan(status):
        return True, describe_plan(status, "套餐有效")
    if query_only:
        return True, "当前没有有效套餐，下次执行会尝试领取"

    refusals = []
    for tier in TIERS:
        payload = client.claim(tier)
        verdict, message, plan_name = classify_claim(payload)
        if verdict in ("held", "granted"):
            receipt = message or (
                "已持有 %s 档套餐，无需重复领取" % tier
                if verdict == "held"
                else "已领取 %s 档免费套餐" % tier
            )
            if plan_name:
                receipt += "（%s）" % plan_name
            try:
                readback = client.status()
            except AtomCodeError as error:
                return False, "领取回执：%s；但 status-v2 回读失败，结果待确认：%s" % (
                    receipt, error)
            if not verified_plan(readback):
                return False, (
                    "领取回执：%s；status-v2 已回读，但未确认 Max/Pro/Lite "
                    "套餐生效或有效期可读" % receipt
                )
            prefix = "已持有，状态回读确认" if verdict == "held" else "领取成功，状态回读确认"
            return True, describe_plan(readback, prefix)
        if message:
            refusals.append("%s: %s" % (tier, message))
    if refusals:
        return False, "三档均未领取：" + "；".join(refusals)
    return False, "三档免费套餐均未领取（上游未说明原因）"


def post_json(url, payload):
    try:
        response = requests.post(url, json=payload, timeout=15, verify=False)
        response.raise_for_status()
        return True
    except Exception as exc:
        log("推送失败：%s" % exc)
        return False


def notify(text, title="AtomCode 套餐"):
    if os.getenv("ATOMCODE_NO_NOTIFY", "").strip() == "1":
        return
    content = text[:1800]
    token = os.getenv("PLUSPLUS_TOKEN", "").strip()
    if token:
        post_json(
            "https://www.pushplus.plus/send",
            {"token": token, "title": title, "content": content, "template": "txt"},
        )
    bark = os.getenv("BARK_URL", "").strip()
    if bark:
        post_json(
            bark.rstrip("/") + "/" + requests.utils.quote(title, safe=""),
            {"body": content},
        )
    wecom = os.getenv("WECOM_WEBHOOK", "").strip() or os.getenv("QYWX_TOKEN", "").strip()
    if wecom:
        if "key=" not in wecom and "/send?" not in wecom:
            wecom = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=" + wecom
        post_json(wecom, {"msgtype": "text", "text": {"content": title + "\n" + content}})
    ding = os.getenv("DINGTALK_WEBHOOK", "").strip()
    if ding:
        post_json(ding, {"msgtype": "text", "text": {"content": title + "\n" + content}})


def main():
    only = ""
    query_only = False
    no_notify = os.getenv("ATOMCODE_NO_NOTIFY", "").strip() == "1"
    args = sys.argv[1:]
    for index, arg in enumerate(args):
        if arg == "--only" and index + 1 < len(args):
            only = args[index + 1]
        elif arg == "--query":
            query_only = True
        elif arg == "--no-notify":
            no_notify = True

    accounts = load_accounts()
    if not accounts:
        log("未配置 ATOMCODE_TOKENS 或 ATOMCODE_TOKEN。")
        return 1
    state = load_state()
    lines = []
    succeeded = 0
    selected = 0
    for index, account in enumerate(accounts, 1):
        if only and str(index) != str(only):
            continue
        selected += 1
        client = AtomCodeClient(account, state)
        try:
            ok, message = run_account(client, query_only=query_only)
            succeeded += 1 if ok else 0
            line = "%s %s：%s" % ("成功" if ok else "失败", client.name, message)
        except Exception as exc:
            line = "失败 %s：%s" % (client.name, str(exc)[:240])
        lines.append(line)
        log(line)
        if index < len(accounts):
            time.sleep(1.0)
    if selected == 0:
        log("没有匹配的账号")
        return 1
    summary = "\n".join(lines)
    log("\n===== AtomCode 套餐汇总 =====\n" + summary)
    if not no_notify:
        notify(summary)
    return 0 if succeeded else 1


if __name__ == "__main__":
    sys.exit(main())
