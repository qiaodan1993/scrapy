import scrapy
from tender.items import TenderItem 
import re

class ShanxiZhongBiaoSpider(scrapy.Spider):
    name = 'shanxi_zhongbiao'
    allowed_domains = ['www.ccgp-shanxi.gov.cn']
    start_urls = ['http://www.ccgp-shanxi.gov.cn/view.php?app=&type=&nav=104']

    province = '山西'
    typical = '中标'

    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']

        for pageNum in range(next_page, max_page):
            yield scrapy.Request(self.start_urls[0]+ '&page=' + str(pageNum), self.parse, dont_filter=True)

    def parse(self, response):
        for row_data in response.xpath('//table[@id="node_list"]/tbody/tr'):
            url = response.urljoin(row_data.css('a::attr(href)').get())

            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data.xpath('td[position()=4]/text()').get()[1:-1]
            item['province'] = self.province
            item['typical'] = self.typical

            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            
            yield request
    
    def parse_detail(self, response):
        item = response.meta['item']

        item['title'] = response.xpath('//table[@class="bk_bt"]//h2/text()').get()
        re_style = re.compile('<\s*a[^>].*>[^<]*<\s*/\s*a\s*>', re.I)
        content = response.xpath('//div[@class="c_bodyDiv"]').get()
        item['content'] = re_style.sub('', content)  # 去掉a标签
        item['html_source'] = response.body

        yield item