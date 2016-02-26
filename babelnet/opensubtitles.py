import urllib2
import sys
from bs4 import BeautifulSoup

def getMovieName(docId):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    url = "http://www.opensubtitles.org/en/subtitles/{0}".format(docId)

    headers={'User-Agent':user_agent,} 

    req = urllib2.Request(url, headers=headers)

    try:
        page = urllib2.urlopen(req)
        
        content = page.read()
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.find('span', {'itemprop': 'name'}).text
        return text[:text.rfind('subtitles')-1]
    
    except urllib2.HTTPError, e:
        print e.fp.read()
        return 'no name found'
    except:
        print "Unexpected error:", sys.exc_info()[0]
        return 'no name found for id ', docId

def parseGroup(text):
    line = BeautifulSoup(text, "lxml")
    fst = line.html.body.linkgrp['fromdoc']
    snd = line.linkgrp['todoc']

    return fst, snd 

def getAllMovieNames(path, filename ):

    with open('{0}/{1}'.format(path, filename)) as f:
        for line in f:
            if line.startswith('<linkGrp'):
                fromDoc, toDoc = parseGroup(line)
                movieId = fromDoc[fromDoc.rfind('/')+1:fromDoc.find('.xml.gz')]
                movie_name = getMovieName(movieId)

                yield (movie_name, fromDoc, toDoc)


if __name__ == '__main__':
#    print getMovieName(2099)
    for name in getAllMovieNames('/home/data/', 'en-pl.xml'):
        print name
