# Web Crawler 使用说明

本项目包含两个使用 crawl4ai 的网页爬虫脚本，用于爬取指定 URL 的网页所有文字信息。

## 文件说明

### 1. `web_crawler.py` - 完整功能爬虫
功能丰富的爬虫，支持多种配置选项和功能：
- 可配置浏览器设置（无头模式、浏览器类型等）
- 支持保存结果到文件
- 提供详细的内容摘要
- 支持命令行参数配置

### 2. `simple_crawler.py` - 简化版爬虫
轻量级爬虫，专注于快速爬取：
- 使用默认配置
- 自动保存为 Markdown 文件
- 代码简洁，易于理解

## 使用方法

### 基本用法

```bash
# 使用简化版爬虫
python simple_crawler.py https://www.example.com

# 使用完整版爬虫
python web_crawler.py https://www.example.com

# 保存结果到文件
python web_crawler.py https://www.example.com --save

# 显示浏览器窗口（调试用）
python web_crawler.py https://www.example.com --visible
```

### 参数说明

- `<URL>`: 要爬取的网页地址（必需）
- `--save`: 保存结果到文件
- `--headless`: 无头模式运行浏览器（默认）
- `--visible`: 显示浏览器窗口

## 功能特性

### 文字提取
- 提取网页的 Markdown 格式内容
- 提取纯文本内容
- 提取页面标题和元数据
- 支持表格内容提取

### 浏览器控制
- 支持 Chromium、Firefox、WebKit
- 自动等待页面加载完成
- 支持滚动到底部加载动态内容
- 可配置超时和等待策略

### 输出格式
- 控制台实时显示爬取进度
- 自动保存为 Markdown 文件
- 提供内容摘要和统计信息

## 示例输出

```
正在爬取: https://www.example.com
请稍候...

============================================================
爬取结果摘要
============================================================
URL: https://www.example.com
标题: Example Domain
状态: success
Markdown 内容长度: 1250 字符
内容预览: # Example Domain

This domain is for use in illustrative examples in documents...
============================================================

内容已保存到文件: crawled_www_example_com.md

爬取完成!
```

## 注意事项

1. **网络连接**: 确保网络连接正常，能够访问目标网站
2. **网站结构**: 某些动态网站可能需要等待时间或特殊配置
3. **反爬虫机制**: 部分网站可能有反爬虫措施，建议合理设置爬取频率
4. **文件权限**: 确保有写入文件的权限

## 故障排除

### 常见问题

1. **爬取失败**
   - 检查 URL 是否正确
   - 确认网络连接
   - 尝试增加超时时间

2. **内容不完整**
   - 使用 `--visible` 参数查看浏览器行为
   - 调整等待策略配置

3. **浏览器启动失败**
   - 运行 `crawl4ai-setup` 安装浏览器
   - 检查系统依赖

### 调试模式

```bash
# 显示浏览器窗口，便于调试
python web_crawler.py https://www.example.com --visible

# 查看详细错误信息
python web_crawler.py https://www.example.com 2>&1 | tee debug.log
```

## 扩展功能

### 自定义配置

可以修改 `web_crawler.py` 中的配置参数：

```python
self.browser_config = BrowserConfig(
    browser_type="firefox",  # 使用 Firefox
    headless=False,          # 显示浏览器
    timeout=60000,           # 60秒超时
    wait_until="domcontentloaded"  # 等待 DOM 加载
)
```

### 批量爬取

可以修改脚本支持批量 URL 爬取：

```python
urls = [
    "https://example1.com",
    "https://example2.com",
    "https://example3.com"
]

for url in urls:
    await crawler.crawl_url(url)
```

## 技术支持

如果遇到问题，可以：
1. 查看 crawl4ai 官方文档
2. 检查 Python 和依赖包版本
3. 尝试使用不同的浏览器类型
4. 调整超时和等待配置
