#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
yuque.py — 语雀 (Yuque) OpenAPI v2 命令行客户端

依赖：仅 Python 3.8+ 标准库（urllib），无需 pip install。

认证：从环境变量 YUQUE_TOKEN 读取 Personal Access Token。
  获取方式：登录语雀 → 右上角头像 → 设置 → 开发者 → Token
  https://www.yuque.com/settings/tokens

用法示例：
  export YUQUE_TOKEN="xxxxxxxx"
  python3 yuque.py whoami
  python3 yuque.py groups
  python3 yuque.py repos my-team
  python3 yuque.py docs my-team my-repo
  python3 yuque.py doc my-team my-repo my-doc-slug
  python3 yuque.py doc-create my-team my-repo --title "标题" --body-md file.md
  python3 yuque.py doc-update my-team my-repo my-doc-slug --body-md file.md
  python3 yuque.py toc my-team my-repo
  python3 yuque.py raw GET /api/v2/user
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

BASE_URL = "https://www.yuque.com"
API_PREFIX = "/api/v2"
DEFAULT_UA = "yuque-cli/1.0"


class YuqueError(Exception):
    def __init__(self, status, message, body=""):
        super().__init__(f"HTTP {status}: {message}")
        self.status = status
        self.body = body


def _request(method, path, token, query=None, body=None):
    """发送一次语雀 API 请求，返回解析后的 JSON dict。"""
    url = BASE_URL + path
    if query:
        # 过滤掉 None 值
        pairs = []
        for k, v in query.items():
            if v is None:
                continue
            if isinstance(v, bool):
                v = "true" if v else "false"
            pairs.append(f"{k}={urllib.parse.quote(str(v))}")
        if pairs:
            url += "?" + "&".join(pairs)

    data = None
    headers = {
        "X-Auth-Token": token,
        "User-Agent": DEFAULT_UA,
        "Accept": "application/json",
    }
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        msg = e.reason
        try:
            err_json = json.loads(err_body)
            if isinstance(err_json, dict):
                msg = err_json.get("message") or err_json.get("error") or msg
        except Exception:
            pass
        raise YuqueError(e.code, msg, err_body)
    except urllib.error.URLError as e:
        raise YuqueError(0, f"网络错误: {e.reason}")


def _get_token(args):
    token = getattr(args, "token", None) or os.environ.get("YUQUE_TOKEN", "")
    if not token:
        print("错误：未设置 YUQUE_TOKEN。请先 export YUQUE_TOKEN='你的token'，"
              "或在语雀 https://www.yuque.com/settings/tokens 创建。", file=sys.stderr)
        sys.exit(2)
    return token


def _print(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def _read_body_file(path):
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ---------- 各子命令处理 ----------

def cmd_whoami(args):
    token = _get_token(args)
    _print(_request("GET", f"{API_PREFIX}/user", token))


def cmd_groups(args):
    token = _get_token(args)
    login = args.login
    _print(_request("GET", f"{API_PREFIX}/users/{login}/groups", token,
                    query={"offset": args.offset, "limit": args.limit}))


def cmd_group_members(args):
    token = _get_token(args)
    _print(_request("GET", f"{API_PREFIX}/groups/{args.login}/users", token,
                    query={"offset": args.offset, "limit": args.limit}))


def cmd_repos(args):
    token = _get_token(args)
    login = args.login
    _print(_request("GET", f"{API_PREFIX}/users/{login}/repos", token,
                    query={"offset": args.offset, "limit": args.limit,
                           "type": args.type, "filterByAbility": args.filter}))


def cmd_repo(args):
    token = _get_token(args)
    path = f"{API_PREFIX}/repos/{args.group}/{args.slug}"
    _print(_request("GET", path, token))


def cmd_repo_create(args):
    token = _get_token(args)
    body = {"name": args.name}
    if args.slug:
        body["slug"] = args.slug
    if args.description:
        body["description"] = args.description
    if args.public is not None:
        body["public"] = args.public
    _print(_request("POST", f"{API_PREFIX}/users/{args.login}/repos", token, body=body))


def cmd_repo_update(args):
    token = _get_token(args)
    body = {}
    if args.name:
        body["name"] = args.name
    if args.slug:
        body["slug"] = args.slug
    if args.description is not None:
        body["description"] = args.description
    if args.public is not None:
        body["public"] = args.public
    _print(_request("PUT", f"{API_PREFIX}/repos/{args.group}/{args.slug}", token, body=body))


def cmd_repo_delete(args):
    token = _get_token(args)
    _print(_request("DELETE", f"{API_PREFIX}/repos/{args.group}/{args.slug}", token))


def cmd_docs(args):
    token = _get_token(args)
    _print(_request("GET", f"{API_PREFIX}/repos/{args.group}/{args.repo}/docs", token,
                    query={"offset": args.offset, "limit": args.limit,
                           "deleted": args.deleted,
                           "optional_properties": args.optional}))


def cmd_doc(args):
    token = _get_token(args)
    _print(_request("GET", f"{API_PREFIX}/repos/{args.group}/{args.repo}/docs/{args.doc}", token))


def cmd_doc_create(args):
    token = _get_token(args)
    if args.body_md:
        body_text = _read_body_file(args.body_md)
    elif args.body:
        body_text = args.body
    else:
        print("错误：创建文档需要 --body-md <文件> 或 --body <文本>", file=sys.stderr)
        sys.exit(2)
    body = {"title": args.title, "body": body_text, "format": "markdown"}
    if args.slug:
        body["slug"] = args.slug
    if args.public is not None:
        body["public"] = args.public
    result = _request("POST", f"{API_PREFIX}/repos/{args.group}/{args.repo}/docs", token, body=body)
    _print(result)
    print("\n提示：创建文档后不会自动加入目录，如需要请调用 toc-update。", file=sys.stderr)


def cmd_doc_update(args):
    token = _get_token(args)
    body = {}
    if args.title:
        body["title"] = args.title
    if args.body_md:
        body["body"] = _read_body_file(args.body_md)
        body["format"] = "markdown"
    elif args.body:
        body["body"] = args.body
        body["format"] = "markdown"
    if args.slug:
        body["slug"] = args.slug
    if args.public is not None:
        body["public"] = args.public
    if not body:
        print("错误：更新文档至少需要提供 title / body / slug / public 之一", file=sys.stderr)
        sys.exit(2)
    _print(_request("PUT", f"{API_PREFIX}/repos/{args.group}/{args.repo}/docs/{args.doc}",
                    token, body=body))


def cmd_doc_delete(args):
    token = _get_token(args)
    _print(_request("DELETE", f"{API_PREFIX}/repos/{args.group}/{args.repo}/docs/{args.doc}", token))


def cmd_toc(args):
    token = _get_token(args)
    _print(_request("GET", f"{API_PREFIX}/repos/{args.group}/{args.repo}/toc", token))


def cmd_toc_update(args):
    token = _get_token(args)
    body = {"action": args.action, "action_mode": args.action_mode}
    if args.target_uuid:
        body["target_uuid"] = args.target_uuid
    if args.node_uuid:
        body["node_uuid"] = args.node_uuid
    if args.doc_ids:
        body["doc_ids"] = [int(x) for x in args.doc_ids.split(",")]
    if args.type:
        body["type"] = args.type
    if args.title:
        body["title"] = args.title
    if args.url:
        body["url"] = args.url
    _print(_request("PUT", f"{API_PREFIX}/repos/{args.group}/{args.repo}/toc", token, body=body))


def cmd_notes(args):
    token = _get_token(args)
    _print(_request("GET", f"{API_PREFIX}/notes", token))


def cmd_note_create(args):
    token = _get_token(args)
    if args.body_md:
        body_text = _read_body_file(args.body_md)
    else:
        body_text = args.body
    if not body_text:
        print("错误：创建小记需要 --body-md <文件> 或 --body <文本>", file=sys.stderr)
        sys.exit(2)
    _print(_request("POST", f"{API_PREFIX}/notes", token, body={"body": body_text}))


def cmd_note(args):
    token = _get_token(args)
    _print(_request("GET", f"{API_PREFIX}/notes/{args.id}", token))


def cmd_statistics(args):
    token = _get_token(args)
    sub = args.subtype or ""
    suffix = f"/{sub}" if sub else ""
    _print(_request("GET", f"{API_PREFIX}/groups/{args.login}/statistics{suffix}", token))


def cmd_raw(args):
    token = _get_token(args)
    path = args.path
    if not path.startswith("/"):
        path = "/" + path
    query = {}
    if args.param:
        for p in args.param:
            if "=" in p:
                k, v = p.split("=", 1)
                query[k] = v
    body = None
    if args.body_file:
        body = json.loads(_read_body_file(args.body_file))
    elif args.body:
        body = json.loads(args.body)
    _print(_request(args.method.upper(), path, token, query=query, body=body))


# ---------- 参数解析 ----------

def build_parser():
    p = argparse.ArgumentParser(
        description="语雀 OpenAPI v2 命令行客户端（零依赖，仅需 YUQUE_TOKEN）")
    p.add_argument("--token", help="直接指定 Token（默认读环境变量 YUQUE_TOKEN）")
    sub = p.add_subparsers(dest="cmd", required=True)

    # whoami
    sub.add_parser("whoami", help="获取当前 Token 对应的用户信息")

    # groups
    sp = sub.add_parser("groups", help="获取某用户加入的团队/组织列表")
    sp.add_argument("login", help="用户 login（可先 whoami 获取自己的 login）")
    sp.add_argument("--offset", type=int, default=0)
    sp.add_argument("--limit", type=int, default=100)

    # group-members
    sp = sub.add_parser("group-members", help="获取团队成员列表")
    sp.add_argument("login", help="团队 login")
    sp.add_argument("--offset", type=int, default=0)
    sp.add_argument("--limit", type=int, default=100)

    # repos
    sp = sub.add_parser("repos", help="列出某用户/团队下的知识库")
    sp.add_argument("login", help="用户或团队 login")
    sp.add_argument("--offset", type=int, default=0)
    sp.add_argument("--limit", type=int, default=100)
    sp.add_argument("--type", choices=["Book", "Design"], help="按类型筛选")
    sp.add_argument("--filter", dest="filter", default="",
                    help="权限筛选，如 create_doc")

    # repo
    sp = sub.add_parser("repo", help="获取知识库详情")
    sp.add_argument("group", help="团队 login")
    sp.add_argument("slug", help="知识库路径 slug")

    # repo-create
    sp = sub.add_parser("repo-create", help="创建知识库")
    sp.add_argument("login", help="归属用户/团队 login")
    sp.add_argument("--name", required=True, help="知识库名称")
    sp.add_argument("--slug", help="知识库路径（不填自动生成）")
    sp.add_argument("--description", help="简介")
    sp.add_argument("--public", type=int, choices=[0, 1, 2], help="0私密 1公开 2企业内公开")

    # repo-update
    sp = sub.add_parser("repo-update", help="更新知识库")
    sp.add_argument("group", help="团队 login")
    sp.add_argument("slug", help="知识库路径 slug")
    sp.add_argument("--name")
    sp.add_argument("--slug", dest="new_slug", help="新路径")
    sp.add_argument("--description")
    sp.add_argument("--public", type=int, choices=[0, 1, 2])

    # repo-delete
    sp = sub.add_parser("repo-delete", help="删除知识库")
    sp.add_argument("group", help="团队 login")
    sp.add_argument("slug", help="知识库路径 slug")

    # docs
    sp = sub.add_parser("docs", help="列出知识库下的文档")
    sp.add_argument("group", help="团队 login")
    sp.add_argument("repo", help="知识库 slug")
    sp.add_argument("--offset", type=int, default=0)
    sp.add_argument("--limit", type=int, default=100)
    sp.add_argument("--deleted", action="store_true", help="包含已删除文档")
    sp.add_argument("--optional", default="", help="附加字段，如 hits,tags")

    # doc
    sp = sub.add_parser("doc", help="获取单篇文档详情（含正文）")
    sp.add_argument("group", help="团队 login")
    sp.add_argument("repo", help="知识库 slug")
    sp.add_argument("doc", help="文档 id 或 slug")

    # doc-create
    sp = sub.add_parser("doc-create", help="创建文档")
    sp.add_argument("group", help="团队 login")
    sp.add_argument("repo", help="知识库 slug")
    sp.add_argument("--title", required=True, help="文档标题")
    sp.add_argument("--slug", help="文档路径（不填自动生成）")
    sp.add_argument("--body-md", dest="body_md", help="Markdown 正文文件路径，- 表示 stdin")
    sp.add_argument("--body", help="直接传入 Markdown 正文文本")
    sp.add_argument("--public", type=int, choices=[0, 1, 2])

    # doc-update
    sp = sub.add_parser("doc-update", help="更新文档")
    sp.add_argument("group", help="团队 login")
    sp.add_argument("repo", help="知识库 slug")
    sp.add_argument("doc", help="文档 id 或 slug")
    sp.add_argument("--title")
    sp.add_argument("--slug", dest="new_slug")
    sp.add_argument("--body-md", dest="body_md", help="Markdown 正文文件路径，- 表示 stdin")
    sp.add_argument("--body", help="直接传入 Markdown 正文文本")
    sp.add_argument("--public", type=int, choices=[0, 1, 2])

    # doc-delete
    sp = sub.add_parser("doc-delete", help="删除文档")
    sp.add_argument("group", help="团队 login")
    sp.add_argument("repo", help="知识库 slug")
    sp.add_argument("doc", help="文档 id 或 slug")

    # toc
    sp = sub.add_parser("toc", help="获取知识库目录（树）")
    sp.add_argument("group", help="团队 login")
    sp.add_argument("repo", help="知识库 slug")

    # toc-update
    sp = sub.add_parser("toc-update", help="更新知识库目录节点")
    sp.add_argument("group")
    sp.add_argument("repo")
    sp.add_argument("--action", required=True,
                    choices=["appendNode", "prependNode", "editNode", "removeNode"])
    sp.add_argument("--action-mode", dest="action_mode", required=True,
                    choices=["sibling", "child"])
    sp.add_argument("--target-uuid", dest="target_uuid")
    sp.add_argument("--node-uuid", dest="node_uuid")
    sp.add_argument("--doc-ids", dest="doc_ids", help="逗号分隔的文档 id 列表")
    sp.add_argument("--type", choices=["DOC", "LINK", "TITLE"])
    sp.add_argument("--title")
    sp.add_argument("--url")

    # notes
    sub.add_parser("notes", help="获取当前用户小记列表")

    # note-create
    sp = sub.add_parser("note-create", help="创建小记")
    sp.add_argument("--body-md", dest="body_md", help="Markdown 文件路径，- 表示 stdin")
    sp.add_argument("--body", help="直接传入 Markdown 文本")

    # note
    sp = sub.add_parser("note", help="获取小记详情")
    sp.add_argument("id", type=int)

    # statistics
    sp = sub.add_parser("statistics", help="团队统计数据")
    sp.add_argument("login", help="团队 login")
    sp.add_argument("--subtype", choices=["members", "books", "docs"],
                    help="不填则返回汇总")

    # raw
    sp = sub.add_parser("raw", help="直接调用任意 API（高级用法）")
    sp.add_argument("method", help="HTTP 方法 GET/POST/PUT/DELETE")
    sp.add_argument("path", help="API 路径，如 /api/v2/user")
    sp.add_argument("-p", "--param", action="append", help="query 参数 key=value，可多次")
    sp.add_argument("--body", help="JSON 请求体字符串")
    sp.add_argument("--body-file", dest="body_file", help="JSON 请求体文件路径")

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    handlers = {
        "whoami": cmd_whoami,
        "groups": cmd_groups,
        "group-members": cmd_group_members,
        "repos": cmd_repos,
        "repo": cmd_repo,
        "repo-create": cmd_repo_create,
        "repo-update": cmd_repo_update,
        "repo-delete": cmd_repo_delete,
        "docs": cmd_docs,
        "doc": cmd_doc,
        "doc-create": cmd_doc_create,
        "doc-update": cmd_doc_update,
        "doc-delete": cmd_doc_delete,
        "toc": cmd_toc,
        "toc-update": cmd_toc_update,
        "notes": cmd_notes,
        "note-create": cmd_note_create,
        "note": cmd_note,
        "statistics": cmd_statistics,
        "raw": cmd_raw,
    }
    try:
        handlers[args.cmd](args)
    except YuqueError as e:
        print(f"\n❌ {e}", file=sys.stderr)
        if e.body:
            print(e.body, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
