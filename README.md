# Generating Infoboxes for Hindi Wikipedia Articles
## IRE Major Project

### Team Members

 - Shradha Sehgal ( 2018101071 )
- Risubh Jain ( 2018101104 )
- Monu Tayal ( 2018201042 )
- Akash Kumar ( 2019201046 )

### Problem Statement
Our problem statement is to generate infoboxes for Hindi wikipedia articles that currently lack infoboxes. We narrowed down oon the domain of articles and generated infoboxes for 10k such pages. There are a number of techniques that we explore and experiment with in order to generate the infoboxes. We also work towards creating an algorithm that is flexible enough to be extended to multiple domains and categories.

### Domain Selection and Data Collection
 We did a preliminary analysis using 3 methods 
 
 - Cluster Categories from Hindi Wiki Dump 
 - Splitting categories into single terms
 - PetScan 
Finally we choose "people" as our primary domain and "places" as our secondary domain.

Data was collected by querying wikidata and parsing the wikidump for both the categories.
Final dataset has 

 - 6501 people related articles
 - 3621 places articles
 ( code in "data-collection" folder )

### Final Methods

1.  Key-value pairs extraction from Wikidata in Hindi ( code in "method1" folder )
2.  Translating and transliterating English infoboxes ( code in "method2" folder )
3. Key-value pair extraction from Wikidata in English + Translation and transliteration ( Baseline ) ( code in "baseline" folder )

### Evaluation
We created a test set of 700 articles for people and 400 articles for places.
Evaluation Metrics were computed by fuzzy-matching generated values and actual infobox values.

### How to Run
To get infobox for an article from the Hindi Wikipedia, 2 values are required.

 - Name of corresponding page in the English Wikipedia ( for method2 )
 -  Qid of the wikidata page ( for method1 and baseline )

Generation code is available in evaluation/example.ipynb