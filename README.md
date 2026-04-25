# novel-skill

> AI 全程执笔的本地小说创作工具。你提供大纲，AI 负责写完整本小说。

---

## 架构概览

```
用户 (CLI Shell)
    │
    ▼
Go CLI (交互式 shell)
    │  HTTP localhost:8000
    ▼
Python FastAPI (AI 服务)
    ├── 写作 / Embedding 模型   ← 由 config.yaml 的 provider 决定
    │     · gemini（Google 原生 API，支持真实 embedding）
    │     · longcat（美团 LongCat-Flash-Thinking）
    │     · 任意 OpenAI 兼容服务（DeepSeek / Groq / 自建网关 等）
    └── ChromaDB                 ← 本地向量库（章节记忆 + 风格 RAG）
```

## 快速开始

**1. 克隆仓库**
```bash
git clone https://github.com/hourinX/novel-skill.git
cd novel-skill
```

**2. 配置 `config.yaml`**

仓库根目录已带一份 `config.yaml`，按你使用的服务商改 `model` 段即可：

```yaml
model:
  provider: "longcat"                              # gemini | longcat | 其他 OpenAI 兼容
  api_key: "你的 API Key"
  model: "LongCat-Flash-Thinking"                  # 具体模型名
  base_url: "https://api.longcat.chat/openai/v1"   # OpenAI 兼容服务必填；gemini 留空
  embedding_model: ""                              # gemini 用 "models/gemini-embedding-001"
  request_timeout: 600                             # thinking 模型建议 ≥300
```

> 用 gemini 时 `provider: "gemini"`、`base_url` 留空、`embedding_model` 填上即可；
> 用 OpenAI 兼容服务时 embedding 暂时降级为哈希伪向量，RAG 效果有限但不影响主流程。

**3. 创建项目运行需要的文件夹**

> ⚠️ 这些缺少的文件夹需要手动创建，它们是运行所必需的（例如用于存放生成的小说等文件）。

**3.1 创建 `preferences.json`**

```
将 `preferences.example.jsonc` 文件改名为 `preferences.json`，并删除文件中的所有注释内容。
```

**3.2 创建 `chapters`文件夹在data中**

**4. 安装依赖**

> ⚠️ **安装 Python 依赖前请先关闭 VPN / 系统代理**。pip 走代理常常 SSL 握手失败（`SSLEOFError`），且部分包从国内镜像直连更快更稳。

**4.1 Python AI 服务依赖（在「项目根目录」执行）**

```powershell
# 当前目录：D:\...\novel-skill\
.venv\Scripts\python.exe -m pip install -r ai_service/requirements.txt
```

如果默认源仍卡，换清华镜像：

```powershell
.venv\Scripts\python.exe -m pip install -r ai_service/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**4.2 Go CLI 依赖（在「项目根目录/cli」执行）**

```powershell
cd cli
# 当前目录：D:\...\novel-skill\cli\
go mod tidy
cd ..
```

> Go 的 `go mod tidy` 需要能访问 `proxy.golang.org`，国内通常需要走代理或设置 `GOPROXY`：
> ```powershell
> go env -w GOPROXY=https://goproxy.cn,direct
> ```

**5. 启动服务（两个终端）**

**终端 1：启动 Python AI 服务（在「项目根目录」执行）**

```powershell
# 当前目录：D:\...\novel-skill\
.venv\Scripts\python.exe -m uvicorn ai_service.main:app --host localhost --port 8000 --reload
```

**终端 2：编译并启动 CLI（在「项目根目录/cli」执行）**

```powershell
cd cli
# 当前目录：D:\...\novel-skill\cli\
go build -o novel-skill.exe .
./novel-skill.exe
```

---

## 使用流程

启动 CLI 后进入交互式 shell，下面所有命令都在 shell 内执行。

### 典型创作循环

```bash
# 1. 生成第一章（约 8000 字）
generate --chapter 1 --words 8000

# 2. 不满意？三种修法 ↓

# 2a. 整章重写：可改字数、可加方向提示
regenerate                                              # 沿用上次字数与默认设定
regenerate --words 6000                                 # 重写并改成 6000 字
regenerate --note "节奏太慢，把前半段开会戏份压缩，加快入江湖"
regenerate --words 10000 --note "把战斗场景写得更激烈，多用短句"

# 2c. 局部润色（不重写，只调风格）
polish                                                  # 默认润色当前章
polish --style 武侠豪迈                                 # 指定风格参考（先 style-index 入库，详见下文）
polish --chapter 2 --style 玄幻热血

# 3. 满意了 → 确认并同步到 novel.md / chapters / 向量库
accept

# 4. 继续下一章
generate --chapter 2 --words 8000
```

### 命令清单

**章节生成**
```bash
generate   --chapter N --words 8000           # 生成新章节
regenerate --words N   --note "方向提示"       # 重写当前章节（chapter 自动跟随上次 generate）
                                              #   --words 省略时使用偏好默认值
                                              #   --note  注入到 prompt，可纠正剧情/节奏/人物表现
polish     --chapter N --style 来源名         # RAG 润色，--style 引用已索引的风格文件
accept                                        # 接受当前草稿：写入 novel.md、章节文件、向量库、记忆
reject                                        # 丢弃当前草稿（清空 draft）
```

**大纲管理**
```bash
extend-outline                                # 自动补齐到下一个 5 的倍数章节
extend-outline --from 10 --count 5            # 从第 10 章后续写 5 章
extend-outline --note "主角进入魔界，遇到劲敌" # 给续写一个方向
```

> `extend-outline` 会自动把生成的章节追加到 `data/outline.md`，格式严格遵守 7 列表格
> （`章节 | 标题 | 核心事件 | 人物弧光 | 伏笔 | 情绪基调 | 结尾钩子类型`）。
> ⚠️ `outline.md` 整个文件原文都会进入 AI prompt，正式开写前请把字段说明等注释从文件里删掉，只留表格。
> 详细写法和示例见 `data/outline.md` 内的模板说明。

**风格 / 状态**
```bash
style-index          # 扫描 data/style_refs/ 下的 .txt 入向量库（polish --style 才能引用）
status               # 查看当前章节、草稿状态、已写章数
memory               # ⚠️ 当前为占位，未实现，请直接看 data/memory.md
config               # 查看 / 修改服务地址等配置
preview --chapter N  # ⚠️ 当前为占位，未实现，请直接看 data/chapters/chNNN.md
```

> **关于 `data/memory.md`**：这是 AI 跨章节"记忆"的核心文件，会**完整进入每次写章节的 prompt 上下文**。
> 由你写"已埋伏笔 / 人物当前状态 / 未解决冲突"三个段落的初始值，AI 在每次 `accept` 后自动追加 `## 第N章更新` 块（提取本章新伏笔、人物变化、未解冲突）。
> 自动追加的内容**请勿手改**，否则会与 AI 后续提取冲突。详细写法见 `data/memory.md` 顶部说明。

> 序言 / 楔子 / 简介接口（`POST /generate-intro`）目前只有 Python 服务端实现，CLI 还未提供对应命令，
> 如需使用可直接 `curl -X POST http://localhost:8000/generate-intro`。

---

## 目录说明

```
novel-skill/
├── ai_service/        # Python AI 服务（FastAPI）
│   ├── core/          # 模型客户端、向量库、记忆等
│   ├── routers/       # /generate /polish /accept ...
│   └── prompts/       # Prompt 模板
├── cli/               # Go CLI
├── data/
│   ├── outline.md             # 结构化大纲（手写 + extend-outline 自动追加）
│   ├── memory.md              # 伏笔/人物状态（手写初始 + accept 自动追加）
│   ├── character.md           # 人设 + 力量体系 + 剧情弧光（手写）
│   ├── worldview.md           # 世界观（手写）
│   ├── preferences.json       # 写作偏好（accept 自动刷新 last_updated）
│   ├── preferences.example.jsonc  # 偏好配置带注释的模板，仅供参考
│   ├── novel.md               # 小说全文汇总（accept 自动追加）
│   ├── chapters/              # 每章独立文件（accept 自动落盘）
│   └── style_refs/            # 风格参考小说（手动放入 .txt，需 style-index）
├── draft/             # 草稿区（accept 后自动清空）
├── config.yaml        # 配置文件（含 API Key，建议加入 .gitignore）
└── Makefile
```

---

## 设定文档（`data/*.md`）

这 4 个 markdown 文件是 AI 写章节的核心知识来源，**每次 `generate` / `regenerate` 都会被完整读取并塞进 prompt**。
分工要清晰，不要互相重复，否则会浪费 prompt 额度也会让 AI 困惑。

| 文件 | 职责范围 | 维护方式 | 详细说明 |
|------|---------|---------|---------|
| `worldview.md` | **整个世界**：地理 / 力量体系 / 势力 / 历史 / 文化 / 终极秘密 / 写作硬规则 | 全手写 | 文件顶部模板说明 |
| `character.md` | **主角及核心配角**：人设 / 主角力量路线 / 人物关系 / 剧情弧光 | 全手写 | 文件顶部模板说明 |
| `outline.md` | **逐章剧本**：7 列 markdown 表格，每行一章 | 手写 + `extend-outline` 自动追加 | 文件顶部模板说明（含示例第 1 章） |
| `memory.md` | **跨章节记忆**：已埋伏笔 / 人物当前状态 / 未解冲突 / 章节更新流水 | 手写初始 + `accept` 自动追加 | 文件顶部模板说明 |

### 分工边界（重要，避免设定打架）

- **世界级设定**（民众如何看待力量者 / 政治体制 / 历史 / 货币）→ 写在 `worldview.md`
- **主角具体修炼路线 / 主角的家人朋友 / 主角的剧情弧光** → 写在 `character.md`
- **每一章具体发生什么** → 写在 `outline.md`
- **当前章节之前已经发生了什么、有哪些线索还没回收** → 写在 `memory.md`

### `worldview.md` 模板要点

仓库自带的 `worldview.md` 是**通用模板**，兼容 都市 / 玄幻 / 仙侠 / 高武 / 西幻 / 穿越古代 / 末世 / 科幻 / 言情 等所有题材。包含 10 大板块：

1. 世界基础（题材 / 时代 / 规模 / 基调）
2. 地理与空间
3. 力量/能力体系（世界级视角，纯都市言情可整段删）
4. 社会与势力（政治 / 阵营 / 阶级 / 经济 / 种族）
5. 文化、信仰与日常（语言 / 宗教 / 习俗 / 婚姻 / 信息媒介）
6. 历史时间线（远古 / 关键事件 / 当下时代）
7. 世界级秘密与未解之谜（埋伏笔的源头）
8. 世界级冲突与时代主题
9. **写作约束（给 AI 的硬规则）** ← 强烈建议填，能防止 AI 写飞
10. 创作锚点（私设细节 / 行话 / 彩蛋）

### 通用注意事项

- ⚠️ 4 个文件**整体内容**都会进 AI prompt。装饰性文字（## 标题分隔线、HTML 注释、用不到的整段）请在正式开写前删掉，建议总字数控制在 8000 字以内
- ✏️ 占位符 `[...]` 填实之前 AI 也能跑，但写出来的内容会很模糊；越具体设定越稳
- 🔁 这 4 份设定不是一次定终身，发现剧情走偏可以随时回头改 `memory.md` 或 `outline.md` 让 AI 拐回来

---

## 写作偏好（`data/preferences.json`）

控制 AI 默认行为的小型配置文件，**标准 JSON，不能写注释**（json.load 会报错，且 `accept` 每次会覆写整个文件）。
带注释的完整说明请看同目录的 `preferences.example.jsonc`。

| 字段 | 含义 | 哪里在用 | 示例值 |
|------|------|----------|--------|
| `preferred_genre` | 题材类型 | `generate-intro` 写序言/楔子时注入 prompt | `"玄幻"` / `"都市"` / `"武侠"` / `"科幻"` / `"悬疑"` / `"言情"` / `"历史架空"` |
| `writing_style` | 整体写作风格关键词（4-8 字） | `generate-intro` 写序言/楔子时注入 prompt | `"紧张大气"` / `"冷峻克制"` / `"诗意细腻"` / `"幽默轻快"` / `"热血爽快"` |
| `chapter_length` | 单章默认目标字数 | `generate` / `regenerate` 未传 `--words` 时使用 | `4000` / `8000` / `12000` |
| `narrative_perspective` | 叙事视角 | 当前仅在 `status` 显示（暂未注入 prompt，预留扩展） | `"第一人称"` / `"第三人称有限视角"` / `"第三人称全知视角"` |
| `hook_preference` | 章节结尾偏好钩子类型 | 当前仅做记录（暂未注入 prompt，预留扩展） | `"悬念型"` / `"命运型"` / `"情感型"` / `"反转型"` / `"危机型"` |
| `last_updated` | 最近一次 `accept` 日期 | `accept` 自动维护，手填会被覆盖 | `"2026-04-25"` |

**典型修改方式**：直接用编辑器改 `preferences.json`（注意保持 JSON 合法），改完下一次 `generate` / `generate-intro` 即生效。
若文件被误删，下次读取会自动 fallback 到 `ai_service/core/preferences.py` 里的 `DEFAULT_PREFERENCES`。

---

## 风格参考（RAG）

`polish --style XXX` 之所以能模仿某种文风，是因为后台对 `data/style_refs/` 下的参考文本做了向量化检索，
把命中的片段拼进 prompt。**新增或修改风格参考后，必须重新跑一次 `style-index` 才会生效。**

### 完整工作流

**1. 准备参考文本**

把任意 `.txt` 文件放入 `data/style_refs/`，**文件名（不含扩展名）就是 `polish --style` 的引用名**。  
仓库默认带了 5 种原创风格样本，可以直接用：

| 文件名 | 风格特征 |
|---|---|
| `武侠豪迈.txt` | 长句铺陈、家国情怀、画面感重（金庸感） |
| `武侠诗意.txt` | 极短句、留白、意境（古龙感） |
| `玄幻热血.txt` | 感叹号密集、爆点节奏、境界破阶（网文爽文） |
| `文艺细腻.txt` | 意象、心理留白、慢速回忆（现代文学） |
| `冷峻悬疑.txt` | 时间戳、克制对白、不点破（推理悬疑） |

要加自己的风格，直接放新 `.txt` 进去即可（推荐每篇 ≥2000 字，便于切多个 RAG 片段）。

**2. 索引入向量库（CLI 内执行）**

```bash
style-index
```

输出会列出 `已入库` / `已跳过` 两类文件。已入库过的不会重复索引，新增/改名才会被处理。

**3. 在润色时引用**

```bash
polish --style 武侠豪迈            # 用「武侠豪迈.txt」的风格润色当前草稿
polish --chapter 3 --style 冷峻悬疑 # 指定章节 + 指定风格
polish                            # 不带 --style 也能润色，只是不做风格 RAG
```

> ⚠️ 真实 embedding 仅在 `provider: "gemini"` 时启用；OpenAI 兼容模式（LongCat / DeepSeek 等）
> 当前 embedding 走哈希伪向量，RAG 命中精度有限，但流程仍可走通。

---

## 注意事项

- `config.yaml` 含 API Key，请自行加入 `.gitignore` —— 当前仓库的 `.gitignore` 默认未排除它
- `data/novel.md`、`data/chapters/`、`data/.chroma/` 同样建议忽略
- Python 服务必须在 CLI 启动前运行
- Makefile 里的 `install-py` / `run-service` 当前指向了错误的目录名（`ai-service`），暂时请用上方"快速开始"中的直接命令；后续会修
