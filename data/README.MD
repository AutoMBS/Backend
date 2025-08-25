Data file是用于存放处理所有MBS金标准的raw data的。

1. data processing file 所有相关的数据处理file，但这里不用再跑，已经处理完备呈现yaml格式和csv格式

2. extracted categories 转换了7个category的数据（部分category由于未知具体含义并未转化，如7，9，10）

3. Raw data and processing file 获取MBS官网的XML file并且转化为json

4. unreliable 的synthetic data（当实在没有病人数据的时候考虑启用检测输出item的准确性）

5.yaml_rules: 存放了用llm通过langchain的强化prompt和gpt-4o-mini解析了category1和category3的金标准，以yaml形式存在

6.Category_1_final.csv和Category_3_final.csv是通过了一部分数据清洗和处理把yaml 的rules解析成table形式存在，方便进行后期数值型的筛选（category1有20条需手工更改，当时识别填关键词有空类型错误；category3有6条需手工更改，当时识别填关键词有空类型错误）。

7.csv通过csv_to_sqlite_converter可以转化成sqlite可读的db文件，存储为medical_categories.db

8.可以运行test_database_reader.py来进行一些示例的查询