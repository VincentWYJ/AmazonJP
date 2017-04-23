# -*- coding: utf-8 -*-


# 1 ----------------模块导入
import csv


# 2 ----------------数据写入csv
def pushDataCmp(product_info_list):
    # 写入数据
    item_file = open('AllItems.csv', 'a+', newline='')
    item_writer = csv.writer(item_file, dialect='excel')
    item_writer.writerow(product_info_list)
    item_file.close()

# 2.1 方法测试
# pushDataCmp([1, 2, 3, 4])