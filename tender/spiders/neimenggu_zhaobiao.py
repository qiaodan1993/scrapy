import scrapy
from tender.items import TenderItem 
from scrapy.shell import inspect_response
import json

class NeimongguZhaoBiaoSpider(scrapy.Spider):
    name = 'neimonggu_zhaobiao'
    allowed_domains = ['www.nmgp.gov.cn']
    start_urls = ['http://www.nmgp.gov.cn/zfcgwslave/web/index.php?r=new-data%2Fanndata']

    base_url = 'http://www.nmgp.gov.cn/category/cggg?tb_id=1'
    province = '内蒙古'
    typical = '招标'

    form_data = {'type_name': '1', 'byf_page': '2', 'fun': 'cggg', 'page_size': '18'}
    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']
        
        for pageNum in range(next_page, max_page):
            self.form_data["byf_page"] = str(pageNum)
            yield scrapy.FormRequest(self.start_urls[0], formdata=self.form_data, dont_filter=True)

    def parse(self, response):
        # inspect_response(response, self)
        js = json.loads(response.body)
        for row_data in js[0]:
            url = self.base_url + '&type=' + row_data['type'] + '&p_id=' + row_data['wp_mark_id']

            item = TenderItem()
            item['url'] = url
            item['title'] = row_data['TITLE']

            item['publish_at'] = row_data['SUBDATE'].split('：')[1][:-1]
            item['province'] = self.province
            item['typical'] = self.typical

            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            
            yield request
    
    def parse_detail(self, response):
        item = response.meta['item']

        item['content'] = response.xpath('//div[@class="protect"]').get()
        item['html_source'] = response.body

        yield item