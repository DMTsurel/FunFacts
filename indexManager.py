'''
Created on 5 Jun 2016

@author: David
'''
import os
import codecs
import collections
import errno
from shutil import copyfile


def copyIndex(src, dest):
    print dest
    if not os.path.exists(os.path.dirname(dest)):
        try:
            os.makedirs(os.path.dirname(dest))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    copyfile(src, dest)
    

def getIndex(filename):
    curridfIndex = {}
    if not os.path.getsize(filename) > 0:
        return None
    with open(filename) as f:
        content = f.readlines()
        for line in content:
            spl = line.split()
            if len(spl) == 2:
                curridfIndex[spl[0]] = float(spl[1])
    return curridfIndex

def getCohesIndex(filename):
    #print os.path.abspath(filename)
    #exit()
    currIndex = collections.OrderedDict()

    baseDir = os.path.dirname(filename)
    if not os.path.exists(baseDir):
        os.makedirs(baseDir)

    if not os.path.isfile(filename):
        with open(filename,"a+") as f:
            f.write("")
            
    with codecs.open(filename, encoding='utf-8') as f:
        content = f.readlines()
        for line in content:
            if line.strip() == "":
                continue
            spl = line.split()
            if spl == [] or len(spl) < 2:
                continue
            try:
                currIndex[" ".join(spl[:-1])] = float(spl[-1])
            except:
                pass
    return currIndex

def getMetricIndex(art, sub = ""):
    filename = "metricOutput/"+sub+art+"metricOutput.txt"
    currIndex = {}

    if not os.path.isfile(filename):
        with open(filename,"a+") as f:
            f.write("")
    
    with codecs.open(filename, "r", "utf-8") as f:
        content = f.readlines()
        if content == []:
            return None
        start = 0
        for i, line in enumerate(content):
            if line.startswith("All categories:"):
                start = i+1
        for line in content[start:]:
            spl = line.split()
            print spl
            if spl == []:
                continue
            try:
                currIndex[" ".join(spl[1:-1])] = float(spl[-1])
            except:
                pass
    return currIndex

if __name__ == "__main__":
    #copyIndex("metricOutput/Bill ClintonmetricOutput.txt", "metricOutput/4/Bill ClintonmetricOutput.txt")
    pass
