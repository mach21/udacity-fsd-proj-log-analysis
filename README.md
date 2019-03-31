# udacity-fsd-proj-log-analysis

## Udacity Full Stack Developer Project - Logs Analysis
Simple python3 program that connects to a local _news_ DB and answers 3 questions:
* What are the most popular three articles of all time?
* Who are the most popular article authors of all time?
* On which days did more than 1% of requests lead to errors? 

## Prerequisites
Only python3 is supported (3.6.7 and up). Install dependencies using pip3:


````
pip3 install -r requirements.txt
````

The _news_ PostgreSQL database needs to be installed and populated.

Please refer to _Project: Logs Analysis -> Section 3 (Prepare the software and data)_ for instructions.

## How to run
Run as python script inside the Vagrant VM where your _news_ DB lives. No args required.

````
user@host:~$ python3 log_analysis.py
````

## Design
The *LogAnalyzer* class establishes a DB connection and obtains a cursor on instantiation. The connection and cursor are (re)used for all the queries this program executes.

There is a *__db_exec_and_fetchall(query)* convenience method that simplifies running queries and fetching results. Individual methods for fetching relevant data for the questions that need to be answered make use of it: *__get_3_most_popular_articles()*, *__get_most_popular_authors()*, *__get_bad_days()*

Note that these internal workings are not intended for public access, thus the name mangling.

Answers are printed to STDOUT via public methods: *print_popular_article_data()*, *print_popular_author_data()*, *print_bad_days_data()*

To avoid the possibility of forgetting to close DB connections, The *LogAnalyzer* class is hidden inside a *LogAnalyzerResource*, which only provides useful functionality when instantiated via context manager, like this:

````
with LogAnalyzerResource(db_name='news') as log_analyzer:
    log_analyzer.print_popular_article_data()
    log_analyzer.print_popular_author_data()
    log_analyzer.print_bad_days_data()
````

The DB connection will be automatically closed when the context ends.

Instantiating a LogAnalyzer the old-fashioned way is not possible:

````
(Pdb) analyzer = LogAnalyzer(db_name='news')
*** NameError: name 'LogAnalyzer' is not defined
````

Furthermore, directly instantiating a LogAnalyzerResource won't produce anything meaningful:

````
(Pdb) analyzer = LogAnalyzerResource(db_name='news')
(Pdb) analyzer.print_popular_article_data()
*** AttributeError: 'LogAnalyzerResource' object has no attribute 'print_popular_article_data'
(Pdb) dir(analyzer)
['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__enter__', '__eq__', '__exit__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'db_name']
````

## Sample output
[See output.txt](https://github.com/mach21/udacity-fsd-proj-log-analysis/blob/master/output.txt)