#!/usr/bin/env python3
"""
CSV to Excel转换器
将category_1_final.csv和category_3_final.csv转换为XLSX格式
"""

import pandas as pd
import os
from datetime import datetime

def convert_csv_to_excel():
    """将CSV文件转换为Excel格式"""
    
    print("🔄 开始转换CSV文件到Excel格式...")
    print("=" * 60)
    
    # 定义文件路径
    csv_files = [
        "category_1_final.csv",
        "category_3_final.csv"
    ]
    
    # 检查并安装openpyxl
    try:
        import openpyxl
        print("✅ openpyxl已安装")
    except ImportError:
        print("📦 正在安装openpyxl...")
        os.system("pip install openpyxl")
        print("✅ openpyxl安装完成")
    
    converted_files = []
    
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            print(f"\n📁 处理文件: {csv_file}")
            
            try:
                # 读取CSV文件
                print(f"   📖 读取CSV文件...")
                df = pd.read_csv(csv_file)
                
                # 显示文件信息
                print(f"   📊 文件信息:")
                print(f"      - 行数: {len(df)}")
                print(f"      - 列数: {len(df.columns)}")
                print(f"      - 列名: {list(df.columns)}")
                
                # 生成输出文件名
                base_name = csv_file.replace('.csv', '')
                excel_file = f"{base_name}.xlsx"
                
                # 转换并保存为Excel
                print(f"   💾 转换为Excel格式...")
                df.to_excel(excel_file, index=False, engine='openpyxl')
                
                # 获取文件大小
                file_size = os.path.getsize(excel_file) / (1024 * 1024)  # MB
                print(f"   ✅ 转换完成: {excel_file}")
                print(f"   📏 文件大小: {file_size:.2f} MB")
                
                converted_files.append(excel_file)
                
            except Exception as e:
                print(f"   ❌ 转换失败: {str(e)}")
        else:
            print(f"❌ 文件不存在: {csv_file}")
    
    print("\n" + "=" * 60)
    
    if converted_files:
        print("🎉 转换完成!")
        print(f"📋 成功转换的文件:")
        for file in converted_files:
            print(f"   ✅ {file}")
        
        # 显示转换统计
        print(f"\n📊 转换统计:")
        print(f"   - 总文件数: {len(csv_files)}")
        print(f"   - 成功转换: {len(converted_files)}")
        print(f"   - 失败数量: {len(csv_files) - len(converted_files)}")
        
        # 显示当前目录中的Excel文件
        print(f"\n📁 当前目录中的Excel文件:")
        excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
        for file in excel_files:
            file_size = os.path.getsize(file) / (1024 * 1024)  # MB
            print(f"   📄 {file} ({file_size:.2f} MB)")
            
    else:
        print("❌ 没有文件转换成功")
    
    print(f"\n⏰ 转换时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def check_file_details():
    """检查CSV文件的详细信息"""
    
    print("\n🔍 检查CSV文件详细信息...")
    print("=" * 60)
    
    csv_files = [
        "category_1_final.csv",
        "category_3_final.csv"
    ]
    
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            print(f"\n📁 文件: {csv_file}")
            
            try:
                # 读取前几行来了解数据结构
                df = pd.read_csv(csv_file, nrows=5)
                
                # 显示基本信息
                file_size = os.path.getsize(csv_file) / 1024  # KB
                print(f"   📏 文件大小: {file_size:.2f} KB")
                print(f"   📊 行数: {len(pd.read_csv(csv_file))}")
                print(f"   🔤 列数: {len(df.columns)}")
                
                # 显示列名
                print(f"   📋 列名:")
                for i, col in enumerate(df.columns):
                    print(f"      {i+1:2d}. {col}")
                
                # 显示数据类型
                print(f"   🏷️  数据类型:")
                for col in df.columns:
                    dtype = df[col].dtype
                    print(f"      {col}: {dtype}")
                
                # 显示前3行数据预览
                print(f"   👀 数据预览 (前3行):")
                print(df.head(3).to_string(index=False))
                
            except Exception as e:
                print(f"   ❌ 读取失败: {str(e)}")
        else:
            print(f"❌ 文件不存在: {csv_file}")

if __name__ == "__main__":
    print("🚀 CSV to Excel 转换器")
    print("=" * 60)
    
    # 检查文件详情
    check_file_details()
    
    # 执行转换
    convert_csv_to_excel()
    
    print("\n" + "=" * 60)
    print("✨ 转换器执行完成!")
    print("\n💡 提示:")
    print("   - 生成的Excel文件可以直接用Excel、Numbers等软件打开")
    print("   - 如果文件很大，转换可能需要一些时间")
    print("   - 确保有足够的磁盘空间")
