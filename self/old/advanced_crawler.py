#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Interactive Web Crawler
高级交互式网页爬虫
"""

import asyncio
import sys
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig


class AdvancedCrawler:
    """高级交互爬虫"""
    
    def __init__(self, headless: bool = True):
        self.browser_config = BrowserConfig(
            headless=headless,
            java_script_enabled=True,
            verbose=True
        )
    
    async def crawl_with_expand(self, url: str) -> bool:
        """爬取并展开所有隐藏内容"""
        try:
            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                print(f"正在爬取并展开: {url}")
                
                # 展开所有内容的 JavaScript 代码
                expand_js = """
                async function expandAll() {
                    let expanded = 0;
                    let rounds = 0;
                    const maxRounds = 5;
                    
                    while (rounds < maxRounds) {
                        rounds++;
                        console.log(`第 ${rounds} 轮展开...`);
                        
                        const buttons = document.querySelectorAll('button, a, span, div');
                        let found = 0;
                        
                        buttons.forEach(btn => {
                            const text = btn.textContent || btn.innerText || '';
                            if (text.includes('展开') || text.includes('展开更多') || 
                                text.includes('显示更多') || text.includes('查看更多')) {
                                try {
                                    if (btn.offsetParent !== null && btn.style.display !== 'none') {
                                        btn.click();
                                        found++;
                                        expanded++;
                                    }
                                } catch (e) {}
                            }
                        });
                        
                        console.log(`第 ${rounds} 轮找到并点击了 ${found} 个按钮`);
                        
                        if (found === 0) break;
                        
                        // 等待内容加载
                        await new Promise(r => setTimeout(r, 1000));
                    }
                    
                    console.log(`总共展开 ${expanded} 个内容`);
                    return expanded;
                }
                
                expandAll();
                """
                
                config = CrawlerRunConfig(
                    js_code=expand_js,
                    wait_for_timeout=10000,
                    delay_before_return_html=3.0,
                    page_timeout=60000
                )
                
                result = await crawler.arun(url=url, config=config)
                
                if result and result.markdown:
                    print(f"爬取成功! 内容长度: {len(result.markdown)} 字符")
                    
                    # 保存结果
                    filename = f"expanded_{url.split('//')[-1].split('/')[0].replace('.', '_')}.md"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"# {getattr(result, 'title', 'N/A')}\n\n")
                        f.write(f"URL: {result.url}\n\n")
                        f.write("---\n\n")
                        f.write(str(result.markdown))
                    
                    print(f"已保存到: {filename}")
                    return True
                else:
                    print("爬取失败")
                    return False
                    
        except Exception as e:
            print(f"爬取失败: {e}")
            return False


async def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python advanced_crawler.py <URL>")
        print("示例: python advanced_crawler.py https://www.kkdaxue.com/")
        return
    
    url = sys.argv[1]
    
    if not url.startswith(('http://', 'https://')):
        print("错误: 请提供有效的 HTTP/HTTPS URL")
        return
    
    crawler = AdvancedCrawler()
    success = await crawler.crawl_with_expand(url)
    
    if success:
        print("高级爬取完成!")
    else:
        print("高级爬取失败!")


if __name__ == "__main__":
    asyncio.run(main())
