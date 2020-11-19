import scrapy


class CcgpJiangSuSpider(scrapy.Spider):
    name = 'info'
    start_urls = [
        'http://www.ccgp-jiangsu.gov.cn/ggxx/gkzbgg/',
    ]

    def parse(self, response):
        for quote in response.css('ul').extract():
            yield {
                'link': quote.css('li::attr("href")').extract_first(),
                'title': quote.css('li a::text').extract_first(),
                'text': quote.css('li::text').extract_first(),
            }

        next_page = response.css('li.next a::attr("href")').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)


# if __name__ == '__main__':
    # CcgpJiangSuSpider().parse()