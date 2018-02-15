# Log Analysis of a newpaper website

#### To Run...

Run the ```logAnalysis.py``` using python 3.
Open [localhost:8000](localhost:8000) or [127.0.0.1:8000](127.0.0.1:8000) in any browser.
Wait for a while for the queries to run and load the results.

## Design

- Python code ```logAnalysis.py``` runs a simple python server (for ever) on localhost:8000 address.

- As soon as it gets a HTTP GET request, it connects to the news database and sends three queries for the three questions from the exercise description.

- Results are sent back as plain text with a **200 status code**.

**Note**: News database was setup initially in a Linux VM _(Vagrant)_.


### Output

```plain
Top three most popular articles:
-------------------------------
Candidate is jerk, alleges rival -- 342102 views
Bears love berries, alleges bear -- 256365 views
Bad things gone, say good people -- 171762 views


Most popular Authors:
--------------------
Ursula La Multa -- 512805 views
Rudolf von Treppenwitz -- 427781 views
Anonymous Contributor -- 171762 views
Markoff Chaney -- 85387 views


On the following days, more than 1% of requests lead to errors:
--------------------------------------------------------------
July 17, 2016 -- 2.32% errors
```