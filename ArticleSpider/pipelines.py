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

import MySQLdb


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


class MysqlPipeline(object):
    """
    导数据进mysql
    """

    def __init__(self):
        # self.conn = MySQLdb.connect('host', 'user', 'password', 'dbname', charset='utf8', use_unicode=True)
        self.conn = MySQLdb.connect('127.0.0.1', 'root', '123123', 'article_spider', charset='utf8',
                                    use_unicode=True)  # 创建链接
        self.cursor = self.conn.cursor()  # 操作mysql

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article(title,create_date,url,url_object_id,fron_image_url,front_image_path,comment_nums,praise_nums,fav_nums,tags,content)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        self.cursor.execute(insert_sql, (
            item['title'], item['create_date'], item['url'], item['url_object_id'], item['fron_image_url'],
            item['front_image_path'], item['comment_nums'], item['praise_nums'], item['fav_nums'], item['tags'],
            item['content']))
        self.conn.commit()


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
