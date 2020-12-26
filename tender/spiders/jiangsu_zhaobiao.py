import scrapy
from tender.items import TenderItem 
import re

class JiangsuZhaoBiaoSpider(scrapy.Spider):
    name = 'jiangsu_zhaobiao'
    allowed_domains = ['www.ccgp-jiangsu.gov.cn']
    start_urls = ['http://www.ccgp-jiangsu.gov.cn/ggxx/gkzbgg/']

    province = '江苏'
    typical = '招标'

    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']

        for pageNum in range(next_page, max_page):
            if pageNum == 1:
                yield scrapy.Request(self.start_urls[0]+ 'index.html', self.parse, dont_filter=True)
            else:
                yield scrapy.Request(self.start_urls[0]+ 'index_' + str(pageNum) + '.html', self.parse, dont_filter=True)

    def parse(self, response):
        for row_data in response.xpath('//*[@id="newsList"]/ul/li'):
            url = response.urljoin(row_data.css('li a::attr(href)').get())
            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data.css('li::text').getall()[-1].split()[0]
            item['province'] = self.province
            item['typical'] = self.typical

            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item

            yield request
            # return

    def parse_detail(self, response):
        item = response.meta['item']
        item['title'] = response.xpath('//div[@class="dtit"]/h1/text()').get()

        content = response.xpath('//div[@class="content"]').get()

        re_style = re.compile('<div class="local">.*</div>', re.I)
        content = re_style.sub('', content)
        re_style = re.compile('<\s*a[^>].*>[^<]*<\s*/\s*a\s*>', re.I)
        content = re_style.sub('', content)

        item['content'] = content # 去掉a标签
        item['html_source'] = response.body
        yield item

    
