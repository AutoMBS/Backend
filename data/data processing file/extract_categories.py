#!/usr/bin/env python3
"""
提取MBS XML数据中的特定Category条目
将Category1、Category5和Category6分别提取到独立的JSON文件
"""

import json
import os
from collections import defaultdict

def extract_categories(input_file, categories_to_extract):
    """
    从JSON文件中提取指定Category的数据
    
    Args:
        input_file (str): 输入JSON文件路径
        categories_to_extract (list): 要提取的Category列表
    
    Returns:
        dict: 按Category分组的数据
    """
    print(f"正在读取文件: {input_file}")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("文件读取成功，开始提取数据...")
        
        # 初始化结果字典
        extracted_data = defaultdict(list)
        
        # 获取数据列表
        if 'MBS_XML' in data and 'Data' in data['MBS_XML']:
            items = data['MBS_XML']['Data']
            total_items = len(items)
            print(f"总共有 {total_items} 个条目")
            
            # 遍历所有条目
            for i, item in enumerate(items):
                if i % 1000 == 0:  # 每1000条显示进度
                    print(f"处理进度: {i}/{total_items}")
                
                # 检查Category字段
                if 'Category' in item and item['Category'] in categories_to_extract:
                    category = item['Category']
                    extracted_data[category].append(item)
            
            print("数据提取完成!")
            
            # 显示统计信息
            for category in categories_to_extract:
                count = len(extracted_data[category])
                print(f"Category {category}: {count} 条记录")
            
            return extracted_data
        else:
            print("错误: 文件结构不符合预期")
            return None
            
    except Exception as e:
        print(f"处理文件时出错: {e}")
        return None

def save_category_files(extracted_data, output_dir="extracted_categories"):
    """
    将提取的数据保存为独立的JSON文件
    
    Args:
        extracted_data (dict): 提取的数据
        output_dir (str): 输出目录
    """
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建输出目录: {output_dir}")
    
    saved_files = []
    
    for category, items in extracted_data.items():
        if items:  # 只处理有数据的Category
            # 创建输出文件名
            output_file = os.path.join(output_dir, f"category_{category}.json")
            
            # 准备输出数据结构
            output_data = {
                "metadata": {
                    "source": "MBS XML Data",
                    "category": category,
                    "total_items": len(items),
                    "extraction_date": "2025-01-27"
                },
                "data": items
            }
            
            # 保存文件
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                
                file_size = os.path.getsize(output_file) / 1024  # KB
                print(f"✅ Category {category}: 保存到 {output_file} ({file_size:.1f} KB)")
                saved_files.append(output_file)
                
            except Exception as e:
                print(f"❌ 保存Category {category}时出错: {e}")
    
    return saved_files

def create_summary_report(extracted_data, output_dir):
    """
    创建数据提取摘要报告
    
    Args:
        extracted_data (dict): 提取的数据
        output_dir (str): 输出目录
    """
    report_file = os.path.join(output_dir, "extraction_summary.txt")
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("MBS XML数据提取摘要报告\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"提取时间: 2025-01-27\n")
            f.write(f"源文件: file.json\n\n")
            
            f.write("各Category统计信息:\n")
            f.write("-" * 30 + "\n")
            
            for category in sorted(extracted_data.keys()):
                count = len(extracted_data[category])
                f.write(f"Category {category}: {count} 条记录\n")
            
            f.write(f"\n总计: {sum(len(items) for items in extracted_data.values())} 条记录\n")
            
            f.write(f"\n输出文件:\n")
            f.write("-" * 20 + "\n")
            for category in sorted(extracted_data.keys()):
                f.write(f"- category_{category}.json\n")
            
            f.write(f"- extraction_summary.txt (本文件)\n")
        
        print(f"📊 摘要报告已保存到: {report_file}")
        
    except Exception as e:
        print(f"创建摘要报告时出错: {e}")

def main():
    """主函数"""
    input_file = "file.json"
    categories_to_extract = ["1", "2", "3", "4", "5", "6",'8']
    output_dir = "extracted_categories"
    
    print("🚀 开始提取MBS XML数据中的特定Category...")
    print(f"目标Category: {', '.join(categories_to_extract)}")
    print("-" * 60)
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"❌ 错误: 输入文件 '{input_file}' 不存在")
        return
    
    # 提取数据
    extracted_data = extract_categories(input_file, categories_to_extract)
    
    if extracted_data is None:
        print("❌ 数据提取失败")
        return
    
    # 保存文件
    print("\n💾 开始保存文件...")
    saved_files = save_category_files(extracted_data, output_dir)
    
    if saved_files:
        # 创建摘要报告
        create_summary_report(extracted_data, output_dir)
        
        print("\n🎉 所有操作完成!")
        print(f"📁 输出目录: {output_dir}")
        print(f"📄 生成的文件:")
        for file_path in saved_files:
            print(f"   - {os.path.basename(file_path)}")
        print(f"   - extraction_summary.txt")
        
        # 显示文件大小统计
        total_size = sum(os.path.getsize(f) for f in saved_files)
        print(f"\n📊 总输出文件大小: {total_size / 1024 / 1024:.2f} MB")
        
    else:
        print("❌ 没有成功保存任何文件")

if __name__ == "__main__":
    main()
