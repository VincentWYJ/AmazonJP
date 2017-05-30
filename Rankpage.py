
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time

picture_name = r"D:\userdata\chansong\Desktop\11.jpg"
def get_taobao_data(picture_name):
    i = 0
    output_data =[]
    driver = webdriver.Firefox()
    try:
        driver.get('https://www.taobao.com/')
    except Exception as e:
        print(e)

    try:
        driver.find_element_by_id("J_IMGSeachUploadBtn").clear() # 非常奇怪，没有这句话无法工作
        time.sleep(10)
        driver.find_element_by_id("J_IMGSeachUploadBtn").send_keys(picture_name)
        driver.find_element_by_id("J_IMGSeachUploadBtn").send_keys(Keys.ENTER)
    except Exception as e:
        print(e)
    time.sleep(20)
    get_html = driver.page_source
    driver.quit()
    bs_obj = BeautifulSoup(get_html,'html.parser')
    target_div_node = bs_obj.find('div', {'class': 'items g-clearfix'})
    if target_div_node and len(target_div_node) > 0:
        for items_div in target_div_node.find_all('div', {'class': r'row row-2 title'}): #获取名称
            item_name = items_div.get_text().strip()
            output_data.append(item_name)
            print (item_name)
        for items_div in target_div_node.find_all('div', {'class': 'price g_price g_price-highlight'}): #获取价格
            item_price = items_div.get_text().strip()
            output_data.append(item_price)
            print(item_price)
        for items_div in target_div_node.find_all('div', {'class': 'deal-cnt'}): #获取销量
            item_account = items_div.get_text().strip()
            output_data.append(item_account)
            print(item_account)
        print(output_data)
    return output_data



if __name__ == '__main__':
    get_taobao_data(picture_name)
