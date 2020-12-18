import scrapy
from tender.items import TenderItem

class SichuanZhongbiaoSpider(scrapy.Spider):
    name = 'sichuan_zhongbiao'
    allowed_domains = ['www.ccgp-sichuan.gov.cn']
    start_urls = ['http://www.ccgp-sichuan.gov.cn/CmsNewsController.do?method=recommendBulletinList&rp=25&page={page}&moreType=provincebuyBulletinMore&channelCode=jggg']

    province = '四川'
    typical = '中标'

    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']
        for pageNum in range(next_page, max_page):
            start_url = self.start_urls[0].replace('{page}', str(pageNum))
            yield scrapy.Request(start_url, self.parse, dont_filter=True)

    def parse(self, response):
        for row_data in (response.xpath('//*[@class="info"]/ul/li')):
            url = row_data.css('li a::attr(href)').get()
            item = TenderItem()
            item['url'] = url

            publish_month = row_data.xpath('div[@class="time curr"]/text()')[1].extract().strip()
            publish_day = row_data.xpath('div[@class="time curr"]/span/text()')[0].extract().strip()
            publish_at = str(publish_month) + '-' + str(publish_day)
            item['publish_at'] = publish_at

            item['province'] = self.province
            item['typical'] = self.typical

            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            yield request

    def parse_detail(self, response):
        item = response.meta['item']
        item['title'] = response.xpath('//h1/text()').get()
        item['content'] = response.xpath('//div[@id="myPrintArea"]').get()
        item['html_source'] = response.body

        yield item
