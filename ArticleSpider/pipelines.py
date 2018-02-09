# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request
import hashlib
from scrapy.utils.python import to_bytes


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class ArticleImagePipelin(ImagesPipeline):
    # 重写
    def item_completed(self, results, item, info):
        # results 是个元组 第一个是ok表示获取成功 第二个是一个字典
        for ok, value in results:
            image_file_path = value['path']
        item['front_image_path'] = image_file_path

        return item
