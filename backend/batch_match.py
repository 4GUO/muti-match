# 通过读取制定的excel
# 用第一行的数据作为请求数据，调用cfi22的semantic_search方法，取第一行的结果，把name写入到对应行的第2列，把code写入到对应行的第3列
# 直接保存到旧的excel文件中

import pandas as pd
from cfi import cfi22


def update_excel_with_search_results(input_file):
    # 初始化 cfi22 类
    classifier = cfi22()

    # 读取指定的 Excel 文件
    df = pd.read_excel(input_file, header=None)
    print(f"加载 Excel 文件: {input_file}")

    # 遍历 DataFrame 中的每一行
    for index, row in df.iterrows():
        query = row[0]  # 假设请求数据在第一列
        print(f"处理第 {index} 行，查询: {query}")

        # 执行语义搜索
        results = classifier.semantic_search(query, top_n=1)

        # 获取第一个结果并更新 DataFrame
        if results:
            # 如果打分低于0.3 则不写入
            if results[0]['score'] < 0.3:
                print(f"查询: {query} 的匹配度低于3，不写入")
                continue
            first_result = results[0]
            df.at[index, 1] = first_result['name']  # 将 name 写入第二列
            df.at[index, 2] = first_result['code']  # 将 code 写入第三列
            print(f"更新第 {index} 行，name: {first_result['name']}，code: {first_result['code']}")
        else:
            print(f"查询: {query} 没有找到结果")

    # 保存到同一个 Excel 文件
    df.to_excel(input_file, index=False, header=False)
    print(f"保存更新后的 Excel 文件: {input_file}")


if __name__ == "__main__":
    input_file = './temp/YLSB-BASE-0.xlsx'
    update_excel_with_search_results(input_file)
