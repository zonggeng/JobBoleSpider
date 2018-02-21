# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import JobBoleArticleItem, ArticleItemloader
from ArticleSpider.utils.common import get_md5
from scrapy.loader import ItemLoader
import datetime
from ArticleSpider.settings import chromedriver_path
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    """
    def __init__(self):  # 相当于爬虫的信号器
        # 设置Chrome无界面运行  chrome_opt.add_argument('--headless')  或者 options.add_argument("headless")
        # 在初始化函数上定义好browser 这样就不会每个请求都创建一个实例!很慢
        self.chrome_opt = webdriver.ChromeOptions()
        self.chrome_opt.add_argument('--headless')
        self.chrome_opt.add_argument('--disable-gpu')
        self.browser = webdriver.Chrome(executable_path=chromedriver_path, chrome_options=self.chrome_opt)
        super(JobboleSpider, self).__init__()
        # 信号映射 第一个参数是处理函数 ,第二个参数是信号链 就是说爬虫发生什么信号用什么函数处理
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        # 当爬虫退出的时候关闭Chrome
        print('spider closed')
        self.browser.close()
        print('browser closed')
    """

    """
    # 手机伯乐在线所有404的url已经404的页面数
    # 404的状态码我们自己处理 遇到404页面会进入parse 处理
    handle_httpstatus_list = [404]

    def __init__(self):
        self.fail_urls = []
        dispatcher.connect(self.handle_spider_closed, signals.spider_closed)

    def handle_spider_closed(self, spider, reason):
        self.crawler.stats.set_value('failed_urls', ','.join(self.fail_urls))
    """

    def parse(self, response):
        """
        1. 获取具体文章url,并交给解析函数进行具体字段的解析
        2. 获取下一页url并交给scrapy进行下载 下载完成后交给parse
        :param response:
        :return:
        """
        """
        if response.status == 404:
            self.fail_urls.append(response.url)
            self.crawler.stats.inv_value('failed_url')  # inv_value 这样调用 failed_url就会+1 就算一开始没有也会创建
        """

        # 因为还要获取封面页!所以先用xpath找到封面图片和文章url的同一个父节点 然后遍历的时候再获取对应的链接和图片 用meta发送到对应函数处理
        post_nodes = response.xpath('//div[@class="post floated-thumb"]/div[@class="post-thumb"]/a')
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.xpath('@href').extract_first('')
            # 有些网站获取的url没有带域名不是完整的!需要用urllib.parse 的一个函数join 下面这样处理可以万无一失
            #  通过meta 把封面地址传到对应的链接去
            yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse_detail,
                          meta={'front_image_url': image_url})

        # 提取下一页url并交给scrapy进行下载
        next_url = response.xpath('//a[@class="next page-numbers"]/@href').extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        """
        提取文章的具体字段
        :param response:
        :return:
        """
        """
        front_image = response.meta.get('front_image_url', '')  # 获取上面传过来的封面
        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract()[0]
        create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace(
            ' ·', '')
        praise_nums = response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract()[0]
        fav_nums = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract()[0].strip().replace(' 收藏',
                                                                                                                 '')
        if fav_nums == '收藏':
            fav_nums = 0
        comment_nums = response.xpath('//a[@href="#article-comment"]/span/text()').extract()[0].strip().replace(' 评论',
                                                                                                                '')
        if comment_nums == '评论':
            comment_nums = 0
        content = response.xpath('//div[@class="entry"]').extract()
        tag_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        tag_list = [element for element in tag_list if not element.strip().endswith('评论')]
        tags = ','.join(tag_list)

        # 创建item对象
        article_item = JobBoleArticleItem()
        article_item['title'] = title
        article_item['url'] = response.url
        try:
            create_date = datetime.datetime.strptime(create_date, '%Y/%m/%d').date()  # 格式化格式
        except Exception as e:
            create_date = datetime.datetime.now()  # 当前时间
        article_item['create_date'] = create_date
        article_item['fron_image_url'] = [front_image]  # 如果用scrapy 的imagepipeline下载图片要给她传进list 不然会报错
        article_item['praise_nums'] = praise_nums
        article_item['comment_nums'] = comment_nums
        article_item['fav_nums'] = fav_nums
        article_item['tags'] = tags
        article_item['content'] = content
        article_item['url_object_id'] = get_md5(response.url)
        """

        # 通过item loader加载item 后期更好维护!直观! 规则还可以写在配置文件或者数据库! 但是都是列表格式  要对数据处理的话要去item里面自定义函数
        item_loader = ArticleItemloader(item=JobBoleArticleItem(), response=response)
        front_image_url = response.meta.get("front_image_url", "")  # 封面图
        item_loader.add_xpath('title', '//div[@class="entry-header"]/h1/text()')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_xpath('create_date', '//p[@class="entry-meta-hide-on-mobile"]/text()')
        item_loader.add_value('fron_image_url', [front_image_url])
        item_loader.add_xpath('praise_nums', '//span[contains(@class,"vote-post-up")]/h10/text()')
        item_loader.add_xpath('comment_nums', '//a[@href="#article-comment"]/span/text()')
        item_loader.add_xpath('fav_nums', '//span[contains(@class,"bookmark-btn")]/text()')
        item_loader.add_xpath('content', '//div[@class="entry"]')
        item_loader.add_xpath('tags', '//p[@class="entry-meta-hide-on-mobile"]/a/text()')

        article_item = item_loader.load_item()

        yield article_item
