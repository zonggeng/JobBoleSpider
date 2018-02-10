from ArticleSpider.settings import chromedriver_path
from selenium import webdriver
from scrapy.selector import Selector

browser = webdriver.Chrome(executable_path=chromedriver_path)

browser.get(r'https://www.zhihu.com/signup')

html = browser.page_source  # 获取用浏览器打开的页面源代码 就是说通过js生成后的源码也可以

browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[2]/span').click()

browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[1]/div[2]/div[1]/input').send_keys('13535419055')
browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[2]/div/div[1]/input').send_keys('xingfu1204..')
browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/button').click()