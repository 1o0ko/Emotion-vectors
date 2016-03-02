import unittest

from babelnet.structures import Tree
from wordvectors.build_emotion_vectors import tree2vector
import numpy as np
import numpy.testing as npt

def getMockTree():
    return Tree(np.array([0., 0.]), [
        Tree(np.array([2.,2.])), 
        Tree(np.array([3.,3.]), [
            Tree(np.array([4.,4.])),
            Tree(np.array([4.,4.])),
            Tree(np.array([4.,4.])), 
            Tree(np.array([5.,5.]), [
                Tree(np.array([1., 1.0])),
                Tree(np.array([1.,1.]))
                ])
            ]), 
        Tree(np.array([1.,1.]))])

class TestTreeAveraging(unittest.TestCase):
    def test(self):
        mockTree = getMockTree()
        treevector = tree2vector(mockTree, {}, lambda tree, params: np.array(tree.value))
        
        npt.assert_allclose(treevector, np.array([ 1.23958333,  1.23958333]))


if __name__ == '__main__':
    unittest.main()
