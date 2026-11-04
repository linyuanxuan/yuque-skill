# 语雀 Skill · 让 AI 直接读写你的语雀

> 一个零依赖的 Python CLI，把语雀 OpenAPI v2 封装成 20 个子命令。配好一个 `YUQUE_TOKEN`，AI 就能确认账号身份、翻知识库、读文档、写回去。

本仓库是这个 skill 的**展示页**（单文件静态站），不含任何业务逻辑，也不收集任何数据。

---

## 页面内容

- **它是什么** —— 三个核心能力（账号确认 / 双向读写 / 目录维护）
- **典型场景** —— 四句自然语言指令，对应实际命令
- **三步接入** —— 放目录、配 Token、跑 `whoami`，含 PowerShell 与 Bash 双版本片段
- **命令清单** —— 20 个子命令，按只读 / 写入 / 删除 / 通用分级，可筛选
- **安全边界** —— 出网域名、凭证读取、写入范围
- **FAQ** —— Windows 9009、401、新建文档不进目录、为什么不能网页直调

## 本地打开

```bash
git clone <repo-url>
cd <repo>
# 直接双击 index.html，或起个静态服务：
python -m http.server 8000
```

## 部署到 GitHub Pages

1. 推到 GitHub；
2. **Settings → Pages**；
3. Source 选 **Deploy from a branch**，分支 `main`、目录 `/ (root)`；
4. 访问 `https://<username>.github.io/<repo>/`。

根目录就是 `index.html`，无需构建、无需 `.nojekyll`。

## 关于隐私

页面是纯静态的，并且刻意做到零副作用：

- 不发起任何网络请求（无 CDN、无字体、无埋点）；
- 不写 `localStorage` / `cookie`；
- 源码内不含任何账号、Token、路径；
- 示例输出里的 `your-login` 全是占位符。

## 配套 skill 需要什么

| 项 | 要求 |
|---|---|
| Python | 3.8+（只用标准库，无需 `pip install`） |
| 凭证 | 环境变量 `YUQUE_TOKEN` |
| 目录 | `~/.workbuddy/skills/yuque/{SKILL.md, references/api.md, scripts/yuque.py}` |

Token 在 <https://www.yuque.com/settings/tokens> 创建，**只显示一次**。只读场景勾读权限即可，要写文档需勾写权限。

## 自定义这个页面

所有可改内容都在 `index.html` 底部的 `<script>` 里：

```js
const CMDS  = [...]   // 命令清单：命令 / 作用 / 风险 / API
const RISK  = {...}   // 风险标签样式
const SNIP  = {...}   // PowerShell / Bash 的安装与运行片段
```

改文案直接搜 HTML 里的中文即可。

## 目录结构

```
.
├── index.html   # 整站，一个文件
├── README.md
├── LICENSE
└── .gitignore
```

## License

[MIT](./LICENSE)
