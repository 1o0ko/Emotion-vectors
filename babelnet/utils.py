import urllib2
import urllib
import json
import gzip
import logging

from StringIO import StringIO

def sendRequest(params, service_url):
    logger = logging.getLogger(__name__)
        
    url = service_url + '?' + urllib.urlencode(params)
    request = urllib2.Request(url)
    request.add_header('Accept-encoding', 'gzip')
    response = urllib2.urlopen(request)

    if response.info().get('Content-Encoding') == 'gzip':
        logger.debug('Recieved response for: {0}'.format(params))
        buf = StringIO( response.read())
        f = gzip.GzipFile(fileobj=buf)
        data = json.loads(f.read())
        return data
    else:
        logger.debug('Could not recieve response for: {0}'.format(params))
    return []

def getSynsetIds(text, lang, key):
    
    ids = []
    
    service_url = 'https://babelfy.io/v1/disambiguate'

    params = {
        'text' : text,
        'lang' : lang,
        'key'  : key
    }
           
    for result in sendRequest(params, service_url):                        
            ids.append(result.get('babelSynsetID'))
    
    return ids

def getInfo(id, key):
    service_url = 'https://babelnet.io/v2/getSynset'
    
    params = {
        'id' : id,
        'key'  : key
    }
    
    return sendRequest(params, service_url)

def getHyperHypoAntoNyms(id, key):
    
    service_url = 'https://babelnet.io/v2/getEdges'

    params = {
        'id' : id,
        'key'  : key
    }
    
    hypernyms, hyponyms, antonyms = [], [], []
    
    # retrieving Edges data
    for result in sendRequest(params, service_url):
        target = result.get('target')
        language = result.get('language')
        weight = result['weight']
        normalizedWeight = result['normalizedWeight']

        # retrieving BabelPointer data
        pointer = result['pointer']
        relation = pointer.get('name')
        group = pointer.get('relationGroup')
        
        # closure FTW!
        def appendElement(elements):
            lemma = getInfo(target, key)['senses'][0]['lemma']
            elements.append({
                'id': target,
                'lemma': lemma,
                'relation' : relation,
                'weight' : weight, 
                'normalizedWeight': normalizedWeight
            })

        # Types of relationGroup: HYPERNYM,  HYPONYM, MERONYM, HOLONYM, OTHER
        if ('hypernym' in group.lower()):
            appendElement(hypernyms)

        if ('hyponym' in group.lower()):
            appendElement(hyponyms)

        if ('antonym' in relation.lower()):
            appendElement(antonyms)
        
    return hypernyms, hyponyms, antonyms
            

def sanityCheck(id, key):    
    
    service_url = 'https://babelnet.io/v2/getSynset'
    
    params = {
        'id' : id,
        'key'  : key
    }
    
    data = sendRequest(params, service_url)
    
    if data != []:
        # retrieving BabelSense data
        senses = data['senses']
        print 'senses'
        for result in senses:
            lemma = result.get('lemma')
            language = result.get('language')
            print language.encode('utf-8') + "\t" + str(lemma.encode('utf-8'))

        print '\nglosses'        
        # retrieving BabelGloss data
        glosses = data['glosses']
        for result in glosses:
            gloss = result.get('gloss')
            language = result.get('language')
            print language.encode('utf-8') + "\t" + str(gloss.encode('utf-8'))        
