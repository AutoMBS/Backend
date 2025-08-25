import pandas as pd
import sqlite3
import os

def create_database():
    """创建SQLite数据库并导入CSV数据"""
    
    # 创建数据库连接
    conn = sqlite3.connect('medical_categories.db')
    
    try:
        # 读取category_1_final.csv
        print("正在读取 category_1_final.csv...")
        df_category1 = pd.read_csv('data/category_1_final.csv')
        print(f"Category 1 数据行数: {len(df_category1)}")
        print(f"Category 1 列名: {list(df_category1.columns)}")
        
        # 读取category_3_final.csv
        print("正在读取 category_3_final.csv...")
        df_category3 = pd.read_csv('data/category_3_final.csv')
        print(f"Category 3 数据行数: {len(df_category3)}")
        print(f"Category 3 列名: {list(df_category3.columns)}")
        
        # 将数据导入到SQLite数据库
        print("正在导入数据到数据库...")
        
        # 导入category_1数据
        df_category1.to_sql('category_1', conn, if_exists='replace', index=False)
        print("Category 1 数据已导入到表 'category_1'")
        
        # 导入category_3数据
        df_category3.to_sql('category_3', conn, if_exists='replace', index=False)
        print("Category 3 数据已导入到表 'category_3'")
        
        # 创建索引以提高查询性能
        print("正在创建索引...")
        conn.execute('CREATE INDEX IF NOT EXISTS idx_cat1_item_number ON category_1(item_number)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_cat1_category_code ON category_1(category_code)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_cat3_item_num ON category_3(item_num)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_cat3_category_code ON category_3(category_code)')
        
        print("索引创建完成")
        
        # 显示表信息
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\n数据库中的表: {[table[0] for table in tables]}")
        
        # 显示每个表的行数
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"表 {table_name}: {count} 行")
        
        print("\n数据库创建完成!")
        return conn
        
    except Exception as e:
        print(f"错误: {e}")
        conn.close()
        return None

def test_database_queries(conn):
    """测试数据库查询功能"""
    
    if not conn:
        print("数据库连接失败")
        return
    
    cursor = conn.cursor()
    
    print("\n=== 数据库查询测试 ===")
    
    # 测试1: 查询category_1的基本信息
    print("\n1. Category 1 表的基本信息:")
    cursor.execute("SELECT category_code, category_name, COUNT(*) as count FROM category_1 GROUP BY category_code, category_name")
    results = cursor.fetchall()
    for row in results:
        print(f"   {row[0]} - {row[1]}: {row[2]} 条记录")
    
    # 测试2: 查询category_3的基本信息
    print("\n2. Category 3 表的基本信息:")
    cursor.execute("SELECT category_code, category_name, COUNT(*) as count FROM category_3 GROUP BY category_code, category_name")
    results = cursor.fetchall()
    for row in results:
        print(f"   {row[0]} - {row[1]}: {row[2]} 条记录")
    
    # 测试3: 查询特定item_number的记录
    print("\n3. 查询item_number为3的记录 (Category 1):")
    cursor.execute("SELECT * FROM category_1 WHERE item_number = 3 LIMIT 1")
    result = cursor.fetchone()
    if result:
        columns = [description[0] for description in cursor.description]
        for i, col in enumerate(columns):
            print(f"   {col}: {result[i]}")
    
    # 测试4: 查询特定item_num的记录 (Category 3)
    print("\n4. 查询item_num为13015的记录 (Category 3):")
    cursor.execute("SELECT * FROM category_3 WHERE item_num = 13015 LIMIT 1")
    result = cursor.fetchone()
    if result:
        columns = [description[0] for description in cursor.description]
        for i, col in enumerate(columns):
            print(f"   {col}: {result[i]}")
    
    # 测试5: 查询年龄限制相关的记录
    print("\n5. Category 1 中年龄限制为0-1岁的记录数量:")
    cursor.execute("SELECT COUNT(*) FROM category_1 WHERE start_age = 0 AND end_age = 1")
    count = cursor.fetchone()[0]
    print(f"   年龄0-1岁的记录: {count} 条")
    
    # 测试6: 查询特定服务提供者
    print("\n6. Category 1 中general practitioner的记录数量:")
    cursor.execute("SELECT COUNT(*) FROM category_1 WHERE service_provider LIKE '%general practitioner%'")
    count = cursor.fetchone()[0]
    print(f"   General Practitioner记录: {count} 条")
    
    # 测试7: 查询特定治疗类型
    print("\n7. Category 3 中hyperbaric oxygen therapy的记录数量:")
    cursor.execute("SELECT COUNT(*) FROM category_3 WHERE therapy_type LIKE '%hyperbaric oxygen therapy%'")
    count = cursor.fetchone()[0]
    print(f"   Hyperbaric Oxygen Therapy记录: {count} 条")
    
    # 测试8: 复杂查询 - 查找特定条件的记录
    print("\n8. Category 1 中在consulting rooms且时长在20-40分钟之间的记录:")
    cursor.execute("""
        SELECT item_number, service_summary, start_time, end_time 
        FROM category_1 
        WHERE location LIKE '%consulting rooms%' 
        AND start_time >= 20 AND end_time <= 40 
        LIMIT 5
    """)
    results = cursor.fetchall()
    for row in results:
        print(f"   Item {row[0]}: {row[1][:50]}... (时长: {row[2]}-{row[3]}分钟)")
    
    print("\n=== 查询测试完成 ===")

def main():
    """主函数"""
    print("开始创建医疗类别数据库...")
    
    # 创建数据库
    conn = create_database()
    
    if conn:
        # 测试数据库查询
        test_database_queries(conn)
        
        # 关闭数据库连接
        conn.close()
        print("\n数据库连接已关闭")
    else:
        print("数据库创建失败")

if __name__ == "__main__":
    main()
