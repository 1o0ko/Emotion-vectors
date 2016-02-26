import re
import sys

path = '/home/u1o0ko/napisy'
subEN = 'American.Pie.1999.720p.x264.Br.YIFY.en.csv'
subPL = 'American.Pie.1999.720p.x264.Br.YIFY.pl.csv'

def readSubtitles(path, fileName):
    with open('{0}/{1}'.format(path, fileName)) as f:
        lines = f.read().splitlines()
        return lines

class LineInfo(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __str__(self):
        return "{0};{1};{2};{3}".format(self.no, self.start, self.end, self.text)

def parseSubs(path, fileName):
    pattern= re.compile('[0-9]+;\d*\.?\d+;\d*\.?\d+;')
    lineBuff = [] 
    lines = []
    
    with open('{0}/{1}'.format(path, fileName)) as f: 
        next(f)
        for line in f:
            current_line = line.strip()
            if(pattern.match(current_line)):
                if lineBuff: 
                    lines[-1].text  += (' ' + ' '.join(lineBuff))
                    lineBuff = []
                
                no, start, end, text = current_line.split(";")

                
                lines.append(LineInfo(
                    no=int(no), 
                    start=float(start),
                    end=float(end),
                    text=text
                    ))


            else:
                lineBuff.append(current_line)
                   
    return lines

def normalizeSubs(subs, div=1000):
    start = subs[0].start / div
#   start = 0
    for sub in subs:
        sub.start = sub.start/div - start
        sub.end = sub.end/div - start

    
    return subs

def groupSubs(subs, time_limit=15, response_limit = 1):
    groups = [[]]    
    
    for sub in subs:
        current_group = groups[-1]
        if not current_group:
            current_group.append(sub)
            continue 

        sub_prev = current_group[-1]        
        sub_first = current_group[0]

        if (sub.start - sub_prev.end > response_limit) or  (sub.start - sub_first.end > time_limit):
            groups.append([sub])
        else:
            current_group.append(sub)

    return groups


if __name__=='__main__':
    if len(sys.argv)==1:
        raise Exception('no language arg')
    
    sub_file = subPL if sys.argv[1]=='PL' else subEN

    lines = parseSubs(path, sub_file)
    lines = normalizeSubs(lines)
    groups = groupSubs(lines)
    
    print 'There are {0} groups'.format(len(groups))

    for g in groups:
        print "Group!"
        for l in g:
            print "\t {0}".format(l)
