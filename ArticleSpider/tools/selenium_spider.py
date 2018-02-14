import time

from ArticleSpider.settings import chromedriver_path, phantomjs_path
from selenium import webdriver
from scrapy.selector import Selector

"""
# 模拟登陆知乎
browser = webdriver.Chrome(executable_path=chromedriver_path)

browser.get(r'https://www.zhihu.com/signup')

html = browser.page_source  # 获取用浏览器打开的页面源代码 就是说通过js生成后的源码也可以

browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[2]/span').click()

browser.find_element_by_xpath(
    '//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[1]/div[2]/div[1]/input').send_keys('13535419055')
browser.find_element_by_xpath(
    '//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[2]/div/div[1]/input').send_keys('xingfu1204..')
browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/button').click()

"""

# selenium 登陆微博
"""
browser = webdriver.Chrome(executable_path=chromedriver_path)

browser.get(r'https://www.weibo.com')
time.sleep(5)
browser.find_element_by_xpath('//*[@id="loginname"]').send_keys('123123')
browser.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[2]/div/input').send_keys('123123')
browser.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a/span').click()

browser.close()
"""

"""
browser = webdriver.Chrome(executable_path=chromedriver_path)
browser.get("https://www.oschina.net/blog")
# 下拉3次
for i in range(3):
    # 执行javaScript代码
    browser.execute_script(
        "window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;")
    time.sleep(3)
"""

# 设置webdriver 不加载图片提高效率
"""
chrome_opt = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images":2}
chrome_opt.add_experimental_option("prefs", prefs)
browser = webdriver.Chrome(executable_path=chromedriver_path, chrome_options=chrome_opt)
browser.get("https://www.oschina.net/blog")
"""
"""

# 快被抛弃了!选用别的方案
browser = webdriver.PhantomJS(executable_path=phantomjs_path)
browser.get(
    "https://zhuanlan.zhihu.com/p/28533642")
print(browser.page_source)
browser.quit()
"""

# 设置Chrome无界面运行  chrome_opt.add_argument('--headless')  或者 options.add_argument("headless")
chrome_opt = webdriver.ChromeOptions()
chrome_opt.add_argument('--headless')
chrome_opt.add_argument('--disable-gpu')
browser = webdriver.Chrome(executable_path=chromedriver_path, chrome_options=chrome_opt)
browser.get(
    "https://item.taobao.com/item.htm?scm=1007.12807.84406.100200300000004&id=549951794075&pvid=4d722218-6281-4fe3-8ef5-230a244534d6")

print(browser.page_source)
browser.quit()
