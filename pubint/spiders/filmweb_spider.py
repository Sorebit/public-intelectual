from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable, List, Callable
from urllib.parse import urlparse

import scrapy
from scrapy.http import Request, Response

from pubint.items import Topic, Comment
from pubint.item_loaders import TopicLoader


def drop_query(url) -> str:
    """Discussion URLs have page numbers located in query string"""
    return urlparse(url)._replace(query="").geturl()


def fragment(url) -> str:
    return urlparse(url).fragment


def add_netloc(url, netloc) -> str:
    """Replaces netloc. Adds https scheme, if needed"""
    u = urlparse(url)._replace(netloc=netloc)
    if not u.scheme:
        u = u._replace(scheme='https')
    return u.geturl()


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
            # ('https://www.filmweb.pl/film/Zakochana+Jane-2007-180058/discussion/McAvoy,1605383', self.parse_topic)
            # ('https://www.filmweb.pl/film/Strange+Darling-2023-10026886/discussion', self.parse_discussion),
            # ('https://www.filmweb.pl/film/Strange+Darling-2023-10026886/discussion/Nie+wiem%252C+dlaczego+nikt+tego+jeszcze+nie+zauwa%C5%BCy%C5%82...,3435035', self.parse_topic)
            # ('https://www.filmweb.pl/film/Substancja-2024-10051631/discussion/Nie+widzia%C5%82em+filmu%2C+ale+plakat...,3434212', self.parse_topic),
            ('https://www.filmweb.pl/serial/W%C5%82adca+Pier%C5%9Bcieni%3A+Pier%C5%9Bcienie+W%C5%82adzy-2022-835082/season/1/discussion/Szkoda,3282235', self.parse_topic)
        ]
        return
        if not file:
            raise ValueError(f"Expected file argument for spider {self.name}")
        self.load_start_urls(Path(file).expanduser())
        self.skip_cached = False  # TODO: cli arg

    def start_requests(self) -> Iterable[Request]:
        """Assumes beginning from discussion pages"""
        self.log(f"Total number of start URLs: {len(self.start_urls)}")
        for url, callback in self.start_urls:
            yield Request(url, dont_filter=True, callback=callback)

    def load_start_urls(self, filename: str) -> None:
        """Expects lines to be discussion URLs

        TODO: urlparse
        """
        with open(filename) as file:
            for line in file:
                url = line.strip()
                if url.startswith("/film/"):
                    url = url[6:]  # Extract film handle
                if not url.startswith("http"):
                    url = self.discussion_tmpl.format(url)
                self.log(f"Appending start URL {url}")
                self.start_urls.append((url, self.parse_discussion))

    def parse_discussion(self, response: Response):
        """parse discussion i.e. page listing topics"""
        self.log("Parse as DISCUSSION url={}".format(response.url))

        topics = response.css('div.forumTopic')
        for topic_container in topics:
            topic = TopicLoader(item=Topic(), selector=topic_container)
            topic.add_css('title', 'a.forumTopic__title::text')
            topic.add_css('url','a.forumTopic__title::attr(href)')
            item = topic.load_item()
            # yield item
            if item.get('url'):
                yield response.follow(item['url'], callback=self.parse_topic)

        next_page = response.css('.pagination__item--next a::attr(href)').extract_first()
        if next_page:
            # response.follow allows using relative links
            yield response.follow(next_page, callback=self.parse_discussion)

    def parse_topic(self, response: Response, **kwargs):
        topic_url = drop_query(response.url)  # maybe it would be better to store the query too but as a separate column
        self.log("Parse as TOPIC url={}".format(topic_url))
        comments = response.css('div.forumTopic')
        topic_title = comments.css('a.forumTopic__title::text').extract_first()
        item = Comment()  # TODO: loader
        offset = kwargs.get("offset", 0)
        for i, comment_container in enumerate(comments):
            item['topic_url'] = topic_url
            item['topic_title'] = topic_title  # reduntant by A LOT
            item['post_id'] = comment_container.attrib.get('data-id')
            item['owner'] = comment_container.attrib.get('data-owner')
            item['text_content'] = " <br> ".join(
                comment_container.css('p.forumTopic__text::text').extract()
            )  # TODO: loader?
            item['position'] = i + offset
            item['indent'] = comment_container.attrib.get('data-indent') or 0
            reply_to = comment_container.css('.forumTopic__authorReply a::attr(href)').extract_first()
            if reply_to:
                # The url also contains the query (page num), so it's convenient to store it all rather than combining
                # it from different columns (which is a violation of which Normal Form?)
                item['reply_to_url'] = add_netloc(reply_to, 'www.filmweb.pl')
                item['reply_to'] = fragment(reply_to).replace("topic_", "").replace("post_", "")
            else:
                item['reply_to_url'] = None
                item['reply_to'] = None

            yield item

        next_page = response.css('.pagination__item--next a::attr(href)').extract_first()
        if next_page:
            # response.follow allows using relative links
            yield response.follow(next_page, callback=self.parse_topic, cb_kwargs={"offset": i + offset})
