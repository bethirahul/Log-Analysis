# Log Analysis of a newpaper website

#### To Run...
Run the logAnalysis.py using python 3.
Open localhost:8000 or 127.0.0.1:8000 in any browser.
Wait for a while for the queries to run and load the results.

#### Design
Python code _logAnalysis.py_ runs a simple python server for ever on localhost:8000 address.
As soon as it gets a HTTP GET request, it connects to the news database and sends three queries for the three questions from the exercise description.
Results are sent back as plain text.