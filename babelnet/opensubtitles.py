import urllib2
import sys
import logging
import logging.config
from bs4 import BeautifulSoup

def getMovieName(docId):

    logger = logging.getLogger(__name__)

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
        content = e.pf.read()
        soup = BeautifulSoup(content, 'html.parser')         
        logger.error("Unexpected error: %s", sys.exc_info()[0])
        return 'no name found: {0} for id {1}'.format(soup.title.string, docId)
    except:
        logger.error("Unexpected error: %s", sys.exc_info()[0])
        return 'no name found for id: {0}'.format(docId)

def parseGroup(text):
    line = BeautifulSoup(text, "lxml")
    fst = line.html.body.linkgrp['fromdoc']
    snd = line.linkgrp['todoc']

    return fst, snd 

def getAllMovieNames(path, filename):

    with open('{0}/{1}'.format(path, filename)) as f:
        for line in f:
            if line.startswith('<linkGrp'):
                from_doc, to_doc = parseGroup(line)
                movie_id = from_doc[from_doc.rfind('/')+1:from_doc.find('.xml.gz')]
                movie_name = getMovieName(movie_id)

                yield (movie_id, movie_name, from_doc, to_doc)


if __name__ == '__main__':
    
    logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
    with open('movies.txt', 'w') as f:
        for movie_id, movie_name, from_doc, to_doc  in getAllMovieNames('/home/data/', 'en-pl.xml'):
            f.write(";".join([movie_id, movie_name, from_doc, to_doc,"\n"]))
