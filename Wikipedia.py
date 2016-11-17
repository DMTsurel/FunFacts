#!/usr/bin/env python
import sys  
import os

reload(sys)  
sys.setdefaultencoding('utf8')

import re
import yaml
import urllib
import urllib2
from Wiki2Plain import Wiki2Plain

class WikipediaError(Exception):
    pass

class Wikipedia:
    url_article = 'http://%s.wikipedia.org/w/index.php?action=raw&title=%s'
    url_image = 'http://%s.wikipedia.org/w/index.php?title=Special:FilePath&file=%s'
    url_search = 'http://%s.wikipedia.org/w/api.php?action=query&list=search&srsearch=%s&sroffset=%d&srlimit=%d&format=yaml'
    
    def __init__(self, lang):
        self.lang = lang
    
    def __fetch(self, url):
        request = urllib2.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        
        try:
            result = urllib2.urlopen(request)
        except urllib2.HTTPError, e:
            raise WikipediaError(e.code)
        except urllib2.URLError, e:
            raise WikipediaError(e.reason)
        
        return result
    
    def article(self, article):
        url = self.url_article % (self.lang, urllib.quote_plus(article))
        content = self.__fetch(url).read()
        
        if content.upper().startswith('#REDIRECT'):
            match = re.match('(?i)#REDIRECT \[\[([^\[\]]+)\]\]', content)
                        
            if not match == None:
                #print match.group(0), match.group(1)
                return self.article(match.group(1))

            match = re.match('(?i)#REDIRECT\[\[([^\[\]]+)\]\]', content)
            if not match == None:
                #print match.group(0), match.group(1)
                return self.article(match.group(1))

            
            raise WikipediaError('Can\'t found redirect article.')
        
        return content
    
    def image(self, image, thumb=None):
        url = self.url_image % (self.lang, image)
        result = self.__fetch(url)
        content = result.read()
        
        if thumb:
            url = result.geturl() + '/' + thumb + 'px-' + image
            url = url.replace('/commons/', '/commons/thumb/')
            url = url.replace('/' + self.lang + '/', '/' + self.lang + '/thumb/')
            
            return self.__fetch(url).read()
        
        return content
    
    def search(self, query, page=1, limit=10):
        offset = (page - 1) * limit
        url = self.url_search % (self.lang, urllib.quote_plus(query), offset, limit)
        content = self.__fetch(url).read()
        
        parsed = yaml.load(content)
        search = parsed['query']['search']
        
        results = []
        
        if search:
            for article in search:
                title = article['title'].strip()
                
                snippet = article['snippet']
                snippet = re.sub(r'(?m)<.*?>', '', snippet)
                snippet = re.sub(r'\s+', ' ', snippet)
                snippet = snippet.replace(' . ', '. ')
                snippet = snippet.replace(' , ', ', ')
                snippet = snippet.strip()
                
                wordcount = article['wordcount']
                
                results.append({
                    'title' : title,
                    'snippet' : snippet,
                    'wordcount' : wordcount
                })
        
        # yaml.dump(results, default_style='', default_flow_style=False,
        #     allow_unicode=True)
        return results
    
def getPlainArticle(name):
    baseDir = "articleCache/"
    if not os.path.exists(baseDir):
        os.makedirs(baseDir)
    filename = baseDir+name
    try:
        if os.path.isfile(filename):
            with open(filename, "r") as f:
                content = f.read()
                return content
        wiki = Wikipedia('en')
        article = wiki.article(name)
        plain = Wiki2Plain(article)
        retval = plain.text
    except:
        print "Wikipedia.getPlainArticle(name): error while getting article ", name
    baseDir = os.path.dirname(filename)
    if not os.path.exists(baseDir):
        os.makedirs(baseDir)
    with open(filename, "w") as f:
        f.write(retval)
    return retval

if __name__ == '__main__':
    import time
    start = time.time()
    art = "Hedy Lamarr"
    content = getPlainArticle(art)
    print content
    end = time.time()
    print(end - start)
    with open("timeRes.txt", "w") as f:
        f.write("parallel "+ str(end - start))
    print 'OK'
