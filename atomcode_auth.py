#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
读取 AtomCode / AtomGit 官方客户端的 auth 文件并输出 ATOMCODE_TOKENS。

用法：
  python atomcode_auth.py
  python atomcode_auth.py --file path\to\auth.toml
  python atomcode_auth.py --write-env .env
"""

import argparse
import json
import os
import sys

try:
    import tomllib
except Exception:
    tomllib = None

try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass


def log(message):
    print(str(message), flush=True)


def first(record, keys):
    for key in keys:
        if key in record and record[key] is not None and str(record[key]).strip():
            return str(record[key]).strip()
    return ""


def candidates():
    home = os.path.expanduser("~")
    appdata = os.getenv("APPDATA", "")
    paths = [
        os.path.join(home, ".atomcode", "auth.toml"),
        os.path.join(home, ".atomcode", "auth.json"),
        os.path.join(home, ".config", "atomcode", "auth.toml"),
        os.path.join(home, ".config", "atomcode", "auth.json"),
    ]
    if appdata:
        paths.extend(
            [
                os.path.join(appdata, "atomcode", "auth.toml"),
                os.path.join(appdata, "atomcode", "auth.json"),
                os.path.join(appdata, "AtomCode", "auth.toml"),
                os.path.join(appdata, "AtomCode", "auth.json"),
            ]
        )
    return [path for path in paths if os.path.isfile(path)]


def load_file(path):
    with open(path, "rb") as handle:
        raw = handle.read()
    if path.lower().endswith(".json"):
        value = json.loads(raw.decode("utf-8-sig"))
    else:
        if tomllib is None:
            raise RuntimeError("Python 3.11+ 才能直接解析 TOML")
        value = tomllib.loads(raw.decode("utf-8-sig"))
    return value


def normalize(value, name):
    tokens = value.get("tokens") if isinstance(value.get("tokens"), dict) else {}
    user = value.get("user") if isinstance(value.get("user"), dict) else {}

    def pick(keys):
        got = first(value, keys)
        return got or first(tokens, keys)

    access = pick(("access_token", "accessToken", "token"))
    refresh = pick(("refresh_token", "refreshToken"))
    if not access:
        return None
    user_id = pick(("user_id", "userId", "uid")) or first(user, ("id", "userId"))
    username = pick(("username", "userName")) or first(user, ("username", "name"))
    expires_at = pick(("expires_at", "expiresAt"))
    created_at = pick(("created_at", "createdAt"))
    expires_in = pick(("expires_in", "expiresIn"))
    account_name = str(value.get("name") or username or user_id or name)
    fields = [account_name, access, refresh, expires_at, created_at, expires_in]
    while len(fields) > 2 and not fields[-1]:
        fields.pop()
    return "|".join(fields)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="")
    parser.add_argument("--write-env", default="")
    args = parser.parse_args()

    paths = [args.file] if args.file else candidates()
    if not paths:
        log("没有找到 AtomCode auth 文件，请使用 --file 指定路径。")
        return 1
    rows = []
    for index, path in enumerate(paths, 1):
        try:
            value = load_file(path)
        except Exception as exc:
            log("读取失败 %s：%s" % (path, exc))
            continue
        items = value.get("accounts") if isinstance(value, dict) and isinstance(value.get("accounts"), list) else [value]
        for item in items:
            if isinstance(item, dict):
                row = normalize(item, "账号%d" % index)
                if row:
                    rows.append(row)
    if not rows:
        log("auth 文件里没有可用的 access_token")
        return 1
    value = "\n".join(rows)
    if args.write_env:
        with open(args.write_env, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("ATOMCODE_TOKENS=" + value + "\n")
        try:
            os.chmod(args.write_env, 0o600)
        except Exception:
            pass
        log("已写入 %s（请勿提交到 Git）" % args.write_env)
    log("\nATOMCODE_TOKENS=<\n%s\n>" % value)
    return 0


if __name__ == "__main__":
    sys.exit(main())
