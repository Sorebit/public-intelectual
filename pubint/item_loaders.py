# https://docs.scrapy.org/en/latest/topics/loaders.html

from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst


class TopicLoader(ItemLoader):
    default_output_processor = TakeFirst()
    url_in = MapCompose(lambda url: "https://filmweb.pl" + url)  # Pewnie urllib zamiast taki +
