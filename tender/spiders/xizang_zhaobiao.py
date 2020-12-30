import scrapy
from tender.items import TenderItem 
import re

class XizangZhaobiaoSpider(scrapy.Spider):
    name = 'xizang_zhaobiao'
    allowed_domains = ['www.ccgp-xizang.gov.cn']
    start_urls = ['http://www.ccgp-xizang.gov.cn/shopHome/morePolicyNews.action?categoryId=124']

    province = '西藏'
    typical = '招标'
    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']
        for pageNum in range(next_page, max_page):
            # post数据拼装
            form_data = {
                'currentPage': str(pageNum),
            }
            yield scrapy.FormRequest(self.start_urls[0], formdata=form_data, callback=self.parse, dont_filter=True)
    def parse(self, response):
        list = response.xpath('//div[@id="news_div"]/ul/li')
        for row_data in list:
            url = response.urljoin(row_data.css('li div a::attr(href)').get())
            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data.xpath('//span/text()').get().split()[0]
            item['province'] = self.province
            item['typical'] = self.typical 
            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            yield request

    def parse_detail(self, response):
        item = response.meta['item']
        title  = response.xpath("//h2[@class='sd']/font/text()").get()
        content = response.xpath("//div[@class='neirong']/span").get()

        re_style = re.compile('<\s*a[^>].*>[^<]*<\s*/\s*a\s*>', re.I)
        item['title'] = title
        item['content'] = re_style.sub('', content) # 去掉a标签
        item['html_source'] = response.body
        yield item

