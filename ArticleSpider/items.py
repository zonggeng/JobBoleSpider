# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import re

from ArticleSpider.utils.common import extract_num, Remove_the_comma
from ArticleSpider.settings import SQL_DATE_FORMAT, SQL_DATETIME_FORMAT
import scrapy
import datetime
# TakeFirst 只要第一个值
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader
from w3lib.html import remove_tags


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


# def add_jobbole(value):
#     return value + '-jobbole'


def handle_date(value):
    # 这里获取到的value是 jobbole 爬虫文件的 item_loader.add_xpath 通过规则传进来的
    try:
        value = value.strip().replace(' ·', '')
        value = datetime.datetime.strptime(value, '%Y/%m/%d').date()  # 格式化格式
    except Exception as e:
        value = datetime.datetime.now()  # 当前时间
    return value


def handle_fav_nums(value):
    value = value.strip().replace(' 收藏', '')
    if value == '收藏':
        value = 0
    return value


def handle_comment_nums(value):
    value = value.strip().replace(' 评论', '')
    if value == '评论':
        value = 0
    return value


def handle_tags(value):
    value = ''.join(value)
    if '评论' in value:
        return None
    return value


# 继承itemloader  所以爬虫文件实现就要实现这个类
class ArticleItemloader(ItemLoader):
    """
    自定义itemLoader实现获取第一个值
    取了第一个值!输出就不是list了!
    """
    default_output_processor = TakeFirst()


def return_value(value):
    return value


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field(
        # 当有数据传过来的时候可以预处理 MapCompose()可以传函数多个函数也可以的!执行顺序从左往右
        # input_processor=MapCompose(add_jobbole)
    )
    create_date = scrapy.Field(
        input_processor=MapCompose(handle_date),  # 传进来用什么参数处理
        # output_processor=TakeFirst()  # 传出去要第一个值 因为继承ItemLoader类重写了所以可以不要了
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()  # 上面的url长度不确定 所以用MD5变成固定的id
    fron_image_url = scrapy.Field(
        # 自带下载图片的pipeline 需要传进去的是一个list所以要用函数处理一下 处理玩后输出要是list
        output_processor=MapCompose(return_value)  # 会覆盖掉我们继承重写的default_output_processor

    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field()
    comment_nums = scrapy.Field(
        input_processor=MapCompose(handle_comment_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(handle_fav_nums)
    )
    tags = scrapy.Field(
        # 因为获取到的tags是一个list所以会分次传进来!所以要用join链接分次传进来的数据
        output_processor=Join(','),  # 会覆盖掉我们继承重写的default_output_processor
        input_processor=MapCompose(handle_tags)
    )
    content = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                           insert into jobbole_article(title,create_date,url,url_object_id,fron_image_url,front_image_path,comment_nums,praise_nums,fav_nums,tags,content)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                           ON DUPLICATE KEY UPDATE fav_nums=VALUES (fav_nums),praise_nums=VALUES (praise_nums)
                       """

        params = (
            self.item['title'], self.item['create_date'], self.item['url'], self.item['url_object_id'],
            self.item['fron_image_url'],
            self.item['front_image_path'], self.item['comment_nums'], self.item['praise_nums'], self.item['fav_nums'],
            self.item['tags'],
            self.item['content'])

        return insert_sql, params


class ZhihuQuestionItem(scrapy.Item):
    # 知乎的问题
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                           insert into zhihu_question(zhihu_id,topics,url,title,content,answer_num,comments_num,watch_user_num,click_num,crawl_time)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                           ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num), comments_num=VALUES(comments_num),watch_user_num=VALUES(watch_user_num), click_num=VALUES(click_num)
                       """
        zhihu_id = int(self['zhihu_id'][0])
        topics = ','.join(self['topics'])
        url = self['url'][0]
        title = ''.join(self['title']).encode('utf-8')
        content = ''.join(self['content'])
        answer_num = Remove_the_comma(self['answer_num'][0]) if self['answer_num'][0] else 0
        comments_num = extract_num(''.join(self['comments_num']))
        watch_user_num = Remove_the_comma(self['watch_user_num'][0]) if self['watch_user_num'][0] else 0
        click_num = Remove_the_comma(self['watch_user_num'][1]) if self['watch_user_num'][1] else 0
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (
            zhihu_id, topics, url, title, content, answer_num, comments_num, watch_user_num, click_num, crawl_time)

        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    # 知乎的问题回答item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                           insert into zhihu_answer(zhihu_id,url,question_id,author_id,content,praise_num,comments_num,create_time,update_time,crawl_time)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                           ON DUPLICATE KEY UPDATE content=VALUES (content),comments_num =VALUES (comments_num),praise_num=VALUES (praise_num),update_time=VALUES (update_time)
                       """
        zhihu_id = self['zhihu_id']
        url = self['url']
        question_id = self['question_id']
        author_id = self['author_id']
        content = self['content']
        praise_num = self['praise_num']
        comments_num = self['comments_num']
        create_time = datetime.datetime.fromtimestamp(self["create_time"]).strftime(SQL_DATE_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATE_FORMAT)
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (
            zhihu_id, url, question_id, author_id, content, praise_num, comments_num, create_time, update_time,
            crawl_time)

        return insert_sql, params


def remove_splash(value):
    # 去掉工作城市的斜线
    return value.replace("/", "")


def handle_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip() != "查看地图"]
    return "".join(addr_list)


class LagouJobItemLoader(ItemLoader):
    # 自定义itemloader
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    # 拉勾网职位信息
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary_min = scrapy.Field()
    salary_max = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    work_years_min = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    work_years_max = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, handle_jobaddr),
    )
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(",")
    )
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into lagou_job(title, url, url_object_id, salary_min, salary_max, job_city, work_years_min, work_years_max, degree_need,
            job_type, publish_time, job_advantage, job_desc, job_addr, company_name, company_url,
            tags, crawl_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE salary_min=VALUES(salary_min), salary_max=VALUES(salary_max), job_desc=VALUES(job_desc)
        """

        match_obj1 = re.match("经验(\d+)-(\d+)年", self['work_years_min'])
        match_obj2 = re.match("经验应届毕业生", self['work_years_min'])
        match_obj3 = re.match("经验不限", self['work_years_min'])
        match_obj4 = re.match("经验(\d+)年以下", self['work_years_min'])
        match_obj5 = re.match("经验(\d+)年以上", self['work_years_min'])

        if match_obj1:
            self['work_years_min'] = match_obj1.group(1)
            self['work_years_max'] = match_obj1.group(2)
        elif match_obj2:
            self['work_years_min'] = 0.5
            self['work_years_max'] = 0.5
        elif match_obj3:
            self['work_years_min'] = 0
            self['work_years_max'] = 0
        elif match_obj4:
            self['work_years_min'] = 0
            self['work_years_max'] = match_obj4.group(1)
        elif match_obj5:
            self['work_years_min'] = match_obj4.group(1)
            self['work_years_max'] = match_obj4.group(1) + 100
        else:
            self['work_years_min'] = 999
            self['work_years_max'] = 999

        match_salary = re.match("(\d+)[Kk]-(\d+)[Kk]", self['salary_min'])
        if match_salary:
            self['salary_min'] = match_salary.group(1)
            self['salary_max'] = match_salary.group(2)
        else:
            self['salary_min'] = 666
            self['salary_max'] = 666
        match_time1 = re.match("(\d+):(\d+).*", self["publish_time"])
        match_time2 = re.match("(\d+)天前.*", self["publish_time"])
        match_time3 = re.match("(\d+)-(\d+)-(\d+)", self["publish_time"])
        if match_time1:
            today = datetime.datetime.now()
            hour = int(match_time1.group(1))
            minutues = int(match_time1.group(2))
            time = datetime.datetime(
                today.year, today.month, today.day, hour, minutues)
            self["publish_time"] = time.strftime(SQL_DATETIME_FORMAT)
        elif match_time2:
            days_ago = int(match_time2.group(1))
            today = datetime.datetime.now() - datetime.timedelta(days=days_ago)
            self["publish_time"] = today.strftime(SQL_DATETIME_FORMAT)
        elif match_time3:
            year = int(match_time3.group(1))
            month = int(match_time3.group(2))
            day = int(match_time3.group(3))
            today = datetime.datetime(year, month, day)
            self["publish_time"] = today.strftime(SQL_DATETIME_FORMAT)
        else:
            self["publish_time"] = datetime.datetime.now(
            ).strftime(SQL_DATETIME_FORMAT)

        params = (
            self["title"],
            self["url"],
            self["url_object_id"],
            self["salary_min"],
            self["salary_max"],
            self["job_city"],
            self["work_years_min"],
            self["work_years_max"],
            self["degree_need"],
            self["job_type"],
            self["publish_time"],
            self["job_advantage"],
            self["job_desc"],
            self["job_addr"],
            self["company_name"],
            self["company_url"],
            self["tags"],
            self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
        )

        return insert_sql, params
