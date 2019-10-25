#!/bin/python

import sys, os, re
from configparser import ConfigParser
import appdirs
import requests as r
import npyscreen

from views import ArticleList, ArticlePicker, ArticleReader
from models import Cache

APPNAME = 'corr-cli'
AUTHOR = 'stfwn'
base_url = 'https://thecorrespondent.com/'

class CorrCli(npyscreen.NPSAppManaged):
    def onStart(self):
        self.load_config()
        self.login()
        self.session.get_article = self.get_article

        self.cache = Cache(APPNAME, AUTHOR)
        self.cache.fetch_new(self.session, APPNAME, AUTHOR)

        self.addForm('MAIN', ArticlePicker, name='Article Picker')
        self.addForm('READER', ArticleReader, name='Article Reader')

    def load_config(self):
        # Load config
        config_path = appdirs.user_config_dir(APPNAME, AUTHOR) + '/config'
        config = ConfigParser()
        config.read(config_path)
        try:
            config['thecorrespondent.com']['name']
            config['thecorrespondent.com']['email']
            config['thecorrespondent.com']['password']
        except KeyError as e:
            sys.stderr.write(f'Info not supplied in config file: {e}\n')
            sys.stderr.write(f"The config file is located here: '{config_path}'\n")
            sys.exit(1)

        self.config = config

    def login(self):
        """ Set the cookie for the session. """
        s = r.Session()

        name = self.config['thecorrespondent.com']['name']
        email = self.config['thecorrespondent.com']['email']
        password = self.config['thecorrespondent.com']['password']
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
    CorrCli = CorrCli().run()
