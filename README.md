
# FunFacts

This is the accompanying repository for the paper: 

David Tsurel, Dan Pelleg, Ido Guy, Dafna Shahaf, "[Fun Facts: Automatic Trivia Fact Extraction from Wikipedia](http://www.hyadatalab.com/papers/funfacts-wsdm17.pdf)", WSDM 2017

Please cite this paper if you use the code or results.

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

## Experiment Results Data

(Added on 08/02/2022)

Uploaded the raw experiment results data, for the experiments described in section 4. They are found under the "experiment_results" folder.