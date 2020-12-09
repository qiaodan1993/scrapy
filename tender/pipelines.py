# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi
import scrapy

class TenderPipeline:
    dbpool = None
    def __init__(self, crawler):
        if TenderPipeline.dbpool is None:
            TenderPipeline.dbpool = adbapi.ConnectionPool('pymysql',
                    cp_max=1,
                    cp_min=1,
                    host=crawler.settings['MYSQL_HOST'],
                    user=crawler.settings['MYSQL_USER'],
                    passwd=crawler.settings['MYSQL_PASSWD'],
                    charset=crawler.settings['MYSQL_CHARSET'],
                    db=crawler.settings['MYSQL_DB'],
                    use_unicode=crawler.settings['MYSQL_UNICODE'])
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)
    
    def __DEL__(self):
        if TenderPipeline.dbpool is not None:
            TenderPipeline.dbpool.close()

    def feishu_notify(self, message):
        url = 'https://open.feishu.cn/open-apis/bot/v2/hook/cf52b690-eeff-4d91-b781-1b10c6bee67d'
        content = { "msg_type": "text",
                "content": {
                    "text": "scrapy " + message
                }
        }
        scrapy.Request(url, method='POST', body=json.dumps(content), headers={"Content-Type": "application/json"})


    def process_item(self, item, spider):
        for val in item:
            if item[val] is None:
                self.feishu_notify("None:" + val)
                raise DropItem("None:"+ val)
            item[val] = item[val].strip()
        try:
            TenderPipeline.dbpool.runInteraction(self.do_insert, item)
        except:
            self.feishu_notify("insert false")
            raise DropItem("insert false")
        return item
    
    def do_insert(self, tx, item):
        sql = "INSERT INTO tender_source(url, province, typical, publish_at, title, content, html_source) VALUES(%s, %s, %s, %s, " \
              "%s, %s, %s)"
        values = (item['url'], item['province'], item['typical'], item['publish_at'], item['title'], item['content'], item['html_source'])
        tx.execute(sql, values)