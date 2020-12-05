import scrapy
import json
from tender.items import TenderItem 
import datetime

class ChongqingZhongBiaoSpider(scrapy.Spider):
    name = 'chongqing_zhongbiao'
    allowed_domains = ['www.ccgp-chongqing.gov.cn']
    start_urls = ['https://www.ccgp-chongqing.gov.cn/gwebsite/api/v1/notices/stable/new?isResult=2&ps=20&startDate=2020-06-06&type=300,302,304,3041,305,306,307,308&endDate=']

    province = '重庆'
    typical = '中标'

    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']
        endDate = str(datetime.date.today())

        for pageNum in range(next_page, max_page):
            yield scrapy.Request(self.start_urls[0] + endDate + '&pi=' + str(pageNum), self.parse, dont_filter=True)

    def parse(self, response):
        js = json.loads(response.body) 
        for row_data in js["notices"]:
            url = response.urljoin(row_data["id"])

            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data["issueTime"].split(' ')[0]
            item['province'] = self.province
            item['typical'] = self.typical
            item['title'] = row_data["title"]


            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            
            yield request
    
    def parse_detail(self, response):
        item = response.meta['item']

        js = json.loads(response.body)
        item['content'] = js["notice"]["html"]
        item['html_source'] = js["notice"]["html"]

        yield item