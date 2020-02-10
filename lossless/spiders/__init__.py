# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import scrapy

class QuotesSpider(scrapy.Spider):
    name: "pages"

    def start_requests(self):
        urls = [
        'http://mylossless.3xforum.ro/topic/40/Muzica_Albume_in_format_MP3_/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'page-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
