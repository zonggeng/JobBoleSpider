from ArticleSpider.zheye import zheye

z = zheye()
import shutil
import requests

headers = {
    "HOST": "www.zhihu.com",
    "Referer": "https://www.zhizhu.com",
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0",
    'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
    'Accept-Encoding': 'gzip, deflate'
}
import time
lp = []
lpp = []
s = requests.session()
