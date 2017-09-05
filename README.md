# DataAnalysis
analysis on spreadsheets using pandas, numpy

query/querymerge.py is a python program used to perform analysis on large CSV data spreadsheets containing columns of biometric or sensor data. The program takes in a spreadsheet containing IDs, timestamps and 'screen names,' corresponding to the time a new window appears on a users computer. It then looks in a directory for a bunch of CSV files of processed data and finds the one with matching ID and a close timestamp. Then it finds the columns in that file corresponding to the name of the entered variables, and computes the mean, min, max, or standard deviation (or a combination of them) for the data in that column over a given time interval

plot/plot.py is similar, but plots the data for each separate user to a graph along with an aggregate from the given function (mean, sum, etc).

matplotlib contains a matplotlib style sheet that is free and open for anyone to use or modify,
and two scripts that generate graphs, each with a corresponding png file showing the graph
generated. I chose to graph the cryptocurrencies Bitcoin, Ether, and XRP (Ripple).

Since almost all coding is done in teams, I consider readability to be paramount when writing code. I may use two or three lines to do something that could be done in one, but it will make the code easier to follow and understand.
