# -*- coding: utf-8 -*-


# 1 ----------------模块导入
import xlrd


# 2 ----------------返回html list
def pullHtml():
    xlsx_file = xlrd.open_workbook('Htmls/Htmls.xlsx')
    table = xlsx_file.sheet_by_name('Htmls')
    html_list = table.col_values(0)

    return html_list

# 2.1 方法测试
# html_list = pullHtml()