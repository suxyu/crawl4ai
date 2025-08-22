# 高级交互爬虫使用说明

本项目包含多个使用 crawl4ai 的高级网页爬虫脚本，专门用于处理需要页面交互的复杂网页。

## 文件说明

### 1. `web_crawler.py` - 基础交互爬虫
- 支持基本的页面交互功能
- 可配置浏览器设置
- 支持保存结果到文件
- 提供多种交互策略

### 2. `advanced_crawler.py` - 高级展开爬虫
- 专门用于展开隐藏内容的爬虫
- 支持多轮展开操作
- 自动等待内容加载

### 3. `power_crawler.py` - 功能强大的综合爬虫
- 使用多种交互策略
- 支持展开、滚动、加载更多等操作
- 可自定义 JavaScript 代码
- 最适合复杂页面的爬取

## 使用方法

### 基础交互爬虫

```bash
# 基本爬取（启用交互）
python web_crawler.py https://www.example.com

# 保存结果到文件
python web_crawler.py https://www.example.com --save

# 指定交互类型
python web_crawler.py https://www.example.com --interaction-type expand_buttons

# 禁用交互功能
python web_crawler.py https://www.example.com --no-interaction

# 显示浏览器窗口（调试用）
python web_crawler.py https://www.example.com --visible

# 列出所有可用交互类型
python web_crawler.py --list-interactions
```

### 高级展开爬虫

```bash
# 爬取并展开所有隐藏内容
python advanced_crawler.py https://www.example.com
```

### 功能强大的综合爬虫

```bash
# 使用多种策略爬取
python power_crawler.py https://www.example.com

# 使用自定义 JavaScript 代码
python power_crawler.py https://www.example.com --custom my_script.js
```

## 交互策略详解

### 1. expand_buttons（展开按钮）
- 自动查找并点击所有展开按钮
- 支持多种展开按钮文本（展开、展开更多、显示更多等）
- 多轮展开，确保所有内容都被展开

### 2. load_more（加载更多）
- 查找并点击加载更多按钮
- 支持无限滚动页面
- 自动等待新内容加载

### 3. 综合策略（power_crawler）
- **策略1**: 展开所有隐藏内容（3轮）
- **策略2**: 滚动加载更多内容（最多10次）
- **策略3**: 等待动态内容加载
- **策略4**: 再次展开新出现的内容

## 自定义交互

### 添加自定义交互策略

```python
from web_crawler import WebTextCrawler

crawler = WebTextCrawler()

# 添加自定义交互配置
crawler.add_custom_interaction(
    name="my_strategy",
    selectors=[".my-button", "button:contains('自定义')"],
    js_code="""
    // 自定义 JavaScript 代码
    document.querySelector('.my-button').click();
    """
)
```

### 创建自定义 JavaScript 文件

```javascript
// my_script.js
async function customInteraction() {
    // 等待页面加载
    await new Promise(r => setTimeout(r, 2000));
    
    // 查找并点击按钮
    const buttons = document.querySelectorAll('.custom-button');
    buttons.forEach(btn => {
        if (btn.offsetParent !== null) {
            btn.click();
        }
    });
    
    // 等待内容加载
    await new Promise(r => setTimeout(r, 3000));
    
    return true;
}

customInteraction();
```

## 适用场景

### 1. 需要点击展开的页面
- 评论区的"展开更多"按钮
- 文章摘要的"阅读全文"按钮
- 折叠的列表内容

### 2. 无限滚动的页面
- 社交媒体信息流
- 商品列表页面
- 新闻资讯页面

### 3. 动态加载的页面
- 单页应用（SPA）
- 异步加载内容的页面
- 需要等待的交互页面

## 性能优化建议

### 1. 超时设置
- 根据页面复杂度调整 `page_timeout`
- 交互后等待时间 `delay_before_return_html`
- 等待超时 `wait_for_timeout`

### 2. 浏览器配置
- 无头模式提高性能
- 启用 JavaScript 支持
- 适当的视口大小

### 3. 交互策略
- 避免过度点击
- 合理设置等待时间
- 限制最大迭代次数

## 故障排除

### 常见问题

1. **页面加载超时**
   - 增加 `page_timeout` 值
   - 检查网络连接
   - 使用 `--visible` 参数调试

2. **交互不生效**
   - 确认 JavaScript 已启用
   - 检查元素选择器是否正确
   - 增加等待时间

3. **内容不完整**
   - 使用 `power_crawler.py` 的综合策略
   - 调整滚动和展开参数
   - 检查是否有反爬虫机制

### 调试技巧

```bash
# 显示浏览器窗口
python web_crawler.py https://example.com --visible

# 使用自定义 JavaScript
python power_crawler.py https://example.com --custom debug.js

# 查看详细日志
python web_crawler.py https://example.com 2>&1 | tee debug.log
```

## 扩展功能

### 1. 添加新的交互策略

```python
# 在 WebTextCrawler 类中添加
def add_scroll_strategy(self):
    self.interaction_configs["scroll"] = {
        "selectors": [".scroll-trigger"],
        "js_code": """
        // 滚动策略的 JavaScript 代码
        """
    }
```

### 2. 支持更多页面类型

```python
# 针对特定网站的优化策略
def add_site_specific_strategy(self, site_domain: str):
    if "twitter.com" in site_domain:
        # Twitter 特定的交互策略
        pass
    elif "zhihu.com" in site_domain:
        # 知乎特定的交互策略
        pass
```

### 3. 批量爬取

```python
# 支持多个 URL 的批量爬取
async def batch_crawl(self, urls: List[str]):
    results = []
    for url in urls:
        result = await self.crawl_url(url)
        results.append(result)
    return results
```

## 最佳实践

1. **选择合适的爬虫**
   - 简单页面：使用 `web_crawler.py`
   - 需要展开：使用 `advanced_crawler.py`
   - 复杂交互：使用 `power_crawler.py`

2. **合理设置参数**
   - 根据页面复杂度调整超时时间
   - 避免过于频繁的交互
   - 适当等待内容加载

3. **错误处理**
   - 捕获并处理异常
   - 记录详细的错误日志
   - 实现重试机制

4. **遵守网站规则**
   - 检查 robots.txt
   - 合理设置爬取频率
   - 尊重网站的使用条款

## 技术支持

如果遇到问题，可以：
1. 查看 crawl4ai 官方文档
2. 使用 `--visible` 参数调试浏览器行为
3. 检查 JavaScript 代码是否正确
4. 调整超时和等待参数
5. 查看控制台日志输出
