# 语雀 OpenAPI v2 速查

Base URL: `https://www.yuque.com`
认证: 请求头 `X-Auth-Token: <token>`
Token 申请: https://www.yuque.com/settings/tokens （头像 → 设置 → 开发者 → Token）

## 通用约定

- 所有路径前缀 `/api/v2`
- 返回 JSON 统一信封: `{ "data": ... }`（小记更新接口为双层 `{ data: { data: ... } }`）
- 分页: `offset`（默认 0）+ `limit`（最大 100，默认 100）
- 公开性 `public`: `0` 私密 / `1` 互联网公开 / `2` 企业内公开
- 内容格式 `format`: `markdown`（默认）/ `html` / `lake`
- 错误码: 400 参数非法 / 401 Token 或 Scope 不足 / 403 无权限 / 404 不存在 / 422 校验失败 / 429 限流 / 500 内部错误
- 知识库两种寻址方式等价:
  - 数字 ID: `/repos/{book_id}/...`
  - 团队+路径: `/repos/{group_login}/{book_slug}/...`
- 文档两种寻址方式等价:
  - 数字 ID
  - 文档 slug（路径名）

## 用户 / 团队

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v2/user` | 当前 Token 对应用户 |
| GET | `/api/v2/users/{login}/groups` | 用户加入的团队列表 |
| GET | `/api/v2/groups/{login}/users` | 团队成员列表 |
| PUT | `/api/v2/groups/{login}/users/{id}` | 变更成员角色（body: `role` 0管理员/1成员/2只读） |
| DELETE | `/api/v2/groups/{login}/users/{id}` | 移除成员 |

## 知识库 (Repo / Book)

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v2/users/{login}/repos` | 列出用户/团队知识库（query: type=Book/Design, filterByAbility=create_doc） |
| POST | `/api/v2/users/{login}/repos` | 创建知识库（body: name*, slug?, description?, public?） |
| GET | `/api/v2/repos/{group}/{slug}` | 知识库详情 |
| PUT | `/api/v2/repos/{group}/{slug}` | 更新知识库（name/slug/description/public/toc） |
| DELETE | `/api/v2/repos/{group}/{slug}` | 删除知识库 |

## 文档 (Doc)

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v2/repos/{group}/{slug}/docs` | 文档列表（query: offset, limit, deleted, optional_properties=hits,tags） |
| POST | `/api/v2/repos/{group}/{slug}/docs` | 创建文档（body: title*, body*, format=markdown, slug?, public?） |
| GET | `/api/v2/repos/{group}/{slug}/docs/{doc}` | 文档详情（含 body/body_html） |
| PUT | `/api/v2/repos/{group}/{slug}/docs/{doc}` | 更新文档（title/body/slug/public 任意组合） |
| DELETE | `/api/v2/repos/{group}/{slug}/docs/{doc}` | 删除文档 |

**重要**: 创建文档后不会自动挂到目录上，需要再调用 `PUT /repos/{g}/{s}/toc` 把 doc_id 加进去。

## 目录 (TOC)

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v2/repos/{group}/{slug}/toc` | 获取目录树（含每个节点的 uuid、doc_id、type） |
| PUT | `/api/v2/repos/{group}/{slug}/toc` | 更新目录节点 |

toc-update body 字段:
- `action*`: `appendNode`(尾插) / `prependNode`(头插，创建时不支持同级头插) / `editNode` / `removeNode`
- `action_mode*`: `sibling`(同级) / `child`(子级)
- `target_uuid`: 目标节点 UUID（不填=根节点）
- `node_uuid`: 操作节点 UUID（移动/编辑/删除必填）
- `doc_ids`: 创建文档节点时必填，逗号分隔数字
- `type`: `DOC` / `LINK` / `TITLE`(分组)
- `title`: 创建分组/外链节点必填
- `url`: 创建外链节点必填

## 小记 (Note)

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v2/notes` | 当前用户小记列表 |
| POST | `/api/v2/notes` | 创建小记（body: `body` Markdown 文本） |
| GET | `/api/v2/notes/{id}` | 小记详情 |
| PUT | `/api/v2/notes/{id}` | 更新小记（body: source, html, abstract） |

## 统计

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v2/groups/{login}/statistics` | 团队汇总 |
| GET | `/api/v2/groups/{login}/statistics/members` | 成员统计 |
| GET | `/api/v2/groups/{login}/statistics/books` | 知识库统计 |
| GET | `/api/v2/groups/{login}/statistics/docs` | 文档统计 |

## 文档版本

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v2/doc_versions` | 最近 100 个已发布版本 |
| GET | `/api/v2/doc_versions/{id}` | 版本详情 |

## 典型工作流

1. **初次配置**: `whoami` 确认 Token → `groups <mylogin>` 找到团队 login → `repos <team>` 找到知识库 slug
2. **读文档**: `docs <team> <repo>` 列出 → `doc <team> <repo> <slug>` 读正文
3. **写文档**: `doc-create <team> <repo> --title "X" --body-md content.md` → （可选）`toc-update` 挂到目录
4. **改文档**: `doc-update <team> <repo> <slug> --body.md new.md`
5. **批量导出**: `docs` 列表拿到所有 slug → 循环 `doc` 拉正文，落盘为 .md
