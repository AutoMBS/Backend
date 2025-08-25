import sqlite3
import pandas as pd

def test_read_database():
    """测试读取已创建的SQLite数据库"""
    
    try:
        # 连接到数据库
        conn = sqlite3.connect('medical_categories.db')
        print("成功连接到数据库: medical_categories.db")
        
        # 显示数据库中的表
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"数据库中的表: {[table[0] for table in tables]}")
        
        # 测试读取category_1表
        print("\n=== 测试读取 Category 1 表 ===")
        df_cat1 = pd.read_sql_query("SELECT * FROM category_1 LIMIT 5", conn)
        print(f"Category 1 表前5行数据:")
        print(df_cat1)
        print(f"\nCategory 1 表总行数: {len(pd.read_sql_query('SELECT * FROM category_1', conn))}")
        
        # 测试读取category_3表
        print("\n=== 测试读取 Category 3 表 ===")
        df_cat3 = pd.read_sql_query("SELECT * FROM category_3 LIMIT 5", conn)
        print(f"Category 3 表前5行数据:")
        print(df_cat3)
        print(f"\nCategory 3 表总行数: {len(pd.read_sql_query('SELECT * FROM category_3', conn))}")
        
        # 测试一些基本查询
        print("\n=== 测试基本查询 ===")
        
        # 查询1: 统计每个category的记录数
        query1 = "SELECT category_code, COUNT(*) as count FROM category_1 GROUP BY category_code"
        result1 = pd.read_sql_query(query1, conn)
        print("Category 1 各分类记录数:")
        print(result1)
        
        # 查询2: 查找特定item_number
        query2 = "SELECT * FROM category_1 WHERE item_number = 23"
        result2 = pd.read_sql_query(query2, conn)
        print("\n查找item_number = 23的记录:")
        print(result2)
        
        # 查询3: 查找特定therapy_type
        query3 = "SELECT item_num, therapy_type, treatment_for FROM category_3 WHERE therapy_type LIKE '%hyperbaric%' LIMIT 3"
        result3 = pd.read_sql_query(query3, conn)
        print("\n查找包含'hyperbaric'的治疗类型:")
        print(result3)
        
        # 查询4: 年龄范围查询
        query4 = "SELECT item_number, service_summary, start_age, end_age FROM category_1 WHERE start_age = 0 AND end_age = 1 LIMIT 3"
        result4 = pd.read_sql_query(query4, conn)
        print("\n查找年龄范围0-1岁的服务:")
        print(result4)
        
        # 查询5: 复杂条件查询
        query5 = """
        SELECT item_number, service_provider, location, start_time, end_time 
        FROM category_1 
        WHERE location LIKE '%consulting rooms%' 
        AND start_time >= 20 AND end_time <= 40 
        LIMIT 5
        """
        result5 = pd.read_sql_query(query5, conn)
        print("\n查找在consulting rooms且时长20-40分钟的服务:")
        print(result5)
        
        conn.close()
        print("\n数据库连接已关闭")
        print("所有测试完成!")
        
    except FileNotFoundError:
        print("错误: 找不到数据库文件 'medical_categories.db'")
        print("请先运行 csv_to_sqlite_converter.py 创建数据库")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    test_read_database()
