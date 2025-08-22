#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Interactive Web Crawler using crawl4ai
高级交互式网页爬虫，支持复杂的页面交互功能
"""

import asyncio
import sys
import time
from typing import Optional, List, Dict, Any
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.models import CrawlResult


class AdvancedInteractiveCrawler:
    """高级交互式网页爬虫类"""
    
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
            java_script_enabled=True
        )
        
        # 基础爬取配置
        self.base_config = CrawlerRunConfig(
            screenshot=False,
            scan_full_page=True,
            scroll_delay=0.3,
            wait_until="networkidle",
            page_timeout=60000,  # 60秒超时
            verbose=True
        )
        
        # 预定义的交互策略
        self.interaction_strategies = {
            "expand_all": {
                "name": "展开所有隐藏内容",
                "description": "点击所有展开按钮，展开隐藏的内容",
                "js_code": """
                async function expandAllContent() {
                    let totalExpanded = 0;
                    let maxIterations = 10; // 最大迭代次数
                    let iteration = 0;
                    
                    while (iteration < maxIterations) {
                        iteration++;
                        console.log(`第 ${iteration} 轮展开操作...`);
                        
                        // 查找所有可能的展开按钮
                        const expandSelectors = [
                            'button:contains("展开")',
                            'button:contains("展开更多")',
                            'button:contains("显示更多")',
                            'button:contains("查看更多")',
                            'a:contains("展开")',
                            'span:contains("展开")',
                            '.expand-button',
                            '.show-more',
                            '.read-more',
                            '.collapse-toggle',
                            '[data-toggle="collapse"]'
                        ];
                        
                        let foundButtons = [];
                        
                        // 查找文本包含展开关键词的元素
                        const allElements = document.querySelectorAll('button, a, span, div, p');
                        allElements.forEach(element => {
                            const text = element.textContent || element.innerText || '';
                            if (text.includes('展开') || text.includes('展开更多') || 
                                text.includes('显示更多') || text.includes('查看更多') ||
                                text.includes('展开全部') || text.includes('显示全部')) {
                                foundButtons.push(element);
                            }
                        });
                        
                        // 查找特定类名的元素
                        const classElements = document.querySelectorAll('.expand-button, .show-more, .read-more, .collapse-toggle');
                        classElements.forEach(element => {
                            if (!foundButtons.includes(element)) {
                                foundButtons.push(element);
                            }
                        });
                        
                        // 查找 data-toggle 属性为 collapse 的元素
                        const dataToggleElements = document.querySelectorAll('[data-toggle="collapse"]');
                        dataToggleElements.forEach(element => {
                            if (!foundButtons.includes(element)) {
                                foundButtons.push(element);
                            }
                        });
                        
                        console.log(`第 ${iteration} 轮找到 ${foundButtons.length} 个展开按钮`);
                        
                        if (foundButtons.length === 0) {
                            console.log('没有找到更多展开按钮，停止迭代');
                            break;
                        }
                        
                        let clickedCount = 0;
                        
                        // 点击所有找到的按钮
                        for (let i = 0; i < foundButtons.length; i++) {
                            const button = foundButtons[i];
                            try {
                                if (button.offsetParent !== null && 
                                    button.style.display !== 'none' && 
                                    button.style.visibility !== 'hidden' &&
                                    button.getBoundingClientRect().width > 0) {
                                    
                                    // 滚动到按钮位置
                                    button.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                    
                                    // 等待一下再点击
                                    await new Promise(resolve => setTimeout(resolve, 200));
                                    
                                    button.click();
                                    clickedCount++;
                                    console.log(`点击了第 ${i + 1} 个展开按钮`);
                                    
                                    // 等待内容加载
                                    await new Promise(resolve => setTimeout(resolve, 500));
                                }
                            } catch (error) {
                                console.log(`点击第 ${i + 1} 个按钮失败:`, error);
                            }
                        }
                        
                        totalExpanded += clickedCount;
                        console.log(`第 ${iteration} 轮点击了 ${clickedCount} 个按钮`);
                        
                        if (clickedCount === 0) {
                            console.log('本轮没有点击任何按钮，停止迭代');
                            break;
                        }
                        
                        // 等待页面稳定
                        await new Promise(resolve => setTimeout(resolve, 1000));
                    }
                    
                    console.log(`展开操作完成，总共点击了 ${totalExpanded} 个按钮，进行了 ${iteration} 轮操作`);
                    return { totalExpanded, iterations: iteration };
                }
                
                // 执行展开操作
                expandAllContent().then(result => {
                    console.log('展开操作结果:', result);
                });
                
                // 返回结果（同步版本）
                return expandAllContent();
                """
            },
            
            "infinite_scroll": {
                "name": "无限滚动加载",
                "description": "模拟无限滚动，加载更多内容",
                "js_code": """
                async function infiniteScrollLoad() {
                    let scrollCount = 0;
                    let maxScrolls = 20; // 最大滚动次数
                    let lastHeight = document.body.scrollHeight;
                    let noChangeCount = 0;
                    
                    console.log('开始无限滚动加载...');
                    
                    while (scrollCount < maxScrolls && noChangeCount < 3) {
                        scrollCount++;
                        console.log(`第 ${scrollCount} 次滚动...`);
                        
                        // 滚动到底部
                        window.scrollTo(0, document.body.scrollHeight);
                        
                        // 等待内容加载
                        await new Promise(resolve => setTimeout(resolve, 2000));
                        
                        // 检查页面高度是否变化
                        const currentHeight = document.body.scrollHeight;
                        if (currentHeight === lastHeight) {
                            noChangeCount++;
                            console.log(`页面高度未变化 ${noChangeCount}/3`);
                        } else {
                            noChangeCount = 0;
                            console.log(`页面高度从 ${lastHeight} 增加到 ${currentHeight}`);
                        }
                        
                        lastHeight = currentHeight;
                        
                        // 查找并点击"加载更多"按钮
                        const loadMoreButtons = document.querySelectorAll('button, a, span');
                        let clickedLoadMore = false;
                        
                        for (const button of loadMoreButtons) {
                            const text = button.textContent || button.innerText || '';
                            if (text.includes('加载更多') || text.includes('Load More') || 
                                text.includes('显示更多') || text.includes('Show More')) {
                                try {
                                    if (button.offsetParent !== null && button.style.display !== 'none') {
                                        button.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                        await new Promise(resolve => setTimeout(resolve, 500));
                                        button.click();
                                        clickedLoadMore = true;
                                        console.log('点击了加载更多按钮');
                                        await new Promise(resolve => setTimeout(resolve, 2000));
                                        break;
                                    }
                                } catch (error) {
                                    console.log('点击加载更多按钮失败:', error);
                                }
                            }
                        }
                        
                        if (!clickedLoadMore) {
                            console.log('没有找到加载更多按钮');
                        }
                    }
                    
                    console.log(`无限滚动完成，总共滚动 ${scrollCount} 次`);
                    return { scrollCount, finalHeight: document.body.scrollHeight };
                }
                
                // 执行无限滚动
                infiniteScrollLoad().then(result => {
                    console.log('无限滚动结果:', result);
                });
                
                return infiniteScrollLoad();
                """
            },
            
            "tab_navigation": {
                "name": "标签页导航",
                "description": "遍历所有标签页，获取完整内容",
                "js_code": """
                async function navigateAllTabs() {
                    const tabSelectors = [
                        '.tab',
                        '.tab-item',
                        '.nav-tab',
                        '.tab-button',
                        '[role="tab"]',
                        '.tab-nav-item'
                    ];
                    
                    let allTabs = [];
                    let visitedTabs = new Set();
                    
                    // 查找所有标签页
                    tabSelectors.forEach(selector => {
                        const tabs = document.querySelectorAll(selector);
                        tabs.forEach(tab => {
                            if (!allTabs.includes(tab)) {
                                allTabs.push(tab);
                            }
                        });
                    });
                    
                    console.log(`找到 ${allTabs.length} 个标签页`);
                    
                    let tabData = [];
                    
                    // 遍历每个标签页
                    for (let i = 0; i < allTabs.length; i++) {
                        const tab = allTabs[i];
                        try {
                            if (tab.offsetParent !== null && tab.style.display !== 'none') {
                                const tabText = tab.textContent || tab.innerText || '';
                                console.log(`访问标签页 ${i + 1}: ${tabText}`);
                                
                                // 点击标签页
                                tab.click();
                                visitedTabs.add(tab);
                                
                                // 等待内容加载
                                await new Promise(resolve => setTimeout(resolve, 1000));
                                
                                // 获取当前标签页内容
                                const content = document.body.innerHTML;
                                tabData.push({
                                    index: i + 1,
                                    text: tabText,
                                    content: content.substring(0, 500) + '...' // 只保存前500字符
                                });
                                
                                console.log(`标签页 ${i + 1} 内容长度: ${content.length}`);
                            }
                        } catch (error) {
                            console.log(`访问标签页 ${i + 1} 失败:`, error);
                        }
                    }
                    
                    console.log(`标签页导航完成，访问了 ${visitedTabs.size} 个标签页`);
                    return { visitedCount: visitedTabs.size, tabData };
                }
                
                // 执行标签页导航
                navigateAllTabs().then(result => {
                    console.log('标签页导航结果:', result);
                });
                
                return navigateAllTabs();
                """
            }
        }
    
    async def crawl_with_strategy(self, url: str, strategy_name: str, 
                                custom_js: str = None, max_wait: int = 30) -> Optional[CrawlResult]:
        """
        使用指定策略爬取网页
        
        Args:
            url: 要爬取的网页 URL
            strategy_name: 策略名称
            custom_js: 自定义 JavaScript 代码
            max_wait: 最大等待时间（秒）
            
        Returns:
            CrawlResult 对象
        """
        try:
            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                print(f"正在爬取: {url}")
                print(f"使用策略: {strategy_name}")
                
                # 选择 JavaScript 代码
                if custom_js:
                    js_code = custom_js
                    print("使用自定义 JavaScript 代码")
                elif strategy_name in self.interaction_strategies:
                    js_code = self.interaction_strategies[strategy_name]["js_code"]
                    print(f"使用预定义策略: {self.interaction_strategies[strategy_name]['name']}")
                else:
                    print(f"未知策略: {strategy_name}，使用默认配置")
                    js_code = None
                
                # 创建爬取配置
                if js_code:
                    config_dict = self.base_config.__dict__.copy()
                    config_dict.update({
                        "js_code": js_code,
                        "wait_for_timeout": max_wait * 1000,
                        "delay_before_return_html": 3.0,  # 交互后等待3秒
                        "page_timeout": (max_wait + 30) * 1000  # 总超时时间
                    })
                    crawl_config = CrawlerRunConfig(**config_dict)
                else:
                    crawl_config = self.base_config
                
                print("开始执行页面交互...")
                result = await crawler.arun(url=url, config=crawl_config)
                
                return result
                
        except Exception as e:
            print(f"爬取失败: {e}")
            return None
    
    def list_strategies(self):
        """列出所有可用的策略"""
        print("可用的交互策略:")
        for name, strategy in self.interaction_strategies.items():
            print(f"  - {name}: {strategy['name']}")
            print(f"    描述: {strategy['description']}")
            print()
    
    def add_custom_strategy(self, name: str, display_name: str, description: str, js_code: str):
        """
        添加自定义交互策略
        
        Args:
            name: 策略标识符
            display_name: 显示名称
            description: 策略描述
            js_code: JavaScript 代码
        """
        self.interaction_strategies[name] = {
            "name": display_name,
            "description": description,
            "js_code": js_code
        }
        print(f"已添加自定义策略: {display_name}")
    
    def get_strategy_info(self, strategy_name: str) -> Optional[Dict[str, Any]]:
        """获取策略信息"""
        return self.interaction_strategies.get(strategy_name)


async def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python advanced_interactive_crawler.py <URL> [--strategy STRATEGY] [--custom-js FILE] [--list]")
        print("示例: python advanced_interactive_crawler.py https://www.example.com --strategy expand_all")
        print("参数说明:")
        print("  <URL>     要爬取的网页地址")
        print("  --strategy STRATEGY  使用预定义策略 (expand_all, infinite_scroll, tab_navigation)")
        print("  --custom-js FILE    使用自定义 JavaScript 文件")
        print("  --list              列出所有可用策略")
        print("  --headless          无头模式运行浏览器 (默认)")
        print("  --visible           显示浏览器窗口")
        return
    
    url = sys.argv[1]
    headless = "--visible" not in sys.argv
    
    # 检查是否要列出策略
    if "--list" in sys.argv:
        crawler = AdvancedInteractiveCrawler(headless=True)
        crawler.list_strategies()
        return
    
    # 获取策略参数
    strategy_name = None
    custom_js_file = None
    
    for i, arg in enumerate(sys.argv):
        if arg == "--strategy" and i + 1 < len(sys.argv):
            strategy_name = sys.argv[i + 1]
        elif arg == "--custom-js" and i + 1 < len(sys.argv):
            custom_js_file = sys.argv[i + 1]
    
    # 验证 URL
    if not url.startswith(('http://', 'https://')):
        print("错误: 请提供有效的 HTTP/HTTPS URL")
        return
    
    print(f"开始爬取网页: {url}")
    print(f"浏览器模式: {'无头模式' if headless else '可见模式'}")
    
    # 创建爬虫实例
    crawler = AdvancedInteractiveCrawler(headless=headless)
    
    # 读取自定义 JavaScript 代码
    custom_js = None
    if custom_js_file:
        try:
            with open(custom_js_file, 'r', encoding='utf-8') as f:
                custom_js = f.read()
            print(f"已加载自定义 JavaScript 文件: {custom_js_file}")
        except Exception as e:
            print(f"读取自定义 JavaScript 文件失败: {e}")
            return
    
    # 执行爬取
    if strategy_name or custom_js:
        result = await crawler.crawl_with_strategy(
            url=url, 
            strategy_name=strategy_name or "custom",
            custom_js=custom_js
        )
    else:
        print("请指定策略或自定义 JavaScript 代码")
        crawler.list_strategies()
        return
    
    if result:
        print("\n爬取成功!")
        print(f"页面标题: {getattr(result, 'title', 'N/A')}")
        print(f"HTML 长度: {len(result.html)} 字符")
        print(f"Markdown 长度: {len(result.markdown) if result.markdown else 0} 字符")
        
        # 保存结果
        filename = f"advanced_crawled_{url.split('//')[-1].split('/')[0].replace('.', '_')}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"URL: {result.url}\n")
                f.write(f"标题: {getattr(result, 'title', 'N/A')}\n")
                f.write("=" * 80 + "\n\n")
                f.write("## Markdown 内容\n\n")
                f.write(str(result.markdown))
                f.write("\n\n" + "=" * 80 + "\n\n")
                f.write("## HTML 内容 (前2000字符)\n\n")
                f.write(result.html[:2000] + "..." if len(result.html) > 2000 else result.html)
            
            print(f"内容已保存到: {filename}")
            
        except Exception as e:
            print(f"保存文件失败: {e}")
        
    else:
        print("爬取失败，请检查 URL 或网络连接")


if __name__ == "__main__":
    asyncio.run(main())
