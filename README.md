# udacity-fsd-proj-log-analysis

## Udacity Full Stack Developer Project - Logs Analysis
Simple python3 program that connects to a local _news_ DB and answers 3 questions:
* What are the most popular three articles of all time?
* Who are the most popular article authors of all time?
* On which days did more than 1% of requests lead to errors? 

### Environment Setup

You'll need to install [VirtualBox5.1](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) and [Vagrant](https://www.vagrantup.com/downloads.html)

Next, you need to set up the VM. You can download and unzip this file: [FSND-Virtual-Machine.zip](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip) This will give you a directory called `FSND-Virtual-Machine`.

Open a terminal (GitBash works well on Windows, or whatever term you prefer on Linux/OSX) and `cd` to `FSND-Virtual-Machine/vagrant`

Bring up the VM with:

````
user@host:~$ vagrant up
````

And log in to it with:

````
user@host:~$ vagrant ssh
````

You VM should be up and running now. Time to populate the DB with data. 

On your host machine, [download the data here](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip). You will need to unzip this file after downloading it. The file inside is called `newsdata.sql`. Put this file into the `vagrant` directory, which is shared with your virtual machine. While you're here, put [log_analysis.py](https://github.com/mach21/udacity-fsd-proj-log-analysis/blob/master/log_analysis.py) into the vagrant directory, so you can run it from the VM.

Now go back to your VM and `cd` into the `vagrant` directory, and import the data using:

````
user@host:~$ psql -d news -f newsdata.sql
````

### How to run log_analysis.py

You will run the program inside the Vagrant VM. Only python3 is supported (3.6.7 and up). Install dependencies using pip3:

````
user@host:~$ pip3 install -r requirements.txt
````

Then run as python script. No args required.

````
user@host:~$ python3 log_analysis.py
````

### Design
The **LogAnalyzer** class establishes a DB connection and obtains a cursor on instantiation. The connection and cursor are (re)used for all the queries this program executes.

There is a **__db_exec_and_fetchall(query)** convenience method that simplifies running queries and fetching results. Individual methods for fetching relevant data for the questions that need to be answered make use of it: **__get_3_most_popular_articles()**, **__get_most_popular_authors()**, **__get_bad_days()**

Note that these internal workings are not intended for public access, thus the name mangling.

Answers are printed to STDOUT via public methods: **print_popular_article_data()**, **print_popular_author_data()**, **print_bad_days_data()**

To avoid the possibility of forgetting to close DB connections, **LogAnalyzer** is hidden inside a **LogAnalyzerResource**, which only provides useful functionality when instantiated via context manager, like this:

````
with LogAnalyzerResource(db_name='news') as log_analyzer:
    log_analyzer.print_popular_article_data()
    log_analyzer.print_popular_author_data()
    log_analyzer.print_bad_days_data()
````

The DB connection will be automatically closed when the context ends.

Instantiating a **LogAnalyzer** the old-fashioned way is not possible:

````
(Pdb) analyzer = LogAnalyzer(db_name='news')
*** NameError: name 'LogAnalyzer' is not defined
````

Furthermore, directly instantiating a **LogAnalyzerResource** won't produce anything meaningful:

````
(Pdb) analyzer = LogAnalyzerResource(db_name='news')
(Pdb) analyzer.print_popular_article_data()
*** AttributeError: 'LogAnalyzerResource' object has no attribute 'print_popular_article_data'
(Pdb) dir(analyzer)
['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__enter__', '__eq__', '__exit__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'db_name']
````

### Sample output
[See output.txt](https://github.com/mach21/udacity-fsd-proj-log-analysis/blob/master/output.txt)
