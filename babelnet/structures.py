class Sense(object):
    def __init__(self, id, lemma, weight=1, normalizedWeight=1):
        self.id = id
        self.lemma = lemma
        self.weight = weight
        self.normalizedWeight = normalizedWeight
    
    def __repr__(self):
        return ' '.join([str(x) for x in [self.id,  self.lemma.encode('utf-8'), self.weight, self.normalizedWeight]])

class Tree(object):
    def __init__(self, value, children=None):
        self.value = value
        self.children = []
        if children is not None:
            for child in children:
                self.add_child(child)
    
    def __repr__(self):
        return str(self.value)
        
    def __str__(self):
        def strTree(tree, level=0):     
            acc = '\t' * level + str(tree.value) + '\n'

            if tree.children:
                for leaf in tree.children:
                    acc += strTree(leaf, level +1)

            return acc 
    
        return strTree(self, 0)
    
    def add_child(self, node):
        assert isinstance(node, Tree)
        self.children.append(node)
