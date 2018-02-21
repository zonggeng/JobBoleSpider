# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import time
from scrapy import signals
from fake_useragent import UserAgent
from tools.crawl_xici_ip import GetIP
from ArticleSpider.settings import chromedriver_path, phantomjs_path
from selenium import webdriver
from scrapy.http import HtmlResponse


class ArticlespiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ArticlespiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomUserAgentMiddlware(object):
    """
    随机更换user-agent
    """

    def __init__(self, crawler):
        super(RandomUserAgentMiddlware, self).__init__()
        self.ua = UserAgent()
        self.ua_type = crawler.settings.get('RANDOM_UA_TYPE', 'random')

    @classmethod
    def from_crawler(csl, crawler):
        return csl(crawler)

    def process_request(self, request, spider):
        def get_ua():
            # getattr 相当于 前面的参数 . 后面的参数  因为你不能 self.ua.self.ua_type
            return getattr(self.ua, self.ua_type)

        random_agent = get_ua()
        request.headers.setdefault('User-Agent', get_ua())
        # 设置代理
        # request.meta['proxy'] = 'http://61.135.217.7:80'


class RandomProxyMiddleware(object):
    def process_request(self, request, spider):
        get_ip = GetIP()
        request.meta['proxy'] = get_ip.get_random_ip()


# 集成selenium
class JSPageMiddleware(object):
    """
    def __init__(self):
        # 设置Chrome无界面运行  chrome_opt.add_argument('--headless')  或者 options.add_argument("headless")
        # 在初始化函数上定义好browser 这样就不会每个请求都创建一个实例!很慢
        self.chrome_opt = webdriver.ChromeOptions()
        self.chrome_opt.add_argument('--headless')
        self.chrome_opt.add_argument('--disable-gpu')
        self.browser = webdriver.Chrome(executable_path=chromedriver_path, chrome_options=self.chrome_opt)
        # super(JSPageMiddleware,self).__init__()
        # 优化:
        # 把selenium放在spider里面会更好,因为可以异步启动chrome !爬虫关闭的时候也可以调用关闭方法
    """

    # 通过chrome 请求动态网页
    def process_request(self, request, spider):
        # 通过spider判断那个爬虫需要用selenium!
        # 也可以通过request判断需不需要用selenium
        if spider.name == "jobbole":
            spider.browser.get(request.url)
            # time.sleep(3)
            print('访问:{}'.format(request.url))
            # 因为已经获取到源代码了!所以要跳过下载器 直接把源代码发送回给spider
            # 一旦遇到HtmlResponse 就不会再发送数据给下载器 而是直接返回给spider
            return HtmlResponse(url=spider.browser.current_url, body=spider.browser.page_source, encoding='utf-8',
                                request=request)
