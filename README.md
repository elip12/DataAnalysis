# DataAnalysis
analysis on spreadsheets using pandas, numpy

Querymerge is a python program used to perform analysis on large CSV data spreadsheets containing columns of biometric or sensor data. The program takes in a spreadsheet containing IDs, timestamps and 'screen names,' corresponding to the time a new window appears on a users computer. It then looks in a directory for a bunch of CSV files of processed data and finds the one with matching ID and a close timestamp. Then it finds the columns in that file corresponding to the name of the entered variables, and computes the mean, min, max, or standard deviation (or a combination of them) for the data in that column over a given time interval

Plot is similar, but plots the data for each separate user to a graph along with an aggregate from the given function (mean, sum, etc).

Since almost all coding is done in teams, I consider readability to be paramount when writing code. I may use two or three lines to do something that could be done in one, but it will make the code easier to follow and understand.
