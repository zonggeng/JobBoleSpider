from scrapy.cmdline import execute

import sys
import os

# os.path.abspath(__file__) 获取当前py文件的路径 os.path.dirname 获取里面文件路径的父目录
# os.path.dirname(os.path.abspath(__file__)) = D:\py3_scrapy\ArticleSpider
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# execute(['scrapy', 'crawl', 'jobbole'])
execute(['scrapy', 'crawl', 'zhihu_sel'])
