# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

class TenderPipeline:
    connect=None
    cursor=None

    def open_spider(self, spider):
        
        if self.connect is None or self.cursor is None:
            self.connect = pymysql.connect(
                host="rm-bp12r25pi1e1q65gwzo.mysql.rds.aliyuncs.com",
                user="developer_user",
                passwd="dev123456",
                charset="utf8",
                db="developer_db",
                use_unicode=False
            )
            self.cursor = self.connect.cursor()

    def close_spider(self, spider):
        if self.cursor is not None:
            self.cursor.close()
    
        if self.connect is not None:
            self.connect.close()

    def process_item(self, item, spider):
        sql = "INSERT INTO tender_source(url, province, typical, publish_at, title, content, html_source) VALUES(%s, %s, %s, %s, " \
              "%s, %s, %s) "
        try:
            self.cursor.execute(sql,
                           (item['url'], item['province'], item['typical'], item['publish_at'], item['title'], item['content'], item['html_source']))
            self.connect.commit()
        except BaseException as e:
            self.connect.rollback()
            raise DropItem(e.args[1])
        return item
