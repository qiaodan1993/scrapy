# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi

class TenderPipeline:

    def __init__(self):
        """Opens a MySQL connection pool"""
        # Parse MySQL URL and try to initialize a connection
        self.dbpool = adbapi.ConnectionPool('pymysql',
                cp_max=1,
                cp_min=1,
                host="rm-bp12r25pi1e1q65gwzo.mysql.rds.aliyuncs.com",
                user="developer_user",
                passwd="dev123456",
                charset="utf8",
                db="developer_db",
                use_unicode=False)


    def close_spider(self, spider):
        self.dbpool.close()

    def process_item(self, item, spider):
        try:
            self.dbpool.runInteraction(self.do_insert, item)
        except:
            raise DropItem("Insert Fail")
        return item
    
    def do_insert(self, tx, item):
        sql = "INSERT INTO tender_source(url, province, typical, publish_at, title, content, html_source) VALUES(%s, %s, %s, %s, " \
              "%s, %s, %s)"
        values = (item['url'], item['province'], item['typical'], item['publish_at'], item['title'], item['content'], item['html_source'])
        tx.execute(sql, values)