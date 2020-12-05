import scrapy
from tender.items import TenderItem 
from scrapy.shell import inspect_response
import json
import datetime

class HunanZhaobiaoSpider(scrapy.Spider):
    name = 'hunan_zhaobiao'
    allowed_domains = ['www.ccgp-hunan.gov.cn']
    start_urls = ['http://www.ccgp-hunan.gov.cn/mvc/getNoticeList4Web.do']

    province = '湖南'
    typical = '招标'

    base_url = 'http://www.ccgp-hunan.gov.cn/mvc/viewNoticeContent.do?noticeId='

    form_data = {'page': '1', 'pageSize':'18', 'nType': 'prcmNotices', 'startDate': '2020-01-01',
'endDate': '2020-12-05'}

    def start_requests(self):
        self.next_page = self.settings['COMMAND_NEXT_PAGE']
        self.max_page = self.settings['COMMAND_MAX_PAGE']
        self.form_data["endDate"] = str(datetime.date.today())

        yield scrapy.FormRequest(self.start_urls[0], formdata=self.form_data, dont_filter=True)

    def parse(self, response):
        js = json.loads(response.body)

        # inspect_response(response, self)

        for row_data in js["rows"]:
            url = self.base_url + str(row_data["NOTICE_ID"])
            item = TenderItem()
            item['title'] = row_data['NOTICE_TITLE']
            item['publish_at'] = row_data['NEWWORK_DATE']
            item['url'] = url
            item['province'] = self.province
            item['typical'] = self.typical

            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item

            yield request

        self.next_page = self.next_page + 1
        if self.next_page < self.max_page:  # 控制爬取的页数
            self.form_data["page"] = str(self.next_page)
            yield scrapy.FormRequest(self.start_urls[0], formdata=self.form_data, dont_filter=True)
            


    def parse_detail(self, response):
        item = response.meta['item']
        item['content'] = response.xpath('//table').get()
        item['html_source'] = response.body
        
        yield item