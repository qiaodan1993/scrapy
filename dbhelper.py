import pymysql

# DB_HOST=rm-bp12r25pi1e1q65gwzo.mysql.rds.aliyuncs.com
# DB_PORT=3306
# DB_DATABASE=developer_db
# DB_USERNAME=developer_user
# DB_PASSWORD=dev123456
# DB_TABLE=ebaina_scrapy

class DbPipline:
    def dbHandle(self):
        conn = pymysql.connect(
            host="rm-bp12r25pi1e1q65gwzo.mysql.rds.aliyuncs.com",
            user="developer_user",
            passwd="dev123456",
            charset="utf8",
            use_unicode=False
        )
        return conn

    def process_item(self, item):
        dbObject = self.dbHandle()
        cursor = dbObject.cursor()
        # cursor.execute()
        sql = "INSERT INTO developer_db.ebaina_scrapy(url, title, content, publish_at, province) VALUES(%s, %s, %s, %s, %s)"
        try:
            cursor.execute(sql, (item['detail_page_url'], item['title'], item['content'], item['date'], item['province']))
            cursor.connection.commit()
        except BaseException as e:
            print("错误在这里>>>>>>>>>>>>>", e, "<<<<<<<<<<<<<错误在这里")
            dbObject.rollback()
        return item


if __name__ == '__main__':
    DbPipline().process_item(item={"detail_page_url": "http://www.ccgp-jiangsu.gov.cn/ggxx/gkzbgg/./yangzhou/202011/t20201120_756131.html", "title": "扬州市公共资源交易中心仪征分中心关于2021年仪征市本级国家机关、事业...", "date": "2020-11-20", "content": "test"})