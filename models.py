import os
import json
import appdirs

class Cache():
    def __init__(self, APPNAME, AUTHOR):
        cache_path = f'{appdirs.user_cache_dir(APPNAME, AUTHOR)}/articles.json'
        self.path = cache_path
        try:
            with open(cache_path) as fp:
                articles = json.load(fp)
        except:
            articles = {}
        self.articles = articles

    def fetch_new(self, session, APPNAME, AUTHOR, persist_to_disk=True):
        try:
            next_id = int(max(self.articles.keys())) + 1
        except:
            next_id = 17

        scanning_margin = 4
        misses = 0
        while misses <= scanning_margin:
            article = session.get_article(next_id)
            if article is None:
                misses += 1
            else:
                self.articles[next_id] = article
            next_id += 1
        
        if persist_to_disk:
            cache_folder = appdirs.user_cache_dir(APPNAME, AUTHOR)
            if not os.path.exists(cache_folder):
                os.makedirs(cache_folder)
            with open(f'{cache_folder}/articles.json', 'w') as fp:
                json.dump(self.articles, fp, indent=4)

    def clear(self):
        if os.path.exists(self.path):
            os.remove(self.path)
            print('Cache cleared.')
        else:
            print('Cache was already empty.')
        self.articles = {}
