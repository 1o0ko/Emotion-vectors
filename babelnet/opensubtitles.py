import urllib2
import sys
import logging
import logging.config
import gzip
import requests 

from bs4 import BeautifulSoup
from cStringIO import StringIO

DATA_PATH = '/home/data/'
DATA_NAME = 'en-pl.xml'

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
        logger.error("Unexpected HTTP error: %s", sys.exc_info()[0])
        return 'no name found for id {0}'.format(docId)
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

def downloadAllMovies(filename):
    logger = logging.getLogger(__name__)

    with open(filename, 'w') as f:
        for result in getAllMovieNames(DATA_PATH, DATA_NAME):
            movie_id, movie_name, from_doc, to_doc = result
            f.write(u';'.join([movie_id, movie_name, from_doc, to_doc]).encode('utf-8').strip() + "\n")

def getGzXml(doc):
    url = "http://opus.lingfil.uu.se/download.php?f=OpenSubtitles2016/xml/{0}".format(doc)
    response = requests.get(url)
    results = gzip.GzipFile(fileobj=StringIO(response.content))
    
    for r in results:
        yield r

def getIndices(line):
    if line == '':
        return None
    else:
        return [int(x) for x in line.split(' ')]

def getParalelSubtittles(en_doc_id):
    logger = logging.getLogger(__name__)
    indices = []
    
    with open('{0}/{1}'.format(DATA_PATH, DATA_NAME)) as f:
        has_found = False
        for line in f:
            if line.startswith('<linkGrp'):
                from_doc, to_doc = parseGroup(line)
                if en_doc_id == from_doc:
                    has_found = True
                    print 'Found it'
                    continue
                    
            if line.startswith('</linkGrp>') and has_found:
                print 'The end!'              
                break
                
            if has_found:
                elem = BeautifulSoup(line, "lxml")
                xtargets = elem.html.head.link['xtargets'].split(";")
                en = getIndices(xtargets[0])
                pl = getIndices(xtargets[1])
                
                indices.append((en, pl))
    
    return indices
    

if __name__ == '__main__':
    
    logging.config.fileConfig('logging.ini', disable_existing_loggers=False)

#    downloadAllMovies('movies.txt')

    doc = "en/0/1218843/5205554.xml.gz"
        
    for idx in getParalelSubtittles(doc):
      print idx
      
    for s in getGzXml(doc):
      print s

