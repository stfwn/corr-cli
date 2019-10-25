import sys
import npyscreen

class ArticleList(npyscreen.MultiLineAction):
    def display_value(self, article):
        return f"{article['id']}\t\t{article['title']}"

    def h_exit_escape(self, _input):
        self.parent.parentApp.switchForm(None)

    def actionHighlighted(self, article, keypress):
        self.parent.parentApp.getForm('READER').value = article
        self.parent.parentApp.switchForm('READER')

class ArticlePicker(npyscreen.FormMutt):
    MAIN_WIDGET_CLASS = ArticleList

    def beforeEditing(self):
        self.wStatus1.value = 'Corr-CLI'
        self.wStatus2.value = 'Select an article or press \'l\' to search.'
        self.update_list()

    def update_list(self):
        self.wMain.values = list(self.parentApp.cache.articles.values())[::-1]
        self.wMain.display()

class ArticleText(npyscreen.Pager):
    def h_exit_escape(self, _input):
        self.parent.parentApp.switchForm('MAIN')


class ArticleReader(npyscreen.FormMutt):
    MAIN_WIDGET_CLASS = ArticleText

    def beforeEditing(self):
        self.wStatus1.value = self.value['title']
        self.wMain.autowrap = True
        self.wMain.max_width = 80
        self.wMain.values = self.value['text'].split('\n')
        self.wStatus2.value = 'Use the arrows to scroll or escape to return.'
        self.wMain.display()
