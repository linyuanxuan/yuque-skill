---
name: yuque
description: 通过语雀 (Yuque) OpenAPI v2 读写个人/团队知识库——查询用户与团队、列出知识库、读取/创建/更新/删除文档、维护目录树、写小记、查看团队统计。当用户提到"语雀"、"Yuque"、"我的知识库"、"把文档写到语雀"、"从语雀拉文档"、"语雀里那篇文章"等场景时使用。本 Skill 自带零依赖 Python CLI（scripts/yuque.py），只需 YUQUE_TOKEN 环境变量即可直接调用真实语雀接口。
---

# 语雀 (Yuque) Skill

通过官方 OpenAPI v2 直接操作语雀，无需浏览器登录。

## 前置条件（必须先确认）

1. **Token**: 必须有 `YUQUE_TOKEN` 环境变量，或用 `--token` 参数传入。
   - 用户若无 Token，引导其到 https://www.yuque.com/settings/tokens 创建（头像 → 设置 → 开发者 → Token）。
   - Token 只在创建时完整显示一次，务必提醒用户复制保存。
   - 只读操作勾选读权限即可；要写文档需勾选写权限。
2. **脚本路径**: `<skill_dir>/scripts/yuque.py`，用 `python3` 执行，**仅依赖 Python 3.8+ 标准库**，不需要 pip install。

## 执行方式

所有操作统一通过 `scripts/yuque.py` 调用，输出为 JSON，便于后续解析。

```bash
export YUQUE_TOKEN="xxxx"
SKILL_DIR="<本 skill 所在目录>"
python3 "$SKILL_DIR/scripts/yuque.py" <子命令> [参数...]
```

**第一步永远先跑 `whoami`** 确认 Token 有效，并从返回里拿到用户自己的 `login`，后续团队/知识库操作都依赖 login 和 slug。

## 常用命令速查

| 目的 | 命令 |
|---|---|
| 确认 Token / 拿自己 login | `python3 yuque.py whoami` |
| 我加入了哪些团队 | `python3 yuque.py groups <my_login>` |
| 团队下有哪些知识库 | `python3 yuque.py repos <team_login>` |
| 知识库详情 | `python3 yuque.py repo <team_login> <repo_slug>` |
| 列出知识库所有文档 | `python3 yuque.py docs <team_login> <repo_slug>` |
| 读某篇文档正文 | `python3 yuque.py doc <team_login> <repo_slug> <doc_slug_or_id>` |
| 创建文档（Markdown 文件） | `python3 yuque.py doc-create <team> <repo> --title "标题" --body-md ./content.md` |
| 更新文档正文 | `python3 yuque.py doc-update <team> <repo> <doc_slug> --body-md ./new.md` |
| 删除文档 | `python3 yuque.py doc-delete <team> <repo> <doc_slug>` |
| 看目录树 | `python3 yuque.py toc <team> <repo>` |
| 写一条小记 | `python3 yuque.py note-create --body "今天完成了xx"` |
| 任意未覆盖接口 | `python3 yuque.py raw GET /api/v2/xxx -p k=v` |

用 `python3 yuque.py <命令> --help` 查看完整参数。

## 关键注意事项

1. **创建文档不会自动进目录**: `doc-create` 后文章是"游离"状态，用户若希望它出现在左侧目录，需要再调 `toc-update`，把返回的 `id` 作为 `--doc-ids` 传进去。
2. **寻址双模式**: `group/repo` 或数字 `book_id` 都可以；文档同理（id 或 slug）。脚本统一用 `group/repo/doc` 字符串形式，更直观。
3. **分页**: 默认 limit=100，知识库文档超过 100 篇时用 `--offset` 翻页。
4. **写文件到本地**: 用 `doc` 命令拿到返回 JSON 后，从中提取 `data.body`（Markdown）写到本地 .md 文件。
5. **从本地 Markdown 上传**: `--body-md ./file.md`；也支持 `--body "直接写字符串"`。管道输入用 `--body-md -`。
6. **错误处理**: 脚本报错会打印 HTTP 状态码和语雀返回的 message。401 = Token 失效或未授权；403 = 没权限；404 = 路径/slug 写错；429 = 触发限流，退避后重试。
7. **完整 API 字段说明**（toc-update 复杂参数、统计接口、版本历史等）见 `references/api.md`，需要时再 Read。

## 典型任务流

- **"把本地 md 发到语雀"**: whoami → repos 找目标知识库 → doc-create --body-md → （如需）toc-update 挂目录。
- **"导出语雀某知识库全部文章"**: docs 列表拿 slug → 循环 doc 拉 body → 逐篇写本地 .md。
- **"查语雀里 XX 主题的文章"**: 语雀 API 无全文搜索接口，应先 `docs` 列出标题/slug，再让 AI 在结果里按标题筛选，命中后用 `doc` 拉正文。
