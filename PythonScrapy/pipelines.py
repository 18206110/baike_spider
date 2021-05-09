# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import redis


class PythonscrapyPipeline:

    def process_item(self, item, spider):

        # 建立连接
        pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
        conn = redis.Redis(connection_pool=pool)

        # 取出标题
        for key, value in item.items():
            value1 = value
            break
        print('目标网站:' + value1)

        for key, value in item.items():
            conn.hset(value1, key, value)

        print(value1 + '爬取成功!')
        # print(conn.hgetall(value1))
        return item
