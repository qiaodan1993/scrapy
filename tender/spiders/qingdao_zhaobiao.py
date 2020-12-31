import scrapy
import json
from tender.items import TenderItem
from scrapy_splash import SplashRequest
import re

# splash lua script
script = """
         function main(splash, args)
             assert(splash:go(args.url))
             assert(splash:wait(args.wait))
             js = string.format("document.getElementById('%s').click()",args.pageNum)
             splash:evaljs(js)
             assert(splash:wait(args.wait))
             return splash:html()
         end
         """

class QingdaoZhaobiaoSpider(scrapy.Spider):
    name = 'qingdao_zhaobiao'
    allowed_domains = ['www.qingdao.gov.cn']
    start_urls = ['http://www.ccgp-qingdao.gov.cn/sdgp2014/site/channelall370200.jsp?colcode=0401&flag=0401#']

    province = '青岛'
    typical = '招标'
    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']
        for pageNum in range(next_page, max_page):
            yield SplashRequest(self.start_urls[0], callback=self.parse,endpoint='execute',args={'lua_source': script, 'pageNum':pageNum, 'wait': 2})
    def parse(self, response):
        list = response.xpath('//div[@class="neitzbox"]')
        for row_data in list:
            url = row_data.css('div a::attr(href)').get()
            if url is None:
                continue
            url = response.urljoin(url)
            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data.xpath('div[@class="neitime"]/text()').get().strip()
            item['title'] = row_data.xpath('div[@class="neinewli"]/a/text()').get().strip()
            item['province'] = self.province
            item['typical'] = self.typical 
            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            yield request
    def parse_detail(self, response):
        item = response.meta['item']
        content = response.xpath("//div[@class='biaotq']/following-sibling::div[1]").get()
        re_style = re.compile('<\s*a[^>].*>[^<]*<\s*/\s*a\s*>', re.I)
        item['content'] = re_style.sub('', content) # 去掉a标签
        item['html_source'] = response.body
        yield item
