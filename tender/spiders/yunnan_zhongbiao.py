import scrapy
import json
from tender.items import TenderItem
from scrapy_splash import SplashRequest
import re
from lxml import etree


class YunnanZhongbiaoSpider(scrapy.Spider):
    name = 'yunnan_zhongbiao'
    allowed_domains = ['www.ccgp-yunnan.gov.cn']
    start_urls = ['http://www.ccgp-yunnan.gov.cn/bulletin.do?method=moreListQuery']
    content_url = 'http://www.ccgp-yunnan.gov.cn/newbulletin_zz.do?method=preinsertgomodify&operator_state=1&flag=view&bulletin_id={bulletin_id}'

    province = '云南'
    typical = '中标'
    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']
        for pageNum in range(next_page, max_page):
            # post数据拼装
            form_data = {
                # 固定的中标渠道id
                'current': str(pageNum),
                'rowCount': '10',
                'searchPhrase': '',
                'query_sign': '2',
            }
            yield scrapy.FormRequest(self.start_urls[0], formdata=form_data, callback=self.parse, dont_filter=True)

    def parse(self, response):
        rs =  json.loads(response.text)
        if not rs:
            return 
        for row_data in rs['rows']:
            url = self.content_url.replace('{bulletin_id}',row_data['bulletin_id'])
            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data['finishday']
            item['title'] = row_data['bulletintitle']
            item['province'] = self.province
            item['typical'] = self.typical 
            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            yield request

    def parse_detail(self, response):
        item = response.meta['item']
        content = response.xpath("//div[@class='table']").get()

        re_style = re.compile('<\s*a[^>].*>[^<]*<\s*/\s*a\s*>', re.I)
        item['content'] = re_style.sub('', content) # 去掉a标签
        item['html_source'] = response.body
        yield item
