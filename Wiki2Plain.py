#!/usr/bin/env python

import re

class Wiki2Plain:
    def __init__(self, wiki):
        self.wiki = wiki
        
        self.text = wiki
        self.text = self.unhtml(self.text)
        self.text = self.unwiki(self.text)
        self.text = self.punctuate(self.text)
    
    def __str__(self):
        return self.text
    
    def unwiki(self, wiki):
        """
        Remove wiki markup from the text.
        """
        wiki = re.sub(r'(?i)\{\{IPA(\-[^\|\{\}]+)*?\|([^\|\{\}]+)(\|[^\{\}]+)*?\}\}', lambda m: m.group(2), wiki)
        wiki = re.sub(r'(?i)\{\{Lang(\-[^\|\{\}]+)*?\|([^\|\{\}]+)(\|[^\{\}]+)*?\}\}', lambda m: m.group(2), wiki)
        wiki = re.sub(r'\{\{[^\{\}]+\}\}', '', wiki)
        wiki = re.sub(r'(?m)\{\{[^\{\}]+\}\}', '', wiki)
        wiki = re.sub(r'(?m)\{\|[^\{\}]*?\|\}', '', wiki)
        wiki = re.sub(r'(?i)\[\[Category:[^\[\]]*?\]\]', '', wiki)
        wiki = re.sub(r'(?i)\[\[Image:[^\[\]]*?\]\]', '', wiki)
        wiki = re.sub(r'(?i)\[\[File:[^\[\]]*?\]\]', '', wiki)
        wiki = re.sub(r'\[\[[^\[\]]*?\|([^\[\]]*?)\]\]', lambda m: m.group(1), wiki)
        wiki = re.sub(r'\[\[([^\[\]]+?)\]\]', lambda m: m.group(1), wiki)
        wiki = re.sub(r'\[\[([^\[\]]+?)\]\]', '', wiki)
        wiki = re.sub(r'(?i)File:[^\[\]]*?', '', wiki)
        wiki = re.sub(r'\[[^\[\]]*? ([^\[\]]*?)\]', lambda m: m.group(1), wiki)
        wiki = re.sub(r"''+", '', wiki)
        wiki = re.sub(r'(?m)^\*$', '', wiki)
        
        return wiki
    
    def unhtml(self, html):
        """
        Remove HTML from the text.
        """
        html = re.sub(r'(?i)&nbsp;', ' ', html)
        html = re.sub(r'(?i)<br[ \\]*?>', '\n', html)
        html = re.sub(r'(?m)<!--.*?--\s*>', '', html)
        html = re.sub(r'(?i)<ref[^>]*>[^>]*<\/ ?ref>', '', html)
        html = re.sub(r'(?m)<.*?>', '', html)
        html = re.sub(r'(?i)&amp;', '&', html)
        
        return html
    
    def punctuate(self, text):
        """
        Convert every text part into well-formed one-space
        separate paragraph.
        """
        text = re.sub(r'\r\n|\n|\r', '\n', text)
        text = re.sub(r'\n\n+', '\n\n', text)
        
        parts = text.split('\n\n')
        partsParsed = []
        
        for part in parts:
            part = part.strip()
            
            if len(part) == 0:
                continue
            
            partsParsed.append(part)
        
        return '\n\n'.join(partsParsed)
    
    def image(self):
        """
        Retrieve the first image in the document.
        """
        # match = re.search(r'(?i)\|?\s*(image|img|image_flag)\s*=\s*(<!--.*-->)?\s*([^\\/:*?<>"|%]+\.[^\\/:*?<>"|%]{3,4})', self.wiki)
        match = re.search(r'(?i)([^\\/:*?<>"|% =]+)\.(gif|jpg|jpeg|png|bmp)', self.wiki)
        
        if match:
            return '%s.%s' % match.groups()
        
        return None

if __name__ == '__main__':
    # @link http://simple.wikipedia.org/w/index.php?action=raw&title=Uruguay
    wiki = """[[File:LocationUruguay.png|right|]]
'''Uruguay''' is a country in [[South America]]. The language spoken there is Spanish. Its [[capital (city)|capital]] and largest [[city]] is [[Montevideo]]. Uruguay is bordered by two large neighbors, [[Brazil]] and [[Argentina]]. The only country in South America that is smaller than Uruguay is [[Suriname]].
The land there is mostly flat and they have many farms there.
{{geo-stub}}

{{South America}}
{{Link FA|af}}
{{Link FA|ast}}
{{Link FA|ca}}

[[Category:Uruguay| ]]"""
    
    wiki2plain = Wiki2Plain(wiki)
    content = wiki2plain.text
    image = wiki2plain.image()
    
    print '---'
    print content
    print '---'
    print image
    print '---'