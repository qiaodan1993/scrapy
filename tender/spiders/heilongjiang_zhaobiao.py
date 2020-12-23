import scrapy
from tender.items import TenderItem 
from scrapy.shell import inspect_response
import re

class HeilongjiangZhaoBiaoSpider(scrapy.Spider):
    name = 'heilongjiang_zhaobiao'
    allowed_domains = ['www.ccgp-heilongj.gov.cn']
    start_urls = ['http://www.ccgp-heilongj.gov.cn/xwzs!queryGd.action']

    province = '黑龙江'
    typical = '招标'

    form_data = {'xwzsPage.zlbh': '', 'xwzsPage.GJZ':'','xwzsPage.pageNo': '1', 'xwzsPage.pageSize':'20', 'lbbh': '99', 'id': '110','xwzsPage.LBBH': '99'}
    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']


        for pageNum in range(next_page, max_page):
            self.form_data["xwzsPage.pageNo"] = str(pageNum)
            yield scrapy.FormRequest(self.start_urls[0], formdata=self.form_data, headers={'COOKIE': 'JSESSIONID=gq1KfMnf2fGrxpHhfVLm8RvPx9qrGpw5RL9QmNJnyyptkgK6f9TJ!1180316171'}, dont_filter=True)


    def parse(self, response):
        for row_data in response.xpath('//div[@class="xxei"]'):
            url = response.urljoin(row_data.css('span a::attr(onclick)').get().split("'")[1])
            
            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data.xpath('span[position()=2]/text()').get()
            item['province'] = self.province
            item['typical'] = self.typical

            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            
            yield request
    
    def parse_detail(self, response):
        item = response.meta['item']

        item['title'] = response.xpath('//div[@class="mtt"]/p[@class="mtt_01"]/text()').get()

        re_style = re.compile('<\s*a[^>].*>[^<]*<\s*/\s*a\s*>', re.I)
        content = response.xpath('//div[@id="rightej"]/div[@class="xxej"]').get()
        item['content'] = re_style.sub('', content) # 去掉a标签
        item['html_source'] = response.body

        yield item