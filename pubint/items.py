# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Topic(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()


class Comment(scrapy.Item):
    topic_url = scrapy.Field()  # need to somehow bind comments to topic and construct a discussion
    user = scrapy.Field()
    user_url = scrapy.Field()
    # order? liczba porządkowa
    text = scrapy.Field()
    """css('p.forumTopic__text::text')"""


# pierwszy post jest na chyba każdej stronie paginacji
# .forumDiscussion__topic
#   p.forumTopic__text::text
# .forumDiscussion__replies
# paginacja taka sama
