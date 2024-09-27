from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable, List, Callable

import scrapy
from scrapy.http import Request, Response

from pubint.items import Topic, Comment
from pubint.item_loaders import TopicLoader


class FilmwebSpiderSpider(scrapy.Spider):
    name = "filmweb"
    allowed_domains = ["filmweb.pl"]
    start_urls: tuple[str, Callable] = []
    """(url, callback)"""
    discussion_tmpl = "https://www.filmweb.pl/film/{}/discussion"
    user_tmpl = "https://www.filmweb.pl/user/{}"

    def __init__(self, file: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [
            # ('https://www.filmweb.pl/film/Zakochana+Jane-2007-180058/discussion/Wisley+naprawde+kochal+Jane.,1131471', self.parse_topic)
            # ('https://www.filmweb.pl/film/Zakochana+Jane-2007-180058/discussion/Prawdziwsza+historia+mi%C5%82o%C5%9Bci+Jane+i+Toma,3114224', self.parse_topic)
            ('https://www.filmweb.pl/film/Zakochana+Jane-2007-180058/discussion/McAvoy,1605383', self.parse_topic)
        ]
        return
        if not file:
            raise ValueError(f"Expected file argument for spider {self.name}")
        self.load_start_urls(Path(file).expanduser())

    def load_start_urls(self, filename: str) -> None:
        """Expects lines to be discussion URLs"""
        with open(filename) as file:
            for line in file:
                url = line.strip()
                if url.startswith("/film/"):
                    url = url[6:]  # Extract film handle
                if not url.startswith("http"):
                    url = self.discussion_tmpl.format(url)
                self.log(f"Appending start URL {url}")
                self.start_urls.append((url, self.parse_discussion))

    def start_requests(self) -> Iterable[Request]:
        """Assumes beginning from discussion pages"""
        self.log(f"Total number of start URLs: {len(self.start_urls)}")
        for url, callback in self.start_urls:
            yield Request(url, dont_filter=True, callback=callback)

    def parse_discussion(self, response: Response):
        """parse discussion i.e. page listing topics"""
        self.log("Parse as DISCUSSION url={}".format(response.url))
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
            yield response.follow(next_page, callback=self.parse_discussion)

    def parse_topic(self, response: Response):
        self.log("Parse as TOPIC url={}".format(response.url))
        comments = response.css('div.forumTopic')
        item = Comment()  # TODO: loader
        for i, comment_container in enumerate(comments):
            item['topic_url'] = response.url
            item['owner'] = comment_container.attrib.get('data-owner')
            item['text'] = comment_container.css('p.forumTopic__text::text').extract()
            item['indent'] = comment_container.attrib.get('data-indent')
            item['post_id'] = comment_container.attrib.get('data-id')
            item['order'] = i
            item['reply_to'] = comment_container.css('.forumTopic__authorReply a::attr(href)').extract_first()

            yield item

        next_page = response.css('.pagination__item--next a::attr(href)').extract_first()
        if next_page:
            # response.follow allows using relative links
            yield response.follow(next_page, callback=self.parse_topic)
