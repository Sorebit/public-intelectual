# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Topic(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()


class Comment(scrapy.Item):
    """
    to jest niby niepotrzebne, bo mamy po prosty div.forumTopic
    topics = response.css('div.forumTopic')
    for topic in topics:
        topic.attrib -> {'id': 'post_5154360', 'class': 'forumTopic', 'data-id': '5154360', 'data-owner': 'Mril24', 'data-indent': '1'}
    """
    post_id = scrapy.Field()
    topic_url = scrapy.Field()  # need to somehow bind comments to topic and construct a discussion
    text_content = scrapy.Field()
    owner = scrapy.Field()
    position = scrapy.Field()
    indent = scrapy.Field()  # na razie zapisujemy indent i kolejność, to może wsm wystarczyć do oglądania i analizowania
    reply_to = scrapy.Field()

# pierwszy post jest na chyba każdej stronie paginacji

#
# paginacja taka sama
# posty mają ID, które można po prostu dopisać po hashu żeby mieć pełny link
# post_5154360 -> https://www.filmweb.pl/film/Zakochana+Jane-2007-180058/discussion/Wisley+naprawde+kochal+Jane.,1131471#post_5154360
# ale na razie mi to niepotrzebne

# powiedzmy że szukamy KotArystokrata
# /user/KotArystokrata
