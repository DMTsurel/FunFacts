Execution Instructions:
- Download and extract the Google News Word2Vec model into the "models" folder:
https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit 
- Install the following Python packages:
    $ pip install gensim
    $ pip install pywikibot
- Set up a configuration file for pywikibot, following this manual. Choose English Wikipedia:
https://www.mediawiki.org/wiki/Manual:Pywikibot/user-config.py
- The file "articleLists/input.txt" should contain a line-separated list of Wikipedia articles for the algorithm to process. A sample file is given.
- Run:
    $ python similarityWord2Vec.py -load -0
- Results will appear in the output folder "metricOutput"
