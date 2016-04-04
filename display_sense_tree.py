import cPickle as pickle
import sys

# to later save the sense tree
def save(tree, fileName):
    with open(fileName, 'wb') as handle:
                pickle.dump(tree, handle)
# to later load the sense tree
def load(fileName):
    with open(fileName, 'rb') as handle:
        return  pickle.load(handle)


def main(argv):
	fileName = argv[0]
	print "Printing sense tree from file {0}".format(argv[0])

	print load(fileName)

if __name__ == "__main__":
    main(sys.argv[1:])
