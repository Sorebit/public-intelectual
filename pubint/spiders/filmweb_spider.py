from typing import TYPE_CHECKING, Any, Iterable, List, Optional, Union, cast

import scrapy
from scrapy.http import Request, Response

from pubint.items import Topic
from pubint.item_loaders import TopicLoader


class FilmwebSpiderSpider(scrapy.Spider):
    name = "filmweb"
    allowed_domains = ["filmweb.pl"]
    start_urls = []

    def __init__(self, film: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not film:
            raise ValueError("Expected film argument for spider")
        # Uciekaj-2017-750704
        self.start_urls = [f"https://www.filmweb.pl/film/{film}/discussion"]


    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            yield Request(url, dont_filter=True)

    def parse(self, response: Response):
        """parse discussion page"""
        self.log("Default parse method for url={}".format(response.url))
        yield Request("https://www.filmweb.pl/", callback=self.parse_other)
        return

        topics = response.css('div.forumTopic')
        for topic_container in topics:
            topic = TopicLoader(item=Topic(), selector=topic_container)
            topic.add_css('title', 'a.forumTopic__title::text')
            topic.add_css('url','a.forumTopic__title::attr(href)')
            yield topic.load_item()

        next_page = response.css('.pagination__item--next a::attr(href)').extract_first()
        if next_page:
            # response.follow allows using relative links
            yield response.follow(next_page, callback=self.parse)

    def parse_other(self, response: Response):
        self.log("OTHER parse method for url={}".format(response.url))
        return
