import scrapy

from pubint.items import Topic
from pubint.item_loaders import TopicLoader


class FilmwebSpiderSpider(scrapy.Spider):
    name = "filmweb_spider"
    allowed_domains = ["filmweb.pl"]
    # start_urls = ["https://filmweb.pl"]
    start_urls = ["https://www.filmweb.pl/film/Uciekaj-2017-750704/discussion"]

    def parse(self, response):
        """parse discussion page"""
        topics = response.css('div.forumTopic')
        for topic_container in topics:
            topic = TopicLoader(item=Topic(), selector=topic_container)
            topic.add_css('title', 'a.forumTopic__title::text')
            topic.add_css('url','a.forumTopic__title::attr(href)')
            yield topic.load_item()

        next_page = response.css('.pagination__item--next a::attr(href)').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
