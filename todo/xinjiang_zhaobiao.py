import scrapy
import json
from tender.items import TenderItem
from scrapy_splash import SplashRequest
import re

script = """
         function main(splash, args)
            assert(splash:go(args.url))
            assert(splash:wait(args.wait))
            js = string.format("document.getElementsByClassName('J-paginationjs-go-pagenumber')[0].value = %s;document.getElementsByClassName('J-paginationjs-go-button')[0].click()",args.pageNum)
            splash:evaljs(js)
            assert(splash:wait(args.wait))
            return splash:html()
         end
         """
class XinjiangZhaobiaoSpider(scrapy.Spider):
    name = 'xinjiang_zhaobiao'
    allowed_domains = ['www.ccgp-xinjiang.gov.cn']
    start_urls = ['http://www.ccgp-xinjiang.gov.cn/ZcyAnnouncement/ZcyAnnouncement2/index.html?districtCode=659900&utm=sites_group_front.2ef5001f.0.0.e0324310557f11eb8d975f7c715b23ee']

    province = '新疆'
    typical = '招标'
    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']
        for pageNum in range(next_page, max_page):
            yield SplashRequest(self.start_urls[0], callback=self.parse,endpoint='execute',args={'lua_source': script, 'pageNum':pageNum, 'wait': 2})
    def parse(self, response):
        list = (response.xpath('//div[@class="list-container"]/ul/li'))
        for row_data in list:
            url = row_data.css('a::attr(href)').get()
            if url is None:
                continue
            url = response.urljoin(url)
            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data.xpath('./span/text()').get().strip()
            item['title'] = ''.join(row_data.xpath('./a/text()').getall()).strip()
            item['province'] = self.province
            item['typical'] = self.typical  
            request = SplashRequest(url, callback=self.parse_detail,  args={'wait': 2})
            request.meta['item'] = item
            yield request
            return 
    def parse_detail(self, response):
        print(response.text)
        return 
        item = response.meta['item']
        content = response.xpath("//body[@class='view']").get()
        print(content)
        return 
        re_style = re.compile('<\s*a[^>].*>[^<]*<\s*/\s*a\s*>', re.I)
        item['content'] = re_style.sub('', content) # 去掉a标签
        item['html_source'] = response.body
        yield item
