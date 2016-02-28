import numpy as np
import os
import string

from display_sense_tree import load
from nltk import word_tokenize
from nltk.corpus import stopwords
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity

def getSentenceVector(sentence, params):    
    word_list = word_tokenize(sentence)
    
    model = params['model']
    blacklist = params['blacklist']
    
    filtered_words = [word.lower() for word in word_list if word.lower() not in blacklist]                       
    sentence_vector = sum([model[word] for word in filtered_words if word in model])
    
    return sentence_vector

def getVector(tree, params):
    word = tree.value.lemma
    model = params['model'] 
    return model[word] if word in model else np.zeros(model.layer1_size)

def tree2vector(tree, params, f = getVector):        
    
    def getvector(tree, current_weight, level):                                     
        
        tree_value = f(tree, params)
        
        node_value =  tree_value
        node_weight = 1.0 / len(tree.children) if tree.children else 1               

        if tree.children:        
            for leaf in tree.children:      
                node_value += node_weight*getvector(leaf, node_weight, level + 1)
        else:
            node_value = tree_value   
        
        return node_value / level
    
    return getvector(tree, 1, 1)

def getEmotionVectors(path, params):
    emotions = {}
    for file in os.listdir(path):
        if file.endswith(".pickle"):
            tree = load('{0}/{1}'.format(path, file))
            emotions[file[:file.find('.')]] = tree2vector(tree, params)

    return emotions

def closest(sentence_vector, emotions):
    
    closest = None
    best_distane = -float('inf')

    for name, emotion_vector in emotions.iteritems():        
        current_distance = cosine_similarity([sentence_vector], [emotion_vector])[0][0]    
        if best_distane < current_distance:
            best_distane = current_distance
            closest = name
    
    return closest

if __name__ == '__main__':
    en_model = Word2Vec.load('/home/models/wiki.en.model')
#    pl_model = Word2Vec.load('/home/models/wiki.pl.model')
    en_params = {'model': en_model, 'blacklist': set(stopwords.words('english')).union(set(string.punctuation))}
#    pl_params = {'model': pl_model, 'blacklist': set(stopwords.words('polish')).union(set(string.punctuation))}

    sentence = getSentenceVector("To continue , you 've listened to a long and complex case , murder in the first degree .", en_params)
    emotions = getEmotionVectors('/home/models/threshold_0/', en_params)
    print closest(sentence, emotions)
