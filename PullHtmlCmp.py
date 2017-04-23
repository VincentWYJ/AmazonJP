# -*- coding: utf-8 -*-


# 1 ----------------模块导入
import csv


# 2 ----------------常量定义
html_head = 'https://www.amazon.co.jp/dp/'


# 3 ----------------返回html listhtml_head + str(row[33])
def pullHtmlCmp():
    html_list = []
    item_file = open('Htmls/AllItems.csv', 'r')
    item_reader = csv.reader(item_file)
    outer_id_list = [str(row[33]) for row in item_reader ]
    outer_id_list = outer_id_list[4:]
    for outer_id in outer_id_list:
        if outer_id != '':
            html_list.append(html_head + str(outer_id))

    return html_list

# 3.1 方法测试
# html_list = pullHtmlCmp()
# for html in html_list:
#     print(html)
