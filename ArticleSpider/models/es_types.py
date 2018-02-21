from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, InnerDoc, Completion, Keyword, Text, Integer

from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=["localhost"])  # 确定链接那个服务器


class ArticleType(DocType):
    # 伯乐在线文章类型
    # Text()类型会被分析器分词
    title = Text(analyzer="ik_max_word")
    create_date = Date()
    url = Keyword()
    url_object_id = Keyword()
    fron_image_url = Keyword()
    front_image_path = Keyword()
    praise_nums = Integer()
    comment_nums = Integer()
    fav_nums = Integer()
    tags = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")

    class Meta:
        # 确定插入那个索引和type
        index = "jobbole"
        doc_type = "article"


if __name__ == '__main__':
    # 调用init() 会直接生成mapping映射
    ArticleType.init()
