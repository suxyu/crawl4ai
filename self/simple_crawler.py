#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Web Crawler using crawl4ai
简化版网页爬虫，快速爬取网页文字信息
"""

import asyncio
import sys
from crawl4ai import AsyncWebCrawler


async def crawl_webpage(url: str):
    """
    爬取网页文字内容
    
    Args:
        url: 要爬取的网页 URL
    """
    try:
        print(f"正在爬取: {url}")
        print("请稍候...")
        
        # 使用默认配置创建爬虫
        async with AsyncWebCrawler() as crawler:
            # 执行爬取
            result = await crawler.arun(url=url)
            
            if result and result.markdown:
                print("\n" + "=" * 60)
                print("爬取成功!")
                print("=" * 60)
                print(f"标题: {result.title}")
                print(f"URL: {result.url}")
                print(f"内容长度: {len(result.markdown)} 字符")
                print("=" * 60)
                print("\n网页内容 (Markdown 格式):")
                print("-" * 40)
                print(result.markdown)
                
                # 保存到文件
                filename = f"crawled_{url.split('//')[-1].split('/')[0].replace('.', '_')}.md"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"# {result.title}\n\n")
                    f.write(f"URL: {result.url}\n\n")
                    f.write("---\n\n")
                    f.write(result.markdown)
                
                print(f"\n内容已保存到: {filename}")
                
            else:
                print("爬取失败或没有获取到内容")
                
    except Exception as e:
        print(f"爬取失败: {e}")


async def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python simple_crawler.py <URL>")
        print("示例: python simple_crawler.py https://www.example.com")
        return
    
    url = sys.argv[1]
    
    # 验证 URL
    if not url.startswith(('http://', 'https://')):
        print("错误: 请提供有效的 HTTP/HTTPS URL")
        return
    
    # 执行爬取
    await crawl_webpage(url)


if __name__ == "__main__":
    asyncio.run(main())
