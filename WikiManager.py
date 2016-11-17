#!/usr/bin/python
# -*- coding: utf-8 -*-

import nltk
from pywikibot import Site, Page, Category
import os.path
import random
import Wikipedia
import re
import stemmer
import codecs
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import cpu_count
import time
import functools
import traceback
import operator

def _instance_method_alias(obj, arg):
    """
    Alias for instance method that allows the method to be called in a 
    multiprocessing pool
    """
    
    #obj.printNum(arg)
    obj.getArticleContent(arg)
    return


class WikiManager:
    def __init__(self):
        print "init WikiManager"
        self.reverseStemHashtable = {}
        self.yearRegex = re.compile("Category:\\d{4}.*")
        #self.p = stemmer.PorterStemmer()
        self.printMode = False
        cnt = cpu_count()
        self.cpuCount = 3 if cnt==4 else 8
        self.historicCats = {}

    def removeStopWords(self, articleWords):
        with open(r"StopWords.txt") as f:
            content = f.read()
            stopWords = content.split()
            return [word for word in articleWords if word not in stopWords]
    
    def filterCategories(self, cats):
        
        cats = [cat for cat in cats if (not self.yearRegex.match(cat) 
                                        and not cat.startswith(("Category:Wikipedia", "Category:Living people")) )]
        return cats
            
    
    def isPeople(self, article):
        site = Site("en")
        page = Page(site, article.decode("utf8"))
        #print article
        #print page.get()
        #print page.get(get_redirect = True)
        #print "redirect?", page.isRedirectPage()
        if page.isRedirectPage():
            page = page.getRedirectTarget()
        #print [cat.title() for cat in page.categories()]
        cats = {cat:1 for cat in page.categories()}
        if any(["People" in tcat.title() for tcat in cats]):
            print cats
            return True
        currcats = cats.copy()
        allcats = {}
        depth = 0
        while currcats!={} and depth < 2:
            depth += 1
            newcats = {}
            for cat in currcats:
                if cat in allcats:
                    continue
                allcats[cat] = 1
                parentcats = {cat:1 for cat in cat.categories()}
                if any(["People" in tcat.title() for tcat in parentcats]):
                    print parentcats
                    return True
                for parcat in parentcats:
                    if parcat not in allcats and parcat not in newcats:
                        newcats[parcat] = 1
            currcats = newcats
            print len(currcats), currcats
        #self.historicCats.update(allcats)
        return False
    
    def getCategories(self, article):
        baseDir = "articleCategoriesCache/"
        if not os.path.exists(baseDir):
            os.makedirs(baseDir)
        fname = baseDir+article
        if os.path.isfile(fname):
            lines = []
            try:
                with codecs.open(fname, encoding='utf-8') as f:
                    lines = [line.strip() for line in f.readlines()]
                #print "utf8 encoding"
            except:
                with codecs.open(fname) as f:
                    lines = [line.strip() for line in f.readlines()]
                #print "ascii encoding"
            lines = self.filterCategories(lines)
            if lines!=[]:
                #print "get Cat Cache:", lines
                return lines
        
        site = Site("en")
        page = Page(site, article.decode("utf8"))
        #print article
        #print page.get()
        #print page.get(get_redirect = True)
        #print "redirect?", page.isRedirectPage()
        if page.isRedirectPage():
            page = page.getRedirectTarget()
        #print [cat.title() for cat in page.categories()]
        cats = sorted([cat.title() for cat in page.categories() if not cat.isHiddenCategory()])
        #print "downloaded cats1: ", cats
        cats = self.filterCategories(cats)
        #print "downloaded cats2: ", cats
        text =""
        for cat in cats:
            text += cat+"\n"
        try:
            with codecs.open(fname, "a+") as f:    
                f.write(text)
        except:
            with codecs.open(fname, "a+") as f:    
                f.write(text.encode('utf-8'))
        return cats
        #for cat in page.categories():
        #    print 
            
    def getArticles(self, category, recurse=False):
        if category.startswith("Category:"):
            category = category.split(":")[1]
        
        #if not isinstance(category, unicode):
        #    category = unicode(category, "utf-8")
        baseDir = "categoryArticlesCache/"
        if not os.path.exists(baseDir):
            os.makedirs(baseDir)
        
        fname = baseDir+category
        if recurse:
            fname = baseDir+category
        fname = fname.encode('utf8')
        if self.printMode:
            try:
                print unicode(fname)
            except:
                print "error printing fname"
        if os.path.isfile(fname):
            lines = []
            try:
                with codecs.open(fname) as f:
                    lines = [line.strip() for line in f.readlines()]
            except:
                with codecs.open(fname, encoding='utf-8') as f:
                    lines = [line.strip() for line in f.readlines()]
            if lines!=[]:
                return lines
    
        site = Site("en")
        cat = ""
        try:
            cat = Category(site, title=category)
        except:
            cat = Category(site, title=category.decode("utf-8"))
        articles = cat.articles(namespaces = 0, recurse=recurse)
        res = [article.title().encode('utf8') for article in articles]
        #print res
        text = ""
        for cat in res:
            text += cat+"\n"
        try:
            with codecs.open(fname, "a+") as f:    
                #print text
                #print type(text)
                f.write(text)
        except:
            with codecs.open(fname, "a+") as f:    
                f.write(text.encode('utf-8'))
        return res
        
            
    def normalizeText(self, text):
        text = text.lower()
        text = re.sub('[^0-9a-zA-Z]+', ' ', text)
        articleWords = text.split()
        articleWords = self.removeStopWords(articleWords)
        stemmedWords = []
        for word in articleWords:
            p = stemmer.PorterStemmer()
            stemmed = p.stemWord(word)
            self.reverseStemHashtable[stemmed] = word
            stemmedWords.append(stemmed)
        return stemmedWords
    
    def getArticleSentencesNLP(self, art):
        text = "this’s a sent tokenize test. this is sent two. is this sent three? sent 4 is cool! Now it’s your turn."
        res = nltk.sent_tokenize(text)
        print res
        exit()
        
    def getArticleSentences(self, art):
        articleContent = Wikipedia.getPlainArticle(art)
        #sentences = articleContent.split(".")
        sentences = nltk.sent_tokenize(articleContent)
        sentences = [re.sub('\n+', ' ', s.strip()) for s in sentences]
        normSentences = [self.normalizeText(art) for art in sentences]
        return (sentences, normSentences)
        
    def printNum(self, num):
        print num
    
    def getArticleContent(self, art):
        try:
            articleContent = Wikipedia.getPlainArticle(art)
            #move to argument
            firstSentence=False
            if firstSentence:
                articleContent = articleContent.split(".")[0]
            normWords = self.normalizeText(articleContent)
            return normWords
        except:
            "error in WikiManager.getArticleContent()"
            traceback.print_exc()
    
    def getRandomArticlesFromCategory(self, categoryName, sampleSize = 50, articleNameCompare = None, multi = False):
        cacheName = "randomArticleCacheNames/"+categoryName
        articles = self.getArticles(categoryName)
        articles = [art for art in articles if not art==articleNameCompare]   
        subSize = min(sampleSize, len(articles))
        subNames = random.sample(articles, subSize)
        if multi:
            _bound_instance_method_alias = functools.partial(_instance_method_alias, self)
            pool = ThreadPool(self.cpuCount) 
            subText = pool.map(_bound_instance_method_alias, subNames)
            #subText = pool.map(_bound_instance_method_alias, range(len(subNames)))
        else:
            subText = [self.getArticleContent(art) for art in subNames]
        catlen = len(articles)
        '''
        with open(cacheName, "w") as f:
            for i in subNames:
                f.write(i+"\n")
        for i, t in enumerate(subText):
            with open("randomArticleCache/"+subNames[i], "w") as f:
                #print subText[i]
                f.write("\n".join(subText[i]))
        '''
        return catlen, len(subText), subNames, subText
    
    def recursiveCats(self, catObj):
        res = set()
        test = [catObj]
        while test:
            currObj = test.pop(0)
            print "currObj is", currObj
            yield currObj.title()
            for subCat in currObj.subcategories(recurse=False):
                print subCat
                if subCat not in res:
                    test.append(subCat)
                    res.add(subCat)
        #print res
        #exit()
        #return res
        
    
    def getBoundedCat(self, cat, currMinSize):
        print
        print "getBoundedCat"
        site = Site("en")
        try:
            catObj = Category(site, title=cat)
        except:
            catObj = Category(site, title=cat.decode("utf-8"))
        
        subCats = self.recursiveCats(catObj) 
        
        articleSet = set()
        
        for subCat in subCats:
            print "inside subCat", subCat
            newArts = set(self.getArticles(subCat, recurse=False))
            articleSet.update(newArts)
            print len(articleSet)
            if len(articleSet) > currMinSize:
                print "break"
                return currMinSize
                #continue

        return len(articleSet)
    
    def getSmallestCat(self, article):
        currMinSize = 100
        catName = None
        cats = self.getCategories(article)
        random.shuffle(cats)
        for cat in cats:
            print "currMinSize", currMinSize, catName
            print "inside", cat
            catLen = self.getBoundedCat(cat, currMinSize)
            if catLen < currMinSize:
                currMinSize = catLen
                catName = cat
        return catName, currMinSize
    

def speedTest():
    wm = WikiManager()
    print wm.cpuCount
    cat = "Member states of the United Nations"
    t0 = time()
    wm.getRandomArticlesFromCategory(cat, multi=True)
    t1 = time()
    print "thread %f" %(t1-t0)
    wm.getRandomArticlesFromCategory(cat, multi=False)
    t2 = time()
    print "regular %f" %(t2-t1)


def getCategoryOfSize():
    wm = WikiManager()
    cacheName = "topComediansCache.txt"
    if os.path.isfile(cacheName):
        with open(cacheName, "r") as f:
            top = [l.strip() for l in f.readlines()]
    cats = []
    for art in top:
        cats += wm.getCategories(art)
    cats = set(cats)
    print "cats", cats
    for cat in cats:
        currArts = wm.getArticles(cat)
        if len(currArts) == 4:
            print "found", cat, currArts
        

def popular():
    with open("popularPages.txt", "r") as f:
        lines = [l.strip() for l in f.readlines()]
    lines = [l for l in lines if l.startswith("|[[") and not l.startswith("|[[File:") and not l.startswith("|[[WP:")]
    lines = [l.split("[")[-1].split("]")[0] for l in lines]
    '''
    with open("popularPagesFilt2.txt", "w") as f:
        for l in lines:
            f.write(l+"\n")
    '''
    for l in lines:
        print l
    print len(lines)
    
    wm = WikiManager()
    for l in lines:
        res = wm.isPeople(l)
        print l, wm.isPeople(l)
        if res:
            with open("popularPeople.txt", "a+") as f:
                f.write(l+"\n")


if __name__ == "__main__":
    #nltk.download()
    #popular()
    #speedTest()
    #exit()
    
    start = time.time()


    wm = WikiManager()
    '''
    cat = "Canadian martial artists"
    print cat
    arts = wm.getArticles(cat, recurse=False)
    print len(arts)
    exit()
    '''
    '''
    cat = "Canadian martial artists"
    site = Site("en")
    catObj = Category(site, title=cat)
    subs = catObj.subcategories(recurse=False)
    for s in subs:
        print s
    exit()
    '''
    
    articles = wm.getArticles("Presidents of the United States")
    articles = ["Akshay Kumar"]
    articles = ["Macaulay Culkin", "Gaurav Tiwari"]
    articles = ["Hedy Lamarr", "Barack Obama", "Abraham Lincoln", "Donald Trump", "Bill Clinton"]
    res = []
    for article in articles: 
        print article, wm.getSmallestCat(article)
        res.append((article, wm.getSmallestCat(article)))
    print res
    end = time.time()
    print(end - start)
    exit()
            
    
    print wm.getRandomArticlesFromCategory("Democratic Party Presidents of the United States")
    
    getCategoryOfSize()
    #for s in sent[1]:
    #    print s
    '''
    content = "#REDIRECT[[Fort Huachuca#US Army Intelligence Museum]]"
    match = re.match('(?i)#REDIRECT \[\[([^\[\]]+)\]\]', content)
    print match          
    '''     
    #content = wm.getArticleContent(art)
    #articleContent = Wikipedia.getPlainArticle(art)
    #print articleContent
    '''
    cats = wm.getCategories("Salar de Uyuni")
    print cats
    exit()
    '''
    
    '''
    catlen, catlen, subNames, subText = wm.getRandomArticlesFromCategory("United States Army museums", 50, None)
    for art in subNames:
        print "art", art
        #print wm.getArticleContent(art)
    '''
