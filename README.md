# 语雀 Skill

> 让 AI 直接操控你的语雀：确认账号身份、翻知识库、读文档、写回去。零依赖 Python CLI，只认一个 `YUQUE_TOKEN`。

把[语雀 OpenAPI v2](https://www.yuque.com/yuque/developer/api) 封装成 20 个子命令，488 行 Python，**只用标准库**，不需要 `pip install`。以 Agent Skill 的形态组织，装上就能让 AI 替你读写语雀。

项目主页：**https://yuque-skill.linyuanxuan.top/**

---

## 它能做什么

| 能力 | 说明 |
|---|---|
| **确认账号** | `whoami` 返回 Token 对应的用户、login、团队数与知识库数 |
| **读** | 团队列表、成员、知识库列表与详情、文档正文、目录树、小记、团队统计 |
| **写** | 创建 / 更新文档（支持直接传 Markdown 文件）、创建知识库、维护目录节点、写小记 |
| **删** | 删除文档、删除知识库（不可逆） |
| **兜底** | `raw` 直接调任意接口，未被封装的 API 也能用 |

触发方式：对 AI 说「我语雀里有哪些知识库」「把这份 md 发到语雀」「把 XX 知识库的文章全导出来」即可。

---

## 安装

把仓库放到 skills 目录，**目录名保持 `yuque`**：

```bash
git clone https://github.com/linyuanxuan/yuque-skill.git ~/.workbuddy/skills/yuque
```

Windows（PowerShell）：

```powershell
git clone https://github.com/linyuanxuan/yuque-skill.git "$env:USERPROFILE\.workbuddy\skills\yuque"
```

也可以下载 ZIP 解压到该路径。目录结构必须是：

```
yuque/
├── SKILL.md            # skill 定义，agent 读这个
├── references/api.md   # 完整 API 字段说明，按需查阅
└── scripts/yuque.py    # 唯一可执行文件
```

装好后**新开一个会话**，skill 才会被加载。

---

## 配置 Token

1. 打开 https://www.yuque.com/settings/tokens → 新建 Token
   - 只读用途勾读权限；要写文档/知识库需勾**写权限**
   - Token 只完整显示一次，当场复制
2. 写入环境变量：

```powershell
# Windows，永久（用户级）
[Environment]::SetEnvironmentVariable('YUQUE_TOKEN','你的token','User')
```

```bash
# macOS / Linux
echo 'export YUQUE_TOKEN="你的token"' >> ~/.bashrc && source ~/.bashrc
```

3. 验证：

```bash
python3 scripts/yuque.py whoami
```

返回你的 `login` 即成功。

---

## 命令速查

```bash
python3 scripts/yuque.py <命令> [参数]
```

| 分组 | 命令 |
|---|---|
| 通用 | `whoami` `raw` |
| 团队 | `groups` `group-members` `statistics` |
| 知识库 | `repos` `repo` `repo-create` `repo-update` `repo-delete` |
| 文档 | `docs` `doc` `doc-create` `doc-update` `doc-delete` |
| 目录 | `toc` `toc-update` |
| 小记 | `notes` `note` `note-create` |

常用示例：

```bash
# 我加入了哪些团队
python3 scripts/yuque.py groups <my_login>

# 某团队下有哪些知识库
python3 scripts/yuque.py repos <team_login>

# 读一篇文档正文
python3 scripts/yuque.py doc <team> <repo> <doc_slug>

# 把本地 Markdown 发上去
python3 scripts/yuque.py doc-create <team> <repo> --title "标题" --body-md ./content.md

# 更新正文
python3 scripts/yuque.py doc-update <team> <repo> <doc_slug> --body-md ./new.md

# 看目录树
python3 scripts/yuque.py toc <team> <repo>
```

完整参数见 `python3 scripts/yuque.py <命令> --help`，字段细节见 [`references/api.md`](references/api.md)。

---

## 三个容易踩的坑

1. **新建文档不进目录**。`doc-create` 之后文章是游离的，要调 `toc-update` 把返回的 `id` 传进 `--doc-ids` 才会出现在左侧目录。
2. **语雀没有全文搜索 API**。要「找某主题的文章」，先 `docs` 拉列表，再按标题筛，命中后 `doc` 取正文。
3. **分页默认 100**。知识库超过 100 篇时用 `--offset` 翻页。

---

## 安全边界

| 项 | 事实 |
|---|---|
| 出网域名 | 只有 `www.yuque.com`，无其他请求 |
| 凭证 | 只读环境变量 `YUQUE_TOKEN`（或 `--token`），不落盘、不打印 |
| 第三方依赖 | 无，仅 Python 3.8+ 标准库 |
| 写入范围 | 仅 Token 有权限的知识库；删除操作不可逆 |

浏览器无法直调语雀 API——响应头没有 `Access-Control-Allow-Origin`，跨域 `fetch` 会被拦。真实调用一律走本地 Python，不要把 Token 交给任何网页代理。

---

## 目录结构

```
.
├── SKILL.md            # skill 定义
├── references/api.md   # API 字段详解
├── scripts/yuque.py    # CLI 本体，488 行
├── index.html          # 项目落地页源码（部署到 Cloudflare Pages，与 skill 无关）
├── README.md
├── LICENSE
└── .gitignore
```

`index.html` 只是介绍页，不参与 skill 的任何逻辑，可忽略。

---

## 许可

[MIT](LICENSE)
