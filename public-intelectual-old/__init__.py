""""""
import json
import requests
import pydantic

from .config import HEADERS


class Cache:
    def __call__(self):
        pass

cache = Cache()


class FilmHandle(str):
    FILM_HANDLE = '{}-{}-{}'
    
    def __str__(self):
        return FILM_HANDLE.format(self.title, self.year, self.id_)

    def __init__(self, title, year, id_) -> FilmHandle:
        self.title, self.year, self.id_ = title, year, id_



class Film:
    """aggregates comments"""

    handle: FilmHandle
    
    def discusions(self) -> list[Topic]:
        """This should be an iterable and doesnt concern itself with where the items come from"""
        

class Topic:
    url: str
    comments: Tree[Comment]
    
    TOPIC = 'https://www.filmweb.pl/film/{}/discussion'
    TOPIC_PAGE_N = 'https://www.filmweb.pl/film/{}/discussion?plusMinus=true&page={}'
    
    def __init__(self, handle):
        self.handle = handle
        self.url = make_topic_url()
    
    def make_topic_url(self, n=1) -> str:
        """n - pagination"""  
        return TOPIC_PAGE_N.format(self.handle, n)


class DiscussionPage:
    comments: Iterable[Comment]
    
    @classmethod
    def make_url(cls, film_handle, thread_handle) -> str:
        DISC_PAGE = 'https://www.filmweb.pl/film/{}/discussion/{}'
        return DISC_PAGE.format(film_handle, thread_handle)


class Comment:
    """Basically text at this point. Raw no HTML"""
    url: str
    text: str




def cache(mode):
    path = '/tmp/out.html'
    
    with open(self.path, 'w') as out_file:
        yield out_file


def scrap_topic(topic_handle):
    print(f'TOPIC handle = {topic_handle}')
    print(f'GET {topic_url}')
    response = requests.get(topic_url)
    print(response.status_code)

    if response.status_code != 200:
        raise ValueError(response)
    
    out_stream = response  #.?
    
    with cache('w') as out_stream:
        print(f'Writing text content to {path}')    
        return out_stream.write(response.text)
    
    

def scrap(film_handle: FilmHandle, pages: list):
    
    for page in pages:
        print(f'Scrap {film_handle} @ {page}')
        discussion_url = make_discussion_url(handle=film_handle, n=page)
        print(f'Discussion ({page}) URL = {discussion_url}')

    thread_url = DiscussionPage.make_url(film_handle, thread_handle)

    # WE NEED TO EXTRACT ALL TOPICS FROM THIS DISCUSSION PAGE

    for topic_handle in discussion:
        # iterujemy po topicach
        scrap_topic(topic_handle)
        
    print('Done')


# div .page__container  ->> forumSection__listContainer ->> forumSection__list1

# pagination__item pagination__item--prev 
# X razy pagination__item  
# pagination__item pagination__item--next 
# jak nie ma --next to koniec

film_handle = make_film_handle('Uciekaj', '2017', '750704')
topic_handle = 'To+jest+thriller+nie+horror,2890869'
scrap(film_handle, range(1, 4))




# 1 osoba
#   jej dorobek składa się z N  komentarzy
#   uczestniczy w co najwyżej (<=)  N  wątków (topic)
#   w co najwyżej  N  filmów
