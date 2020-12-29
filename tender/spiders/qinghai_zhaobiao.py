import scrapy
from tender.items import TenderItem 
from scrapy.shell import inspect_response
import json
import time
import re

class QinghaiZhaoBiaoSpider(scrapy.Spider):
    name = 'qinghai_zhaobiao'
    allowed_domains = ['www.ccgp-qinghai.gov.cn']
    start_urls = ['http://www.ccgp-qinghai.gov.cn/front/search/category']

    province = '青海'
    typical = '招标'

    form_data = {"pageNo":'1', "pageSize":'15', "categoryCode":"ZcyAnnouncement2"}

    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']
        
        for pageNum in range(next_page, max_page):
            self.form_data['pageNo'] = str(pageNum)
            yield scrapy.Request(self.start_urls[0], method='POST', body=json.dumps(self.form_data),headers={'Content-Type':'application/json'},  dont_filter=True)


    def parse(self, response):
        js = json.loads(response.body)
        for row_data in js['hits']['hits']:
            
            url = response.urljoin(row_data['_source']['url'])

            item = TenderItem()
            item['url'] = url
            item['title'] = row_data['_source']['title']


            timeArray = time.localtime(int(row_data['_source']["publishDate"])/1000)
            item['publish_at'] = time.strftime("%Y-%m-%d", timeArray)

            item['province'] = self.province
            item['typical'] = self.typical

            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            
            yield request
    
    def parse_detail(self, response):
        item = response.meta['item']

        item['html_source'] = response.xpath('//input[@name="articleDetail"]/@value').get()
        js = json.loads(item['html_source'])
        content = js['content']
        re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)
        content = re_style.sub('', content)
        re_style = re.compile('<\s*a[^>].*>[^<]*<\s*/\s*a\s*>', re.I)
        content = re_style.sub('', content)
        item['content'] = content # 去掉style标签

        yield item