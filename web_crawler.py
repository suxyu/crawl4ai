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
            timeout=30000,  # 30秒超时
            wait_until="networkidle"  # 等待网络空闲
        )
        
        self.crawler_config = CrawlerRunConfig(
            screenshot=False,  # 不截图
            extract_links=False,  # 不提取链接
            extract_media=False,  # 不提取媒体
            extract_tables=True,  # 提取表格
            wait_for_selectors=None,  # 等待特定选择器
            wait_for_timeout=5000,  # 等待5秒
            scroll_to_bottom=True,  # 滚动到底部
            scroll_pause_time=1000,  # 滚动暂停时间
        )
    
    async def crawl_url(self, url: str) -> Optional[CrawlResult]:
        """
        爬取指定 URL 的网页内容
        
        Args:
            url: 要爬取的网页 URL
            
        Returns:
            CrawlResult 对象，包含爬取结果
        """
        try:
            async with AsyncWebCrawler(
                browser_config=self.browser_config,
                crawler_config=self.crawler_config
            ) as crawler:
                
                print(f"正在爬取: {url}")
                print("请稍候...")
                
                # 执行爬取
                result = await crawler.arun(
                    url=url,
                    config=self.crawler_config
                )
                
                return result
                
        except Exception as e:
            print(f"爬取失败: {e}")
            return None
    
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
            "title": result.title,
            "markdown": result.markdown,
            "text": result.text,
            "html": result.html[:1000] + "..." if len(result.html) > 1000 else result.html,
            "metadata": result.metadata,
            "status": result.status,
            "error": result.error
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
        print("使用方法: python web_crawler.py <URL> [--save] [--headless]")
        print("示例: python web_crawler.py https://www.example.com --save")
        print("参数说明:")
        print("  <URL>     要爬取的网页地址")
        print("  --save    保存结果到文件")
        print("  --headless 无头模式运行浏览器 (默认)")
        print("  --visible  显示浏览器窗口")
        return
    
    url = sys.argv[1]
    save_to_file = "--save" in sys.argv
    headless = "--visible" not in sys.argv
    
    # 验证 URL
    if not url.startswith(('http://', 'https://')):
        print("错误: 请提供有效的 HTTP/HTTPS URL")
        return
    
    print(f"开始爬取网页: {url}")
    print(f"浏览器模式: {'无头模式' if headless else '可见模式'}")
    
    # 创建爬虫实例
    crawler = WebTextCrawler(headless=headless)
    
    # 执行爬取
    result = await crawler.crawl_url(url)
    
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
