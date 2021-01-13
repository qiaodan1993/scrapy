import scrapy
from tender.items import TenderItem 
import re


class JiangxiZhongbiaoSpider(scrapy.Spider):
    name = 'jiangxi_zhongbiao'
    allowed_domains = ['www.ccgp-jiangxi.gov.cn']
    start_urls = ['http://www.ccgp-jiangxi.gov.cn/web/jyxx/002006/002006004/']

    province = '江西'
    typical = '中标'

    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']
        for pageNum in range(next_page, max_page):
            yield scrapy.Request(self.start_urls[0] + str(pageNum) + '.html', self.parse, dont_filter=True)


    def parse(self, response):
        for row_data in response.xpath('//div[@class="ewb-infolist"]/ul/li'):
            url = response.urljoin(row_data.xpath('./a[@class="ewb-list-name"]/@href').get())
            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data.xpath('./span[@class="ewb-list-date"]/text()').get()
            title_list = row_data.xpath('./a[@class="ewb-list-name"]/text()').getall()
            item['title'] = "".join(title_list)
            item['province'] = self.province
            item['typical'] = self.typical
            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            yield request

    def parse_detail(self, response):
        item = response.meta['item']

        content = response.xpath('//div[@class="article-info"]').get()
        re_style = re.compile('<\s*a[^>].*>[^<]*<\s*/\s*a\s*>', re.I)
        content = re_style.sub('', content)
        re_style = re.compile('<\s*style[^>]*>[^<][\s\S]*<\s*/\s*style\s*>', re.I)
        content = re_style.sub('', content)
        item['content'] = re_style.sub('', content) # 去掉a标签
        item['html_source'] = response.body

        yield item
