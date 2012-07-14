#!/usr/bin/python
# http://www.ldoceonline.com/search/?q=bore

import urllib
import urllib2
from optparse import OptionParser
from BeautifulSoup import BeautifulSoup

#from django.template import Template, Context
#from django.conf import settings
#settings.configure()
from django.template.loader import render_to_string
from django.conf import settings
settings.configure()
settings.TEMPLATE_DIRS = (".",)

class Ldoce(object):

    def __init__(self, word=None, is_short=False, tag=''):
        self.urlsearch = "http://www.ldoceonline.com/search/"
        self.urllink = "http://www.ldoceonline.com"
        self.data = {}
        self.params = {}
        self.soup = None
        self.rendered = None
        self.is_short = is_short
        if word is not None:
            self.word = word 
            self.tag = tag 
            self.params['q'] = self.word

    def find(self, selector):
        result = self.soup.findAll('',selector)
        if result != []:
            return [i.text for i in result]

        return ['']

    def showDescription(self):
        soup = self.choiseDescription()
        self.soup = soup[0]
        self.data = {
                'head': {
                    'word': self.find({'class':'HWD'})[0],
                    'homographsSelected': self.find({'class':'homographsSelected'})[0],
                    'POS': self.find({'class':'POS'})[0],
                    },
                'tag':self.tag,
                'body': {
                    'DEF': self.find({'class':'DEF'})[0],
                    'EXAMPLE': self.find({'class':'EXAMPLE'}),
                    }
                }
        self.rendered = render_to_string('./template.anki', self.data)

    def choiseDescription(self):
        req = urllib2.Request(self.urlsearch, urllib.urlencode(self.params))
        htmlSource = urllib2.urlopen(req).read()
        soup = BeautifulSoup(htmlSource)
        choice = 1
        entry = soup.findAll('div', {'class':'Entry'})
        while entry == [] and choice != 0:
            words = soup.findAll('td',{'class':'hwdunSelMM'})
            rangeWords = range(1,len(words)+1)
            for i in rangeWords:
                print i, words[i-1].text
            choice = int(raw_input("Select description: "))
            if choice not in rangeWords: choice=0
            else:
                req = urllib2.Request(self.urllink + words[choice-1].find('a').get('href'))
                htmlSource = urllib2.urlopen(req).read()
                soup = BeautifulSoup(htmlSource)
                entry = soup.findAll('div', {'class':'Entry'})

        if self.is_short:
            entry = self.choiseSense(BeautifulSoup(str(entry)))
        
        return entry

    def choiseSense(self, soup):
        choice = 1
        words = soup.findAll('div',{'class':'Sense'})
        while len(words) > 1 and choice != 0:
            rangeWords = range(1,len(words)+1)
            for i in rangeWords:
                print i, words[i-1].text
            choice = int(raw_input("Select sense: "))
            if choice in rangeWords: 
                soup.findAll('div', {'class':'Sense'})[choice-1]['id'] = 'markedSense' 
                [i.extract() for i in words if i['id'] != 'markedSense']
                break

        return soup.findAll('div', {'class':'Entry'})


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-w", "--word", dest="word",
                              help="Word to find")
    parser.add_option("-W", "--words", dest="words",
                              help="Words from file")
    parser.add_option("-s", "--short", dest="is_short", action="store_true", default=False,
                              help="Make short description")
    parser.add_option("-t", "--tag", dest="tag", default='',
                              help="Set tag")
    (options, args) = parser.parse_args()

    if options.word is not None:
        ldoce = Ldoce(options.word, is_short=options.is_short, tag=options.tag)
        ldoce.showDescription()
        print ldoce.rendered

    if options.words is not None:
        ldoces = []
        f = open(options.words)
        words = [i[:-1] for i in f]
        f.close()
        for i in words:
            ldoce = Ldoce(i, is_short=options.is_short, tag=options.tag)
            ldoce.showDescription()
            ldoces.append(ldoce)
        f = open(options.words+'.results', 'w')
        for i in ldoces:
             f.write(i.rendered)
        f.close()
