# -*- coding: utf-8 -*-
import datetime
import json
import re

from ArticleSpider.settings import chromedriver_path
import scrapy
from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuAnswerItem, ZhihuQuestionItem

try:
    import urlparse as parse
except:
    from urllib import parse


class ZhihuSpider(scrapy.Spider):
    name = "zhihu_sel"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['https://www.zhihu.com/']

    # question的第一页answer的请求url API
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccollapsed_counts%2Creviewing_comments_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.is_blocking%2Cis_blocked%2Cis_followed%2Cvoteup_count%2Cmessage_thread_token%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"

    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }

    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def parse(self, response):
        """
        提取出html页面中的所有url 并跟踪这些url进行一步爬取
        如果提取的url中格式为 /question/xxx 就下载之后直接进入解析函数
        """
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                # 如果提取到question相关的页面则下载后交由提取函数进行处理
                request_url = match_obj.group(1)
                question_id = match_obj.group(2)
                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question,
                                     meta={"question_id": question_id})
            else:
                # yield scrapy.Request(url, headers=self.headers, callback=self.parse)
                pass

    def parse_question(self, response):
        # 处理question页面， 从页面中提取出具体的question item

        match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
        if match_obj:
            question_id = int(match_obj.group(2))

        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        item_loader.add_xpath('title', '//div[@class="QuestionHeader-main"]/h1/text()')
        item_loader.add_xpath('content', '//div[@class="QuestionHeader-detail"]')
        item_loader.add_value('url', response.url)
        item_loader.add_value('zhihu_id', question_id)
        item_loader.add_xpath('answer_num', '//h4[@class="List-headerText"]/span/text()')
        item_loader.add_xpath('comments_num', '//div[@class="QuestionHeader-Comment"]/button/text()')
        item_loader.add_xpath('watch_user_num', '//*[@class="NumberBoard-itemInner"]/strong/text()')
        item_loader.add_xpath('topics', '//div[contains(@class, "QuestionTopic")]//div[@class="Popover"]/div/text()')
        question_item = item_loader.load_item()
        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0), callback=self.parse_answer,
                             headers=self.headers)
        yield question_item

    def parse_answer(self, reponse):
        # 处理question 的 answer
        ans_json = json.loads(reponse.text)
        is_end = ans_json['paging']['is_end']
        next_url = ans_json['paging']['next']

        # 提取具体字段
        for answer in ans_json['data']:
            answer_item = ZhihuAnswerItem()
            answer_item['zhihu_id'] = answer['id']
            answer_item['url'] = answer['url']
            answer_item['question_id'] = answer['question']['id']
            answer_item['author_id'] = answer['author']['id'] if 'id' in answer['author'] else None
            answer_item['content'] = answer['content'] if 'content' in answer else None
            answer_item['praise_num'] = answer['voteup_count']
            answer_item['comments_num'] = answer['comment_count']
            answer_item['create_time'] = answer['created_time']
            answer_item['update_time'] = answer['updated_time']
            answer_item['crawl_time'] = datetime.datetime.now()
            yield answer_item

        if not is_end:
            datetime.time.sleep(1.5)
            print('休眠1.5秒,防止301')
            yield scrapy.Request(next_url, callback=self.parse_answer, headers=self.headers)

    def start_requests(self):
        from selenium import webdriver
        browser = webdriver.Chrome(executable_path=chromedriver_path)
        browser.get("https://www.zhihu.com/signin")
        browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
            "13535419055")
        browser.find_element_by_css_selector(".SignFlow-password input").send_keys(
            "xingfu1204..")
        browser.find_element_by_css_selector(
            ".Button.SignFlow-submitButton").click()
        import time
        time.sleep(10)
        Cookies = browser.get_cookies()
        cookie_dict = {}
        import pickle
        for cookie in Cookies:
            # 写入文件
            # f = open('D:/py3_scrapy/ArticleSpider/ArticleSpider/cookies/zhihu/' + cookie['name'] + '.zhihu', 'wb')
            # pickle.dump(cookie, f)
            # f.close()
            cookie_dict[cookie['name']] = cookie['value']
        browser.close()
        return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict, headers=self.headers,
                               callback=self.parse)]
