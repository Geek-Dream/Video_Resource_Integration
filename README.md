# 视频资源聚合器 (Video Resource Aggregator)

一个强大的公开视频资源搜索和聚合工具，支持从多个平台搜索和下载视频。

## 功能特性

- 🔍 **多平台搜索** - 支持 YouTube、Internet Archive、Vimeo 等平台
- 🌐 **网页爬取** - 从任意网页提取视频资源
- 📥 **视频下载** - 支持 MP4、M3U8 等格式下载
- 💾 **数据存储** - SQLite 数据库存储，支持 JSON 导出
- 🎯 **智能去重** - 自动识别并过滤重复视频
- 📊 **CLI 界面** - 命令行操作，简单高效

## 技术栈

- **Python 3.11+**
- **requests** - HTTP 请求
- **BeautifulSoup4** - HTML 解析
- **Playwright** - 浏览器自动化（备用）
- **yt-dlp** - 视频信息提取和下载
- **Rich** - 终端美化输出
- **Click** - CLI 框架
- **Peewee** - ORM 数据库操作
- **Loguru** - 日志系统

## 项目结构

```
VideoResourceIntegration/
├── crawler/            # 爬虫模块
│   ├── base_crawler.py     # 爬虫基类
│   ├── youtube_crawler.py  # YouTube 爬虫
│   ├── archive_crawler.py  # Internet Archive 爬虫
│   ├── vimeo_crawler.py    # Vimeo 爬虫
│   └── web_crawler.py      # 通用网页爬虫
├── downloader/         # 下载模块
│   └── video_downloader.py # 视频下载器
├── parser/             # 解析模块
│   ├── video_parser.py     # 视频解析器
│   └── html_parser.py      # HTML 解析器
├── database/           # 数据库模块
│   ├── models.py           # 数据模型
│   └── manager.py          # 数据库管理器
├── utils/              # 工具模块
│   ├── logger.py           # 日志系统
│   └── helpers.py          # 辅助函数
├── main.py             # 主程序入口
├── requirements.txt    # 依赖列表
└── README.md           # 项目说明
```

## 安装

1. 克隆项目
```bash
cd /Users/wl/开发/My\ File/VideoResourceIntegration
```

2. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 安装 Playwright 浏览器（可选）
```bash
playwright install chromium
```

## 使用方法

### 搜索视频

```bash
# 搜索所有平台
python main.py search "流浪地球"

# 指定平台搜索
python main.py search "music" -s youtube

# 限制结果数量
python main.py search "tutorial" -l 50
```

### 列出已保存视频

```bash
# 列出所有视频
python main.py list

# 按来源筛选
python main.py list -s youtube

# 限制显示数量
python main.py list -l 100
```

### 下载视频

```bash
# 使用哈希ID下载
python main.py download abc123

# 下载指定URL的视频
python main.py download https://example.com/video.mp4
```

### 获取视频信息

```bash
python main.py info https://www.youtube.com/watch?v=xxxxx
```

### 爬取网页视频

```bash
python main.py crawl https://example.com/videos
```

### 导出数据

```bash
# 导出为JSON
python main.py export videos.json
```

### 查看统计

```bash
python main.py stats
```

## 输出示例

### 搜索结果

```
┌─────────────────────────────────────────────────────────┐
│                    搜索结果: 流浪地球                    │
├──────┬──────────────────────────────────────┬──────┬─────┤
│ ID   │ 标题                                │ 来源 │ 时长│
├──────┼──────────────────────────────────────┼──────┼─────┤
│ 1    │ 流浪地球2 官方预告片                 │ you  │ 02:│
│ 2    │ 流浪地球2 幕后花絮                   │ you  │ 15:│
│ 3    │ 流浪地球2 完整版                     │ arch │ 02:│
└──────┴──────────────────────────────────────┴──────┴─────┘

共找到 3 个视频
```

## 数据存储

- **SQLite 数据库**: `data/videos.db`
- **下载目录**: `downloads/`
- **日志文件**: `logs/`

## 配置说明

### 环境变量

- `DOWNLOAD_DIR` - 自定义下载目录
- `LOG_LEVEL` - 日志级别 (DEBUG, INFO, WARNING, ERROR)

### 数据库

数据库文件位于 `data/videos.db`，使用 SQLite 存储，支持：
- 自动去重（基于 URL 哈希）
- 全文搜索
- JSON 导出

## 注意事项

1. 本工具仅用于搜索和下载**公开可访问**的视频资源
2. 请遵守各平台的使用条款和版权规定
3. 下载的视频仅供个人学习使用，请勿用于商业用途
4. 部分平台可能需要代理才能访问

## 常见问题

### Q: 为什么搜索不到结果？
A: 可能原因：
- 网络连接问题
- 平台限制访问
- 搜索关键词过于具体

### Q: 下载失败怎么办？
A: 检查：
- 视频链接是否有效
- 网络连接是否正常
- 磁盘空间是否充足

### Q: 如何更新 yt-dlp？
A: 运行：
```bash
pip install --upgrade yt-dlp
```

## 开发

### 添加新爬虫

1. 在 `crawler/` 目录创建新文件
2. 继承 `BaseCrawler` 类
3. 实现 `search()` 和 `get_video_info()` 方法
4. 在 `main.py` 中注册新爬虫

### 代码规范

- 使用 type hints
- 遵循 PEP 8 规范
- 添加适当的注释和文档字符串
- 使用 loguru 记录日志

## 许可证

MIT License

## 作者

Video Resource Aggregator Team
