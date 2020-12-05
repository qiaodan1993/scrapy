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
    dbpool = None
    def open_spider(self, spider):
        if TenderPipeline.dbpool is None:
            TenderPipeline.dbpool = adbapi.ConnectionPool('pymysql',
                    cp_max=1,
                    cp_min=1,
                    host=spider.settings['MYSQL_HOST'],
                    user=spider.settings['MYSQL_USER'],
                    passwd=spider.settings['MYSQL_PASSWD'],
                    charset=spider.settings['MYSQL_CHARSET'],
                    db=spider.settings['MYSQL_DB'],
                    use_unicode=spider.settings['MYSQL_UNICODE'])
        else:
            print("USE adbapi ConnectionPool")

    def close_spider(self, spider):
        TenderPipeline.dbpool.close()

    def process_item(self, item, spider):
        for val in item:
            if item[val] is None:
                raise DropItem("None:"+item[val])
        try:
            TenderPipeline.dbpool.runInteraction(self.do_insert, item)
        except:
            raise DropItem("INSERT FALSE")
        return item
    
    def do_insert(self, tx, item):
        sql = "INSERT INTO tender_source(url, province, typical, publish_at, title, content, html_source) VALUES(%s, %s, %s, %s, " \
              "%s, %s, %s)"
        values = (item['url'], item['province'], item['typical'], item['publish_at'], item['title'], item['content'], item['html_source'])
        tx.execute(sql, values)