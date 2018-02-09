# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
# TakeFirst 只要第一个值
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader


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
