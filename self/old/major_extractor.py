#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Major Options Extractor for KKDaxue
专门用于提取 kkdaxue.com 上"专业"按钮下的所有选项
"""

import asyncio
import os
import uuid
from datetime import datetime
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig


class MajorExtractor:
    """专门用于提取专业选项的爬虫"""
    
    def __init__(self, headless: bool = True, output_dir: str = None):
        self.headless = headless
        self.output_dir = output_dir
        
    async def extract_major_options(self, url: str) -> list:
        """提取专业按钮下的所有选项"""
        try:
            # 配置浏览器
            browser_config = BrowserConfig(
                browser_type="chromium",
                headless=self.headless,
                verbose=True,
                java_script_enabled=True
            )
            
            async with AsyncWebCrawler(config=browser_config) as crawler:
                print(f"正在访问: {url}")
                print(f"浏览器模式: {'有头模式' if not self.headless else '无头模式'}")
                print("开始提取专业选项...")
                
                # 第一步：等待页面完全加载，然后查找并点击"专业"按钮
                js_commands_step1 = [
                    # 等待页面完全加载
                    "await new Promise(resolve => setTimeout(resolve, 3000));",
                    # 滚动到页面顶部
                    "window.scrollTo(0, 0);",
                    # 等待一下
                    "await new Promise(resolve => setTimeout(resolve, 1000));",
                    # 查找并点击"专业"按钮 - 多种查找策略
                    """
                    let majorButton = null;
                    
                    // 策略1: 查找包含"专业"的按钮
                    const buttons = Array.from(document.querySelectorAll('button, a, span, div, li, label'));
                    for (const btn of buttons) {
                        const text = btn.textContent || btn.innerText || '';
                        if (text.includes('专业') && text.trim().length <= 10) {
                            console.log('策略1找到专业按钮:', text.trim());
                            majorButton = btn;
                            break;
                        }
                    }
                    
                    // 策略2: 查找包含"专业"的label或span
                    if (!majorButton) {
                        const labels = Array.from(document.querySelectorAll('label, span'));
                        for (const label of labels) {
                            const text = label.textContent || label.innerText || '';
                            if (text.includes('专业') && text.trim().length <= 10) {
                                console.log('策略2找到专业标签:', text.trim());
                                majorButton = label;
                                break;
                            }
                        }
                    }
                    
                    // 策略3: 查找包含"专业"的div
                    if (!majorButton) {
                        const divs = Array.from(document.querySelectorAll('div'));
                        for (const div of divs) {
                            const text = div.textContent || div.innerText || '';
                            if (text.includes('专业') && text.trim().length <= 10) {
                                console.log('策略3找到专业div:', text.trim());
                                majorButton = div;
                                break;
                            }
                        }
                    }
                    
                    if (majorButton) {
                        console.log('找到专业按钮:', majorButton.textContent);
                        console.log('按钮类型:', majorButton.tagName);
                        console.log('按钮类名:', majorButton.className);
                        
                        // 尝试点击
                        try {
                            majorButton.click();
                            console.log('已点击专业按钮');
                            
                            // 等待下拉菜单展开
                            await new Promise(resolve => setTimeout(resolve, 2000));
                            
                            return true;
                        } catch (e) {
                            console.log('点击失败，尝试其他方法:', e);
                            // 尝试触发事件
                            majorButton.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                            await new Promise(resolve => setTimeout(resolve, 2000));
                            return true;
                        }
                    } else {
                        console.log('未找到专业按钮');
                        return false;
                    }
                    """
                ]
                
                config1 = CrawlerRunConfig(
                    js_code=js_commands_step1, 
                    session_id="major_extraction_session",
                    wait_for_timeout=10000,
                    delay_before_return_html=5.0
                )
                
                print("步骤1: 查找并点击专业按钮...")
                result1 = await crawler.arun(url=url, config=config1)
                
                if not result1:
                    print("步骤1失败")
                    return []
                
                print("专业按钮点击成功，等待下拉菜单展开...")
                # 额外等待5秒确保下拉菜单完全展开
                await asyncio.sleep(5)
                
                # 第二步：提取下拉菜单中的所有选项
                js_commands_step2 = [
                    """
                    // 等待下拉菜单完全展开
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    
                    console.log('开始查找专业选项...');
                    
                    // 查找可能的下拉菜单容器 - 扩展选择器
                    const dropdownSelectors = [
                        'select option',
                        '.dropdown-menu li',
                        '.menu li',
                        '.options li',
                        '.list li',
                        '[role="menu"] li',
                        '[role="listbox"] option',
                        '.select-options li',
                        '.filter-options li',
                        '.dropdown li',
                        '.select-dropdown li',
                        '.filter li',
                        '.option-list li',
                        '.choice-list li',
                        '.item-list li',
                        '.select-item li',
                        '.filter-item li',
                        '.dropdown-item',
                        '.select-option',
                        '.filter-option',
                        '.menu-item',
                        '.list-item'
                    ];
                    
                    let majorOptions = [];
                    let foundSelector = '';
                    
                    // 遍历所有选择器查找选项
                    for (const selector of dropdownSelectors) {
                        const elements = document.querySelectorAll(selector);
                        if (elements.length > 0) {
                            console.log('找到选择器:', selector, '元素数量:', elements.length);
                            foundSelector = selector;
                            
                            for (const el of elements) {
                                const text = el.textContent || el.innerText || '';
                                const trimmedText = text.trim();
                                
                                // 过滤掉空文本和"专业"本身
                                if (trimmedText && 
                                    trimmedText !== '专业' && 
                                    !trimmedText.includes('专业：') &&
                                    trimmedText.length > 1 && 
                                    trimmedText.length < 100) {
                                    
                                    majorOptions.push(trimmedText);
                                    console.log('添加选项:', trimmedText);
                                }
                            }
                            
                            if (majorOptions.length > 0) {
                                console.log('使用选择器', selector, '找到选项数量:', majorOptions.length);
                                break;
                            }
                        }
                    }
                    
                    // 如果没有找到，尝试查找所有可见的文本元素
                    if (majorOptions.length === 0) {
                        console.log('尝试查找所有可见文本元素...');
                        
                        const allElements = document.querySelectorAll('*');
                        for (const el of allElements) {
                            // 检查元素是否可见
                            const style = window.getComputedStyle(el);
                            if (style.display === 'none' || style.visibility === 'hidden') continue;
                            
                            const text = el.textContent || el.innerText || '';
                            const trimmedText = text.trim();
                            
                            // 检查是否看起来像专业名称
                            if (trimmedText && 
                                trimmedText.length > 2 && 
                                trimmedText.length < 50 &&
                                !trimmedText.includes('专业') &&
                                !trimmedText.includes('选择') &&
                                !trimmedText.includes('请选择')) {
                                
                                // 检查是否包含专业相关关键词
                                const majorKeywords = ['工程', '科学', '技术', '管理', '经济', '文学', '艺术', '医学', '法律', '教育', '农业', '计算机', '软件', '数据', '人工智能', '机械', '电子', '化学', '物理', '数学', '历史', '哲学', '心理学', '社会学', '政治学', '国际关系', '新闻', '传播', '设计', '建筑', '土木', '环境', '生物', '护理', '药学', '口腔', '临床', '预防', '康复', '中医', '针灸', '推拿', '中药', '西药', '药剂', '药事', '药管', '药监', '药检', '药研', '药开', '药制', '药分', '药化', '药生', '药代', '药动', '药效', '药毒', '药安', '药质', '药标', '药典', '药方', '药膳', '药茶', '药酒', '药浴', '药熏', '药贴', '药膏', '药丸', '药片', '药粉', '药液', '药膏', '药油', '药水'];
                                
                                for (const keyword of majorKeywords) {
                                    if (trimmedText.includes(keyword)) {
                                        majorOptions.push(trimmedText);
                                        console.log('通过关键词匹配添加:', trimmedText);
                                        break;
                                    }
                                }
                            }
                        }
                    }
                    
                    // 去重并返回
                    majorOptions = [...new Set(majorOptions)];
                    console.log('最终找到的专业选项数量:', majorOptions.length);
                    console.log('专业选项:', majorOptions);
                    console.log('使用的选择器:', foundSelector);
                    
                    return {
                        options: majorOptions,
                        selector: foundSelector,
                        count: majorOptions.length
                    };
                    """
                ]
                
                config2 = CrawlerRunConfig(
                    js_code=js_commands_step2, 
                    session_id="major_extraction_session",
                    js_only=True,
                    wait_for_timeout=15000,
                    delay_before_return_html=5.0
                )
                
                print("步骤2: 提取专业选项...")
                result2 = await crawler.arun(url=url, config=config2)
                
                if result2 and result2.markdown:
                    try:
                        # 尝试解析JavaScript返回的结果
                        import json
                        import re
                        
                        # 查找JavaScript返回的结果
                        js_result_match = re.search(r'return\s*\{[^}]*options[^}]*\};', str(result2.markdown))
                        if js_result_match:
                            print("JavaScript执行成功，正在解析结果...")
                            # 这里需要进一步处理JavaScript返回的数据
                            pass
                        
                        # 如果JavaScript没有返回预期结果，尝试从页面内容中提取
                        page_content = str(result2.markdown)
                        major_options = self._parse_major_options_from_text(page_content)
                        
                        if major_options:
                            print(f"通过页面内容解析找到 {len(major_options)} 个专业选项")
                            return major_options
                            
                    except Exception as e:
                        print(f"解析JavaScript结果失败: {e}")
                
                # 第三步：获取页面HTML，手动解析专业选项
                js_commands_step3 = [
                    """
                    // 获取页面所有文本内容，用于手动分析
                    const pageText = document.body.innerText || document.body.textContent || '';
                    return pageText;
                    """
                ]
                
                config3 = CrawlerRunConfig(
                    js_code=js_commands_step3, 
                    session_id="major_extraction_session",
                    js_only=True,
                    wait_for_timeout=5000,
                    delay_before_return_html=2.0
                )
                
                print("步骤3: 获取页面文本内容...")
                result3 = await crawler.arun(url=url, config=config3)
                
                if result3 and result3.markdown:
                    # 手动解析页面内容，查找专业选项
                    page_content = str(result3.markdown)
                    major_options = self._parse_major_options_from_text(page_content)
                    
                    if major_options:
                        print(f"通过文本解析找到 {len(major_options)} 个专业选项")
                        return major_options
                
                print("未能成功提取专业选项")
                return []
                
        except Exception as e:
            print(f"提取失败: {e}")
            return []
    
    def _parse_major_options_from_text(self, text: str) -> list:
        """从页面文本中手动解析专业选项"""
        # 常见专业关键词
        major_keywords = [
            '计算机科学与技术', '软件工程', '数据科学与大数据技术', '人工智能', '网络工程', '信息安全',
            '电子信息工程', '通信工程', '自动化', '电气工程及其自动化', '机械工程', '机械设计制造及其自动化',
            '土木工程', '建筑学', '城乡规划', '环境工程', '化学工程与工艺', '材料科学与工程',
            '生物工程', '生物技术', '临床医学', '口腔医学', '护理学', '药学', '中药学',
            '经济学', '金融学', '国际经济与贸易', '工商管理', '会计学', '财务管理', '市场营销',
            '法学', '政治学与行政学', '国际政治', '外交学', '新闻学', '传播学', '广告学',
            '汉语言文学', '英语', '日语', '德语', '法语', '西班牙语', '俄语',
            '历史学', '哲学', '社会学', '心理学', '教育学', '学前教育', '小学教育',
            '数学与应用数学', '物理学', '化学', '生物科学', '地理科学', '地质学',
            '艺术设计', '视觉传达设计', '环境设计', '产品设计', '服装与服饰设计',
            '音乐学', '舞蹈学', '戏剧影视文学', '广播电视编导', '播音与主持艺术'
        ]
        
        found_majors = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if len(line) > 2 and len(line) < 50:
                # 检查是否包含专业关键词
                for keyword in major_keywords:
                    if keyword in line:
                        found_majors.append(line)
                        break
                
                # 检查是否看起来像专业名称（包含常见后缀）
                if any(suffix in line for suffix in ['专业', '学', '工程', '技术', '管理', '科学']):
                    if line not in found_majors:
                        found_majors.append(line)
        
        # 去重并排序
        found_majors = list(set(found_majors))
        found_majors.sort()
        
        return found_majors


async def main():
    """主函数"""
    # 创建唯一的输出文件夹
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]  # 使用UUID的前8位
    output_dir = f"major_extraction_{timestamp}_{unique_id}"
    
    # 确保文件夹存在
    os.makedirs(output_dir, exist_ok=True)
    print(f"创建输出文件夹: {output_dir}")
    
    # 保存任务信息
    task_info_file = os.path.join(output_dir, "task_info.txt")
    with open(task_info_file, 'w', encoding='utf-8') as f:
        f.write(f"专业选项提取任务开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"输出文件夹: {output_dir}\n")
        f.write(f"任务ID: {unique_id}\n")
        f.write(f"目标网站: https://www.kkdaxue.com/\n\n")
    
    print(f"任务信息已保存到: {task_info_file}")

    # 开始提取专业选项
    url = "https://www.kkdaxue.com/"
    print(f"\n{'='*50}")
    print(f"开始提取专业选项: {url}")
    print(f"{'='*50}")
    
    extractor = MajorExtractor(headless=False, output_dir=output_dir)
    major_options = await extractor.extract_major_options(url)
    
    if major_options:
        print(f"\n成功提取到 {len(major_options)} 个专业选项:")
        for i, major in enumerate(major_options, 1):
            print(f"  {i:3d}. {major}")
        
        # 保存结果
        results_file = os.path.join(output_dir, "major_options.txt")
        with open(results_file, 'w', encoding='utf-8') as f:
            f.write(f"专业选项提取结果\n")
            f.write(f"提取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"目标网站: {url}\n")
            f.write(f"选项总数: {len(major_options)}\n")
            f.write(f"{'='*50}\n\n")
            
            for i, major in enumerate(major_options, 1):
                f.write(f"{i:3d}. {major}\n")
        
        # 保存为Python列表格式
        python_list_file = os.path.join(output_dir, "major_options.py")
        with open(python_list_file, 'w', encoding='utf-8') as f:
            f.write("# 专业选项列表\n")
            f.write("major_options = [\n")
            for major in major_options:
                f.write(f'    "{major}",\n')
            f.write("]\n\n")
            f.write(f"# 总数: {len(major_options)}\n")
        
        print(f"\n结果已保存到:")
        print(f"  - 文本格式: {results_file}")
        print(f"  - Python列表: {python_list_file}")
        
    else:
        print("未能提取到任何专业选项")
        
        # 保存失败信息
        failure_file = os.path.join(output_dir, "extraction_failed.txt")
        with open(failure_file, 'w', encoding='utf-8') as f:
            f.write(f"专业选项提取失败\n")
            f.write(f"失败时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"目标网站: {url}\n")
            f.write("可能原因:\n")
            f.write("1. 网站结构发生变化\n")
            f.write("2. 专业按钮未找到\n")
            f.write("3. 下拉菜单未正确展开\n")
            f.write("4. 页面加载时间不足\n")
        
        print(f"失败信息已保存到: {failure_file}")
    
    # 保存任务完成信息
    completion_info_file = os.path.join(output_dir, "completion_info.txt")
    with open(completion_info_file, 'w', encoding='utf-8') as f:
        f.write(f"专业选项提取任务完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"输出文件夹: {output_dir}\n")
        f.write(f"任务ID: {unique_id}\n")
        f.write(f"提取结果: {'成功' if major_options else '失败'}\n")
        if major_options:
            f.write(f"选项数量: {len(major_options)}\n")
    
    print(f"\n{'='*50}")
    print(f"专业选项提取任务完成!")
    print(f"结果保存在文件夹: {output_dir}")
    print(f"任务完成信息: {completion_info_file}")
    print(f"{'='*50}")


if __name__ == "__main__":
    asyncio.run(main())
