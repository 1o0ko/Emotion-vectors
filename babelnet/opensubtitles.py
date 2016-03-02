import sys
import requests 
import urllib2
import logging
import logging.config
import gzip


from bs4 import BeautifulSoup
from cStringIO import StringIO

DATA_PATH = '/home/data/'
DATA_NAME = 'en-pl.xml'

#-------------------------------| PARSING

"""Returns documents ids

Helper method to retrieve subtitles ids from line
"""
def parseGroup(text):
    line = BeautifulSoup(text, "lxml")
    fst = line.html.body.linkgrp['fromdoc']
    snd = line.linkgrp['todoc']

    return fst, snd 

"""Returns string with xml contents

Helper method to donwload document from the internet and unpack it 
"""    
def getGzXml(doc):
    url = "http://opus.lingfil.uu.se/download.php?f=OpenSubtitles2016/xml/{0}".format(doc)
    response = requests.get(url)
    results = gzip.GzipFile(fileobj=StringIO(response.content))
    
    return ''.join([r for r in results])


"""Returns list with subtitle lines

"""
def getDialogueLines(xml):
  
    soup = BeautifulSoup(xml, "lxml")      
    get_text = lambda line: ' '.join([word.get_text() for word in line.findAll('w')])
            
    return [get_text(line) for line in soup.findAll('s')]

#-------------------------------| Indices
def getIndices(line):
    return (None if line == '' else [(int(x)-1) for x in line.split(' ')])
        


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



def getParalelSubtittles(en_doc_id):
    
    logger = logging.getLogger(__name__)
    
    subtitles = []
    en_subs, pl_subs = None, None
    with open('{0}/{1}'.format(DATA_PATH, DATA_NAME)) as f:
        has_found = False
        
        for line in f:
        
            if line.startswith('<linkGrp'):
                from_doc, to_doc = parseGroup(line)
                
                if en_doc_id == from_doc:
                    has_found = True
                    
                    en_subs = getDialogueLines(getGzXml(from_doc))
                    pl_subs = getDialogueLines(getGzXml(to_doc))
                    
                    continue
                    
            if line.startswith('</linkGrp>') and has_found:  
                break
                
            if has_found:
                elem = BeautifulSoup(line, "lxml")
                xtargets = elem.html.head.link['xtargets'].split(";")
                en_idxs = getIndices(xtargets[0])
                pl_idxs = getIndices(xtargets[1])
                
                if en_idxs and pl_idxs:
                    try: 
                        en_text = "".join([en_subs[idx] for idx in en_idxs]).encode('utf-8').strip()
                        pl_text = "".join([pl_subs[idx] for idx in pl_idxs]).encode('utf-8').strip()
                    
                        subtitles.append((en_text, pl_text))
                    except:
                        logger.error("Unexpected error: %s", sys.exc_info())                        
    
    return subtitles
    

if __name__ == '__main__':
    
    logging.config.fileConfig('logging.ini', disable_existing_loggers=False)

    downloadAllMovies('movies.txt')

#    doc = "en/1957/50083/3127877.xml.gz"
    
#    for from_, to_ in getParalelSubtittles(doc):
#      print from_
#      print to_
#      print "-------"  
      

