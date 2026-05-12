# 🎬 Video Resource Integration

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue?style=flat-square" alt="version">
  <img src="https://img.shields.io/badge/python-3.9+-green?style=flat-square&logo=python" alt="python">
  <img src="https://img.shields.io/badge/license-MIT-orange?style=flat-square" alt="license">
  <img src="https://img.shields.io/badge/platform-macOS%20|%20Linux%20|%20Windows-lightgrey?style=flat-square" alt="platform">
</p>

<p align="center"><b>🔍 搜索 · 📥 下载 · 🎯 去重 · 💾 存储</b></p>
<p align="center">一个强大的视频资源搜索与聚合工具，覆盖国内外主流视频平台</p>

---

## ✨ 核心亮点

| 🔥 | 功能 | 说明 |
|---|---|---|
| 🎯 | **一键搜索** | 输入关键词，自动搜索多个视频源 |
| 📥 | **多任务下载** | 支持同时下载多个视频，实时进度条 |
| 🌐 | **多平台支持** | YouTube / Vimeo / Internet Archive / 自定义网站 |
| 🏠 | **国内源直连** | 内置国内视频站，免代理直接搜 |
| 🧠 | **智能去重** | 基于 URL 哈希自动识别重复视频 |
| 💾 | **数据持久化** | SQLite 数据库 + JSON 导出 |
| 🎨 | **终端美化** | Rich 表格 + 彩色 CLI 交互界面 |
| ⚡ | **一键启动** | `bash run.sh` 自动配置环境，全局可用 |

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

# 3. （可选）安装 Playwright 浏览器
playwright install chromium

# 4. 启动
python main.py search "电影名"
```

---

## 📖 使用方法

### 🎬 vid — 交互式 Shell 工具

```bash
vid              # 进入彩色交互界面
                 # [1] 搜索电影  [2] 管理网站  [3] 代理设置
```

**搜索流程：**
1. 输入电影名称 → 自动搜索多个源
2. 翻页浏览结果（q 上一页 / e 下一页）
3. 输入序号选择要下载的视频（逗号分隔多个）
4. 实时进度条显示下载状态

### 🐍 Python CLI — 命令行模式

```bash
# 🔍 搜索视频
python main.py search "星际穿越"           # 搜索所有平台
python main.py search "动作片" -s youtube  # 指定平台
python main.py search "电影" -d            # 仅国内源
python main.py search "关键词" -l 50       # 限制50条

# 📥 下载视频
python main.py download abc123             # 按哈希ID下载
python main.py download https://...        # 直接下载URL

# ℹ️ 获取视频信息
python main.py info https://www.youtube.com/watch?v=xxxxx

# 📋 查看已保存
python main.py list                        # 列出所有
python main.py list -s youtube             # 按来源筛选

# 🌐 爬取网页视频
python main.py crawl https://example.com/videos

# 📊 导出与统计
python main.py export videos.json          # 导出JSON
python main.py stats                       # 数据库统计
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
├── 🔍 crawler/            # 爬虫模块
│   ├── base_crawler.py        # 爬虫基类
│   ├── youtube_crawler.py     # YouTube 爬虫
│   ├── archive_crawler.py     # Internet Archive 爬虫
│   ├── vimeo_crawler.py       # Vimeo 爬虫
│   └── web_crawler.py         # 通用网页爬虫
│
├── 📥 downloader/         # 下载模块
│   └── video_downloader.py    # 视频下载器（支持 MP4/M3U8）
│
├── 📖 parser/             # 解析模块
│   ├── video_parser.py        # 视频解析器
│   └── html_parser.py         # HTML 解析器
│
├── 💾 database/           # 数据库模块
│   ├── models.py              # ORM 数据模型
│   └── manager.py             # 数据库管理器
│
├── 🛠️ utils/              # 工具模块
│   ├── logger.py              # 日志系统
│   └── helpers.py             # 辅助函数
│
├── 📂 data/               # 运行时数据（.gitignore 排除）
│   ├── sites.json             # 自定义视频站配置
│   ├── config.json            # 代理/下载配置
│   └── videos.db              # 视频数据库
│
└── 📂 downloads/          # 下载目录（.gitignore 排除）
```

---

## 🛠️ 技术栈

| 组件 | 技术 | 用途 |
|---|---|---|
| 🐚 Shell | Bash 4+ | `vid` 交互界面 + `run.sh` 启动器 |
| 🐍 核心 | Python 3.9+ | 爬虫 / 解析 / 下载引擎 |
| 🌐 HTTP | `requests` | 网络请求 |
| 📄 解析 | `BeautifulSoup4` | HTML 提取 |
| 🤖 浏览器 | `Playwright` | 动态页面渲染（备用） |
| 📥 下载 | `yt-dlp` | 视频信息提取与下载 |
| 🎨 界面 | `Rich` + `Click` | 终端美化 + CLI 框架 |
| 💾 存储 | `Peewee` + `SQLite` | ORM + 数据库 |

---

## ⚙️ 配置

### 视频站点配置

`vid` 内置了国内视频站配置（`data/sites.json`），支持基于 **MACCMS** 的内容管理系统网站。在交互界面中按 `[2]` 即可管理：

- 📋 查看已配置的网站
- ➕ 新增自定义视频站
- 🗑️ 删除不再使用的站点

### 代理设置

```bash
# vid 交互界面按 [3] 进入代理设置
# 或直接编辑配置文件
cat data/config.json
# → {"proxy_enabled": true, "proxy_url": "http://127.0.0.1:1080"}
```

代理开启后，所有搜索和下载请求都会走代理，适用于访问 YouTube / Vimeo 等平台。

---

## 📊 输出示例

### 搜索结果

```
╔══════════════════════════════════════════════════════════╗
║  🎬 VID - 视频资源下载器  🔥🔥🔥                        ║
║  ● 代理关闭                                            ║
╚══════════════════════════════════════════════════════════╝

  🔍 搜索结果 - 星际穿越  共 12 个资源
  📄 第 1/2 页

┌──────┬────────────────────────────────────┬──────────────┐
│ 序号 │ 标题                               │ 来源         │
├──────┼────────────────────────────────────┼──────────────┤
│ 1    │ 星际穿越 1080P 蓝光                 │ 碟调网       │
│ 2    │ 星际穿越 4K HDR                     │ 52电影网     │
│ 3    │ 星际穿越 中英双字                    │ 一起看影院   │
└──────┴────────────────────────────────────┴──────────────┘

  [q] ◀️ 上一页   [e] ▶️ 下一页   [数字] 选择下载
  [b] 返回菜单
```

### 下载进度

```
  ⬇️ 开始下载 2 个视频

  🎬 星际穿越_碟调网
  🎬 星际穿越_52电影网

  ───────────────────────────────────────

  ✅ 下载完成! 2.8GB /Users/.../downloads/星际穿越_碟调网.mp4
  ✅ 下载完成! 4.2GB /Users/.../downloads/星际穿越_52电影网.mp4

  ───────────────────────────────────────
  ✅ 全部完成! 文件保存在: downloads/
```

---

## 🔒 注意事项

- ⚖️ 本工具仅用于搜索和下载**公开可访问**的视频资源
- 📜 请遵守各平台的使用条款和版权规定
- 🏠 下载的视频仅供个人学习使用，请勿用于商业用途
- 🌐 部分平台（YouTube / Vimeo）可能需要代理才能访问

---

## ❓ 常见问题

<details>
<summary><b>Q: 搜索不到结果？</b></summary>

可能原因：网络连接问题 / 平台限制访问 / 搜索关键词过于具体。试试简化关键词或切换代理。
</details>

<details>
<summary><b>Q: 下载失败？</b></summary>

检查：视频链接是否有效 / 网络连接是否正常 / 磁盘空间是否充足 / yt-dlp 是否最新（`pip install --upgrade yt-dlp`）
</details>

<details>
<summary><b>Q: 如何添加新的视频网站？</b></summary>

在 vid 交互界面按 `[2]` → `[2]`，输入网站名称、地址和搜索方式即可。支持基于 MACCMS 的网站。
</details>

---

## 🧑‍💻 开发

### 架构设计

```
用户输入 → vid (Shell) / main.py (Python CLI)
              │
              ├─ search → crawler/ → 各平台爬虫 → 结果汇总
              ├─ download → downloader/ → yt-dlp 引擎 → downloads/
              ├─ list/stats → database/ → SQLite 查询
              └─ export → JSON 文件输出
```

### 添加新爬虫

1. 在 `crawler/` 目录创建新文件
2. 继承 `BaseCrawler` 类
3. 实现 `search()` 和 `get_video_info()` 方法
4. 在 `main.py` 中注册新爬虫

### 代码规范

- 使用 Type Hints
- 遵循 PEP 8
- 添加文档字符串
- 使用 `loguru` 记录日志

---

## 📄 许可证

MIT License — 自由使用、修改、分发。

---

<p align="center">
  <b>🎬 Video Resource Integration</b><br>
  <sub>Made with ❤️ by Geek-Dream</sub>
</p>
