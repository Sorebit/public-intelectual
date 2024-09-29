# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

from pubint.items import Topic, Comment


class MissingTopicUrl(DropItem):
    pass


class Duplicate(DropItem):
    pass


class FilterTopicsPipeline:
    def process_item(self, item, spider):
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


class FilterDuplicatesPipeline:
    """TODO"""
