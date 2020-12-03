# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TenderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    province = scrapy.Field()
    typical = scrapy.Field()
    publish_at = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    html_source = scrapy.Field()
    # pass
