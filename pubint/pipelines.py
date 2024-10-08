# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pdb
import logging
from typing import TYPE_CHECKING, Any
import sqlite3

from itemadapter import ItemAdapter
from scrapy import Spider
from scrapy.crawler import Crawler
from scrapy.exceptions import DropItem

from pubint.items import Topic, Comment
from pubint import db


class MissingTopicUrl(DropItem):
    pass


class Duplicate(DropItem):
    pass


class LoggingMixin:
    name: str

    @property
    def logger(self) -> logging.LoggerAdapter:
        logger = logging.getLogger(self.name)
        return logging.LoggerAdapter(logger, {})

    def log(self, message: Any, level: int = logging.DEBUG, **kw: Any) -> None:
        self.logger.log(level, message, **kw)


class FilterTopicsPipeline:
    def process_item(self, item, spider: Spider):
        adapter = ItemAdapter(item)
        match item:
            case Topic():
                if adapter.get("url") is None:
                    raise MissingTopicUrl(f"Missing URL in topic {item}")
            case Comment():
                pass
            case _:
                pass
        return item


def dict_factory(cursor, row):
    """TODO: I think this is the place to plug in pydantic"""
    fields = [column[0] for column in cursor.description]
    return {k: v for k, v in zip(fields, row)}


class SqlitePipeline(LoggingMixin):
    def __init__(self, db_uri):
        self.db_uri = db_uri
        self.name = self.__class__.__name__
        self._cursor = None

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        return cls(
            crawler.settings.get("SQLITE_URI", "filmweb.db"),
        )

    def open_spider(self, spider: Spider):
        self.log(f"Connecting to {self.db_uri}")
        self.connection = sqlite3.connect(self.db_uri, uri=True)
        self.connection.row_factory = dict_factory
        self.create_tables()

    def close_spider(self, spider: Spider):
        self.log(f"Closing connection to {self.db_uri}")
        self.connection.commit()
        self.connection.close()

    def process_item(self, item, spider: Spider):
        try:
            self.save(item)
        except sqlite3.IntegrityError as exc:
            if exc.sqlite_errorname == 'SQLITE_CONSTRAINT_PRIMARYKEY':
                # Rozkmina jest taka, że chciałbym się dowiedzieć czy post_id jest unikalne w obrębie całego filmwebu
                # czy jakoś bardziej zawężone
                # ale może bez sensu tak robić i lepiej zapisywać handle filmu i unique na parze
                raise Duplicate
            pdb.set_trace()
        except sqlite3.DatabaseError as exc:
            pdb.set_trace()
        return item

    def save(self, item):
        # stmt = "INSERT OR REPLACE"  # TODO: switch as arg?
        stmt = "INSERT"
        stmt += """
            INTO comment(post_id, topic_url, text_content,owner, position, indent, reply_to)
            VALUES (:post_id, :topic_url, :text_content, :owner, :position, :indent, :reply_to)
        """
        self.cursor.execute(
            stmt,
            {
                "post_id": item.get("post_id"),
                "topic_url": item.get("topic_url"),
                "text_content": item.get("text_content"),
                "owner": item.get("owner"),
                "position": item.get("position"),
                "indent": item.get("indent"),
                "reply_to": item.get("reply_to"),
            }
        )

    def create_tables(self):
        """This may be a worse idea than manually executing schema sql (migration)"""
        res = self.cursor.execute("SELECT name from sqlite_schema")
        names = [row["name"] for row in res.fetchall()]
        if "comment" not in names:
            self.log(db.schema)
            self.cursor.execute(db.schema)
        self.connection.commit()

    @property
    def cursor(self):
        if self._cursor is None:
            self._cursor = self.connection.cursor()
        return self._cursor
