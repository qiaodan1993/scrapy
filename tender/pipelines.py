# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class TenderPipeline:
    def dbHandle(self):
        conn = pymysql.connect(
            host="rm-bp12r25pi1e1q65gwzo.mysql.rds.aliyuncs.com",
            user="developer_user",
            passwd="dev123456",
            charset="utf8",
            use_unicode=False
        )
        return conn

    def process_item(self, item, spider):
        dbObject = self.dbHandle()
        cursor = dbObject.cursor()
        # cursor.execute()
        sql = "INSERT INTO developer_db.tender_source(url, title, html_content, publish_at, province, city) VALUES(%s, %s, %s, " \
              "%s, %s, %s) "
        try:
            cursor.execute(sql,
                           (item['url'], item['title'], item['html_content'], item['publish_at'], item['province'], item['city']))
            cursor.connection.commit()
        except BaseException as e:
            print("错误在这里>>>>>>>>>>>>>", e, "<<<<<<<<<<<<<错误在这里")
            dbObject.rollback()
        return item
