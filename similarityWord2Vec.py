#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

import logging
import WikiManager
import matplotlib.pyplot as plt
#from gensim.models import word2vec
#from gensim import models
import gensim
#import Wikipedia
#import Wiki
import heapq
import re
import stemmer
import math
import textwrap
#import numpy
#import random
import os
#import CategoryViews
#from plot import plotScat
import sys
import codecs
import indexManager
import traceback
from multiprocessing.dummy import Pool as ThreadPool 


class similarityWord2Vec:

    def __init__(self):
        print "init similarityWord2Vec"
        self.wikiManager = WikiManager.WikiManager()
        self.model = None
        self.idfIndex = None
        self.sampleDict = {}
        self.forceRefresh = False
        self.wikiManager.printMode = self.printMode = False
        self.batch = None
        for arg in sys.argv:
            matchObj = re.match("-(\d+)", arg)
            if matchObj:
                self.batch = matchObj.group(1)



        
    
    
    def loadIndexes(self):
        
        if self.model or self.idfIndex:
            return 
        #global model
        print "loading word2vec model"
        self.model = gensim.models.Word2Vec.load_word2vec_format("models/GoogleNews-vectors-negative300.bin", binary=True)  # C text format
        print "done"
        #model = gensim.models.Word2Vec.load_word2vec_format("models/glove_model.txt", binary=False)  # C text format
    
        #global idfIndex
        print "loading idfIndex model"
        self.idfIndex = indexManager.getIndex("plainIdfIndex.txt")
        print "done"
        #return (model, idfIndex)
    

    def getTopTfIdfTerms(self, articleText, topK, idfLimit=10):
        articleIndex = {}
        tfIndex = {}
        wordCounter = 0
        for word in articleText:
            if not self.wikiManager.reverseStemHashtable[word] in self.model.vocab:
                continue
            #if wordCounter==500:
            #    break
            tfIndex[word] = tfIndex[word]+1 if word in tfIndex else 1
            wordCounter+=1
            
        for word in tfIndex:
            tfScore = tfIndex[word]
            idfScore = self.idfIndex[word] if word in self.idfIndex else 1.5
            #filter rare terms:
            if idfScore < idfLimit:
                continue 
            articleIndex[word] = tfScore * math.log10(float(self.idfIndex["docsSizeIndex"]) / idfScore)
            #articleIndex[word] = tfScore
            
        #Math.log10(1 + tf) * Math.log10(_articleCount / idf);    
        
        topWords = heapq.nlargest(topK, articleIndex, key=articleIndex.get)
        topWordsDestemmed = [self.wikiManager.reverseStemHashtable[word] for word in topWords]
        
        if len(topWordsDestemmed)!=topK:
            if self.printMode:
                print topWordsDestemmed
                for word in articleText:
                    print word
                    if not self.wikiManager.reverseStemHashtable[word] in self.model.vocab:
                        print "not present"
            #assert len(topWordsDestemmed)==topK
    
        
        return topWordsDestemmed
    
    
    def articlesSimilarity2(self, article1, article2, weighted=True):
        #article1 = getTopTfIdfTerms(articleName1)
        #article2 = getTopTfIdfTerms(articleName2)
        if self.printMode:
            print "article1", article1
            print "article2", article2
        distance = 0
        wordsLen = len(article1)
        if wordsLen == 0 or len(article2) == 0: 
            return 0.0 
        for index, word1 in enumerate(article1):
            cosDist = [self.model.similarity(word1, word2) for word2 in article2]
            if weighted:
                distance += (wordsLen-index) * max(cosDist)
            else:
                distance += max(cosDist)
        if weighted:
            distance /= (wordsLen+1) * float(wordsLen) / 2
        else:
            distance /= wordsLen
        return distance
    
    def articlesSimilarity(self, articleText1, articleText2, articleName1, articleName2, topK=10, weighted=True, idfLimit=10):
        article1 = self.getTopTfIdfTerms(articleText1, topK, idfLimit)
        article2 = self.getTopTfIdfTerms(articleText2, topK, idfLimit)
        if article1==[] or article2==[]:
            return 0
        if self.printMode:
            print articleName1, ",", articleName2
            print "top-K", topK
            print "top tf-idf tokens for", articleName1, article1
            print "top tf-idf tokens for", articleName2, article2
        #print "n_similarity", model.n_similarity(article1, article2)
        '''
        sim1to2 = self.articlesSimilarity2(article1, article2, weighted)
        sim2to1 = self.articlesSimilarity2(article2, article1, weighted)
        retval = (sim1to2+sim2to1) / 2
        '''
        retval1 = self.articlesSimilarity2(article1, article2, weighted)
        retval2 = self.articlesSimilarity2(article2, article1, weighted)
        retval = (retval1+retval2)/2
        #with open("categoryExample.txt", "a") as f:
        #    f.write(articleName1+"|||"+articleName2+"|||"+str(retval)+"\n")
        if self.printMode:
            print retval
            print
        return retval
    
    #articlesSimilarity("queen", "king")
    
    def firstSentenceBasicCategory(self,art):
    
        first = self.wikiManager.getArticleContent(art, firstSentence=True)
        catlenDict = [cat for cat in self.wikiManager.getCategories(art)]
        catNorm = [(cat, self.wikiManager.normalizeText(cat)) for cat in catlenDict]
    
        #destem
        for word in first:
            if not self.wikiManager.reverseStemHashtable[word] in self.model.vocab:
                print "word not found", self.wikiManager.reverseStemHashtable[word]
                #exit()
        for cat in catNorm:
            for word in cat[1]:
                if not self.wikiManager.reverseStemHashtable[word] in self.model.vocab:
                    print "word not found", self.wikiManager.reverseStemHashtable[word]
                    #exit()
        
        first = [self.wikiManager.reverseStemHashtable[word] for word in first if self.wikiManager.reverseStemHashtable[word] in self.model.vocab]
        catNorm = [(cat[0], [self.wikiManager.reverseStemHashtable[word] for word in cat[1] if self.wikiManager.reverseStemHashtable[word] in self.model.vocab]) for cat in catNorm]
        
        print first
        print catNorm
        
        catSim = [(cat[0], self.articlesSimilarity2(cat[1], first, weighted=False)) for cat in catNorm]
        for cat in sorted(catSim, key=lambda x:x[1]):
            print cat
        exit()
    
    
    def categoryCohesiveness(self, categoryName, compareToArticleName = None):
        print "categoryCohesiveness function"
        baseIndex = "cohesivenessIndex.txt"
        indexName = compareToArticleName+baseIndex if compareToArticleName else baseIndex
        indexName = "cohesivenessIndexCache/"+indexName
        if self.printMode:
            print indexName
        #global cohesivenessIndex
        cohesivenessIndex = indexManager.getCohesIndex(indexName)
        #print cohesivenessIndex
        #exit()
        #print "inside", categoryName, cohesivenessIndex
        #print cohesivenessIndex
        if not self.forceRefresh and categoryName in cohesivenessIndex:
            #print categoryName, "inside"
            #print "returning", categoryName, cohesivenessIndex[categoryName]
            return categoryName, cohesivenessIndex[categoryName]
        
        #fix this!!!
        #return None
        
        #print categoryName, "outside"
        if categoryName not in self.sampleDict:
            (catlen, subSize, subNames, subText) = self.wikiManager.getRandomArticlesFromCategory(categoryName, 50, compareToArticleName)
            self.sampleDict[categoryName] = (catlen, subSize, subNames, subText)
        else:
            (catlen, subSize, subNames, subText) = self.sampleDict[categoryName]
        pairNum = subSize if compareToArticleName else subSize * (subSize-1) / 2
        #pairNum = subSize if compareToArticleName else subSize * (subSize-1) / 2
        summa = 0.0
        sumSq = 0.0
        
        if compareToArticleName:
            compareToArticleText = self.wikiManager.getArticleContent(compareToArticleName)
            if self.printMode:
                print compareToArticleName, compareToArticleText
            for i in range(subSize):
                currCohes = self.articlesSimilarity(compareToArticleText, subText[i], compareToArticleName, subNames[i])
                
                summa += currCohes
                sumSq += currCohes * currCohes 
        else:
            for i in range(subSize):
                for j in range(i):
                    '''
                for j in range(subSize):
                    if i==j:
                        continue
                    '''
                       
                    currCohes = self.articlesSimilarity(subText[i], subText[j], subNames[i], subNames[j], 10)
                    summa += currCohes
                    sumSq += currCohes * currCohes
        aveCohes = 0.0
        stdCohes = 0.0
        if (subSize > 1):          
            aveCohes = summa / pairNum
            stdCohes = math.sqrt((sumSq - ((summa * summa) / pairNum)) / pairNum)
        res = categoryName, "len:", catlen, "average:", aveCohes, "std", stdCohes
        
        cohesivenessIndex[categoryName] = aveCohes
        
        with open(indexName, "a") as f:
            f.write(categoryName.encode('utf-8') + " " + str(aveCohes) + "\n")
        
        if self.printMode:
            print res
    
        return categoryName, aveCohes
    
    
    def createRatioDict(self, cohesAbsList, cohesList, labels):
        #remove threshold?
        #cohesThresh = 0
        cohesThresh = sorted(cohesAbsList)[len(cohesAbsList)/3]
        #cohesAbsListFilt = []
        #cohesListFilt = []
        #viewsListFilt = []
        #labelsFilt = []
        ratio = {}
        for i in range(len(cohesAbsList)):
            if cohesAbsList[i] < cohesThresh:
                continue
            #cohesListFilt.append(cohesList[i])
            #viewsListFilt.append(viewsList[i])
            #cohesAbsListFilt.append(cohesAbsList[i])
            #labelsFilt.append(labels[i])
            '''
            try:
                print "label", labels[i].encode("utf8")
                print "cohesAbsList", cohesAbsList[i].encode("utf8")
                print "cohesList", cohesList[i].encode("utf8")
            except:
                print "error print label"
            '''
            if cohesList[i]==0:
                ratio[1.0] = labels[i]
            else:
                ratio[cohesAbsList[i] / cohesList[i]] = labels[i]
        if self.printMode:
            try:
                for rat in sorted(ratio):
                    print ratio[rat], rat.encode('utf8')
            except:
                print "error printing rat"
        return ratio
            
    def getInterestingness(self, art, cat):
        surpriseResult = self.categoryCohesiveness(cat, art)[1]
        cohesResult = self.categoryCohesiveness(cat)[1]
        return cohesResult, surpriseResult
            
    def viewsVsCohesiveness(self, art):
        indexName = "metricOutput/"+art+"metricOutput.txt"
        if not os.path.exists("metricOutput/"):
            os.makedirs("metricOutput/")
        if self.batch:
            subDir = "metricOutput/"+self.batch+"/"
            if not os.path.exists(subDir):
                os.makedirs(subDir)
            subIndex = subDir+art+"metricOutput.txt"
            
        print art
        
        if not self.forceRefresh:
            try:
                sub = str(self.batch)+"/" if self.batch else ""
                metricIndex = indexManager.getMetricIndex(art, sub)
                if self.printMode:
                    print metricIndex
                if self.batch:
                    indexManager.copyIndex(indexName, subIndex)
            except:
                metricIndex = {}
            if metricIndex != {} and metricIndex !=None:
                return
        
        
        cats = self.wikiManager.getCategories(art)
        if cats == []:
            print "Error! No categories found for article ", art
            print "Please fix this bug"
        #views = CategoryViews.getViews(cats)
        #cats = [cat.split(":")[1] for cat in cats]
        print "mycats", cats
        cohesResults = {}
        cohesAbsResults = {}
    
        for cat in sorted(cats):
            #cat = view.split(":")[1]
            try:
                print "cat", unicode(cat), art.encode("utf8")
            except:
                print "cat print error"
            if not self.categoryCohesiveness(cat, art):
                continue
            cohesResults[cat] = self.categoryCohesiveness(cat, art)[1]
            cohesAbsResults[cat] = self.categoryCohesiveness(cat)[1]
        catSizes = []
        labels = []
        cohesList = []
        viewsList = []
        cohesAbsList = []
        for cat in cohesResults:
            #print "cat", cat
            #labels.append(str(views[cat]) + " " + cat)
            labels.append(str(0) + " " + cat)
            cohesList.append(cohesResults[cat])
            #if views[cat] > 0:
            #    viewsList.append(math.log10(views[cat]))
            #else:
            #    viewsList.append(0)
            viewsList.append(0)
            cohesAbsList.append(cohesAbsResults[cat])
            articles = self.wikiManager.getArticles(cat)
            if len(articles) > 0:
                catSizes.append(math.log10(len(articles)))
            else:
                catSizes.append(0)
        if self.printMode:    
            print cohesList
            print viewsList
        ratio = self.createRatioDict(cohesAbsList, cohesList, labels)
        metricOutput = u""
        metricOutput += art.decode("utf8") + "\n"
        metricOutput += "Bottom 5 categories:\n"
        for rat in sorted(ratio)[:5]:
            metricOutput += ratio[rat]
            metricOutput += " " + str(rat) + "\n" 
        metricOutput += "\n"
        metricOutput += "Top 5 categories:\n"
        for rat in sorted(ratio)[-5:]:
            metricOutput += ratio[rat]
            metricOutput += " " + str(rat) + "\n" 
        metricOutput += "\n"
        metricOutput += "All categories:\n"
        for rat in sorted(ratio):
            metricOutput += ratio[rat]
            metricOutput += " " + str(rat) + "\n" 
        metricOutput += "\n"
    
        if self.printMode:
            try:
                print metricOutput.encode('utf8')
            except:
                print "error printing metric"
        try:
            print "writing metric to file", art.encode('utf8')
        except:
            print "error printing article name"

        with codecs.open(indexName, "w+", "utf-8") as f:
            f.write(metricOutput)
        if self.batch:
            indexManager.copyIndex(indexName, subIndex)
        #'''
        cohesivenessRes = [cohesAbsResults[curr] for curr in sorted(cohesAbsResults)]
        print cohesivenessRes
        print cohesAbsResults
        surpriseRes = [1.0/cohesResults[curr] for curr in sorted(cohesResults)]
        print surpriseRes
        print cohesResults
        labels = sorted([t[11:] for t in labels])    
        z = zip(*(labels, cohesivenessRes, surpriseRes, [cohesResults[curr] for curr in sorted(cohesResults)]))
        for i in z:
            print i
        #plotScat(cohesivenessRes, surpriseRes, "Cohesiveness", "Surprise", labels, 4, art)
    
    
    def articleToCategorySimilarity(self, art):
        categories = self.wikiManager.getCategories(art)
        if self.printMode:
            print "categories", categories
        cohesResults = []
        for cat in categories:
            cohesResults.append(self.categoryCohesiveness(cat, art))
            
        #cohesResults = sorted(cohesResults, key=lambda x:x[1])
        if self.printMode:   
            for cohes in cohesResults:
                print cohes
        labels = []
        x = []
        y = []
        ratio = {}
        for cohes in cohesResults:
            label = cohes[0]
            labels.append(label)
            catCohes = self.categoryCohesiveness(cohes[0])[1]
            x.append(catCohes)
            artCohes = cohes[1]
            y.append(artCohes)
            ratio[catCohes / artCohes] = label
    
        #cohesThresh = sorted(catCohes)[len(catCohes)/3]
    
        print art
        print "ratio:"
        for rat in sorted(ratio):
            print ratio[rat], rat
        
        print "x", x
        print "y", y
        
        plotScat(x, y, "category cohesiveness", "article to category similarity", labels, 4, art) 
        #exit()

    def surprisingCatTest(self):
        surprisingCategories1 = ["Women in technology", "Grammy Award winners", "20th-century American male actors",
                                "People prosecuted under anti-homosexuality laws", "French people of Polish descent", "Zoologists", "African-American businesspeople",
                                "Mystics", "Heisman Trophy winners", "American anarchists", "Deified people", 
                                "Tony Award winners", "Chief Justices of the United States", "Presidents of Austria",
                                "Democratic Party United States Senators", "Participants in American reality television series", "Botanists with author abbreviations",
                                "Harvard Medical School alumni", "American inventors", "American inventors"
                                ]
        surprisingCategories2 = ["1914 births","2000 deaths","20th-century Austrian people","20th-century American actresses","American anti-fascists","American film actresses","American inventors","Austrian emigrants to the United States","Austrian film actresses","Austrian inventors","Metro-Goldwyn-Mayer contract players","Radio pioneers","Women in technology","American people of Hungarian-Jewish descent","Actresses from Vienna","Women inventors","20th-century Austrian actresses","Disease-related deaths in Florida"]
        
        cohesResults = []
        for cat in surprisingCategories1:
            cohes = self.categoryCohesiveness(cat)
            cohesResults.append(cohes)
        #print cohes
        for cohes in sorted(cohesResults, key=lambda x:x[1]):
            print cohes
        '''
        for cohes in sorted(cohesResults, key=lambda x:x[4]):
            print cohes
        '''
        exit()
        
    #surprisingCatTest()
    
    def hillaryTest(self):
        self.loadIndexes()
        presidents = ["Barack Obama","George Walker Bush","William Jefferson Clinton","George Herbert Walker Bush","Ronald Wilson Reagan","James Earl Carter, Jr.","Gerald Rudolph Ford, Jr.","Richard Milhous Nixon","Lyndon Baines Johnson","John Fitzgerald Kennedy"]
        other = ["Wolfgang Amadeus Mozart", "Cooperative Dictionary of the Rhinelandic Colloquial Language", "History of the New York Rangers", "Trumpet", "Oscar Hammerstein II", "Monomyth", "Gwonbeop", "Symphony", "Condorcet method", "Climate change"]
        compares = presidents + other
        topKs = [1, 3, 5, 10, 20, 30, 50, 100]
        #topKs = [10]
        plt.figure(3)
        colors = ["orange", "b", "g", "r", "c", "m", "y", "k"]
        
        #plt.subplot(211)
        #tups = zip(*enumerate(JerSim))
        #plt.plot(tups[0], tups[1])
        for index, topK in enumerate(topKs):
            ress = [self.articlesSimilarity(self.wikiManager.getArticleContent("Hillary Clinton"), self.wikiManager.getArticleContent(art), "Hillary Clinton", art, topK) for art in compares]
            tups = zip(*enumerate(ress))
            plt.xlabel('Compared articles')
            plt.ylabel('Word2Vec average max similarity')
            plt.title('Hillary Clinton similarity')
        
            plt.xticks(tups[0], [textwrap.fill(text,10) for text in compares], rotation=90, fontsize=8)
            plt.plot(tups[0], tups[1], label=str(topK), color=colors[index])
            plt.ylim((0.0,1.0))
        plt.legend(title="Top k tokens").draggable()
        plt.show()
    
    #hillaryTest()
    
    
    def plotCohesVsSurprise(self):
        surpriseDict = {}
        catlenDict = {}
    
        with open(r"ObamaSurprise.txt") as f:
            content = f.readlines()
            for line in content:
                spl = line.split(":")
                val = float(spl[2].split()[0])
                catlenDict[spl[1]] = float(spl[2].split()[1])
                surpriseDict[spl[1]] = val
        cohesDict = {}
        for cat in surpriseDict:
            cohesDict[cat] = self.categoryCohesiveness(cat)
        x = []
        y = []
        catLen = []
        labels = []
        for cat in surpriseDict:
            x.append(abs(surpriseDict[cat]))
            y.append(cohesDict[cat][1])
            catLen.append(math.log10(catlenDict[cat]))
            labels.append(cat)
            print cat, surpriseDict[cat], cohesDict[cat], catlenDict[cat]
            
            
        cohesSurprise = [(labels[i], x[i]*y[i]) for i in range(len(x))]
        for cohes in sorted(cohesSurprise, key=lambda x:x[1]):
            print cohes
        
        plotScat(x, y, 'Surprise', 'Cohesiveness', labels, 1)
        plotScat(x, catLen, 'Surprise', 'len', labels, 2)
        plotScat(y, catLen, 'Cohesiveness', 'len', labels, 3)
    
    
    def articlesMulSim(self, topK):
        HillarySim = []
        HillarySim.append(self.articlesSimilarity("Hillary Clinton", "Bill Clinton", topK))
        HillarySim.append(self.articlesSimilarity("Hillary Clinton", "Barack Obama", topK))
        HillarySim.append(self.articlesSimilarity("Hillary Clinton", "Bernie Sanders", topK))
        HillarySim.append(self.articlesSimilarity("Hillary Clinton", "Donald Trump", topK))
        HillarySim.append(self.articlesSimilarity("Hillary Clinton", "Benjamin Netanyahu", topK))
        HillarySim.append(self.articlesSimilarity("Hillary Clinton", "Wolfgang Amadeus Mozart", topK))
        HillarySim.append(self.articlesSimilarity("Hillary Clinton", "Cooperative Dictionary of the Rhinelandic Colloquial Language", topK))
        HillarySim.append(self.articlesSimilarity("Hillary Clinton", "History of the New York Rangers", topK))
        HillarySim.append(self.articlesSimilarity("Hillary Clinton", "Trumpet", topK))
        return HillarySim
        
    
    def test1(self):
        
        #topKs = [1, 3]
        topKs = [1, 3, 5, 10, 20, 30, 50, 100]
        colors = ["orange", "b", "g", "r", "c", "m", "y", "k"]
        plt.figure(1)
        #plt.subplot(211)
        #tups = zip(*enumerate(JerSim))
        #plt.plot(tups[0], tups[1])
        for index, topK in enumerate(topKs):
            HillarySim = self.articlesMulSim(topK)
            tups = zip(*enumerate(HillarySim))
            plt.plot(tups[0], tups[1], label=str(topK), color=colors[index])
            plt.ylim((0.0,1.0))
        plt.legend().draggable()
        plt.show()
        
        
        exit()
    
    def test2(self):
        topWords = self.getTopTfIdfTerms("Jerusalem")
        for word in topWords:
            #print word, idfIndex[word] if word in idfIndex else 1.5
            try:
                print self.model.most_similar(positive=[word], topn=10)
            except:
                print "word not in vocabulary"


#print model.accuracy(r"C:\Users\David\workspace\Wiki\gitWiki\questions-words.txt")

#model = word2vec.Word2Vec(sentences)
#model = word2vec.Word2Vec.load_word2vec_format("C:\Users\David\workspace\Wiki\gitWiki\text8-queen", binary=False)
#model = gensim.models.Word2Vec.load_word2vec_format('/tmp/vectors.txt', binary=False)

    def prepareBatches(self):
        batch = [[] for x in range(20)]
        print batch
        
        with open("articleLists/input.txt") as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]
            batch[0] = lines

        '''
        batch[1] = ["Marie Curie", "Hedy Lamarr", "Barack Obama", "Ronald Reagan",
                "Pythagoras", "Leonardo da Vinci", "Aristotle", "George Foreman", 
                "Steve Spurrier", "Noam Chomsky", "Imhotep", 
                "Whoopi Goldberg", "William Howard Taft", "Kurt Waldheim", 
                "John Glenn", "Deion Sanders", "George Washington Carver", 
                "Michael Crichton", "Thomas Jefferson", "Benjamin Franklin"]
        surprisingCategories = ["French people of Polish descent", "Women in technology", "Grammy Award winners", "20th-century American male actors",
                "Mystics", "People prosecuted under anti-homosexuality laws", "Zoologists", "African-American businesspeople",
                "Heisman Trophy winners", "American anarchists", "Deified people", 
                "Tony Award winners", "Chief Justices of the United States", "Presidents of Austria",
                "Democratic Party United States Senators", "Participants in American reality television series", "Botanists with author abbreviations",
                "Harvard Medical School alumni", "American inventors", "American inventors"]
        batch[2] = ["Lin-Manuel Miranda",
                "Wayne Gretzky",
                "The Bahamas",
                "Gone with the Wind",
                "Gone with the Wind (film)",
                "Eminem",
                "Emperor penguin",
                "Lavandula",    
                "Foie gras",
                "Portrait of Adele Bloch-Bauer I",
                "Salar de Uyuni",
                "War of Jenkins' Ear",
                "The Wire",
                "Levirate marriage",
                "Zeppelin",
                "The Wall",
                "Minotaur",
                "Snooker",
                "Robert E. Lee",
                "Trolley problem",
                "United States Military Academy",
                "Stethoscope",
                "Emily Dickinson",
                "The Taming of the Shrew",
                "Psalms"]
        
        batch[3] = ["Aliens (film)",
                "Batman Begins",
                "Elf (film)",
                "Final Destination (film)",
                "Gravity (film)",
                "Her (film)",
                "Interstellar (film)",
                "Let Me In (film)",
                "Lone Survivor (film)",
                "Man of Steel (film)",
                "Pineapple Express (film)",
                "Primary Colors (film)",
                "Riddick (film)",
                "Rio 2",
                "Talk to Her",
                "The Commitments (film)",
                "The Deer Hunter",
                "The Incredibles",
                "Transformers: Dark of the Moon",
                "Who Framed Roger Rabbit"]
        cat = "Presidents of the United States"
        batch[4] = sim.wikiManager.getArticles(cat)
        cat2 = "Prime Ministers of Israel"
        batch[5] = sim.wikiManager.getArticles(cat2)
        #batch = batch1+batch2+batch3+arts2+arts
        with open("articleLists/List of 20th-century writers.txt") as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]
            batch[6] = lines
        with open("articleLists/List of contraltos in non-classical music.txt") as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]
            batch[7] = lines
        with open("articleLists/List of comedians.txt") as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]
            batch[8] = lines
        with open("popularPagesFilt.txt") as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]
            batch[9] = lines
        batch[10] = ["Theresa May"]
        batch[13] = ["Hedy Lamarr", "Barack Obama"]
        '''
        
        return batch[int(self.batch)]
        
        #print "usage: enter -number for batch number (e.g. -1)"
        #exit()
    def metricWrapper(self, art):
        try:
            self.viewsVsCohesiveness(art)
        except:
            print "Error"
            try:
                print art
            except:
                pass
            traceback.print_exc(file=sys.stdout)
            return

    def categoryRepresentative(self, cat):
        arts = self.wikiManager.getArticles(cat)
        print "arts", arts
        interestingness = {}
        for art in arts:
            cohes, surprise = self.getInterestingness(art, cat)
            interestingness[art] = cohes/surprise
        indexName = "categoryRepresentative/"+cat+".txt"
        with codecs.open(indexName, "w+", "utf-8") as f:
            text = ""
            for art in sorted(interestingness, key=lambda x:x[1]):
                text += art + " " + str(interestingness[art]) + "\n"
            print text
            f.write(text)




if __name__ == "__main__":   

    sim = similarityWord2Vec()
    
    if "-log" in sys.argv:
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO, filename="similarity.log")
    if "-refresh" in sys.argv:
        sim.forceRefresh = True
    if "-print" in sys.argv:
        sim.wikiManager.printMode = sim.printMode = False
    if "-load" in sys.argv:
        sim.loadIndexes()
    batch = sim.prepareBatches()
    import time
    start = time.time()
    if "-parallel" in sys.argv:
        pool = ThreadPool(sim.wikiManager.cpuCount) 
        results = pool.map(sim.metricWrapper, batch)
    else:
        for article in batch:
            sim.metricWrapper(article)
    end = time.time()
    if "-time" in sys.argv:
        print(end - start)
        with open("timeRes.txt", "w") as f:
            f.write("parallel "+ str(end - start))
    print 'OK'       
