import scrapy
from tender.items import TenderItem

class GuizhouZhongbiaoSpider(scrapy.Spider):
    name = 'guizhou_zhongbiao'
    allowed_domains = ['www.ccgp-guizhou.gov.cn']

    start_urls = ['http://www.ccgp-guizhou.gov.cn/sjbx/zbcggg/']

    province = '贵州'
    typical = '中标'

    def start_requests(self):

        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']
        for pageNum in range(next_page, max_page):
            if pageNum == 1:
                yield scrapy.Request(self.start_urls[0] + 'index.html', self.parse, dont_filter=True)
            else:
                yield scrapy.Request(self.start_urls[0] + 'index_' + str(pageNum) + '.html', self.parse,
                                     dont_filter=True)

    def parse(self, response):
        for row_data in (response.xpath('//*[@class="xnrx"]/ul/li')):
            url = response.urljoin(row_data.css('li a::attr(href)').get())
            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data.xpath('span/text()')[0].extract()
            item['province'] = self.province
            item['typical'] = self.typical
            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item

            yield request
    def parse_detail(self, response):
        item = response.meta['item']
        item['title'] = response.xpath('//h3/text()').get()
        item['content'] = response.xpath('//div[@id="border"]').get()
        item['html_source'] = response.body

        yield item
