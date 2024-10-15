# https://docs.scrapy.org/en/latest/topics/loaders.html

from urllib.parse import urlparse

from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst


def prepend_domain(url: str) -> str:
    """Pewnie urllib zamiast taki +"""
    return "https://filmweb.pl" + url


class TopicLoader(ItemLoader):
    default_output_processor = TakeFirst()
    url_in = MapCompose(prepend_domain)


class CommentLoader(ItemLoader):
    default_output_processor = TakeFirst()
    # item['user_url'] = comment_container.css('.forumTopic__authorName a::attr(href)').extract()
