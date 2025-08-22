#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Power Web Crawler for KKDaxue
专门用于爬取 kkdaxue.com 上所有展开按钮的爬虫
"""

import asyncio
import sys
import os
import uuid
from datetime import datetime
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig


class PowerCrawler:
    """专门用于展开按钮的爬虫"""
    
    def __init__(self, headless: bool = True, output_dir: str = None):
        self.headless = headless
        self.output_dir = output_dir
        
    async def crawl_with_expand_buttons(self, url: str) -> bool:
        """爬取并点击所有展开按钮"""
        try:
            # 配置浏览器
            browser_config = BrowserConfig(
                browser_type="chromium",
                headless=self.headless,
                verbose=True,
                java_script_enabled=True
            )
            
            async with AsyncWebCrawler(config=browser_config) as crawler:
                print(f"正在爬取: {url}")
                print(f"浏览器模式: {'有头模式' if not self.headless else '无头模式'}")
                print("开始点击所有展开按钮...")
                
                # 第一轮：点击所有展开按钮
                js_commands = [
                    "window.scrollTo(0, document.body.scrollHeight);",
                    # 查找并点击所有包含"展开"的按钮
                    """
                    const expandButtons = Array.from(document.querySelectorAll('button, a, span, div')).filter(el => {
                        const text = el.textContent || el.innerText || '';
                        return text.includes('展开') || text.includes('展开更多') || text.includes('显示更多');
                    });
                    console.log('找到展开按钮数量:', expandButtons.length);
                    expandButtons.forEach((btn, index) => {
                        if (btn.offsetParent !== null && btn.style.display !== 'none') {
                            btn.click();
                            console.log('点击了第', index + 1, '个展开按钮');
                        }
                    });
                    """
                ]
                
                config = CrawlerRunConfig(
                    js_code=js_commands, 
                    session_id="kkdaxue_session",
                    wait_for_timeout=10000,
                    delay_before_return_html=5.0
                )
                
                print("执行第一轮展开...")
                result = await crawler.arun(url=url, config=config)
                
                if not result or not result.markdown:
                    print("第一轮爬取失败")
                    return False
                
                print(f"第一轮完成，内容长度: {len(result.markdown)} 字符")
                
                # 等待一下让内容加载
                await asyncio.sleep(5)
                
                # 第二轮：再次点击可能新出现的展开按钮，使用相同的session_id
                js_commands_round2 = [
                    "window.scrollTo(0, document.body.scrollHeight);",
                    # 第二轮查找并点击展开按钮
                    """
                    const expandButtons2 = Array.from(document.querySelectorAll('button, a, span, div')).filter(el => {
                        const text = el.textContent || el.innerText || '';
                        return text.includes('展开') || text.includes('展开更多') || text.includes('显示更多');
                    });
                    console.log('第二轮找到展开按钮数量:', expandButtons2.length);
                    expandButtons2.forEach((btn, index) => {
                        if (btn.offsetParent !== null && btn.style.display !== 'none') {
                            btn.click();
                            console.log('第二轮点击了第', index + 1, '个展开按钮');
                        }
                    });
                    """
                ]
                
                config2 = CrawlerRunConfig(
                    js_code=js_commands_round2, 
                    session_id="kkdaxue_session",
                    js_only=True,
                    wait_for_timeout=10000,
                    delay_before_return_html=5.0
                )
                
                print("执行第二轮展开...")
                result2 = await crawler.arun(url=url, config=config2)
                
                if not result2 or not result2.markdown:
                    print("第二轮爬取失败")
                    return False
                
                print(f"第二轮完成，内容长度: {len(result2.markdown)} 字符")
                
                # 第三轮：最后一次尝试展开，使用相同的session_id
                js_commands_round3 = [
                    "window.scrollTo(0, document.body.scrollHeight);",
                    # 第三轮查找并点击展开按钮
                    """
                    const expandButtons3 = Array.from(document.querySelectorAll('button, a, span, div')).filter(el => {
                        const text = el.textContent || el.innerText || '';
                        return text.includes('展开') || text.includes('展开更多') || text.includes('显示更多');
                    });
                    console.log('第三轮找到展开按钮数量:', expandButtons3.length);
                    expandButtons3.forEach((btn, index) => {
                        if (btn.offsetParent !== null && btn.style.display !== 'none') {
                            btn.click();
                            console.log('第三轮点击了第', index + 1, '个展开按钮');
                        }
                    });
                    """
                ]
                
                config3 = CrawlerRunConfig(
                    js_code=js_commands_round3, 
                    session_id="kkdaxue_session",
                    js_only=True,
                    wait_for_timeout=10000,
                    delay_before_return_html=5.0
                )
                
                print("执行第三轮展开...")
                result3 = await crawler.arun(url=url, config=config3)
                
                if not result3 or not result3.markdown:
                    print("第三轮爬取失败")
                    return False
                
                print(f"第三轮完成，内容长度: {len(result3.markdown)} 字符")
                
                # 保存最终结果到指定文件夹
                if self.output_dir:
                    # 生成文件名，使用URL的页码信息
                    page_num = url.split('current=')[-1] if 'current=' in url else 'unknown'
                    filename = f"page_{page_num}_fully_expanded.md"
                    filepath = os.path.join(self.output_dir, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(f"# {getattr(result3, 'title', 'N/A')}\n\n")
                        f.write(f"URL: {result3.url}\n\n")
                        f.write(f"页码: {page_num}\n\n")
                        f.write("---\n\n")
                        f.write(str(result3.markdown))
                    
                    print(f"已保存到: {filepath}")
                    print(f"最终内容长度: {len(result3.markdown)} 字符")
                
                return True
                
        except Exception as e:
            print(f"爬取失败: {e}")
            return False


async def main():
    """主函数"""
    # 创建唯一的输出文件夹
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]  # 使用UUID的前8位
    output_dir = f"crawl_results_{timestamp}_{unique_id}"
    
    # 确保文件夹存在
    os.makedirs(output_dir, exist_ok=True)
    print(f"创建输出文件夹: {output_dir}")
    
    # 保存任务信息
    task_info_file = os.path.join(output_dir, "task_info.txt")
    with open(task_info_file, 'w', encoding='utf-8') as f:
        f.write(f"爬取任务开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"输出文件夹: {output_dir}\n")
        f.write(f"任务ID: {unique_id}\n\n")
    
    print(f"任务信息已保存到: {task_info_file}")

    # 爬取多个页面
    for i in range(1, 986):
        url = f"https://www.kkdaxue.com/?current={i}"
        print(f"\n{'='*50}")
        print(f"开始爬取第 {i} 页: {url}")
        print(f"{'='*50}")
        
        crawler = PowerCrawler(headless=False, output_dir=output_dir)
        success = await crawler.crawl_with_expand_buttons(url)
        
        if success:
            print(f"第 {i} 页爬取完成!")
        else:
            print(f"第 {i} 页爬取失败!")
    
    # 保存任务完成信息
    completion_info_file = os.path.join(output_dir, "completion_info.txt")
    with open(completion_info_file, 'w', encoding='utf-8') as f:
        f.write(f"爬取任务完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"输出文件夹: {output_dir}\n")
        f.write(f"任务ID: {unique_id}\n")
    
    print(f"\n{'='*50}")
    print(f"所有页面爬取完成!")
    print(f"结果保存在文件夹: {output_dir}")
    print(f"任务完成信息: {completion_info_file}")
    print(f"{'='*50}")


async def main_major():
    """主函数"""
    # 创建唯一的输出文件夹
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]  # 使用UUID的前8位
    output_dir = f"crawl_results_{timestamp}_{unique_id}"
    
    # 确保文件夹存在
    os.makedirs(output_dir, exist_ok=True)
    print(f"创建输出文件夹: {output_dir}")
    
    # 保存任务信息
    task_info_file = os.path.join(output_dir, "task_info.txt")
    with open(task_info_file, 'w', encoding='utf-8') as f:
        f.write(f"爬取任务开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"输出文件夹: {output_dir}\n")
        f.write(f"任务ID: {unique_id}\n\n")
    
    print(f"任务信息已保存到: {task_info_file}")

    # 爬取多个页面
    for i in range(1, 986):
        url = f"https://www.kkdaxue.com/?current={i}"
        print(f"\n{'='*50}")
        print(f"开始爬取第 {i} 页: {url}")
        print(f"{'='*50}")
        
        crawler = PowerCrawler(headless=False, output_dir=output_dir)
        success = await crawler.crawl_with_expand_buttons(url)
        
        if success:
            print(f"第 {i} 页爬取完成!")
        else:
            print(f"第 {i} 页爬取失败!")
    
    # 保存任务完成信息
    completion_info_file = os.path.join(output_dir, "completion_info.txt")
    with open(completion_info_file, 'w', encoding='utf-8') as f:
        f.write(f"爬取任务完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"输出文件夹: {output_dir}\n")
        f.write(f"任务ID: {unique_id}\n")
    
    print(f"\n{'='*50}")
    print(f"所有页面爬取完成!")
    print(f"结果保存在文件夹: {output_dir}")
    print(f"任务完成信息: {completion_info_file}")
    print(f"{'='*50}")


if __name__ == "__main__":
    asyncio.run(main())
