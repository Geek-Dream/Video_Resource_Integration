# 🎬 Video Resource Integration

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue?style=flat-square" alt="version">
  <img src="https://img.shields.io/badge/python-3.9+-green?style=flat-square&logo=python" alt="python">
  <img src="https://img.shields.io/badge/license-MIT-orange?style=flat-square" alt="license">
  <img src="https://img.shields.io/badge/platform-macOS%20|%20Linux%20|%20Windows-lightgrey?style=flat-square" alt="platform">
</p>

<p align="center"><b>🔍 检索 · 📊 采集 · 🎯 去重 · 💾 存储</b></p>
<p align="center">一个面向学术研究的公开多媒体资源检索与聚合分析工具</p>

> ⚠️ **学术声明：本项目仅供学术研究与技术学习使用。** 项目旨在探索网络信息检索、分布式爬虫架构、多媒体数据处理等计算机科学课题。使用者应严格遵守所在地区法律法规及各平台服务条款，不得将本工具用于任何侵犯他人知识产权或商业用途的行为。本项目不存储、分发任何版权内容，所有数据处理均在用户本地完成。

---

## ✨ 核心功能

| 🔥 | 功能 | 说明 |
|---|---|---|
| 🎯 | **资源检索** | 输入关键词，自动检索多个公开信息源 |
| 📊 | **数据采集** | 支持批量采集公开资源元数据，实时状态反馈 |
| 🌐 | **多源聚合** | 整合 YouTube / Vimeo / Internet Archive 等平台的公开数据 |
| 🏠 | **本地优先** | 支持本地化检索，降低网络依赖 |
| 🧠 | **智能去重** | 基于内容哈希自动识别重复资源 |
| 💾 | **数据持久化** | SQLite 数据库存储 + JSON 格式导出，便于学术分析 |
| 🎨 | **可视化界面** | Rich 表格 + 彩色 CLI 交互终端 |
| ⚡ | **一键启动** | `bash run.sh` 自动检测系统环境，零配置上手 |

---

## 🚀 快速开始

### 方式一：一键启动（推荐）

```bash
# 克隆项目
git clone git@github.com:Geek-Dream/Video_Resource_Integration.git
cd Video_Resource_Integration

# 一键启动（自动检测系统、配置环境）
bash run.sh
```

`run.sh` 会：
- 🖥️ 自动检测 macOS / Linux / Windows 系统
- 🔧 macOS：让你选择 **临时生效** 或 **永久注入** 到 PATH
- 🪟 Windows：尝试写入系统 PATH，失败则直接启动
- 🚀 配置完成后自动进入 vid 交互界面

配置完成后，在任何目录直接输入 `vid` 即可启动！

### 方式二：手动安装

```bash
# 1. 进入项目
cd Video_Resource_Integration

# 2. 安装依赖
pip install -r requirements.txt

# 3. （可选）安装 Playwright 浏览器（用于动态页面渲染）
playwright install chromium

# 4. 启动
python main.py search "检索关键词"
```

---

## 📖 使用方法

### 🎬 vid — 交互式 Shell 工具

```bash
vid              # 进入彩色交互界面
                 # [1] 资源检索  [2] 管理数据源  [3] 网络配置
```

**检索流程：**
1. 输入检索关键词 → 自动查询多个数据源
2. 翻页浏览结果（q 上一页 / e 下一页）
3. 输入序号选择需要采集的资源（逗号分隔可多选）
4. 实时进度条显示采集状态

### 🐍 Python CLI — 命令行模式

```bash
# 🔍 检索公开资源
python main.py search "检索关键词"           # 检索所有数据源
python main.py search "关键词" -s youtube    # 指定数据源
python main.py search "关键词" -d            # 仅本地优先源
python main.py search "关键词" -l 50         # 限制返回数量

# 📥 采集资源元数据
python main.py download abc123               # 按哈希标识采集
python main.py download https://...          # 直接使用URL采集

# ℹ️ 获取资源元信息
python main.py info https://www.example.com/...

# 📋 查看数据库记录
python main.py list                          # 列出所有
python main.py list -s youtube               # 按数据源筛选

# 🌐 分析网页中的多媒体资源
python main.py crawl https://example.com

# 📊 导出与统计
python main.py export research_data.json     # 导出JSON（用于学术分析）
python main.py stats                         # 数据库统计概览
```

---

## 📁 项目结构

```
VideoResourceIntegration/
│
├── 🎬 vid                 # Shell 交互式工具（主入口）
├── 🚀 run.sh              # 一键启动器（平台检测 + PATH注入）
├── 🐍 main.py             # Python CLI 主程序
├── 📋 requirements.txt    # Python 依赖
│
├── 🔍 crawler/            # 数据采集模块
│   ├── base_crawler.py        # 采集器基类
│   ├── youtube_crawler.py     # YouTube 平台适配
│   ├── archive_crawler.py     # Internet Archive 适配
│   ├── vimeo_crawler.py       # Vimeo 平台适配
│   └── web_crawler.py         # 通用网页解析
│
├── 📥 downloader/         # 资源获取模块
│   └── video_downloader.py    # 公开资源获取器（支持 MP4/M3U8）
│
├── 📖 parser/             # 数据解析模块
│   ├── video_parser.py        # 资源元数据解析
│   └── html_parser.py         # HTML 内容提取
│
├── 💾 database/           # 数据存储模块
│   ├── models.py              # ORM 数据模型
│   └── manager.py             # 数据库管理器
│
├── 🛠️ utils/              # 工具模块
│   ├── logger.py              # 日志系统
│   └── helpers.py             # 辅助函数
│
├── 📂 data/               # 运行时数据（.gitignore 排除）
│   ├── sites.json             # 数据源配置
│   ├── config.json            # 网络/采集参数配置
│   └── videos.db              # 本地检索索引数据库
│
└── 📂 downloads/          # 本地数据目录（.gitignore 排除）
```

---

## 🛠️ 技术栈

| 组件 | 技术 | 用途 |
|---|---|---|
| 🐚 Shell | Bash | `vid` 交互界面 + `run.sh` 启动器 |
| 🐍 核心 | Python 3.9+ | 数据采集 / 解析 / 资源获取引擎 |
| 🌐 HTTP | `requests` | 网络请求 |
| 📄 解析 | `BeautifulSoup4` | HTML 结构化提取 |
| 🤖 浏览器 | `Playwright` | 动态页面渲染（备用） |
| 📥 数据处理 | `yt-dlp` | 多媒体元信息提取 |
| 🎨 界面 | `Rich` + `Click` | 终端美化 + CLI 框架 |
| 💾 存储 | `Peewee` + `SQLite` | ORM + 本地索引数据库 |

---

## ⚙️ 配置

### 数据源配置

`vid` 内置了公开资源站配置（`data/sites.json`），支持基于常见内容管理系统的网站。在交互界面中按 `[2]` 即可管理：

- 📋 查看已配置的数据源
- ➕ 新增自定义数据源
- 🗑️ 移除不再使用的数据源

### 网络配置

```bash
# vid 交互界面按 [3] 进入网络设置
# 或直接编辑配置文件
cat data/config.json
# → {"proxy_enabled": true, "proxy_url": "http://127.0.0.1:1080"}
```

适用于跨区域网络环境下的研究数据采集。

---

## 🔒 学术合规声明

> **本项目为计算机科学学术研究工具，使用者须遵守以下原则：**
>
> - 📚 **研究目的**：仅用于网络信息检索、分布式系统、数据处理等技术领域的学术学习与探索
> - ⚖️ **合法合规**：使用者应严格遵守所在地法律法规，确保所有操作均在合法框架内进行
> - 📜 **尊重版权**：不存储、分发、传播任何受版权保护的内容；所有数据仅作学术分析用途
> - 🏫 **教育用途**：如需引用或使用采集数据，请遵循合理使用（Fair Use）原则及学术规范
> - 🚫 **禁止商业**：严禁将本项目用于任何商业目的或侵权行为
> - 🗑️ **及时清理**：学术研究完成后应及时删除本地缓存的实验数据
>
> 使用本工具即表示您已阅读并同意上述声明。项目作者不承担任何因使用者违反上述原则而产生的法律责任。

---

## ❓ 常见问题

<details>
<summary><b>Q: 检索不到结果？</b></summary>

可能原因：网络连接波动 / 数据源服务暂时不可用 / 检索关键词过于具体。建议简化关键词或检查网络配置。
</details>

<details>
<summary><b>Q: 数据采集失败？</b></summary>

排查：资源链接是否有效 / 网络连接是否正常 / 存储空间是否充足 / yt-dlp 是否需要更新（`pip install --upgrade yt-dlp`）
</details>

<details>
<summary><b>Q: 如何添加新的数据源？</b></summary>

在 vid 交互界面按 `[2]` → `[2]`，输入数据源名称、地址和检索方式即可。
</details>

---

## 🧑‍💻 开发

### 架构设计

```
用户输入 → vid (Shell) / main.py (Python CLI)
              │
              ├─ search → crawler/ → 各平台公开数据检索 → 结果汇总
              ├─ download → downloader/ → yt-dlp 引擎 → 本地存储
              ├─ list/stats → database/ → SQLite 查询分析
              └─ export → JSON 文件输出（用于学术分析）
```

### 扩展新平台

1. 在 `crawler/` 目录创建新的适配文件
2. 继承 `BaseCrawler` 基类
3. 实现 `search()` 和 `get_video_info()` 方法
4. 在 `main.py` 中注册

### 代码规范

- 使用 Type Hints
- 遵循 PEP 8
- 添加文档字符串
- 使用 `loguru` 记录日志

---

## 📄 许可证

MIT License — 本工具仅供学术研究使用。

---

<p align="center">
  <b>🎬 Video Resource Integration</b><br>
  <sub>Academic Research Tool — For Educational Purposes Only</sub><br>
  <sub>Made for learning ❤️ by Geek-Dream</sub>
</p>
