import scrapy
import json
from tender.items import TenderItem
from scrapy_splash import SplashRequest
import re

script = """
         function main(splash, args)
            assert(splash:go(args.url))
            assert(splash:wait(args.wait))
            js = string.format("document.getElementById('noticetype_3').click();document.getElementById('infoNoticeInputPage').value=%s;document.getElementsByClassName('btn btn-bg')[1].click()",args.pageNum)
            splash:evaljs(js)
            assert(splash:wait(args.wait))
            return splash:html()
         end
         """
class ShaanxiZhaobiaoSpider(scrapy.Spider):
    name = 'shaanxi_zhaobiao'
    allowed_domains = ['www.ccgp-shaanxi.gov.cn']
    start_urls = ['http://www.ccgp-shaanxi.gov.cn/notice/list.do?noticetype=3&index=3&province=province']

    province = '陕西'
    typical = '招标'
    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']
        for pageNum in range(next_page, max_page):
            yield SplashRequest(self.start_urls[0], callback=self.parse,endpoint='execute',args={'lua_source': script, 'pageNum':pageNum, 'wait': 2})
    def parse(self, response):
        list = (response.xpath('//table[@class="table table-no tab-striped tab-hover"]/tbody/tr'))
        for row_data in list:
            url = row_data.css('td a::attr(href)').get()
            if url is None:
                continue
            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data.xpath('./td[4]/text()').get().strip()
            item['title'] = row_data.xpath('./td[3]/a/text()').get().strip()
            item['province'] = self.province
            item['typical'] = self.typical  
            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            yield request 
            return 
    def parse_detail(self, response):
        item = response.meta['item']

        content = response.xpath("//div[@class='contain detail-con']").get()

        re_style = re.compile('<style>[\s\S]*</style>', re.I)
        content = re_style.sub('', content)      
        re_style = re.compile('<\s*a[^>].*>[^<]*<\s*/\s*a\s*>', re.I)
        content = re_style.sub('', content)

        item['content'] = content # 去掉a标签
        item['html_source'] = response.body
        yield item

