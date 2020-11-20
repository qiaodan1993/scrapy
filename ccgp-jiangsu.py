import scrapy
import time
import requests
import random
from lxml import etree
from dbhelper import DbPipline


class CcgpJiangSuSpider(scrapy.Spider):
    name = '江苏政府采购网爬虫程序'
    start_urls = [
        'http://www.ccgp-jiangsu.gov.cn/ggxx/gkzbgg/'
    ]
    next_page = 1

    def parse(self, response):
        for row_data in response.xpath('//*[@id="newsList"]/ul/li'):
            time.sleep(random.randint(1, 2))  # 随机休眠 1-2s
            webpage_date = row_data.css('li::text').extract()[-1].split()[0]
            local_date = time.strftime("%Y-%m-%d", time.localtime(time.time()))

            if int(time.mktime(time.strptime(local_date, "%Y-%m-%d"))) - int(
                    time.mktime(time.strptime(webpage_date, "%Y-%m-%d"))) < 86400 * 60:  # 限制爬取xx天, 60为天数

                detail_page_url = CcgpJiangSuSpider.start_urls[0] + row_data.css('li a::attr(href)').extract_first()

                detail_resp = requests.get(detail_page_url)  # 详情页的响应
                selector = etree.HTML(detail_resp.content)
                content = ''.join(selector.xpath('/html/body/div[2]/div[2]/div[2]/div[2]/*[name(.)!="style"]//text()')).replace("\n", "").replace("\t", "").replace(" ", "")  # 获取所有文本并格式化

                item = {'detail_page_url': CcgpJiangSuSpider.start_urls[0] + row_data.css('li a::attr(href)').extract_first(),
                        'title': row_data.css('li a::text').extract_first(),
                        'date': row_data.css('li::text').extract()[-1].split()[0],
                        'content': content,
                        'province': '江苏'
                        }

                if item['content']:  # 404导致的没有内容文本不存库
                    DbPipline().process_item(item)
                yield item

        if self.next_page < 1000:  # 控制爬取的页数
            yield response.follow(self.start_urls[0] + 'index_' + str(self.next_page) + '.html', self.parse)
            self.next_page = self.next_page + 1

        # 终端执行命令  scrapy runspider ccgp-jiangsu.py -o test.jl -s FEED_EXPORT_ENCODING=UTF-8
        # 请求页面终端调试页面 scrapy shell http://www.ccgp-jiangsu.gov.cn/ggxx/gkzbgg/index.html
