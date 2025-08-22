#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deep Crawler for KKDaxue Domain
使用 crawl4ai 的深度爬取功能爬取 kkdaxue.com 域名下的所有网页
"""

import asyncio
import sys
import subprocess
import os
import time
import re
from pathlib import Path
from typing import List, Dict, Any
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy, DFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy


class DeepCrawler:
    """深度爬虫类"""
    
    def __init__(self, domain: str = "kkdaxue.com", headless: bool = False):
        self.domain = domain
        self.base_url = f"https://www.{domain}"
        self.crawled_urls = set()
        self.power_crawler_path = "power_crawler.py"
        self.start_time = time.time()
        self.headless = headless
        self.output_dir = f"deep_crawl_output_{self.domain.replace('.', '_')}"
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"输出目录: {self.output_dir}")
        
    def extract_urls_from_html(self, html_content: str) -> List[str]:
        """
        从HTML内容中提取所有链接
        
        Args:
            html_content: HTML内容
            
        Returns:
            URL列表
        """
        urls = set()
        
        # 使用正则表达式提取链接
        # 匹配 href 属性
        href_pattern = r'href=["\']([^"\']+)["\']'
        href_matches = re.findall(href_pattern, html_content)
        
        # 匹配 src 属性
        src_pattern = r'src=["\']([^"\']+)["\']'
        src_matches = re.findall(src_pattern, html_content)
        
        # 合并所有匹配
        all_matches = href_matches + src_matches
        
        for match in all_matches:
            # 处理相对URL
            if match.startswith('/'):
                url = f"https://www.{self.domain}{match}"
                urls.add(url)
            elif match.startswith('http') and self.domain in match:
                urls.add(match)
            elif not match.startswith(('http', 'javascript:', 'mailto:', 'tel:')):
                # 相对路径
                if match and not match.startswith('#'):
                    url = f"https://www.{self.domain}/{match.lstrip('/')}"
                    urls.add(url)
        
        return list(urls)
    
    async def discover_all_urls(self, max_depth: int = 3, max_pages: int = 100) -> List[str]:
        """
        发现域名下的所有 URL
        
        Args:
            max_depth: 爬取深度
            max_pages: 最大页面数量
            
        Returns:
            发现的 URL 列表
        """
        print(f"开始发现 {self.domain} 域名下的所有 URL...")
        print(f"爬取深度: {max_depth}, 最大页面数: {max_pages}")
        print(f"浏览器模式: {'有头模式' if not self.headless else '无头模式'}")
        
        try:
            async with AsyncWebCrawler() as crawler:
                # 配置深度爬取策略
                config = CrawlerRunConfig(
                    deep_crawl_strategy=BFSDeepCrawlStrategy(
                        max_depth=max_depth,
                        include_external=False,  # 只爬取同一域名
                        max_pages=max_pages,
                        score_threshold=0.1  # 较低的阈值，确保获取更多 URL
                    ),
                    scraping_strategy=LXMLWebScrapingStrategy(),
                    verbose=True
                )
                
                print("开始深度爬取...")
                results = await crawler.arun(self.base_url, config=config)
                
                if not results:
                    print("深度爬取失败")
                    return []
                
                print(f"深度爬取完成，共发现 {len(results)} 个页面")
                
                # 提取所有 URL
                all_urls = set()
                
                # 从深度爬取结果中提取URL
                for result in results:
                    if hasattr(result, 'url') and result.url:
                        all_urls.add(result.url)
                        print(f"发现页面: {result.url}")
                    
                    # 从HTML内容中提取更多链接
                    if hasattr(result, 'html') and result.html:
                        extracted_urls = self.extract_urls_from_html(result.html)
                        print(f"从 {result.url} 提取到 {len(extracted_urls)} 个链接")
                        all_urls.update(extracted_urls)
                
                # 手动添加一些已知的URL模式
                print("添加已知的URL模式...")
                known_patterns = [
                    f"https://www.{self.domain}/post/add",
                    f"https://www.{self.domain}/?current=1",
                    f"https://www.{self.domain}/?current=2",
                    f"https://www.{self.domain}/?current=3",
                    f"https://www.{self.domain}/?current=4",
                    f"https://www.{self.domain}/?current=5",
                    f"https://www.{self.domain}/?current=10",
                    f"https://www.{self.domain}/?current=20",
                    f"https://www.{self.domain}/?current=50",
                    f"https://www.{self.domain}/?current=100",
                ]
                all_urls.update(known_patterns)
                
                # 去重并过滤
                filtered_urls = []
                for url in all_urls:
                    if (self.domain in url and 
                        url.startswith('http') and 
                        url not in self.crawled_urls and
                        not url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.css', '.js'))):
                        filtered_urls.append(url)
                
                print(f"过滤后共有 {len(filtered_urls)} 个唯一 URL")
                
                # 显示前20个URL用于调试
                print("前20个发现的URL:")
                for i, url in enumerate(filtered_urls[:20], 1):
                    print(f"  {i}. {url}")
                
                return filtered_urls
                
        except Exception as e:
            print(f"深度爬取失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def crawl_single_page_with_power_crawler(self, url: str) -> bool:
        """
        使用 power_crawler.py 爬取单个页面
        
        Args:
            url: 要爬取的 URL
            
        Returns:
            是否成功
        """
        try:
            print(f"使用 power_crawler.py 爬取: {url}")
            
            # 检查 power_crawler.py 是否存在
            if not os.path.exists(self.power_crawler_path):
                print(f"错误: {self.power_crawler_path} 文件不存在")
                return False
            
            # 调用 power_crawler.py，传递headless参数
            cmd = [sys.executable, self.power_crawler_path, url]
            if not self.headless:
                cmd.append("--visible")
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode == 0:
                print(f"✅ 成功爬取: {url}")
                self.crawled_urls.add(url)
                
                # 查找并复制生成的文件到输出目录
                self.copy_generated_files(url)
                
                return True
            else:
                print(f"❌ 爬取失败: {url}")
                print(f"错误信息: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"调用 power_crawler.py 失败: {e}")
            return False
    
    def copy_generated_files(self, url: str):
        """复制生成的文件到输出目录"""
        try:
            # 生成可能的文件名
            domain_part = url.split('//')[-1].split('/')[0].replace('.', '_')
            path_part = url.split('//')[-1].split('/', 1)[1] if '/' in url.split('//')[-1] else ''
            if path_part:
                path_part = path_part.replace('?', '_').replace('&', '_').replace('=', '_')
            
            possible_files = [
                f"fully_expanded_{domain_part}.md",
                f"power_crawled_{domain_part}.md",
                f"expanded_{domain_part}.md",
                f"crawled_{domain_part}.txt"
            ]
            
            for filename in possible_files:
                if os.path.exists(filename):
                    # 创建新的文件名
                    new_filename = f"page_{len(self.crawled_urls):03d}_{path_part or 'home'}.md"
                    if filename.endswith('.txt'):
                        new_filename = new_filename.replace('.md', '.txt')
                    
                    # 复制文件
                    import shutil
                    shutil.copy2(filename, os.path.join(self.output_dir, new_filename))
                    print(f"  📁 保存内容到: {self.output_dir}/{new_filename}")
                    
        except Exception as e:
            print(f"复制文件失败: {e}")
    
    async def crawl_all_pages(self, urls: List[str], delay: float = 2.0) -> Dict[str, bool]:
        """
        爬取所有页面
        
        Args:
            urls: URL 列表
            delay: 页面间延迟（秒）
            
        Returns:
            爬取结果字典 {url: success}
        """
        print(f"开始爬取 {len(urls)} 个页面...")
        
        results = {}
        total = len(urls)
        
        for i, url in enumerate(urls, 1):
            print(f"\n进度: {i}/{total} ({i/total*100:.1f}%)")
            print(f"当前爬取: {url}")
            
            success = await self.crawl_single_page_with_power_crawler(url)
            results[url] = success
            
            # 添加延迟，避免过于频繁的请求
            if i < total:
                print(f"等待 {delay} 秒...")
                await asyncio.sleep(delay)
        
        return results
    
    def generate_summary_report(self, results: Dict[str, bool], output_file: str = "deep_crawl_report.md"):
        """
        生成爬取摘要报告
        
        Args:
            results: 爬取结果字典
            output_file: 输出文件名
        """
        print(f"\n生成爬取摘要报告: {output_file}")
        
        total_urls = len(results)
        successful_urls = sum(1 for success in results.values() if success)
        failed_urls = total_urls - successful_urls
        elapsed_time = time.time() - self.start_time
        
        # 保存到输出目录
        output_path = os.path.join(self.output_dir, output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {self.domain} 深度爬取报告\n\n")
            f.write(f"**爬取时间**: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time))}\n")
            f.write(f"**耗时**: {elapsed_time:.2f} 秒\n")
            f.write(f"**浏览器模式**: {'有头模式' if not self.headless else '无头模式'}\n")
            f.write(f"**输出目录**: {self.output_dir}\n")
            f.write(f"**总 URL 数**: {total_urls}\n")
            f.write(f"**成功爬取**: {successful_urls}\n")
            f.write(f"**失败数量**: {failed_urls}\n")
            f.write(f"**成功率**: {successful_urls/total_urls*100:.1f}%\n\n")
            
            f.write("## 爬取详情\n\n")
            f.write("| 序号 | URL | 状态 |\n")
            f.write("|------|-----|------|\n")
            
            for i, (url, success) in enumerate(results.items(), 1):
                status = "✅ 成功" if success else "❌ 失败"
                f.write(f"| {i} | {url} | {status} |\n")
            
            f.write("\n## 成功爬取的页面\n\n")
            for url, success in results.items():
                if success:
                    f.write(f"- {url}\n")
            
            f.write("\n## 失败的页面\n\n")
            for url, success in results.items():
                if not success:
                    f.write(f"- {url}\n")
            
            f.write(f"\n## 输出文件\n\n")
            f.write(f"所有爬取的内容都保存在 `{self.output_dir}` 目录中。\n")
            
            # 列出输出目录中的文件
            if os.path.exists(self.output_dir):
                files = os.listdir(self.output_dir)
                if files:
                    f.write("\n**生成的文件:**\n")
                    for file in sorted(files):
                        f.write(f"- {file}\n")
        
        print(f"报告已保存到: {output_path}")
        print(f"爬取完成! 成功: {successful_urls}/{total_urls}")
        print(f"总耗时: {elapsed_time:.2f} 秒")
        print(f"所有内容已保存到: {self.output_dir}")
    
    async def run_full_crawl(self, max_depth: int = 3, max_pages: int = 100, delay: float = 2.0):
        """
        运行完整的深度爬取流程
        
        Args:
            max_depth: 爬取深度
            max_pages: 最大页面数量
            delay: 页面间延迟
        """
        print("=" * 60)
        print(f"开始 {self.domain} 的完整深度爬取")
        print(f"浏览器模式: {'有头模式' if not self.headless else '无头模式'}")
        print("=" * 60)
        
        # 第一步：发现所有 URL
        urls = await self.discover_all_urls(max_depth, max_pages)
        
        if not urls:
            print("没有发现任何 URL，爬取结束")
            return
        
        print(f"\n发现 {len(urls)} 个 URL:")
        for i, url in enumerate(urls[:10], 1):  # 只显示前10个
            print(f"  {i}. {url}")
        if len(urls) > 10:
            print(f"  ... 还有 {len(urls) - 10} 个 URL")
        
        # 第二步：爬取所有页面
        results = await self.crawl_all_pages(urls, delay)
        
        # 第三步：生成报告
        self.generate_summary_report(results)
        
        print("\n" + "=" * 60)
        print("深度爬取完成!")
        print(f"所有内容已保存到: {self.output_dir}")
        print("=" * 60)


async def main():
    """主函数"""
    if len(sys.argv) == 1:
        print("使用方法: python deep_crawler.py [--depth N] [--max-pages N] [--delay N] [--visible]")
        print("参数说明:")
        print("  --depth N        爬取深度 (默认: 3)")
        print("  --max-pages N    最大页面数 (默认: 100)")
        print("  --delay N        页面间延迟秒数 (默认: 2)")
        print("  --visible        显示浏览器窗口 (默认: 无头模式)")
        print("示例: python deep_crawler.py --depth 2 --max-pages 50 --delay 3 --visible")
        print("\n注意: 确保 power_crawler.py 在同一目录下")
        return
    
    # 解析命令行参数
    max_depth = 3
    max_pages = 100
    delay = 2.0
    headless = True  # 默认无头模式
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--depth" and i + 1 < len(sys.argv):
            try:
                max_depth = int(sys.argv[i + 1])
                i += 2
            except ValueError:
                print(f"错误: --depth 参数必须是整数，收到: {sys.argv[i + 1]}")
                return
        elif sys.argv[i] == "--max-pages" and i + 1 < len(sys.argv):
            try:
                max_pages = int(sys.argv[i + 1])
                i += 2
            except ValueError:
                print(f"错误: --max-pages 参数必须是整数，收到: {sys.argv[i + 1]}")
                return
        elif sys.argv[i] == "--delay" and i + 1 < len(sys.argv):
            try:
                delay = float(sys.argv[i + 1])
                i += 2
            except ValueError:
                print(f"错误: --delay 参数必须是数字，收到: {sys.argv[i + 1]}")
                return
        elif sys.argv[i] == "--visible":
            headless = False
            i += 1
        else:
            i += 1
    
    print(f"配置参数:")
    print(f"  爬取深度: {max_depth}")
    print(f"  最大页面数: {max_pages}")
    print(f"  页面间延迟: {delay} 秒")
    print(f"  浏览器模式: {'有头模式' if not headless else '无头模式'}")
    
    # 检查 power_crawler.py 是否存在
    if not os.path.exists("power_crawler.py"):
        print("错误: power_crawler.py 文件不存在，请确保它在同一目录下")
        return
    
    # 创建深度爬虫实例
    crawler = DeepCrawler(headless=headless)
    
    # 运行完整爬取
    await crawler.run_full_crawl(max_depth, max_pages, delay)


if __name__ == "__main__":
    asyncio.run(main())
