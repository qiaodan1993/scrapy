import scrapy
from tender.items import TenderItem
import re

class HenanZhongbiaoSpider(scrapy.Spider):
    name = 'henan_zhongbiao'
    allowed_domains = ['www.ccgp-henan.gov.cn']
    start_urls = ['http://www.ccgp-henan.gov.cn/henan/list2?channelCode=0102&pageNo={pageNo}&pageSize=16&bz=1&gglb=10&gglx=0']

    province = '河南'
    typical = '中标'

    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']
        for pageNum in range(next_page, max_page):
            start_url = self.start_urls[0].replace('{pageNo}', str(pageNum))
            yield scrapy.Request(start_url, self.parse, dont_filter=True)

    def parse(self, response):
        for row_data in (response.xpath('//div[@class="List2"]/ul/li')):
            url = response.urljoin(row_data.css('li a::attr(href)').get())
            item = TenderItem()
            item['url'] = url
            publish_at = row_data.xpath('p/span[@class="Gray Right"]/text()')[0].extract().split()[0]
            item['publish_at'] = publish_at
            item['province'] = self.province
            item['typical'] = self.typical
            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            yield request

    def parse_detail(self, response):
        item = response.meta['item']
        item['title'] = response.xpath('//h1/text()').get()

        # 通过js 获取一下详情地址
        pattern = re.compile('get\(\"(.*)\", function', re.I)
        search_bbj = re.search(pattern, response.text)
        url = response.urljoin(search_bbj.group(1))
        request = scrapy.Request(url, callback=self.parse_detail_api, dont_filter=True)
        request.meta['item'] = item

        yield request

    def parse_detail_api(self, response):
        item = response.meta['item']
        content = response.xpath('//body').get()
        re_style = re.compile('<\s*a[^>].*>[^<]*<\s*/\s*a\s*>', re.I)
        item['content'] = re_style.sub('', content)  # 去掉a标签
        item['html_source'] = response.body
        yield item
