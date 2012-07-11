#! /usb/bin/python
# http://www.ldoceonline.com/search/?q=bore

import urllib
import urllib2
from optparse import OptionParser
from BeautifulSoup import BeautifulSoup


class Ldoce(object):

    def __init__(self, word=None):
        self.urlsearch = "http://www.ldoceonline.com/search/"
        self.urllink = "http://www.ldoceonline.com"
        self.params = {}
        if word is not None:
            self.word = word
            self.params['q'] = self.word

    def showDescription(self):
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

        print entry[0].text


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-w", "--word", dest="word",
                              help="Word to find", metavar="FILE")
    (options, args) = parser.parse_args()
    if hasattr(options, 'word'):
       ldoce = Ldoce(options.word)
       ldoce.showDescription()
