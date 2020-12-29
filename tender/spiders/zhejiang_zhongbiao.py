import scrapy
import json
from tender.items import TenderItem 
import time
import re
import urllib.parse as urlparse
import requests

class ZhejiangZhongBiaoSpider(scrapy.Spider):
    name = 'zhejiang_zhongbiao'
    allowed_domains = ['czt.zj.gov.cn']
    start_urls = ['https://zfcgmanager.czt.zj.gov.cn/cms/api/cors/remote/results?pageSize=15&sourceAnnouncementType=3004%2C4005%2C4006&url=notice']
    detail_url = 'https://zfcgmanager.czt.zj.gov.cn/cms/api/cors/remote/results?noticeId={noticeId}&url=noticeDetail'

    province = '浙江'
    typical = '中标'

    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']

        for pageNum in range(next_page, max_page):
            yield scrapy.Request(self.start_urls[0]+ '&pageNo=' + str(pageNum), self.parse, dont_filter=True)

    def parse(self, response):
        js = json.loads(response.body) 
        for row_data in js["articles"]:

            item = TenderItem()
            url = row_data["url"]
            url = url.replace('http', 'https')
            item['url'] = url

            timeArray = time.localtime(int(row_data["pubDate"])/1000)
            item['publish_at'] = time.strftime("%Y-%m-%d", timeArray)
            item['province'] = self.province
            item['typical'] = self.typical
            item['title'] = row_data["projectName"]

            request = scrapy.Request(item['url'], callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            
            yield request
    
    def parse_detail(self, response):
        item = response.meta['item']

        # 获取一下noticeid
        parsed = urlparse.urlparse(item['url'])
        querys = urlparse.parse_qs(parsed.query)
        noticeId = querys['noticeId'][0]
        detial_url = self.detail_url.replace('{noticeId}', noticeId)

        # 获取一下详情
        detail_info = requests.get(detial_url)
        content = (detail_info.json()['noticeContent'])

        # 去掉一些标签
        re_style = re.compile('<\s*style[^>].*>[^<]*<\s*/\s*style\s*>', re.I)
        content = re_style.sub('', content)
        re_style = re.compile('<\s*a[^>].*>[^<]*<\s*/\s*a\s*>', re.I)
        content = re_style.sub('', content)

        item['content'] = content
        item['html_source'] = response.body
        yield item