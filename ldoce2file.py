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

    def __init__(self, word=None, is_short=False, tag='', sense=None, defenition=None):
        self.urlsearch = "http://www.ldoceonline.com/search/"
        self.urllink = "http://www.ldoceonline.com"
        self.data = {}
        self.sense = sense
        self.entry = None
        self.entry_senses = None
        self.defenition = defenition
        self.params = {}
        self.soup = None
        self.rendered = None
        self.is_short = is_short
        if word is not None:
            self.word = word 
            self.tag = tag 
            self.params['q'] = self.word

    def find(self, selector):
        result = self.entry.findAll('',selector)
        return self._to_text(result)

    def _to_text(self, result):
        if result != []:
            return [i.text for i in result]
        return ['']

    def head(self):
        return {'word': self.find({'class':'HWD'})[0],
                'homographsSelected': self.find({'class':'homographsSelected'})[0],
                'POS': self.find({'class':'POS'})[0],
                }

    def senses(self):
        return [
                { 'DEF': self._to_text(i.findAll('',{'class':'DEF'}))[0],
                  'EXAMPLE': self._to_text(i.findAll('',{'class':'EXAMPLE'}))}
                for i in self.entry_senses
                ]


    def showDescription(self):
        self.choiseDescription()
        if self.is_short:
            self.choiseSense()
        self.data = {
                'head': self.head(),
                'tag':  self.tag,
                'senses': self.senses()                }
        self.rendered = render_to_string('./template.anki', self.data)

    def choiseDescription(self):
        req = urllib2.Request(self.urlsearch, urllib.urlencode(self.params))
        htmlSource = urllib2.urlopen(req).read()
        soup = BeautifulSoup(htmlSource)
        choice = self.defenition
        entry = soup.findAll('div', {'class':'Entry'})
        while entry == [] and choice != 0:
            words = soup.findAll('td',{'class':'hwdunSelMM'})
            rangeWords = range(1,len(words)+1)
            if choice is None:
                for i in rangeWords:
                    print i, words[i-1].text
                choice = int(raw_input("Select description: "))
            choice = int(choice)
            if choice not in rangeWords: 
                choice=0
            else:
                req = urllib2.Request(self.urllink + words[choice-1].find('a').get('href'))
                htmlSource = urllib2.urlopen(req).read()
                soup = BeautifulSoup(htmlSource)
                entry = soup.findAll('div', {'class':'Entry'})

        self.entry = BeautifulSoup(str(entry))

    def choiseSense(self):
        choice = self.sense
        words = self.entry.findAll('div',{'class':'Sense'})
        while len(words) > 1 and choice != 0:
            rangeWords = range(1,len(words)+1)
            if choice is None:
                for i in rangeWords:
                    print i, words[i-1].text
                choice = raw_input("Select sense(s)(separeate ','): ")
            try:
                choice = [int(i) for i in choice.split(',')]
            except:
                choice = [int(choice)]
            choice = [i for i in choice if i in rangeWords]
            if choice: 
                for i in choice:
                    self.entry.findAll('div', {'class':'Sense'})[i-1]['id'] = 'markedSense' 
                [i.extract() for i in words if i['id'] != 'markedSense']
                break
            else: choice = None
        self.entry_senses = [BeautifulSoup(str(i)) for i in self.entry.findAll('div', {'class':'Sense'})]



if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-w", "--word", dest="word",
                              help="Word to find")
    parser.add_option("-W", "--words", dest="words",
                              help="Words from file")
    parser.add_option("-s", "--short", dest="is_short", action="store_true", default=False,
                              help="Make short description")
    parser.add_option("-S", "--sense", dest="sense", default=None,
                              help="Select sense")
    parser.add_option("-D", "--defenition", dest="defenition", default=None,
                              help="Select defenition")
    parser.add_option("-t", "--tag", dest="tag", default='',
                              help="Set tag")
    (options, args) = parser.parse_args()

    if options.word is not None:
        ldoce = Ldoce(
                options.word, 
                is_short   = options.is_short, 
                tag        = options.tag, 
                sense      = options.sense,
                defenition = options.defenition,
                )
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
