#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Crawler using crawl4ai
爬取指定 URL 的网页所有文字信息
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional, List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.models import CrawlResult


class WebTextCrawler:
    """网页文字爬虫类"""
    
    def __init__(self, headless: bool = True, browser_type: str = "chromium"):
        """
        初始化爬虫
        
        Args:
            headless: 是否无头模式运行浏览器
            browser_type: 浏览器类型 (chromium, firefox, webkit)
        """
        self.browser_config = BrowserConfig(
            browser_type=browser_type,
            headless=headless,
            verbose=True,
            java_script_enabled=True  # 启用 JavaScript
        )
        
        self.crawler_config = CrawlerRunConfig(
            screenshot=False,  # 不截图
            scan_full_page=True,  # 扫描完整页面
            scroll_delay=0.2,  # 滚动延迟
            wait_until="networkidle",  # 等待网络空闲
            page_timeout=30000,  # 30秒超时
            verbose=True
        )
        
        # 页面交互配置
        self.interaction_configs = {
            "expand_buttons": {
                "selectors": [
                    "button:contains('展开')",
                    "button:contains('展开更多')", 
                    "button:contains('显示更多')",
                    "button:contains('查看更多')",
                    "a:contains('展开')",
                    "span:contains('展开')",
                    ".expand-button",
                    ".show-more",
                    ".read-more"
                ],
                "js_code": """
                // 查找并点击所有展开按钮
                function clickExpandButtons() {
                    const expandSelectors = [
                        'button:contains("展开")',
                        'button:contains("展开更多")',
                        'button:contains("显示更多")',
                        'button:contains("查看更多")',
                        'a:contains("展开")',
                        'span:contains("展开")',
                        '.expand-button',
                        '.show-more',
                        '.read-more'
                    ];
                    
                    let clickedCount = 0;
                    let totalFound = 0;
                    
                    // 查找所有可能的展开按钮
                    const allButtons = document.querySelectorAll('button, a, span, div');
                    const expandButtons = [];
                    
                    allButtons.forEach(element => {
                        const text = element.textContent || element.innerText || '';
                        if (text.includes('展开') || text.includes('展开更多') || 
                            text.includes('显示更多') || text.includes('查看更多')) {
                            expandButtons.push(element);
                        }
                    });
                    
                    // 查找特定类名的元素
                    const classButtons = document.querySelectorAll('.expand-button, .show-more, .read-more');
                    classButtons.forEach(btn => {
                        if (!expandButtons.includes(btn)) {
                            expandButtons.push(btn);
                        }
                    });
                    
                    totalFound = expandButtons.length;
                    console.log(`找到 ${totalFound} 个展开按钮`);
                    
                    // 点击所有展开按钮
                    expandButtons.forEach((button, index) => {
                        try {
                            if (button.offsetParent !== null && button.style.display !== 'none') {
                                button.click();
                                clickedCount++;
                                console.log(`点击了第 ${index + 1} 个展开按钮`);
                                
                                // 等待一下让内容加载
                                setTimeout(() => {}, 500);
                            }
                        } catch (error) {
                            console.log(`点击第 ${index + 1} 个按钮失败:`, error);
                        }
                    });
                    
                    return { clicked: clickedCount, total: totalFound };
                }
                
                // 执行点击
                const result = clickExpandButtons();
                console.log(`展开按钮点击完成: 点击了 ${result.clicked}/${result.total} 个按钮`);
                return result;
                """
            },
            "load_more": {
                "selectors": [
                    "button:contains('加载更多')",
                    "button:contains('Load More')",
                    ".load-more",
                    ".load-more-button"
                ],
                "js_code": """
                // 查找并点击加载更多按钮
                function clickLoadMoreButtons() {
                    const loadMoreSelectors = [
                        'button:contains("加载更多")',
                        'button:contains("Load More")',
                        '.load-more',
                        '.load-more-button'
                    ];
                    
                    let clickedCount = 0;
                    let totalFound = 0;
                    
                    const allButtons = document.querySelectorAll('button, a, span, div');
                    const loadMoreButtons = [];
                    
                    allButtons.forEach(element => {
                        const text = element.textContent || element.innerText || '';
                        if (text.includes('加载更多') || text.includes('Load More')) {
                            loadMoreButtons.push(element);
                        }
                    });
                    
                    const classButtons = document.querySelectorAll('.load-more, .load-more-button');
                    classButtons.forEach(btn => {
                        if (!loadMoreButtons.includes(btn)) {
                            loadMoreButtons.push(btn);
                        }
                    });
                    
                    totalFound = loadMoreButtons.length;
                    console.log(`找到 ${totalFound} 个加载更多按钮`);
                    
                    loadMoreButtons.forEach((button, index) => {
                        try {
                            if (button.offsetParent !== null && button.style.display !== 'none') {
                                button.click();
                                clickedCount++;
                                console.log(`点击了第 ${index + 1} 个加载更多按钮`);
                                setTimeout(() => {}, 500);
                            }
                        } catch (error) {
                            console.log(`点击第 ${index + 1} 个按钮失败:`, error);
                        }
                    });
                    
                    return { clicked: clickedCount, total: totalFound };
                }
                
                const result = clickLoadMoreButtons();
                console.log(`加载更多按钮点击完成: 点击了 ${result.clicked}/${result.total} 个按钮`);
                return result;
                """
            }
        }
    
    async def crawl_url(self, url: str, enable_interactions: bool = True) -> Optional[CrawlResult]:
        """
        爬取指定 URL 的网页内容
        
        Args:
            url: 要爬取的网页 URL
            enable_interactions: 是否启用页面交互（点击展开按钮等）
            
        Returns:
            CrawlResult 对象，包含爬取结果
        """
        try:
            async with AsyncWebCrawler(
                config=self.browser_config
            ) as crawler:
                
                print(f"正在爬取: {url}")
                print("请稍候...")
                
                if enable_interactions:
                    print("启用页面交互功能...")
                    # 创建包含交互功能的配置
                    config_dict = self.crawler_config.__dict__.copy()
                    config_dict.update({
                        "js_code": self.interaction_configs["expand_buttons"]["js_code"],
                        "wait_for_timeout": 5000,  # 等待交互完成
                        "delay_before_return_html": 2.0  # 交互后等待2秒
                    })
                    interaction_config = CrawlerRunConfig(**config_dict)
                    
                    # 执行带交互的爬取
                    result = await crawler.arun(
                        url=url,
                        config=interaction_config
                    )
                else:
                    # 执行普通爬取
                    result = await crawler.arun(
                        url=url,
                        config=self.crawler_config
                    )
                
                return result
                
        except Exception as e:
            print(f"爬取失败: {e}")
            return None
    
    async def crawl_with_custom_interaction(self, url: str, interaction_type: str = "expand_buttons") -> Optional[CrawlResult]:
        """
        使用自定义交互配置爬取网页
        
        Args:
            url: 要爬取的网页 URL
            interaction_type: 交互类型 ("expand_buttons", "load_more", 或自定义)
            
        Returns:
            CrawlResult 对象，包含爬取结果
        """
        try:
            async with AsyncWebCrawler(
                config=self.browser_config
            ) as crawler:
                
                print(f"正在爬取: {url}")
                print(f"使用交互类型: {interaction_type}")
                print("请稍候...")
                
                if interaction_type in self.interaction_configs:
                    # 使用预定义的交互配置
                    config_dict = self.crawler_config.__dict__.copy()
                    config_dict.update({
                        "js_code": self.interaction_configs[interaction_type]["js_code"],
                        "wait_for_timeout": 5000,
                        "delay_before_return_html": 2.0
                    })
                    interaction_config = CrawlerRunConfig(**config_dict)
                else:
                    # 使用默认配置
                    interaction_config = self.crawler_config
                
                # 执行爬取
                result = await crawler.arun(
                    url=url,
                    config=interaction_config
                )
                
                return result
                
        except Exception as e:
            print(f"爬取失败: {e}")
            return None
    
    def add_custom_interaction(self, name: str, selectors: list, js_code: str):
        """
        添加自定义交互配置
        
        Args:
            name: 交互配置名称
            selectors: 选择器列表
            js_code: JavaScript 代码
        """
        self.interaction_configs[name] = {
            "selectors": selectors,
            "js_code": js_code
        }
        print(f"已添加自定义交互配置: {name}")
    
    def list_interaction_types(self):
        """
        列出所有可用的交互类型
        """
        print("可用的交互类型:")
        for name, config in self.interaction_configs.items():
            print(f"  - {name}: {len(config['selectors'])} 个选择器")
    
    def extract_text_content(self, result: CrawlResult) -> dict:
        """
        从爬取结果中提取文字内容
        
        Args:
            result: 爬取结果对象
            
        Returns:
            包含各种文字内容的字典
        """
        if not result:
            return {}
        
        content = {
            "url": result.url,
            "title": getattr(result, 'title', 'N/A'),  # 可能没有 title 属性
            "markdown": result.markdown,
            "text": getattr(result, 'text', 'N/A'),  # 可能没有 text 属性
            "html": result.html[:1000] + "..." if len(result.html) > 1000 else result.html,
            "metadata": result.metadata,
            "status": getattr(result, 'status', 'N/A'),  # 可能没有 status 属性
            "error": result.error_message
        }
        
        return content
    
    def save_to_file(self, content: dict, filename: str = None):
        """
        保存内容到文件
        
        Args:
            content: 要保存的内容
            filename: 文件名，如果不指定则自动生成
        """
        if not filename:
            # 从 URL 生成文件名
            url = content.get("url", "unknown")
            domain = url.split("//")[-1].split("/")[0].replace(".", "_")
            filename = f"crawled_{domain}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"URL: {content.get('url', 'N/A')}\n")
                f.write(f"标题: {content.get('title', 'N/A')}\n")
                f.write(f"状态: {content.get('status', 'N/A')}\n")
                f.write("=" * 80 + "\n\n")
                
                # 保存 Markdown 格式内容
                f.write("## Markdown 格式内容\n\n")
                f.write(content.get('markdown', 'N/A'))
                f.write("\n\n" + "=" * 80 + "\n\n")
                
                # 保存纯文本内容
                f.write("## 纯文本内容\n\n")
                f.write(content.get('text', 'N/A'))
                f.write("\n\n" + "=" * 80 + "\n\n")
                
                # 保存元数据
                f.write("## 页面元数据\n\n")
                metadata = content.get('metadata', {})
                for key, value in metadata.items():
                    f.write(f"{key}: {value}\n")
                
                if content.get('error'):
                    f.write(f"\n## 错误信息\n{content['error']}")
            
            print(f"内容已保存到文件: {filename}")
            
        except Exception as e:
            print(f"保存文件失败: {e}")
    
    def print_summary(self, content: dict):
        """
        打印内容摘要
        
        Args:
            content: 爬取的内容
        """
        print("\n" + "=" * 60)
        print("爬取结果摘要")
        print("=" * 60)
        print(f"URL: {content.get('url', 'N/A')}")
        print(f"标题: {content.get('title', 'N/A')}")
        print(f"状态: {content.get('status', 'N/A')}")
        
        if content.get('markdown'):
            markdown_length = len(content['markdown'])
            print(f"Markdown 内容长度: {markdown_length} 字符")
            
            # 显示前200个字符的预览
            preview = content['markdown'][:200]
            if len(content['markdown']) > 200:
                preview += "..."
            print(f"内容预览: {preview}")
        
        if content.get('error'):
            print(f"错误: {content['error']}")
        
        print("=" * 60)


async def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("使用方法: python web_crawler.py <URL> [--save] [--headless] [--no-interaction] [--interaction-type TYPE]")
        print("示例: python web_crawler.py https://www.example.com --save")
        print("参数说明:")
        print("  <URL>     要爬取的网页地址")
        print("  --save    保存结果到文件")
        print("  --headless 无头模式运行浏览器 (默认)")
        print("  --visible  显示浏览器窗口")
        print("  --no-interaction 禁用页面交互功能")
        print("  --interaction-type TYPE 指定交互类型 (expand_buttons, load_more)")
        print("  --list-interactions 列出所有可用的交互类型")
        return
    
    url = sys.argv[1]
    save_to_file = "--save" in sys.argv
    headless = "--visible" not in sys.argv
    enable_interactions = "--no-interaction" not in sys.argv
    interaction_type = None
    
    # 检查是否要列出交互类型
    if "--list-interactions" in sys.argv:
        crawler = WebTextCrawler(headless=True)
        crawler.list_interaction_types()
        return
    
    # 检查交互类型参数
    for i, arg in enumerate(sys.argv):
        if arg == "--interaction-type" and i + 1 < len(sys.argv):
            interaction_type = sys.argv[i + 1]
            break
    
    # 验证 URL
    if not url.startswith(('http://', 'https://')):
        print("错误: 请提供有效的 HTTP/HTTPS URL")
        return
    
    print(f"开始爬取网页: {url}")
    print(f"浏览器模式: {'无头模式' if headless else '可见模式'}")
    print(f"页面交互: {'启用' if enable_interactions else '禁用'}")
    if interaction_type:
        print(f"交互类型: {interaction_type}")
    
    # 创建爬虫实例
    crawler = WebTextCrawler(headless=headless)
    
    # 执行爬取
    if interaction_type and enable_interactions:
        # 使用指定的交互类型
        result = await crawler.crawl_with_custom_interaction(url, interaction_type)
    else:
        # 使用默认交互设置
        result = await crawler.crawl_url(url, enable_interactions)
    
    if result:
        # 提取内容
        content = crawler.extract_text_content(result)
        
        # 打印摘要
        crawler.print_summary(content)
        
        # 保存到文件
        if save_to_file:
            crawler.save_to_file(content)
        
        print("\n爬取完成!")
        
    else:
        print("爬取失败，请检查 URL 或网络连接")


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
