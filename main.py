#!/bin/python

import sys, os, re
from configparser import ConfigParser
from argparse import ArgumentParser
import appdirs
import requests as r
import npyscreen

from views import ArticleList, ArticlePicker, ArticleReader
from models import Cache

APPNAME = 'corr-cli'
AUTHOR = 'stfwn'
base_url = 'https://thecorrespondent.com/'

class CorrCli(npyscreen.NPSAppManaged):
    def __init__(self, config):
        super(CorrCli, self).__init__()
        self.config = config

    def onStart(self):
        if not self.config['offline_mode']:
            self.login()
            self.session.get_article = self.get_article

        self.cache = Cache(APPNAME, AUTHOR)
        if self.config['clear_cache']:
            self.cache.clear()

        if not self.config['offline_mode']:
            self.cache.fetch_new(self.session, APPNAME, AUTHOR)

        if self.config['update_only']:
            sys.exit(0)

        self.addForm('MAIN', ArticlePicker, name='Article Picker')
        self.addForm('READER', ArticleReader, name='Article Reader')

    def login(self):
        """ Set the cookie for the session. """
        s = r.Session()

        name = self.config['name']
        email = self.config['email']
        password = self.config['password']
        try:
            page = s.post(base_url + 'api2/account/password-authenticate',
                    data={'emailAddress': email, 'password': password}).text
            if name not in page:
                raise KeyError('name')
        except KeyError as e:
            sys.stderr.write('Login failed.\n'
                            'Is there a typo in the config file?\n')
            sys.exit(1)
        self.session = s

    def get_article(self, article_id):
        response = self.session.get(base_url + str(article_id))
        if response.status_code == 404:
            return None

        article_page = response.text

        html_cruft = re.compile('<h1.*[\t\n]*(?P<title>[A-Z\u201c].*)[\n\t]*</h1>')
        article_title = re.search('<h1.*</h1>', article_page, re.DOTALL)[0]
        article_title = re.sub(html_cruft, '\g<title>', article_title, re.DOTALL)

        html_cruft = re.compile(' ?</?p> ?')
        article_text = [re.sub(html_cruft, '\n', x) for x in re.findall('<p>.*</p>', article_page)]
        article_text = '\n'.join(article_text).replace('\n\n\n', '\n\n')[1:]
        article = {
                'id': article_id,
                'title': article_title,
                'text': article_text}
        return article


if __name__ == '__main__':
        # Load config from config file
        config_path = appdirs.user_config_dir(APPNAME, AUTHOR) + '/config'
        config = ConfigParser()
        config.read(config_path)
        config = config['thecorrespondent.com']
        try:
            config['name']
            config['email']
            config['password']
        except KeyError as e:
            sys.stderr.write(f'Info not supplied in config file: {e}\n')
            sys.stderr.write(f"The config file is located here: '{config_path}'\n")
            sys.exit(1)

        config = dict(config)

        # Parse command-line args
        argparser = ArgumentParser(description='A CLI reader for https://www.thecorrespondent.com')
        argparser.add_argument('-o', '--offline-mode', action='store_true',
                dest='offline_mode', help='enable offline mode')
        argparser.add_argument('-c', '--clear-cache', action='store_true',
                dest='clear_cache', help='clear the articles cache and refetch')
        argparser.add_argument('-u', '--update-only', action='store_true',
                dest='update_only', help='update the cache and exit')

        args = argparser.parse_args()
        
        # Handle conflicts
        if args.offline_mode and args.update_only:
            sys.stderr.write('Conflicting arguments: '
                    'fetching articles is not possible in offline mode.\n')
            sys.exit(1)

        # Merge config file and command-line arguments (latter has precedence)
        for attr in dir(args):
            if attr[0] != '_':
                config[attr] = getattr(args, attr)

        CorrCli = CorrCli(config).run()
