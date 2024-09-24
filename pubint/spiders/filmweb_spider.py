import scrapy


class FilmwebSpiderSpider(scrapy.Spider):
    name = "filmweb_spider"
    allowed_domains = ["filmweb.pl"]
    start_urls = ["https://filmweb.pl"]

    def parse(self, response):
        pass
