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
from twisted.enterprise import adbapi

import MySQLdb
import MySQLdb.cursors


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
    导数据进mysql  第一种方法!但是有个缺点  爬虫解析出来的数据有可能比mysql执行insert语句要快!那么就会形成阻塞!
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


class MysqlTwistedPipeline(object):
    """
    mysql 插入的异步化 这样就不会形成阻塞
    可以将配置写到settings
    """

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod  # 类方法 被spider调用 然后参数的settings 就是 配置文件的settings
    def from_settings(cls, settings):
        dbparms = dict(
            # !!!!!!键的名字要和mysqlDB传进去的一样  固定写法!!!!!!!!!!!
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparms)  # 连接池  *是元组 **字典 是可变参数
        return cls(dbpool)

    def process_item(self, item, spider):
        """
        使用twisted将mysql插入变成异步执行
        """
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)  # 异步执行的时候出现错误的要处理的函数
        return item

    def handle_error(self, failure):
        """
        处理异步插入的异常
        :param failure:
        :return:
        """
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        insert_sql = """
                    insert into jobbole_article(title,create_date,url,url_object_id,fron_image_url,front_image_path,comment_nums,praise_nums,fav_nums,tags,content)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """
        cursor.execute(insert_sql, (
            item['title'], item['create_date'], item['url'], item['url_object_id'], item['fron_image_url'],
            item['front_image_path'], item['comment_nums'], item['praise_nums'], item['fav_nums'], item['tags'],
            item['content']))


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
        if 'front_image_url' in item:
            # results 是个元组 第一个是ok表示获取成功 第二个是一个字典
            for ok, value in results:
                image_file_path = value['path']
            item['front_image_path'] = image_file_path
        return item
