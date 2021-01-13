import scrapy
from tender.items import TenderItem 
from scrapy.shell import inspect_response
import json
import re

class NingboZhaobiaoSpider(scrapy.Spider):
    name = 'ningbo_zhaobiao'
    allowed_domains = ['www.ccgp-ningbo.gov.cn']
    start_urls = ['http://www.ccgp-ningbo.gov.cn/project/zcyNotice.aspx?noticetype=2']

    province = '宁波'
    typical = '招标'
    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']
        for pageNum in range(next_page, max_page):
            # post数据拼装
            form_data = {
                '__EVENTARGUMENT': str(pageNum),
            }
            yield scrapy.FormRequest(self.start_urls[0], formdata=form_data, callback=self.parse, dont_filter=True)
    def parse(self, response):
        list = response.xpath('//table[@id="gdvNotice3"]/tr')
        for row_data in list:
            url = row_data.css('tr td a::attr(href)').get()
            if url is None:
                continue
            url = response.urljoin(url)
            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data.xpath('td[4]/text()').get().strip()
            item['title'] = row_data.xpath('td[3]/a/text()').get().strip()
            item['province'] = self.province
            item['typical'] = self.typical 

            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            yield request

    def parse_detail(self, response):
        item = response.meta['item']
        
        content = response.xpath("//table").get()
        re_style = re.compile('<\s*a[^>].*>[^<]*<\s*/\s*a\s*>', re.I)
        content = re_style.sub('', content) # 去掉a标签
        re_style = re.compile('<\s*style[^>]*>[^<][\s\S]*<\s*/\s*style\s*>', re.I)
        content = re_style.sub('', content)
        item['content'] = content
        item['html_source'] = response.body
        yield item
