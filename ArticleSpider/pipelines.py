# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

from scrapy.pipelines.images import ImagesPipeline
# codecs 和open最大的区别的就是让我们避免很多编码的问题
import codecs
from scrapy.exporters import JsonItemExporter  # scrapy 自带的输出json


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    """
    自定义json文件导出

    """
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + '\n'  # 有中文ensure_ascii一定要设置为False
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class JsonExporterPipleline(object):
    """
    调用scrapy自带的json export到处json文件
    """

    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()  # 停止导出
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item=item)
        return item


class ArticleImagePipelin(ImagesPipeline):
    # 重写
    def item_completed(self, results, item, info):
        # results 是个元组 第一个是ok表示获取成功 第二个是一个字典
        for ok, value in results:
            image_file_path = value['path']
        item['front_image_path'] = image_file_path

        return item
