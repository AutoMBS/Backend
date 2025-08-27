import pandas as pd
import os
from datetime import datetime

def convert_excel_to_csv():
    """将Excel文件转换为CSV格式"""
    print("🔄 开始转换Excel文件到CSV格式...")
    print("=" * 60)
    
    # 检查openpyxl是否安装
    try:
        import openpyxl
        print("✅ openpyxl已安装")
    except ImportError:
        print("📦 正在安装openpyxl...")
        os.system("pip install openpyxl")
        print("✅ openpyxl安装完成")
    
    # 查找所有Excel文件
    excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    print(f"📁 找到 {len(excel_files)} 个Excel文件:")
    for file in excel_files:
        file_size = os.path.getsize(file) / 1024
        print(f"   📄 {file} ({file_size:.1f} KB)")
    
    converted_files = []
    failed_files = []
    
    for excel_file in excel_files:
        print(f"\n🔄 正在处理: {excel_file}")
        try:
            # 读取Excel文件
            print(f"   📖 读取Excel文件...")
            df = pd.read_excel(excel_file, engine='openpyxl')
            print(f"   📊 文件信息:\n      - 行数: {len(df)}\n      - 列数: {len(df.columns)}")
            
            # 生成CSV文件名
            base_name = excel_file.replace('.xlsx', '')
            csv_file = f"{base_name}.csv"
            
            # 转换为CSV
            print(f"   💾 转换为CSV格式...")
            df.to_csv(csv_file, index=False, encoding='utf-8')
            
            # 检查文件大小
            csv_size = os.path.getsize(csv_file) / 1024
            print(f"   ✅ 转换完成: {csv_file}\n   📏 文件大小: {csv_size:.1f} KB")
            
            converted_files.append(csv_file)
            
        except Exception as e:
            print(f"   ❌ 转换失败: {str(e)}")
            failed_files.append(excel_file)
    
    print("\n" + "=" * 60)
    print("📊 转换结果统计:")
    print(f"   - 总Excel文件数: {len(excel_files)}")
    print(f"   - 成功转换: {len(converted_files)}")
    print(f"   - 转换失败: {len(failed_files)}")
    
    if converted_files:
        print(f"\n✅ 成功转换的文件:")
        for file in converted_files:
            file_size = os.path.getsize(file) / 1024
            print(f"   📄 {file} ({file_size:.1f} KB)")
    
    if failed_files:
        print(f"\n❌ 转换失败的文件:")
        for file in failed_files:
            print(f"   📄 {file}")
    
    # 显示当前目录中的所有CSV文件
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    if csv_files:
        print(f"\n📁 当前目录中的CSV文件:")
        for file in csv_files:
            file_size = os.path.getsize(file) / 1024
            print(f"   📄 {file} ({file_size:.1f} KB)")
    
    print(f"\n⏰ 转换时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n💡 提示:")
    print("   - CSV文件可以用Excel、Numbers、文本编辑器等打开")
    print("   - 如果文件很大，转换可能需要一些时间")
    print("   - CSV格式更适合数据处理和导入到其他系统")

def check_file_details():
    """检查文件详细信息"""
    print("🔍 检查当前目录文件...")
    print("=" * 60)
    
    # 检查Excel文件
    excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    if excel_files:
        print("📊 Excel文件:")
        for file in excel_files:
            file_size = os.path.getsize(file) / 1024
            mod_time = datetime.fromtimestamp(os.path.getmtime(file)).strftime('%Y-%m-%d %H:%M:%S')
            print(f"   📄 {file}")
            print(f"      - 大小: {file_size:.1f} KB")
            print(f"      - 修改时间: {mod_time}")
            
            # 尝试读取文件信息
            try:
                df = pd.read_excel(file, engine='openpyxl')
                print(f"      - 行数: {len(df)}")
                print(f"      - 列数: {len(df.columns)}")
                print(f"      - 列名: {list(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
            except Exception as e:
                print(f"      - 读取失败: {str(e)}")
            print()
    else:
        print("❌ 没有找到Excel文件")
    
    # 检查CSV文件
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    if csv_files:
        print("📊 CSV文件:")
        for file in csv_files:
            file_size = os.path.getsize(file) / 1024
            mod_time = datetime.fromtimestamp(os.path.getmtime(file)).strftime('%Y-%m-%d %H:%M:%S')
            print(f"   📄 {file}")
            print(f"      - 大小: {file_size:.1f} KB")
            print(f"      - 修改时间: {mod_time}")
            
            # 尝试读取文件信息
            try:
                df = pd.read_csv(file)
                print(f"      - 行数: {len(df)}")
                print(f"      - 列数: {len(df.columns)}")
                print(f"      - 列名: {list(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
            except Exception as e:
                print(f"      - 读取失败: {str(e)}")
            print()

if __name__ == "__main__":
    print("🚀 Excel to CSV 转换器\n" + "=" * 60)
    check_file_details()
    convert_excel_to_csv()
    print("\n" + "=" * 60 + "\n✨ 转换器执行完成!")
