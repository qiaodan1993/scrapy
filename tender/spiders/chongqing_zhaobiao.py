import scrapy
import json
from tender.items import TenderItem 
import datetime
import re

class ChongqingZhaoBiaoSpider(scrapy.Spider):
    name = 'chongqing_zhaobiao'
    allowed_domains = ['www.ccgp-chongqing.gov.cn']
    start_urls = ['https://www.ccgp-chongqing.gov.cn/gwebsite/api/v1/notices/stable/new?isResult=1&ps=20&startDate=2020-06-06&type=100,200,201,202,203,204,205,206,207,309,400,401,402,3091,4001&endDate=']

    province = '重庆'
    typical = '招标'

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
        content = js["notice"]["html"]
        re_style = re.compile('<\s*style[^>]*>[^<][\s\S]*<\s*/\s*style\s*>', re.I)
        content = re_style.sub('', content)
        re_style = re.compile('<\s*a[^>].*>[^<]*<\s*/\s*a\s*>', re.I)
        content = re_style.sub('', content)

        item['content'] = content # 去掉a标签
        item['html_source'] = js["notice"]["html"]

        yield item