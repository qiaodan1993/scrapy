import scrapy
from tender.items import TenderItem 
from scrapy.shell import inspect_response
import json
import re


class XiamenZhaobiaoSpider(scrapy.Spider):
    name = 'xiamen_zhaobiao'
    allowed_domains = ['www.ccgp-xiamen.gov.cn']
    start_urls = ['http://www.ccgp-xiamen.gov.cn/350200/noticelist/d03180adb4de41acbb063875889f9af1/']

    province = '厦门'
    typical = '招标'
    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']
        for pageNum in range(next_page, max_page):
            yield scrapy.Request(self.start_urls[0]+ '?page='+str(pageNum), self.parse, dont_filter=True)
    def parse(self, response):
        
        list = response.xpath('//tr[@class="gradeX"]')
        for row_data in list:
            url = row_data.css('tr td a::attr(href)').get()
            if url is None:
                continue
            url = response.urljoin(url)
            item = TenderItem()
            item['url'] = url
            item['title'] = row_data.xpath('./td[4]/a/text()').get().strip()
            item['publish_at'] = row_data.xpath('./td[5]/text()').get().strip()
            item['province'] = self.province
            item['typical'] = self.typical 
            # return 
            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            yield request

    def parse_detail(self, response):
        item = response.meta['item'] 
        content = response.xpath("//div[@id='print-content']").get()
        re_style = re.compile('<\s*a[^>].*>[^<]*<\s*/\s*a\s*>', re.I)
        content = re_style.sub('', content) # 去掉a标签
        re_style = re.compile('<\s*style[^>]*>[^<][\s\S]*<\s*/\s*style\s*>', re.I)
        content = re_style.sub('', content)
        item['content'] = content
        item['html_source'] = response.body
        yield item
