#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Major Parameter Validator for KKDaxue
专门用于找出 kkdaxue.com 上 major 参数的所有合法值
"""

import asyncio
import os
import uuid
from datetime import datetime
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig


class MajorValidator:
    """专门用于验证major参数值的爬虫"""
    
    def __init__(self, headless: bool = True, output_dir: str = None):
        self.headless = headless
        self.output_dir = output_dir
        
    async def validate_major_value(self, url: str, major: str) -> dict:
        """验证单个major值是否有效"""
        try:
            # 配置浏览器
            browser_config = BrowserConfig(
                browser_type="chromium",
                headless=self.headless,
                verbose=False,  # 减少日志输出
                java_script_enabled=True
            )
            
            async with AsyncWebCrawler(config=browser_config) as crawler:
                # 构建带major参数的URL
                test_url = f"{url}?current=1&major={major}"
                
                # 简单的页面访问，检查是否有内容
                config = CrawlerRunConfig(
                    session_id=f"major_validation_{major}",
                    wait_for_timeout=5000,
                    delay_before_return_html=2.0
                )
                
                result = await crawler.arun(url=test_url, config=config)
                
                if result and result.markdown:
                    content = str(result.markdown)
                    
                    # 检查页面是否有效（不是错误页面）
                    is_valid = self._check_page_validity(content, major)
                    
                    return {
                        'major': major,
                        'url': test_url,
                        'is_valid': is_valid,
                        'content_length': len(content),
                        'has_error': '错误' in content or '404' in content or '找不到' in content,
                        'has_content': len(content.strip()) > 100
                    }
                else:
                    return {
                        'major': major,
                        'url': test_url,
                        'is_valid': False,
                        'content_length': 0,
                        'has_error': True,
                        'has_content': False
                    }
                    
        except Exception as e:
            return {
                'major': major,
                'url': f"{url}?current=1&major={major}",
                'is_valid': False,
                'content_length': 0,
                'has_error': True,
                'has_content': False,
                'error': str(e)
            }
    
    def _check_page_validity(self, content: str, major: str) -> bool:
        """检查页面内容是否有效"""
        # 检查是否包含错误信息
        error_indicators = ['错误', '404', '找不到', '页面不存在', '参数错误', '无效']
        for indicator in error_indicators:
            if indicator in content:
                return False
        
        # 检查是否有实际内容
        if len(content.strip()) < 100:
            return False
        
        # 检查是否包含专业相关信息
        if major in content:
            return True
        
        # 检查是否包含页面结构信息
        page_indicators = ['专业', '大学', '学院', '招生', '信息', '详情']
        for indicator in page_indicators:
            if indicator in content:
                return True
        
        return True
    
    async def validate_all_majors(self, base_url: str, major_list: list) -> list:
        """验证所有专业值"""
        print(f"开始验证 {len(major_list)} 个专业值...")
        
        valid_majors = []
        invalid_majors = []
        
        for i, major in enumerate(major_list, 1):
            print(f"进度: {i}/{len(major_list)} - 验证: {major}")
            
            result = await self.validate_major_value(base_url, major)
            
            if result['is_valid']:
                valid_majors.append(result)
                print(f"  ✓ 有效 - 内容长度: {result['content_length']}")
            else:
                invalid_majors.append(result)
                print(f"  ✗ 无效 - 原因: {'内容过短' if result['content_length'] < 100 else '包含错误信息'}")
            
            # 避免请求过于频繁
            await asyncio.sleep(1)
        
        return {
            'valid': valid_majors,
            'invalid': invalid_majors,
            'total': len(major_list),
            'valid_count': len(valid_majors),
            'invalid_count': len(invalid_majors)
        }


async def main():
    """主函数"""
    # 创建唯一的输出文件夹
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]  # 使用UUID的前8位
    output_dir = f"major_validation_{timestamp}_{unique_id}"
    
    # 确保文件夹存在
    os.makedirs(output_dir, exist_ok=True)
    print(f"创建输出文件夹: {output_dir}")
    
    # 保存任务信息
    task_info_file = os.path.join(output_dir, "task_info.txt")
    with open(task_info_file, 'w', encoding='utf-8') as f:
        f.write(f"Major参数验证任务开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"输出文件夹: {output_dir}\n")
        f.write(f"任务ID: {unique_id}\n")
        f.write(f"目标网站: https://www.kkdaxue.com/\n\n")
    
    print(f"任务信息已保存到: {task_info_file}")

    # 专业列表（从power_crawler.py中获取）
    major_list = [
        "计算机科学与技术", "软件工程", "汉语言文学", "英语", "临床医学", 
        "土木工程", "机械设计制造及其自动化", "法学", "电气工程及其自动化", 
        "会计学", "电子信息工程", "通信工程", "电子商务", "自动化", 
        "数学与应用数学", "学前教育", "工商管理", "市场营销", "视觉传达设计", 
        "软件技术", "国际经济与贸易", "生物科学", "金融学", "物流管理", 
        "财务管理", "计算机应用技术", "物联网工程", "数据科学与大数据技术", 
        "历史学", "物理学", "护理学", "信息管理与信息系统"
    ]
    
    print(f"专业列表包含 {len(major_list)} 个专业")
    
    # 开始验证
    base_url = "https://www.kkdaxue.com/"
    print(f"\n{'='*50}")
    print(f"开始验证major参数: {base_url}")
    print(f"{'='*50}")
    
    validator = MajorValidator(headless=False, output_dir=output_dir)
    validation_results = await validator.validate_all_majors(base_url, major_list)
    
    # 输出结果
    print(f"\n{'='*50}")
    print(f"验证完成!")
    print(f"总数: {validation_results['total']}")
    print(f"有效: {validation_results['valid_count']}")
    print(f"无效: {validation_results['invalid_count']}")
    print(f"{'='*50}")
    
    # 保存验证结果
    if validation_results['valid']:
        print(f"\n有效的专业值 ({validation_results['valid_count']} 个):")
        for i, result in enumerate(validation_results['valid'], 1):
            print(f"  {i:3d}. {result['major']} - 内容长度: {result['content_length']}")
        
        # 保存有效结果
        valid_results_file = os.path.join(output_dir, "valid_majors.txt")
        with open(valid_results_file, 'w', encoding='utf-8') as f:
            f.write(f"有效的Major参数值\n")
            f.write(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"目标网站: {base_url}\n")
            f.write(f"有效数量: {validation_results['valid_count']}\n")
            f.write(f"{'='*50}\n\n")
            
            for i, result in enumerate(validation_results['valid'], 1):
                f.write(f"{i:3d}. {result['major']}\n")
                f.write(f"    URL: {result['url']}\n")
                f.write(f"    内容长度: {result['content_length']}\n")
                f.write(f"    状态: 有效\n\n")
        
        # 保存为Python列表格式
        valid_python_file = os.path.join(output_dir, "valid_majors.py")
        with open(valid_python_file, 'w', encoding='utf-8') as f:
            f.write("# 有效的Major参数值列表\n")
            f.write("valid_majors = [\n")
            for result in validation_results['valid']:
                f.write(f'    "{result["major"]}",\n')
            f.write("]\n\n")
            f.write(f"# 总数: {validation_results['valid_count']}\n")
            f.write(f"# 验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"\n有效结果已保存到:")
        print(f"  - 文本格式: {valid_results_file}")
        print(f"  - Python列表: {valid_python_file}")
    
    if validation_results['invalid']:
        print(f"\n无效的专业值 ({validation_results['invalid_count']} 个):")
        for i, result in enumerate(validation_results['invalid'], 1):
            print(f"  {i:3d}. {result['major']} - 原因: {'内容过短' if result['content_length'] < 100 else '包含错误信息'}")
        
        # 保存无效结果
        invalid_results_file = os.path.join(output_dir, "invalid_majors.txt")
        with open(invalid_results_file, 'w', encoding='utf-8') as f:
            f.write(f"无效的Major参数值\n")
            f.write(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"目标网站: {base_url}\n")
            f.write(f"无效数量: {validation_results['invalid_count']}\n")
            f.write(f"{'='*50}\n\n")
            
            for i, result in enumerate(validation_results['invalid'], 1):
                f.write(f"{i:3d}. {result['major']}\n")
                f.write(f"    URL: {result['url']}\n")
                f.write(f"    内容长度: {result['content_length']}\n")
                f.write(f"    状态: 无效\n")
                if 'error' in result:
                    f.write(f"    错误: {result['error']}\n")
                f.write("\n")
        
        print(f"无效结果已保存到: {invalid_results_file}")
    
    # 保存详细验证报告
    detailed_report_file = os.path.join(output_dir, "validation_report.txt")
    with open(detailed_report_file, 'w', encoding='utf-8') as f:
        f.write(f"Major参数验证详细报告\n")
        f.write(f"{'='*50}\n")
        f.write(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"目标网站: {base_url}\n")
        f.write(f"总专业数: {validation_results['total']}\n")
        f.write(f"有效数量: {validation_results['valid_count']}\n")
        f.write(f"无效数量: {validation_results['invalid_count']}\n")
        f.write(f"成功率: {validation_results['valid_count']/validation_results['total']*100:.1f}%\n\n")
        
        f.write(f"有效专业列表:\n")
        f.write(f"{'='*30}\n")
        for result in validation_results['valid']:
            f.write(f"✓ {result['major']}\n")
        
        f.write(f"\n无效专业列表:\n")
        f.write(f"{'='*30}\n")
        for result in validation_results['invalid']:
            f.write(f"✗ {result['major']}\n")
    
    # 保存任务完成信息
    completion_info_file = os.path.join(output_dir, "completion_info.txt")
    with open(completion_info_file, 'w', encoding='utf-8') as f:
        f.write(f"Major参数验证任务完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"输出文件夹: {output_dir}\n")
        f.write(f"任务ID: {unique_id}\n")
        f.write(f"验证结果: 成功\n")
        f.write(f"总专业数: {validation_results['total']}\n")
        f.write(f"有效数量: {validation_results['valid_count']}\n")
        f.write(f"无效数量: {validation_results['invalid_count']}\n")
        f.write(f"成功率: {validation_results['valid_count']/validation_results['total']*100:.1f}%\n")
    
    print(f"\n{'='*50}")
    print(f"Major参数验证任务完成!")
    print(f"结果保存在文件夹: {output_dir}")
    print(f"详细报告: {detailed_report_file}")
    print(f"任务完成信息: {completion_info_file}")
    print(f"{'='*50}")


if __name__ == "__main__":
    asyncio.run(main())
