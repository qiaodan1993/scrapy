import scrapy
from tender.items import TenderItem 
import re

class HebeiZhongBiaoSpider(scrapy.Spider):
    name = 'hebei_zhongbiao'

    allowed_domains = ['www.ccgp-hebei.gov.cn']
    start_urls = ['http://www.ccgp-hebei.gov.cn/province/cggg/zhbgg/']

    province = '河北'
    typical = '中标'

    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']

        for pageNum in range(next_page, max_page):
            if pageNum == 1:
                yield scrapy.Request(self.start_urls[0]+ 'index.html', self.parse, dont_filter=True)
            else:
                yield scrapy.Request(self.start_urls[0]+ 'index_' + str(pageNum-1) + '.html', self.parse, dont_filter=True)


    def parse(self, response):
        for row_data in response.xpath('//table[@id="moredingannctable"]/tr[not(@bgcolor)]'):
            url = response.urljoin(row_data.xpath('.//a[@class="a3"]/@href').get())

            item = TenderItem()
            item['url'] = url
            item['province'] = self.province
            item['typical'] = self.typical
            url = 'http://www.ccgp-hebei.gov.cn/province/cggg/zhbgg/202012/t20201225_1362376.html'
            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item

            yield request

    def parse_detail(self, response):
        item = response.meta['item']


        item['title'] = response.xpath('//table[@id="2020_VERSION"]/tr[3]/td/span/text()').get()
        item['publish_at'] = response.xpath('//table[@id="2020_VERSION"]/tr[6]/td/span/text()').get()
        re_style = re.compile('<\s*a[^>].*>[^<]*<\s*/\s*a\s*>', re.I)
        content = response.xpath('//table[@id="2020_VERSION"]/tr[7]/td/span').get()

        item['content'] = re_style.sub('', content)  # 去掉a标签
        item['html_source'] = response.body

        yield item
    

        