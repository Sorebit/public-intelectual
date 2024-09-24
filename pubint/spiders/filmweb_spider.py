from typing import TYPE_CHECKING, Any, Iterable, List, Optional, Union, cast

import scrapy
from scrapy.http import Request, Response

from pubint.items import Topic
from pubint.item_loaders import TopicLoader


class FilmwebSpiderSpider(scrapy.Spider):
    name = "filmweb"
    allowed_domains = ["filmweb.pl"]
    start_urls = []

    def __init__(self, user: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not user:
            raise ValueError("Expected user argument for spider")
        # Uciekaj-2017-750704
        self.start_urls = [
            # f"https://www.filmweb.pl/film/{film}/discussion",
            f"https://www.filmweb.pl/user/{user}#/votes/film",
        ]


    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            yield Request(url, dont_filter=True, callback=self.parse_user)

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

    def parse_user(self, response: Response):
        first_batch = [url for url in response.css('a::attr(href)').extract() if url.startswith('/film/')]
        for url in sorted(first_batch):
            if url.endswith("/vod"):
                url = url[:-4]
            self.log(url)



"""Czyli problem jest aktualnie taki, że zapytanie w stylu https://www.filmweb.pl/user/kira_chan_123411#/votes/film
Gdzie ta część po hashu nie jest zbyt istotna zwraca duużo za mało danych
No ale zawsze coś
W każdym razie dobrze by było z tego wyciągnąć te handle
Bo czasem jest vod na przykład
No i seriale są w oddzielnych zakładkach w sensie /serial/{handle}
Wygląda to tak, jakby się w trakcie scrollowania doładowywały a z requestem przychodził pierwszy batch
Co jest problematyczne

/film/Aftermath.+Most+w+ogniu-2024-10059684
/film/Akademia+Magii-2024-10054493
/film/Anatomia+upadku-2023-10032723/vod
/film/Bangkok+Breaking%3A+Mi%C4%99dzy+niebem+a+piek%C5%82em-2024-10059907
/film/Batman-2022-626318/vod
/film/Bokser-2024-10017699/vod
/film/Brzydcy-2024-375638/vod
/film/Dzikie+serce-2023-10040621
/film/Fernando-2017-718863
/film/Gotowi+na+wszystko.+Exterminator-2017-787951
/film/Gra+o+wszystko-2017-774747
/film/Historia+braci+Menendez%C3%B3w-2024-10061408
/film/I+tak+ci%C4%99+kocham-2017-781068
/film/Id%C5%BA+pod+pr%C4%85d-2024-10056847
/film/Jego+trzy+c%C3%B3rki-2023-10041439/vod
/film/Joker%3A+Folie+%C3%A0+deux-2024-10014539
/film/Kliczko%3A+wi%C4%99cej+ni%C5%BC+walka-2024-10055295
/film/Las-2024-10049220
/film/M+jak+morderca-2017-787686
/film/Marcello+Mio-2024-10040722
/film/Miasteczko+Salem-2024-10001584
/film/Naznaczony%3A+Ostatni+klucz-2018-751893
/film/Nie+obiecujcie+sobie+zbyt+wiele+po+ko%C5%84cu+%C5%9Bwiata-2023-10038751
/film/Party-2017-777179
/film/Platforma+2-2024-10052749
/film/Pogromcy+duch%C3%B3w%3A+Imperium+lodu-2024-10043538/vod
/film/Prawdziwy+d%C5%BCentelmen-2024-10059904
/film/Pszczelarz-2024-10042333/vod
/film/Reagan-2024-630439
/film/Rebel+Ridge-2024-10057562/vod
/film/Rez+Ball-2024-10058502
/film/Rozwodnicy-2024-10031660
/film/Rzeczy+niezb%C4%99dne-2024-10055769
/film/Smok+Diplodok-2024-761330
/film/Sok+z+%C5%BCuka-1988-9641/vod
/film/Studni%C3%B3wk%40-2018-648728
/film/Wiecz%C3%B3r+kawalerski-2024-10024233/vod
/film/Wszech%C5%9Bwiat+Oliviera-2022-10022572


Okej to nawet nie jest pierwszy batch tylko kurczę jakieś popularne teraz filmy. Eh
"""
